"""Blockchain Module Index - IA-Influencer-Agent Platform
===================================================

This module provides centralized access to all blockchain infrastructure components
for the IA-Influencer-Agent platform. It serves as the main entry point for
content protection, smart contracts, NFT systems, cryptocurrency payments,
consensus mechanisms, and decentralized governance.

Key Features:
- Unified blockchain infrastructure access
- Content rights management and protection
- Automated licensing and royalty distribution
- NFT-based content monetization
- Multi-chain cryptocurrency payments (Bitcoin, Ethereum)
- Proof-of-stake consensus mechanism
- Decentralized governance and voting
- Treasury management and fund allocation

Quick Start:
-----------
```python
from backend.business.blockchain import BlockchainPlatform

# Initialize blockchain platform
blockchain = BlockchainPlatform()
await blockchain.initialize()

# Register content rights
rights_result = await blockchain.register_content_rights(
    user_id="creator_123",
    content_id="content_456",
    content_hash="0x...",
    metadata={"title": "My Song", "type": "audio"}
)

# Create NFT license
license_result = await blockchain.create_nft_license(
    user_id="creator_123",
    content_id="content_456",
    license_terms={"type": "commercial", "duration": "1_year"},
    price=Decimal("99.99")
)

# Process crypto payment
payment_result = await blockchain.process_crypto_payment(
    user_id="buyer_789",
    amount=Decimal("99.99"),
    currency="ETH",
    recipient_address="0x..."
)
```

Author: Expert Blockchain Development Team
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from contextlib import asynccontextmanager

# Core blockchain components
from .blockchain_manager import (
    BlockchainManager,
    ContentRights,
    LicenseTerms,
    PaymentMetadata
)

# Smart contract infrastructure
from .smart_contracts import (
    SmartContractManager,
    ContentProtectionContract,
    LicensingContract,
    RoyaltyDistributionContract,
    GovernanceContract,
    StakingContract
)

# NFT system components
from .nft_system import (
    NFTSystem,
    NFTMinter,
    NFTMarketplace,
    NFTLicenseManager,
    NFTRoyaltyManager,
    NFTMetadataManager,
    NFTMetadata,
    LicenseNFT,
    MarketplaceListing,
    RoyaltySplit
)

# Cryptocurrency payment processing
from .crypto_payments import (
    CryptoPaymentSystem,
    BitcoinProcessor,
    EthereumProcessor,
    MultiChainWallet,
    PaymentGateway,
    CryptoConverter,
    PaymentRequest,
    PaymentResult,
    WalletBalance
)

# Consensus engine
from .consensus_engine import (
    ConsensusEngine,
    ProofOfStakeConsensus,
    ValidatorNetwork,
    BlockValidator,
    TransactionPool,
    Validator,
    Block,
    Transaction,
    ConsensusState
)

# Governance system
from .governance_system import (
    GovernanceSystem,
    GovernanceTokenManager,
    ProposalManager,
    TreasuryManager,
    ProposalType,
    ProposalStatus,
    VoteType,
    ProposalMetadata,
    VotingPower,
    TreasuryAllocation,
    create_governance_proposal,
    vote_on_governance_proposal,
    get_user_voting_power,
    execute_governance_proposal
)

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import BlockchainError, ValidationError
from backend.core.database import get_async_session

# Configure logging
logger = get_logger(__name__)

class BlockchainPlatform:
    """    Main blockchain platform orchestrator providing unified access
    to all blockchain infrastructure components
    """    
    def __init__(self):
        self.blockchain_manager: Optional[BlockchainManager] = None
        self.nft_system: Optional[NFTSystem] = None
        self.crypto_payments: Optional[CryptoPaymentSystem] = None
        self.consensus_engine: Optional[ConsensusEngine] = None
        self.governance_system: Optional[GovernanceSystem] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize all blockchain components"""        try:
            logger.info("Initializing blockchain platform...")
            
            # Initialize blockchain manager
            self.blockchain_manager = BlockchainManager()
            await self.blockchain_manager.initialize()
            
            # Initialize NFT system
            self.nft_system = NFTSystem()
            await self.nft_system.initialize()
            
            # Initialize crypto payments
            self.crypto_payments = CryptoPaymentSystem()
            await self.crypto_payments.initialize()
            
            # Initialize consensus engine
            self.consensus_engine = ConsensusEngine()
            await self.consensus_engine.initialize()
            
            # Initialize governance system
            self.governance_system = GovernanceSystem()
            await self.governance_system.initialize()
            
            self.initialized = True
            logger.info("Blockchain platform initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain platform: {str(e)}")
            raise BlockchainError(f"Platform initialization failed: {str(e)}")
    
    def _check_initialized(self):
        """Check if platform is initialized"""        if not self.initialized:
            raise BlockchainError("Blockchain platform not initialized. Call initialize() first.")
    
    # Content Rights Management
    async def register_content_rights(
        self,
        user_id: str,
        content_id: str,
        content_hash: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register content rights on blockchain"""        self._check_initialized()
        return await self.blockchain_manager.register_content_rights(
            user_id, content_id, content_hash, metadata
        )
    
    async def verify_content_ownership(
        self,
        content_hash: str,
        claimed_owner: str
    ) -> Dict[str, Any]:
        """Verify content ownership on blockchain"""        self._check_initialized()
        return await self.blockchain_manager.verify_content_ownership(
            content_hash, claimed_owner
        )
    
    # NFT Licensing
    async def create_nft_license(
        self,
        user_id: str,
        content_id: str,
        license_terms: Dict[str, Any],
        price: Decimal,
        royalty_percentage: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Create NFT-based content license"""        self._check_initialized()
        return await self.blockchain_manager.create_nft_license(
            user_id, content_id, license_terms, price, royalty_percentage
        )
    
    async def purchase_nft_license(
        self,
        buyer_id: str,
        nft_token_id: int,
        payment_currency: str
    ) -> Dict[str, Any]:
        """Purchase NFT license"""        self._check_initialized()
        return await self.nft_system.purchase_license(
            buyer_id, nft_token_id, payment_currency
        )
    
    # Cryptocurrency Payments
    async def process_crypto_payment(
        self,
        user_id: str,
        amount: Decimal,
        currency: str,
        recipient_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process cryptocurrency payment"""        self._check_initialized()
        return await self.blockchain_manager.process_crypto_payment(
            user_id, amount, currency, recipient_address, metadata
        )
    
    async def get_wallet_balance(
        self,
        user_id: str,
        currency: str
    ) -> Dict[str, Any]:
        """Get user wallet balance"""        self._check_initialized()
        return await self.crypto_payments.get_wallet_balance(user_id, currency)
    
    async def convert_cryptocurrency(
        self,
        from_currency: str,
        to_currency: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Convert between cryptocurrencies"""        self._check_initialized()
        return await self.crypto_payments.convert_currency(
            from_currency, to_currency, amount
        )
    
    # Royalty Distribution
    async def distribute_royalties(
        self,
        content_id: str,
        total_amount: Decimal,
        currency: str,
        distribution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distribute royalties to content creators"""        self._check_initialized()
        return await self.blockchain_manager.distribute_royalties(
            content_id, total_amount, currency, distribution_data
        )
    
    # Governance Operations
    async def create_governance_proposal(
        self,
        proposer: str,
        title: str,
        description: str,
        proposal_type: ProposalType,
        targets: List[str] = None,
        values: List[int] = None,
        calldatas: List[str] = None
    ) -> Dict[str, Any]:
        """Create governance proposal"""        self._check_initialized()
        return await self.governance_system.create_proposal(
            proposer, title, description, proposal_type, targets, values, calldatas
        )
    
    async def vote_on_proposal(
        self,
        voter: str,
        proposal_id: int,
        vote_type: VoteType,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Vote on governance proposal"""        self._check_initialized()
        return await self.governance_system.vote_on_proposal(
            voter, proposal_id, vote_type, reason
        )
    
    async def get_voting_power(
        self,
        user_address: str,
        block_number: Optional[int] = None
    ) -> VotingPower:
        """Get user voting power"""        self._check_initialized()
        return await self.governance_system.get_voting_power(user_address, block_number)
    
    # Validator Operations
    async def become_validator(
        self,
        user_id: str,
        stake_amount: Decimal
    ) -> Dict[str, Any]:
        """Register as validator"""        self._check_initialized()
        return await self.consensus_engine.register_validator(user_id, stake_amount)
    
    async def delegate_stake(
        self,
        delegator: str,
        validator: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Delegate stake to validator"""        self._check_initialized()
        return await self.consensus_engine.delegate_stake(delegator, validator, amount)
    
    # Analytics and Monitoring
    async def get_blockchain_metrics(self) -> Dict[str, Any]:
        """Get blockchain performance metrics"""        self._check_initialized()
        
        try:
            metrics = {
                "consensus": await self.consensus_engine.get_metrics(),
                "nft_system": await self.nft_system.get_metrics(),
                "payments": await self.crypto_payments.get_metrics(),
                "governance": await self.governance_system.get_metrics() if hasattr(self.governance_system, 'get_metrics') else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get blockchain metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_blockchain_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive blockchain summary for user"""        self._check_initialized()
        
        try:
            summary = {
                "user_id": user_id,
                "content_rights": await self._get_user_content_rights(user_id),
                "nft_licenses": await self._get_user_nft_licenses(user_id),
                "wallet_balances": await self._get_user_wallet_balances(user_id),
                "voting_power": await self._get_user_voting_summary(user_id),
                "validator_status": await self._get_user_validator_status(user_id),
                "royalty_earnings": await self._get_user_royalty_earnings(user_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get user blockchain summary: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive blockchain platform health check"""        try:
            health_status = {
                "platform_initialized": self.initialized,
                "blockchain_manager": self.blockchain_manager is not None and await self._check_component_health("blockchain_manager"),
                "nft_system": self.nft_system is not None and await self._check_component_health("nft_system"),
                "crypto_payments": self.crypto_payments is not None and await self._check_component_health("crypto_payments"),
                "consensus_engine": self.consensus_engine is not None and await self._check_component_health("consensus_engine"),
                "governance_system": self.governance_system is not None and await self._check_component_health("governance_system"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            all_healthy = all(health_status[key] for key in health_status if key != "timestamp")
            
            return {
                "success": True,
                "healthy": all_healthy,
                "components": health_status
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e)
            }
    
    # Private helper methods
    async def _get_user_content_rights(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's registered content rights"""        # Implementation would query database
        return []
    
    async def _get_user_nft_licenses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's NFT licenses"""        # Implementation would query NFT system
        return []
    
    async def _get_user_wallet_balances(self, user_id: str) -> Dict[str, str]:
        """Get user's wallet balances"""        # Implementation would query crypto payment system
        return {}
    
    async def _get_user_voting_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's voting power and history"""        # Implementation would query governance system
        return {}
    
    async def _get_user_validator_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's validator status"""        # Implementation would query consensus engine
        return {}
    
    async def _get_user_royalty_earnings(self, user_id: str) -> Dict[str, Any]:
        """Get user's royalty earnings"""        # Implementation would query royalty system
        return {}
    
    async def _check_component_health(self, component_name: str) -> bool:
        """Check health of specific component"""        try:
            component = getattr(self, component_name)
            if hasattr(component, 'health_check'):
                result = await component.health_check()
                return result.get('healthy', False)
            return True
        except Exception:
            return False

# Global blockchain platform instance
blockchain_platform = BlockchainPlatform()

# Convenience functions for direct access
async def initialize_blockchain() -> None:
    """Initialize blockchain platform"""    await blockchain_platform.initialize()

async def get_blockchain_platform() -> BlockchainPlatform:
    """Get initialized blockchain platform"""    if not blockchain_platform.initialized:
        await blockchain_platform.initialize()
    return blockchain_platform

# Quick access functions for common operations
async def register_content_on_blockchain(
    user_id: str,
    content_id: str,
    content_hash: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Quick function to register content rights"""    platform = await get_blockchain_platform()
    return await platform.register_content_rights(user_id, content_id, content_hash, metadata)

async def create_content_nft_license(
    user_id: str,
    content_id: str,
    license_terms: Dict[str, Any],
    price: Decimal,
    royalty_percentage: Optional[Decimal] = None
) -> Dict[str, Any]:
    """Quick function to create NFT license"""    platform = await get_blockchain_platform()
    return await platform.create_nft_license(
        user_id, content_id, license_terms, price, royalty_percentage
    )

async def process_crypto_content_payment(
    user_id: str,
    amount: Decimal,
    currency: str,
    recipient_address: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick function to process crypto payment"""    platform = await get_blockchain_platform()
    return await platform.process_crypto_payment(
        user_id, amount, currency, recipient_address, metadata
    )

async def distribute_content_royalties(
    content_id: str,
    total_amount: Decimal,
    currency: str,
    distribution_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Quick function to distribute royalties"""    platform = await get_blockchain_platform()
    return await platform.distribute_royalties(
        content_id, total_amount, currency, distribution_data
    )

# Export all main classes and functions
__all__ = [
    # Main platform
    'BlockchainPlatform',
    'blockchain_platform',
    
    # Initialization functions
    'initialize_blockchain',
    'get_blockchain_platform',
    
    # Quick access functions
    'register_content_on_blockchain',
    'create_content_nft_license',
    'process_crypto_content_payment',
    'distribute_content_royalties',
    
    # Core managers
    'BlockchainManager',
    'SmartContractManager',
    'NFTSystem',
    'CryptoPaymentSystem',
    'ConsensusEngine',
    'GovernanceSystem',
    
    # Smart contracts
    'ContentProtectionContract',
    'LicensingContract',
    'RoyaltyDistributionContract',
    'GovernanceContract',
    'StakingContract',
    
    # NFT components
    'NFTMinter',
    'NFTMarketplace',
    'NFTLicenseManager',
    'NFTRoyaltyManager',
    'NFTMetadataManager',
    
    # Payment processors
    'BitcoinProcessor',
    'EthereumProcessor',
    'MultiChainWallet',
    'PaymentGateway',
    'CryptoConverter',
    
    # Consensus components
    'ProofOfStakeConsensus',
    'ValidatorNetwork',
    'BlockValidator',
    'TransactionPool',
    
    # Governance components
    'GovernanceTokenManager',
    'ProposalManager',
    'TreasuryManager',
    
    # Data structures
    'ContentRights',
    'LicenseTerms',
    'PaymentMetadata',
    'NFTMetadata',
    'LicenseNFT',
    'MarketplaceListing',
    'RoyaltySplit',
    'PaymentRequest',
    'PaymentResult',
    'WalletBalance',
    'Validator',
    'Block',
    'Transaction',
    'ConsensusState',
    'ProposalMetadata',
    'VotingPower',
    'TreasuryAllocation',
    
    # Enums
    'ProposalType',
    'ProposalStatus',
    'VoteType',
    
    # Governance functions
    'create_governance_proposal',
    'vote_on_governance_proposal',
    'get_user_voting_power',
    'execute_governance_proposal'
]
