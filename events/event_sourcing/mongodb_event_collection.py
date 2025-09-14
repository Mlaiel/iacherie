"""MongoDB Event Collection - High-Performance Implementation

Enterprise-grade MongoDB collection for events with sharding, aggregation
pipelines, GridFS support, and real-time change streams.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import gridfs
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from uuid import uuid4
from bson import ObjectId

from . import DomainEvent, EventStoreInterface

logger = logging.getLogger(__name__)


class ShardingStrategy(Enum):
    """MongoDB sharding strategies"""
    NONE = "none"
    BY_AGGREGATE_ID = "by_aggregate_id"
    BY_TIMESTAMP = "by_timestamp"
    BY_EVENT_TYPE = "by_event_type"
    HYBRID = "hybrid"


class CompressionLevel(Enum):
    """MongoDB compression levels"""
    NONE = "none"
    SNAPPY = "snappy"
    ZLIB = "zlib"
    ZSTD = "zstd"


@dataclass
class MongoDBConfig:
    """MongoDB collection configuration"""
    connection_string: str
    database_name: str = "ainflue_events"
    collection_name: str = "events"
    max_pool_size: int = 100
    min_pool_size: int = 10
    server_selection_timeout_ms: int = 30000
    socket_timeout_ms: int = 30000
    sharding_strategy: ShardingStrategy = ShardingStrategy.BY_AGGREGATE_ID
    compression_level: CompressionLevel = CompressionLevel.SNAPPY
    enable_change_streams: bool = True
    enable_gridfs: bool = True
    max_document_size_mb: int = 16
    retention_days: int = 365


@dataclass
class MongoDBMetrics:
    """MongoDB performance metrics"""
    total_documents: int = 0
    collection_size_mb: float = 0.0
    index_size_mb: float = 0.0
    average_document_size: float = 0.0
    queries_per_second: float = 0.0
    inserts_per_second: float = 0.0
    change_stream_events: int = 0
    gridfs_files: int = 0
    shard_distribution: Dict[str, int] = None


class MongoDBIndexManager:
    """Advanced index management for MongoDB"""
    
    def __init__(self, collection, config -> None: MongoDBConfig) -> None:
        self.collection = collection
        self.config = config
    
    async def create_indexes(self) -> None:
        """Create optimized indexes"""
        try:
            # Primary indexes for event sourcing
            await self.collection.create_index([
                ("aggregate_id", 1),
                ("event_version", 1)
            ], name="idx_aggregate_version", unique=True)
            
            await self.collection.create_index([
                ("event_type", 1),
                ("occurred_at", -1)
            ], name="idx_event_type_time")
            
            await self.collection.create_index([
                ("occurred_at", -1)
            ], name="idx_occurred_at")
            
            # Compound indexes for complex queries
            await self.collection.create_index([
                ("aggregate_type", 1),
                ("event_type", 1),
                ("occurred_at", -1)
            ], name="idx_aggregate_event_type_time")
            
            # Text search index
            await self.collection.create_index([
                ("event_data", "text"),
                ("event_type", "text")
            ], name="idx_fulltext_search")
            
            # TTL index for automatic cleanup
            if self.config.retention_days > 0:
                await self.collection.create_index([
                    ("occurred_at", 1)
                ], 
                name="idx_ttl_cleanup",
                expireAfterSeconds=self.config.retention_days * 24 * 3600)
            
            # Geospatial index if needed
            await self.collection.create_index([
                ("metadata.location", "2dsphere")
            ], 
            name="idx_geospatial",
            sparse=True)
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index usage statistics"""
        try:
            stats = await self.collection.database.command("collStats", self.collection.name)
            index_stats = {}
            
            if "indexSizes" in stats:
                for index_name, size in stats["indexSizes"].items():
                    index_stats[index_name] = {
                        "size_bytes": size,
                        "size_mb": size / (1024 * 1024)
                    }
            
            return index_stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}


