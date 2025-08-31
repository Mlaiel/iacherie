"""Database Fingerprinting Module

This module handles all database operations related to content fingerprinting storage,
indexing, and retrieval for AI-powered content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
"""from .fingerprint_storage import FingerprintStorageManager
from .fingerprint_indexing import FingerprintIndexManager
from .fingerprint_matching import FingerprintMatchingEngine
from .fingerprint_repository import FingerprintRepository
from .fingerprint_cache import FingerprintCacheManager
from .fingerprint_cleanup import FingerprintCleanupService
from .fingerprint_analytics import FingerprintAnalyticsEngine
from .fingerprint_versioning import FingerprintVersionManager

__all__ = [
    "FingerprintStorageManager",
    "FingerprintIndexManager",
    "FingerprintMatchingEngine",
    "FingerprintRepository",
    "FingerprintCacheManager",
    "FingerprintCleanupService",
    "FingerprintAnalyticsEngine",
    "FingerprintVersionManager"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
