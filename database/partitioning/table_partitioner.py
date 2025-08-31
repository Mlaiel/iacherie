"""Table Partitioner - Specialized Partition Implementations

Ultra-industrial table-specific partitioning implementations for enterprise database operations.
Provides specialized partitioning strategies optimized for each table type in the IA Influencer
Agent + Content Protection Platform.

Specialized partitioners:
- ContentFingerprintPartitioner: Time + user-based for optimal fingerprint storage
- RevenueTrackingPartitioner: Financial compliance with temporal partitioning
- ProtectionAlertPartitioner: Real-time alerts with severity-based distribution
- UserContentPartitioner: Multi-tenant isolation with user-based partitioning
- AnalyticsPartitioner: High-volume analytics with compression optimization
- AuditLogPartitioner: Long-term compliance storage with immutable archival

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING 🚨
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, or distribution is strictly prohibited.
"""import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid

from sqlalchemy import text, inspect, MetaData, Table, Column, Index
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .partition_manager import (
    PartitionConfig, PartitionStrategy, PartitionType, 
    PartitionStatus, CompressionType, ArchivalPolicy
)

logger = logging.getLogger(__name__)

class PartitioningError(Exception):
    """Custom exception for partitioning operations"""    pass

class TablePartitioner(ABC):
    """    Abstract base class for table-specific partitioners
    
    Provides common functionality and interface for specialized partitioners
    """    
    def __init__(self, session_factory, table_name: str, config: PartitionConfig):
        """        Initialize table partitioner
        
        Args:
            session_factory: SQLAlchemy session factory
            table_name: Name of the table to partition
            config: Partition configuration
        """        self.session_factory = session_factory
        self.table_name = table_name
        self.config = config
        self.partitions_created = []
        
        logger.info(f"Initialized {self.__class__.__name__} for table: {table_name}")

    @abstractmethod
    def create_partitions(self) -> bool:
        """Create partitions for the table"""        pass

    @abstractmethod
    def get_partition_name(self, **kwargs) -> str:
        """Get partition name for given parameters"""        pass

    @abstractmethod
    def get_partition_for_data(self, **kwargs) -> str:
        """Determine which partition should contain specific data"""        pass

    def _create_base_indexes(self, session: Session, partition_name: str):
        """Create base indexes common to all partitions"""        try:
            # Primary key index (usually exists by default)
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_id 
                ON {partition_name} (id)
            """))
            
            # Created at index for temporal queries
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_created_at 
                ON {partition_name} (created_at)
            """))
            
            logger.debug(f"Created base indexes for partition: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create base indexes for {partition_name}: {e}")

    def _create_specialized_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for the partition"""        # To be overridden by subclasses
        pass

    def validate_partition_health(self, partition_name: str) -> bool:
        """Validate partition health and integrity"""        try:
            with self.session_factory() as session:
                # Check if partition exists
                exists_query = text("""                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = :partition_name
                    )
                """)
                exists = session.execute(exists_query, {'partition_name': partition_name}).scalar()
                
                if not exists:
                    logger.error(f"Partition does not exist: {partition_name}")
                    return False
                
                # Check partition constraints
                constraints_query = text("""                    SELECT conname, pg_get_constraintdef(oid) as definition
                    FROM pg_constraint 
                    WHERE conrelid = :partition_name::regclass
                """)
                constraints = session.execute(constraints_query, {'partition_name': partition_name}).fetchall()
                
                if not constraints:
                    logger.warning(f"No constraints found for partition: {partition_name}")
                
                # Check indexes
                indexes_query = text("""                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = :partition_name
                """)
                indexes = session.execute(indexes_query, {'partition_name': partition_name}).fetchall()
                
                logger.debug(f"Partition {partition_name} validation: {len(constraints)} constraints, {len(indexes)} indexes")
                return True
                
        except Exception as e:
            logger.error(f"Failed to validate partition {partition_name}: {e}")
            return False

    def get_partition_statistics(self, partition_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a partition"""        try:
            with self.session_factory() as session:
                stats_query = text(f"""                    SELECT 
                        COUNT(*) as row_count,
                        pg_total_relation_size('{partition_name}') as total_size_bytes,
                        pg_relation_size('{partition_name}') as table_size_bytes,
                        pg_indexes_size('{partition_name}') as indexes_size_bytes,
                        GREATEST(
                            last_vacuum, last_autovacuum, 
                            last_analyze, last_autoanalyze
                        ) as last_maintenance
                    FROM {partition_name}, pg_stat_user_tables 
                    WHERE schemaname = 'public' AND relname = '{partition_name}'
                """)
                
                result = session.execute(stats_query).fetchone()
                
                if result:
                    return {
                        'partition_name': partition_name,
                        'row_count': result.row_count or 0,
                        'total_size_bytes': result.total_size_bytes or 0,
                        'table_size_bytes': result.table_size_bytes or 0,
                        'indexes_size_bytes': result.indexes_size_bytes or 0,
                        'total_size_mb': round((result.total_size_bytes or 0) / (1024 * 1024), 2),
                        'last_maintenance': result.last_maintenance
                    }
                
                return {'partition_name': partition_name, 'error': 'No statistics available'}
                
        except Exception as e:
            logger.error(f"Failed to get statistics for partition {partition_name}: {e}")
            return {'partition_name': partition_name, 'error': str(e)}

