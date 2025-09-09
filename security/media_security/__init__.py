"""
Media Security Module
====================

This module provides comprehensive media security features including
encryption, secure streaming, integrity validation, content sanitization,
malware scanning, and deepfake detection.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

from .media_encryption_engine import MediaEncryptionEngine
from .secure_streaming_engine import SecureStreamingEngine
from .media_integrity_validator import MediaIntegrityValidator
from .content_sanitization_engine import ContentSanitizationEngine
from .malware_content_scanner import MalwareContentScanner
from .deepfake_detection_system import DeepfakeDetectionSystem

__all__ = [
    'MediaEncryptionEngine',
    'SecureStreamingEngine',
    'MediaIntegrityValidator',
    'ContentSanitizationEngine',
    'MalwareContentScanner',
    'DeepfakeDetectionSystem',
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"