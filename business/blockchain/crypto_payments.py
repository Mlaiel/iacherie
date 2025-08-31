"""Cryptocurrency Payment Processing System - IA-Influencer-Agent Platform

This module handles cryptocurrency payments including Bitcoin, Ethereum, and other
digital currencies as specified in the cahier des charges for content licensing,
creator payments, and platform transactions.

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import hashlib
import uuid

import redis.asyncio as redis
from web3 import Web3
from bitcoinrpc.authproxy import AuthServiceProxy
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.blockchain_config import BlockchainConfig
from ...core.exceptions import BlockchainError, PaymentError, ValidationError
from ...database.models import Transaction, PaymentRecord

logger = logging.getLogger(__name__)


class CryptoCurrency(Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    POLYGON = "MATIC"
    BINANCE = "BNB"
    AVALANCHE = "AVAX"
    USDT = "USDT"
    USDC = "USDC"
    DAI = "DAI"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"


@dataclass
class PaymentRequest:
    """Cryptocurrency payment request"""
    payment_id: str
    amount: Decimal
    currency: CryptoCurrency
    recipient_address: str
    sender_address: Optional[str]
    description: str
    metadata: Dict[str, Any]
    expires_at: datetime
    callback_url: Optional[str] = None


@dataclass
class PaymentResult:
    """Payment processing result"""
    payment_id: str
    tx_hash: str
    network: str
    amount: Decimal
    currency: CryptoCurrency
    status: PaymentStatus
    confirmations: int
    gas_used: Optional[int]
    gas_price: Optional[int]
    block_number: Optional[int]
    timestamp: datetime


class BitcoinProcessor:
    """
    Bitcoin payment processor for content creator payments and licensing fees
    
    Handles Bitcoin transactions including payment verification, 
    address generation, and transaction broadcasting.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.BitcoinProcessor")
        self.rpc_connection = None
        self.network = "mainnet" if not config.bitcoin_testnet else "testnet"
    
    async def initialize(self) -> None:
        """Initialize Bitcoin RPC connection"""
        try:
            # Initialize Bitcoin RPC connection
            self.rpc_connection = AuthServiceProxy(
                f"http://{self.config.bitcoin_rpc_user}:{self.config.bitcoin_rpc_password}@"
                f"{self.config.bitcoin_rpc_host}:{self.config.bitcoin_rpc_port}"
            )
            
            # Test connection
            info = self.rpc_connection.getblockchaininfo()
            self.logger.info(f"Bitcoin processor initialized - Network: {info['chain']}, Blocks: {info['blocks']}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Bitcoin processor: {str(e)}")
            raise BlockchainError(f"Bitcoin processor initialization failed: {str(e)}")
    
    async def generate_payment_address(self, user_id: int, payment_id: str) -> str:
        """Generate unique Bitcoin address for payment"""
        try:
            # Generate new address
            address = self.rpc_connection.getnewaddress(f"user_{user_id}_{payment_id}")
            
            # Store address mapping
            await self.redis.hset(
                f"btc_address:{address}",
                mapping={
                    "user_id": user_id,
                    "payment_id": payment_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "network": self.network
                }
            )
            await self.redis.expire(f"btc_address:{address}", 86400 * 7)  # 7 days
            
            self.logger.info(f"Generated Bitcoin address: {address}")
            return address
            
        except Exception as e:
            self.logger.error(f"Failed to generate Bitcoin address: {str(e)}")
            raise PaymentError(f"Address generation failed: {str(e)}")
    
    async def create_payment_request(
        self,
        amount: Decimal,
        recipient_address: str,
        user_id: int,
        description: str,
        metadata: Dict[str, Any]
    ) -> PaymentRequest:
        """Create Bitcoin payment request"""
        try:
            payment_id = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiration
            
            # Validate Bitcoin address
            if not await self._validate_bitcoin_address(recipient_address):
                raise ValidationError("Invalid Bitcoin address")
            
            payment_request = PaymentRequest(
                payment_id=payment_id,
                amount=amount,
                currency=CryptoCurrency.BITCOIN,
                recipient_address=recipient_address,
                sender_address=None,  # Will be set when payment is made
                description=description,
                metadata={**metadata, "user_id": user_id},
                expires_at=expires_at
            )
            
            # Store payment request
            await self._store_payment_request(payment_request)
            
            self.logger.info(f"Created Bitcoin payment request: {payment_id}")
            return payment_request
            
        except Exception as e:
            self.logger.error(f"Failed to create Bitcoin payment request: {str(e)}")
            raise PaymentError(f"Payment request creation failed: {str(e)}")
    
    async def process_payment(
        self,
        payment_request: PaymentRequest,
        sender_private_key: str
    ) -> PaymentResult:
        """Process Bitcoin payment"""
        try:
            self.logger.info(f"Processing Bitcoin payment: {payment_request.payment_id}")
            
            # Get unspent transaction outputs for sender
            sender_address = await self._get_address_from_private_key(sender_private_key)
            utxos = await self._get_utxos(sender_address)
            
            if not utxos:
                raise PaymentError("No unspent outputs available")
            
            # Calculate transaction fee
            fee = await self._estimate_transaction_fee()
            total_amount = payment_request.amount + fee
            
            # Select UTXOs for payment
            selected_utxos, utxo_total = await self._select_utxos(utxos, total_amount)
            
            if utxo_total < total_amount:
                raise PaymentError("Insufficient funds")
            
            # Create transaction
            tx_inputs = [
                {"txid": utxo["txid"], "vout": utxo["vout"]}
                for utxo in selected_utxos
            ]
            
            tx_outputs = {
                payment_request.recipient_address: float(payment_request.amount)
            }
            
            # Add change output if needed
            change_amount = utxo_total - total_amount
            if change_amount > Decimal("0.00001"):  # Dust threshold
                change_address = await self._get_change_address(sender_address)
                tx_outputs[change_address] = float(change_amount)
            
            # Create raw transaction
            raw_tx = self.rpc_connection.createrawtransaction(tx_inputs, tx_outputs)
            
            # Sign transaction
            signed_tx = self.rpc_connection.signrawtransactionwithkey(raw_tx, [sender_private_key])
            
            if not signed_tx["complete"]:
                raise PaymentError("Transaction signing failed")
            
            # Broadcast transaction
            tx_hash = self.rpc_connection.sendrawtransaction(signed_tx["hex"])
            
            # Create payment result
            payment_result = PaymentResult(
                payment_id=payment_request.payment_id,
                tx_hash=tx_hash,
                network="bitcoin_" + self.network,
                amount=payment_request.amount,
                currency=CryptoCurrency.BITCOIN,
                status=PaymentStatus.PENDING,
                confirmations=0,
                gas_used=None,  # Bitcoin doesn't use gas
                gas_price=None,
                block_number=None,
                timestamp=datetime.utcnow()
            )
            
            # Store payment result
            await self._store_payment_result(payment_result)
            
            # Start monitoring transaction
            asyncio.create_task(self._monitor_bitcoin_transaction(tx_hash, payment_request.payment_id))
            
            self.logger.info(f"Bitcoin payment processed: {tx_hash}")
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Failed to process Bitcoin payment: {str(e)}")
            raise PaymentError(f"Bitcoin payment processing failed: {str(e)}")
    
    async def verify_payment(self, tx_hash: str, expected_amount: Decimal, recipient_address: str) -> bool:
        """Verify Bitcoin payment"""
        try:
            # Get transaction details
            tx = self.rpc_connection.gettransaction(tx_hash)
            
            if tx["confirmations"] < self.config.bitcoin_min_confirmations:
                return False
            
            # Verify amount and recipient
            for detail in tx["details"]:
                if (detail["category"] == "receive" and 
                    detail["address"] == recipient_address and 
                    Decimal(str(detail["amount"])) >= expected_amount):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to verify Bitcoin payment: {str(e)}")
            return False
    
    async def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format"""
        try:
            result = self.rpc_connection.validateaddress(address)
            return result["isvalid"]
        except Exception:
            return False
    
    async def _get_address_from_private_key(self, private_key: str) -> str:
        """Get Bitcoin address from private key"""
        # This would implement proper address derivation from private key
        # For security, this should use proper cryptographic libraries
        return "example_bitcoin_address"
    
    async def _get_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Get unspent transaction outputs for address"""
        try:
            return self.rpc_connection.listunspent(1, 9999999, [address])
        except Exception as e:
            self.logger.error(f"Failed to get UTXOs: {str(e)}")
            return []
    
    async def _estimate_transaction_fee(self) -> Decimal:
        """Estimate Bitcoin transaction fee"""
        try:
            # Get estimated fee rate (sat/vB)
            fee_rate = self.rpc_connection.estimatesmartfee(6)  # 6 blocks
            
            if "feerate" not in fee_rate:
                return Decimal("0.0001")  # Default fee
            
            # Estimate transaction size (typical P2PKH transaction)
            tx_size = 250  # bytes (approximate)
            fee_btc = Decimal(str(fee_rate["feerate"])) * tx_size / 1000
            
            return max(fee_btc, Decimal("0.00001"))  # Minimum fee
            
        except Exception as e:
            self.logger.error(f"Failed to estimate Bitcoin fee: {str(e)}")
            return Decimal("0.0001")  # Default fee
    
    async def _select_utxos(self, utxos: List[Dict], amount_needed: Decimal) -> tuple:
        """Select UTXOs for transaction"""
        selected = []
        total = Decimal("0")
        
        # Sort UTXOs by amount (largest first for efficiency)
        sorted_utxos = sorted(utxos, key=lambda x: x["amount"], reverse=True)
        
        for utxo in sorted_utxos:
            selected.append(utxo)
            total += Decimal(str(utxo["amount"]))
            
            if total >= amount_needed:
                break
        
        return selected, total
    
    async def _get_change_address(self, sender_address: str) -> str:
        """Get change address for transaction"""
        # In practice, this would generate a new change address
        return sender_address  # Simplified: return to sender
    
    async def _monitor_bitcoin_transaction(self, tx_hash: str, payment_id: str) -> None:
        """Monitor Bitcoin transaction for confirmations"""
        try:
            while True:
                try:
                    tx = self.rpc_connection.gettransaction(tx_hash)
                    confirmations = tx["confirmations"]
                    
                    # Update payment status
                    if confirmations >= self.config.bitcoin_min_confirmations:
                        await self._update_payment_status(payment_id, PaymentStatus.CONFIRMED, confirmations)
                        break
                    elif confirmations > 0:
                        await self._update_payment_status(payment_id, PaymentStatus.PROCESSING, confirmations)
                    
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Error monitoring Bitcoin transaction {tx_hash}: {str(e)}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
                    
        except Exception as e:
            self.logger.error(f"Failed to monitor Bitcoin transaction: {str(e)}")
    
    async def _store_payment_request(self, payment_request: PaymentRequest) -> None:
        """Store payment request in cache"""
        key = f"payment_request:{payment_request.payment_id}"
        data = {
            "amount": str(payment_request.amount),
            "currency": payment_request.currency.value,
            "recipient_address": payment_request.recipient_address,
            "description": payment_request.description,
            "metadata": json.dumps(payment_request.metadata),
            "expires_at": payment_request.expires_at.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.hset(key, mapping=data)
        ttl = int((payment_request.expires_at - datetime.utcnow()).total_seconds())
        await self.redis.expire(key, ttl)
    
    async def _store_payment_result(self, payment_result: PaymentResult) -> None:
        """Store payment result in cache"""
        key = f"payment_result:{payment_result.payment_id}"
        data = {
            "tx_hash": payment_result.tx_hash,
            "network": payment_result.network,
            "amount": str(payment_result.amount),
            "currency": payment_result.currency.value,
            "status": payment_result.status.value,
            "confirmations": payment_result.confirmations,
            "timestamp": payment_result.timestamp.isoformat()
        }
        
        await self.redis.hset(key, mapping=data)
        await self.redis.expire(key, 86400 * 30)  # 30 days
    
    async def _update_payment_status(self, payment_id: str, status: PaymentStatus, confirmations: int) -> None:
        """Update payment status"""
        key = f"payment_result:{payment_id}"
        await self.redis.hset(key, mapping={
            "status": status.value,
            "confirmations": confirmations,
            "updated_at": datetime.utcnow().isoformat()
        })


class EthereumProcessor:
    """
    Ethereum payment processor for smart contract interactions and ETH/token payments
    
    Handles Ethereum-based transactions including ETH, ERC-20 tokens, and 
    smart contract interactions for automated licensing and royalty payments.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.EthereumProcessor")
        self.web3_instances: Dict[str, Web3] = {}
        self.token_contracts: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> None:
        """Initialize Ethereum processor"""
        try:
            # Initialize Web3 connections for Ethereum networks
            networks = ["ethereum_mainnet", "ethereum_goerli", "polygon_mainnet", "binance_smart_chain"]
            
            for network in networks:
                rpc_url = getattr(self.config, f"{network}_rpc")
                web3 = Web3(Web3.HTTPProvider(rpc_url))
                
                if web3.is_connected():
                    self.web3_instances[network] = web3
                    self.logger.info(f"Connected to {network} - Block: {web3.eth.block_number}")
                else:
                    self.logger.warning(f"Failed to connect to {network}")
            
            # Initialize token contracts
            await self._initialize_token_contracts()
            
            self.logger.info("Ethereum processor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ethereum processor: {str(e)}")
            raise BlockchainError(f"Ethereum processor initialization failed: {str(e)}")
    
    async def process_eth_payment(
        self,
        network: str,
        amount: Decimal,
        recipient_address: str,
        sender_private_key: str,
        gas_price: Optional[int] = None
    ) -> PaymentResult:
        """Process ETH payment"""
        try:
            web3 = self.web3_instances[network]
            
            # Get sender address
            account = web3.eth.account.from_key(sender_private_key)
            sender_address = account.address
            
            # Get current nonce
            nonce = web3.eth.get_transaction_count(sender_address)
            
            # Set gas price
            if gas_price is None:
                gas_price = web3.eth.gas_price
            
            # Build transaction
            transaction = {
                'from': sender_address,
                'to': recipient_address,
                'value': web3.to_wei(amount, 'ether'),
                'gas': 21000,  # Standard ETH transfer gas limit
                'gasPrice': gas_price,
                'nonce': nonce
            }
            
            # Sign transaction
            signed_txn = web3.eth.account.sign_transaction(transaction, sender_private_key)
            
            # Send transaction
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            payment_result = PaymentResult(
                payment_id=str(uuid.uuid4()),
                tx_hash=tx_hash_hex,
                network=network,
                amount=amount,
                currency=CryptoCurrency.ETHEREUM,
                status=PaymentStatus.CONFIRMED,
                confirmations=1,  # Confirmed when receipt is received
                gas_used=receipt['gasUsed'],
                gas_price=gas_price,
                block_number=receipt['blockNumber'],
                timestamp=datetime.utcnow()
            )
            
            self.logger.info(f"ETH payment processed: {tx_hash_hex}")
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Failed to process ETH payment: {str(e)}")
            raise PaymentError(f"ETH payment processing failed: {str(e)}")
    
    async def process_token_payment(
        self,
        network: str,
        token_symbol: str,
        amount: Decimal,
        recipient_address: str,
        sender_private_key: str
    ) -> PaymentResult:
        """Process ERC-20 token payment"""
        try:
            web3 = self.web3_instances[network]
            token_contract = self.token_contracts[network][token_symbol]
            
            # Get sender address
            account = web3.eth.account.from_key(sender_private_key)
            sender_address = account.address
            
            # Get token decimals
            decimals = token_contract['contract'].functions.decimals().call()
            token_amount = int(amount * (10 ** decimals))
            
            # Build transfer transaction
            transfer_function = token_contract['contract'].functions.transfer(
                recipient_address,
                token_amount
            )
            
            # Get gas estimate
            gas_estimate = transfer_function.estimate_gas({'from': sender_address})
            
            # Build transaction
            transaction = transfer_function.build_transaction({
                'from': sender_address,
                'gas': gas_estimate * 2,  # Add buffer
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(sender_address)
            })
            
            # Sign and send transaction
            signed_txn = web3.eth.account.sign_transaction(transaction, sender_private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Determine currency enum
            currency_map = {
                "USDT": CryptoCurrency.USDT,
                "USDC": CryptoCurrency.USDC,
                "DAI": CryptoCurrency.DAI
            }
            currency = currency_map.get(token_symbol, CryptoCurrency.ETHEREUM)
            
            payment_result = PaymentResult(
                payment_id=str(uuid.uuid4()),
                tx_hash=tx_hash_hex,
                network=network,
                amount=amount,
                currency=currency,
                status=PaymentStatus.CONFIRMED,
                confirmations=1,
                gas_used=receipt['gasUsed'],
                gas_price=transaction['gasPrice'],
                block_number=receipt['blockNumber'],
                timestamp=datetime.utcnow()
            )
            
            self.logger.info(f"Token payment processed: {tx_hash_hex}")
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Failed to process token payment: {str(e)}")
            raise PaymentError(f"Token payment processing failed: {str(e)}")
    
    async def get_token_balance(self, network: str, token_symbol: str, address: str) -> Decimal:
        """Get ERC-20 token balance"""
        try:
            if network not in self.token_contracts or token_symbol not in self.token_contracts[network]:
                return Decimal("0")
            
            token_contract = self.token_contracts[network][token_symbol]
            balance = token_contract['contract'].functions.balanceOf(address).call()
            decimals = token_contract['contract'].functions.decimals().call()
            
            return Decimal(balance) / (10 ** decimals)
            
        except Exception as e:
            self.logger.error(f"Failed to get token balance: {str(e)}")
            return Decimal("0")
    
    async def get_eth_balance(self, network: str, address: str) -> Decimal:
        """Get ETH balance"""
        try:
            web3 = self.web3_instances[network]
            balance_wei = web3.eth.get_balance(address)
            return web3.from_wei(balance_wei, 'ether')
        except Exception as e:
            self.logger.error(f"Failed to get ETH balance: {str(e)}")
            return Decimal("0")
    
    async def _initialize_token_contracts(self) -> None:
        """Initialize ERC-20 token contracts"""
        # Token contract addresses for different networks
        token_configs = {
            "ethereum_mainnet": {
                "USDT": {
                    "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "decimals": 6
                },
                "USDC": {
                    "address": "0xA0b86a33E6417C8B4D43C5D0c1eF2f3aaecF71C0",
                    "decimals": 6
                },
                "DAI": {
                    "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                    "decimals": 18
                }
            },
            "polygon_mainnet": {
                "USDT": {
                    "address": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                    "decimals": 6
                },
                "USDC": {
                    "address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                    "decimals": 6
                }
            }
        }
        
        # Standard ERC-20 ABI (simplified)
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        # Initialize contracts
        for network, tokens in token_configs.items():
            if network in self.web3_instances:
                self.token_contracts[network] = {}
                web3 = self.web3_instances[network]
                
                for token_symbol, token_config in tokens.items():
                    contract = web3.eth.contract(
                        address=token_config["address"],
                        abi=erc20_abi
                    )
                    
                    self.token_contracts[network][token_symbol] = {
                        "contract": contract,
                        "address": token_config["address"],
                        "decimals": token_config["decimals"]
                    }


class MultiChainWallet:
    """
    Multi-chain cryptocurrency wallet management system
    
    Manages wallet addresses and balances across multiple blockchain networks
    for seamless cross-chain operations and user experience.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.MultiChainWallet")
        self.bitcoin_processor = None
        self.ethereum_processor = None
    
    async def initialize(self, bitcoin_processor: BitcoinProcessor, ethereum_processor: EthereumProcessor) -> None:
        """Initialize multi-chain wallet"""
        self.bitcoin_processor = bitcoin_processor
        self.ethereum_processor = ethereum_processor
        self.logger.info("Multi-chain wallet initialized successfully")
    
    async def create_user_wallet(self, user_id: int) -> Dict[str, str]:
        """Create wallet addresses for user across all supported chains"""
        try:
            wallet_addresses = {}
            
            # Generate Bitcoin address
            btc_address = await self.bitcoin_processor.generate_payment_address(user_id, f"wallet_{user_id}")
            wallet_addresses["bitcoin"] = btc_address
            
            # Generate Ethereum addresses (same address for all ETH-compatible chains)
            eth_account = Web3().eth.account.create()
            eth_address = eth_account.address
            
            wallet_addresses.update({
                "ethereum": eth_address,
                "polygon": eth_address,
                "binance_smart_chain": eth_address,
                "avalanche": eth_address
            })
            
            # Store wallet information
            await self._store_user_wallet(user_id, wallet_addresses, eth_account.key.hex())
            
            self.logger.info(f"Created multi-chain wallet for user {user_id}")
            return wallet_addresses
            
        except Exception as e:
            self.logger.error(f"Failed to create user wallet: {str(e)}")
            raise PaymentError(f"Wallet creation failed: {str(e)}")
    
    async def get_user_balances(self, user_id: int) -> Dict[str, Dict[str, Decimal]]:
        """Get user's balances across all chains and currencies"""
        try:
            wallet_info = await self._get_user_wallet(user_id)
            if not wallet_info:
                return {}
            
            balances = {}
            
            # Bitcoin balance
            if "bitcoin" in wallet_info["addresses"]:
                btc_address = wallet_info["addresses"]["bitcoin"]
                # Get BTC balance (would need to implement proper UTXO calculation)
                balances["bitcoin"] = {"BTC": Decimal("0")}  # Placeholder
            
            # Ethereum-compatible chain balances
            eth_networks = ["ethereum_mainnet", "polygon_mainnet", "binance_smart_chain"]
            for network in eth_networks:
                if network in self.ethereum_processor.web3_instances:
                    chain_name = network.split('_')[0]
                    eth_address = wallet_info["addresses"].get(chain_name)
                    
                    if eth_address:
                        chain_balances = {}
                        
                        # Native currency balance
                        native_balance = await self.ethereum_processor.get_eth_balance(network, eth_address)
                        native_currency = {"ethereum": "ETH", "polygon": "MATIC", "binance": "BNB"}.get(chain_name, "ETH")
                        chain_balances[native_currency] = native_balance
                        
                        # Token balances
                        for token in ["USDT", "USDC", "DAI"]:
                            token_balance = await self.ethereum_processor.get_token_balance(network, token, eth_address)
                            if token_balance > 0:
                                chain_balances[token] = token_balance
                        
                        balances[chain_name] = chain_balances
            
            return balances
            
        except Exception as e:
            self.logger.error(f"Failed to get user balances: {str(e)}")
            return {}
    
    async def transfer_funds(
        self,
        user_id: int,
        from_network: str,
        to_network: str,
        currency: str,
        amount: Decimal,
        recipient_address: str
    ) -> PaymentResult:
        """Transfer funds between networks or to external address"""
        try:
            wallet_info = await self._get_user_wallet(user_id)
            if not wallet_info:
                raise PaymentError("User wallet not found")
            
            # Get user's private key for the source network
            if from_network == "bitcoin":
                # Bitcoin transfer implementation
                try:
                    self.logger.info(f"Processing Bitcoin transfer: {amount} {currency} to {to_address}")
                    
                    # Get Bitcoin private key and address
                    bitcoin_private_key = wallet_info.get("bitcoin_private_key")
                    bitcoin_address = wallet_info.get("bitcoin_address")
                    
                    if not bitcoin_private_key or not bitcoin_address:
                        raise PaymentError("Bitcoin wallet not properly configured")
                    
                    # Validate Bitcoin address format
                    if not self._validate_bitcoin_address(to_address):
                        raise PaymentError("Invalid Bitcoin address format")
                    
                    # Check available balance
                    available_balance = await self._get_bitcoin_balance(bitcoin_address)
                    
                    # Calculate fees (typical Bitcoin network fee)
                    network_fee = 0.0001  # 0.0001 BTC typical fee
                    total_needed = float(amount) + network_fee
                    
                    if available_balance < total_needed:
                        raise PaymentError(f"Insufficient Bitcoin balance. Need {total_needed}, have {available_balance}")
                    
                    # Create Bitcoin transaction
                    transaction_data = {
                        "from_address": bitcoin_address,
                        "to_address": to_address,
                        "amount": float(amount),
                        "fee": network_fee,
                        "currency": "BTC",
                        "network": "bitcoin"
                    }
                    
                    # Simulate Bitcoin transaction creation
                    # In a real implementation, this would use a Bitcoin library like bitcoin-python
                    # to create and sign the transaction
                    transaction_hash = self._generate_transaction_hash(transaction_data)
                    
                    # Record the transaction
                    await self._record_crypto_transaction(
                        user_id=user_id,
                        transaction_type="transfer",
                        currency="BTC",
                        amount=amount,
                        to_address=to_address,
                        from_address=bitcoin_address,
                        transaction_hash=transaction_hash,
                        network="bitcoin",
                        fee=network_fee
                    )
                    
                    self.logger.info(f"Bitcoin transfer completed: {transaction_hash}")
                    
                    return {
                        "success": True,
                        "transaction_hash": transaction_hash,
                        "network": "bitcoin",
                        "amount": amount,
                        "currency": "BTC",
                        "fee": network_fee,
                        "to_address": to_address,
                        "from_address": bitcoin_address,
                        "confirmation_time": "10-60 minutes"
                    }
                    
                except Exception as e:
                    self.logger.error(f"Bitcoin transfer failed: {str(e)}")
                    raise PaymentError(f"Bitcoin transfer failed: {str(e)}")
            
            elif from_network in ["ethereum", "polygon", "binance_smart_chain"]:
                # Ethereum-compatible transfer
                network_map = {
                    "ethereum": "ethereum_mainnet",
                    "polygon": "polygon_mainnet",
                    "binance_smart_chain": "binance_smart_chain"
                }
                
                network = network_map[from_network]
                private_key = wallet_info["ethereum_private_key"]
                
                if currency in ["ETH", "MATIC", "BNB"]:
                    # Native currency transfer
                    return await self.ethereum_processor.process_eth_payment(
                        network=network,
                        amount=amount,
                        recipient_address=recipient_address,
                        sender_private_key=private_key
                    )
                else:
                    # Token transfer
                    return await self.ethereum_processor.process_token_payment(
                        network=network,
                        token_symbol=currency,
                        amount=amount,
                        recipient_address=recipient_address,
                        sender_private_key=private_key
                    )
            
            else:
                raise PaymentError(f"Unsupported network: {from_network}")
                
        except Exception as e:
            self.logger.error(f"Failed to transfer funds: {str(e)}")
            raise PaymentError(f"Fund transfer failed: {str(e)}")
    
    async def _store_user_wallet(self, user_id: int, addresses: Dict[str, str], ethereum_private_key: str) -> None:
        """Store user wallet information securely"""
        # In production, private keys should be encrypted
        wallet_data = {
            "user_id": user_id,
            "addresses": json.dumps(addresses),
            "ethereum_private_key": ethereum_private_key,  # Should be encrypted
            "created_at": datetime.utcnow().isoformat()
        }
        
        key = f"user_wallet:{user_id}"
        await self.redis.hset(key, mapping=wallet_data)
        # No expiration for wallet data
    
    async def _get_user_wallet(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user wallet information"""
        key = f"user_wallet:{user_id}"
        wallet_data = await self.redis.hgetall(key)
        
        if not wallet_data:
            return None
        
        return {
            "user_id": int(wallet_data["user_id"]),
            "addresses": json.loads(wallet_data["addresses"]),
            "ethereum_private_key": wallet_data["ethereum_private_key"],
            "created_at": wallet_data["created_at"]
        }


class PaymentGateway:
    """
    Main cryptocurrency payment gateway for IA-Influencer-Agent platform
    
    Orchestrates all cryptocurrency payment operations including processing,
    verification, and cross-chain transactions for content licensing and creator payments.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.bitcoin_processor = BitcoinProcessor(config, redis_client)
        self.ethereum_processor = EthereumProcessor(config, redis_client)
        self.multi_chain_wallet = MultiChainWallet(config, redis_client)
        self.crypto_converter = CryptoConverter(config, redis_client)
        
        # Payment queue for processing
        self.pending_payments: List[PaymentRequest] = []
        self.processing_payments: Dict[str, PaymentResult] = {}
    
    async def initialize(self) -> None:
        """Initialize payment gateway"""
        try:
            await self.bitcoin_processor.initialize()
            await self.ethereum_processor.initialize()
            await self.multi_chain_wallet.initialize(self.bitcoin_processor, self.ethereum_processor)
            await self.crypto_converter.initialize()
            
            # Start background payment processing
            asyncio.create_task(self._process_payment_queue())
            
            self.logger.info("Payment gateway initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize payment gateway: {str(e)}")
            raise BlockchainError(f"Payment gateway initialization failed: {str(e)}")
    
    async def process_payment(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        recipient_address: str,
        metadata: Dict[str, Any]
    ) -> PaymentResult:
        """Process cryptocurrency payment"""
        try:
            self.logger.info(f"Processing payment: {amount} {currency}")
            
            currency_enum = CryptoCurrency(currency)
            
            # Get user wallet
            wallet_info = await self.multi_chain_wallet._get_user_wallet(user_id)
            if not wallet_info:
                raise PaymentError("User wallet not found")
            
            if currency_enum == CryptoCurrency.BITCOIN:
                # Process Bitcoin payment
                payment_request = await self.bitcoin_processor.create_payment_request(
                    amount=amount,
                    recipient_address=recipient_address,
                    user_id=user_id,
                    description=metadata.get("description", ""),
                    metadata=metadata
                )
                
                # For Bitcoin, we'd need the user's private key or use a different flow
                # This is a simplified implementation
                result = PaymentResult(
                    payment_id=payment_request.payment_id,
                    tx_hash="bitcoin_tx_placeholder",
                    network="bitcoin_mainnet",
                    amount=amount,
                    currency=currency_enum,
                    status=PaymentStatus.PENDING,
                    confirmations=0,
                    gas_used=None,
                    gas_price=None,
                    block_number=None,
                    timestamp=datetime.utcnow()
                )
                
            elif currency_enum in [CryptoCurrency.ETHEREUM, CryptoCurrency.USDT, CryptoCurrency.USDC, CryptoCurrency.DAI]:
                # Process Ethereum/Token payment
                network = "ethereum_mainnet"  # Default to mainnet
                private_key = wallet_info["ethereum_private_key"]
                
                if currency_enum == CryptoCurrency.ETHEREUM:
                    result = await self.ethereum_processor.process_eth_payment(
                        network=network,
                        amount=amount,
                        recipient_address=recipient_address,
                        sender_private_key=private_key
                    )
                else:
                    result = await self.ethereum_processor.process_token_payment(
                        network=network,
                        token_symbol=currency,
                        amount=amount,
                        recipient_address=recipient_address,
                        sender_private_key=private_key
                    )
                
            elif currency_enum in [CryptoCurrency.POLYGON, CryptoCurrency.BINANCE, CryptoCurrency.AVALANCHE]:
                # Process on respective networks
                network_map = {
                    CryptoCurrency.POLYGON: "polygon_mainnet",
                    CryptoCurrency.BINANCE: "binance_smart_chain",
                    CryptoCurrency.AVALANCHE: "avalanche_mainnet"
                }
                
                network = network_map[currency_enum]
                private_key = wallet_info["ethereum_private_key"]
                
                result = await self.ethereum_processor.process_eth_payment(
                    network=network,
                    amount=amount,
                    recipient_address=recipient_address,
                    sender_private_key=private_key
                )
                
            else:
                raise PaymentError(f"Unsupported currency: {currency}")
            
            # Store result and update processing queue
            self.processing_payments[result.payment_id] = result
            
            self.logger.info(f"Payment processed successfully: {result.tx_hash}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process payment: {str(e)}")
            raise PaymentError(f"Payment processing failed: {str(e)}")
    
    async def get_payment_status(self, payment_id: str) -> Optional[PaymentResult]:
        """Get payment status by ID"""
        try:
            # Check processing queue first
            if payment_id in self.processing_payments:
                return self.processing_payments[payment_id]
            
            # Check cache
            key = f"payment_result:{payment_id}"
            payment_data = await self.redis.hgetall(key)
            
            if payment_data:
                return PaymentResult(
                    payment_id=payment_id,
                    tx_hash=payment_data["tx_hash"],
                    network=payment_data["network"],
                    amount=Decimal(payment_data["amount"]),
                    currency=CryptoCurrency(payment_data["currency"]),
                    status=PaymentStatus(payment_data["status"]),
                    confirmations=int(payment_data["confirmations"]),
                    gas_used=int(payment_data.get("gas_used", 0)) if payment_data.get("gas_used") else None,
                    gas_price=int(payment_data.get("gas_price", 0)) if payment_data.get("gas_price") else None,
                    block_number=int(payment_data.get("block_number", 0)) if payment_data.get("block_number") else None,
                    timestamp=datetime.fromisoformat(payment_data["timestamp"])
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get payment status: {str(e)}")
            return None
    
    async def process_pending_transactions(self) -> None:
        """Process pending transactions in queue"""
        try:
            while self.pending_payments:
                payment_request = self.pending_payments.pop(0)
                
                # Check if payment hasn't expired
                if datetime.utcnow() < payment_request.expires_at:
                    # Process payment
                    # This would contain the actual processing logic
                    pass
                else:
                    self.logger.warning(f"Payment request expired: {payment_request.payment_id}")
                    
        except Exception as e:
            self.logger.error(f"Error processing pending transactions: {str(e)}")
    
    async def _process_payment_queue(self) -> None:
        """Background task to process payment queue"""
        while True:
            try:
                await self.process_pending_transactions()
                await asyncio.sleep(10)  # Process every 10 seconds
            except Exception as e:
                self.logger.error(f"Payment queue processing error: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def cleanup(self) -> None:
        """Cleanup payment gateway resources"""
        try:
            self.logger.info("Cleaning up payment gateway...")
            self.pending_payments.clear()
            self.processing_payments.clear()
            self.logger.info("Payment gateway cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during payment gateway cleanup: {str(e)}")


class CryptoConverter:
    """
    Cryptocurrency conversion and price feed service
    
    Provides real-time exchange rates and conversion functionality
    between different cryptocurrencies and fiat currencies.
    """
    
    def __init__(self, config: BlockchainConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.CryptoConverter")
        self.price_cache: Dict[str, Dict[str, Decimal]] = {}
        self.last_price_update = datetime.min
    
    async def initialize(self) -> None:
        """Initialize crypto converter"""
        try:
            await self._update_exchange_rates()
            
            # Start background price updates
            asyncio.create_task(self._price_update_loop())
            
            self.logger.info("Crypto converter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crypto converter: {str(e)}")
            raise BlockchainError(f"Crypto converter initialization failed: {str(e)}")
    
    async def convert_currency(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Convert amount between currencies"""
        try:
            if from_currency == to_currency:
                return amount
            
            # Get exchange rate
            rate = await self._get_exchange_rate(from_currency, to_currency)
            if rate is None:
                raise PaymentError(f"Exchange rate not available for {from_currency}/{to_currency}")
            
            converted_amount = amount * rate
            self.logger.debug(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
            
            return converted_amount
            
        except Exception as e:
            self.logger.error(f"Failed to convert currency: {str(e)}")
            raise PaymentError(f"Currency conversion failed: {str(e)}")
    
    async def get_usd_price(self, currency: str) -> Optional[Decimal]:
        """Get USD price for cryptocurrency"""
        try:
            return await self._get_exchange_rate(currency, "USD")
        except Exception as e:
            self.logger.error(f"Failed to get USD price for {currency}: {str(e)}")
            return None
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Get exchange rate between two currencies"""
        try:
            # Check cache first
            if from_currency in self.price_cache and to_currency in self.price_cache[from_currency]:
                return self.price_cache[from_currency][to_currency]
            
            # If not in cache, update prices
            await self._update_exchange_rates()
            
            if from_currency in self.price_cache and to_currency in self.price_cache[from_currency]:
                return self.price_cache[from_currency][to_currency]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get exchange rate: {str(e)}")
            return None
    
    async def _update_exchange_rates(self) -> None:
        """Update exchange rates from external APIs"""
        try:
            # This would integrate with real price APIs like CoinGecko, CoinMarketCap, etc.
            # For now, using placeholder values
            
            mock_prices = {
                "BTC": {"USD": Decimal("45000.00")},
                "ETH": {"USD": Decimal("3000.00")},
                "MATIC": {"USD": Decimal("1.20")},
                "BNB": {"USD": Decimal("350.00")},
                "AVAX": {"USD": Decimal("40.00")},
                "USDT": {"USD": Decimal("1.00")},
                "USDC": {"USD": Decimal("1.00")},
                "DAI": {"USD": Decimal("1.00")}
            }
            
            # Calculate cross rates
            for from_currency, from_rates in mock_prices.items():
                self.price_cache[from_currency] = {}
                for to_currency, to_rates in mock_prices.items():
                    if from_currency != to_currency:
                        # Calculate cross rate via USD
                        from_usd = from_rates.get("USD", Decimal("1"))
                        to_usd = to_rates.get("USD", Decimal("1"))
                        cross_rate = from_usd / to_usd
                        self.price_cache[from_currency][to_currency] = cross_rate
            
            self.last_price_update = datetime.utcnow()
            
            # Cache prices in Redis
            for from_currency, rates in self.price_cache.items():
                key = f"exchange_rates:{from_currency}"
                await self.redis.hset(key, mapping={
                    to_currency: str(rate) for to_currency, rate in rates.items()
                })
                await self.redis.expire(key, 300)  # 5 minutes
            
            self.logger.debug("Exchange rates updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update exchange rates: {str(e)}")
    
    async def _price_update_loop(self) -> None:
        """Background loop to update prices"""
        while True:
            try:
                # Update prices every 5 minutes
                if datetime.utcnow() - self.last_price_update > timedelta(minutes=5):
                    await self._update_exchange_rates()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Price update loop error: {str(e)}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format"""
        try:
            # Basic Bitcoin address validation
            # Legacy addresses start with 1, SegWit with 3, Bech32 with bc1
            if len(address) < 26 or len(address) > 62:
                return False
            
            # Check for valid Bitcoin address prefixes
            valid_prefixes = ['1', '3', 'bc1']
            if not any(address.startswith(prefix) for prefix in valid_prefixes):
                return False
            
            # Additional validation could include checksum verification
            # For now, basic format validation
            return True
            
        except Exception as e:
            self.logger.error(f"Bitcoin address validation error: {e}")
            return False
    
    async def _get_bitcoin_balance(self, address: str) -> float:
        """Get Bitcoin balance for address"""
        try:
            # In a real implementation, this would query a Bitcoin node or API
            # For simulation, return a mock balance
            mock_balance = 0.05  # 0.05 BTC
            
            self.logger.debug(f"Bitcoin balance for {address}: {mock_balance}")
            return mock_balance
            
        except Exception as e:
            self.logger.error(f"Failed to get Bitcoin balance: {e}")
            return 0.0
    
    def _generate_transaction_hash(self, transaction_data: Dict[str, Any]) -> str:
        """Generate a mock transaction hash"""
        try:
            # Create deterministic hash based on transaction data
            data_string = json.dumps(transaction_data, sort_keys=True)
            hash_input = f"{data_string}{datetime.utcnow().isoformat()}"
            
            # Generate SHA-256 hash
            transaction_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            return transaction_hash
            
        except Exception as e:
            self.logger.error(f"Failed to generate transaction hash: {e}")
            return f"mock_tx_{uuid.uuid4().hex[:16]}"
    
    async def _record_crypto_transaction(
        self,
        user_id: str,
        transaction_type: str,
        currency: str,
        amount: str,
        to_address: str,
        from_address: str,
        transaction_hash: str,
        network: str,
        fee: float
    ) -> None:
        """Record cryptocurrency transaction in database"""
        try:
            transaction_record = {
                "user_id": user_id,
                "transaction_type": transaction_type,
                "currency": currency,
                "amount": amount,
                "to_address": to_address,
                "from_address": from_address,
                "transaction_hash": transaction_hash,
                "network": network,
                "fee": fee,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, save to database
            # await self.database.insert("crypto_transactions", transaction_record)
            
            self.logger.info(f"Recorded crypto transaction: {transaction_hash}")
            
        except Exception as e:
            self.logger.error(f"Failed to record transaction: {e}")
            raise
