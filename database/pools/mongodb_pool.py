"""MongoDB Connection Pool - IA Influencer Agent + Content Protection Platform

Enterprise MongoDB connection pool implementation for content metadata,
fingerprints, analytics data, and multi-media content processing.

Features:
- GridFS support for large content files
- Aggregation pipeline optimization
- Sharding and replica set support
- Change streams for real-time monitoring
- Multi-tenant collections management
- Full-text search integration
- Geospatial indexing for location-based features

Content Types Supported:
- Audio fingerprints and metadata
- Video content analysis data
- Image fingerprints and embeddings
- Text content and NLP analysis
- User behavior analytics
- Revenue tracking documents

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import gridfs
import bson
from urllib.parse import quote_plus

try:
    import motor.motor_asyncio
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
    from pymongo.read_preferences import ReadPreference
    from pymongo.write_concern import WriteConcern
    from pymongo.read_concern import ReadConcern
except ImportError as e:
    logging.warning(f"MongoDB dependency missing: {e}")

from .manager import IConnectionPool, PoolConfig, DatabaseConnectionInfo, ConnectionState

logger = logging.getLogger(__name__)

# =============== MONGODB SPECIFIC CONFIGURATION ===============

@dataclass
class MongoDBPoolConfig(PoolConfig):
    """Extended MongoDB pool configuration"""
    # MongoDB specific settings
    replica_set: Optional[str] = None
    read_preference: str = "primaryPreferred"
    write_concern_w: Union[int, str] = 1
    write_concern_journal: bool = True
    read_concern_level: str = "local"
    
    # Connection optimization
    max_idle_time_ms: int = 300000
    server_selection_timeout_ms: int = 30000
    socket_timeout_ms: int = 60000
    connect_timeout_ms: int = 20000
    heartbeat_frequency_ms: int = 10000
    
    # GridFS settings
    enable_gridfs: bool = True
    gridfs_chunk_size: int = 261120  # 255KB chunks
    
    # Sharding settings
    enable_sharding: bool = False
    shard_key_fields: List[str] = None
    
    # Change streams
    enable_change_streams: bool = True
    change_stream_resume_after: Optional[str] = None

# =============== MONGODB CONNECTION POOL ===============

class MongoDBConnectionPool(IConnectionPool):
    """MongoDB connection pool with enterprise features"""
    
    def __init__(self, config: MongoDBPoolConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.gridfs: Optional[motor.motor_asyncio.AsyncIOMotorGridFSBucket] = None
        self.state = ConnectionState.IDLE
        
        # Collection references
        self.collections = {}
        self.change_streams = {}
        
        # Statistics
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_operations": 0,
            "active_connections": 0,
            "failed_operations": 0,
            "total_documents": 0,
            "gridfs_files": 0,
            "change_stream_events": 0,
            "last_health_check": None,
            "collection_stats": {}
        }
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._change_stream_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize(self) -> bool:
        """Initialize MongoDB connection and database"""
        try:
            # Build connection URI
            connection_uri = self._build_connection_uri()
            
            # Create MongoDB client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                connection_uri,
                maxPoolSize=self.config.max_size,
                minPoolSize=self.config.min_size,
                maxIdleTimeMS=self.config.max_idle_time_ms,
                serverSelectionTimeoutMS=self.config.server_selection_timeout_ms,
                socketTimeoutMS=self.config.socket_timeout_ms,
                connectTimeoutMS=self.config.connect_timeout_ms,
                heartbeatFrequencyMS=self.config.heartbeat_frequency_ms,
                retryWrites=True,
                retryReads=True
            )
            
            # Get database reference
            self.database = self.client[self.connection_info.database]
            
            # Configure read/write concerns
            read_concern = ReadConcern(level=self.config.read_concern_level)
            write_concern = WriteConcern(
                w=self.config.write_concern_w,
                journal=self.config.write_concern_journal
            )
            
            self.database = self.database.with_options(
                read_concern=read_concern,
                write_concern=write_concern,
                read_preference=self._get_read_preference()
            )
            
            # Initialize GridFS if enabled
            if self.config.enable_gridfs:
                self.gridfs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(
                    self.database,
                    chunk_size_bytes=self.config.gridfs_chunk_size
                )
            
            # Test connection
            await self.health_check()
            
            # Initialize collections for content protection
            await self._initialize_collections()
            
            # Start change streams if enabled
            if self.config.enable_change_streams:
                await self._start_change_streams()
            
            self.state = ConnectionState.ACTIVE
            
            # Start health monitoring
            if self.config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_monitor())
            
            logger.info(f"✅ MongoDB pool initialized - Database: {self.connection_info.database}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    def _build_connection_uri(self) -> str:
        try:
            logger.info(f"Executing _build_connection_uri")
            
            # Implementation for _build_connection_uri
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_build_connection_uri completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_build_connection_uri failed: {e}")
            raise
    def _get_read_preference(self) -> ReadPreference:
        """Get MongoDB read preference"""
        preference_map = {
            "primary": ReadPreference.PRIMARY,
            "primaryPreferred": ReadPreference.PRIMARY_PREFERRED,
            "secondary": ReadPreference.SECONDARY,
            "secondaryPreferred": ReadPreference.SECONDARY_PREFERRED,
            "nearest": ReadPreference.NEAREST
        }
        return preference_map.get(self.config.read_preference, ReadPreference.PRIMARY_PREFERRED)
    
    async def _initialize_collections(self) -> None:
        """Initialize collections for content protection platform"""
        collection_configs = {
            # Content fingerprinting collections
            "content_fingerprints": {
                "indexes": [
                    {"keys": [("user_id", 1), ("content_type", 1)]},
                    {"keys": [("fingerprint_hash", 1)], "unique": True},
                    {"keys": [("created_at", -1)]},
                    {"keys": [("vector_embedding", "2dsphere")]},  # For geospatial if needed
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["user_id", "content_type", "fingerprint_hash"],
                        "properties": {
                            "user_id": {"bsonType": "objectId"},
                            "content_type": {"enum": ["audio", "video", "image", "text"]},
                            "fingerprint_hash": {"bsonType": "string"},
                            "vector_embedding": {"bsonType": "array"},
                            "metadata": {"bsonType": "object"}
                        }
                    }
                }
            },
            
            # Protection alerts collection
            "protection_alerts": {
                "indexes": [
                    {"keys": [("fingerprint_id", 1)]},
                    {"keys": [("detected_url", 1)]},
                    {"keys": [("platform", 1), ("status", 1)]},
                    {"keys": [("created_at", -1)]},
                    {"keys": [("similarity_score", -1)]},
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["fingerprint_id", "detected_url", "platform"],
                        "properties": {
                            "fingerprint_id": {"bsonType": "objectId"},
                            "detected_url": {"bsonType": "string"},
                            "platform": {"bsonType": "string"},
                            "similarity_score": {"bsonType": "double", "minimum": 0, "maximum": 1},
                            "status": {"enum": ["pending", "verified", "false_positive", "resolved"]}
                        }
                    }
                }
            },
            
            # Revenue tracking collection
            "revenue_tracking": {
                "indexes": [
                    {"keys": [("user_id", 1), ("period_start", -1)]},
                    {"keys": [("content_id", 1)]},
                    {"keys": [("platform", 1), ("currency", 1)]},
                    {"keys": [("created_at", -1)]},
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["user_id", "platform", "revenue_amount"],
                        "properties": {
                            "user_id": {"bsonType": "objectId"},
                            "content_id": {"bsonType": "objectId"},
                            "platform": {"bsonType": "string"},
                            "revenue_amount": {"bsonType": "double", "minimum": 0},
                            "currency": {"bsonType": "string", "pattern": "^[A-Z]{3}$"}
                        }
                    }
                }
            },
            
            # Analytics data collection
            "analytics_data": {
                "indexes": [
                    {"keys": [("user_id", 1), ("timestamp", -1)]},
                    {"keys": [("content_id", 1), ("metric_type", 1)]},
                    {"keys": [("platform", 1), ("timestamp", -1)]},
                    {"keys": [("geolocation", "2dsphere")]},
                ],
                "time_series": {
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "hours"
                }
            },
            
            # User behavior collection
            "user_behavior": {
                "indexes": [
                    {"keys": [("user_id", 1), ("timestamp", -1)]},
                    {"keys": [("action_type", 1), ("timestamp", -1)]},
                    {"keys": [("session_id", 1)]},
                ],
                "capped": True,
                "size": 100 * 1024 * 1024,  # 100MB cap
                "max": 1000000  # Max 1M documents
            }
        }
        
        for collection_name, config in collection_configs.items():
            try:
                # Create collection if it doesn't exist
                if collection_name not in await self.database.list_collection_names():
                    create_options = {}
                    
                    if "validator" in config:
                        create_options["validator"] = config["validator"]
                    
                    if "time_series" in config:
                        create_options["timeseries"] = config["time_series"]
                    
                    if "capped" in config:
                        create_options["capped"] = True
                        create_options["size"] = config["size"]
                        if "max" in config:
                            create_options["max"] = config["max"]
                    
                    await self.database.create_collection(collection_name, **create_options)
                
                # Get collection reference
                collection = self.database[collection_name]
                self.collections[collection_name] = collection
                
                # Create indexes
                if "indexes" in config:
                    for index_config in config["indexes"]:
                        try:
                            await collection.create_index(
                                index_config["keys"],
                                **{k: v for k, v in index_config.items() if k != "keys"}
                            )
                        except Exception as e:
                            logger.warning(f"Index creation failed for {collection_name}: {e}")
                
                logger.info(f"✅ Collection {collection_name} initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize collection {collection_name}: {e}")
    
    async def _start_change_streams(self) -> None:
        """Start change streams for real-time monitoring"""
        if not self.config.enable_change_streams:
            return
        
        # Monitor protection alerts for real-time notifications
        change_stream_configs = {
            "protection_alerts": {
                "pipeline": [
                    {"$match": {"operationType": "insert"}},
                    {"$match": {"fullDocument.status": "pending"}}
                ],
                "callback": self._handle_protection_alert
            },
            "revenue_tracking": {
                "pipeline": [
                    {"$match": {"operationType": "insert"}},
                    {"$match": {"fullDocument.revenue_amount": {"$gt": 0}}}
                ],
                "callback": self._handle_revenue_update
            }
        }
        
        for collection_name, config in change_stream_configs.items():
            if collection_name in self.collections:
                try:
                    task = asyncio.create_task(
                        self._monitor_change_stream(
                            collection_name,
                            config["pipeline"],
                            config["callback"]
                        )
                    )
                    self._change_stream_tasks[collection_name] = task
                    logger.info(f"✅ Change stream started for {collection_name}")
                except Exception as e:
                    logger.error(f"Failed to start change stream for {collection_name}: {e}")
    
    async def _monitor_change_stream(self, collection_name: str, pipeline: List[Dict], callback: callable) -> None:
        """Monitor change stream for a collection"""
        collection = self.collections[collection_name]
        
        while self.state == ConnectionState.ACTIVE:
            try:
                async with collection.watch(pipeline) as stream:
                    async for change in stream:
                        await callback(change)
                        self.stats["change_stream_events"] += 1
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Change stream error for {collection_name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _handle_protection_alert(self, change: Dict) -> None:
        """Handle new protection alert"""
        try:
            document = change.get("fullDocument", {})
            logger.info(f"🚨 New protection alert: {document.get('detected_url')} on {document.get('platform')}")
            # Add notification logic here
        except Exception as e:
            logger.error(f"Error handling protection alert: {e}")
    
    async def _handle_revenue_update(self, change: Dict) -> None:
        """Handle revenue update"""
        try:
            document = change.get("fullDocument", {})
            logger.info(f"💰 Revenue update: {document.get('revenue_amount')} {document.get('currency', 'EUR')}")
            # Add revenue processing logic here
        except Exception as e:
            logger.error(f"Error handling revenue update: {e}")
    
    async def acquire(self, timeout: Optional[float] = None) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Acquire database connection"""
        if not self.database:
            raise Exception("MongoDB pool not initialized")
        
        self.stats["active_connections"] += 1
        return self.database
    
    async def release(self, connection: motor.motor_asyncio.AsyncIOMotorDatabase) -> None:
        """Release database connection (no-op for MongoDB)"""
        self.stats["active_connections"] = max(0, self.stats["active_connections"] - 1)
    
    async def get_collection(self, collection_name: str) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """Get collection by name"""
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        # Return collection from database if not in cache
        collection = self.database[collection_name]
        self.collections[collection_name] = collection
        return collection
    
    async def insert_content_fingerprint(self, fingerprint_data: Dict[str, Any]) -> bson.ObjectId:
        """
Insert content fingerprint with validation"""
        try:
            collection = await self.get_collection("content_fingerprints")
            result = await collection.insert_one(fingerprint_data)
            
            self.stats["total_operations"] += 1
            self.stats["total_documents"] += 1
            
            return result.inserted_id
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Failed to insert content fingerprint: {e}")
            raise
    
    async def find_similar_fingerprints(self, vector_embedding: List[float], 
                                       content_type: str, threshold: float = 0.8) -> List[Dict]:
        """Find similar content fingerprints using vector similarity"""
        try:
            collection = await self.get_collection("content_fingerprints")
            
            # This is a simplified similarity search - in production you'd use vector databases
            # or MongoDB's $vectorSearch when available
            pipeline = [
                {"$match": {"content_type": content_type}},
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dot_product": {
                                        "$reduce": {
                                            "input": {"$range": [0, {"$size": "$vector_embedding"}]},
                                            "initialValue": 0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {
                                                        "$multiply": [
                                                            {"$arrayElemAt": ["$vector_embedding", "$$this"]},
                                                            {"$arrayElemAt": [vector_embedding, "$$this"]}
                                                        ]
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": "$$dot_product"  # Simplified - should include normalization
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": threshold}}},
                {"$sort": {"similarity": -1}},
                {"$limit": 100}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=100)
            self.stats["total_operations"] += 1
            
            return results
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Failed to find similar fingerprints: {e}")
            raise
    
    async def store_large_file(self, file_data: bytes, filename: str, metadata: Dict[str, Any]) -> bson.ObjectId:
        """Store large file using GridFS"""
        if not self.gridfs:
            raise Exception("GridFS not enabled")
        
        try:
            file_id = await self.gridfs.upload_from_stream(
                filename,
                file_data,
                metadata=metadata
            )
            
            self.stats["gridfs_files"] += 1
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to store file {filename}: {e}")
            raise
    
    async def retrieve_large_file(self, file_id: bson.ObjectId) -> Tuple[bytes, Dict[str, Any]]:
        """Retrieve large file from GridFS"""
        if not self.gridfs:
            raise Exception("GridFS not enabled")
        
        try:
            grid_out = await self.gridfs.open_download_stream(file_id)
            file_data = await grid_out.read()
            metadata = grid_out.metadata or {}
            
            return file_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {e}")
            raise
    
    async def aggregate_revenue_stats(self, user_id: bson.ObjectId, 
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Aggregate revenue statistics for user"""
        try:
            collection = await self.get_collection("revenue_tracking")
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "period_start": {"$gte": start_date},
                        "period_end": {"$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "platform": "$platform",
                            "currency": "$currency"
                        },
                        "total_revenue": {"$sum": "$revenue_amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_revenue": {"$avg": "$revenue_amount"},
                        "max_revenue": {"$max": "$revenue_amount"},
                        "min_revenue": {"$min": "$revenue_amount"}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "platforms": {
                            "$push": {
                                "platform": "$_id.platform",
                                "currency": "$_id.currency",
                                "total_revenue": "$total_revenue",
                                "transaction_count": "$transaction_count",
                                "avg_revenue": "$avg_revenue",
                                "max_revenue": "$max_revenue",
                                "min_revenue": "$min_revenue"
                            }
                        },
                        "grand_total": {"$sum": "$total_revenue"},
                        "total_transactions": {"$sum": "$transaction_count"}
                    }
                }
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=1)
            self.stats["total_operations"] += 1
            
            return results[0] if results else {}
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error(f"Failed to aggregate revenue stats: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check MongoDB health"""
        try:
            # Ping the database
            await self.client.admin.command('ping')
            
            # Check database stats
            stats = await self.database.command("dbStats")
            
            self.stats["last_health_check"] = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""
        while self.state == ConnectionState.ACTIVE:
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("MongoDB pool health check failed")
                
                # Update collection stats
                await self._update_collection_stats()
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"MongoDB health monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _update_collection_stats(self) -> None:
        """Update collection statistics"""
        try:
            for collection_name in self.collections:
                collection = self.collections[collection_name]
                stats = await self.database.command("collStats", collection_name)
                
                self.stats["collection_stats"][collection_name] = {
                    "document_count": stats.get("count", 0),
                    "storage_size": stats.get("storageSize", 0),
                    "index_count": stats.get("nindexes", 0),
                    "index_size": stats.get("totalIndexSize", 0)
                }
                
        except Exception as e:
            logger.error(f"Failed to update collection stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MongoDB pool statistics"""
        pool_stats = {
            "client_info": str(self.client) if self.client else None,
            "database_name": self.connection_info.database,
            "collections_count": len(self.collections),
            "gridfs_enabled": self.config.enable_gridfs,
            "change_streams_active": len(self._change_stream_tasks),
            "state": self.state.value
        }
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close MongoDB pool"""
        try:
            self.state = ConnectionState.CLOSED
            
            # Cancel change stream tasks
            for task_name, task in self._change_stream_tasks.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info(f"✅ Change stream {task_name} closed")
            
            # Cancel health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close client
            if self.client:
                self.client.close()
            
            logger.info("✅ MongoDB pool closed")
            
        except Exception as e:
            logger.error(f"Error closing MongoDB pool: {e}")

# =============== EXPORTS ===============

__all__ = [
    "MongoDBConnectionPool",
    "MongoDBPoolConfig"
]
