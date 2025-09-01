"""MongoDB Connection Handler - IA Influencer Agent Platform

Manages MongoDB connections for content metadata and analytics:
- Content fingerprint metadata and embeddings
- User-generated content analytics
- Platform integration logs and metrics
- AI processing results and history
- Collaboration recommendation data
- Revenue analytics and reporting data

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

import motor.motor_asyncio as motor
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


@dataclass
class MongoDBConfig:
    """MongoDB connection configuration"""
    host: str = "localhost"
    port: int = 27017
    database: str = "ia_influencer_content"
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    replica_set: Optional[str] = None
    ssl: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    ssl_ca_file: Optional[str] = None
    max_pool_size: int = 100
    min_pool_size: int = 10
    max_idle_time_ms: int = 300000  # 5 minutes
    server_selection_timeout_ms: int = 30000  # 30 seconds
    socket_timeout_ms: int = 60000  # 60 seconds
    connect_timeout_ms: int = 20000  # 20 seconds
    tenant_database_prefix: str = "tenant_"


class MongoDBConnectionHandler:
    """
    MongoDB connection handler for IA Influencer platform.
    
    Manages MongoDB for:
    - Content fingerprint metadata storage
    - User analytics and behavioral data
    - AI processing logs and results
    - Platform integration metrics
    - Collaboration and recommendation data
    - Revenue analytics and reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = MongoDBConfig(**config)
        self.logger = logging.getLogger(__name__)
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        
        # Tenant databases
        self.tenant_databases: Dict[str, AsyncIOMotorDatabase] = {}
        
        # Connection metrics
        self.connection_count = 0
        self.operation_count = 0
        self.error_count = 0
        self.last_health_check = None
    
    async def initialize(self) -> None:
        """Initialize MongoDB connection"""
        try:
            self.logger.info("Initializing MongoDB connection...")
            
            # Build connection URI
            uri = self._build_connection_uri()
            
            # Create client
            self.client = AsyncIOMotorClient(
                uri,
                maxPoolSize=self.config.max_pool_size,
                minPoolSize=self.config.min_pool_size,
                maxIdleTimeMS=self.config.max_idle_time_ms,
                serverSelectionTimeoutMS=self.config.server_selection_timeout_ms,
                socketTimeoutMS=self.config.socket_timeout_ms,
                connectTimeoutMS=self.config.connect_timeout_ms
            )
            
            # Get database
            self.database = self.client[self.config.database]
            
            # Create indexes
            await self._create_indexes()
            
            # Verify connection
            await self.health_check()
            
            self.logger.info("MongoDB connection initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise
    
    def _build_connection_uri(self) -> str:
        """Build MongoDB connection URI"""
        if self.config.username and self.config.password:
            auth_part = f"{self.config.username}:{self.config.password}@"
        else:
            auth_part = ""
        
        uri = f"mongodb://{auth_part}{self.config.host}:{self.config.port}/{self.config.database}"
        
        # Add query parameters
        params = []
        
        if self.config.auth_source:
            params.append(f"authSource={self.config.auth_source}")
        
        if self.config.replica_set:
            params.append(f"replicaSet={self.config.replica_set}")
        
        if self.config.ssl:
            params.append("ssl=true")
            if self.config.ssl_cert_file:
                params.append(f"ssl_certfile={self.config.ssl_cert_file}")
            if self.config.ssl_key_file:
                params.append(f"ssl_keyfile={self.config.ssl_key_file}")
            if self.config.ssl_ca_file:
                params.append(f"ssl_ca_certs={self.config.ssl_ca_file}")
        
        if params:
            uri += "?" + "&".join(params)
        
        return uri
    
    async def _create_indexes(self) -> None:
        """Create necessary indexes for collections"""
        try:
            # Content fingerprints collection indexes
            fingerprints = self.database.content_fingerprints
            await fingerprints.create_index([("user_id", ASCENDING)])
            await fingerprints.create_index([("content_type", ASCENDING)])
            await fingerprints.create_index([("fingerprint_hash", ASCENDING)], unique=True)
            await fingerprints.create_index([("created_at", DESCENDING)])
            await fingerprints.create_index([("metadata.platform", ASCENDING)])
            
            # User analytics collection indexes
            analytics = self.database.user_analytics
            await analytics.create_index([("user_id", ASCENDING)])
            await analytics.create_index([("event_type", ASCENDING)])
            await analytics.create_index([("timestamp", DESCENDING)])
            await analytics.create_index([("session_id", ASCENDING)])
            
            # AI processing results indexes
            ai_results = self.database.ai_processing_results
            await ai_results.create_index([("content_id", ASCENDING)])
            await ai_results.create_index([("processing_type", ASCENDING)])
            await ai_results.create_index([("status", ASCENDING)])
            await ai_results.create_index([("created_at", DESCENDING)])
            
            # Platform integrations indexes
            integrations = self.database.platform_integrations
            await integrations.create_index([("user_id", ASCENDING)])
            await integrations.create_index([("platform", ASCENDING)])
            await integrations.create_index([("status", ASCENDING)])
            await integrations.create_index([("last_sync", DESCENDING)])
            
            # Revenue analytics indexes
            revenue = self.database.revenue_analytics
            await revenue.create_index([("user_id", ASCENDING)])
            await revenue.create_index([("platform", ASCENDING)])
            await revenue.create_index([("period_start", DESCENDING)])
            await revenue.create_index([("content_id", ASCENDING)])
            
            # Collaboration data indexes
            collaborations = self.database.collaborations
            await collaborations.create_index([("creator_id", ASCENDING)])
            await collaborations.create_index([("collaborator_id", ASCENDING)])
            await collaborations.create_index([("status", ASCENDING)])
            await collaborations.create_index([("match_score", DESCENDING)])
            
            # Text indexes for search
            await fingerprints.create_index([("metadata.title", TEXT), ("metadata.description", TEXT)])
            await analytics.create_index([("event_data.search_query", TEXT)])
            
            self.logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB indexes: {e}")
            # Don't raise here, indexes might already exist
    
    async def get_connection(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database connection"""
        if not self.database:
            raise RuntimeError("MongoDB not initialized")
        
        self.connection_count += 1
        return self.database
    
    async def get_tenant_connection(self, tenant_id: str) -> AsyncIOMotorDatabase:
        """Get tenant-specific database connection"""
        if tenant_id not in self.tenant_databases:
            await self._create_tenant_database(tenant_id)
        
        return self.tenant_databases[tenant_id]
    
    async def _create_tenant_database(self, tenant_id: str) -> None:
        """Create database for specific tenant"""
        if not self.client:
            raise RuntimeError("MongoDB client not initialized")
        
        db_name = f"{self.config.tenant_database_prefix}{tenant_id}"
        tenant_db = self.client[db_name]
        
        # Create tenant-specific indexes
        await self._create_tenant_indexes(tenant_db)
        
        self.tenant_databases[tenant_id] = tenant_db
    
    async def _create_tenant_indexes(self, database: AsyncIOMotorDatabase) -> None:
        """Create indexes for tenant database"""
        # Create same indexes as main database for tenant isolation
        await self._create_indexes_for_database(database)
    
    async def _create_indexes_for_database(self, database: AsyncIOMotorDatabase) -> None:
        """Create indexes for a specific database"""
        try:
            # Content fingerprints
            fingerprints = database.content_fingerprints
            await fingerprints.create_index([("user_id", ASCENDING)])
            await fingerprints.create_index([("content_type", ASCENDING)])
            await fingerprints.create_index([("fingerprint_hash", ASCENDING)], unique=True)
            await fingerprints.create_index([("created_at", DESCENDING)])
            
            # User analytics
            analytics = database.user_analytics
            await analytics.create_index([("user_id", ASCENDING)])
            await analytics.create_index([("event_type", ASCENDING)])
            await analytics.create_index([("timestamp", DESCENDING)])
            
        except Exception as e:
            self.logger.warning(f"Some indexes might already exist: {e}")
    
    # Collection operations
    async def get_collection(self, 
                           collection_name: str, 
                           tenant_id: Optional[str] = None) -> AsyncIOMotorCollection:
        """Get collection from database"""
        if tenant_id:
            database = await self.get_tenant_connection(tenant_id)
        else:
            database = await self.get_connection()
        
        return database[collection_name]
    
    # Document operations
    async def insert_one(self, 
                        collection_name: str, 
                        document: Dict[str, Any],
                        tenant_id: Optional[str] = None) -> str:
        """Insert single document"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow()
            
            result = await collection.insert_one(document)
            self.operation_count += 1
            
            return str(result.inserted_id)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB insert_one failed: {e}")
            raise
    
    async def insert_many(self, 
                         collection_name: str, 
                         documents: List[Dict[str, Any]],
                         tenant_id: Optional[str] = None) -> List[str]:
        """Insert multiple documents"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            
            # Add timestamps if not present
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = datetime.utcnow()
            
            result = await collection.insert_many(documents)
            self.operation_count += 1
            
            return [str(oid) for oid in result.inserted_ids]
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB insert_many failed: {e}")
            raise
    
    async def find_one(self, 
                      collection_name: str, 
                      filter_dict: Dict[str, Any],
                      projection: Optional[Dict[str, Any]] = None,
                      tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find single document"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            result = await collection.find_one(filter_dict, projection)
            self.operation_count += 1
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB find_one failed: {e}")
            raise
    
    async def find(self, 
                  collection_name: str, 
                  filter_dict: Dict[str, Any],
                  projection: Optional[Dict[str, Any]] = None,
                  sort: Optional[List[tuple]] = None,
                  limit: Optional[int] = None,
                  skip: Optional[int] = None,
                  tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            
            cursor = collection.find(filter_dict, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            
            if skip:
                cursor = cursor.skip(skip)
            
            if limit:
                cursor = cursor.limit(limit)
            
            results = await cursor.to_list(length=limit)
            self.operation_count += 1
            
            return results
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB find failed: {e}")
            raise
    
    async def update_one(self, 
                        collection_name: str, 
                        filter_dict: Dict[str, Any],
                        update_dict: Dict[str, Any],
                        upsert: bool = False,
                        tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Update single document"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            
            # Add updated_at timestamp
            if '$set' not in update_dict:
                update_dict['$set'] = {}
            update_dict['$set']['updated_at'] = datetime.utcnow()
            
            result = await collection.update_one(filter_dict, update_dict, upsert=upsert)
            self.operation_count += 1
            
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB update_one failed: {e}")
            raise
    
    async def update_many(self, 
                         collection_name: str, 
                         filter_dict: Dict[str, Any],
                         update_dict: Dict[str, Any],
                         tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Update multiple documents"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            
            # Add updated_at timestamp
            if '$set' not in update_dict:
                update_dict['$set'] = {}
            update_dict['$set']['updated_at'] = datetime.utcnow()
            
            result = await collection.update_many(filter_dict, update_dict)
            self.operation_count += 1
            
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB update_many failed: {e}")
            raise
    
    async def delete_one(self, 
                        collection_name: str, 
                        filter_dict: Dict[str, Any],
                        tenant_id: Optional[str] = None) -> int:
        """Delete single document"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            result = await collection.delete_one(filter_dict)
            self.operation_count += 1
            
            return result.deleted_count
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB delete_one failed: {e}")
            raise
    
    async def delete_many(self, 
                         collection_name: str, 
                         filter_dict: Dict[str, Any],
                         tenant_id: Optional[str] = None) -> int:
        """Delete multiple documents"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            result = await collection.delete_many(filter_dict)
            self.operation_count += 1
            
            return result.deleted_count
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB delete_many failed: {e}")
            raise
    
    async def count_documents(self, 
                            collection_name: str, 
                            filter_dict: Dict[str, Any],
                            tenant_id: Optional[str] = None) -> int:
        """Count documents in collection"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            result = await collection.count_documents(filter_dict)
            self.operation_count += 1
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB count_documents failed: {e}")
            raise
    
    async def aggregate(self, 
                       collection_name: str, 
                       pipeline: List[Dict[str, Any]],
                       tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            collection = await self.get_collection(collection_name, tenant_id)
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            self.operation_count += 1
            
            return results
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"MongoDB aggregate failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health"""
        try:
            start_time = datetime.utcnow()
            
            if not self.client:
                raise RuntimeError("MongoDB client not initialized")
            
            # Test basic connectivity
            await self.client.admin.command('ismaster')
            
            # Get server status
            server_status = await self.client.admin.command('serverStatus')
            
            # Get database stats
            db_stats = await self.database.command('dbStats')
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "server_version": server_status.get("version"),
                "uptime": server_status.get("uptime"),
                "connections": server_status.get("connections", {}),
                "database": {
                    "name": self.config.database,
                    "collections": db_stats.get("collections"),
                    "data_size": db_stats.get("dataSize"),
                    "storage_size": db_stats.get("storageSize"),
                    "indexes": db_stats.get("indexes")
                },
                "metrics": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count
                },
                "tenant_databases": len(self.tenant_databases),
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"MongoDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed MongoDB metrics"""
        try:
            if not self.client:
                return {"status": "not_initialized"}
            
            # Server status
            server_status = await self.client.admin.command('serverStatus')
            
            # Database stats
            db_stats = await self.database.command('dbStats')
            
            # Collection stats
            collection_stats = {}
            for collection_name in await self.database.list_collection_names():
                stats = await self.database.command('collStats', collection_name)
                collection_stats[collection_name] = {
                    "count": stats.get("count"),
                    "size": stats.get("size"),
                    "storage_size": stats.get("storageSize"),
                    "total_index_size": stats.get("totalIndexSize")
                }
            
            return {
                "server": {
                    "version": server_status.get("version"),
                    "uptime": server_status.get("uptime"),
                    "local_time": server_status.get("localTime")
                },
                "connections": server_status.get("connections", {}),
                "opcounters": server_status.get("opcounters", {}),
                "memory": server_status.get("mem", {}),
                "network": server_status.get("network", {}),
                "database": {
                    "name": self.config.database,
                    "collections": db_stats.get("collections"),
                    "objects": db_stats.get("objects"),
                    "data_size": db_stats.get("dataSize"),
                    "storage_size": db_stats.get("storageSize"),
                    "num_extents": db_stats.get("numExtents"),
                    "indexes": db_stats.get("indexes"),
                    "index_size": db_stats.get("indexSize")
                },
                "collections": collection_stats,
                "client_metrics": {
                    "connection_count": self.connection_count,
                    "operation_count": self.operation_count,
                    "error_count": self.error_count,
                    "tenant_databases": len(self.tenant_databases)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get MongoDB metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown MongoDB connections"""
        self.logger.info("Shutting down MongoDB connections...")
        
        if self.client:
            self.client.close()
            self.logger.info("Closed MongoDB client")
        
        self.client = None
        self.database = None
        self.tenant_databases.clear()
        
        self.logger.info("MongoDB connections shutdown completed")
