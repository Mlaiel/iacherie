"""Storage Configuration Module for IA-Influencer Agent Platform
=============================================================

Professional storage and file management configuration for enterprise content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
# Cloud Storage Configurations
from .s3_config import S3Config, s3_config
from .azure_blob_config import AzureBlobConfig, azure_blob_config
from .gcs_config import GCSConfig, gcs_config

# Local and Hybrid Storage
from .local_storage_config import LocalStorageConfig, local_storage_config

# Content Delivery and Processing
from .cdn_config import CDNConfig, cdn_config, CDNProvider
from .file_processing_config import (
    FileProcessingConfig, 
    file_processing_config,
    ProcessingType,
    AudioProcessingConfig,
    VideoProcessingConfig,
    ImageProcessingConfig,
    DocumentProcessingConfig
)

# Backup and Security
from .backup_storage_config import (
    BackupStorageConfig, 
    backup_storage_config,
    BackupType,
    BackupStorage,
    RetentionPolicy,
    BackupSchedule,
    BackupDestination
)
from .storage_security_config import (
    StorageSecurityConfig,
    storage_security_config,
    EncryptionAlgorithm,
    AccessLevel,
    SecurityThreat,
    EncryptionConfig,
    AccessControl,
    ContentScanningConfig,
    AuditingConfig
)

# Content Protection and Monitoring
from .content_protection_storage_config import (
    ContentProtectionStorageConfig,
    MonitoringStorageConfig,
    ProtectionContentType,
    FingerprintingEngine,
    content_protection_storage_config,
    monitoring_storage_config,
    validate_content_protection_storage_config,
    validate_monitoring_storage_config
)

# Monetization and Revenue Tracking
from .monetization_storage_config import (
    MonetizationStorageConfig,
    PaymentProcessingConfig,
    LicensingStorageConfig,
    MonetizationPlatform,
    RevenueType,
    PaymentProvider,
    monetization_storage_config,
    payment_processing_config,
    licensing_storage_config,
    validate_monetization_storage_config,
    validate_payment_processing_config
)

# Multi-Platform Distribution
from .distribution_storage_config import (
    MultiPlatformDistributionConfig,
    ContentSyndicationConfig,
    DistributionAnalyticsConfig,
    PlatformDistributionConfig,
    DistributionPlatform,
    ContentFormat,
    DistributionStatus,
    multi_platform_distribution_config,
    content_syndication_config,
    distribution_analytics_config,
    validate_distribution_config,
    validate_content_syndication_config
)

# Real-time Collaboration
from .collaboration_storage_config import (
    CollaborationStorageConfig,
    CreatorMatchingConfig,
    BrandCollaborationConfig,
    CollaborationAnalyticsConfig,
    CollaborationWorkspaceConfig,
    CollaborationType,
    CollaboratorRole,
    WorkspaceType,
    collaboration_storage_config,
    creator_matching_config,
    brand_collaboration_config,
    collaboration_analytics_config,
    validate_collaboration_storage_config,
    validate_creator_matching_config,
    create_collaboration_workspace
)

# Storage orchestration
from .index import (
    StorageOrchestrator,
    storage_orchestrator,
    initialize_storage_system,
    get_storage_orchestrator
)

# Advanced validation and health monitoring
from .storage_validation import (
    StorageValidator,
    StorageHealthStatus,
    StoragePerformanceMetrics,
    storage_validator,
    run_comprehensive_storage_validation,
    validate_storage_configuration_sync
)

# Global configuration instances for easy access
STORAGE_CONFIGS = {
    's3': s3_config,
    'azure': azure_blob_config,
    'gcs': gcs_config,
    'local': local_storage_config,
    'cdn': cdn_config,
    'processing': file_processing_config,
    'backup': backup_storage_config,
    'security': storage_security_config,
    'content_protection': content_protection_storage_config,
    'monitoring': monitoring_storage_config,
    'monetization': monetization_storage_config,
    'payment_processing': payment_processing_config,
    'licensing': licensing_storage_config,
    'distribution': multi_platform_distribution_config,
    'syndication': content_syndication_config,
    'distribution_analytics': distribution_analytics_config,
    'collaboration': collaboration_storage_config,
    'creator_matching': creator_matching_config,
    'brand_collaboration': brand_collaboration_config,
    'collaboration_analytics': collaboration_analytics_config
}

def get_storage_config(storage_type: str):
    """Get storage configuration by type."""    return STORAGE_CONFIGS.get(storage_type)

def validate_all_storage_configs() -> bool:
    """Validate all storage configurations."""    results = {}
    for name, config in STORAGE_CONFIGS.items():
        if hasattr(config, 'validate_configuration'):
            results[name] = config.validate_configuration()
        else:
            results[name] = True
    
    # Additional custom validation functions
    results['content_protection_validation'] = validate_content_protection_storage_config()
    results['monitoring_validation'] = validate_monitoring_storage_config()
    results['monetization_validation'] = validate_monetization_storage_config()
    results['payment_processing_validation'] = validate_payment_processing_config()
    results['distribution_validation'] = validate_distribution_config()
    results['syndication_validation'] = validate_content_syndication_config()
    results['collaboration_validation'] = validate_collaboration_storage_config()
    results['creator_matching_validation'] = validate_creator_matching_config()
    
    all_valid = all(results.values())
    if not all_valid:
        print("Storage configuration validation results:")
        for name, valid in results.items():
            status = "✅" if valid else "❌"
            print(f"  {status} {name}: {'Valid' if valid else 'Invalid'}")
    
    return all_valid

def get_storage_statistics() -> dict:
    """Get comprehensive storage statistics."""    stats = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'configurations': {}
    }
    
    for name, config in STORAGE_CONFIGS.items():
        if hasattr(config, 'export_configuration'):
            stats['configurations'][name] = config.export_configuration()
    
    return stats

__all__ = [
    # Main configuration classes
    'S3Config',
    'AzureBlobConfig', 
    'GCSConfig',
    'LocalStorageConfig',
    'CDNConfig',
    'FileProcessingConfig',
    'BackupStorageConfig',
    'StorageSecurityConfig',
    
    # Content Protection and Monitoring classes
    'ContentProtectionStorageConfig',
    'MonitoringStorageConfig',
    
    # Monetization and Revenue classes
    'MonetizationStorageConfig',
    'PaymentProcessingConfig',
    'LicensingStorageConfig',
    
    # Distribution and Syndication classes
    'MultiPlatformDistributionConfig',
    'ContentSyndicationConfig',
    'DistributionAnalyticsConfig',
    'PlatformDistributionConfig',
    
    # Collaboration classes
    'CollaborationStorageConfig',
    'CreatorMatchingConfig',
    'BrandCollaborationConfig',
    'CollaborationAnalyticsConfig',
    'CollaborationWorkspaceConfig',
    
    # Processing configurations
    'AudioProcessingConfig',
    'VideoProcessingConfig', 
    'ImageProcessingConfig',
    'DocumentProcessingConfig',
    
    # Backup configurations
    'BackupSchedule',
    'BackupDestination',
    
    # Security configurations
    'EncryptionConfig',
    'AccessControl',
    'ContentScanningConfig',
    'AuditingConfig',
    
    # Enums
    'CDNProvider',
    'ProcessingType',
    'BackupType',
    'BackupStorage',
    'RetentionPolicy',
    'EncryptionAlgorithm',
    'AccessLevel',
    'SecurityThreat',
    'ProtectionContentType',
    'FingerprintingEngine',
    'MonetizationPlatform',
    'RevenueType',
    'PaymentProvider',
    'DistributionPlatform',
    'ContentFormat',
    'DistributionStatus',
    'CollaborationType',
    'CollaboratorRole',
    'WorkspaceType',
    
    # Global instances
    's3_config',
    'azure_blob_config',
    'gcs_config', 
    'local_storage_config',
    'cdn_config',
    'file_processing_config',
    'backup_storage_config',
    'storage_security_config',
    'content_protection_storage_config',
    'monitoring_storage_config',
    'monetization_storage_config',
    'payment_processing_config',
    'licensing_storage_config',
    'multi_platform_distribution_config',
    'content_syndication_config',
    'distribution_analytics_config',
    'collaboration_storage_config',
    'creator_matching_config',
    'brand_collaboration_config',
    'collaboration_analytics_config',
    
    # Storage orchestration
    'StorageOrchestrator',
    'storage_orchestrator',
    'initialize_storage_system',
    'get_storage_orchestrator',
    
    # Advanced validation and health monitoring
    'StorageValidator',
    'StorageHealthStatus',
    'StoragePerformanceMetrics',
    'storage_validator',
    'run_comprehensive_storage_validation',
    'validate_storage_configuration_sync',
    
    # Utility functions
    'get_storage_config',
    'validate_all_storage_configs',
    'get_storage_statistics',
    'validate_content_protection_storage_config',
    'validate_monitoring_storage_config',
    'validate_monetization_storage_config',
    'validate_payment_processing_config',
    'validate_distribution_config',
    'validate_content_syndication_config',
    'validate_collaboration_storage_config',
    'validate_creator_matching_config',
    'create_collaboration_workspace',
    'STORAGE_CONFIGS'
]
