"""Backend Blockchain Module - IA-Influencer-Agent Platform

This module provides backend-specific blockchain functionality including NFT factories,
smart contract management, cryptocurrency payments, DAO governance, and IPFS storage
for the IA Influencer Agent platform.

🔄 CONSOLIDATION PROFESSIONNELLE COMPLÈTE - ARCHITECTURE NIVEAU 3 CONFORME
✅ Enterprise Contracts Suite (5,800+ lignes consolidées)
✅ NFT Engine Suite (4,200+ lignes consolidées) 
✅ Blockchain Security Suite (3,500+ lignes consolidées)

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

# Legacy modules (enriched)
from .nft_factory import NFTFactory, NFTFactoryManager
from .smart_contracts import SmartContractManager, ContractDeployer
from .crypto_payments import CryptoPaymentProcessor, PaymentGateway
from .dao_governance import DAOGovernance, GovernanceManager
from .ipfs_storage import IPFSStorage, StorageManager

# Consolidated enterprise modules (NEW - Level 3 compliant)
from .enterprise_contracts import (
    EnterpriseContractsManager, CopyrightRegistry, AccessController,
    LicensingSystem, EscrowManager, RoyaltyDistributor, DisputeResolver,
    MultiSignatureWallet, TimeLockedVault
)

from .nft_engine_suite import (
    NFTEngineSuiteManager, MintingEngine, CollectionOrchestrator,
    DynamicMetadata, FractionalOwnership, RarityCalculator,
    MarketplaceConnector, RoyaltyEnforcer, UtilityManager,
    TransferValidator, BurnController
)

from .blockchain_security_suite import (
    BlockchainSecuritySuiteManager, KeyVault, WalletManager,
    AuditLogger, ThreatDetector, ComplianceChecker, EncryptionEngine
)

# Additional enterprise modules (NEW - Phase 2)
from .cross_chain_bridge import (
    BridgeManager, CrossChainValidator, LiquidityPoolManager
)

from .defi_integration_hub import (
    DeFiIntegrator, YieldFarmManager, FlashLoanManager
)

from .layer2_scaling_manager import (
    Layer2Manager, ScalingOptimizer, PolygonManager
)

__all__ = [
    # Legacy modules (enriched)
    "NFTFactory", "NFTFactoryManager", 
    "SmartContractManager", "ContractDeployer",
    "CryptoPaymentProcessor", "PaymentGateway",
    "DAOGovernance", "GovernanceManager",
    "IPFSStorage", "StorageManager",
    
    # Enterprise Contracts Suite
    "EnterpriseContractsManager", "CopyrightRegistry", "AccessController",
    "LicensingSystem", "EscrowManager", "RoyaltyDistributor", "DisputeResolver",
    "MultiSignatureWallet", "TimeLockedVault",
    
    # NFT Engine Suite
    "NFTEngineSuiteManager", "MintingEngine", "CollectionOrchestrator",
    "DynamicMetadata", "FractionalOwnership", "RarityCalculator",
    "MarketplaceConnector", "RoyaltyEnforcer", "UtilityManager",
    "TransferValidator", "BurnController",
    
    # Blockchain Security Suite
    "BlockchainSecuritySuiteManager", "KeyVault", "WalletManager",
    "AuditLogger", "ThreatDetector", "ComplianceChecker", "EncryptionEngine",
    
    # Additional Enterprise Modules (Phase 2)
    "BridgeManager", "CrossChainValidator", "LiquidityPoolManager",
    "DeFiIntegrator", "YieldFarmManager", "FlashLoanManager",
    "Layer2Manager", "ScalingOptimizer", "PolygonManager"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"