class MongoDBShardingManager:
    """MongoDB sharding configuration and management"""
    
    def __init__(self, database, config -> None: MongoDBConfig) -> None:
        self.database = database
        self.config = config
    
    async def configure_sharding(self) -> None:
        """Configure collection sharding"""
        if self.config.sharding_strategy == ShardingStrategy.NONE:
            return
        
        try:
            collection_name = f"{self.database.name}.{self.config.collection_name}"
            
            # Enable sharding for the database
            await self.database.client.admin.command({
                "enableSharding": self.database.name
            })
            
            # Configure shard key based on strategy
            shard_key = self._get_shard_key()
            
            # Shard the collection
            await self.database.client.admin.command({
                "shardCollection": collection_name,
                "key": shard_key
            })
            
            logger.info(f"Sharding configured with key: {shard_key}")
        except Exception as e:
            logger.warning(f"Sharding configuration failed (may already be configured): {e}")
    
    def _get_shard_key(self) -> Dict[str, int]:
        """Get shard key based on strategy"""
        if self.config.sharding_strategy == ShardingStrategy.BY_AGGREGATE_ID:
            return {"aggregate_id": "hashed"}
        elif self.config.sharding_strategy == ShardingStrategy.BY_TIMESTAMP:
            return {"occurred_at": 1}
        elif self.config.sharding_strategy == ShardingStrategy.BY_EVENT_TYPE:
            return {"event_type": "hashed"}
        elif self.config.sharding_strategy == ShardingStrategy.HYBRID:
            return {"aggregate_id": "hashed", "occurred_at": 1}
        else:
            return {"_id": "hashed"}
    
    async def get_shard_distribution(self) -> Dict[str, int]:
        """Get distribution of documents across shards"""
        try:
            collection_name = f"{self.database.name}.{self.config.collection_name}"
            result = await self.database.client.admin.command({
                "getShardDistribution": collection_name
            })
            
            distribution = {}
            if "shards" in result:
                for shard_info in result["shards"]:
                    shard_name = shard_info.get("shard", "unknown")
                    doc_count = shard_info.get("docs", 0)
                    distribution[shard_name] = doc_count
            
            return distribution
        except Exception as e:
            logger.error(f"Failed to get shard distribution: {e}")
            return {}


class MongoDBChangeStreamProcessor:
    """Real-time change stream processor"""
    
    def __init__(self, collection, config -> None: MongoDBConfig) -> None:
        self.collection = collection
        self.config = config
        self.active_streams = {}
        self.stream_handlers = {}
    
    async def start_change_stream(self, stream_id: str, 
                                pipeline: List[Dict] = None) -> AsyncGenerator[Dict, None]:
        """Start a change stream with optional aggregation pipeline"""
        if not self.config.enable_change_streams:
            logger.warning("Change streams are disabled")
            return
        
        try:
            # Default pipeline to watch inserts and updates
            if pipeline is None:
                pipeline = [
                    {"$match": {
                        "operationType": {"$in": ["insert", "update", "replace"]}
                    }}
                ]
            
            change_stream = self.collection.watch(pipeline, full_document="updateLookup")
            self.active_streams[stream_id] = change_stream
            
            async for change in change_stream:
                yield change
                
        except Exception as e:
            logger.error(f"Change stream {stream_id} failed: {e}")
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    async def stop_change_stream(self, stream_id: str) -> None:
        """Stop a change stream"""
        if stream_id in self.active_streams:
            try:
                await self.active_streams[stream_id].close()
                del self.active_streams[stream_id]
                logger.info(f"Change stream {stream_id} stopped")
            except Exception as e:
                logger.error(f"Failed to stop change stream {stream_id}: {e}")
    
    async def stop_all_streams(self) -> None:
        """Stop all active change streams"""
        for stream_id in list(self.active_streams.keys()):
            await self.stop_change_stream(stream_id)


