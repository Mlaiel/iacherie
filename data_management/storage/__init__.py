"""🗄️ Storage System Module - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/storage/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps
Type: Industrial Storage System - Multi-Tier Enterprise Production-Ready
Responsibility: Stockage intelligent multi-format avec protection et distribution avancée
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute tentative de vol,
reproduction, modification ou utilisation non autorisée donnera lieu à des
poursuites judiciaires selon la loi allemande et internationale.

LOGIQUE MÉTIER STORAGE:
Upload Multi-Format → Analyse Intelligente → Stockage Multi-Tier → 
Réplication Cross-Cloud → CDN Distribution → Cache Optimisé → 
Protection Avancée → Analytics Real-time → Lifecycle Management
"""from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Protocol
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum

# Core storage components
from .manager import (
    StorageManager, StorageRequest, StorageResponse, 
    StorageTier, ContentType
)

from .cloud_storage import (
    CloudStorageManager, AsyncCloudStorageManager, 
    CloudConfig, CloudProvider
)

from .local_storage import (
    LocalStorageManager, LocalStorageConfig,
    NetworkStorageManager, DistributedFileSystemManager
)

from .cdn_storage import (
    CDNStorageManager, CDNConfig, CDNProvider,
    GlobalDistributionManager, EdgeCacheManager
)

from .cache_storage import (
    CacheStorageManager, CacheConfig, CacheProvider,
    RedisStorageCache, MemcachedStorageCache, InMemoryCache
)

# Processing engines
from .compression_engine import (
    CompressionEngine, CompressionAlgorithm, CompressionConfig, 
    CompressionResult, ContentTypeAnalyzer
)

from .encryption_engine import (
    EncryptionEngine, EncryptionAlgorithm, EncryptionConfig,
    KeyManagementSystem, SecurityAuditLogger
)

from .deduplication_engine import (
    DeduplicationEngine, DeduplicationConfig, HashingStrategy,
    ContentDeduplicator, StorageOptimizer
)

from .lifecycle_engine import (
    LifecycleEngine, LifecyclePolicy, LifecycleAction,
    TieringManager, ArchivalManager, RetentionManager
)

from .replication_engine import (
    ReplicationEngine, ReplicationConfig, ReplicationStrategy,
    CrossRegionReplicator, BackupReplicator, SyncManager
)

from .analytics_engine import (
    AnalyticsEngine, StorageAnalytics, PerformanceMetrics,
    UsageAnalyzer, CostAnalyzer, TrendAnalyzer
)

# Utility components
from .metadata_extractor import (
    MetadataExtractor, ContentMetadata, 
    AudioMetadataExtractor, VideoMetadataExtractor, ImageMetadataExtractor
)

from .content_analyzer import (
    ContentAnalyzer, ContentAnalysis, QualityAnalyzer,
    FingerprintAnalyzer, SimilarityAnalyzer
)

from .performance_monitor import (
    PerformanceMonitor, PerformanceReport, MetricsCollector,
    AlertManager, HealthChecker
)

# New advanced modules
from .distributed_storage import (
    DistributedStorageManager, ShardingManager, 
    ConsistencyManager, PartitionManager
)

from .backup_storage import (
    BackupStorageManager, BackupScheduler, BackupVerifier,
    IncrementalBackupEngine, SnapshotManager
)

from .archive_storage import (
    ArchiveStorageManager, LongTermRetention, ArchivalPolicy,
    ColdStorageManager, DeepArchiveManager
)

from .sync_engine import (
    SyncEngine, BidirectionalSync, ConflictResolver,
    DeltaSyncManager, RealTimeSyncManager
)

from .integrity_checker import (
    IntegrityChecker, ChecksumValidator, CorruptionDetector,
    DataRepairManager, ConsistencyValidator
)

from .access_controller import (
    AccessController, PermissionManager, AuditLogger,
    TokenManager, AccessPolicyEngine
)

from .quota_manager import (
    QuotaManager, UsageLimiter, BillingManager,
    ResourceAllocationManager, TierLimitManager
)

from .migration_engine import (
    MigrationEngine, DataMigrator, CloudMigrationManager,
    LegacyDataConverter, BatchMigrationProcessor
)

