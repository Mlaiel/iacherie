"""🚀 MongoDB Analytics Store - IA Influencer Agent Platform
===========================================================
Module: events/event_store/mongodb_analytics_store.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MONGODB ANALYTICS EVENT STORE
High-performance MongoDB store for analytics, metrics, and business intelligence
optimized for Ainflue platform's analytical workloads.

Key Features:
- Optimized for Ainflue analytics patterns
- Sharded collections for massive scalability
- Real-time aggregation pipelines
- Time-series collections for metrics
- GridFS for large event payloads
- Change streams for real-time notifications
- Specialized indexes for analytics queries
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator
from decimal import Decimal
import json

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
    from pymongo import ASCENDING, DESCENDING, TEXT
    from pymongo.errors import PyMongoError
    from bson import ObjectId
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    # Create placeholder classes
    class AsyncIOMotorClient: pass
    class AsyncIOMotorCollection: pass
    class AsyncIOMotorDatabase: pass
    class PyMongoError(Exception): pass
    class ObjectId:
    """ObjectId: class implementation"""
        def __init__(self) -> None: pass
    ASCENDING = 1
    DESCENDING = -1
    TEXT = "text"

from ..core.base_event import BaseEvent
from .enterprise_store_interface import (
    IEventStoreBackend, EventQuery, StreamConfig, StoreResult, StorageBackendType
)

logger = logging.getLogger(__name__)

if not MOTOR_AVAILABLE:
    logger.warning("motor not available - install with: pip install motor")


class MongoDBAnalyticsStore(IEventStoreBackend):
    """
    MongoDB analytics store for Ainflue platform
    
    Optimized for:
    - User engagement analytics and metrics
    - Content performance tracking
    - Revenue analytics and reporting
    - Real-time dashboard data
    - Business intelligence aggregations
    - Time-series metrics collection
    """
    
    def __init__(self, connection_config -> None: Dict[str, Any]) -> None:
        if not MOTOR_AVAILABLE:
            raise ImportError("motor not available. Install with: pip install motor")
        
        self.config = connection_config
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._collections: Dict[str, AsyncIOMotorCollection] = {}
        self._is_initialized = False
        self._metrics = {
            'events_stored': 0,
            'total_latency': 0.0,
            'latency_samples': 0,
            'errors': 0,
            'aggregations_executed': 0
        }
        
        # Collection names for different event types
        self.collection_names = {
            'user_analytics': 'user_analytics_events',
            'content_analytics': 'content_analytics_events',
            'revenue_analytics': 'revenue_analytics_events',
            'engagement_metrics': 'engagement_metrics',
            'performance_metrics': 'performance_metrics',
            'collaboration_analytics': 'collaboration_analytics_events',
            'general_events': 'general_analytics_events'
        }
    
    async def initialize(self) -> None:
        """Initialize MongoDB connection and collections"""
        try:
            # Create MongoDB client
            connection_string = self._build_connection_string()
            self.client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.config.get('max_pool_size', 50),
                minPoolSize=self.config.get('min_pool_size', 10),
                maxIdleTimeMS=self.config.get('max_idle_time', 30000),
                serverSelectionTimeoutMS=self.config.get('server_selection_timeout', 5000)
            )
            
            # Get database
            self.database = self.client[self.config['database']]
            
            # Initialize collections
            await self._initialize_collections()
            
            # Create indexes
            await self._create_analytics_indexes()
            
            # Setup sharding if configured
            if self.config.get('enable_sharding', False):
                await self._setup_sharding()
            
            self._is_initialized = True
            logger.info("MongoDB Analytics Store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB analytics store: {e}")
            raise
    
    def _build_connection_string(self) -> str:
        """Build MongoDB connection string from config"""
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 27017)
        username = self.config.get('username')
        password = self.config.get('password')
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}"
        else:
            return f"mongodb://{host}:{port}"
    
    async def _initialize_collections(self) -> None:
        """Initialize specialized collections for analytics"""
        
        # Initialize regular collections
        for collection_type, collection_name in self.collection_names.items():
            self._collections[collection_type] = self.database[collection_name]
        
        # Create time-series collections for metrics
        try:
            await self.database.create_collection(
                "performance_time_series",
                timeseries={
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "minutes"
                }
            )
            self._collections['time_series'] = self.database["performance_time_series"]
            logger.info("Created time-series collection for performance metrics")
        except Exception as e:
            # Collection might already exist
            if "already exists" not in str(e):
                logger.warning(f"Could not create time-series collection: {e}")
            self._collections['time_series'] = self.database["performance_time_series"]
        
        # Create capped collection for real-time events
        try:
            await self.database.create_collection(
                "realtime_events",
                capped=True,
                size=100 * 1024 * 1024,  # 100MB
                max=10000  # Max 10k documents
            )
            self._collections['realtime'] = self.database["realtime_events"]
            logger.info("Created capped collection for real-time events")
        except Exception as e:
            if "already exists" not in str(e):
                logger.warning(f"Could not create capped collection: {e}")
            self._collections['realtime'] = self.database["realtime_events"]
    
    async def _create_analytics_indexes(self) -> None:
        """Create specialized indexes for analytics queries"""
        
        # User analytics indexes
        user_collection = self._collections['user_analytics']
        await user_collection.create_index([
            ("event_data.creator_id", ASCENDING),
            ("event_type", ASCENDING),
            ("occurred_at", DESCENDING)
        ])
        await user_collection.create_index([
            ("event_data.user_id", ASCENDING),
            ("occurred_at", DESCENDING)
        ])
        
        # Content analytics indexes
        content_collection = self._collections['content_analytics']
        await content_collection.create_index([
            ("event_data.content_id", ASCENDING),
            ("event_type", ASCENDING),
            ("occurred_at", DESCENDING)
        ])
        await content_collection.create_index([
            ("event_data.content_type", ASCENDING),
            ("event_data.engagement_metrics.views", DESCENDING)
        ])
        
        # Revenue analytics indexes
        revenue_collection = self._collections['revenue_analytics']
        await revenue_collection.create_index([
            ("event_data.creator_id", ASCENDING),
            ("event_data.revenue_amount", DESCENDING),
            ("occurred_at", DESCENDING)
        ])
        await revenue_collection.create_index([
            ("event_data.currency", ASCENDING),
            ("occurred_at", DESCENDING)
        ])
        
        # Engagement metrics indexes
        engagement_collection = self._collections['engagement_metrics']
        await engagement_collection.create_index([
            ("metadata.content_id", ASCENDING),
            ("timestamp", DESCENDING)
        ])
        await engagement_collection.create_index([
            ("metadata.creator_id", ASCENDING),
            ("engagement_score", DESCENDING)
        ])
        
        # Performance metrics indexes (time-series)
        if 'time_series' in self._collections:
            time_series_collection = self._collections['time_series']
            await time_series_collection.create_index([
                ("metadata.component", ASCENDING),
                ("timestamp", DESCENDING)
            ])
        
        # Collaboration analytics indexes
        collaboration_collection = self._collections['collaboration_analytics']
        await collaboration_collection.create_index([
            ("event_data.collaboration_id", ASCENDING),
            ("event_type", ASCENDING),
            ("occurred_at", DESCENDING)
        ])
        
        # Text search indexes
        await content_collection.create_index([
            ("event_data.title", TEXT),
            ("event_data.description", TEXT),
            ("event_data.tags", TEXT)
        ])
        
        logger.info("Created analytics indexes successfully")
    
    async def _setup_sharding(self) -> None:
        """Setup sharding for scalability"""
        try:
            # Enable sharding on database
            admin_db = self.client.admin
            await admin_db.command("enableSharding", self.config['database'])
            
            # Shard collections by creator_id for even distribution
            for collection_name in self.collection_names.values():
                try:
                    await admin_db.command(
                        "shardCollection",
                        f"{self.config['database']}.{collection_name}",
                        key={"event_data.creator_id": "hashed"}
                    )
                except Exception as e:
                    if "already sharded" not in str(e):
                        logger.warning(f"Could not shard collection {collection_name}: {e}")
            
            logger.info("Sharding setup completed")
            
        except Exception as e:
            logger.warning(f"Sharding setup failed: {e}")
    
    async def store_event(self, event: BaseEvent) -> StoreResult:
        """Store event in appropriate analytics collection"""
        start_time = datetime.utcnow()
        
        try:
            # Determine target collection based on event type
            collection = self._get_collection_for_event(event)
            
            # Prepare document
            document = self._prepare_analytics_document(event)
            
            # Insert document
            result = await collection.insert_one(document)
            
            # Also store in real-time collection for immediate access
            if self._is_realtime_event(event):
                await self._collections['realtime'].insert_one(document)
            
            # Store performance metrics if applicable
            if self._is_performance_event(event):
                await self._store_performance_metrics(event)
            
            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._metrics['events_stored'] += 1
            self._metrics['total_latency'] += latency
            self._metrics['latency_samples'] += 1
            
            return StoreResult(
                success=True,
                event_id=event.event_id,
                backends_used=[StorageBackendType.MONGODB],
                latency_ms=latency,
                metadata={
                    'collection': collection.name,
                    'document_id': str(result.inserted_id)
                }
            )
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to store analytics event {event.event_id}: {e}")
            return StoreResult(
                success=False,
                event_id=event.event_id,
                backends_used=[],
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                errors=[str(e)]
            )
    
    def _get_collection_for_event(self, event: BaseEvent) -> AsyncIOMotorCollection:
        """Determine optimal collection for event type"""
        
        event_type = event.event_type.lower()
        
        # User-related analytics
        if 'user' in event_type or 'creator' in event_type:
            return self._collections['user_analytics']
        
        # Content-related analytics
        elif 'content' in event_type or 'media' in event_type:
            return self._collections['content_analytics']
        
        # Revenue and monetization analytics
        elif 'revenue' in event_type or 'payment' in event_type or 'monetization' in event_type:
            return self._collections['revenue_analytics']
        
        # Engagement metrics
        elif 'engagement' in event_type or 'view' in event_type or 'like' in event_type:
            return self._collections['engagement_metrics']
        
        # Collaboration analytics
        elif 'collaboration' in event_type:
            return self._collections['collaboration_analytics']
        
        # Performance metrics
        elif 'performance' in event_type or 'metrics' in event_type:
            return self._collections['performance_metrics']
        
        # Default to general analytics
        else:
            return self._collections['general_events']
    
    def _prepare_analytics_document(self, event: BaseEvent) -> Dict[str, Any]:
        """Prepare optimized document for analytics storage"""
        
        document = {
            '_id': ObjectId(),
            'event_id': event.event_id,
            'event_type': event.event_type,
            'event_data': event.data or {},
            'occurred_at': event.timestamp,
            'created_at': datetime.utcnow(),
            'metadata': getattr(event, 'metadata', {}),
            'source': getattr(event, 'source', None),
            'correlation_id': getattr(event, 'correlation_id', None)
        }
        
        # Add analytics-specific fields
        if event.data:
            data = event.data
            
            # Extract analytics dimensions
            analytics_dimensions = {
                'creator_id': data.get('creator_id'),
                'content_id': data.get('content_id'),
                'content_type': data.get('content_type'),
                'user_id': data.get('user_id'),
                'platform': data.get('platform'),
                'session_id': data.get('session_id')
            }
            
            # Remove None values
            analytics_dimensions = {k: v for k, v in analytics_dimensions.items() if v is not None}
            document['analytics_dimensions'] = analytics_dimensions
            
            # Extract business metrics
            business_metrics = {}
            
            # Engagement metrics
            if 'views' in data or 'likes' in data or 'shares' in data:
                business_metrics.update({
                    'views': data.get('views', 0),
                    'likes': data.get('likes', 0),
                    'shares': data.get('shares', 0),
                    'comments': data.get('comments', 0),
                    'engagement_score': data.get('engagement_score', 0.0)
                })
            
            # Revenue metrics
            if 'revenue_amount' in data or 'amount' in data:
                amount = data.get('revenue_amount') or data.get('amount')
                if amount:
                    business_metrics.update({
                        'revenue_amount': float(amount) if isinstance(amount, Decimal) else amount,
                        'currency': data.get('currency'),
                        'revenue_source': data.get('source')
                    })
            
            # Performance metrics
            if 'processing_time' in data or 'duration' in data:
                business_metrics.update({
                    'processing_time': data.get('processing_time'),
                    'duration': data.get('duration'),
                    'performance_score': data.get('performance_score')
                })
            
            if business_metrics:
                document['business_metrics'] = business_metrics
        
        # Add time-based partitioning fields
        document['date_partition'] = event.timestamp.strftime('%Y-%m-%d')
        document['hour_partition'] = event.timestamp.hour
        document['day_of_week'] = event.timestamp.weekday()
        
        return document
    
    def _is_realtime_event(self, event: BaseEvent) -> bool:
        """Check if event should be stored in real-time collection"""
        realtime_types = [
            'content.viewed', 'content.liked', 'content.shared',
            'user.login', 'user.logout', 'collaboration.started',
            'performance.alert', 'system.error'
        ]
        return event.event_type in realtime_types
    
    def _is_performance_event(self, event: BaseEvent) -> bool:
        """Check if event contains performance metrics"""
        performance_patterns = ['performance', 'metrics', 'latency', 'throughput']
        return any(pattern in event.event_type.lower() for pattern in performance_patterns)
    
    async def _store_performance_metrics(self, event -> None: BaseEvent) -> None:
        """Store performance metrics in time-series collection"""
        if 'time_series' not in self._collections:
            return
        
        try:
            metrics_document = {
                'timestamp': event.timestamp,
                'metadata': {
                    'event_type': event.event_type,
                    'component': event.data.get('component', 'unknown'),
                    'source': getattr(event, 'source', 'unknown')
                }
            }
            
            # Extract numeric metrics
            if event.data:
                for key, value in event.data.items():
                    if isinstance(value, (int, float, Decimal)):
                        metrics_document[key] = float(value) if isinstance(value, Decimal) else value
            
            await self._collections['time_series'].insert_one(metrics_document)
            
        except Exception as e:
            logger.warning(f"Failed to store performance metrics: {e}")
    
    async def store_events_batch(self, events: List[BaseEvent]) -> List[StoreResult]:
        """Store multiple events in optimized batch operation"""
        start_time = datetime.utcnow()
        results = []
        
        if not events:
            return results
        
        try:
            # Group events by collection for batch insert
            collection_groups = {}
            for event in events:
                collection = self._get_collection_for_event(event)
                collection_name = collection.name
                
                if collection_name not in collection_groups:
                    collection_groups[collection_name] = {'collection': collection, 'documents': []}
                
                document = self._prepare_analytics_document(event)
                collection_groups[collection_name]['documents'].append(document)
            
            # Execute batch inserts
            for collection_name, group in collection_groups.items():
                try:
                    await group['collection'].insert_many(group['documents'])
                    
                    # Create success results for this group
                    for i, document in enumerate(group['documents']):
                        event_id = document['event_id']
                        results.append(StoreResult(
                            success=True,
                            event_id=event_id,
                            backends_used=[StorageBackendType.MONGODB],
                            latency_ms=0,  # Will be calculated below
                            metadata={
                                'collection': collection_name,
                                'batch_size': len(group['documents'])
                            }
                        ))
                        
                except Exception as e:
                    logger.error(f"Batch insert failed for collection {collection_name}: {e}")
                    
                    # Create error results for this group
                    for document in group['documents']:
                        event_id = document['event_id']
                        results.append(StoreResult(
                            success=False,
                            event_id=event_id,
                            backends_used=[],
                            latency_ms=0,
                            errors=[str(e)]
                        ))
            
            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            successful_events = sum(1 for r in results if r.success)
            
            self._metrics['events_stored'] += successful_events
            self._metrics['total_latency'] += latency
            self._metrics['latency_samples'] += 1
            
            # Update latency for all results
            avg_latency = latency / len(events) if events else 0
            for result in results:
                result.latency_ms = avg_latency
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Batch operation failed: {e}")
            
            # Create error results for all events
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
        """Retrieve events with analytics-optimized queries"""
        
        try:
            # Build MongoDB query
            mongo_query, sort_spec, limit_spec = self._build_mongo_query(query)
            
            # Determine which collections to search
            collections_to_search = self._get_collections_for_query(query)
            
            events = []
            for collection in collections_to_search:
                # Execute query
                cursor = collection.find(mongo_query)
                
                if sort_spec:
                    cursor = cursor.sort(sort_spec)
                
                if limit_spec:
                    cursor = cursor.limit(limit_spec)
                
                if query.offset:
                    cursor = cursor.skip(query.offset)
                
                # Convert documents to events
                async for document in cursor:
                    event = self._document_to_event(document)
                    events.append(event)
            
            # Sort combined results if needed
            if len(collections_to_search) > 1:
                events.sort(key=lambda e: e.timestamp, reverse=(query.order_direction == "DESC"))
            
            # Apply final limit if searching multiple collections
            if query.limit and len(collections_to_search) > 1:
                events = events[:query.limit]
            
            return events
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Failed to retrieve analytics events: {e}")
            raise
    
    def _build_mongo_query(self, query: EventQuery) -> tuple:
        """Build MongoDB query from EventQuery parameters"""
        
        mongo_query = {}
        
        # Add filters
        if query.aggregate_id:
            mongo_query['analytics_dimensions.aggregate_id'] = query.aggregate_id
        
        if query.event_types:
            mongo_query['event_type'] = {'$in': query.event_types}
        
        if query.creator_id:
            mongo_query['analytics_dimensions.creator_id'] = query.creator_id
        
        if query.content_type:
            mongo_query['analytics_dimensions.content_type'] = query.content_type
        
        # Time range filters
        time_filter = {}
        if query.start_time:
            time_filter['$gte'] = query.start_time
        if query.end_time:
            time_filter['$lte'] = query.end_time
        
        if time_filter:
            mongo_query['occurred_at'] = time_filter
        
        # Sort specification
        sort_direction = DESCENDING if query.order_direction == "DESC" else ASCENDING
        sort_spec = [(query.order_by, sort_direction)]
        
        return mongo_query, sort_spec, query.limit
    
    def _get_collections_for_query(self, query: EventQuery) -> List[AsyncIOMotorCollection]:
        """Determine which collections to search based on query"""
        
        # If specific event types are requested, route to appropriate collections
        if query.event_types:
            collections = set()
            for event_type in query.event_types:
                if 'user' in event_type or 'creator' in event_type:
                    collections.add(self._collections['user_analytics'])
                elif 'content' in event_type:
                    collections.add(self._collections['content_analytics'])
                elif 'revenue' in event_type or 'payment' in event_type:
                    collections.add(self._collections['revenue_analytics'])
                elif 'engagement' in event_type:
                    collections.add(self._collections['engagement_metrics'])
                elif 'collaboration' in event_type:
                    collections.add(self._collections['collaboration_analytics'])
                else:
                    collections.add(self._collections['general_events'])
            
            return list(collections)
        
        # Search all analytics collections
        return [
            self._collections['user_analytics'],
            self._collections['content_analytics'],
            self._collections['revenue_analytics'],
            self._collections['engagement_metrics'],
            self._collections['collaboration_analytics'],
            self._collections['general_events']
        ]
    
    def _document_to_event(self, document: Dict[str, Any]) -> BaseEvent:
        """Convert MongoDB document to BaseEvent"""
        
        event = BaseEvent(
            event_type=document['event_type'],
            data=document.get('event_data', {}),
            event_id=document['event_id'],
            timestamp=document['occurred_at'],
            metadata=document.get('metadata', {}),
            source=document.get('source')
        )
        
        return event
    
    async def stream_events(self, config: StreamConfig) -> AsyncIterator[BaseEvent]:
        """Stream events using MongoDB change streams"""
        
        try:
            # Use change streams for real-time events
            collection = self._collections['realtime']
            
            # Set up change stream pipeline
            pipeline = []
            if config.filter_criteria:
                pipeline.append({'$match': config.filter_criteria})
            
            async with collection.watch(pipeline) as stream:
                async for change in stream:
                    if change['operationType'] == 'insert':
                        document = change['fullDocument']
                        event = self._document_to_event(document)
                        yield event
                        
        except Exception as e:
            logger.error(f"Event streaming failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check MongoDB analytics store health"""
        try:
            if not self.client:
                return False
            
            # Test connection
            await self.client.admin.command('ismaster')
            
            # Test database access
            await self.database.command('ping')
            
            return True
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get analytics store performance metrics"""
        
        # Calculate derived metrics
        avg_latency = 0.0
        if self._metrics['latency_samples'] > 0:
            avg_latency = self._metrics['total_latency'] / self._metrics['latency_samples']
        
        # Get collection stats
        collection_stats = {}
        for collection_type, collection in self._collections.items():
            try:
                stats = await self.database.command('collStats', collection.name)
                collection_stats[collection_type] = {
                    'document_count': stats.get('count', 0),
                    'storage_size': stats.get('storageSize', 0),
                    'average_document_size': stats.get('avgObjSize', 0)
                }
            except Exception as e:
                logger.warning(f"Could not get stats for collection {collection_type}: {e}")
        
        return {
            'events_stored': self._metrics['events_stored'],
            'total_latency': self._metrics['total_latency'],
            'latency_samples': self._metrics['latency_samples'],
            'average_latency_ms': avg_latency,
            'errors': self._metrics['errors'],
            'aggregations_executed': self._metrics['aggregations_executed'],
            'error_rate': self._metrics['errors'] / max(self._metrics['events_stored'], 1),
            'collection_stats': collection_stats
        }
    
    async def execute_analytics_aggregation(self, pipeline: List[Dict[str, Any]], 
                                          collection_type: str = 'general_events') -> List[Dict[str, Any]]:
        """Execute analytics aggregation pipeline"""
        
        try:
            collection = self._collections[collection_type]
            results = []
            
            async for document in collection.aggregate(pipeline):
                results.append(document)
            
            self._metrics['aggregations_executed'] += 1
            return results
            
        except Exception as e:
            self._metrics['errors'] += 1
            logger.error(f"Analytics aggregation failed: {e}")
            raise
    
    async def get_engagement_metrics(self, creator_id: str, 
                                   start_date: datetime, 
                                   end_date: datetime) -> Dict[str, Any]:
        """Get engagement metrics for creator"""
        
        pipeline = [
            {
                '$match': {
                    'analytics_dimensions.creator_id': creator_id,
                    'occurred_at': {'$gte': start_date, '$lte': end_date},
                    'event_type': {'$in': ['content.viewed', 'content.liked', 'content.shared']}
                }
            },
            {
                '$group': {
                    '_id': '$analytics_dimensions.content_id',
                    'total_views': {'$sum': '$business_metrics.views'},
                    'total_likes': {'$sum': '$business_metrics.likes'},
                    'total_shares': {'$sum': '$business_metrics.shares'},
                    'avg_engagement_score': {'$avg': '$business_metrics.engagement_score'}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_content_pieces': {'$sum': 1},
                    'total_views': {'$sum': '$total_views'},
                    'total_likes': {'$sum': '$total_likes'},
                    'total_shares': {'$sum': '$total_shares'},
                    'avg_engagement_score': {'$avg': '$avg_engagement_score'}
                }
            }
        ]
        
        results = await self.execute_analytics_aggregation(pipeline, 'engagement_metrics')
        return results[0] if results else {}
    
    async def get_revenue_analytics(self, creator_id: str, 
                                  start_date: datetime, 
                                  end_date: datetime) -> Dict[str, Any]:
        """Get revenue analytics for creator"""
        
        pipeline = [
            {
                '$match': {
                    'analytics_dimensions.creator_id': creator_id,
                    'occurred_at': {'$gte': start_date, '$lte': end_date},
                    'event_type': {'$regex': 'revenue|payment'}
                }
            },
            {
                '$group': {
                    '_id': '$business_metrics.currency',
                    'total_revenue': {'$sum': '$business_metrics.revenue_amount'},
                    'transaction_count': {'$sum': 1},
                    'avg_transaction_amount': {'$avg': '$business_metrics.revenue_amount'}
                }
            }
        ]
        
        results = await self.execute_analytics_aggregation(pipeline, 'revenue_analytics')
        return results
    
    async def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._is_initialized = False
            logger.info("MongoDB Analytics Store closed")


# Export public APIs
__all__ = [
    'MongoDBAnalyticsStore'
]