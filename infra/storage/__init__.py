# IA Chérie Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for IA Chérie platform
# Supports multi-cloud deployment and enterprise storage
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Storage Infrastructure Module

Enterprise storage infrastructure for IA Chérie platform.
Provides comprehensive storage management, backup, and optimization capabilities.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary"

# Storage infrastructure components
from .object_storage_manager import ObjectStorageManager
from .block_storage_configuration import BlockStorageConfiguration
from .file_system_manager import FileSystemManager
from .backup_management import BackupManagementSystem
from .data_lifecycle_manager import DataLifecycleManager
from .database_storage_provisioning import DatabaseStorageProvisioning
from .cache_storage_manager import CacheStorageManager
from .vector_database_storage import VectorDatabaseStorage
from .data_replication_engine import DataReplicationEngine
from .storage_optimization import StorageOptimization

__all__ = [
    # Storage Management
    "ObjectStorageManager",
    "BlockStorageConfiguration",
    "FileSystemManager",
    "BackupManagementSystem",
    "DataLifecycleManager",
    
    # Database Storage
    "DatabaseStorageProvisioning",
    "CacheStorageManager",
    "VectorDatabaseStorage",
    "DataReplicationEngine",
    "StorageOptimization",
]

# Storage configuration constants
STORAGE_TIERS = {
    "hot": 1,
    "warm": 2,
    "cold": 3,
    "archive": 4
}

STORAGE_PROVIDERS = [
    "AWS_S3",
    "AWS_EBS",
    "Azure_Blob",
    "Azure_Disk",
    "GCP_Storage",
    "GCP_Persistent_Disk"
]

def get_storage_info():
    """Get storage module information."""
    return {
        "version": __version__,
        "author": __author__,
        "storage_tiers": STORAGE_TIERS,
        "storage_providers": STORAGE_PROVIDERS
    }
