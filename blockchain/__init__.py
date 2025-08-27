"""
Advanced Blockchain Infrastructure for IA Influencer Agent Platform
Enterprise-grade blockchain integration for content protection and monetization

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.

Key Features:
- Blockchain-based copyright protection and verification
- Smart contract deployment and management
- Digital rights management (DRM) with usage tracking
- Multi-creator collaboration with automated revenue sharing
- Advanced monetization strategies with AI optimization
- Cross-platform content distribution with blockchain verification
- NFT minting for premium content protection
- Real-time transaction monitoring and analytics
"""

from .copyright_registry import (
    CopyrightRegistryManager,
    CopyrightAsset,
    CopyrightProof,
    CopyrightType,
    ProtectionLevel,
    CopyrightAnalytics
)

from .digital_rights import (
    DRMManager,
    DigitalLicense,
    UsageEvent,
    ProtectionPolicy,
    UsageRights,
    AccessLevel,
    LicenseType
)

from .collaboration import (
    CollaborationManager,
    CollaborationProposal,
    CollaborationProject,
    RevenueDistribution,
    CollaboratorProfile,
    CollaborationType,
    CollaborationStatus,
    RevenueDistributionModel
)

from .monetization import (
    MonetizationManager,
    RevenueTransaction,
    MonetizationStrategy,
    RevenueAnalytics,
    PayoutConfiguration,
    RevenueStream,
    PaymentMethod,
    SubscriptionTier
)

from .distribution import (
    DistributionManager,
    DistributionJob,
    PlatformConfiguration,
    PlatformMetrics,
    CrossPlatformAnalytics,
    Platform,
    DistributionStatus,
    ContentFormat
)

from .smart_contracts import (
    SmartContractManager,
    ContractManager,
    SmartContract,
    ContractInteraction,
    ContractType,
    ContractStatus
)

from .connection import (
    BlockchainConnection,
    MultiNetworkManager,
    NetworkConfig,
)
from .gas_optimizer import (
    GasOptimizer,
    GasEstimate,
    TransactionBatch,
)
from .transaction_manager import (
    TransactionManager,
    TransactionRequest,
    TransactionResult,
    TransactionStatus,
    NonceManager,
)
from .validator import (
    BlockchainValidator,
    ValidationResult,
    ValidationSeverity,
    SecurityAudit,
)
from .nft import (
    NFTManager,
    ContentNFT,
    NFTMarketplace,
    NFTMetadata,
)
from .rights import (
    DigitalRightsManager,
    ContentLicense,
    RightsProtection,
    LicenseNFT,
    RightsAnchor,
)
from .smart_contracts import (
    SmartContractManager,
    ContractDeployer,
    ContractInteractor,
    ContractABI,
    ContractManager,
)

__all__ = [
    # Core blockchain infrastructure
    "BlockchainConnection",
    "MultiNetworkManager",
    "NetworkConfig",
    
    # Gas optimization
    "GasOptimizer",
    "GasEstimate",
    "TransactionBatch",
    
    # Transaction management
    "TransactionManager",
    "TransactionRequest",
    "TransactionResult",
    "TransactionStatus",
    "NonceManager",
    
    # Validation and security
    "BlockchainValidator",
    "ValidationResult",
    "ValidationSeverity",
    "SecurityAudit",
    
    # NFT functionality
    "NFTManager",
    "ContentNFT",
    "NFTMarketplace",
    "NFTMetadata",
    
    # Rights management
    "DigitalRightsManager",
    "ContentLicense",
    "RightsProtection",
    "LicenseNFT",
    "RightsAnchor",
    
    # Smart contracts
    "SmartContractManager",
    "ContractDeployer",
    "ContractInteractor",
    "ContractABI",
    "ContractManager",
]
