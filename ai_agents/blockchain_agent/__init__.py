"""
IA-Influencer Agent - Blockchain Agent Module

Enterprise-grade blockchain integration for decentralized rights management,
NFT creation, smart contracts, and cryptocurrency monetization.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Expert Team Specializations:
- Lead AI Developer: Fahed Mlaiel
- Senior Backend Engineer  
- Blockchain Architect
- Smart Contracts Developer
- Cryptocurrency Expert
- Security Specialist
- NFT Marketplace Integration
- DeFi Integration Expert
"""

from .blockchain_agent import (
    BlockchainAgent,
    BlockchainNetwork,
    ContractType,
    TransactionStatus,
    NFTMetadata,
    SmartContract,
    BlockchainTransaction
)
from .smart_contracts import (
    SmartContractsManager,
    ContractStatus,
    SecurityLevel,
    ContractTemplate,
    DeploymentConfig
)
from .nft_creator import (
    NFTCreator,
    ContentType,
    NFTStandard,
    MarketplaceType,
    RarityTier,
    ContentMetadata,
    NFTCollection,
    NFTRoyalty,
    MarketplaceListing
)
from .copyright_registry import (
    CopyrightRegistry,
    CopyrightType,
    RegistrationStatus,
    LegalJurisdiction,
    CopyrightClaim,
    CopyrightEvidence,
    OwnershipTransfer
)
from .crypto_payments import (
    CryptoPaymentProcessor,
    PaymentStatus,
    PaymentType,
    CurrencyType,
    PaymentRequest,
    PaymentTransaction,
    SubscriptionPlan,
    PaymentStream
)
from .defi_integration import (
    DeFiIntegration,
    DeFiProtocol,
    StrategyType,
    RiskLevel,
    DeFiPool,
    YieldPosition,
    LendingPosition,
    DeFiStrategy
)
from .index import (
    BlockchainAgentIndex,
    get_blockchain_index,
    create_nft_with_copyright,
    setup_creator_platform
)

__all__ = [
    # Core blockchain agent
    'BlockchainAgent',
    'BlockchainNetwork',
    'ContractType',
    'TransactionStatus',
    'NFTMetadata',
    'SmartContract',
    'BlockchainTransaction',
    
    # Smart contracts management
    'SmartContractsManager',
    'ContractStatus',
    'SecurityLevel',
    'ContractTemplate',
    'DeploymentConfig',
    
    # NFT creation and management
    'NFTCreator',
    'ContentType',
    'NFTStandard',
    'MarketplaceType',
    'RarityTier',
    'ContentMetadata',
    'NFTCollection',
    'NFTRoyalty',
    'MarketplaceListing',
    
    # Copyright registry
    'CopyrightRegistry',
    'CopyrightType',
    'RegistrationStatus',
    'LegalJurisdiction',
    'CopyrightClaim',
    'CopyrightEvidence',
    'OwnershipTransfer',
    
    # Cryptocurrency payments
    'CryptoPaymentProcessor',
    'PaymentStatus',
    'PaymentType',
    'CurrencyType',
    'PaymentRequest',
    'PaymentTransaction',
    'SubscriptionPlan',
    'PaymentStream',
    
    # DeFi integration
    'DeFiIntegration',
    'DeFiProtocol',
    'StrategyType',
    'RiskLevel',
    'DeFiPool',
    'YieldPosition',
    'LendingPosition',
    'DeFiStrategy',
    
    # Blockchain Agent Index and utilities
    'BlockchainAgentIndex',
    'get_blockchain_index',
    'create_nft_with_copyright',
    'setup_creator_platform',
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
