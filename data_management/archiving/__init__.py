"""Data Management Archiving Module - Enterprise Content Archival System

Provides comprehensive archival management for multi-format content including
audio, video, image, text, and composite content with intelligent lifecycle
management, retention policies, compression, and retrieval optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""
from .archival_manager import (
    ArchivalManager,
    ArchivalPolicy,
    ArchivalStatus,
    ArchivalTier,
    CompressionStrategy
)

from .archival_storage import (
    ArchivalStorageBackend,
    HierarchicalStorageManager,
    CloudArchivalStorage,
    LocalArchivalStorage
)

from .content_archiver import (
    ContentArchiver,
    ArchivalMetadata,
    ContentArchiveRecord,
    ArchivalJobStatus
)

from .retention_engine import (
    RetentionEngine,
    RetentionPolicy,
    RetentionAction,
    RetentionScheduler
)

from .lifecycle_manager import (
    ArchivalLifecycleManager,
    LifecyclePolicy,
    LifecycleStage,
    TransitionRule
)

from .compression_manager import (
    ArchivalCompressionManager,
    CompressionMethod,
    CompressionLevel,
    CompressionMetrics
)

from .retrieval_engine import (
    ArchivalRetrievalEngine,
    RetrievalRequest,
    RetrievalStrategy,
    RetrievalPerformance
)

from .metadata_manager import (
    ArchivalMetadataManager,
    MetadataSchema,
    IndexingStrategy,
    SearchCriteria
)

from .monitoring import (
    ArchivalMonitoring,
    ArchivalMetrics,
    PerformanceAnalytics,
    AlertManager
)

from .compliance import (
    ComplianceManager,
    RegulatoryRequirement,
    AuditTrail,
    ComplianceReport
)

from .models import (
    ArchiveEntry,
    ArchivalConfiguration,
    StorageQuota,
    AccessPattern
)

from .exceptions import (
    ArchivalError,
    StorageQuotaExceededError,
    RetentionPolicyViolationError,
    CompressionError,
    RetrievalTimeoutError
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Module exports
__all__ = [
    # Core managers
    'ArchivalManager',
    'ArchivalPolicy',
    'ArchivalStatus',
    'ArchivalTier',
    'CompressionStrategy',
    
    # Storage backends
    'ArchivalStorageBackend',
    'HierarchicalStorageManager',
    'CloudArchivalStorage',
    'LocalArchivalStorage',
    
    # Content archiving
    'ContentArchiver',
    'ArchivalMetadata',
    'ContentArchiveRecord',
    'ArchivalJobStatus',
    
    # Retention management
    'RetentionEngine',
    'RetentionPolicy',
    'RetentionAction',
    'RetentionScheduler',
    
    # Lifecycle management
    'ArchivalLifecycleManager',
    'LifecyclePolicy',
    'LifecycleStage',
    'TransitionRule',
    
    # Compression
    'ArchivalCompressionManager',
    'CompressionMethod',
    'CompressionLevel',
    'CompressionMetrics',
    
    # Retrieval
    'ArchivalRetrievalEngine',
    'RetrievalRequest',
    'RetrievalStrategy',
    'RetrievalPerformance',
    
    # Metadata management
    'ArchivalMetadataManager',
    'MetadataSchema',
    'IndexingStrategy',
    'SearchCriteria',
    
    # Monitoring & analytics
    'ArchivalMonitoring',
    'ArchivalMetrics',
    'PerformanceAnalytics',
    'AlertManager',
    
    # Compliance
    'ComplianceManager',
    'RegulatoryRequirement',
    'AuditTrail',
    'ComplianceReport',
    
    # Models
    'ArchiveEntry',
    'ArchivalConfiguration',
    'StorageQuota',
    'AccessPattern',
    
    # Exceptions
    'ArchivalError',
    'StorageQuotaExceededError',
    'RetentionPolicyViolationError',
    'CompressionError',
    'RetrievalTimeoutError'
]
