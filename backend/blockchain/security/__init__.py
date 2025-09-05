"""Security & Cryptography Module - IA-Influencer-Agent Platform

This module provides enterprise-grade security and cryptography functionality
for the blockchain infrastructure including wallet management, key storage,
signature validation, hardware security integration, and zero-knowledge proofs.

Features:
- Secure wallet management
- Cryptographic key vault
- Digital signature validation
- Hardware security module integration
- Zero-knowledge proof systems
- Security audit logging
- Threat detection and monitoring
- Advanced encryption engines
- Access control integration
- Cold storage management
- Compliance checking

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

from .wallet_manager import WalletManager, SecureWallet
from .key_vault import KeyVault, CryptographicKey
from .signature_validator import SignatureValidator, SignatureVerification
from .hardware_security import HardwareSecurityModule, HSMManager
from .zero_knowledge import ZeroKnowledgeProofs, ZKProofSystem
from .audit_logger import SecurityAuditLogger, AuditEvent
from .threat_detector import ThreatDetector, SecurityThreat
from .encryption_engine import EncryptionEngine, CryptoProvider
from .access_controller import SecurityAccessController, SecurityPolicy
from .cold_storage import ColdStorageManager, OfflineWallet
from .compliance_checker import ComplianceChecker, ComplianceReport

__all__ = [
    "WalletManager",
    "SecureWallet",
    "KeyVault",
    "CryptographicKey",
    "SignatureValidator",
    "SignatureVerification",
    "HardwareSecurityModule",
    "HSMManager",
    "ZeroKnowledgeProofs",
    "ZKProofSystem",
    "SecurityAuditLogger",
    "AuditEvent",
    "ThreatDetector",
    "SecurityThreat",
    "EncryptionEngine",
    "CryptoProvider",
    "SecurityAccessController",
    "SecurityPolicy",
    "ColdStorageManager",
    "OfflineWallet",
    "ComplianceChecker",
    "ComplianceReport"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"