class ContentFingerprintPartitioner(TablePartitioner):
    """    Specialized partitioner for content_fingerprints table
    
    Uses composite partitioning strategy:
    - Primary: Time-based (monthly) for efficient querying and archival
    - Secondary: User-based hash for multi-tenant isolation
    
    Optimized for:
    - High-volume fingerprint storage
    - Fast similarity searches
    - User isolation and privacy
    - Efficient archival and compression
    """    
    def __init__(self, session_factory, config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.COMPOSITE,
                partition_type=PartitionType.HORIZONTAL,
                table_name='content_fingerprints',
                partition_key='created_at,user_id',
                partition_count=24,  # 24 months of data
                max_partition_size=50_000_000,  # 50M fingerprints per partition
                compression=CompressionType.ZSTD,
                retention_days=1095,  # 3 years
                metadata={
                    'priority': 'high',
                    'business_critical': True,
                    'supports_similarity_search': True
                }
            )
        
        super().__init__(session_factory, 'content_fingerprints', config)

    def create_partitions(self) -> bool:
        """Create time+user composite partitions for content fingerprints"""        try:
            with self.session_factory() as session:
                current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Create monthly partitions for the next 2 years
                for month_idx in range(24):
                    partition_date = current_date + timedelta(days=32 * month_idx)
                    partition_date = partition_date.replace(day=1)
                    next_month = (partition_date + timedelta(days=32)).replace(day=1)
                    
                    month_partition_name = f"content_fingerprints_{partition_date.strftime('%Y_%m')}"
                    
                    # Create monthly partition with user sub-partitioning
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {month_partition_name} 
                    PARTITION OF content_fingerprints
                    FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_month.isoformat()}')
                    PARTITION BY HASH (user_id)
                    """                    
                    session.execute(text(create_partition_sql))
                    
                    # Create user sub-partitions (8 per month for load distribution)
                    for user_idx in range(8):
                        user_partition_name = f"{month_partition_name}_user_{user_idx:02d}"
                        
                        create_user_partition_sql = f"""                        CREATE TABLE IF NOT EXISTS {user_partition_name}
                        PARTITION OF {month_partition_name}
                        FOR VALUES WITH (modulus 8, remainder {user_idx})
                        """                        
                        session.execute(text(create_user_partition_sql))
                        self.partitions_created.append(user_partition_name)
                        
                        # Create specialized indexes for fingerprint operations
                        self._create_fingerprint_indexes(session, user_partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} content fingerprint partitions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create content fingerprint partitions: {e}")
            return False

    def _create_fingerprint_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for fingerprint operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # Fingerprint hash index for exact matches
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_fingerprint_hash 
                ON {partition_name} USING HASH (fingerprint_hash)
            """))
            
            # Content type + user index for filtering
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_content_type 
                ON {partition_name} (user_id, content_type)
            """))
            
            # Vector embedding index for similarity search (GiST for geometric operations)
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_vector_embedding 
                ON {partition_name} USING GiST (vector_embedding)
            """))
            
            # Metadata JSON index for flexible queries
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_metadata_gin 
                ON {partition_name} USING GIN (metadata)
            """))
            
            # Quality level index for filtering
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_quality_level 
                ON {partition_name} (quality_level) 
                WHERE quality_level IS NOT NULL
            """))
            
            logger.debug(f"Created fingerprint-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create fingerprint indexes for {partition_name}: {e}")

    def get_partition_name(self, created_at: datetime, user_id: int) -> str:
        """Get partition name for given timestamp and user ID"""        month_str = created_at.strftime('%Y_%m')
        user_partition = user_id % 8
        return f"content_fingerprints_{month_str}_user_{user_partition:02d}"

    def get_partition_for_data(self, created_at: datetime = None, user_id: int = None) -> str:
        """Determine partition for fingerprint data"""        if not created_at:
            created_at = datetime.utcnow()
        if not user_id:
            raise ValueError("user_id is required for content fingerprint partitioning")
        
        return self.get_partition_name(created_at, user_id)

