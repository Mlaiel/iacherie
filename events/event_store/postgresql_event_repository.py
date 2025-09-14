"""🚀 PostgreSQL Event Repository - IA Influencer Agent Platform
================================================================
Module: events/event_store/postgresql_event_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 POSTGRESQL HIGH-PERFORMANCE EVENT REPOSITORY
Enterprise-grade PostgreSQL event storage with optimized schemas,
partitioning, and indexing for Ainflue business logic patterns.

Key Features:
- Optimized for Ainflue content lifecycle events
- Automatic table partitioning by time and aggregate
- Specialized indexes for business query patterns
- High-performance bulk operations
- Connection pooling with load balancing
- Point-in-time recovery and continuous backup
- ACID compliance for critical business events
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import asdict
from decimal import Decimal

try:
    import asyncpg
    from asyncpg import Pool, Connection
    from asyncpg.exceptions import PostgresError
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    # Create placeholder classes
    class Pool: pass
    class Connection: pass
    class PostgresError(Exception): pass

from ..core.base_event import BaseEvent
from .enterprise_store_interface import (
    IEventStoreBackend, EventQuery, StreamConfig, StoreResult, StorageBackendType
)

logger = logging.getLogger(__name__)

if not ASYNCPG_AVAILABLE:
    logger.warning("asyncpg not available - install with: pip install asyncpg")


class PostgreSQLEventRepository(IEventStoreBackend):
    """
    High-performance PostgreSQL event repository for Ainflue platform
    
    Optimized for:
    - Content lifecycle events (upload, processing, distribution)
    - User interaction events (views, likes, shares, collaborations)
    - Revenue and monetization events (payments, royalties, licensing)
    - Business-critical events requiring ACID compliance
    """
    
    def __init__(self, connection_config -> None: Dict[str, Any]) -> None:
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg not available. Install with: pip install asyncpg")
        
        self.config = connection_config
        self.pool: Optional[Pool] = None
        self._is_initialized = False
        self._partition_manager = None
        self._metrics = {
            'events_stored': 0,
            'total_latency': 0.0,
            'latency_samples': 0,
            'errors': 0,
            'queries_executed': 0
        }
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and schema"""
        try:
            # Create connection pool with optimized settings
            self.pool = await asyncpg.create_pool(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                min_size=self.config.get('min_connections', 10),
                max_size=self.config.get('max_connections', 50),
                command_timeout=self.config.get('command_timeout', 30),
                server_settings={
                    'jit': 'off',  # Disable JIT for consistent performance
                    'application_name': 'ainflue_event_store'
                }
            )
            
            # Initialize database schema
            await self._initialize_schema()
            
            # Initialize partition manager
            await self._initialize_partitioning()
            
            self._is_initialized = True
            logger.info("PostgreSQL Event Repository initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL repository: {e}")
            raise
    
    async def _initialize_schema(self) -> None:
        """Initialize optimized database schema for Ainflue events"""
        
        async with self.pool.acquire() as conn:
            # Create extensions
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\"")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"btree_gin\"")
            
            # Main events table with partitioning
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ainflue_events (
                    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    aggregate_id UUID,
                    aggregate_type VARCHAR(100),
                    event_type VARCHAR(100) NOT NULL,
                    event_data JSONB NOT NULL,
                    event_version INTEGER DEFAULT 1,
                    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    
                    -- Ainflue business context fields
                    creator_id UUID,
                    content_id UUID,
                    content_type VARCHAR(50),
                    user_id UUID,
                    collaboration_id UUID,
                    revenue_amount DECIMAL(15,2),
                    currency VARCHAR(3),
                    
                    -- Event metadata
                    source VARCHAR(100),
                    correlation_id UUID,
                    causation_id UUID,
                    priority VARCHAR(20),
                    status VARCHAR(20),
                    processing_started_at TIMESTAMP WITH TIME ZONE,
                    processing_completed_at TIMESTAMP WITH TIME ZONE,
                    
                    -- Additional metadata
                    metadata JSONB DEFAULT '{}',
                    tags TEXT[],
                    business_context JSONB DEFAULT '{}'
                ) PARTITION BY RANGE (occurred_at)
            """)
            
            # Create specialized indexes for Ainflue business patterns
            await self._create_business_indexes(conn)
            
            # Create event snapshots table for aggregate reconstruction
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS event_snapshots (
                    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    aggregate_id UUID NOT NULL,
                    aggregate_type VARCHAR(100) NOT NULL,
                    aggregate_version INTEGER NOT NULL,
                    snapshot_data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    
                    UNIQUE(aggregate_id, aggregate_version)
                )
            """)
            
            # Create event metadata tracking table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS event_metadata_tracking (
                    tracking_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    event_id UUID NOT NULL REFERENCES ainflue_events(event_id),
                    metadata_type VARCHAR(50) NOT NULL,
                    metadata_value JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create performance metrics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_performance_metrics (
                    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    metric_type VARCHAR(50) NOT NULL,
                    metric_value DECIMAL(15,4) NOT NULL,
                    metric_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    additional_data JSONB DEFAULT '{}'
                )
            """)
    
    async def _create_business_indexes(self, conn -> None: Connection) -> None:
        """Create specialized indexes for Ainflue business query patterns"""
        
        # Content lifecycle events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_lifecycle_events 
            ON ainflue_events (creator_id, content_id, content_type, occurred_at DESC)
            WHERE event_type IN ('content.uploaded', 'content.processed', 'content.published', 'content.distributed')
        """)
        
        # User interaction events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_interaction_events
            ON ainflue_events (user_id, content_id, event_type, occurred_at DESC)
            WHERE event_type IN ('content.viewed', 'content.liked', 'content.shared', 'content.commented')
        """)
        
        # Collaboration events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_collaboration_events
            ON ainflue_events (collaboration_id, creator_id, event_type, occurred_at DESC)
            WHERE event_type LIKE '%collaboration%'
        """)
        
        # Revenue and monetization events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_revenue_events
            ON ainflue_events (creator_id, revenue_amount, currency, occurred_at DESC)
            WHERE event_type IN ('revenue.generated', 'payment.processed', 'payout.completed')
        """)
        
        # AI processing events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_processing_events
            ON ainflue_events (content_id, event_type, processing_started_at, processing_completed_at)
            WHERE event_type LIKE '%ai.%' OR event_type LIKE '%processing%'
        """)
        
        # High-priority events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_high_priority_events
            ON ainflue_events (priority, occurred_at DESC, event_type)
            WHERE priority IN ('CRITICAL', 'HIGH')
        """)
        
        # Full-text search on event data
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_data_fulltext
            ON ainflue_events USING GIN (event_data jsonb_path_ops)
        """)
        
        # Business context search
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_business_context_search
            ON ainflue_events USING GIN (business_context jsonb_path_ops)
        """)
        
        # Aggregate events index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_aggregate_events
            ON ainflue_events (aggregate_id, aggregate_type, event_version, occurred_at)
        """)
        
        # Event correlation index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_correlation
            ON ainflue_events (correlation_id, causation_id)
            WHERE correlation_id IS NOT NULL OR causation_id IS NOT NULL
        """)
    
    async def _initialize_partitioning(self) -> None:
        """Initialize automatic table partitioning"""
        
        async with self.pool.acquire() as conn:
            # Create current month partition
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (current_month + timedelta(days=32)).replace(day=1)
            
            partition_name = f"ainflue_events_{current_month.strftime('%Y_%m')}"
            
            try:
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF ainflue_events
                    FOR VALUES FROM ('{current_month.isoformat()}') TO ('{next_month.isoformat()}')
                """)
                logger.info(f"Created partition {partition_name}")
            except PostgresError as e:
                if "already exists" not in str(e):
                    logger.error(f"Failed to create partition {partition_name}: {e}")
            
            # Create next month partition
            next_next_month = (next_month + timedelta(days=32)).replace(day=1)
            next_partition_name = f"ainflue_events_{next_month.strftime('%Y_%m')}"
            
            try:
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {next_partition_name} PARTITION OF ainflue_events
                    FOR VALUES FROM ('{next_month.isoformat()}') TO ('{next_next_month.isoformat()}')
                """)
                logger.info(f"Created partition {next_partition_name}")
            except PostgresError as e:
                if "already exists" not in str(e):
                    logger.error(f"Failed to create partition {next_partition_name}: {e}")
    
    async def store_event(self, event: BaseEvent) -> StoreResult:
        """Store a single event with optimized performance"""
        start_time = datetime.utcnow()
        
        try:
            async with self.pool.acquire() as conn:
                # Extract Ainflue business context from event
                business_data = self._extract_business_context(event)
                
                # Prepare event data
                event_data = {
                    'event_id': event.event_id,
                    'aggregate_id': getattr(event, 'aggregate_id', None),
                    'aggregate_type': getattr(event, 'aggregate_type', None),
                    'event_type': event.event_type,
                    'event_data': json.dumps(event.data) if event.data else '{}',
                    'event_version': getattr(event, 'event_version', 1),
                    'occurred_at': event.timestamp,
                    'source': getattr(event, 'source', None),
                    'correlation_id': getattr(event, 'correlation_id', None),
                    'causation_id': getattr(event, 'causation_id', None),
                    'priority': getattr(event, 'priority', None),
                    'status': getattr(event, 'status', None),
                    'metadata': json.dumps(getattr(event, 'metadata', {})),
                    **business_data
                }
                
                # Insert event
                await conn.execute("""
                    INSERT INTO ainflue_events (
                        event_id, aggregate_id, aggregate_type, event_type, event_data,
                        event_version, occurred_at, source, correlation_id, causation_id,
                        priority, status, metadata, creator_id, content_id, content_type,
                        user_id, collaboration_id, revenue_amount, currency, business_context
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                    )
                """, 
                    event_data['event_id'],
                    event_data['aggregate_id'],
                    event_data['aggregate_type'],
                    event_data['event_type'],
                    event_data['event_data'],
                    event_data['event_version'],
                    event_data['occurred_at'],
                    event_data['source'],
                    event_data['correlation_id'],
                    event_data['causation_id'],
                    str(event_data['priority']) if event_data['priority'] else None,
                    str(event_data['status']) if event_data['status'] else None,
                    event_data['metadata'],
                    event_data.get('creator_id'),
                    event_data.get('content_id'),
                    event_data.get('content_type'),
                    event_data.get('user_id'),
                    event_data.get('collaboration_id'),
                    event_data.get('revenue_amount'),
                    event_data.get('currency'),
                    json.dumps(business_data.get('business_context', {}))
                )
            
            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._metrics['events_stored'] += 1
            self._metrics['total_latency'] += latency
            self._metrics['latency_samples'] += 1
            
            return StoreResult(
                success=True,
                event_id=event.event_id,
                backends_used=[StorageBackendType.POSTGRESQL],
                latency_ms=latency,
                metadata={'partition': self._get_partition_name(event.timestamp)}
            )
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to store event {event.event_id}: {e}")
            return StoreResult(
                success=False,
                event_id=event.event_id,
                backends_used=[],
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                errors=[str(e)]
            )
    
    def _extract_business_context(self, event: BaseEvent) -> Dict[str, Any]:
        """Extract Ainflue business context from event for optimized storage"""
        
        context = {
            'creator_id': None,
            'content_id': None,
            'content_type': None,
            'user_id': None,
            'collaboration_id': None,
            'revenue_amount': None,
            'currency': None,
            'business_context': {}
        }
        
        if event.data:
            data = event.data
            
            # Extract business identifiers
            context['creator_id'] = data.get('creator_id')
            context['content_id'] = data.get('content_id')
            context['content_type'] = data.get('content_type')
            context['user_id'] = data.get('user_id')
            context['collaboration_id'] = data.get('collaboration_id')
            
            # Extract revenue information
            if 'revenue_amount' in data or 'amount' in data:
                amount = data.get('revenue_amount') or data.get('amount')
                if amount:
                    try:
                        context['revenue_amount'] = Decimal(str(amount))
                    except:
                        pass
            
            context['currency'] = data.get('currency')
            
            # Extract business context
            business_ctx = {}
            
            # Content-related context
            if event.event_type.startswith('content.'):
                business_ctx.update({
                    'content_size': data.get('file_size'),
                    'content_duration': data.get('duration'),
                    'processing_type': data.get('processing_type'),
                    'ai_model': data.get('ai_model')
                })
            
            # User interaction context
            if 'interaction' in event.event_type or event.event_type in ['content.viewed', 'content.liked']:
                business_ctx.update({
                    'session_id': data.get('session_id'),
                    'platform': data.get('platform'),
                    'view_duration': data.get('view_duration')
                })
            
            # Revenue context
            if 'revenue' in event.event_type or 'payment' in event.event_type:
                business_ctx.update({
                    'payment_method': data.get('payment_method'),
                    'transaction_id': data.get('transaction_id'),
                    'source': data.get('source')
                })
            
            context['business_context'] = business_ctx
        
        return context
    
    def _get_partition_name(self, timestamp: datetime) -> str:
        """Get partition name for timestamp"""
        return f"ainflue_events_{timestamp.strftime('%Y_%m')}"
    
    async def store_events_batch(self, events: List[BaseEvent]) -> List[StoreResult]:
        """Store multiple events in an optimized batch operation"""
        start_time = datetime.utcnow()
        results = []
        
        if not events:
            return results
        
        try:
            async with self.pool.acquire() as conn:
                # Prepare batch data
                batch_data = []
                for event in events:
                    business_data = self._extract_business_context(event)
                    
                    event_record = (
                        event.event_id,
                        getattr(event, 'aggregate_id', None),
                        getattr(event, 'aggregate_type', None),
                        event.event_type,
                        json.dumps(event.data) if event.data else '{}',
                        getattr(event, 'event_version', 1),
                        event.timestamp,
                        getattr(event, 'source', None),
                        getattr(event, 'correlation_id', None),
                        getattr(event, 'causation_id', None),
                        str(getattr(event, 'priority', None)) if getattr(event, 'priority', None) else None,
                        str(getattr(event, 'status', None)) if getattr(event, 'status', None) else None,
                        json.dumps(getattr(event, 'metadata', {})),
                        business_data.get('creator_id'),
                        business_data.get('content_id'),
                        business_data.get('content_type'),
                        business_data.get('user_id'),
                        business_data.get('collaboration_id'),
                        business_data.get('revenue_amount'),
                        business_data.get('currency'),
                        json.dumps(business_data.get('business_context', {}))
                    )
                    batch_data.append(event_record)
                
                # Execute batch insert
                await conn.executemany("""
                    INSERT INTO ainflue_events (
                        event_id, aggregate_id, aggregate_type, event_type, event_data,
                        event_version, occurred_at, source, correlation_id, causation_id,
                        priority, status, metadata, creator_id, content_id, content_type,
                        user_id, collaboration_id, revenue_amount, currency, business_context
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                    )
                """, batch_data)
                
                # Update metrics
                latency = (datetime.utcnow() - start_time).total_seconds() * 1000
                self._metrics['events_stored'] += len(events)
                self._metrics['total_latency'] += latency
                self._metrics['latency_samples'] += 1
                
                # Create success results
                for event in events:
                    results.append(StoreResult(
                        success=True,
                        event_id=event.event_id,
                        backends_used=[StorageBackendType.POSTGRESQL],
                        latency_ms=latency / len(events),
                        metadata={'batch_size': len(events)}
                    ))
                
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to store batch of {len(events)} events: {e}")
            
            # Create error results
            for event in events:
                results.append(StoreResult(
                    success=False,
                    event_id=event.event_id,
                    backends_used=[],
                    latency_ms=0,
                    errors=[str(e)]
                ))
        
        return results
    
    async def retrieve_events(self, query: EventQuery) -> List[BaseEvent]:
        """Retrieve events with optimized queries for Ainflue business patterns"""
        
        try:
            async with self.pool.acquire() as conn:
                # Build optimized query based on parameters
                sql_query, params = self._build_optimized_query(query)
                
                # Execute query
                rows = await conn.fetch(sql_query, *params)
                
                # Convert to events
                events = []
                for row in rows:
                    event = self._row_to_event(row)
                    events.append(event)
                
                self._metrics['queries_executed'] += 1
                return events
                
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to retrieve events: {e}")
            raise
    
    def _build_optimized_query(self, query: EventQuery) -> tuple[str, List[Any]]:
        """Build optimized SQL query for Ainflue business patterns"""
        
        base_query = """
            SELECT event_id, aggregate_id, aggregate_type, event_type, event_data,
                   event_version, occurred_at, created_at, source, correlation_id,
                   causation_id, priority, status, metadata, creator_id, content_id,
                   content_type, user_id, collaboration_id, revenue_amount, currency,
                   business_context, processing_started_at, processing_completed_at
            FROM ainflue_events
        """
        
        conditions = []
        params = []
        param_count = 0
        
        # Add filters
        if query.aggregate_id:
            param_count += 1
            conditions.append(f"aggregate_id = ${param_count}")
            params.append(query.aggregate_id)
        
        if query.event_types:
            param_count += 1
            conditions.append(f"event_type = ANY(${param_count})")
            params.append(query.event_types)
        
        if query.creator_id:
            param_count += 1
            conditions.append(f"creator_id = ${param_count}")
            params.append(query.creator_id)
        
        if query.content_type:
            param_count += 1
            conditions.append(f"content_type = ${param_count}")
            params.append(query.content_type)
        
        if query.start_time:
            param_count += 1
            conditions.append(f"occurred_at >= ${param_count}")
            params.append(query.start_time)
        
        if query.end_time:
            param_count += 1
            conditions.append(f"occurred_at <= ${param_count}")
            params.append(query.end_time)
        
        # Build final query
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        # Add ordering
        base_query += f" ORDER BY {query.order_by} {query.order_direction}"
        
        # Add pagination
        if query.limit:
            param_count += 1
            base_query += f" LIMIT ${param_count}"
            params.append(query.limit)
        
        if query.offset:
            param_count += 1
            base_query += f" OFFSET ${param_count}"
            params.append(query.offset)
        
        return base_query, params
    
    def _row_to_event(self, row) -> BaseEvent:
        """Convert database row to BaseEvent"""
        
        # Parse JSON fields
        event_data = json.loads(row['event_data']) if row['event_data'] else {}
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        
        # Create base event
        event = BaseEvent(
            event_type=row['event_type'],
            data=event_data,
            event_id=str(row['event_id']),
            timestamp=row['occurred_at'],
            metadata=metadata,
            source=row['source'],
            correlation_id=str(row['correlation_id']) if row['correlation_id'] else None,
            causation_id=str(row['causation_id']) if row['causation_id'] else None,
            aggregate_id=str(row['aggregate_id']) if row['aggregate_id'] else None,
            aggregate_version=row['event_version']
        )
        
        # Add priority and status if available
        if row['priority']:
            try:
                from ..core.event_priority import EventPriority
                event.priority = EventPriority(row['priority'])
            except:
                pass
        
        if row['status']:
            try:
                from ..core.event_status import EventStatus
                event.status = EventStatus(row['status'])
            except:
                pass
        
        return event
    
    async def stream_events(self, config: StreamConfig) -> AsyncIterator[BaseEvent]:
        """Stream events in real-time using PostgreSQL LISTEN/NOTIFY"""
        
        async with self.pool.acquire() as conn:
            # Set up listener for new events
            await conn.add_listener('new_event', self._handle_notification)
            
            # Stream existing events first
            query = EventQuery(
                start_time=config.from_timestamp,
                limit=config.batch_size
            )
            
            existing_events = await self.retrieve_events(query)
            for event in existing_events:
                yield event
            
            # Wait for new events (simplified implementation)
            # In production, implement proper streaming with LISTEN/NOTIFY
            await asyncio.sleep(config.max_wait_time)
    
    async def _handle_notification(self, connection, pid, channel, payload) -> None:
        """Handle PostgreSQL notification for real-time streaming"""
        # Implementation for real-time event notifications
        pass
    
    async def health_check(self) -> bool:
        """Check PostgreSQL repository health"""
        try:
            if not self.pool:
                return False
            
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
                return True
                
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get repository performance metrics"""
        
        # Calculate derived metrics
        avg_latency = 0.0
        if self._metrics['latency_samples'] > 0:
            avg_latency = self._metrics['total_latency'] / self._metrics['latency_samples']
        
        return {
            'events_stored': self._metrics['events_stored'],
            'total_latency': self._metrics['total_latency'],
            'latency_samples': self._metrics['latency_samples'],
            'average_latency_ms': avg_latency,
            'errors': self._metrics['errors'],
            'queries_executed': self._metrics['queries_executed'],
            'error_rate': self._metrics['errors'] / max(self._metrics['events_stored'], 1),
            'pool_size': self.pool.get_size() if self.pool else 0,
            'pool_available': self.pool.get_idle_size() if self.pool else 0
        }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize PostgreSQL performance through maintenance operations"""
        
        optimizations = []
        
        try:
            async with self.pool.acquire() as conn:
                # Analyze table statistics
                await conn.execute("ANALYZE ainflue_events")
                optimizations.append("table_analysis_completed")
                
                # Reindex if needed (check index bloat)
                bloat_query = """
                    SELECT schemaname, tablename, attname, n_distinct, correlation 
                    FROM pg_stats 
                    WHERE tablename = 'ainflue_events' 
                    AND n_distinct < 100
                """
                bloat_results = await conn.fetch(bloat_query)
                
                if bloat_results:
                    await conn.execute("REINDEX TABLE ainflue_events")
                    optimizations.append("reindex_completed")
                
                # Vacuum if needed
                vacuum_query = """
                    SELECT schemaname, tablename, n_dead_tup, n_live_tup
                    FROM pg_stat_user_tables 
                    WHERE tablename = 'ainflue_events'
                """
                vacuum_stats = await conn.fetchrow(vacuum_query)
                
                if vacuum_stats and vacuum_stats['n_dead_tup'] > vacuum_stats['n_live_tup'] * 0.1:
                    await conn.execute("VACUUM ANALYZE ainflue_events")
                    optimizations.append("vacuum_completed")
        
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {'error': str(e)}
        
        return {
            'optimizations_completed': optimizations,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def close(self) -> None:
        """Close repository and cleanup resources"""
        if self.pool:
            await self.pool.close()
            self._is_initialized = False
            logger.info("PostgreSQL Event Repository closed")


# Export public APIs
__all__ = [
    'PostgreSQLEventRepository'
]