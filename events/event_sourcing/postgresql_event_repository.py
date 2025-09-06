"""PostgreSQL Event Repository - Optimized Implementation

High-performance PostgreSQL repository with advanced features like
partitioning, connection pooling, streaming, and enterprise-grade optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from . import DomainEvent, EventStoreInterface

logger = logging.getLogger(__name__)


class PartitionStrategy(Enum):
    """Event table partitioning strategies"""
    NONE = "none"
    BY_DATE = "by_date"
    BY_AGGREGATE = "by_aggregate"
    BY_AGGREGATE_AND_DATE = "by_aggregate_and_date"


class IndexStrategy(Enum):
    """Index optimization strategies"""
    BASIC = "basic"
    ADVANCED = "advanced"
    FULL_TEXT = "full_text"
    ANALYTICS = "analytics"


@dataclass
class PostgreSQLConfig:
    """PostgreSQL repository configuration"""
    connection_string: str
    max_connections: int = 100
    min_connections: int = 10
    command_timeout: int = 30
    query_timeout: int = 60
    partition_strategy: PartitionStrategy = PartitionStrategy.BY_AGGREGATE_AND_DATE
    index_strategy: IndexStrategy = IndexStrategy.ADVANCED
    enable_wal_archiving: bool = True
    enable_streaming_replication: bool = True
    backup_retention_days: int = 30
    table_prefix: str = "ainflue_"


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    total_queries: int = 0
    average_query_time: float = 0.0
    slow_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    connection_pool_usage: float = 0.0


class PostgreSQLSchemaManager:
    """Advanced schema management for PostgreSQL"""
    
    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self.table_prefix = config.table_prefix
    
    def get_base_table_schema(self) -> str:
        """Get base events table schema"""
        return f"""
        CREATE TABLE IF NOT EXISTS {self.table_prefix}events (
            event_id UUID PRIMARY KEY,
            aggregate_id UUID NOT NULL,
            aggregate_type VARCHAR(100) NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            event_version INTEGER NOT NULL,
            occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{{}}'::jsonb,
            checksum VARCHAR(64),
            compressed BOOLEAN DEFAULT FALSE,
            encryption_status VARCHAR(20) DEFAULT 'none'
        ) PARTITION BY {self._get_partition_clause()};
        """
    
    def _get_partition_clause(self) -> str:
        """Get partitioning clause based on strategy"""
        if self.config.partition_strategy == PartitionStrategy.BY_DATE:
            return "RANGE (occurred_at)"
        elif self.config.partition_strategy == PartitionStrategy.BY_AGGREGATE:
            return "HASH (aggregate_id)"
        elif self.config.partition_strategy == PartitionStrategy.BY_AGGREGATE_AND_DATE:
            return "RANGE (occurred_at)"
        else:
            return "RANGE (occurred_at)"  # Default fallback
    
    def get_partition_schemas(self) -> List[str]:
        """Get partition table schemas"""
        schemas = []
        
        if self.config.partition_strategy in [PartitionStrategy.BY_DATE, 
                                            PartitionStrategy.BY_AGGREGATE_AND_DATE]:
            # Create monthly partitions for the next 2 years
            current_date = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for i in range(24):  # 24 months
                partition_start = current_date + timedelta(days=i*30)
                partition_end = partition_start + timedelta(days=30)
                partition_name = f"{self.table_prefix}events_{partition_start.strftime('%Y_%m')}"
                
                schema = f"""
                CREATE TABLE IF NOT EXISTS {partition_name}
                PARTITION OF {self.table_prefix}events
                FOR VALUES FROM ('{partition_start.isoformat()}') TO ('{partition_end.isoformat()}');
                """
                schemas.append(schema)
        
        return schemas
    
    def get_index_schemas(self) -> List[str]:
        """Get index schemas based on strategy"""
        indexes = []
        table_name = f"{self.table_prefix}events"
        
        # Basic indexes - always created
        basic_indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_aggregate_id ON {table_name} (aggregate_id);",
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_aggregate_version ON {table_name} (aggregate_id, event_version);",
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_type ON {table_name} (event_type);",
            f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_occurred_at ON {table_name} (occurred_at);",
        ]
        indexes.extend(basic_indexes)
        
        # Advanced indexes
        if self.config.index_strategy in [IndexStrategy.ADVANCED, IndexStrategy.ANALYTICS]:
            advanced_indexes = [
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_composite ON {table_name} (aggregate_type, event_type, occurred_at);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_data_gin ON {table_name} USING GIN (event_data);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_metadata_gin ON {table_name} USING GIN (metadata);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_checksum ON {table_name} (checksum) WHERE checksum IS NOT NULL;",
            ]
            indexes.extend(advanced_indexes)
        
        # Full-text search indexes
        if self.config.index_strategy == IndexStrategy.FULL_TEXT:
            fulltext_indexes = [
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}events_fulltext ON {table_name} USING GIN (to_tsvector('english', event_data::text));",
            ]
            indexes.extend(fulltext_indexes)
        
        return indexes
    
    def get_performance_views(self) -> List[str]:
        """Get performance monitoring views"""
        views = []
        table_name = f"{self.table_prefix}events"
        
        # Event statistics view
        event_stats_view = f"""
        CREATE OR REPLACE VIEW {self.table_prefix}event_statistics AS
        SELECT 
            aggregate_type,
            event_type,
            COUNT(*) as event_count,
            MIN(occurred_at) as first_event,
            MAX(occurred_at) as last_event,
            AVG(EXTRACT(EPOCH FROM (created_at - occurred_at))) as avg_processing_delay
        FROM {table_name}
        GROUP BY aggregate_type, event_type;
        """
        views.append(event_stats_view)
        
        # Aggregate health view
        aggregate_health_view = f"""
        CREATE OR REPLACE VIEW {self.table_prefix}aggregate_health AS
        SELECT 
            aggregate_id,
            aggregate_type,
            COUNT(*) as total_events,
            MAX(event_version) as current_version,
            MAX(occurred_at) as last_activity,
            CASE 
                WHEN MAX(occurred_at) > NOW() - INTERVAL '1 day' THEN 'active'
                WHEN MAX(occurred_at) > NOW() - INTERVAL '7 days' THEN 'recent'
                WHEN MAX(occurred_at) > NOW() - INTERVAL '30 days' THEN 'inactive'
                ELSE 'stale'
            END as activity_status
        FROM {table_name}
        GROUP BY aggregate_id, aggregate_type;
        """
        views.append(aggregate_health_view)
        
        return views


class PostgreSQLEventStream:
    """Streaming event processor for PostgreSQL"""
    
    def __init__(self, connection_pool, config: PostgreSQLConfig):
        self.connection_pool = connection_pool
        self.config = config
        self.active_streams = {}
    
    async def stream_events(self, aggregate_id: Optional[str] = None, 
                          event_types: Optional[List[str]] = None,
                          from_timestamp: Optional[datetime] = None) -> AsyncGenerator[DomainEvent, None]:
        """Stream events in real-time"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Build query based on filters
                query = f"SELECT * FROM {self.config.table_prefix}events WHERE 1=1"
                params = []
                
                if aggregate_id:
                    query += " AND aggregate_id = $" + str(len(params) + 1)
                    params.append(aggregate_id)
                
                if event_types:
                    query += " AND event_type = ANY($" + str(len(params) + 1) + ")"
                    params.append(event_types)
                
                if from_timestamp:
                    query += " AND occurred_at >= $" + str(len(params) + 1)
                    params.append(from_timestamp)
                
                query += " ORDER BY occurred_at"
                
                # Execute query and stream results
                async with conn.transaction():
                    async for record in conn.cursor(query, *params):
                        yield DomainEvent(
                            event_id=record['event_id'],
                            aggregate_id=record['aggregate_id'],
                            aggregate_type=record['aggregate_type'],
                            event_type=record['event_type'],
                            event_data=record['event_data'],
                            event_version=record['event_version'],
                            occurred_at=record['occurred_at']
                        )
        except Exception as e:
            logger.error(f"Event streaming failed: {e}")
            raise