class RevenueTrackingPartitioner(TablePartitioner):
    """    Specialized partitioner for revenue_tracking table
    
    Uses temporal partitioning strategy optimized for financial compliance:
    - Monthly partitions for current data
    - Quarterly partitions for historical data
    - Long-term retention (7 years) for compliance
    - Encrypted storage for sensitive financial data
    
    Optimized for:
    - Financial compliance requirements
    - Audit trail maintenance
    - Performance analytics
    - Automated tax reporting
    """    
    def __init__(self, session_factory, config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type=PartitionType.HORIZONTAL,
                table_name='revenue_tracking',
                partition_key='created_at',
                partition_count=84,  # 7 years of monthly partitions
                max_partition_size=25_000_000,  # 25M revenue records per partition
                compression=CompressionType.ZSTD,
                archival_policy=ArchivalPolicy.COMPLIANCE_BASED,
                retention_days=2555,  # 7 years for financial compliance
                metadata={
                    'compliance': 'financial',
                    'encryption_required': True,
                    'audit_trail': True,
                    'tax_reporting': True
                }
            )
        
        super().__init__(session_factory, 'revenue_tracking', config)

    def create_partitions(self) -> bool:
        """Create temporal partitions for revenue tracking"""        try:
            with self.session_factory() as session:
                current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Create monthly partitions for current and future periods
                for month_idx in range(-12, 24):  # 1 year past, 2 years future
                    partition_date = current_date + timedelta(days=32 * month_idx)
                    partition_date = partition_date.replace(day=1)
                    next_month = (partition_date + timedelta(days=32)).replace(day=1)
                    
                    partition_name = f"revenue_tracking_{partition_date.strftime('%Y_%m')}"
                    
                    # Create monthly partition
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {partition_name} 
                    PARTITION OF revenue_tracking
                    FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_month.isoformat()}')
                    """                    
                    session.execute(text(create_partition_sql))
                    self.partitions_created.append(partition_name)
                    
                    # Create revenue-specific indexes
                    self._create_revenue_indexes(session, partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} revenue tracking partitions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create revenue tracking partitions: {e}")
            return False

    def _create_revenue_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for revenue operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # User + platform index for user revenue queries
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_platform 
                ON {partition_name} (user_id, platform)
            """))
            
            # Revenue amount index for analytics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_revenue_amount 
                ON {partition_name} (revenue_amount DESC)
            """))
            
            # Currency index for multi-currency support
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_currency 
                ON {partition_name} (currency)
            """))
            
            # Revenue type + status for filtering
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_type_status 
                ON {partition_name} (revenue_type, revenue_status)
            """))
            
            # Tax reporting index
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_tax_period 
                ON {partition_name} (period_start, period_end)
            """))
            
            # Content ID index for content-based revenue tracking
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_content_id 
                ON {partition_name} (content_id) 
                WHERE content_id IS NOT NULL
            """))
            
            logger.debug(f"Created revenue-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create revenue indexes for {partition_name}: {e}")

    def get_partition_name(self, created_at: datetime) -> str:
        """Get partition name for given timestamp"""        return f"revenue_tracking_{created_at.strftime('%Y_%m')}"

    def get_partition_for_data(self, created_at: datetime = None, **kwargs) -> str:
        """Determine partition for revenue data"""        if not created_at:
            created_at = datetime.utcnow()
        
        return self.get_partition_name(created_at)

class ProtectionAlertPartitioner(TablePartitioner):
    """    Specialized partitioner for protection_alerts table
    
    Uses composite partitioning strategy for real-time alerting:
    - Primary: Time-based (daily) for recent high-volume alerts
    - Secondary: Severity-based for prioritization
    
    Optimized for:
    - Real-time alert processing
    - Severity-based queries
    - Fast incident response
    - Alert analytics and reporting
    """    
    def __init__(self, session_factory, config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.COMPOSITE,
                partition_type=PartitionType.HORIZONTAL,
                table_name='protection_alerts',
                partition_key='created_at,severity',
                partition_count=90,  # 90 days of daily partitions
                max_partition_size=100_000_000,  # 100M alerts per partition
                compression=CompressionType.LZ4,  # Fast compression for real-time
                retention_days=730,  # 2 years
                metadata={
                    'real_time': True,
                    'alert_system': True,
                    'incident_response': True
                }
            )
        
        super().__init__(session_factory, 'protection_alerts', config)

    def create_partitions(self) -> bool:
        """Create time+severity composite partitions for protection alerts"""        try:
            with self.session_factory() as session:
                current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Create daily partitions for the next 90 days
                for day_idx in range(-7, 90):  # 7 days past, 90 days future
                    partition_date = current_date + timedelta(days=day_idx)
                    next_day = partition_date + timedelta(days=1)
                    
                    day_partition_name = f"protection_alerts_{partition_date.strftime('%Y_%m_%d')}"
                    
                    # Create daily partition with severity sub-partitioning
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {day_partition_name} 
                    PARTITION OF protection_alerts
                    FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_day.isoformat()}')
                    PARTITION BY LIST (severity)
                    """                    
                    session.execute(text(create_partition_sql))
                    
                    # Create severity-based sub-partitions
                    severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
                    for severity in severities:
                        severity_partition_name = f"{day_partition_name}_sev_{severity.lower()}"
                        
                        create_severity_partition_sql = f"""                        CREATE TABLE IF NOT EXISTS {severity_partition_name}
                        PARTITION OF {day_partition_name}
                        FOR VALUES IN ('{severity}')
                        """                        
                        session.execute(text(create_severity_partition_sql))
                        self.partitions_created.append(severity_partition_name)
                        
                        # Create alert-specific indexes
                        self._create_alert_indexes(session, severity_partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} protection alert partitions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create protection alert partitions: {e}")
            return False

    def _create_alert_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for alert operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # Status index for alert management
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_status 
                ON {partition_name} (status)
            """))
            
            # Platform index for platform-specific alerts
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_platform 
                ON {partition_name} (platform) 
                WHERE platform IS NOT NULL
            """))
            
            # Fingerprint ID index for content correlation
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_fingerprint_id 
                ON {partition_name} (fingerprint_id) 
                WHERE fingerprint_id IS NOT NULL
            """))
            
            # Similarity score index for duplicate detection
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_similarity_score 
                ON {partition_name} (similarity_score DESC) 
                WHERE similarity_score IS NOT NULL
            """))
            
            # Detection method index for analytics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_detection_method 
                ON {partition_name} (detection_method) 
                WHERE detection_method IS NOT NULL
            """))
            
            # Evidence URL index for investigation
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_detected_url_hash 
                ON {partition_name} USING HASH (detected_url)
            """))
            
            logger.debug(f"Created alert-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create alert indexes for {partition_name}: {e}")

    def get_partition_name(self, created_at: datetime, severity: str) -> str:
        """Get partition name for given timestamp and severity"""        day_str = created_at.strftime('%Y_%m_%d')
        return f"protection_alerts_{day_str}_sev_{severity.lower()}"

    def get_partition_for_data(self, created_at: datetime = None, severity: str = None, **kwargs) -> str:
        """Determine partition for alert data"""        if not created_at:
            created_at = datetime.utcnow()
        if not severity:
            severity = 'MEDIUM'  # Default severity
        
        return self.get_partition_name(created_at, severity)