# Storage configuration and factories
ENTERPRISE_STORAGE_CONFIG = {
    # Core settings
    'default_tier': StorageTier.WARM,
    'enable_compression': True,
    'enable_encryption': True,
    'enable_deduplication': True,
    'enable_cdn': True,
    'enable_replication': True,
    'enable_versioning': True,
    
    # Performance settings
    'max_file_size': 5 * 1024 * 1024 * 1024,  # 5GB
    'multipart_threshold': 100 * 1024 * 1024,  # 100MB
    'concurrent_uploads': 10,
    'concurrent_downloads': 20,
    'timeout_seconds': 300,
    'retry_attempts': 3,
    
    # Business logic settings
    'supported_formats': [
        'audio/*', 'video/*', 'image/*', 'text/*',
        'application/pdf', 'application/json',
        'fingerprint/*', 'embedding/*', 'model/*'
    ],
    'retention_policies': {
        'hot_tier_days': 30,
        'warm_tier_days': 90,
        'cold_tier_days': 365,
        'archive_tier_days': 2555  # 7 years
    },
    
    # Security settings
    'encryption_algorithm': 'AES-256-GCM',
    'key_rotation_days': 90,
    'audit_logging': True,
    'access_logging': True,
    'integrity_checking': True,
    
    # Cost optimization
    'intelligent_tiering': True,
    'compression_threshold': 1024,  # 1KB
    'deduplication_enabled': True,
    'lifecycle_management': True,
    
    # Multi-cloud settings
    'primary_cloud': 'aws_s3',
    'backup_clouds': ['azure_blob', 'google_cloud'],
    'cdn_providers': ['cloudfront', 'cloudflare'],
    'cache_providers': ['redis', 'memcached'],
    
    # Content-specific settings
    'audio_quality_preservation': True,
    'video_transcoding': True,
    'image_optimization': True,
    'fingerprint_indexing': True,
    'embedding_vectorization': True,
    
    # Monitoring and analytics
    'performance_monitoring': True,
    'usage_analytics': True,
    'cost_tracking': True,
    'health_checks': True,
    'alerting_enabled': True
}

# Provider type mappings
STORAGE_PROVIDER_TYPES = {
    'cloud': ['aws_s3', 'azure_blob', 'google_cloud', 'minio'],
    'local': ['filesystem', 'network_storage', 'distributed_fs'],
    'cdn': ['cloudfront', 'cloudflare', 'azure_cdn', 'google_cdn'],
    'cache': ['redis', 'memcached', 'inmemory', 'hybrid'],
    'backup': ['glacier', 'archive', 'tape_storage'],
    'distributed': ['hdfs', 'ceph', 'glusterfs', 'ipfs']
}

