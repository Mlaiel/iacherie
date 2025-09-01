"""Enterprise Backup Management System for IA Influencer Agent Platform.

This module provides comprehensive backup and recovery solutions for the
IA Influencer Agent platform, supporting multi-format content protection,
user data, and system configurations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code, concept, and implementation are the exclusive intellectual property
of Fahed Mlaiel (mlaiel@live.de). Any unauthorized copying, distribution,
modification, or commercial use without explicit written permission is strictly
prohibited and will result in immediate legal action under German and
international law.

Key Features:
- Automated content backup (audio, video, image, text)
- User data and fingerprint backup
- System configuration backup  
- Real-time backup monitoring
- Multi-destination backup support
- Enterprise-grade encryption and compression
- Backup verification and integrity checks
- Advanced recovery automation
- Multi-tenant backup isolation
- Compliance and audit trails
- Performance optimization
- Cloud storage integration
"""
import logging
from typing import Dict, List, Optional, Any

# Core backup services
from .backup_manager import (
    BackupManager,
    BackupType,
    BackupStatus,
    BackupMetadata
)

from .content_backup import (
    ContentBackupService,
    ContentBackupRecord
)

from .user_backup import (
    UserDataBackupService,
    UserBackupRecord
)

from .system_backup import SystemConfigBackupService

# Supporting services
from .backup_scheduler import BackupScheduler
from .backup_monitor import BackupMonitor
from .recovery_manager import RecoveryManager

from .backup_encryption import (
    BackupEncryption,
    EncryptionAlgorithm,
    EncryptionConfig,
    EncryptionMetadata
)

from .backup_validator import BackupValidator
from .backup_storage import BackupStorage

# Configuration and utilities
from .backup_config import (
    BackupConfig,
    StorageConfig,
    EncryptionConfig,
    SchedulingConfig,
    MonitoringConfig,
    ValidationConfig,
    RecoveryConfig,
    PerformanceConfig,
    StorageBackend,
    CompressionAlgorithm,
    get_backup_config,
    reload_backup_config
)

from .backup_metrics import (
    BackupMetrics,
    BackupOperationType,
    MetricType,
    OperationMetrics,
    get_backup_metrics,
    record_operation_metrics
)

from .backup_utils import (
    BackupUtils,
    format_backup_size,
    generate_backup_id,
    parse_backup_id,
    async_file_copy,
    validate_backup_path,
    get_backup_file_extension
)

# Main platform interface
from .index import (
    BackupPlatform,
    create_backup_platform,
    quick_full_backup,
    quick_content_backup,
    quick_restore
)

# Version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "Copyright (c) 2025 IA Influencer Agent Platform"

# Configure module logging
logger = logging.getLogger(__name__)


def get_module_info() -> Dict[str, Any]:
    """
    Get comprehensive module information.
    
    Returns:
        Module metadata and capabilities
    """
    return {
        "name": "backup",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": "Enterprise Backup Management System",
        "capabilities": [
            "Full platform backup",
            "Incremental backup",
            "Content protection backup",
            "User data backup",
            "System configuration backup",
            "Multi-algorithm encryption",
            "Real-time monitoring",
            "Automated scheduling",
            "Disaster recovery",
            "Integrity verification",
            "Cloud storage support",
            "Audit trails"
        ],
        "supported_formats": [
            "audio",
            "video", 
            "image",
            "text",
            "fingerprints",
            "user_profiles",
            "collaborations",
            "monetization_data",
            "system_configs"
        ],
        "encryption_algorithms": [
            "AES-256-GCM",
            "AES-256-CBC", 
            "ChaCha20-Poly1305",
            "Fernet"
        ],
        "storage_backends": [
            "local_filesystem",
            "aws_s3",
            "azure_blob",
            "google_cloud_storage"
        ]
    }


def validate_backup_config(config: Dict[str, Any]) -> bool:
    """
    Validate backup configuration.
    
    Args:
        config: Backup configuration to validate
        
    Returns:
        Configuration validity
    """
    required_keys = ["storage", "encryption_key"]
    
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            return False
    
    # Validate storage config
    storage_config = config.get("storage", {})
    if not storage_config.get("backend"):
        logger.error("Storage backend not specified")
        return False
    
    return True


def create_default_config() -> Dict[str, Any]:
    """
    Create default backup configuration.
    
    Returns:
        Default configuration
    """
    return {
        "storage": {
            "backend": "local_filesystem",
            "path": "/var/backups/ia_influencer",
            "max_storage_gb": 1000,
            "retention_days": 30
        },
        "encryption_key": None,  # Should be provided by user
        "compression_level": 6,
        "max_concurrent_backups": 3,
        "verification_enabled": True,
        "monitoring_enabled": True,
        "scheduling": {
            "full_backup_cron": "0 2 * * 0",  # Weekly at 2 AM
            "incremental_backup_cron": "0 2 * * 1-6"  # Daily at 2 AM
        }
    }


# Export all important classes and functions
__all__ = [
    # Core backup services
    "BackupManager",
    "ContentBackupService", 
    "UserDataBackupService",
    "SystemConfigBackupService",
    
    # Supporting services
    "BackupScheduler",
    "BackupMonitor",
    "RecoveryManager",
    "BackupEncryption",
    "BackupValidator",
    "BackupStorage",
    
    # Main platform interface
    "BackupPlatform",
    "create_backup_platform",
    
    # Configuration classes
    "BackupConfig",
    "StorageConfig",
    "EncryptionConfig", 
    "SchedulingConfig",
    "MonitoringConfig",
    "ValidationConfig",
    "RecoveryConfig",
    "PerformanceConfig",
    "get_backup_config",
    "reload_backup_config",
    
    # Metrics and monitoring
    "BackupMetrics",
    "OperationMetrics",
    "get_backup_metrics",
    "record_operation_metrics",
    
    # Utilities
    "BackupUtils",
    "format_backup_size",
    "generate_backup_id",
    "parse_backup_id",
    "async_file_copy",
    "validate_backup_path",
    "get_backup_file_extension",
    
    # Enums and data classes
    "BackupType",
    "BackupStatus",
    "BackupMetadata",
    "ContentBackupRecord",
    "UserBackupRecord",
    "EncryptionAlgorithm",
    "EncryptionMetadata",
    "StorageBackend",
    "CompressionAlgorithm",
    "BackupOperationType",
    "MetricType",
    
    # Convenience functions
    "quick_full_backup",
    "quick_content_backup",
    "quick_restore",
    
    # Utility functions
    "get_module_info",
    "validate_backup_config",
    "create_default_config",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__"
]
