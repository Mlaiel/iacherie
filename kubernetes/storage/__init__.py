"""IA Influencer Agent - Storage Deployment Module
================================================================================
Module: backend/deployment/storage/__init__.py
Author: Fahed Mlaiel <mlaiel@live.de>
Type: Industrial Deployment Module - Storage Infrastructure Management
Responsibility: Production-grade storage deployment orchestration
Technologies: Python, AWS S3, Kubernetes, CDN, Backup Systems
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior: Expert Python/FastAPI  
- ML Engineer: IA & Audio Processing
- DevOps Engineer: Infrastructure & Déploiement
- DBA: Optimisation Base de Données
- Sécurité Expert: Protection & Compliance
- Microservices: Architecture Distribuée

LOGIQUE MÉTIER:
Content creation → Storage allocation → Multi-cloud distribution → 
CDN optimization → Backup strategies → Performance monitoring → Cost optimization

Enterprise Storage Deployment Suite for IA-Influencer-Agent platform
providing comprehensive storage infrastructure management capabilities.
"""
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "© 2025 Fahed Mlaiel"

# Core Storage Managers
from .s3_manager import (
    S3Manager,
    S3BucketConfig,
    S3DeploymentMetrics,
    S3StorageClass,
    S3Region,
    S3ConfigurationManager,
    create_s3_manager
)

from .volume_manager import (
    VolumeManager,
    VolumeConfig,
    VolumeMetrics,
    VolumeType,
    StorageClass as VolumeStorageClass,
    VolumeAccessMode,
    VolumeStatus,
    VolumeConfigurationManager,
    create_volume_manager
)

from .backup_storage import (
    BackupStorageManager,
    BackupConfig,
    BackupJob,
    BackupMetrics,
    BackupType,
    BackupDestination,
    BackupStatus,
    CompressionType,
    EncryptionType,
    BackupConfigurationManager,
    create_backup_manager
)

from .cdn_manager import (
    CDNManager,
    CDNConfig,
    CDNMetrics,
    CDNProvider,
    CachePolicy,
    ContentType,
    DistributionStatus,
    CDNConfigurationManager,
    create_cdn_manager
)

# Advanced Storage Managers
from .distributed_storage import (
    DistributedStorageManager,
    DistributedStorageConfig,
    StorageNode,
    DistributedStorageMetrics,
    DistributedStorageType,
    ReplicationStrategy,
    ConsistencyLevel,
    ShardingStrategy,
    DistributedStorageConfigurationManager,
    create_distributed_storage_manager
)

from .performance_optimizer import (
    StoragePerformanceOptimizer,
    PerformanceMetric,
    PerformanceBaseline,
    OptimizationRecommendation,
    PerformanceAnalysisResult,
    PerformanceMetricType,
    OptimizationPriority,
    OptimizationType,
    performance_optimizer,
    create_performance_optimizer
)

from .security_manager import (
    StorageSecurityManager,
    SecurityPolicy,
    EncryptionKey,
    AccessToken,
    SecurityAuditEvent,
    SecurityMetrics,
    SecurityLevel,
    EncryptionAlgorithm,
    AccessPermission,
    ComplianceStandard,
    ThreatLevel,
    security_manager,
    create_security_manager,
    create_high_security_policy
)

from .advanced_backup import (
    AdvancedBackupManager,
    BackupPolicy,
    BackupMetadata,
    RecoveryRequest,
    BackupMetrics as AdvancedBackupMetrics,
    BackupType as AdvancedBackupType,
    BackupTier,
    RecoveryObjective,
    BackupStatus as AdvancedBackupStatus,
    CloudProvider,
    backup_manager,
    create_backup_manager as create_advanced_backup_manager,
    create_custom_backup_policy
)

# Main exports for external use
__all__ = [
    # Core Storage Managers
    "S3Manager",
    "S3BucketConfig", 
    "S3DeploymentMetrics",
    "S3StorageClass",
    "S3Region",
    "S3ConfigurationManager",
    "create_s3_manager",
    
    "VolumeManager",
    "VolumeConfig",
    "VolumeMetrics", 
    "VolumeType",
    "VolumeStorageClass",
    "VolumeAccessMode",
    "VolumeStatus",
    "VolumeConfigurationManager",
    "create_volume_manager",
    
    "BackupStorageManager",
    "BackupConfig",
    "BackupJob",
    "BackupMetrics",
    "BackupType",
    "BackupDestination", 
    "BackupStatus",
    "CompressionType",
    "EncryptionType",
    "BackupConfigurationManager",
    "create_backup_manager",
    
    "CDNManager",
    "CDNConfig",
    "CDNMetrics",
    "CDNProvider",
    "CachePolicy",
    "ContentType",
    "DistributionStatus",
    "CDNConfigurationManager",
    "create_cdn_manager",
    
    # Advanced Storage Managers
    "DistributedStorageManager",
    "DistributedStorageConfig",
    "StorageNode",
    "DistributedStorageMetrics",
    "DistributedStorageType",
    "ReplicationStrategy",
    "ConsistencyLevel",
    "ShardingStrategy",
    "DistributedStorageConfigurationManager",
    "create_distributed_storage_manager",
    
    "StoragePerformanceOptimizer",
    "PerformanceMetric",
    "PerformanceBaseline",
    "OptimizationRecommendation",
    "PerformanceAnalysisResult",
    "PerformanceMetricType",
    "OptimizationPriority",
    "OptimizationType",
    "performance_optimizer",
    "create_performance_optimizer",
    
    "StorageSecurityManager",
    "SecurityPolicy",
    "EncryptionKey",
    "AccessToken",
    "SecurityAuditEvent",
    "SecurityMetrics",
    "SecurityLevel",
    "EncryptionAlgorithm",
    "AccessPermission",
    "ComplianceStandard",
    "ThreatLevel",
    "security_manager",
    "create_security_manager",
    "create_high_security_policy",
    
    "AdvancedBackupManager",
    "BackupPolicy",
    "BackupMetadata",
    "RecoveryRequest",
    "AdvancedBackupMetrics",
    "AdvancedBackupType",
    "BackupTier",
    "RecoveryObjective",
    "AdvancedBackupStatus",
    "CloudProvider",
    "backup_manager",
    "create_advanced_backup_manager",
    "create_custom_backup_policy",
]# Module metadata
__module_info__ = {
    "name": "storage_deployment",
    "description": "Industrial storage deployment and management suite",
    "version": __version__,
    "author": __author__,
    "components": [
        "S3 Storage Management",
        "Volume Storage Management", 
        "Backup & Recovery Systems",
        "CDN & Edge Distribution"
    ],
    "capabilities": [
        "Multi-cloud storage orchestration",
        "Automated backup strategies",
        "Global CDN distribution",
        "Performance optimization",
        "Cost management",
        "Security compliance",
        "Disaster recovery",
        "Real-time monitoring"
    ]
}
