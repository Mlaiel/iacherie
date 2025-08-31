"""Database Management System
Advanced multi-database management for PostgreSQL, Redis, and MongoDB.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import asyncpg
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, inspect

from ..config import settings


# SQLAlchemy Base Model
Base = declarative_base()
metadata = MetaData()


class DatabaseManager:
    """    Advanced database manager handling multiple database systems.
    Provides connection pooling, transaction management, and health monitoring.
    """    
    def __init__(self):
        self.postgres_engine = None
        self.postgres_sessionmaker = None
        self.redis_client = None
        self.mongodb_client = None
        self.mongodb_database = None
        self._health_status = {
            "postgres": False,
            "redis": False,
            "mongodb": False
        }
    
    async def initialize(self) -> None:
        """Initialize all database connections"""        await self._initialize_postgres()
        await self._initialize_redis()
        await self._initialize_mongodb()
        await self._run_health_checks()
    
    async def _initialize_postgres(self) -> None:
        """Initialize PostgreSQL connection with connection pooling"""        try:
            # Create async engine with connection pooling
            self.postgres_engine = create_async_engine(
                settings.database.postgres_url,
                echo=settings.app.debug,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Create session factory
            self.postgres_sessionmaker = async_sessionmaker(
                bind=self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.postgres_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            self._health_status["postgres"] = True
            
        except Exception as e:
            self._health_status["postgres"] = False
            raise Exception(f"PostgreSQL initialization failed: {str(e)}")
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection with connection pooling"""        try:
            self.redis_client = aioredis.from_url(
                settings.database.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            self._health_status["redis"] = True
            
        except Exception as e:
            self._health_status["redis"] = False
            raise Exception(f"Redis initialization failed: {str(e)}")
    
    async def _initialize_mongodb(self) -> None:
        """Initialize MongoDB connection"""        try:
            self.mongodb_client = AsyncIOMotorClient(
                settings.database.mongodb_url,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                socketKeepAlive=True
            )
            
            self.mongodb_database = self.mongodb_client[settings.database.mongodb_db]
            
            # Test connection
            await self.mongodb_client.admin.command("ping")
            self._health_status["mongodb"] = True
            
        except Exception as e:
            self._health_status["mongodb"] = False
            raise Exception(f"MongoDB initialization failed: {str(e)}")
    
    @asynccontextmanager
    async def get_postgres_session(self):
        """Get PostgreSQL session with automatic cleanup"""        async with self.postgres_sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_redis_client(self):
        """Get Redis client"""        if not self.redis_client:
            raise Exception("Redis client not initialized")
        return self.redis_client
    
    async def get_mongodb_database(self):
        """Get MongoDB database"""        if not self.mongodb_database:
            raise Exception("MongoDB database not initialized")
        return self.mongodb_database
    
    async def get_mongodb_collection(self, collection_name: str):
        """Get MongoDB collection"""        database = await self.get_mongodb_database()
        return database[collection_name]
    
    async def _run_health_checks(self) -> None:
        """Run health checks on all databases"""        # PostgreSQL health check
        try:
            async with self.postgres_engine.begin() as conn:
                await conn.execute("SELECT 1")
            self._health_status["postgres"] = True
        except Exception:
            self._health_status["postgres"] = False
        
        # Redis health check
        try:
            await self.redis_client.ping()
            self._health_status["redis"] = True
        except Exception:
            self._health_status["redis"] = False
        
        # MongoDB health check
        try:
            await self.mongodb_client.admin.command("ping")
            self._health_status["mongodb"] = True
        except Exception:
            self._health_status["mongodb"] = False
    
    async def get_health_status(self) -> Dict[str, bool]:
        """Get current health status of all databases"""        await self._run_health_checks()
        return self._health_status.copy()
    
    async def execute_postgres_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw PostgreSQL query"""        async with self.get_postgres_session() as session:
            result = await session.execute(query, params or {})
            return [dict(row) for row in result.fetchall()]
    
    async def execute_redis_command(self, command: str, *args, **kwargs) -> Any:
        """Execute Redis command"""        redis_client = await self.get_redis_client()
        return await getattr(redis_client, command)(*args, **kwargs)
    
    async def find_mongodb_documents(self, collection: str, filter_dict: Dict = None, 
                                   limit: Optional[int] = None) -> List[Dict]:
        """Find documents in MongoDB collection"""        collection_obj = await self.get_mongodb_collection(collection)
        cursor = collection_obj.find(filter_dict or {})
        
        if limit:
            cursor = cursor.limit(limit)
        
        return await cursor.to_list(length=None)
    
    async def insert_mongodb_document(self, collection: str, document: Dict) -> str:
        """Insert document into MongoDB collection"""        collection_obj = await self.get_mongodb_collection(collection)
        result = await collection_obj.insert_one(document)
        return str(result.inserted_id)
    
    async def update_mongodb_document(self, collection: str, filter_dict: Dict, 
                                    update_dict: Dict) -> int:
        """Update documents in MongoDB collection"""        collection_obj = await self.get_mongodb_collection(collection)
        result = await collection_obj.update_many(filter_dict, {"$set": update_dict})
        return result.modified_count
    
    async def delete_mongodb_documents(self, collection: str, filter_dict: Dict) -> int:
        """Delete documents from MongoDB collection"""        collection_obj = await self.get_mongodb_collection(collection)
        result = await collection_obj.delete_many(filter_dict)
        return result.deleted_count
    
    async def create_indexes(self) -> None:
        """Create database indexes for performance optimization"""        # PostgreSQL indexes will be created via SQLAlchemy migrations
        
        # MongoDB indexes
        try:
            # Content fingerprints collection indexes
            fingerprints = await self.get_mongodb_collection("content_fingerprints")
            await fingerprints.create_index([("user_id", 1), ("content_type", 1)])
            await fingerprints.create_index([("fingerprint_hash", 1)])
            await fingerprints.create_index([("created_at", -1)])
            
            # Protection alerts collection indexes
            alerts = await self.get_mongodb_collection("protection_alerts")
            await alerts.create_index([("fingerprint_id", 1)])
            await alerts.create_index([("platform", 1), ("status", 1)])
            await alerts.create_index([("created_at", -1)])
            
            # User analytics collection indexes
            analytics = await self.get_mongodb_collection("user_analytics")
            await analytics.create_index([("user_id", 1), ("date", -1)])
            await analytics.create_index([("platform", 1)])
            
        except Exception as e:
            raise Exception(f"Index creation failed: {str(e)}")
    
    async def close_connections(self) -> None:
        """Close all database connections"""        try:
            if self.postgres_engine:
                await self.postgres_engine.dispose()
            
            if self.redis_client:
                await self.redis_client.close()
            
            if self.mongodb_client:
                self.mongodb_client.close()
                
        except Exception as e:
            raise Exception(f"Error closing database connections: {str(e)}")


# Global database manager instance
database_manager = DatabaseManager()