class UserContentPartitioner(TablePartitioner):
    """    Specialized partitioner for user_content table
    
    Uses user-based hash partitioning for multi-tenant isolation:
    - Hash partitioning by user_id for perfect tenant isolation
    - Secondary indexing by content_type for efficient filtering
    
    Optimized for:
    - Multi-tenant data isolation
    - User privacy and security
    - Content type filtering
    - Scalable user growth
    """    
    def __init__(self, session_factory, config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.USER_BASED,
                partition_type=PartitionType.HORIZONTAL,
                table_name='user_content',
                partition_key='user_id',
                partition_count=32,  # 32 user partitions for load distribution
                max_partition_size=75_000_000,  # 75M content items per partition
                compression=CompressionType.ZSTD,
                retention_days=1825,  # 5 years
                metadata={
                    'user_isolation': True,
                    'privacy_critical': True,
                    'content_management': True
                }
            )
        
        super().__init__(session_factory, 'user_content', config)

    def create_partitions(self) -> bool:
        """Create user-based hash partitions for user content"""        try:
            with self.session_factory() as session:
                # Create hash partitions based on user_id
                for partition_idx in range(self.config.partition_count):
                    partition_name = f"user_content_user_{partition_idx:03d}"
                    
                    # Create user-based hash partition
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {partition_name}
                    PARTITION OF user_content
                    FOR VALUES WITH (modulus {self.config.partition_count}, remainder {partition_idx})
                    """                    
                    session.execute(text(create_partition_sql))
                    self.partitions_created.append(partition_name)
                    
                    # Create user content-specific indexes
                    self._create_user_content_indexes(session, partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} user content partitions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create user content partitions: {e}")
            return False

    def _create_user_content_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for user content operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # User ID index (primary access pattern)
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_id 
                ON {partition_name} (user_id)
            """))
            
            # Content type + user index for filtering
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_content_type 
                ON {partition_name} (user_id, content_type)
            """))
            
            # Content status for workflow management
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_content_status 
                ON {partition_name} (content_status)
            """))
            
            # Privacy level for access control
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_privacy_level 
                ON {partition_name} (privacy_level) 
                WHERE privacy_level IS NOT NULL
            """))
            
            # Original filename for file management
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_original_filename 
                ON {partition_name} USING HASH (original_filename) 
                WHERE original_filename IS NOT NULL
            """))
            
            # File size for storage analytics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_file_size 
                ON {partition_name} (file_size_bytes) 
                WHERE file_size_bytes IS NOT NULL
            """))
            
            # Content genre and mood for recommendation systems
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_genre_mood 
                ON {partition_name} (content_genre, content_mood) 
                WHERE content_genre IS NOT NULL
            """))
            
            logger.debug(f"Created user content-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create user content indexes for {partition_name}: {e}")

    def get_partition_name(self, user_id: int) -> str:
        """Get partition name for given user ID"""        partition_idx = user_id % self.config.partition_count
        return f"user_content_user_{partition_idx:03d}"

    def get_partition_for_data(self, user_id: int = None, **kwargs) -> str:
        """Determine partition for user content data"""        if not user_id:
            raise ValueError("user_id is required for user content partitioning")
        
        return self.get_partition_name(user_id)

