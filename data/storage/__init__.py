"""Professional Data Storage Management - IA Influencer Agent Platform
===================================================================
Module: backend/data/storage/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Storage Core - Multi-Format Content Management
Responsibility: Complete storage ecosystem for content protection & monetization
Technologies: Python, Multi-cloud, Version control, Backup & Recovery
===================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER INTÉGRÉE:
Content Upload → File Processing → Version Tracking → 
Storage Distribution → Backup Protection → Recovery Support → 
Access Control → Performance Optimization → Security Compliance

MODULES PROFESSIONNELS:
- StorageManager: Multi-cloud storage orchestration
- FileManager: Multi-format file processing & validation
- VersionManager: Git-like version control for content
- BackupManager: Multi-tier backup & disaster recovery
"""
from .storage_manager import StorageManager
from .file_manager import (
    FileManager, 
    ContentType, 
    FileStatus, 
    CompressionLevel,
    FileMetadata,
    FileValidationResult,
    FileProcessingResult,
    FileValidationConfig
)
from .version_manager import (
    VersionManager,
    VersionType,
    ChangeType,
    ConflictResolution,
    VersionInfo,
    VersionDelta,
    BranchInfo,
    MergeResult,
    VersionComparison
)
from .backup_manager import (
    BackupManager,
    BackupTier,
    BackupStatus,
    BackupType,
    RecoveryType,
    BackupConfig,
    BackupDestination,
    BackupJob,
    RestoreJob,
    BackupStatistics
)
from .distributed_manager import (
    DistributedStorageManager,
    DistributionStrategy,
    ProviderHealth,
    ProviderMetrics,
    DistributionConfig,
    FileDistribution
)
from .performance_monitor import (
    PerformanceMonitor,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceReport,
    MetricType,
    AlertSeverity,
    PerformanceCategory,
    MetricPoint
)
from .encryption_manager import (
    EncryptionManager,
    EncryptionKey,
    EncryptionConfig,
    EncryptionResult,
    DecryptionResult,
    EncryptionAlgorithm,
    KeyType,
    SecurityLevel
)
from .config_manager import (
    ConfigurationManager,
    StorageConfiguration,
    StorageProviderConfig,
    SecurityConfig,
    PerformanceConfig,
    BackupConfig,
    MonitoringConfig,
    EnvironmentType,
    ConfigurationSource
)
from .index import (
    StorageIndex,
    StorageOperation,
    StorageIndexConfig
)

__all__ = [
    # Core managers
    "StorageManager",
    "FileManager",
    "VersionManager", 
    "BackupManager",
    "DistributedStorageManager",
    "PerformanceMonitor",
    "EncryptionManager",
    "ConfigurationManager",
    "StorageIndex",
    
    # File management enums and classes
    "ContentType",
    "FileStatus", 
    "CompressionLevel",
    "FileMetadata",
    "FileValidationResult",
    "FileProcessingResult",
    "FileValidationConfig",
    
    # Version management enums and classes
    "VersionType",
    "ChangeType",
    "ConflictResolution",
    "VersionInfo",
    "VersionDelta",
    "BranchInfo",
    "MergeResult",
    "VersionComparison",
    
    # Backup management enums and classes
    "BackupTier",
    "BackupStatus",
    "BackupType",
    "RecoveryType",
    "BackupConfig",
    "BackupDestination",
    "BackupJob",
    "RestoreJob",
    "BackupStatistics",
    
    # Distributed storage enums and classes
    "DistributionStrategy",
    "ProviderHealth",
    "ProviderMetrics",
    "DistributionConfig",
    "FileDistribution",
    
    # Performance monitoring enums and classes
    "PerformanceMetric",
    "PerformanceAlert", 
    "PerformanceReport",
    "MetricType",
    "AlertSeverity",
    "PerformanceCategory",
    "MetricPoint",
    
    # Encryption enums and classes
    "EncryptionKey",
    "EncryptionConfig",
    "EncryptionResult",
    "DecryptionResult",
    "EncryptionAlgorithm",
    "KeyType",
    "SecurityLevel",
    
    # Configuration management enums and classes
    "StorageConfiguration",
    "StorageProviderConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "BackupConfig",
    "MonitoringConfig",
    "EnvironmentType",
    "ConfigurationSource",
    
    # Storage index orchestration
    "StorageOperation",
    "StorageIndexConfig"
]

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Industrial storage management system for IA Influencer Agent platform"
__status__ = "Production-Ready"
