"""
Configuration Database Module for IA-Influencer Agent Platform
=============================================================

Professional database configuration management for multi-tenant content protection
and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from .postgresql_config import PostgreSQLConfig
from .mongodb_config import MongoDBConfig  
from .redis_config import RedisConfig
from .faiss_config import FAISSConfig
from .elasticsearch_config import ElasticsearchConfig
from .connection_pool import DatabaseConnectionPool
from .migration_config import MigrationConfig
from .backup_config import BackupConfig
from .vector_database_config import VectorDatabaseConfig, VectorDatabaseManager
from .timeseries_config import TimeSeriesConfig, TimeSeriesManager
from .graph_database_config import GraphDatabaseConfig, GraphDatabaseManager
from .sharding_config import DatabaseShardingConfig, ShardingManager
from .index import DatabaseIndexManager, get_index_manager
from .master_config import MasterDatabaseConfig, MasterDatabaseManager, create_master_database_config

# New modules for content protection and monetization
from .content_protection_config import (
    ContentProtectionConfig, ContentProtectionManager,
    ContentType, ProtectionLevel, ViolationStatus, DetectionMethod,
    create_content_protection_config, create_content_protection_manager
)
from .monetization_config import (
    MonetizationConfig, MonetizationManager,
    Platform, RevenueType, PaymentStatus, Currency, DistributionStatus,
    create_monetization_config, create_monetization_manager
)
from .fingerprint_config import (
    FingerprintConfig, FingerprintManager,
    FingerprintType, ContentFormat, MatchingAlgorithm, ProcessingStatus,
    create_fingerprint_config, create_fingerprint_manager
)
from .platform_integration_config import (
    PlatformIntegrationConfig, PlatformIntegrationManager,
    PlatformType, IntegrationStatus, SyncFrequency, DataType,
    create_platform_integration_config, create_platform_integration_manager
)

__all__ = [
    # Core database configurations
    'PostgreSQLConfig',
    'MongoDBConfig',
    'RedisConfig', 
    'FAISSConfig',
    'ElasticsearchConfig',
    'DatabaseConnectionPool',
    'MigrationConfig',
    'BackupConfig',
    'VectorDatabaseConfig',
    'VectorDatabaseManager',
    'TimeSeriesConfig',
    'TimeSeriesManager',
    'GraphDatabaseConfig',
    'GraphDatabaseManager',
    'DatabaseShardingConfig',
    'ShardingManager',
    'DatabaseIndexManager',
    'get_index_manager',
    'MasterDatabaseConfig',
    'MasterDatabaseManager',
    'create_master_database_config',
    
    # Content protection system
    'ContentProtectionConfig',
    'ContentProtectionManager',
    'ContentType',
    'ProtectionLevel',
    'ViolationStatus', 
    'DetectionMethod',
    'create_content_protection_config',
    'create_content_protection_manager',
    
    # Monetization system
    'MonetizationConfig',
    'MonetizationManager',
    'Platform',
    'RevenueType',
    'PaymentStatus',
    'Currency',
    'DistributionStatus',
    'create_monetization_config',
    'create_monetization_manager',
    
    # Fingerprint system
    'FingerprintConfig',
    'FingerprintManager',
    'FingerprintType',
    'ContentFormat',
    'MatchingAlgorithm',
    'ProcessingStatus',
    'create_fingerprint_config',
    'create_fingerprint_manager',
    
    # Platform integration system
    'PlatformIntegrationConfig',
    'PlatformIntegrationManager',
    'PlatformType',
    'IntegrationStatus',
    'SyncFrequency',
    'DataType',
    'create_platform_integration_config',
    'create_platform_integration_manager'
]
