"""Protection & Security Module - IA Influencer Agent Platform
============================================================

Enterprise-grade content protection and security system providing comprehensive
rights management, piracy detection, and automated enforcement for creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Architecture: 12-module protection and security suite
"""

from .fingerprint_analyzer import FingerprintAnalyzer
from .violation_detector import ViolationDetector
from .dmca_processor import DMCAProcessor
from .rights_enforcer import RightsEnforcer
from .piracy_hunter import PiracyHunter
from .watermark_embedder import WatermarkEmbedder
from .blockchain_notary import BlockchainNotary
from .legal_automation import LegalAutomation
from .evidence_collector import EvidenceCollector
from .takedown_orchestrator import TakedownOrchestrator
from .compliance_monitor import ComplianceMonitor

__all__ = [
    'FingerprintAnalyzer',
    'ViolationDetector',
    'DMCAProcessor',
    'RightsEnforcer', 
    'PiracyHunter',
    'WatermarkEmbedder',
    'BlockchainNotary',
    'LegalAutomation',
    'EvidenceCollector',
    'TakedownOrchestrator',
    'ComplianceMonitor'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"