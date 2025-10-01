#!/usr/bin/env python3
"""
Blockchain Payment Integration - IA Chéries Enterprise Collaboration
Decentralized payment and smart contract management for creator collaborations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0 Enterprise

⚠️ INTELLECTUAL PROPERTY WARNING
This blockchain payment system is proprietary technology of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import logging

# Core FastAPI and async imports
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, JSON, DateTime, Integer, Boolean, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Blockchain and crypto imports
from web3 import Web3
from eth_account import Account
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    # Compatibilité web3 - fallback sécurisé
    def geth_poa_middleware(*args, **kwargs):
        return lambda request, response: response
import structlog

logger = structlog.get_logger("blockchain_payments")

# Database Models
Base = declarative_base()

class BlockchainWallet(Base):
    """Blockchain wallet management"""
    __tablename__ = "blockchain_wallets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    user_type = Column(String(20), nullable=False)  # creator, brand
    wallet_address = Column(String(42), nullable=False, unique=True)
    blockchain_network = Column(String(50), nullable=False)  # ethereum, polygon, bsc
    wallet_type = Column(String(50), default="custodial")  # custodial, non_custodial
    encryption_key_id = Column(String)  # For encrypted private key storage
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlockchainTransaction(Base):
    """Blockchain transaction records"""
    __tablename__ = "blockchain_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String)
    contract_id = Column(String)
    transaction_hash = Column(String(66))  # 0x + 64 hex chars
    blockchain_network = Column(String(50), nullable=False)
    transaction_type = Column(String(50))  # payment, escrow_create, escrow_release, refund
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    amount = Column(Numeric(36, 18))  # Support for 18 decimal places
    currency = Column(String(10), nullable=False)  # ETH, USDC, USDT, etc.
    gas_used = Column(Integer)
    gas_price = Column(Numeric(36, 18))
    transaction_fee = Column(Numeric(36, 18))
    block_number = Column(Integer)
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    smart_contract_address = Column(String(42))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)

class SmartContract(Base):
    """Smart contract deployments"""
    __tablename__ = "smart_contracts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, nullable=False)
    contract_type = Column(String(50), nullable=False)  # escrow, milestone, revenue_share
    contract_address = Column(String(42), nullable=False)
    blockchain_network = Column(String(50), nullable=False)
    abi = Column(JSON)  # Contract ABI
    bytecode = Column(Text)
    deployment_transaction = Column(String(66))
    contract_terms = Column(JSON)
    parties = Column(JSON)  # Contract parties
    status = Column(String(20), default="deployed")  # deployed, active, completed, terminated
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class CryptocurrencyRate(Base):
    """Cryptocurrency exchange rates"""
    __tablename__ = "cryptocurrency_rates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    rate = Column(Numeric(36, 18), nullable=False)
    source = Column(String(50))  # coingecko, coinbase, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class BlockchainNetwork(str, Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"

class CryptoCurrency(str, Enum):
    """Supported cryptocurrencies"""
    ETH = "ETH"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    MATIC = "MATIC"
    BNB = "BNB"

class TransactionType(str, Enum):
    """Blockchain transaction types"""
    PAYMENT = "payment"
    ESCROW_CREATE = "escrow_create"
    ESCROW_RELEASE = "escrow_release"
    ESCROW_REFUND = "escrow_refund"
    MILESTONE_PAYMENT = "milestone_payment"
    REVENUE_SHARE = "revenue_share"
    STAKING = "staking"
    WITHDRAWAL = "withdrawal"

class SmartContractType(str, Enum):
    """Smart contract types"""
    ESCROW = "escrow"
    MILESTONE = "milestone"
    REVENUE_SHARE = "revenue_share"
    SUBSCRIPTION = "subscription"
    NFT_MINTING = "nft_minting"

class WalletCreateRequest(BaseModel):
    """Create blockchain wallet request"""
    user_id: str
    user_type: str = Field(..., pattern="^(creator|brand)$")
    blockchain_network: BlockchainNetwork
    wallet_type: str = Field(default="custodial", pattern="^(custodial|non_custodial)$")

class PaymentRequest(BaseModel):
    """Blockchain payment request"""
    collaboration_id: str
    from_user_id: str
    to_user_id: str
    amount: Decimal = Field(..., gt=0)
    currency: CryptoCurrency
    blockchain_network: BlockchainNetwork
    transaction_type: TransactionType = TransactionType.PAYMENT
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EscrowContractRequest(BaseModel):
    """Escrow smart contract creation request"""
    collaboration_id: str
    brand_user_id: str
    creator_user_id: str
    total_amount: Decimal = Field(..., gt=0)
    currency: CryptoCurrency
    blockchain_network: BlockchainNetwork
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    terms: Dict[str, Any] = Field(default_factory=dict)
    auto_release_days: int = Field(default=30, ge=1, le=90)

class MilestonePaymentRequest(BaseModel):
    """Milestone payment request"""
    contract_id: str
    milestone_id: str
    amount: Decimal = Field(..., gt=0)
    approver_user_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

@dataclass
class NetworkConfig:
    """Blockchain network configuration"""
    name: str
    rpc_url: str
    chain_id: int
    explorer_url: str
    gas_limit: int
    gas_price_multiplier: float = 1.2
    confirmation_blocks: int = 12
    currency: str = "ETH"

class BlockchainPaymentProcessor:
    """Enterprise Blockchain Payment Processor"""
    
    def __init__(
        self,
        db_session: Session,
        redis_client: Any = None
    ):
        self.db = db_session
        self.redis = redis_client
        
        # Network configurations
        self.networks = {
            BlockchainNetwork.ETHEREUM: NetworkConfig(
                name="Ethereum Mainnet",
                rpc_url="https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                chain_id=1,
                explorer_url="https://etherscan.io",
                gas_limit=100000,
                confirmation_blocks=12
            ),
            BlockchainNetwork.POLYGON: NetworkConfig(
                name="Polygon Mainnet",
                rpc_url="https://polygon-rpc.com",
                chain_id=137,
                explorer_url="https://polygonscan.com",
                gas_limit=100000,
                gas_price_multiplier=1.1,
                confirmation_blocks=20,
                currency="MATIC"
            ),
            BlockchainNetwork.BSC: NetworkConfig(
                name="Binance Smart Chain",
                rpc_url="https://bsc-dataseed.binance.org",
                chain_id=56,
                explorer_url="https://bscscan.com",
                gas_limit=100000,
                gas_price_multiplier=1.1,
                confirmation_blocks=15,
                currency="BNB"
            )
        }
        
        # Web3 instances
        self.web3_instances: Dict[BlockchainNetwork, Web3] = {}
        self._initialize_web3_connections()
        
        # Contract addresses (would be deployed contracts)
        self.contract_addresses = {
            "escrow": {
                BlockchainNetwork.ETHEREUM: "0x1234567890123456789012345678901234567890",
                BlockchainNetwork.POLYGON: "0x2345678901234567890123456789012345678901",
                BlockchainNetwork.BSC: "0x3456789012345678901234567890123456789012"
            },
            "milestone": {
                BlockchainNetwork.ETHEREUM: "0x4567890123456789012345678901234567890123",
                BlockchainNetwork.POLYGON: "0x5678901234567890123456789012345678901234",
                BlockchainNetwork.BSC: "0x6789012345678901234567890123456789012345"
            }
        }
        
        logger.info("Blockchain Payment Processor initialized")

    def _initialize_web3_connections(self):
        """Initialize Web3 connections for all networks"""
        for network, config in self.networks.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config.rpc_url))
                if network == BlockchainNetwork.BSC:
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                self.web3_instances[network] = w3
                logger.info(f"Connected to {config.name}", connected=w3.is_connected())
            except Exception as e:
                logger.error(f"Failed to connect to {config.name}", error=str(e))

    async def create_wallet(
        self,
        request: WalletCreateRequest
    ) -> Dict[str, Any]:
        """Create a new blockchain wallet"""
        try:
            # Check if user already has a wallet for this network
            existing_wallet = self.db.query(BlockchainWallet).filter(
                BlockchainWallet.user_id == request.user_id,
                BlockchainWallet.blockchain_network == request.blockchain_network.value,
                BlockchainWallet.is_active == True
            ).first()
            
            if existing_wallet:
                raise HTTPException(
                    status_code=400,
                    detail=f"User already has an active wallet for {request.blockchain_network.value}"
                )
            
            # Generate new wallet
            if request.wallet_type == "custodial":
                wallet_data = await self._create_custodial_wallet(request)
            else:
                wallet_data = await self._create_non_custodial_wallet(request)
            
            # Save wallet to database
            wallet = BlockchainWallet(
                user_id=request.user_id,
                user_type=request.user_type,
                wallet_address=wallet_data["address"],
                blockchain_network=request.blockchain_network.value,
                wallet_type=request.wallet_type,
                encryption_key_id=wallet_data.get("encryption_key_id"),
                metadata=wallet_data.get("metadata", {})
            )
            
            self.db.add(wallet)
            self.db.commit()
            
            logger.info(
                "Blockchain wallet created",
                wallet_id=wallet.id,
                user_id=request.user_id,
                address=wallet_data["address"],
                network=request.blockchain_network.value
            )
            
            return {
                "wallet_id": wallet.id,
                "address": wallet_data["address"],
                "blockchain_network": request.blockchain_network.value,
                "wallet_type": request.wallet_type,
                "private_key": wallet_data.get("private_key") if request.wallet_type == "non_custodial" else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to create wallet", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to create wallet: {str(e)}")

    async def process_payment(
        self,
        request: PaymentRequest
    ) -> str:
        """Process a blockchain payment"""
        try:
            # Get sender and receiver wallets
            sender_wallet = await self._get_user_wallet(request.from_user_id, request.blockchain_network)
            receiver_wallet = await self._get_user_wallet(request.to_user_id, request.blockchain_network)
            
            if not sender_wallet or not receiver_wallet:
                raise HTTPException(status_code=404, detail="Wallet not found for one or both users")
            
            # Get Web3 instance
            w3 = self.web3_instances.get(request.blockchain_network)
            if not w3 or not w3.is_connected():
                raise HTTPException(status_code=503, detail="Blockchain network unavailable")
            
            # Check balance
            balance = await self._get_wallet_balance(
                sender_wallet.wallet_address,
                request.currency,
                request.blockchain_network
            )
            
            if balance < request.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            
            # Create transaction
            transaction = await self._create_transaction(
                w3=w3,
                from_address=sender_wallet.wallet_address,
                to_address=receiver_wallet.wallet_address,
                amount=request.amount,
                currency=request.currency,
                network=request.blockchain_network
            )
            
            # Sign and send transaction
            signed_txn = await self._sign_transaction(
                w3, transaction, sender_wallet
            )
            
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Save transaction record
            tx_record = BlockchainTransaction(
                collaboration_id=request.collaboration_id,
                transaction_hash=tx_hash.hex(),
                blockchain_network=request.blockchain_network.value,
                transaction_type=request.transaction_type.value,
                from_address=sender_wallet.wallet_address,
                to_address=receiver_wallet.wallet_address,
                amount=request.amount,
                currency=request.currency.value,
                status="pending",
                metadata=request.metadata
            )
            
            self.db.add(tx_record)
            self.db.commit()
            
            # Start monitoring transaction
            asyncio.create_task(self._monitor_transaction(tx_hash.hex(), request.blockchain_network))
            
            logger.info(
                "Blockchain payment initiated",
                transaction_id=tx_record.id,
                tx_hash=tx_hash.hex(),
                from_address=sender_wallet.wallet_address,
                to_address=receiver_wallet.wallet_address,
                amount=f"{request.amount} {request.currency.value}"
            )
            
            return tx_record.id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to process payment", error=str(e))
            raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

    async def create_escrow_contract(
        self,
        request: EscrowContractRequest
    ) -> str:
        """Create an escrow smart contract"""
        try:
            # Get brand and creator wallets
            brand_wallet = await self._get_user_wallet(request.brand_user_id, request.blockchain_network)
            creator_wallet = await self._get_user_wallet(request.creator_user_id, request.blockchain_network)
            
            if not brand_wallet or not creator_wallet:
                raise HTTPException(status_code=404, detail="Wallet not found for one or both parties")
            
            # Get Web3 instance
            w3 = self.web3_instances.get(request.blockchain_network)
            if not w3 or not w3.is_connected():
                raise HTTPException(status_code=503, detail="Blockchain network unavailable")
            
            # Deploy escrow contract
            contract_address, deployment_tx = await self._deploy_escrow_contract(
                w3=w3,
                brand_address=brand_wallet.wallet_address,
                creator_address=creator_wallet.wallet_address,
                amount=request.total_amount,
                currency=request.currency,
                terms=request.terms,
                network=request.blockchain_network
            )
            
            # Save contract record
            contract = SmartContract(
                collaboration_id=request.collaboration_id,
                contract_type=SmartContractType.ESCROW.value,
                contract_address=contract_address,
                blockchain_network=request.blockchain_network.value,
                deployment_transaction=deployment_tx,
                contract_terms={
                    "total_amount": str(request.total_amount),
                    "currency": request.currency.value,
                    "milestones": request.milestones,
                    "auto_release_days": request.auto_release_days,
                    **request.terms
                },
                parties={
                    "brand": {
                        "user_id": request.brand_user_id,
                        "wallet_address": brand_wallet.wallet_address
                    },
                    "creator": {
                        "user_id": request.creator_user_id,
                        "wallet_address": creator_wallet.wallet_address
                    }
                },
                status="deployed"
            )
            
            self.db.add(contract)
            self.db.commit()
            
            logger.info(
                "Escrow contract created",
                contract_id=contract.id,
                contract_address=contract_address,
                collaboration_id=request.collaboration_id,
                amount=f"{request.total_amount} {request.currency.value}"
            )
            
            return contract.id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to create escrow contract", error=str(e))
            raise HTTPException(status_code=500, detail=f"Escrow creation failed: {str(e)}")

    async def fund_escrow(
        self,
        contract_id: str,
        funder_user_id: str
    ) -> str:
        """Fund an escrow contract"""
        try:
            # Get contract
            contract = self.db.query(SmartContract).filter(
                SmartContract.id == contract_id,
                SmartContract.contract_type == SmartContractType.ESCROW.value
            ).first()
            
            if not contract:
                raise HTTPException(status_code=404, detail="Escrow contract not found")
            
            # Get funder wallet
            network = BlockchainNetwork(contract.blockchain_network)
            funder_wallet = await self._get_user_wallet(funder_user_id, network)
            
            if not funder_wallet:
                raise HTTPException(status_code=404, detail="Funder wallet not found")
            
            # Get Web3 instance
            w3 = self.web3_instances.get(network)
            if not w3 or not w3.is_connected():
                raise HTTPException(status_code=503, detail="Blockchain network unavailable")
            
            # Fund escrow
            tx_hash = await self._fund_escrow_contract(
                w3=w3,
                contract_address=contract.contract_address,
                funder_address=funder_wallet.wallet_address,
                amount=Decimal(contract.contract_terms["total_amount"]),
                currency=CryptoCurrency(contract.contract_terms["currency"]),
                funder_wallet=funder_wallet
            )
            
            # Create transaction record
            tx_record = BlockchainTransaction(
                collaboration_id=contract.collaboration_id,
                contract_id=contract_id,
                transaction_hash=tx_hash,
                blockchain_network=contract.blockchain_network,
                transaction_type=TransactionType.ESCROW_CREATE.value,
                from_address=funder_wallet.wallet_address,
                to_address=contract.contract_address,
                amount=Decimal(contract.contract_terms["total_amount"]),
                currency=contract.contract_terms["currency"],
                smart_contract_address=contract.contract_address,
                status="pending"
            )
            
            self.db.add(tx_record)
            self.db.commit()
            
            # Update contract status
            contract.status = "active"
            self.db.commit()
            
            # Monitor transaction
            asyncio.create_task(self._monitor_transaction(tx_hash, network))
            
            logger.info(
                "Escrow contract funded",
                contract_id=contract_id,
                tx_hash=tx_hash,
                amount=f"{contract.contract_terms['total_amount']} {contract.contract_terms['currency']}"
            )
            
            return tx_record.id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to fund escrow", error=str(e))
            raise HTTPException(status_code=500, detail=f"Escrow funding failed: {str(e)}")

    async def release_milestone_payment(
        self,
        request: MilestonePaymentRequest
    ) -> str:
        """Release a milestone payment from escrow"""
        try:
            # Get contract
            contract = self.db.query(SmartContract).filter(
                SmartContract.id == request.contract_id
            ).first()
            
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            # Validate approver permissions
            brand_user_id = contract.parties["brand"]["user_id"]
            if request.approver_user_id != brand_user_id:
                raise HTTPException(status_code=403, detail="Only brand can release milestone payments")
            
            # Get approver wallet
            network = BlockchainNetwork(contract.blockchain_network)
            approver_wallet = await self._get_user_wallet(request.approver_user_id, network)
            
            if not approver_wallet:
                raise HTTPException(status_code=404, detail="Approver wallet not found")
            
            # Get Web3 instance
            w3 = self.web3_instances.get(network)
            if not w3 or not w3.is_connected():
                raise HTTPException(status_code=503, detail="Blockchain network unavailable")
            
            # Release milestone payment
            tx_hash = await self._release_milestone_payment(
                w3=w3,
                contract_address=contract.contract_address,
                milestone_id=request.milestone_id,
                amount=request.amount,
                approver_wallet=approver_wallet,
                recipient_address=contract.parties["creator"]["wallet_address"]
            )
            
            # Create transaction record
            tx_record = BlockchainTransaction(
                collaboration_id=contract.collaboration_id,
                contract_id=request.contract_id,
                transaction_hash=tx_hash,
                blockchain_network=contract.blockchain_network,
                transaction_type=TransactionType.MILESTONE_PAYMENT.value,
                from_address=contract.contract_address,
                to_address=contract.parties["creator"]["wallet_address"],
                amount=request.amount,
                currency=contract.contract_terms["currency"],
                smart_contract_address=contract.contract_address,
                status="pending",
                metadata={
                    "milestone_id": request.milestone_id,
                    **request.metadata
                }
            )
            
            self.db.add(tx_record)
            self.db.commit()
            
            # Monitor transaction
            asyncio.create_task(self._monitor_transaction(tx_hash, network))
            
            logger.info(
                "Milestone payment released",
                contract_id=request.contract_id,
                milestone_id=request.milestone_id,
                tx_hash=tx_hash,
                amount=f"{request.amount} {contract.contract_terms['currency']}"
            )
            
            return tx_record.id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to release milestone payment", error=str(e))
            raise HTTPException(status_code=500, detail=f"Milestone payment failed: {str(e)}")

    async def get_wallet_balance(
        self,
        user_id: str,
        blockchain_network: BlockchainNetwork,
        currency: Optional[CryptoCurrency] = None
    ) -> Dict[str, Any]:
        """Get wallet balance for a user"""
        try:
            wallet = await self._get_user_wallet(user_id, blockchain_network)
            if not wallet:
                raise HTTPException(status_code=404, detail="Wallet not found")
            
            balances = {}
            
            if currency:
                # Get specific currency balance
                balance = await self._get_wallet_balance(
                    wallet.wallet_address,
                    currency,
                    blockchain_network
                )
                balances[currency.value] = str(balance)
            else:
                # Get all supported currency balances
                for curr in CryptoCurrency:
                    try:
                        balance = await self._get_wallet_balance(
                            wallet.wallet_address,
                            curr,
                            blockchain_network
                        )
                        balances[curr.value] = str(balance)
                    except Exception as e:
                        logger.warning(f"Failed to get {curr.value} balance", error=str(e))
                        balances[curr.value] = "0"
            
            return {
                "wallet_address": wallet.wallet_address,
                "blockchain_network": blockchain_network.value,
                "balances": balances,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get wallet balance", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to get balance: {str(e)}")

    async def get_transaction_history(
        self,
        user_id: Optional[str] = None,
        collaboration_id: Optional[str] = None,
        contract_id: Optional[str] = None,
        blockchain_network: Optional[BlockchainNetwork] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get transaction history"""
        try:
            query = self.db.query(BlockchainTransaction)
            
            # Apply filters
            if user_id:
                # Get user's wallet addresses
                wallets = self.db.query(BlockchainWallet).filter(
                    BlockchainWallet.user_id == user_id,
                    BlockchainWallet.is_active == True
                ).all()
                
                wallet_addresses = [w.wallet_address for w in wallets]
                if wallet_addresses:
                    query = query.filter(
                        (BlockchainTransaction.from_address.in_(wallet_addresses)) |
                        (BlockchainTransaction.to_address.in_(wallet_addresses))
                    )
                else:
                    return {"transactions": [], "total_count": 0, "has_more": False}
            
            if collaboration_id:
                query = query.filter(BlockchainTransaction.collaboration_id == collaboration_id)
            
            if contract_id:
                query = query.filter(BlockchainTransaction.contract_id == contract_id)
            
            if blockchain_network:
                query = query.filter(BlockchainTransaction.blockchain_network == blockchain_network.value)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination and ordering
            transactions = query.order_by(
                BlockchainTransaction.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Format response
            tx_data = []
            for tx in transactions:
                tx_info = {
                    "id": tx.id,
                    "collaboration_id": tx.collaboration_id,
                    "contract_id": tx.contract_id,
                    "transaction_hash": tx.transaction_hash,
                    "blockchain_network": tx.blockchain_network,
                    "transaction_type": tx.transaction_type,
                    "from_address": tx.from_address,
                    "to_address": tx.to_address,
                    "amount": str(tx.amount),
                    "currency": tx.currency,
                    "status": tx.status,
                    "confirmations": tx.confirmations,
                    "gas_used": tx.gas_used,
                    "transaction_fee": str(tx.transaction_fee) if tx.transaction_fee else None,
                    "created_at": tx.created_at.isoformat(),
                    "confirmed_at": tx.confirmed_at.isoformat() if tx.confirmed_at else None,
                    "explorer_url": self._get_explorer_url(tx.transaction_hash, tx.blockchain_network),
                    "metadata": tx.metadata
                }
                tx_data.append(tx_info)
            
            return {
                "transactions": tx_data,
                "total_count": total_count,
                "has_more": offset + limit < total_count
            }
            
        except Exception as e:
            logger.error("Failed to get transaction history", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")

    async def get_gas_estimates(
        self,
        blockchain_network: BlockchainNetwork,
        transaction_type: TransactionType,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Get gas price estimates for transactions"""
        try:
            w3 = self.web3_instances.get(blockchain_network)
            if not w3 or not w3.is_connected():
                raise HTTPException(status_code=503, detail="Blockchain network unavailable")
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            network_config = self.networks[blockchain_network]
            
            # Estimate gas limit based on transaction type
            gas_limits = {
                TransactionType.PAYMENT: 21000,
                TransactionType.ESCROW_CREATE: 150000,
                TransactionType.ESCROW_RELEASE: 100000,
                TransactionType.MILESTONE_PAYMENT: 80000,
                TransactionType.REVENUE_SHARE: 120000
            }
            
            estimated_gas_limit = gas_limits.get(transaction_type, network_config.gas_limit)
            
            # Calculate fees
            estimated_fee = (gas_price * estimated_gas_limit * network_config.gas_price_multiplier) / 10**18
            
            # Get USD equivalent if possible
            usd_rate = await self._get_crypto_to_usd_rate(network_config.currency)
            usd_fee = estimated_fee * usd_rate if usd_rate else None
            
            return {
                "blockchain_network": blockchain_network.value,
                "transaction_type": transaction_type.value,
                "gas_price_wei": str(gas_price),
                "gas_price_gwei": str(gas_price / 10**9),
                "estimated_gas_limit": estimated_gas_limit,
                "estimated_fee": str(estimated_fee),
                "estimated_fee_currency": network_config.currency,
                "estimated_fee_usd": str(usd_fee) if usd_fee else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get gas estimates", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to get gas estimates: {str(e)}")

    # Helper Methods
    async def _create_custodial_wallet(self, request: WalletCreateRequest) -> Dict[str, Any]:
        """Create a custodial wallet (platform manages private keys)"""
        # Generate new account
        account = Account.create()
        
        # In production, private key would be encrypted and stored securely
        # This is a simplified implementation
        encrypted_private_key = self._encrypt_private_key(account.key.hex())
        
        return {
            "address": account.address,
            "encryption_key_id": str(uuid.uuid4()),
            "metadata": {
                "wallet_type": "custodial",
                "created_by": "platform"
            }
        }

    async def _create_non_custodial_wallet(self, request: WalletCreateRequest) -> Dict[str, Any]:
        """Create a non-custodial wallet (user manages private keys)"""
        # Generate new account
        account = Account.create()
        
        return {
            "address": account.address,
            "private_key": account.key.hex(),
            "metadata": {
                "wallet_type": "non_custodial",
                "created_by": "user"
            }
        }

    def _encrypt_private_key(self, private_key: str) -> str:
        """Encrypt private key for secure storage"""
        # In production, use proper encryption (AES, HSM, etc.)
        # This is a placeholder
        return f"encrypted_{private_key[:10]}..."

    async def _get_user_wallet(
        self,
        user_id: str,
        blockchain_network: BlockchainNetwork
    ) -> Optional[BlockchainWallet]:
        """Get user's wallet for a specific network"""
        return self.db.query(BlockchainWallet).filter(
            BlockchainWallet.user_id == user_id,
            BlockchainWallet.blockchain_network == blockchain_network.value,
            BlockchainWallet.is_active == True
        ).first()

    async def _get_wallet_balance(
        self,
        wallet_address: str,
        currency: CryptoCurrency,
        blockchain_network: BlockchainNetwork
    ) -> Decimal:
        """Get wallet balance for specific currency"""
        w3 = self.web3_instances.get(blockchain_network)
        if not w3 or not w3.is_connected():
            return Decimal("0")
        
        if currency in [CryptoCurrency.ETH, CryptoCurrency.MATIC, CryptoCurrency.BNB]:
            # Native currency balance
            balance_wei = w3.eth.get_balance(wallet_address)
            return Decimal(balance_wei) / Decimal(10**18)
        else:
            # ERC-20 token balance
            token_address = self._get_token_address(currency, blockchain_network)
            if token_address:
                # Would use ERC-20 contract to get balance
                # This is simplified
                return Decimal("1000.0")  # Mock balance
            return Decimal("0")

    def _get_token_address(self, currency: CryptoCurrency, network: BlockchainNetwork) -> Optional[str]:
        """Get token contract address for currency on network"""
        # This would contain the actual token addresses
        token_addresses = {
            BlockchainNetwork.ETHEREUM: {
                CryptoCurrency.USDC: "0xA0b86a33E6441aE91fC5Bb4EcfcBb16EcF7A2E44",
                CryptoCurrency.USDT: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                CryptoCurrency.DAI: "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            },
            BlockchainNetwork.POLYGON: {
                CryptoCurrency.USDC: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                CryptoCurrency.USDT: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
            }
        }
        
        return token_addresses.get(network, {}).get(currency)

    async def _create_transaction(
        self,
        w3: Web3,
        from_address: str,
        to_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Create a blockchain transaction"""
        nonce = w3.eth.get_transaction_count(from_address)
        gas_price = w3.eth.gas_price
        
        if currency in [CryptoCurrency.ETH, CryptoCurrency.MATIC, CryptoCurrency.BNB]:
            # Native currency transfer
            transaction = {
                'to': to_address,
                'value': w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.networks[network].chain_id
            }
        else:
            # ERC-20 token transfer
            token_address = self._get_token_address(currency, network)
            if not token_address:
                raise ValueError(f"Token address not found for {currency.value} on {network.value}")
            
            # Create token transfer transaction
            # This would use the actual ERC-20 contract interface
            transaction = {
                'to': token_address,
                'value': 0,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.networks[network].chain_id,
                'data': '0x'  # Would be actual transfer function call
            }
        
        return transaction

    async def _sign_transaction(
        self,
        w3: Web3,
        transaction: Dict[str, Any],
        wallet: BlockchainWallet
    ) -> Any:
        """Sign a transaction"""
        if wallet.wallet_type == "custodial":
            # Get private key from secure storage
            private_key = await self._get_private_key(wallet.encryption_key_id)
        else:
            raise ValueError("Cannot sign transaction for non-custodial wallet")
        
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        return signed_txn

    async def _get_private_key(self, encryption_key_id: str) -> str:
        """Get and decrypt private key"""
        # In production, this would decrypt the private key from secure storage
        # This is a placeholder
        return "0x1234567890123456789012345678901234567890123456789012345678901234"

    async def _deploy_escrow_contract(
        self,
        w3: Web3,
        brand_address: str,
        creator_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        terms: Dict[str, Any],
        network: BlockchainNetwork
    ) -> tuple[str, str]:
        """Deploy an escrow smart contract"""
        # This would deploy the actual escrow contract
        # For now, return mock values
        contract_address = "0x" + "".join([f"{i:02x}" for i in range(20)])
        deployment_tx = "0x" + "".join([f"{i:02x}" for i in range(32)])
        
        logger.info(
            "Escrow contract deployment simulated",
            contract_address=contract_address,
            brand_address=brand_address,
            creator_address=creator_address
        )
        
        return contract_address, deployment_tx

    async def _fund_escrow_contract(
        self,
        w3: Web3,
        contract_address: str,
        funder_address: str,
        amount: Decimal,
        currency: CryptoCurrency,
        funder_wallet: BlockchainWallet
    ) -> str:
        """Fund an escrow contract"""
        # This would call the escrow contract's fund function
        # For now, return mock transaction hash
        tx_hash = "0x" + "".join([f"{i:02x}" for i in range(32)])
        
        logger.info(
            "Escrow funding simulated",
            contract_address=contract_address,
            funder_address=funder_address,
            amount=f"{amount} {currency.value}"
        )
        
        return tx_hash

    async def _release_milestone_payment(
        self,
        w3: Web3,
        contract_address: str,
        milestone_id: str,
        amount: Decimal,
        approver_wallet: BlockchainWallet,
        recipient_address: str
    ) -> str:
        """Release milestone payment from escrow"""
        # This would call the escrow contract's release function
        # For now, return mock transaction hash
        tx_hash = "0x" + "".join([f"{i:02x}" for i in range(32)])
        
        logger.info(
            "Milestone payment release simulated",
            contract_address=contract_address,
            milestone_id=milestone_id,
            amount=str(amount),
            recipient_address=recipient_address
        )
        
        return tx_hash

    async def _monitor_transaction(
        self,
        tx_hash: str,
        network: BlockchainNetwork,
        max_confirmations: int = 12
    ):
        """Monitor transaction confirmations"""
        try:
            w3 = self.web3_instances.get(network)
            if not w3 or not w3.is_connected():
                return
            
            confirmations = 0
            while confirmations < max_confirmations:
                try:
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    if receipt:
                        current_block = w3.eth.block_number
                        confirmations = current_block - receipt.blockNumber
                        
                        # Update transaction in database
                        tx = self.db.query(BlockchainTransaction).filter(
                            BlockchainTransaction.transaction_hash == tx_hash
                        ).first()
                        
                        if tx:
                            tx.confirmations = confirmations
                            tx.block_number = receipt.blockNumber
                            tx.gas_used = receipt.gasUsed
                            
                            if receipt.status == 1:  # Success
                                tx.status = "confirmed"
                                if not tx.confirmed_at:
                                    tx.confirmed_at = datetime.utcnow()
                            else:  # Failed
                                tx.status = "failed"
                            
                            self.db.commit()
                        
                        if confirmations >= max_confirmations:
                            logger.info(
                                "Transaction fully confirmed",
                                tx_hash=tx_hash,
                                confirmations=confirmations
                            )
                            break
                    
                    # Wait before checking again
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.warning(f"Error monitoring transaction {tx_hash}", error=str(e))
                    await asyncio.sleep(60)  # Wait longer on error
            
        except Exception as e:
            logger.error(f"Failed to monitor transaction {tx_hash}", error=str(e))

    def _get_explorer_url(self, tx_hash: str, network: str) -> str:
        """Get blockchain explorer URL for transaction"""
        network_enum = BlockchainNetwork(network)
        config = self.networks.get(network_enum)
        if config:
            return f"{config.explorer_url}/tx/{tx_hash}"
        return ""

    async def _get_crypto_to_usd_rate(self, currency: str) -> Optional[float]:
        """Get cryptocurrency to USD exchange rate"""
        # This would integrate with a price API like CoinGecko
        # For now, return mock rates
        mock_rates = {
            "ETH": 2500.0,
            "MATIC": 0.85,
            "BNB": 320.0,
            "USDC": 1.0,
            "USDT": 1.0,
            "DAI": 1.0
        }
        
        return mock_rates.get(currency)

    # API Methods for external integration
    async def estimate_transaction_cost(
        self,
        from_user_id: str,
        to_user_id: str,
        amount: Decimal,
        currency: CryptoCurrency,
        blockchain_network: BlockchainNetwork
    ) -> Dict[str, Any]:
        """Estimate total transaction cost including fees"""
        try:
            # Get gas estimates
            gas_estimates = await self.get_gas_estimates(
                blockchain_network,
                TransactionType.PAYMENT,
                amount
            )
            
            # Calculate total cost
            transaction_fee = Decimal(gas_estimates["estimated_fee"])
            total_cost = amount + transaction_fee
            
            # Get USD equivalents
            currency_rate = await self._get_crypto_to_usd_rate(currency.value)
            fee_rate = await self._get_crypto_to_usd_rate(gas_estimates["estimated_fee_currency"])
            
            return {
                "amount": str(amount),
                "currency": currency.value,
                "transaction_fee": gas_estimates["estimated_fee"],
                "fee_currency": gas_estimates["estimated_fee_currency"],
                "total_cost": str(total_cost),
                "total_cost_currency": currency.value,
                "amount_usd": str(amount * currency_rate) if currency_rate else None,
                "fee_usd": gas_estimates["estimated_fee_usd"],
                "total_cost_usd": str((amount * currency_rate) + Decimal(gas_estimates["estimated_fee_usd"])) if currency_rate and gas_estimates["estimated_fee_usd"] else None,
                "blockchain_network": blockchain_network.value
            }
            
        except Exception as e:
            logger.error("Failed to estimate transaction cost", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")

    async def get_supported_currencies(
        self,
        blockchain_network: Optional[BlockchainNetwork] = None
    ) -> Dict[str, Any]:
        """Get supported currencies for blockchain networks"""
        if blockchain_network:
            # Get currencies for specific network
            currencies = []
            for currency in CryptoCurrency:
                if currency in [CryptoCurrency.ETH, CryptoCurrency.MATIC, CryptoCurrency.BNB]:
                    # Native currencies
                    if (currency == CryptoCurrency.ETH and blockchain_network == BlockchainNetwork.ETHEREUM) or \
                       (currency == CryptoCurrency.MATIC and blockchain_network == BlockchainNetwork.POLYGON) or \
                       (currency == CryptoCurrency.BNB and blockchain_network == BlockchainNetwork.BSC):
                        currencies.append({
                            "currency": currency.value,
                            "type": "native",
                            "decimals": 18
                        })
                else:
                    # Token currencies
                    token_address = self._get_token_address(currency, blockchain_network)
                    if token_address:
                        currencies.append({
                            "currency": currency.value,
                            "type": "token",
                            "contract_address": token_address,
                            "decimals": 6 if currency in [CryptoCurrency.USDC, CryptoCurrency.USDT] else 18
                        })
            
            return {
                "blockchain_network": blockchain_network.value,
                "currencies": currencies
            }
        else:
            # Get all supported currencies across all networks
            result = {}
            for network in BlockchainNetwork:
                currencies = await self.get_supported_currencies(network)
                result[network.value] = currencies["currencies"]
            
            return {"supported_currencies": result}

# Factory function
def create_blockchain_processor(
    db_session: Session,
    redis_client: Any = None
) -> BlockchainPaymentProcessor:
    """Create blockchain payment processor instance"""
    return BlockchainPaymentProcessor(
        db_session=db_session,
        redis_client=redis_client
    )

# Smart Contract ABIs (simplified versions)
ESCROW_CONTRACT_ABI = [
    {
        "type": "function",
        "name": "fund",
        "inputs": [],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "releaseMilestone",
        "inputs": [
            {"name": "milestoneId", "type": "uint256"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "refund",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    }
]

ERC20_ABI = [
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view"
    }
]

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        print("Blockchain Payment Integration - Enterprise Edition")
        print("Copyright © 2025 Fahed Mlaiel. All rights reserved.")
        print("\n⚠️ UNAUTHORIZED USE PROHIBITED")
        print("This blockchain payment system is protected intellectual property.")
        
    asyncio.run(main())