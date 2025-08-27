"""
Main Blockchain Manager for IA-Influencer-Agent Platform

This is the central blockchain management system that orchestrates all blockchain
operations including smart contracts, NFTs, consensus, payments, governance, and
cross-chain functionality for content creators and rights protection.

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import json

from sqlalchemy.ext.asyncio import AsyncSession
from web3 import Web3
from web3.middleware import geth_poa_middleware
import redis.asyncio as redis

from .smart_contracts import SmartContractManager
from .nft_system import NFTMinter, NFTMarketplace
from .consensus_engine import ConsensusManager
from .crypto_payments import PaymentGateway
from .governance_system import DecentralizedGovernance
from .cross_chain_bridge import CrossChainBridge
from .ipfs_integration import IPFSContentManager
from .blockchain_analytics import OnChainAnalytics
from .defi_protocols import YieldFarming, LiquidityPoolManager
from .oracle_services import PriceOracle, ContentVerificationOracle
from .blockchain_security import SecurityAuditor
from .wallet_integration import WalletManager
from .blockchain_indexer import IndexerManager

from ...config.blockchain_config import BlockchainConfig
from ...core.exceptions import BlockchainError, ValidationError
from ...database.models import User, ContentItem, Transaction, BlockchainRecord

logger = logging.getLogger(__name__)


@dataclass
class BlockchainNetwork:
    """Blockchain network configuration"""
    name: str
    rpc_url: str
    chain_id: int
    native_currency: str
    explorer_url: str
    is_testnet: bool


@dataclass
class TransactionResult:
    """Result of blockchain transaction"""
    tx_hash: str
    block_number: int
    gas_used: int
    status: str
    timestamp: datetime
    network: str


class BlockchainManager:
    """
    Central blockchain management system for IA-Influencer-Agent platform.
    
    Manages all blockchain operations including smart contracts, NFTs, 
    cryptocurrency payments, governance, and content protection.
    """
    
    def __init__(
        self,
        config: BlockchainConfig,
        redis_client: redis.Redis,
        db_session: AsyncSession
    ):
        self.config = config
        self.redis = redis_client
        self.db_session = db_session
        
        # Network configurations
        self.networks = self._initialize_networks()
        self.web3_instances: Dict[str, Web3] = {}
        
        # Core managers
        self.smart_contract_manager = SmartContractManager(config, redis_client)
        self.nft_minter = NFTMinter(config)
        self.nft_marketplace = NFTMarketplace(config, redis_client)
        self.consensus_manager = ConsensusManager(config)
        self.payment_gateway = PaymentGateway(config, redis_client)
        self.governance = DecentralizedGovernance(config)
        self.cross_chain_bridge = CrossChainBridge(config)
        self.ipfs_manager = IPFSContentManager(config)
        self.analytics = OnChainAnalytics(config, redis_client)
        self.yield_farming = YieldFarming(config)
        self.liquidity_manager = LiquidityPoolManager(config)
        self.price_oracle = PriceOracle(config)
        self.content_oracle = ContentVerificationOracle(config)
        self.security_auditor = SecurityAuditor(config)
        self.wallet_manager = WalletManager(config)
        self.indexer_manager = IndexerManager(config, db_session)
        
        # State management
        self.active_networks: List[str] = []
        self.network_status: Dict[str, bool] = {}
        self.last_block_numbers: Dict[str, int] = {}
        
        logger.info("BlockchainManager initialized successfully")
    
    def _initialize_networks(self) -> Dict[str, BlockchainNetwork]:
        """Initialize blockchain network configurations"""
        return {
            "ethereum_mainnet": BlockchainNetwork(
                name="Ethereum Mainnet",
                rpc_url=self.config.ethereum_mainnet_rpc,
                chain_id=1,
                native_currency="ETH",
                explorer_url="https://etherscan.io",
                is_testnet=False
            ),
            "ethereum_goerli": BlockchainNetwork(
                name="Ethereum Goerli",
                rpc_url=self.config.ethereum_goerli_rpc,
                chain_id=5,
                native_currency="ETH",
                explorer_url="https://goerli.etherscan.io",
                is_testnet=True
            ),
            "polygon_mainnet": BlockchainNetwork(
                name="Polygon Mainnet",
                rpc_url=self.config.polygon_mainnet_rpc,
                chain_id=137,
                native_currency="MATIC",
                explorer_url="https://polygonscan.com",
                is_testnet=False
            ),
            "binance_smart_chain": BlockchainNetwork(
                name="Binance Smart Chain",
                rpc_url=self.config.bsc_mainnet_rpc,
                chain_id=56,
                native_currency="BNB",
                explorer_url="https://bscscan.com",
                is_testnet=False
            ),
            "avalanche_mainnet": BlockchainNetwork(
                name="Avalanche C-Chain",
                rpc_url=self.config.avalanche_mainnet_rpc,
                chain_id=43114,
                native_currency="AVAX",
                explorer_url="https://snowtrace.io",
                is_testnet=False
            )
        }
    
    async def initialize(self) -> None:
        """Initialize blockchain connections and services"""
        try:
            logger.info("Initializing blockchain connections...")
            
            # Initialize Web3 connections for all networks
            for network_name, network_config in self.networks.items():
                try:
                    web3 = Web3(Web3.HTTPProvider(network_config.rpc_url))
                    
                    # Add PoA middleware for networks that need it
                    if network_name in ["binance_smart_chain", "polygon_mainnet"]:
                        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    # Test connection
                    if await self._test_network_connection(web3):
                        self.web3_instances[network_name] = web3
                        self.active_networks.append(network_name)
                        self.network_status[network_name] = True
                        
                        # Get latest block number
                        latest_block = web3.eth.block_number
                        self.last_block_numbers[network_name] = latest_block
                        
                        logger.info(f"Connected to {network_config.name} (Block: {latest_block})")
                    else:
                        self.network_status[network_name] = False
                        logger.warning(f"Failed to connect to {network_config.name}")
                        
                except Exception as e:
                    logger.error(f"Error connecting to {network_name}: {str(e)}")
                    self.network_status[network_name] = False
            
            # Initialize core managers
            await self.smart_contract_manager.initialize()
            await self.consensus_manager.initialize()
            await self.payment_gateway.initialize()
            await self.governance.initialize()
            await self.cross_chain_bridge.initialize()
            await self.ipfs_manager.initialize()
            await self.analytics.initialize()
            await self.indexer_manager.initialize()
            
            # Start background tasks
            asyncio.create_task(self._monitor_networks())
            asyncio.create_task(self._process_pending_transactions())
            asyncio.create_task(self._update_analytics())
            
            logger.info(f"Blockchain manager initialized with {len(self.active_networks)} active networks")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain manager: {str(e)}")
            raise BlockchainError(f"Initialization failed: {str(e)}")
    
    async def _test_network_connection(self, web3: Web3) -> bool:
        """Test blockchain network connection"""
        try:
            # Test if we can get the latest block
            latest_block = web3.eth.block_number
            return latest_block > 0
        except Exception:
            return False
    
    async def register_content_rights(
        self,
        user_id: int,
        content_id: int,
        content_hash: str,
        metadata: Dict[str, Any],
        network: str = "polygon_mainnet"
    ) -> TransactionResult:
        """
        Register content rights on blockchain for immutable protection
        
        This creates an immutable record of content ownership and metadata
        that can be used for copyright protection and licensing.
        """
        try:
            logger.info(f"Registering content rights for content {content_id}")
            
            # Validate network
            if network not in self.active_networks:
                raise ValidationError(f"Network {network} is not active")
            
            # Get user wallet address
            user_wallet = await self.wallet_manager.get_user_wallet(user_id)
            if not user_wallet:
                raise ValidationError("User wallet not found")
            
            # Prepare registration data
            registration_data = {
                "content_id": content_id,
                "content_hash": content_hash,
                "owner_address": user_wallet.address,
                "timestamp": int(datetime.utcnow().timestamp()),
                "metadata": metadata
            }
            
            # Register on smart contract
            tx_result = await self.smart_contract_manager.register_content(
                network=network,
                registration_data=registration_data,
                from_address=user_wallet.address
            )
            
            # Store in database
            blockchain_record = BlockchainRecord(
                user_id=user_id,
                content_id=content_id,
                transaction_hash=tx_result.tx_hash,
                network=network,
                action="content_registration",
                data=registration_data
            )
            self.db_session.add(blockchain_record)
            await self.db_session.commit()
            
            # Update analytics
            await self.analytics.track_content_registration(
                content_id=content_id,
                network=network,
                tx_hash=tx_result.tx_hash
            )
            
            logger.info(f"Content rights registered successfully: {tx_result.tx_hash}")
            return tx_result
            
        except Exception as e:
            logger.error(f"Failed to register content rights: {str(e)}")
            raise BlockchainError(f"Content registration failed: {str(e)}")
    
    async def create_nft_license(
        self,
        user_id: int,
        content_id: int,
        license_terms: Dict[str, Any],
        price: Decimal,
        network: str = "polygon_mainnet"
    ) -> TransactionResult:
        """
        Create NFT-based license for content monetization
        
        This mints an NFT representing licensing rights for the content,
        enabling automated licensing and royalty distribution.
        """
        try:
            logger.info(f"Creating NFT license for content {content_id}")
            
            # Validate network
            if network not in self.active_networks:
                raise ValidationError(f"Network {network} is not active")
            
            # Get content metadata
            content_metadata = await self._get_content_metadata(content_id)
            
            # Upload metadata to IPFS
            ipfs_hash = await self.ipfs_manager.upload_metadata({
                "name": f"License - {content_metadata.get('title', 'Untitled')}",
                "description": license_terms.get("description", ""),
                "content_id": content_id,
                "license_terms": license_terms,
                "creator": content_metadata.get("creator", ""),
                "created_at": datetime.utcnow().isoformat()
            })
            
            # Mint NFT
            mint_result = await self.nft_minter.mint_license_nft(
                network=network,
                recipient_address=await self.wallet_manager.get_user_address(user_id),
                token_uri=f"ipfs://{ipfs_hash}",
                license_data=license_terms,
                price=price
            )
            
            # List on marketplace
            await self.nft_marketplace.list_license(
                network=network,
                token_id=mint_result["token_id"],
                price=price,
                license_terms=license_terms
            )
            
            # Store in database
            blockchain_record = BlockchainRecord(
                user_id=user_id,
                content_id=content_id,
                transaction_hash=mint_result["tx_hash"],
                network=network,
                action="nft_license_creation",
                data={
                    "token_id": mint_result["token_id"],
                    "ipfs_hash": ipfs_hash,
                    "license_terms": license_terms,
                    "price": str(price)
                }
            )
            self.db_session.add(blockchain_record)
            await self.db_session.commit()
            
            logger.info(f"NFT license created successfully: {mint_result['tx_hash']}")
            return TransactionResult(
                tx_hash=mint_result["tx_hash"],
                block_number=mint_result["block_number"],
                gas_used=mint_result["gas_used"],
                status="success",
                timestamp=datetime.utcnow(),
                network=network
            )
            
        except Exception as e:
            logger.error(f"Failed to create NFT license: {str(e)}")
            raise BlockchainError(f"NFT license creation failed: {str(e)}")
    
    async def process_crypto_payment(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        recipient_address: str,
        metadata: Dict[str, Any]
    ) -> TransactionResult:
        """
        Process cryptocurrency payment for content licensing or services
        
        Supports Bitcoin, Ethereum, and other major cryptocurrencies
        as specified in the cahier des charges.
        """
        try:
            logger.info(f"Processing crypto payment: {amount} {currency}")
            
            # Validate currency support
            supported_currencies = ["BTC", "ETH", "MATIC", "BNB", "AVAX", "USDT", "USDC"]
            if currency not in supported_currencies:
                raise ValidationError(f"Currency {currency} is not supported")
            
            # Process payment through payment gateway
            payment_result = await self.payment_gateway.process_payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                recipient_address=recipient_address,
                metadata=metadata
            )
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                currency=currency,
                transaction_hash=payment_result.tx_hash,
                network=payment_result.network,
                status="completed",
                metadata=metadata
            )
            self.db_session.add(transaction)
            await self.db_session.commit()
            
            # Update analytics
            await self.analytics.track_payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                tx_hash=payment_result.tx_hash
            )
            
            logger.info(f"Crypto payment processed successfully: {payment_result.tx_hash}")
            return payment_result
            
        except Exception as e:
            logger.error(f"Failed to process crypto payment: {str(e)}")
            raise BlockchainError(f"Payment processing failed: {str(e)}")
    
    async def distribute_royalties(
        self,
        content_id: int,
        total_revenue: Decimal,
        distribution_rules: Dict[str, Any]
    ) -> List[TransactionResult]:
        """
        Automatically distribute royalties to content creators and stakeholders
        
        Uses smart contracts to ensure transparent and automatic distribution
        based on predefined rules and percentages.
        """
        try:
            logger.info(f"Distributing royalties for content {content_id}: {total_revenue}")
            
            # Get distribution smart contract
            royalty_contract = await self.smart_contract_manager.get_royalty_contract()
            
            # Calculate distributions
            distributions = await self._calculate_royalty_distributions(
                content_id=content_id,
                total_revenue=total_revenue,
                rules=distribution_rules
            )
            
            distribution_results = []
            
            # Execute distributions
            for distribution in distributions:
                result = await royalty_contract.distribute(
                    recipient=distribution["address"],
                    amount=distribution["amount"],
                    content_id=content_id,
                    metadata=distribution["metadata"]
                )
                
                distribution_results.append(result)
                
                # Record distribution
                blockchain_record = BlockchainRecord(
                    user_id=distribution["user_id"],
                    content_id=content_id,
                    transaction_hash=result.tx_hash,
                    network=result.network,
                    action="royalty_distribution",
                    data=distribution
                )
                self.db_session.add(blockchain_record)
            
            await self.db_session.commit()
            
            # Update analytics
            await self.analytics.track_royalty_distribution(
                content_id=content_id,
                total_amount=total_revenue,
                distributions=distributions
            )
            
            logger.info(f"Royalty distribution completed: {len(distribution_results)} transactions")
            return distribution_results
            
        except Exception as e:
            logger.error(f"Failed to distribute royalties: {str(e)}")
            raise BlockchainError(f"Royalty distribution failed: {str(e)}")
    
    async def create_governance_proposal(
        self,
        proposer_id: int,
        title: str,
        description: str,
        proposal_type: str,
        voting_period: timedelta,
        execution_data: Dict[str, Any]
    ) -> TransactionResult:
        """
        Create governance proposal for decentralized platform management
        
        Enables community governance of platform parameters, upgrades,
        and policy decisions through democratic voting.
        """
        try:
            logger.info(f"Creating governance proposal: {title}")
            
            # Validate proposer has sufficient governance tokens
            proposer_balance = await self.governance.get_voting_power(proposer_id)
            if proposer_balance < self.config.min_proposal_stake:
                raise ValidationError("Insufficient voting power to create proposal")
            
            # Create proposal
            proposal_result = await self.governance.create_proposal(
                proposer_id=proposer_id,
                title=title,
                description=description,
                proposal_type=proposal_type,
                voting_period=voting_period,
                execution_data=execution_data
            )
            
            # Notify stakeholders
            await self._notify_governance_stakeholders(
                proposal_id=proposal_result["proposal_id"],
                title=title,
                proposer_id=proposer_id
            )
            
            # Record proposal
            blockchain_record = BlockchainRecord(
                user_id=proposer_id,
                content_id=None,
                transaction_hash=proposal_result["tx_hash"],
                network=proposal_result["network"],
                action="governance_proposal",
                data={
                    "proposal_id": proposal_result["proposal_id"],
                    "title": title,
                    "description": description,
                    "proposal_type": proposal_type,
                    "voting_deadline": (datetime.utcnow() + voting_period).isoformat()
                }
            )
            self.db_session.add(blockchain_record)
            await self.db_session.commit()
            
            logger.info(f"Governance proposal created: {proposal_result['proposal_id']}")
            return TransactionResult(
                tx_hash=proposal_result["tx_hash"],
                block_number=proposal_result["block_number"],
                gas_used=proposal_result["gas_used"],
                status="success",
                timestamp=datetime.utcnow(),
                network=proposal_result["network"]
            )
            
        except Exception as e:
            logger.error(f"Failed to create governance proposal: {str(e)}")
            raise BlockchainError(f"Proposal creation failed: {str(e)}")
    
    async def bridge_assets(
        self,
        user_id: int,
        amount: Decimal,
        token: str,
        from_network: str,
        to_network: str
    ) -> TransactionResult:
        """
        Bridge assets between different blockchain networks
        
        Enables cross-chain functionality for multi-network operations
        and asset mobility across supported blockchain ecosystems.
        """
        try:
            logger.info(f"Bridging {amount} {token} from {from_network} to {to_network}")
            
            # Validate networks
            if from_network not in self.active_networks or to_network not in self.active_networks:
                raise ValidationError("Source or destination network not active")
            
            # Execute bridge operation
            bridge_result = await self.cross_chain_bridge.bridge_tokens(
                user_id=user_id,
                amount=amount,
                token=token,
                from_network=from_network,
                to_network=to_network
            )
            
            # Record bridge operation
            blockchain_record = BlockchainRecord(
                user_id=user_id,
                content_id=None,
                transaction_hash=bridge_result["tx_hash"],
                network=from_network,
                action="cross_chain_bridge",
                data={
                    "amount": str(amount),
                    "token": token,
                    "from_network": from_network,
                    "to_network": to_network,
                    "bridge_id": bridge_result["bridge_id"]
                }
            )
            self.db_session.add(blockchain_record)
            await self.db_session.commit()
            
            logger.info(f"Asset bridge completed: {bridge_result['tx_hash']}")
            return TransactionResult(
                tx_hash=bridge_result["tx_hash"],
                block_number=bridge_result["block_number"],
                gas_used=bridge_result["gas_used"],
                status="pending",
                timestamp=datetime.utcnow(),
                network=from_network
            )
            
        except Exception as e:
            logger.error(f"Failed to bridge assets: {str(e)}")
            raise BlockchainError(f"Asset bridging failed: {str(e)}")
    
    async def get_network_status(self) -> Dict[str, Any]:
        """Get status of all blockchain networks"""
        status = {}
        
        for network_name in self.networks.keys():
            if network_name in self.active_networks:
                web3 = self.web3_instances[network_name]
                latest_block = web3.eth.block_number
                gas_price = web3.eth.gas_price
                
                status[network_name] = {
                    "active": True,
                    "latest_block": latest_block,
                    "gas_price": gas_price,
                    "network_id": web3.net.version,
                    "connected_peers": len(web3.net.peer_count) if hasattr(web3.net, 'peer_count') else 0
                }
            else:
                status[network_name] = {
                    "active": False,
                    "error": "Not connected"
                }
        
        return status
    
    async def get_user_blockchain_assets(self, user_id: int) -> Dict[str, Any]:
        """Get user's blockchain assets across all networks"""
        assets = {}
        user_wallet = await self.wallet_manager.get_user_wallet(user_id)
        
        if not user_wallet:
            return assets
        
        for network_name in self.active_networks:
            network_assets = await self._get_network_assets(user_wallet.address, network_name)
            assets[network_name] = network_assets
        
        return assets
    
    async def _calculate_royalty_distributions(
        self,
        content_id: int,
        total_revenue: Decimal,
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate royalty distributions based on rules"""
        # This would implement complex royalty calculation logic
        # For now, returning a simplified structure
        return [
            {
                "user_id": rules.get("creator_id"),
                "address": rules.get("creator_address"),
                "amount": total_revenue * Decimal("0.8"),  # 80% to creator
                "metadata": {"role": "creator", "percentage": 80}
            },
            {
                "user_id": rules.get("platform_id"),
                "address": rules.get("platform_address"),
                "amount": total_revenue * Decimal("0.2"),  # 20% to platform
                "metadata": {"role": "platform", "percentage": 20}
            }
        ]
    
    async def _get_content_metadata(self, content_id: int) -> Dict[str, Any]:
        """Get content metadata from database"""
        # Implementation would query the content database
        return {
            "title": "Sample Content",
            "creator": "Creator Name",
            "content_type": "audio"
        }
    
    async def _get_network_assets(self, address: str, network: str) -> Dict[str, Any]:
        """Get user's assets on specific network"""
        web3 = self.web3_instances[network]
        
        # Get native balance
        native_balance = web3.eth.get_balance(address)
        
        # Get token balances (would need to implement token contract calls)
        token_balances = {}
        
        return {
            "native_balance": web3.from_wei(native_balance, 'ether'),
            "token_balances": token_balances,
            "nft_count": await self._get_nft_count(address, network)
        }
    
    async def _get_nft_count(self, address: str, network: str) -> int:
        """Get NFT count for address on network"""
        # Implementation would query NFT contracts
        return 0
    
    async def _notify_governance_stakeholders(
        self,
        proposal_id: int,
        title: str,
        proposer_id: int
    ) -> None:
        """Notify stakeholders about new governance proposal"""
        # Implementation would send notifications to governance token holders
        pass
    
    async def _monitor_networks(self) -> None:
        """Background task to monitor network health"""
        while True:
            try:
                for network_name in self.active_networks:
                    web3 = self.web3_instances[network_name]
                    current_block = web3.eth.block_number
                    
                    # Check if network is progressing
                    if current_block > self.last_block_numbers[network_name]:
                        self.last_block_numbers[network_name] = current_block
                        self.network_status[network_name] = True
                    else:
                        logger.warning(f"Network {network_name} appears stalled")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Network monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _process_pending_transactions(self) -> None:
        """Background task to process pending transactions"""
        while True:
            try:
                # Process pending transactions from queue
                await self.payment_gateway.process_pending_transactions()
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Pending transaction processing error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _update_analytics(self) -> None:
        """Background task to update blockchain analytics"""
        while True:
            try:
                await self.analytics.update_metrics()
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Analytics update error: {str(e)}")
                await asyncio.sleep(300)
    
    async def cleanup(self) -> None:
        """Cleanup blockchain connections and resources"""
        try:
            logger.info("Cleaning up blockchain manager...")
            
            # Close all connections and cleanup managers
            await self.smart_contract_manager.cleanup()
            await self.consensus_manager.cleanup()
            await self.payment_gateway.cleanup()
            await self.governance.cleanup()
            await self.cross_chain_bridge.cleanup()
            await self.ipfs_manager.cleanup()
            await self.analytics.cleanup()
            await self.indexer_manager.cleanup()
            
            # Clear Web3 instances
            self.web3_instances.clear()
            self.active_networks.clear()
            
            logger.info("Blockchain manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during blockchain manager cleanup: {str(e)}")
