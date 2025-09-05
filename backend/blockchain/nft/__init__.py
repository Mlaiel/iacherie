"""NFT Management Advanced Module - IA-Influencer-Agent Platform

This module provides advanced NFT management functionality including professional
minting engines, metadata management, collection orchestration, marketplace
integration, and utility management for the blockchain infrastructure.

Features:
- Professional NFT minting engine
- Advanced metadata management
- Collection orchestration
- Rarity calculation algorithms
- Marketplace connector integration
- Royalty enforcement automation
- Fractional ownership support
- Dynamic metadata systems
- Transfer validation
- Burn control mechanisms
- Utility management
- Cross-chain NFT support

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

from .minting_engine import MintingEngine, MintingResult
from .metadata_manager import MetadataManager, NFTMetadata
from .collection_orchestrator import CollectionOrchestrator, NFTCollection
from .rarity_calculator import RarityCalculator, RarityAnalysis
from .marketplace_connector import MarketplaceConnector, MarketplaceListing
from .royalty_enforcer import RoyaltyEnforcer, RoyaltyDistribution
from .fractional_ownership import FractionalOwnership, OwnershipShare
from .dynamic_metadata import DynamicMetadata, MetadataUpdate
from .transfer_validator import TransferValidator, TransferValidation
from .burn_controller import BurnController, BurnRecord
from .utility_manager import UtilityManager, NFTUtility

__all__ = [
    "MintingEngine",
    "MintingResult",
    "MetadataManager",
    "NFTMetadata",
    "CollectionOrchestrator",
    "NFTCollection",
    "RarityCalculator",
    "RarityAnalysis",
    "MarketplaceConnector",
    "MarketplaceListing",
    "RoyaltyEnforcer", 
    "RoyaltyDistribution",
    "FractionalOwnership",
    "OwnershipShare",
    "DynamicMetadata",
    "MetadataUpdate",
    "TransferValidator",
    "TransferValidation",
    "BurnController",
    "BurnRecord",
    "UtilityManager",
    "NFTUtility"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"