# Content type mappings for intelligent processing
CONTENT_TYPE_MAPPINGS = {
    ContentType.AUDIO: {
        'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'mime_types': ['audio/*'],
        'default_compression': CompressionAlgorithm.MP3_OPTIMIZED,
        'metadata_fields': ['duration', 'bitrate', 'sample_rate', 'channels', 'genre', 'artist']
    },
    ContentType.VIDEO: {
        'extensions': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
        'mime_types': ['video/*'],
        'default_compression': CompressionAlgorithm.MP4_COMPRESSED,
        'metadata_fields': ['duration', 'resolution', 'framerate', 'codec', 'bitrate']
    },
    ContentType.IMAGE: {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        'mime_types': ['image/*'],
        'default_compression': CompressionAlgorithm.WEBP,
        'metadata_fields': ['resolution', 'color_depth', 'format', 'creation_date']
    },
    ContentType.TEXT: {
        'extensions': ['.txt', '.md', '.html', '.css', '.js', '.json', '.xml'],
        'mime_types': ['text/*', 'application/json', 'application/xml'],
        'default_compression': CompressionAlgorithm.GZIP,
        'metadata_fields': ['encoding', 'language', 'word_count', 'content_type']
    },
    ContentType.FINGERPRINT: {
        'extensions': ['.fp', '.hash', '.signature'],
        'mime_types': ['application/fingerprint'],
        'default_compression': CompressionAlgorithm.LZMA,
        'metadata_fields': ['algorithm', 'precision', 'content_hash', 'creation_time']
    },
    ContentType.EMBEDDING: {
        'extensions': ['.emb', '.vec', '.tensor'],
        'mime_types': ['application/embedding'],
        'default_compression': CompressionAlgorithm.LZMA,
        'metadata_fields': ['dimensions', 'model_type', 'precision', 'creation_time']
    }
}

# Logging configuration
logger = logging.getLogger("data_management.storage")
logger.setLevel(logging.INFO)

class StorageFactory:
    """Factory for creating storage managers with enterprise configurations"""    
    @staticmethod
    def create_enterprise_manager(
        config: Optional[Dict[str, Any]] = None
    ) -> StorageManager:
        """Create enterprise storage manager with full feature set"""        final_config = {**ENTERPRISE_STORAGE_CONFIG, **(config or {})}
        return StorageManager(final_config)
    
    @staticmethod
    def create_cloud_manager(
        provider: CloudProvider,
        credentials: Dict[str, str],
        config: Optional[Dict[str, Any]] = None
    ) -> CloudStorageManager:
        """Create cloud-specific storage manager"""        cloud_config = CloudConfig(
            provider=provider,
            **credentials,
            **(config or {})
        )
        return CloudStorageManager(cloud_config)
    
    @staticmethod
    def create_hybrid_manager(
        cloud_config: CloudConfig,
        local_config: LocalStorageConfig,
        cdn_config: Optional[CDNConfig] = None,
        cache_config: Optional[CacheConfig] = None
    ) -> StorageManager:
        """Create hybrid storage manager with multiple providers"""        config = {
            'cloud_config': cloud_config,
            'local_config': local_config,
            'cdn_config': cdn_config,
            'cache_config': cache_config,
            **ENTERPRISE_STORAGE_CONFIG
        }
        return StorageManager(config)

def initialize_storage_system(config: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize complete storage system with all components"""    try:
        # Create main storage manager
        storage_manager = StorageFactory.create_enterprise_manager(config)
        
        # Initialize performance monitoring
        performance_monitor = PerformanceMonitor()
        
        # Initialize analytics engine
        analytics_engine = AnalyticsEngine(config.get('analytics_config', {}))
        
        # Initialize access controller
        access_controller = AccessController(config.get('access_config', {}))
        
        # Initialize quota manager
        quota_manager = QuotaManager(config.get('quota_config', {}))
        
        logger.info("✅ Storage system initialized successfully")
        
        return {
            'storage_manager': storage_manager,
            'performance_monitor': performance_monitor,
            'analytics_engine': analytics_engine,
            'access_controller': access_controller,
            'quota_manager': quota_manager,
            'status': 'initialized',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize storage system: {str(e)}")
        raise

def get_content_type_from_filename(filename: str) -> ContentType:
    """Determine content type from filename"""    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    for content_type, mapping in CONTENT_TYPE_MAPPINGS.items():
        if extension in mapping['extensions']:
            return content_type
    
    return ContentType.DOCUMENT  # Default fallback

def get_optimal_storage_tier(
    content_type: ContentType,
    file_size: int,
    access_pattern: str = 'unknown'
) -> StorageTier:
    """Determine optimal storage tier based on content characteristics"""    # High-priority content types
    if content_type in [ContentType.FINGERPRINT, ContentType.EMBEDDING]:
        return StorageTier.HOT
    
    # Active content based on access pattern
    if access_pattern in ['frequent', 'real_time']:
        return StorageTier.HOT
    
    # Recent or medium access content
    if access_pattern in ['regular', 'periodic']:
        return StorageTier.WARM
    
    # Large files or cold access
    if file_size > 100 * 1024 * 1024 or access_pattern == 'rare':  # 100MB
        return StorageTier.COLD
    
    # Archive content
    if access_pattern in ['archive', 'backup']:
        return StorageTier.ARCHIVE
    
    # Default tier
    return StorageTier.WARM

# Module exports - Complete enterprise storage system
__all__ = [
    # Core Management
    'StorageManager', 'StorageRequest', 'StorageResponse',
    'StorageTier', 'ContentType',
    
    # Storage Providers
    'CloudStorageManager', 'AsyncCloudStorageManager',
    'LocalStorageManager', 'NetworkStorageManager', 'DistributedFileSystemManager',
    'CDNStorageManager', 'GlobalDistributionManager', 'EdgeCacheManager',
    'CacheStorageManager', 'RedisStorageCache', 'MemcachedStorageCache',
    
    # Processing Engines
    'CompressionEngine', 'ContentTypeAnalyzer',
    'EncryptionEngine', 'KeyManagementSystem', 'SecurityAuditLogger',
    'DeduplicationEngine', 'ContentDeduplicator', 'StorageOptimizer',
    'LifecycleEngine', 'TieringManager', 'ArchivalManager', 'RetentionManager',
    'ReplicationEngine', 'CrossRegionReplicator', 'BackupReplicator', 'SyncManager',
    'AnalyticsEngine', 'UsageAnalyzer', 'CostAnalyzer', 'TrendAnalyzer',
    
    # Advanced Storage Systems
    'DistributedStorageManager', 'ShardingManager', 'ConsistencyManager',
    'BackupStorageManager', 'BackupScheduler', 'IncrementalBackupEngine',
    'ArchiveStorageManager', 'LongTermRetention', 'ColdStorageManager',
    'SyncEngine', 'BidirectionalSync', 'ConflictResolver',
    'IntegrityChecker', 'ChecksumValidator', 'CorruptionDetector',
    'AccessController', 'PermissionManager', 'AuditLogger',
    'QuotaManager', 'UsageLimiter', 'BillingManager',
    'MigrationEngine', 'DataMigrator', 'CloudMigrationManager',
    
    # Utility Components
    'MetadataExtractor', 'AudioMetadataExtractor', 'VideoMetadataExtractor',
    'ContentAnalyzer', 'QualityAnalyzer', 'FingerprintAnalyzer',
    'PerformanceMonitor', 'MetricsCollector', 'AlertManager',
    
    # Configuration Classes
    'CloudConfig', 'LocalStorageConfig', 'CDNConfig', 'CacheConfig',
    'CompressionConfig', 'EncryptionConfig', 'DeduplicationConfig',
    'LifecyclePolicy', 'ReplicationConfig',
    
    # Enums and Constants
    'CloudProvider', 'CDNProvider', 'CacheProvider',
    'CompressionAlgorithm', 'EncryptionAlgorithm',
    'LifecycleAction', 'ReplicationStrategy',
    
    # Factory and Utilities
    'StorageFactory', 'initialize_storage_system',
    'get_content_type_from_filename', 'get_optimal_storage_tier',
    
    # Configuration Constants
    'ENTERPRISE_STORAGE_CONFIG', 'STORAGE_PROVIDER_TYPES', 'CONTENT_TYPE_MAPPINGS'
]

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"
__license__ = "Proprietary - All Rights Reserved"

from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta
import hashlib
import os

from .cloud_storage import CloudStorageManager, AsyncCloudStorageManager
from .local_storage import LocalStorageManager, AsyncLocalStorageManager
from .cdn_storage import CDNStorageManager, AsyncCDNStorageManager
from .cache_storage import CacheStorageManager, AsyncCacheStorageManager

class StorageTier(Enum):
    """Niveaux de stockage par fréquence d'accès"""    HOT = "hot"        # Accès fréquent (< 30 jours)
    WARM = "warm"      # Accès occasionnel (30-90 jours)
    COLD = "cold"      # Accès rare (90-365 jours)
    ARCHIVE = "archive" # Archivage long terme (> 365 jours)

class StorageProvider(Enum):
    """Fournisseurs de stockage supportés"""    LOCAL = "local"
    S3 = "s3"
    MINIO = "minio"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    CDN = "cdn"
    CACHE = "cache"

@dataclass
class StorageConfig:
    """Configuration du système de stockage"""    
    # Configuration par tiers
    tier_config: Dict[StorageTier, Dict[str, Any]] = None
    
    # Providers par défaut par tiers
    default_providers: Dict[StorageTier, StorageProvider] = None
    
    # Limites de stockage par type de créateur
    storage_limits: Dict[str, Dict[str, int]] = None  # en GB
    
    # Politiques de rétention
    retention_policies: Dict[StorageTier, int] = None  # en jours
    
    def __post_init__(self):
        if self.tier_config is None:
            self.tier_config = {
                StorageTier.HOT: {
                    'replication': 2,
                    'compression': False,
                    'encryption': True,
                    'backup_frequency': 'daily'
                },
                StorageTier.WARM: {
                    'replication': 1,
                    'compression': True,
                    'encryption': True,
                    'backup_frequency': 'weekly'
                },
                StorageTier.COLD: {
                    'replication': 1,
                    'compression': True,
                    'encryption': True,
                    'backup_frequency': 'monthly'
                },
                StorageTier.ARCHIVE: {
                    'replication': 1,
                    'compression': True,
                    'encryption': True,
                    'backup_frequency': 'quarterly'
                }
            }
        
        if self.default_providers is None:
            self.default_providers = {
                StorageTier.HOT: StorageProvider.LOCAL,
                StorageTier.WARM: StorageProvider.S3,
                StorageTier.COLD: StorageProvider.S3,
                StorageTier.ARCHIVE: StorageProvider.S3
            }
        
        if self.storage_limits is None:
            self.storage_limits = {
                'musician': {
                    'hot': 100,    # 100 GB
                    'warm': 500,   # 500 GB
                    'cold': 1000,  # 1 TB
                    'archive': 5000 # 5 TB
                },
                'influencer': {
                    'hot': 200,
                    'warm': 1000,
                    'cold': 2000,
                    'archive': 10000
                },
                'photographer': {
                    'hot': 500,
                    'warm': 2000,
                    'cold': 5000,
                    'archive': 20000
                },
                'blogger': {
                    'hot': 50,
                    'warm': 200,
                    'cold': 500,
                    'archive': 2000
                },
                'comedian': {
                    'hot': 150,
                    'warm': 700,
                    'cold': 1500,
                    'archive': 7000
                }
            }
        
        if self.retention_policies is None:
            self.retention_policies = {
                StorageTier.HOT: 30,      # 30 jours
                StorageTier.WARM: 90,     # 90 jours
                StorageTier.COLD: 365,    # 1 an
                StorageTier.ARCHIVE: 2555 # 7 ans
            }

@dataclass
class StorageMetadata:
    """Métadonnées d'un objet stocké"""    file_id: str
    original_path: str
    storage_path: str
    provider: StorageProvider
    tier: StorageTier
    size: int
    checksum: str
    content_type: str
    creator_type: str
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    tags: List[str]
    encryption_key: Optional[str]

@dataclass
class StorageResult:
    """Résultat d'une opération de stockage"""    success: bool
    file_id: Optional[str]
    storage_path: Optional[str]
    metadata: Optional[StorageMetadata]
    errors: List[str]
    warnings: List[str]

class StorageManager:
    """Gestionnaire principal du système de stockage multi-tiers"""    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des gestionnaires de stockage
        self.storage_managers = {
            StorageProvider.LOCAL: LocalStorageManager(),
            StorageProvider.S3: CloudStorageManager('s3'),
            StorageProvider.MINIO: CloudStorageManager('minio'),
            StorageProvider.AZURE_BLOB: CloudStorageManager('azure'),
            StorageProvider.GOOGLE_CLOUD: CloudStorageManager('gcp'),
            StorageProvider.CDN: CDNStorageManager(),
            StorageProvider.CACHE: CacheStorageManager()
        }
        
        # Métadonnées des objets stockés
        self.metadata_store: Dict[str, StorageMetadata] = {}
        
        # Statistiques d'utilisation
        self.usage_stats: Dict[str, Dict[str, int]] = {}  # creator_type -> tier -> size_used
    
    def store(
        self,
        file_path: str,
        creator_type: str,
        content_type: str,
        tier: Optional[StorageTier] = None,
        tags: Optional[List[str]] = None
    ) -> StorageResult:
        """Stocke un fichier dans le tiers approprié"""        
        try:
            # Déterminer le tiers si non spécifié
            if tier is None:
                tier = self._determine_optimal_tier(file_path, creator_type, content_type)
            
            # Vérifier les limites de stockage
            if not self._check_storage_limits(creator_type, tier, file_path):
                return StorageResult(
                    success=False,
                    file_id=None,
                    storage_path=None,
                    metadata=None,
                    errors=["Limite de stockage dépassée pour ce tiers"],
                    warnings=[]
                )
            
            # Générer l'ID unique du fichier
            file_id = self._generate_file_id(file_path)
            
            # Calculer le checksum
            checksum = self._calculate_checksum(file_path)
            
            # Déterminer le provider
            provider = self.config.default_providers[tier]
            
            # Stocker le fichier
            storage_manager = self.storage_managers[provider]
            storage_path = storage_manager.store(file_path, file_id, tier)
            
            # Créer les métadonnées
            metadata = StorageMetadata(
                file_id=file_id,
                original_path=file_path,
                storage_path=storage_path,
                provider=provider,
                tier=tier,
                size=os.path.getsize(file_path),
                checksum=checksum,
                content_type=content_type,
                creator_type=creator_type,
                created_at=datetime.now(),
                last_accessed=None,
                access_count=0,
                tags=tags or [],
                encryption_key=None  # Sera généré par le storage manager si nécessaire
            )
            
            # Enregistrer les métadonnées
            self.metadata_store[file_id] = metadata
            
            # Mettre à jour les statistiques
            self._update_usage_stats(creator_type, tier, metadata.size)
            
            return StorageResult(
                success=True,
                file_id=file_id,
                storage_path=storage_path,
                metadata=metadata,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur stockage {file_path}: {e}")
            return StorageResult(
                success=False,
                file_id=None,
                storage_path=None,
                metadata=None,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[]
            )
    
    def retrieve(self, file_id: str, local_path: Optional[str] = None) -> StorageResult:
        """Récupère un fichier depuis le stockage"""        
        try:
            # Vérifier l'existence du fichier
            if file_id not in self.metadata_store:
                return StorageResult(
                    success=False,
                    file_id=file_id,
                    storage_path=None,
                    metadata=None,
                    errors=["Fichier non trouvé"],
                    warnings=[]
                )
            
            metadata = self.metadata_store[file_id]
            
            # Récupérer le fichier
            storage_manager = self.storage_managers[metadata.provider]
            retrieved_path = storage_manager.retrieve(metadata.storage_path, local_path)
            
            # Mettre à jour les statistiques d'accès
            metadata.last_accessed = datetime.now()
            metadata.access_count += 1
            
            return StorageResult(
                success=True,
                file_id=file_id,
                storage_path=retrieved_path,
                metadata=metadata,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur récupération {file_id}: {e}")
            return StorageResult(
                success=False,
                file_id=file_id,
                storage_path=None,
                metadata=None,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[]
            )
    
    def delete(self, file_id: str) -> StorageResult:
        """Supprime un fichier du stockage"""        
        try:
            if file_id not in self.metadata_store:
                return StorageResult(
                    success=False,
                    file_id=file_id,
                    storage_path=None,
                    metadata=None,
                    errors=["Fichier non trouvé"],
                    warnings=[]
                )
            
            metadata = self.metadata_store[file_id]
            
            # Supprimer le fichier
            storage_manager = self.storage_managers[metadata.provider]
            storage_manager.delete(metadata.storage_path)
            
            # Mettre à jour les statistiques
            self._update_usage_stats(metadata.creator_type, metadata.tier, -metadata.size)
            
            # Supprimer les métadonnées
            del self.metadata_store[file_id]
            
            return StorageResult(
                success=True,
                file_id=file_id,
                storage_path=None,
                metadata=metadata,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur suppression {file_id}: {e}")
            return StorageResult(
                success=False,
                file_id=file_id,
                storage_path=None,
                metadata=None,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[]
            )
    
    def migrate_tier(self, file_id: str, target_tier: StorageTier) -> StorageResult:
        """Migre un fichier vers un autre tiers de stockage"""        
        try:
            if file_id not in self.metadata_store:
                return StorageResult(
                    success=False,
                    file_id=file_id,
                    storage_path=None,
                    metadata=None,
                    errors=["Fichier non trouvé"],
                    warnings=[]
                )
            
            metadata = self.metadata_store[file_id]
            
            if metadata.tier == target_tier:
                return StorageResult(
                    success=True,
                    file_id=file_id,
                    storage_path=metadata.storage_path,
                    metadata=metadata,
                    errors=[],
                    warnings=["Fichier déjà dans le tiers cible"]
                )
            
            # Récupérer le fichier temporairement
            temp_path = f"/tmp/{file_id}"
            self.retrieve(file_id, temp_path)
            
            # Supprimer l'ancien fichier
            old_storage_manager = self.storage_managers[metadata.provider]
            old_storage_manager.delete(metadata.storage_path)
            
            # Stocker dans le nouveau tiers
            new_provider = self.config.default_providers[target_tier]
            new_storage_manager = self.storage_managers[new_provider]
            new_storage_path = new_storage_manager.store(temp_path, file_id, target_tier)
            
            # Mettre à jour les métadonnées
            metadata.tier = target_tier
            metadata.provider = new_provider
            metadata.storage_path = new_storage_path
            
            # Nettoyer le fichier temporaire
            os.remove(temp_path)
            
            return StorageResult(
                success=True,
                file_id=file_id,
                storage_path=new_storage_path,
                metadata=metadata,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur migration {file_id}: {e}")
            return StorageResult(
                success=False,
                file_id=file_id,
                storage_path=None,
                metadata=None,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[]
            )
    
    def auto_tier_migration(self) -> Dict[str, Any]:
        """Migration automatique basée sur les patterns d'accès"""        migrated_files = []
        errors = []
        
        current_time = datetime.now()
        
        for file_id, metadata in self.metadata_store.items():
            try:
                # Calculer l'âge du fichier et le dernier accès
                file_age = (current_time - metadata.created_at).days
                
                if metadata.last_accessed:
                    days_since_access = (current_time - metadata.last_accessed).days
                else:
                    days_since_access = file_age
                
                # Déterminer le tiers optimal
                optimal_tier = self._calculate_optimal_tier(file_age, days_since_access, metadata.access_count)
                
                # Migrer si nécessaire
                if optimal_tier != metadata.tier:
                    result = self.migrate_tier(file_id, optimal_tier)
                    if result.success:
                        migrated_files.append({
                            'file_id': file_id,
                            'from_tier': metadata.tier.value,
                            'to_tier': optimal_tier.value
                        })
                    else:
                        errors.extend(result.errors)
                        
            except Exception as e:
                errors.append(f"Erreur migration auto {file_id}: {str(e)}")
        
        return {
            'migrated_count': len(migrated_files),
            'migrated_files': migrated_files,
            'errors': errors
        }
    
    def get_usage_stats(self, creator_type: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les statistiques d'utilisation du stockage"""        if creator_type:
            return self.usage_stats.get(creator_type, {})
        return self.usage_stats
    
    def _determine_optimal_tier(self, file_path: str, creator_type: str, content_type: str) -> StorageTier:
        """Détermine le tiers de stockage optimal pour un nouveau fichier"""        # Par défaut, nouveaux fichiers vont en HOT
        return StorageTier.HOT
    
    def _check_storage_limits(self, creator_type: str, tier: StorageTier, file_path: str) -> bool:
        """Vérifie si les limites de stockage permettent d'ajouter le fichier"""        file_size_gb = os.path.getsize(file_path) / (1024**3)  # Convertir en GB
        
        # Récupérer la limite pour ce créateur et tiers
        limits = self.config.storage_limits.get(creator_type, {})
        tier_limit = limits.get(tier.value, float('inf'))
        
        # Récupérer l'utilisation actuelle
        current_usage = self.usage_stats.get(creator_type, {}).get(tier.value, 0)
        current_usage_gb = current_usage / (1024**3)
        
        return (current_usage_gb + file_size_gb) <= tier_limit
    
    def _generate_file_id(self, file_path: str) -> str:
        """Génère un ID unique pour le fichier"""        timestamp = datetime.now().isoformat()
        content = f"{file_path}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcule le checksum MD5 du fichier"""        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _update_usage_stats(self, creator_type: str, tier: StorageTier, size_delta: int):
        """Met à jour les statistiques d'utilisation"""        if creator_type not in self.usage_stats:
            self.usage_stats[creator_type] = {}
        
        if tier.value not in self.usage_stats[creator_type]:
            self.usage_stats[creator_type][tier.value] = 0
        
        self.usage_stats[creator_type][tier.value] += size_delta
    
    def _calculate_optimal_tier(self, file_age: int, days_since_access: int, access_count: int) -> StorageTier:
        """Calcule le tiers optimal basé sur les patterns d'usage"""        # Logique de migration automatique
        if days_since_access <= 7 and access_count > 5:
            return StorageTier.HOT
        elif days_since_access <= 30:
            return StorageTier.WARM
        elif days_since_access <= 90:
            return StorageTier.COLD
        else:
            return StorageTier.ARCHIVE

# Instance globale
storage_manager = StorageManager()

# Export des classes principales
__all__ = [
    'StorageManager',
    'StorageConfig',
    'StorageMetadata',
    'StorageResult',
    'StorageTier',
    'StorageProvider',
    'CloudStorageManager',
    'LocalStorageManager',
    'CDNStorageManager',
    'CacheStorageManager',
    'storage_manager'
]