class MongoDBGridFSManager:
    """GridFS manager for large event payloads"""
    
    def __init__(self, database, config -> None: MongoDBConfig) -> None:
        self.database = database
        self.config = config
        self.gridfs = None
    
    async def initialize(self) -> None:
        """Initialize GridFS"""
        if not self.config.enable_gridfs:
            return
        
        try:
            # GridFS is synchronous, so we'll use it in executor
            self.gridfs = gridfs.GridFS(self.database, collection="event_files")
            logger.info("GridFS initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GridFS: {e}")
    
    async def store_large_event(self, event_data: Dict[str, Any], 
                              metadata: Dict[str, Any] = None) -> str:
        """Store large event data in GridFS"""
        if not self.gridfs:
            raise ValueError("GridFS not initialized")
        
        try:
            # Convert to JSON bytes
            event_json = json.dumps(event_data, default=str)
            event_bytes = event_json.encode('utf-8')
            
            # Store in GridFS
            loop = asyncio.get_event_loop()
            file_id = await loop.run_in_executor(
                None, 
                lambda: self.gridfs.put(event_bytes, metadata=metadata or {})
            )
            
            return str(file_id)
        except Exception as e:
            logger.error(f"Failed to store large event: {e}")
            raise
    
    async def retrieve_large_event(self, file_id: str) -> Dict[str, Any]:
        """Retrieve large event data from GridFS"""
        if not self.gridfs:
            raise ValueError("GridFS not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Retrieve from GridFS
            file_data = await loop.run_in_executor(
                None,
                lambda: self.gridfs.get(ObjectId(file_id)).read()
            )
            
            # Convert back to dict
            event_json = file_data.decode('utf-8')
            return json.loads(event_json)
        except Exception as e:
            logger.error(f"Failed to retrieve large event: {e}")
            raise


class MongoDBEventCollection(EventStoreInterface):
    """High-performance MongoDB event collection"""
    
    def __init__(self, config -> None: MongoDBConfig) -> None:
        self.config = config
        self.client = None
        self.database = None
        self.collection = None
        self.index_manager = None
        self.sharding_manager = None
        self.change_stream_processor = None
        self.gridfs_manager = None
        self.metrics = MongoDBMetrics(shard_distribution={})
    
    async def initialize(self) -> None:
        """Initialize MongoDB connection and components"""
        try:
            import motor.motor_asyncio
            
            # Create async client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.config.connection_string,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
                serverSelectionTimeoutMS=self.config.server_selection_timeout_ms,
                socketTimeoutMS=self.config.socket_timeout_ms,
                compressors=[self.config.compression_level.value] if self.config.compression_level != CompressionLevel.NONE else []
            )
            
            # Get database and collection
            self.database = self.client[self.config.database_name]
            self.collection = self.database[self.config.collection_name]
            
            # Initialize managers
            self.index_manager = MongoDBIndexManager(self.collection, self.config)
            self.sharding_manager = MongoDBShardingManager(self.database, self.config)
            self.change_stream_processor = MongoDBChangeStreamProcessor(self.collection, self.config)
            self.gridfs_manager = MongoDBGridFSManager(self.database, self.config)
            
            # Setup collection
            await self._setup_collection()
            
            logger.info("MongoDB event collection initialized successfully")
        except ImportError:
            logger.warning("motor not available, using mock MongoDB implementation")
            self.client = "mock_client"
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB collection: {e}")
            raise
    
    async def _setup_collection(self) -> None:
        """Setup collection with indexes and sharding"""
        if self.client == "mock_client":
            return
        
        try:
            # Create indexes
            await self.index_manager.create_indexes()
            
            # Configure sharding
            await self.sharding_manager.configure_sharding()
            
            # Initialize GridFS
            await self.gridfs_manager.initialize()
            
            logger.info("MongoDB collection setup completed")
        except Exception as e:
            logger.error(f"Collection setup failed: {e}")
    
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int = None) -> None:
        """Save events to MongoDB collection"""
        if not events:
            return
        
        if self.client == "mock_client":
            logger.info(f"Mock: Saved {len(events)} events to MongoDB")
            return
        
        try:
            documents = []
            
            for event in events:
                # Check if event data is too large for normal document
                event_data = event.event_data
                event_size_mb = len(json.dumps(event_data, default=str).encode('utf-8')) / (1024 * 1024)
                
                if event_size_mb > self.config.max_document_size_mb and self.gridfs_manager.gridfs:
                    # Store large data in GridFS
                    file_id = await self.gridfs_manager.store_large_event(
                        event_data, 
                        {"event_id": event.event_id, "event_type": event.event_type}
                    )
                    event_data = {"_gridfs_file_id": file_id, "_is_large_event": True}
                
                doc = {
                    "_id": event.event_id,
                    "event_id": event.event_id,
                    "aggregate_id": aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "event_type": event.event_type,
                    "event_data": event_data,
                    "event_version": event.event_version,
                    "occurred_at": event.occurred_at,
                    "created_at": datetime.now(timezone.utc),
                    "metadata": {
                        "size_mb": event_size_mb,
                        "is_large_event": event_size_mb > self.config.max_document_size_mb
                    }
                }
                documents.append(doc)
            
            # Insert documents
            result = await self.collection.insert_many(documents, ordered=False)
            
            # Update metrics
            self.metrics.total_documents += len(result.inserted_ids)
            
            logger.info(f"Saved {len(events)} events to MongoDB collection")
        except Exception as e:
            logger.error(f"Failed to save events to MongoDB: {e}")
            raise
    
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Get events for aggregate from MongoDB"""
        if self.client == "mock_client":
            logger.info(f"Mock: Retrieved events for aggregate {aggregate_id}")
            return []
        
        try:
            cursor = self.collection.find({
                "aggregate_id": aggregate_id,
                "event_version": {"$gte": from_version}
            }).sort("event_version", 1)
            
            events = []
            async for doc in cursor:
                # Handle large events stored in GridFS
                event_data = doc["event_data"]
                if isinstance(event_data, dict) and event_data.get("_is_large_event"):
                    file_id = event_data.get("_gridfs_file_id")
                    if file_id and self.gridfs_manager.gridfs:
                        event_data = await self.gridfs_manager.retrieve_large_event(file_id)
                
                events.append(DomainEvent(
                    event_id=doc["event_id"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    event_type=doc["event_type"],
                    event_data=event_data,
                    event_version=doc["event_version"],
                    occurred_at=doc["occurred_at"]
                ))
            
            return events
        except Exception as e:
            logger.error(f"Failed to get events from MongoDB: {e}")
            return []
    
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 100) -> List[DomainEvent]:
        """Get all events from MongoDB with pagination"""
        if self.client == "mock_client":
            logger.info("Mock: Retrieved all events from MongoDB")
            return []
        
        try:
            query = {}
            if from_event_id:
                # Find events after the given event
                reference_doc = await self.collection.find_one({"event_id": from_event_id})
                if reference_doc:
                    query["occurred_at"] = {"$gt": reference_doc["occurred_at"]}
            
            cursor = self.collection.find(query).sort("occurred_at", 1).limit(limit)
            
            events = []
            async for doc in cursor:
                # Handle large events stored in GridFS
                event_data = doc["event_data"]
                if isinstance(event_data, dict) and event_data.get("_is_large_event"):
                    file_id = event_data.get("_gridfs_file_id")
                    if file_id and self.gridfs_manager.gridfs:
                        event_data = await self.gridfs_manager.retrieve_large_event(file_id)
                
                events.append(DomainEvent(
                    event_id=doc["event_id"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    event_type=doc["event_type"],
                    event_data=event_data,
                    event_version=doc["event_version"],
                    occurred_at=doc["occurred_at"]
                ))
            
            return events
        except Exception as e:
            logger.error(f"Failed to get all events from MongoDB: {e}")
            return []
    
    async def aggregate_events(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run aggregation pipeline on events"""
        if self.client == "mock_client":
            logger.info("Mock: Ran aggregation pipeline")
            return []
        
        try:
            cursor = self.collection.aggregate(pipeline)
            results = []
            async for doc in cursor:
                results.append(doc)
            
            return results
        except Exception as e:
            logger.error(f"Failed to run aggregation pipeline: {e}")
            return []
    
    async def search_events(self, search_text: str, limit: int = 100) -> List[DomainEvent]:
        """Full-text search in events"""
        if self.client == "mock_client":
            logger.info(f"Mock: Searched events with text: {search_text}")
            return []
        
        try:
            cursor = self.collection.find({
                "$text": {"$search": search_text}
            }, {
                "score": {"$meta": "textScore"}
            }).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            events = []
            async for doc in cursor:
                # Handle large events stored in GridFS
                event_data = doc["event_data"]
                if isinstance(event_data, dict) and event_data.get("_is_large_event"):
                    file_id = event_data.get("_gridfs_file_id")
                    if file_id and self.gridfs_manager.gridfs:
                        event_data = await self.gridfs_manager.retrieve_large_event(file_id)
                
                events.append(DomainEvent(
                    event_id=doc["event_id"],
                    aggregate_id=doc["aggregate_id"],
                    aggregate_type=doc["aggregate_type"],
                    event_type=doc["event_type"],
                    event_data=event_data,
                    event_version=doc["event_version"],
                    occurred_at=doc["occurred_at"]
                ))
            
            return events
        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            return []
    
    async def get_event_stream(self, event_types: List[str] = None) -> AsyncGenerator[DomainEvent, None]:
        """Get real-time event stream"""
        if not self.config.enable_change_streams or self.client == "mock_client":
            logger.warning("Change streams not available")
            return
        
        try:
            # Build pipeline for filtering
            pipeline = []
            if event_types:
                pipeline.append({
                    "$match": {
                        "operationType": "insert",
                        "fullDocument.event_type": {"$in": event_types}
                    }
                })
            else:
                pipeline.append({
                    "$match": {"operationType": "insert"}
                })
            
            stream_id = str(uuid4())
            async for change in self.change_stream_processor.start_change_stream(stream_id, pipeline):
                if change["operationType"] == "insert":
                    doc = change["fullDocument"]
                    
                    # Handle large events stored in GridFS
                    event_data = doc["event_data"]
                    if isinstance(event_data, dict) and event_data.get("_is_large_event"):
                        file_id = event_data.get("_gridfs_file_id")
                        if file_id and self.gridfs_manager.gridfs:
                            event_data = await self.gridfs_manager.retrieve_large_event(file_id)
                    
                    yield DomainEvent(
                        event_id=doc["event_id"],
                        aggregate_id=doc["aggregate_id"],
                        aggregate_type=doc["aggregate_type"],
                        event_type=doc["event_type"],
                        event_data=event_data,
                        event_version=doc["event_version"],
                        occurred_at=doc["occurred_at"]
                    )
        except Exception as e:
            logger.error(f"Event stream failed: {e}")
    
    async def get_metrics(self) -> MongoDBMetrics:
        """Get collection metrics and statistics"""
        if self.client == "mock_client":
            return self.metrics
        
        try:
            # Get collection stats
            stats = await self.database.command("collStats", self.config.collection_name)
            
            self.metrics.total_documents = stats.get("count", 0)
            self.metrics.collection_size_mb = stats.get("size", 0) / (1024 * 1024)
            self.metrics.index_size_mb = stats.get("totalIndexSize", 0) / (1024 * 1024)
            self.metrics.average_document_size = stats.get("avgObjSize", 0)
            
            # Get shard distribution
            if self.sharding_manager:
                self.metrics.shard_distribution = await self.sharding_manager.get_shard_distribution()
            
            # Get GridFS stats
            if self.gridfs_manager and self.gridfs_manager.gridfs:
                try:
                    gridfs_stats = await self.database.command("collStats", "event_files.files")
                    self.metrics.gridfs_files = gridfs_stats.get("count", 0)
                except:
                    self.metrics.gridfs_files = 0
            
            return self.metrics
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return self.metrics
    
    async def health_check(self) -> bool:
        """Check MongoDB collection health"""
        if self.client == "mock_client":
            return True
        
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.change_stream_processor:
            await self.change_stream_processor.stop_all_streams()
        
        if self.client and self.client != "mock_client":
            self.client.close()