class AnalyticsPartitioner(TablePartitioner):
    """    Specialized partitioner for analytics tables (engagement_metrics, etc.)
    
    Uses temporal partitioning with aggressive compression:
    - Monthly partitions for recent data
    - Quarterly partitions for historical data
    - Heavy compression for long-term storage
    
    Optimized for:
    - High-volume analytics data
    - Time-series analysis
    - Compressed historical storage
    - Fast aggregation queries
    """    
    def __init__(self, session_factory, table_name: str = 'engagement_metrics', config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type=PartitionType.HORIZONTAL,
                table_name=table_name,
                partition_key='created_at',
                partition_count=36,  # 3 years of monthly partitions
                max_partition_size=200_000_000,  # 200M analytics records per partition
                compression=CompressionType.ZSTD,
                retention_days=1095,  # 3 years
                metadata={
                    'analytics': True,
                    'compression_priority': 'high',
                    'time_series': True
                }
            )
        
        super().__init__(session_factory, table_name, config)

    def create_partitions(self) -> bool:
        """Create temporal partitions for analytics data"""        try:
            with self.session_factory() as session:
                current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Create monthly partitions
                for month_idx in range(-6, 36):  # 6 months past, 3 years future
                    partition_date = current_date + timedelta(days=32 * month_idx)
                    partition_date = partition_date.replace(day=1)
                    next_month = (partition_date + timedelta(days=32)).replace(day=1)
                    
                    partition_name = f"{self.table_name}_{partition_date.strftime('%Y_%m')}"
                    
                    # Create monthly partition
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {partition_name} 
                    PARTITION OF {self.table_name}
                    FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_month.isoformat()}')
                    """                    
                    session.execute(text(create_partition_sql))
                    self.partitions_created.append(partition_name)
                    
                    # Create analytics-specific indexes
                    self._create_analytics_indexes(session, partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} analytics partitions for {self.table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create analytics partitions for {self.table_name}: {e}")
            return False

    def _create_analytics_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for analytics operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # User ID for user-specific analytics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_id 
                ON {partition_name} (user_id)
            """))
            
            # Platform for platform-specific analytics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_platform 
                ON {partition_name} (platform)
            """))
            
            # Metric type for filtering specific metrics
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_metric_type 
                ON {partition_name} (metric_type)
            """))
            
            # Content ID for content performance analysis
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_content_id 
                ON {partition_name} (content_id) 
                WHERE content_id IS NOT NULL
            """))
            
            # Metric value for aggregation queries
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_metric_value 
                ON {partition_name} (metric_value) 
                WHERE metric_value IS NOT NULL
            """))
            
            # Composite index for time-series queries
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_time_series 
                ON {partition_name} (user_id, metric_type, created_at)
            """))
            
            logger.debug(f"Created analytics-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create analytics indexes for {partition_name}: {e}")

    def get_partition_name(self, created_at: datetime) -> str:
        """Get partition name for given timestamp"""        return f"{self.table_name}_{created_at.strftime('%Y_%m')}"

    def get_partition_for_data(self, created_at: datetime = None, **kwargs) -> str:
        """Determine partition for analytics data"""        if not created_at:
            created_at = datetime.utcnow()
        
        return self.get_partition_name(created_at)

class AuditLogPartitioner(TablePartitioner):
    """    Specialized partitioner for audit_logs table
    
    Uses temporal partitioning with long-term retention:
    - Monthly partitions for active logs
    - Immutable partitions for compliance
    - Long-term archival (7 years)
    - Compressed storage for historical data
    
    Optimized for:
    - Compliance and audit requirements
    - Immutable log storage
    - Long-term data retention
    - Security and forensics
    """    
    def __init__(self, session_factory, config: PartitionConfig = None):
        if not config:
            config = PartitionConfig(
                strategy=PartitionStrategy.TEMPORAL,
                partition_type=PartitionType.HORIZONTAL,
                table_name='audit_logs',
                partition_key='created_at',
                partition_count=84,  # 7 years of monthly partitions
                max_partition_size=500_000_000,  # 500M audit records per partition
                compression=CompressionType.GZIP,  # Good compression for logs
                archival_policy=ArchivalPolicy.COMPLIANCE_BASED,
                retention_days=2555,  # 7 years for compliance
                metadata={
                    'audit_trail': True,
                    'immutable': True,
                    'compliance': 'security',
                    'forensics': True
                }
            )
        
        super().__init__(session_factory, 'audit_logs', config)

    def create_partitions(self) -> bool:
        """Create temporal partitions for audit logs"""        try:
            with self.session_factory() as session:
                current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Create monthly partitions for 7 years
                for month_idx in range(-12, 84):  # 1 year past, 7 years future
                    partition_date = current_date + timedelta(days=32 * month_idx)
                    partition_date = partition_date.replace(day=1)
                    next_month = (partition_date + timedelta(days=32)).replace(day=1)
                    
                    partition_name = f"audit_logs_{partition_date.strftime('%Y_%m')}"
                    
                    # Create monthly partition
                    create_partition_sql = f"""                    CREATE TABLE IF NOT EXISTS {partition_name} 
                    PARTITION OF audit_logs
                    FOR VALUES FROM ('{partition_date.isoformat()}') TO ('{next_month.isoformat()}')
                    """                    
                    session.execute(text(create_partition_sql))
                    self.partitions_created.append(partition_name)
                    
                    # Create audit-specific indexes
                    self._create_audit_indexes(session, partition_name)
                
                session.commit()
                logger.info(f"Created {len(self.partitions_created)} audit log partitions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create audit log partitions: {e}")
            return False

    def _create_audit_indexes(self, session: Session, partition_name: str):
        """Create specialized indexes for audit operations"""        try:
            # Base indexes
            self._create_base_indexes(session, partition_name)
            
            # User ID for user activity tracking
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_id 
                ON {partition_name} (user_id) 
                WHERE user_id IS NOT NULL
            """))
            
            # Action type for filtering specific actions
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_action_type 
                ON {partition_name} (action_type)
            """))
            
            # Entity type and ID for resource tracking
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_entity 
                ON {partition_name} (entity_type, entity_id)
            """))
            
            # Security classification for access control
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_security_classification 
                ON {partition_name} (security_classification)
            """))
            
            # IP address for security analysis
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_ip_address 
                ON {partition_name} USING HASH (ip_address) 
                WHERE ip_address IS NOT NULL
            """))
            
            # Session ID for session tracking
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_session_id 
                ON {partition_name} USING HASH (session_id) 
                WHERE session_id IS NOT NULL
            """))
            
            # Log level for filtering by severity
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_log_level 
                ON {partition_name} (log_level)
            """))
            
            # Compliance category for audit requirements
            session.execute(text(f"""                CREATE INDEX IF NOT EXISTS idx_{partition_name}_compliance_category 
                ON {partition_name} (compliance_category) 
                WHERE compliance_category IS NOT NULL
            """))
            
            logger.debug(f"Created audit-specific indexes for: {partition_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create audit indexes for {partition_name}: {e}")

    def get_partition_name(self, created_at: datetime) -> str:
        """Get partition name for given timestamp"""        return f"audit_logs_{created_at.strftime('%Y_%m')}"

    def get_partition_for_data(self, created_at: datetime = None, **kwargs) -> str:
        """Determine partition for audit log data"""        if not created_at:
            created_at = datetime.utcnow()
        
        return self.get_partition_name(created_at)

