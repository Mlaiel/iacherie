"""Backend Blockchain Module - IA-Influencer-Agent Platform

This module provides backend-specific blockchain functionality including NFT factories,
smart contract management, cryptocurrency payments, DAO governance, and IPFS storage
for the IA Influencer Agent platform.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

from .nft_factory import NFTFactory, NFTFactoryManager
from .smart_contracts import SmartContractManager, ContractDeployer
from .crypto_payments import CryptoPaymentProcessor, PaymentGateway
from .dao_governance import DAOGovernance, GovernanceManager
from .ipfs_storage import IPFSStorage, StorageManager

__all__ = [
    "NFTFactory",
    "NFTFactoryManager", 
    "SmartContractManager",
    "ContractDeployer",
    "CryptoPaymentProcessor",
    "PaymentGateway",
    "DAOGovernance",
    "GovernanceManager",
    "IPFSStorage",
    "StorageManager"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"