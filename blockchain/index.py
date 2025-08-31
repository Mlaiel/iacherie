"""Blockchain Module Index - IA Influencer Agent Platform
Main entry point for blockchain infrastructure access

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
# Core blockchain infrastructure
from .connection import BlockchainConnection, MultiNetworkManager, NetworkConfig
from .transaction_manager import TransactionManager, TransactionRequest, TransactionResult
from .smart_contracts import SmartContractManager, ContractManager, SmartContract
from .gas_optimizer import GasOptimizer, GasEstimate, TransactionBatch

# Business logic managers
from .copyright_registry import (
    CopyrightRegistryManager,
    CopyrightAsset,
    CopyrightProof,
    CopyrightType,
    ProtectionLevel
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
    CollaborationType,
    CollaborationStatus
)

from .monetization import (
    MonetizationManager,
    RevenueTransaction,
    MonetizationStrategy,
    RevenueAnalytics,
    PayoutConfiguration,
    RevenueStream
)

from .distribution import (
    DistributionManager,
    DistributionJob,
    PlatformConfiguration,
    PlatformMetrics,
    CrossPlatformAnalytics,
    Platform
)

# Specialized managers
from .nft import NFTManager
from .rights import RightsManager

# Main blockchain service
from . import BlockchainService


def get_blockchain_service(encryption_manager, database_manager=None):
    """    Factory function to create blockchain service instance
    
    Args:
        encryption_manager: Security encryption manager
        database_manager: Optional database manager for caching
        
    Returns:
        BlockchainService: Configured blockchain service
    """    return BlockchainService(encryption_manager, database_manager)


def get_copyright_manager(encryption_manager):
    """Get standalone copyright registry manager"""    service = get_blockchain_service(encryption_manager)
    return service.copyright_registry


def get_drm_manager(encryption_manager):
    """Get standalone digital rights manager"""    service = get_blockchain_service(encryption_manager)
    return service.drm_manager


def get_collaboration_manager(encryption_manager):
    """Get standalone collaboration manager"""    service = get_blockchain_service(encryption_manager)
    return service.collaboration_manager


def get_monetization_manager(encryption_manager):
    """Get standalone monetization manager"""    service = get_blockchain_service(encryption_manager)
    return service.monetization_manager


def get_distribution_manager(encryption_manager):
    """Get standalone distribution manager"""    service = get_blockchain_service(encryption_manager)
    return service.distribution_manager


# Quick access aliases for common operations
create_blockchain_service = get_blockchain_service
create_copyright_registry = get_copyright_manager
create_drm_system = get_drm_manager
create_collaboration_platform = get_collaboration_manager
create_monetization_engine = get_monetization_manager
create_distribution_system = get_distribution_manager


__all__ = [
    # Core Infrastructure
    'BlockchainConnection',
    'TransactionManager', 
    'SmartContractManager',
    'GasOptimizer',
    
    # Business Logic Managers
    'CopyrightRegistryManager',
    'DRMManager',
    'CollaborationManager', 
    'MonetizationManager',
    'DistributionManager',
    
    # Data Models
    'CopyrightAsset',
    'DigitalLicense',
    'CollaborationProject',
    'RevenueTransaction',
    'DistributionJob',
    
    # Factory Functions
    'get_blockchain_service',
    'get_copyright_manager',
    'get_drm_manager',
    'get_collaboration_manager',
    'get_monetization_manager',
    'get_distribution_manager',
    
    # Service Aliases
    'create_blockchain_service',
    'create_copyright_registry',
    'create_drm_system',
    'create_collaboration_platform',
    'create_monetization_engine',
    'create_distribution_system',
    
    # Main Service
    'BlockchainService'
]