# Factory function for creating appropriate partitioner
def create_partitioner(table_name: str, session_factory, config: PartitionConfig = None) -> TablePartitioner:
    """    Factory function to create appropriate partitioner for table
    
    Args:
        table_name: Name of the table to partition
        session_factory: SQLAlchemy session factory
        config: Optional partition configuration
        
    Returns:
        TablePartitioner: Appropriate partitioner instance
    """    partitioner_map = {
        'content_fingerprints': ContentFingerprintPartitioner,
        'revenue_tracking': RevenueTrackingPartitioner,
        'protection_alerts': ProtectionAlertPartitioner,
        'user_content': UserContentPartitioner,
        'engagement_metrics': AnalyticsPartitioner,
        'audit_logs': AuditLogPartitioner
    }
    
    partitioner_class = partitioner_map.get(table_name)
    
    if not partitioner_class:
        # Default to analytics partitioner for unknown tables
        logger.warning(f"No specific partitioner for {table_name}, using default analytics partitioner")
        return AnalyticsPartitioner(session_factory, table_name, config)
    
    if table_name == 'engagement_metrics':
        return partitioner_class(session_factory, table_name, config)
    else:
        return partitioner_class(session_factory, config)

__all__ = [
    'TablePartitioner',
    'ContentFingerprintPartitioner',
    'RevenueTrackingPartitioner', 
    'ProtectionAlertPartitioner',
    'UserContentPartitioner',
    'AnalyticsPartitioner',
    'AuditLogPartitioner',
    'create_partitioner',
    'PartitioningError'
]
