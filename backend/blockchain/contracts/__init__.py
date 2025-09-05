"""Smart Contracts Enterprise Module - IA-Influencer-Agent Platform

This module provides enterprise-grade smart contract functionality including copyright
registry, licensing systems, royalty distribution, escrow management, and advanced
access control for the blockchain infrastructure.

Features:
- Copyright registry with immutable records
- Automated licensing system
- Royalty distribution automation
- Escrow management for collaborations
- Granular access control
- Multi-signature wallet integration
- Time-locked payments
- Oracle connectivity
- Emergency pause mechanisms

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

from .copyright_registry import CopyrightRegistry, CopyrightRecord
from .licensing_system import LicensingSystem, LicenseManager
from .royalty_distributor import RoyaltyDistributor, RoyaltyManager
from .escrow_manager import EscrowManager, EscrowContract
from .access_controller import AccessController, PermissionManager
from .revenue_splitter import RevenueSplitter, SplitManager
from .dispute_resolver import DisputeResolver, DisputeManager
from .multi_signature import MultiSignatureWallet, MultiSigManager
from .time_locked import TimeLockedPayments, TimeLockManager
from .oracle_connector import OracleConnector, OracleManager
from .emergency_pause import EmergencyPause, PauseManager

__all__ = [
    "CopyrightRegistry",
    "CopyrightRecord",
    "LicensingSystem",
    "LicenseManager",
    "RoyaltyDistributor",
    "RoyaltyManager",
    "EscrowManager",
    "EscrowContract",
    "AccessController", 
    "PermissionManager",
    "RevenueSplitter",
    "SplitManager",
    "DisputeResolver",
    "DisputeManager",
    "MultiSignatureWallet",
    "MultiSigManager",
    "TimeLockedPayments",
    "TimeLockManager",
    "OracleConnector",
    "OracleManager",
    "EmergencyPause",
    "PauseManager"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"