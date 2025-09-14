"""MongoDB Indexing Management
import asyncio

===========================

Advanced indexing utilities for optimal query performance in the Ainflue platform.
Provides index creation, monitoring, optimization, and performance analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

try:
    import motor.motor_asyncio
    import pymongo
    from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, HASHED, GEO2D, GEOSPHERE
    from pymongo.errors import OperationFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # Create mock constants and classes to prevent NameError
    ASCENDING = 1
    DESCENDING = -1
    TEXT = "text"
    HASHED = "hashed"
    GEO2D = "2d"
    GEOSPHERE = "2dsphere"
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
class IndexDefinition:
    """MongoDB index definition."""
    name: str
    keys: List[Tuple[str, Union[int, str]]]
    unique: bool = False
    sparse: bool = False
    background: bool = True
    partial_filter: Optional[Dict[str, Any]] = None
    expire_after_seconds: Optional[int] = None
    text_weights: Optional[Dict[str, int]] = None
    collation: Optional[Dict[str, Any]] = None

@dataclass
class IndexUsageStats:
    """Index usage statistics."""
    name: str
    accesses: int
    since: datetime
    collection: str
    size_bytes: int
    key_pattern: Dict[str, Any]

class MongoDBIndexManager:
    """MongoDB index management and optimization."""
    
    def __init__(self, connection -> None: Optional[MongoDBConnection] = None) -> None:
        """Initialize index manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB dependencies not available")
        
        self.connection = connection or get_connection()
        
    async def create_index(self, collection_name: str, index_def: IndexDefinition) -> bool:
        """Create a single index."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            
            # Build index options
            options = {
                "name": index_def.name,
                "unique": index_def.unique,
                "sparse": index_def.sparse,
                "background": index_def.background
            }
            
            if index_def.partial_filter:
                options["partialFilterExpression"] = index_def.partial_filter
            
            if index_def.expire_after_seconds is not None:
                options["expireAfterSeconds"] = index_def.expire_after_seconds
            
            if index_def.text_weights:
                options["weights"] = index_def.text_weights
            
            if index_def.collation:
                options["collation"] = index_def.collation
            
            # Create index
            await collection.create_index(index_def.keys, **options)
            
            logger.info(f"Created index {index_def.name} on {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index {index_def.name} on {collection_name}: {e}")
            return False
    
    async def create_indexes(self, collection_name: str, index_defs: List[IndexDefinition]) -> int:
        """Create multiple indexes."""
        success_count = 0
        
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            index_models = []
            
            for index_def in index_defs:
                options = {
                    "name": index_def.name,
                    "unique": index_def.unique,
                    "sparse": index_def.sparse,
                    "background": index_def.background
                }
                
                if index_def.partial_filter:
                    options["partialFilterExpression"] = index_def.partial_filter
                
                if index_def.expire_after_seconds is not None:
                    options["expireAfterSeconds"] = index_def.expire_after_seconds
                
                if index_def.text_weights:
                    options["weights"] = index_def.text_weights
                
                if index_def.collation:
                    options["collation"] = index_def.collation
                
                index_models.append(IndexModel(index_def.keys, **options))
            
            # Create all indexes
            await collection.create_indexes(index_models)
            success_count = len(index_defs)
            
            logger.info(f"Created {success_count} indexes on {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to create indexes on {collection_name}: {e}")
        
        return success_count
    
    async def drop_index(self, collection_name: str, index_name: str) -> bool:
        """Drop a specific index."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            await collection.drop_index(index_name)
            
            logger.info(f"Dropped index {index_name} from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop index {index_name} from {collection_name}: {e}")
            return False
    
    async def drop_all_indexes(self, collection_name: str) -> bool:
        """Drop all indexes except _id."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            await collection.drop_indexes()
            
            logger.info(f"Dropped all indexes from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop indexes from {collection_name}: {e}")
            return False
    
    async def list_indexes(self, collection_name: str) -> List[Dict[str, Any]]:
        """List all indexes for a collection."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            indexes = []
            
            async for index_info in collection.list_indexes():
                indexes.append(index_info)
            
            return indexes
            
        except Exception as e:
            logger.error(f"Failed to list indexes for {collection_name}: {e}")
            return []
    
    async def get_index_stats(self, collection_name: str) -> List[IndexUsageStats]:
        """Get index usage statistics."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            # Get index stats using $indexStats aggregation
            collection = self.connection.database[collection_name]
            pipeline = [{"$indexStats": {}}]
            
            stats = []
            async for stat_doc in collection.aggregate(pipeline):
                stats.append(IndexUsageStats(
                    name=stat_doc["name"],
                    accesses=stat_doc["accesses"]["ops"],
                    since=stat_doc["accesses"]["since"],
                    collection=collection_name,
                    size_bytes=stat_doc.get("size", 0),
                    key_pattern=stat_doc["key"]
                ))
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get index stats for {collection_name}: {e}")
            return []
    
    async def analyze_query_performance(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query performance and index usage."""
        try:
            if not self.connection.is_connected:
                await self.connection.connect()
            
            collection = self.connection.database[collection_name]
            
            # Execute explain to get query plan
            explain_result = await collection.find(query).explain("executionStats")
            
            # Extract relevant performance metrics
            execution_stats = explain_result.get("executionStats", {})
            winning_plan = explain_result.get("queryPlanner", {}).get("winningPlan", {})
            
            analysis = {
                "total_docs_examined": execution_stats.get("totalDocsExamined", 0),
                "total_keys_examined": execution_stats.get("totalKeysExamined", 0),
                "execution_time_ms": execution_stats.get("executionTimeMillis", 0),
                "docs_returned": execution_stats.get("totalDocsReturned", 0),
                "index_used": winning_plan.get("inputStage", {}).get("indexName"),
                "stage": winning_plan.get("stage"),
                "is_covered_query": execution_stats.get("totalDocsExamined", 0) == 0,
                "selectivity": self._calculate_selectivity(execution_stats)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze query performance for {collection_name}: {e}")
            return {}
    
    def _calculate_selectivity(self, execution_stats: Dict[str, Any]) -> float:
        """Calculate query selectivity (0-1, where 1 is most selective)."""
        docs_examined = execution_stats.get("totalDocsExamined", 0)
        docs_returned = execution_stats.get("totalDocsReturned", 0)
        
        if docs_examined == 0:
            return 1.0  # Covered query - very selective
        
        return docs_returned / docs_examined if docs_examined > 0 else 0.0
    
    async def suggest_indexes(self, collection_name: str, queries: List[Dict[str, Any]]) -> List[IndexDefinition]:
        """Suggest indexes based on query patterns."""
        suggestions = []
        
        try:
            for query in queries:
                # Analyze each query to suggest indexes
                analysis = await self.analyze_query_performance(collection_name, query)
                
                # If query performance is poor, suggest index
                if (analysis.get("execution_time_ms", 0) > 100 or 
                    analysis.get("selectivity", 1.0) < 0.1):
                    
                    # Extract fields from query for index suggestion
                    query_fields = self._extract_query_fields(query)
                    
                    if query_fields:
                        index_name = f"idx_{collection_name}_" + "_".join(query_fields)
                        index_keys = [(field, ASCENDING) for field in query_fields]
                        
                        suggestions.append(IndexDefinition(
                            name=index_name,
                            keys=index_keys,
                            background=True
                        ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest indexes for {collection_name}: {e}")
            return []
    
    def _extract_query_fields(self, query: Dict[str, Any]) -> List[str]:
        """Extract field names from query for index suggestions."""
        fields = []
        
        def extract_fields(obj, prefix="") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.startswith("$"):
                        continue  # Skip operators
                    
                    field_name = f"{prefix}.{key}" if prefix else key
                    
                    if isinstance(value, dict):
                        extract_fields(value, field_name)
                    else:
                        fields.append(field_name)
        
        extract_fields(query)
        return fields
    
    async def optimize_collection_indexes(self, collection_name: str) -> Dict[str, Any]:
        """Comprehensive index optimization for a collection."""
        try:
            # Get current indexes
            current_indexes = await self.list_indexes(collection_name)
            
            # Get index usage stats
            usage_stats = await self.get_index_stats(collection_name)
            
            # Identify unused indexes (except _id_)
            unused_indexes = [
                stat.name for stat in usage_stats 
                if stat.accesses == 0 and stat.name != "_id_"
            ]
            
            # Calculate total index size
            total_size = sum(stat.size_bytes for stat in usage_stats)
            
            optimization_report = {
                "collection": collection_name,
                "total_indexes": len(current_indexes),
                "unused_indexes": unused_indexes,
                "total_index_size_mb": total_size / (1024 * 1024),
                "recommendations": []
            }
            
            # Add recommendations
            if unused_indexes:
                optimization_report["recommendations"].append(
                    f"Consider dropping {len(unused_indexes)} unused indexes to save space"
                )
            
            if len(current_indexes) > 10:
                optimization_report["recommendations"].append(
                    "High number of indexes may impact write performance"
                )
            
            return optimization_report
            
        except Exception as e:
            logger.error(f"Failed to optimize indexes for {collection_name}: {e}")
            return {}

# Global index manager instance
_default_manager: Optional[MongoDBIndexManager] = None

def get_index_manager(connection: Optional[MongoDBConnection] = None) -> MongoDBIndexManager:
    """Get or create default index manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = MongoDBIndexManager(connection)
    return _default_manager

# Common index patterns for Ainflue platform
COMMON_INDEX_PATTERNS = {
    "user_lookup": IndexDefinition(
        name="idx_user_lookup",
        keys=[("user_id", ASCENDING)],
        background=True
    ),
    "email_unique": IndexDefinition(
        name="idx_email_unique",
        keys=[("email", ASCENDING)],
        unique=True,
        sparse=True
    ),
    "created_at_desc": IndexDefinition(
        name="idx_created_desc",
        keys=[("created_at", DESCENDING)],
        background=True
    ),
    "text_search": IndexDefinition(
        name="idx_text_search",
        keys=[("title", TEXT), ("content", TEXT), ("tags", TEXT)],
        text_weights={"title": 10, "content": 5, "tags": 2}
    ),
    "geospatial": IndexDefinition(
        name="idx_location_2dsphere",
        keys=[("location", GEOSPHERE)],
        background=True
    ),
    "ttl_expire": IndexDefinition(
        name="idx_ttl_expire",
        keys=[("expires_at", ASCENDING)],
        expire_after_seconds=0,  # Use document field value
        background=True
    )
}

# Export main classes and functions
__all__ = [
    'IndexDefinition',
    'IndexUsageStats',
    'MongoDBIndexManager',
    'get_index_manager',
    'COMMON_INDEX_PATTERNS',
    'ASCENDING',
    'DESCENDING',
    'TEXT',
    'HASHED',
    'GEO2D',
    'GEOSPHERE'
]