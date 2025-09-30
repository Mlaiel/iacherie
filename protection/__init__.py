"""
IA Chérie Content Protection System
Enterprise-grade content protection and rights management platform.
"""

# Configuration professionnelle et corrections
try:
    import os
    import warnings
    # Corrections des imports problématiques
    from config.langdetect_correction import fix_langdetect_imports
    from config.essentia_professional import setup_essentia_models
    fix_langdetect_imports()
    setup_essentia_models()
except ImportError:
    pass

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright © 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary"

# Core services
from .fingerprinting import FingerprintingService
from .monitoring import MonitoringService
from .alerts import AlertService
from .copyright_enforcement import CopyrightEnforcementService
from .dmca_automation import DMCAAutomationService
from .drm import DRMService
from .watermarking import WatermarkingService
from .rights_tracking import RightsTrackingService
from .blockchain import BlockchainService
from .vector_database import VectorDatabaseService
from .crawlers import CrawlerService

# Main service
class ContentProtectionService:
    """Main content protection service."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the service."""
        self.initialized = True
        return True

# Export main service class and version info
__all__ = [
    "ContentProtectionService",
    "FingerprintingService",
    "MonitoringService", 
    "AlertService",
    "CopyrightEnforcementService",
    "DMCAAutomationService",
    "DRMService",
    "WatermarkingService",
    "RightsTrackingService",
    "BlockchainService",
    "VectorDatabaseService",
    "CrawlerService",
    "__version__",
    "__author__",
    "__email__",
    "__copyright__",
    "__license__"
]