class PostgreSQLEventRepository(EventStoreInterface):
    """High-performance PostgreSQL event repository"""
    
    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self.connection_pool = None
        self.schema_manager = PostgreSQLSchemaManager(config)
        self.metrics = QueryMetrics()
        self.event_stream = None
        self._query_cache = {}
        self._connection_semaphore = None
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and schema"""
        try:
            import asyncpg
            
            # Create connection pool
            self.connection_pool = await asyncpg.create_pool(
                self.config.connection_string,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=self.config.command_timeout
            )
            
            # Initialize semaphore for connection management
            self._connection_semaphore = asyncio.Semaphore(self.config.max_connections)
            
            # Initialize schema
            await self._initialize_schema()
            
            # Initialize event stream
            self.event_stream = PostgreSQLEventStream(self.connection_pool, self.config)
            
            logger.info("PostgreSQL event repository initialized successfully")
        except ImportError:
            logger.warning("asyncpg not available, using mock implementation")
            self.connection_pool = "mock_pool"
            self.event_stream = None
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL repository: {e}")
            raise
    
    async def _initialize_schema(self):
        """Initialize database schema"""
        if self.connection_pool == "mock_pool":
            return
        
        try:
            async with self.connection_pool.acquire() as conn:
                # Create base table
                base_schema = self.schema_manager.get_base_table_schema()
                await conn.execute(base_schema)
                
                # Create partitions
                partition_schemas = self.schema_manager.get_partition_schemas()
                for schema in partition_schemas:
                    try:
                        await conn.execute(schema)
                    except Exception as e:
                        # Partition might already exist
                        logger.debug(f"Partition creation warning: {e}")
                
                # Create indexes
                index_schemas = self.schema_manager.get_index_schemas()
                for index_schema in index_schemas:
                    try:
                        await conn.execute(index_schema)
                    except Exception as e:
                        logger.debug(f"Index creation warning: {e}")
                
                # Create performance views
                view_schemas = self.schema_manager.get_performance_views()
                for view_schema in view_schemas:
                    try:
                        await conn.execute(view_schema)
                    except Exception as e:
                        logger.debug(f"View creation warning: {e}")
                
                logger.info("PostgreSQL schema initialized successfully")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
    
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int = None) -> None:
        """Save events with optimistic concurrency control"""
        if not events:
            return
        
        if self.connection_pool == "mock_pool":
            logger.info(f"Mock: Saved {len(events)} events for aggregate {aggregate_id}")
            return
        
        start_time = datetime.now()
        
        try:
            async with self._connection_semaphore:
                async with self.connection_pool.acquire() as conn:
                    async with conn.transaction():
                        # Check expected version if specified
                        if expected_version is not None:
                            current_version = await self._get_current_version(conn, aggregate_id)
                            if current_version != expected_version:
                                raise ConcurrencyError(
                                    f"Version mismatch: expected {expected_version}, got {current_version}"
                                )
                        
                        # Prepare batch insert
                        insert_query = f"""
                            INSERT INTO {self.config.table_prefix}events 
                            (event_id, aggregate_id, aggregate_type, event_type, 
                             event_data, event_version, occurred_at, checksum)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """
                        
                        # Insert events in batch
                        for event in events:
                            checksum = self._calculate_event_checksum(event)
                            await conn.execute(
                                insert_query,
                                event.event_id, aggregate_id, event.aggregate_type,
                                event.event_type, json.dumps(event.event_data),
                                event.event_version, event.occurred_at, checksum
                            )
                        
                        # Update metrics
                        self._update_write_metrics(start_time, len(events))
                        
                        logger.info(f"Saved {len(events)} events for aggregate {aggregate_id}")
                        
        except Exception as e:
            logger.error(f"Failed to save events: {e}")
            raise
    
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Get events for aggregate with caching"""
        if self.connection_pool == "mock_pool":
            logger.info(f"Mock: Retrieved events for aggregate {aggregate_id}")
            return []
        
        start_time = datetime.now()
        cache_key = f"{aggregate_id}:{from_version}"
        
        # Check cache first
        if cache_key in self._query_cache:
            self.metrics.cache_hits += 1
            return self._query_cache[cache_key]
        
        try:
            async with self._connection_semaphore:
                async with self.connection_pool.acquire() as conn:
                    query = f"""
                        SELECT event_id, aggregate_id, aggregate_type, event_type,
                               event_data, event_version, occurred_at
                        FROM {self.config.table_prefix}events
                        WHERE aggregate_id = $1 AND event_version >= $2
                        ORDER BY event_version
                    """
                    
                    rows = await conn.fetch(query, aggregate_id, from_version)
                    
                    events = []
                    for row in rows:
                        event_data = json.loads(row['event_data']) if isinstance(row['event_data'], str) else row['event_data']
                        events.append(DomainEvent(
                            event_id=row['event_id'],
                            aggregate_id=row['aggregate_id'],
                            aggregate_type=row['aggregate_type'],
                            event_type=row['event_type'],
                            event_data=event_data,
                            event_version=row['event_version'],
                            occurred_at=row['occurred_at']
                        ))
                    
                    # Cache result (with size limit)
                    if len(self._query_cache) < 1000:
                        self._query_cache[cache_key] = events
                    
                    self.metrics.cache_misses += 1
                    self._update_read_metrics(start_time)
                    
                    return events
                    
        except Exception as e:
            logger.error(f"Failed to get events for aggregate {aggregate_id}: {e}")
            return []
    
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 100) -> List[DomainEvent]:
        """Get all events with pagination"""
        if self.connection_pool == "mock_pool":
            logger.info("Mock: Retrieved all events")
            return []
        
        start_time = datetime.now()
        
        try:
            async with self._connection_semaphore:
                async with self.connection_pool.acquire() as conn:
                    if from_event_id:
                        query = f"""
                            SELECT event_id, aggregate_id, aggregate_type, event_type,
                                   event_data, event_version, occurred_at
                            FROM {self.config.table_prefix}events
                            WHERE occurred_at > (
                                SELECT occurred_at FROM {self.config.table_prefix}events 
                                WHERE event_id = $1
                            )
                            ORDER BY occurred_at
                            LIMIT $2
                        """
                        rows = await conn.fetch(query, from_event_id, limit)
                    else:
                        query = f"""
                            SELECT event_id, aggregate_id, aggregate_type, event_type,
                                   event_data, event_version, occurred_at
                            FROM {self.config.table_prefix}events
                            ORDER BY occurred_at
                            LIMIT $1
                        """
                        rows = await conn.fetch(query, limit)
                    
                    events = []
                    for row in rows:
                        event_data = json.loads(row['event_data']) if isinstance(row['event_data'], str) else row['event_data']
                        events.append(DomainEvent(
                            event_id=row['event_id'],
                            aggregate_id=row['aggregate_id'],
                            aggregate_type=row['aggregate_type'],
                            event_type=row['event_type'],
                            event_data=event_data,
                            event_version=row['event_version'],
                            occurred_at=row['occurred_at']
                        ))
                    
                    self._update_read_metrics(start_time)
                    return events
                    
        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            return []
    
    async def get_events_by_type(self, event_types: List[str], 
                               limit: int = 100) -> List[DomainEvent]:
        """Get events by type with performance optimization"""
        if self.connection_pool == "mock_pool":
            logger.info(f"Mock: Retrieved events by types {event_types}")
            return []
        
        start_time = datetime.now()
        
        try:
            async with self._connection_semaphore:
                async with self.connection_pool.acquire() as conn:
                    query = f"""
                        SELECT event_id, aggregate_id, aggregate_type, event_type,
                               event_data, event_version, occurred_at
                        FROM {self.config.table_prefix}events
                        WHERE event_type = ANY($1)
                        ORDER BY occurred_at DESC
                        LIMIT $2
                    """
                    
                    rows = await conn.fetch(query, event_types, limit)
                    
                    events = []
                    for row in rows:
                        event_data = json.loads(row['event_data']) if isinstance(row['event_data'], str) else row['event_data']
                        events.append(DomainEvent(
                            event_id=row['event_id'],
                            aggregate_id=row['aggregate_id'],
                            aggregate_type=row['aggregate_type'],
                            event_type=row['event_type'],
                            event_data=event_data,
                            event_version=row['event_version'],
                            occurred_at=row['occurred_at']
                        ))
                    
                    self._update_read_metrics(start_time)
                    return events
                    
        except Exception as e:
            logger.error(f"Failed to get events by type: {e}")
            return []
    
    async def get_aggregate_stream(self, aggregate_id: str) -> AsyncGenerator[DomainEvent, None]:
        """Get real-time event stream for aggregate"""
        if self.event_stream:
            async for event in self.event_stream.stream_events(aggregate_id=aggregate_id):
                yield event
    
    async def search_events(self, search_query: str, limit: int = 100) -> List[DomainEvent]:
        """Full-text search in events"""
        if self.connection_pool == "mock_pool":
            logger.info(f"Mock: Searched events with query: {search_query}")
            return []
        
        try:
            async with self._connection_semaphore:
                async with self.connection_pool.acquire() as conn:
                    query = f"""
                        SELECT event_id, aggregate_id, aggregate_type, event_type,
                               event_data, event_version, occurred_at,
                               ts_rank(to_tsvector('english', event_data::text), plainto_tsquery($1)) as rank
                        FROM {self.config.table_prefix}events
                        WHERE to_tsvector('english', event_data::text) @@ plainto_tsquery($1)
                        ORDER BY rank DESC, occurred_at DESC
                        LIMIT $2
                    """
                    
                    rows = await conn.fetch(query, search_query, limit)
                    
                    events = []
                    for row in rows:
                        event_data = json.loads(row['event_data']) if isinstance(row['event_data'], str) else row['event_data']
                        events.append(DomainEvent(
                            event_id=row['event_id'],
                            aggregate_id=row['aggregate_id'],
                            aggregate_type=row['aggregate_type'],
                            event_type=row['event_type'],
                            event_data=event_data,
                            event_version=row['event_version'],
                            occurred_at=row['occurred_at']
                        ))
                    
                    return events
                    
        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            return []
    
    async def _get_current_version(self, conn, aggregate_id: str) -> int:
        """Get current version for aggregate"""
        query = f"""
            SELECT COALESCE(MAX(event_version), 0) as version
            FROM {self.config.table_prefix}events
            WHERE aggregate_id = $1
        """
        result = await conn.fetchval(query, aggregate_id)
        return result or 0
    
    def _calculate_event_checksum(self, event: DomainEvent) -> str:
        """Calculate checksum for event integrity"""
        event_str = f"{event.event_id}{event.aggregate_id}{event.event_type}{json.dumps(event.event_data, sort_keys=True)}"
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def _update_write_metrics(self, start_time: datetime, event_count: int) -> None:
        """Update write metrics"""
        duration = (datetime.now() - start_time).total_seconds()
        self.metrics.total_queries += 1
        self.metrics.average_query_time = (
            (self.metrics.average_query_time + duration) / 2
        )
        if duration > 1.0:  # Slow query threshold
            self.metrics.slow_queries += 1
    
    def _update_read_metrics(self, start_time: datetime) -> None:
        """Update read metrics"""
        duration = (datetime.now() - start_time).total_seconds()
        self.metrics.total_queries += 1
        self.metrics.average_query_time = (
            (self.metrics.average_query_time + duration) / 2
        )
        if duration > 0.5:  # Slow query threshold for reads
            self.metrics.slow_queries += 1
    
    async def get_metrics(self) -> QueryMetrics:
        """Get current repository metrics"""
        if self.connection_pool and self.connection_pool != "mock_pool":
            try:
                pool_size = self.connection_pool.get_size()
                idle_size = self.connection_pool.get_idle_size()
                self.metrics.connection_pool_usage = (pool_size - idle_size) / pool_size
            except:
                self.metrics.connection_pool_usage = 0.0
        
        return self.metrics
    
    async def health_check(self) -> bool:
        """Check repository health"""
        if self.connection_pool == "mock_pool":
            return True
        
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.connection_pool and self.connection_pool != "mock_pool":
            await self.connection_pool.close()
        self._query_cache.clear()


class ConcurrencyError(Exception):
    """Raised when optimistic concurrency control fails"""
    pass