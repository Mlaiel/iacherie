"""
Content Protection Security Module
===================================

This module provides comprehensive content protection and security features
for the Ainflue platform, including DRM, watermarking, fingerprinting,
piracy detection, copyright protection, and access control.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

from .digital_rights_management import DigitalRightsManagement
from .content_watermarking_engine import ContentWatermarkingEngine
from .content_fingerprinting import ContentFingerprinting
from .piracy_detection_engine import PiracyDetectionEngine
from .copyright_protection_system import CopyrightProtectionSystem
from .content_access_control import ContentAccessControl

__all__ = [
    'DigitalRightsManagement',
    'ContentWatermarkingEngine', 
    'ContentFingerprinting',
    'PiracyDetectionEngine',
    'CopyrightProtectionSystem',
    'ContentAccessControl',
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"