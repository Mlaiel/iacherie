"""MongoDB Collections Management
import asyncio

==============================

Advanced collection management for the Ainflue platform including collection
creation, validation, schema management, and data operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import json

try:
    import motor.motor_asyncio
    import pymongo
    from pymongo import IndexModel
    from pymongo.errors import CollectionInvalid, OperationFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # Create mock classes to prevent NameError
    class motor:
    """motor: class implementation"""
        class motor_asyncio:
    """motor_asyncio: class implementation"""
            pass
    class pymongo:
    """pymongo: class implementation"""
        pass
    class IndexModel:
    """IndexModel: class implementation"""
        pass

from .connection import MongoDBConnection, get_connection

logger = logging.getLogger(__name__)

@dataclass
class CollectionSchema:
    """MongoDB collection schema definition."""
    name: str
    validator: Optional[Dict[str, Any]] = None
    validation_level: str = "strict"  # strict, moderate, off
    validation_action: str = "error"  # error, warn
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    capped: bool = False
    max_size: Optional[int] = None
    max_documents: Optional[int] = None
    time_series: Optional[Dict[str, Any]] = None

class MongoDBCollectionManager:
    """MongoDB collection management with schema validation."""
    
    def __init__(self, connection -> None: Optional[MongoDBConnection] = None) -> None:
        """Initialize collection manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB dependencies not available")
        
        self.connection = connection or get_connection()
        self._collections_cache: Dict[str, Any] = {}
        
    async def create_collection(self, schema: CollectionSchema) -> bool:
        """Create collection with schema validation."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            database = self.connection.database
            
            # Check if collection already exists
            if schema.name in await database.list_collection_names():
                logger.info(f"Collection {schema.name} already exists")
                return True
            
            # Build collection options
            options = {}
            
            if schema.validator:
                options["validator"] = schema.validator
                options["validationLevel"] = schema.validation_level
                options["validationAction"] = schema.validation_action
            
            if schema.capped:
                options["capped"] = True
                if schema.max_size:
                    options["size"] = schema.max_size
                if schema.max_documents:
                    options["max"] = schema.max_documents
            
            if schema.time_series:
                options["timeseries"] = schema.time_series
            
            # Create collection
            await database.create_collection(schema.name, **options)
            
            # Create indexes if specified
            if schema.indexes:
                collection = database[schema.name]
                index_models = []
                for index_spec in schema.indexes:
                    index_models.append(IndexModel(**index_spec))
                await collection.create_indexes(index_models)
            
            logger.info(f"Successfully created collection: {schema.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {schema.name}: {e}")
            return False
    
    async def drop_collection(self, collection_name: str) -> bool:
        """Drop a collection."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            await self.connection.database.drop_collection(collection_name)
            
            # Remove from cache
            self._collections_cache.pop(collection_name, None)
            
            logger.info(f"Successfully dropped collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop collection {collection_name}: {e}")
            return False
    
    async def get_collection(self, collection_name -> None: str) -> None:
        """Get collection instance with caching."""
        if collection_name in self._collections_cache:
            return self._collections_cache[collection_name]
        
        if not self.connection.is_connected:
            await self.connection.connect()
        
        collection = self.connection.database[collection_name]
        self._collections_cache[collection_name] = collection
        return collection
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections with metadata."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collections = []
            async for collection_info in self.connection.database.list_collections():
                collections.append(collection_info)
            
            return collections
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            collection = await self.get_collection(collection_name)
            stats = await self.connection.database.command("collStats", collection_name)
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats for {collection_name}: {e}")
            return {}
    
    async def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """Insert a single document."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document in {collection_name}: {e}")
            return None
    
    async def insert_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Failed to insert documents in {collection_name}: {e}")
            return []
    
    async def find_document(self, collection_name: str, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        try:
            collection = await self.get_collection(collection_name)
            document = await collection.find_one(filter_query)
            return document
        except Exception as e:
            logger.error(f"Failed to find document in {collection_name}: {e}")
            return None
    
    async def find_documents(
        self, 
        collection_name: str, 
        filter_query: Dict[str, Any] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents."""
        try:
            collection = await self.get_collection(collection_name)
            cursor = collection.find(filter_query or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = []
            async for doc in cursor:
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to find documents in {collection_name}: {e}")
            return []
    
    async def update_document(
        self, 
        collection_name: str, 
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update a single document."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.update_one(filter_query, update_data, upsert=upsert)
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            return False
    
    async def update_documents(
        self, 
        collection_name: str, 
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any]
    ) -> int:
        """Update multiple documents."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.update_many(filter_query, update_data)
            return result.modified_count
        except Exception as e:
            logger.error(f"Failed to update documents in {collection_name}: {e}")
            return 0
    
    async def delete_document(self, collection_name: str, filter_query: Dict[str, Any]) -> bool:
        """Delete a single document."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.delete_one(filter_query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document in {collection_name}: {e}")
            return False
    
    async def delete_documents(self, collection_name: str, filter_query: Dict[str, Any]) -> int:
        """Delete multiple documents."""
        try:
            collection = await self.get_collection(collection_name)
            result = await collection.delete_many(filter_query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to delete documents in {collection_name}: {e}")
            return 0
    
    async def count_documents(self, collection_name: str, filter_query: Dict[str, Any] = None) -> int:
        """Count documents matching filter."""
        try:
            collection = await self.get_collection(collection_name)
            count = await collection.count_documents(filter_query or {})
            return count
        except Exception as e:
            logger.error(f"Failed to count documents in {collection_name}: {e}")
            return 0
    
    async def aggregate(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        try:
            collection = await self.get_collection(collection_name)
            results = []
            async for doc in collection.aggregate(pipeline):
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"Failed to execute aggregation in {collection_name}: {e}")
            return []

# Global collection manager instance
_default_manager: Optional[MongoDBCollectionManager] = None

def get_collection_manager(connection: Optional[MongoDBConnection] = None) -> MongoDBCollectionManager:
    """Get or create default collection manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = MongoDBCollectionManager(connection)
    return _default_manager

# Predefined schemas for Ainflue platform collections
AINFLUE_SCHEMAS = {
    "users": CollectionSchema(
        name="users",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "email", "username", "created_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "username": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        indexes=[
            {"keys": [("user_id", 1)], "unique": True},
            {"keys": [("email", 1)], "unique": True},
            {"keys": [("username", 1)], "unique": True}
        ]
    ),
    "media_content": CollectionSchema(
        name="media_content",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["content_id", "user_id", "content_type", "created_at"],
                "properties": {
                    "content_id": {"bsonType": "string"},
                    "user_id": {"bsonType": "string"},
                    "content_type": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
        },
        indexes=[
            {"keys": [("content_id", 1)], "unique": True},
            {"keys": [("user_id", 1)]},
            {"keys": [("content_type", 1)]},
            {"keys": [("created_at", -1)]}
        ]
    )
}

# Export main classes and functions
__all__ = [
    'CollectionSchema',
    'MongoDBCollectionManager',
    'get_collection_manager',
    'AINFLUE_SCHEMAS'
]