"""
Storage Modules - Ainflue Infrastructure Enterprise
==================================================
Point d'entrée principal pour tous les services de stockage

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 2.0 Production
"""

# Imports principaux
from . import *

# Exports publics principaux
__all__ = [
    'StorageManager',
    'DatabaseAdapter',
    'FileStorage',
    'MongoDBAdapter',
    'RedisAdapter',
    'BlockStorage',
    'ObjectStorage',
    'ContentCache'
]

# Metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise storage infrastructure for Ainflue platform"

# Configuration stockage métier Ainflue
AINFLUE_STORAGE_WORKFLOW = {
    'upload': 'Multi-format content storage and indexing',
    'ai_processing': 'AI model storage and versioning', 
    'protection': 'Secure storage for IP rights and watermarks',
    'monetization': 'Revenue data storage and analytics',
    'collaboration': 'Collaborative content storage and versioning',
    'seo': 'SEO metadata and optimization data storage',
    'distribution': 'Multi-platform content distribution storage'
}

# Storage requirements pour créateurs
CREATOR_STORAGE_REQUIREMENTS = {
    'musician': 'High-performance audio file storage with metadata',
    'blogger': 'Text content storage with version control',
    'photographer': 'Large image file storage with RAW support',
    'influencer': 'Multi-media content storage and CDN integration',
    'comedian': 'Video content storage with streaming optimization'
}