"""{{model_name}} MongoDB Model Template for Ainflue Platform
{{model_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from enum import Enum
import json
from bson import ObjectId
from bson.errors import InvalidId

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import DuplicateKeyError, ValidationError
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.json import pydantic_encoder

from core.config import get_settings
from core.database import get_mongodb_database
from utils.exceptions import DatabaseException, ValidationException
from monitoring.database_metrics import DatabaseMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DocumentStatus(Enum):
    """Document status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class IndexType(Enum):
    """MongoDB index types"""
    SINGLE = "single"
    COMPOUND = "compound"
    TEXT = "text"
    GEOSPATIAL = "geospatial"
    HASHED = "hashed"
    SPARSE = "sparse"
    UNIQUE = "unique"


class BaseMongoModel(BaseModel):
    """Base model for MongoDB documents"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, description="Document version for optimistic locking")
    status: DocumentStatus = Field(default=DocumentStatus.ACTIVE)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "version": 1,
                "status": "active",
                "metadata": {}
            }
        }
    
    @validator("created_at", "updated_at", pre=True)
    def validate_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    @root_validator(pre=True)
    def set_updated_at(cls, values):
        if "updated_at" not in values:
            values["updated_at"] = datetime.now(timezone.utc)
        return values


class {{model_name}}(BaseMongoModel):
    """{{model_description}} MongoDB document model"""
    
    # Core fields - customize based on your model
    name: str = Field(..., description="Name of the {{model_name_lower}}")
    description: Optional[str] = Field(None, description="Description of the {{model_name_lower}}")
    
    # Relationship fields
    owner_id: Optional[PyObjectId] = Field(None, description="Owner user ID")
    parent_id: Optional[PyObjectId] = Field(None, description="Parent document ID")
    
    # Search and categorization
    tags: List[str] = Field(default_factory=list, description="Document tags")
    categories: List[str] = Field(default_factory=list, description="Document categories")
    
    # Permissions and access
    is_public: bool = Field(default=False, description="Whether document is public")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="User/role permissions")
    
    # Analytics and metrics
    view_count: int = Field(default=0, description="Number of views")
    like_count: int = Field(default=0, description="Number of likes")
    share_count: int = Field(default=0, description="Number of shares")
    
    # Content-specific fields (customize as needed)
    content_type: Optional[str] = Field(None, description="Type of content")
    content_data: Dict[str, Any] = Field(default_factory=dict, description="Content data")
    
    # Audit fields
    created_by: Optional[PyObjectId] = Field(None, description="User who created this document")
    updated_by: Optional[PyObjectId] = Field(None, description="User who last updated this document")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Example {{model_name}}",
                "description": "This is an example {{model_name_lower}}",
                "owner_id": "507f1f77bcf86cd799439011",
                "tags": ["example", "template"],
                "categories": ["general"],
                "is_public": True,
                "content_type": "text",
                "content_data": {"text": "Example content"},
                "created_by": "507f1f77bcf86cd799439011"
            }
        }
    
    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return v.strip()
    
    @validator("tags", "categories")
    def validate_lists(cls, v):
        if v is None:
            return []
        # Remove duplicates and empty strings
        return list(set(filter(None, [item.strip() for item in v])))
    
    @validator("permissions")
    def validate_permissions(cls, v):
        if v is None:
            return {}
        # Ensure permissions are properly structured
        valid_permissions = {}
        for user_id, perms in v.items():
            if isinstance(perms, list):
                valid_permissions[user_id] = list(set(perms))
        return valid_permissions


class {{model_name}}Repository:
    """MongoDB repository for {{model_name}} documents"""
    
    def __init__(self, database: AsyncIOMotorDatabase, metrics_collector: Optional[DatabaseMetricsCollector] = None):
        self.database = database
        self.collection: AsyncIOMotorCollection = database[self._get_collection_name()]
        self.metrics_collector = metrics_collector or DatabaseMetricsCollector()
        self._indexes_created = False
    
    @classmethod
    def _get_collection_name(cls) -> str:
        """Get the collection name for this model"""
        return "{{collection_name}}"
    
    async def ensure_indexes(self):
        """Ensure database indexes are created"""
        if self._indexes_created:
            return
        
        indexes = [
            # Basic indexes
            IndexModel([("name", ASCENDING)], background=True),
            IndexModel([("status", ASCENDING)], background=True),
            IndexModel([("created_at", DESCENDING)], background=True),
            IndexModel([("updated_at", DESCENDING)], background=True),
            
            # Relationship indexes
            IndexModel([("owner_id", ASCENDING)], background=True),
            IndexModel([("parent_id", ASCENDING)], background=True),
            IndexModel([("created_by", ASCENDING)], background=True),
            
            # Search indexes
            IndexModel([("name", TEXT), ("description", TEXT)], background=True),
            IndexModel([("tags", ASCENDING)], background=True),
            IndexModel([("categories", ASCENDING)], background=True),
            
            # Compound indexes for common queries
            IndexModel([("owner_id", ASCENDING), ("status", ASCENDING)], background=True),
            IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], background=True),
            IndexModel([("is_public", ASCENDING), ("status", ASCENDING)], background=True),
            
            # Unique constraints
            IndexModel([("name", ASCENDING), ("owner_id", ASCENDING)], unique=True, background=True),
        ]
        
        try:
            await self.collection.create_indexes(indexes)
            self._indexes_created = True
            logger.info(f"Created indexes for collection {self._get_collection_name()}")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise DatabaseException(f"Index creation failed: {e}")
    
    async def create(self, document: {{model_name}}, user_id: Optional[str] = None) -> {{model_name}}:
        """Create a new document"""
        start_time = datetime.now()
        
        try:
            await self.ensure_indexes()
            
            # Set audit fields
            if user_id:
                document.created_by = PyObjectId(user_id)
                document.updated_by = PyObjectId(user_id)
            
            # Convert to dict for insertion
            doc_dict = document.dict(by_alias=True, exclude_none=False)
            
            # Insert document
            result = await self.collection.insert_one(doc_dict)
            
            # Fetch the created document
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="create",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=True
            )
            
            return {{model_name}}(**created_doc)
            
        except DuplicateKeyError as e:
            await self.metrics_collector.record_operation(
                operation="create",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            raise DatabaseException(f"Document with this name already exists: {e}")
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="create",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error creating document: {e}")
            raise DatabaseException(f"Failed to create document: {e}")
    
    async def get_by_id(self, document_id: str, user_id: Optional[str] = None) -> Optional[{{model_name}}]:
        """Get document by ID"""
        start_time = datetime.now()
        
        try:
            if not ObjectId.is_valid(document_id):
                return None
            
            query = {"_id": ObjectId(document_id), "status": {"$ne": DocumentStatus.DELETED.value}}
            
            # Add permission check if user_id provided
            if user_id:
                query = await self._add_permission_filter(query, user_id)
            
            doc = await self.collection.find_one(query)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="get_by_id",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=doc is not None
            )
            
            return {{model_name}}(**doc) if doc else None
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="get_by_id",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error getting document by ID {document_id}: {e}")
            return None
    
    async def get_by_name(self, name: str, owner_id: Optional[str] = None) -> Optional[{{model_name}}]:
        """Get document by name"""
        start_time = datetime.now()
        
        try:
            query = {"name": name, "status": {"$ne": DocumentStatus.DELETED.value}}
            
            if owner_id:
                if ObjectId.is_valid(owner_id):
                    query["owner_id"] = ObjectId(owner_id)
                else:
                    return None
            
            doc = await self.collection.find_one(query)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="get_by_name",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=doc is not None
            )
            
            return {{model_name}}(**doc) if doc else None
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="get_by_name",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error getting document by name {name}: {e}")
            return None
    
    async def update(
        self, 
        document_id: str, 
        updates: Dict[str, Any], 
        user_id: Optional[str] = None,
        optimistic_lock: bool = True
    ) -> Optional[{{model_name}}]:
        """Update document"""
        start_time = datetime.now()
        
        try:
            if not ObjectId.is_valid(document_id):
                return None
            
            # Build update query
            query = {"_id": ObjectId(document_id), "status": {"$ne": DocumentStatus.DELETED.value}}
            
            # Add permission check
            if user_id:
                query = await self._add_permission_filter(query, user_id)
            
            # Build update document
            update_doc = {
                "$set": {
                    **updates,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
            
            # Add audit fields
            if user_id:
                update_doc["$set"]["updated_by"] = ObjectId(user_id)
            
            # Optimistic locking
            if optimistic_lock and "version" in updates:
                query["version"] = updates["version"]
                update_doc["$inc"] = {"version": 1}
                del update_doc["$set"]["version"]
            
            # Perform update
            result = await self.collection.find_one_and_update(
                query,
                update_doc,
                return_document=True
            )
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="update",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=result is not None
            )
            
            return {{model_name}}(**result) if result else None
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="update",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error updating document {document_id}: {e}")
            return None
    
    async def delete(self, document_id: str, user_id: Optional[str] = None, soft_delete: bool = True) -> bool:
        """Delete document (soft or hard delete)"""
        start_time = datetime.now()
        
        try:
            if not ObjectId.is_valid(document_id):
                return False
            
            query = {"_id": ObjectId(document_id)}
            
            # Add permission check
            if user_id:
                query = await self._add_permission_filter(query, user_id)
            
            if soft_delete:
                # Soft delete - mark as deleted
                update_doc = {
                    "$set": {
                        "status": DocumentStatus.DELETED.value,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
                
                if user_id:
                    update_doc["$set"]["updated_by"] = ObjectId(user_id)
                
                result = await self.collection.update_one(query, update_doc)
                success = result.modified_count > 0
            else:
                # Hard delete - remove document
                result = await self.collection.delete_one(query)
                success = result.deleted_count > 0
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="delete",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=success
            )
            
            return success
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="delete",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List documents with pagination and filtering"""
        start_time = datetime.now()
        
        try:
            # Build query
            query = {"status": {"$ne": DocumentStatus.DELETED.value}}
            
            # Add filters
            if filters:
                query.update(await self._build_filters(filters))
            
            # Add permission filter
            if user_id:
                query = await self._add_permission_filter(query, user_id)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Get documents
            cursor = self.collection.find(query).sort(sort_by, sort_order).skip(skip).limit(page_size)
            documents = await cursor.to_list(length=page_size)
            
            # Convert to model instances
            items = [{{model_name}}(**doc) for doc in documents]
            
            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size
            
            result = {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="list",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="list",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error listing documents: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }
    
    async def search(
        self,
        search_query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Full-text search documents"""
        start_time = datetime.now()
        
        try:
            # Build search query
            query = {
                "$text": {"$search": search_query},
                "status": {"$ne": DocumentStatus.DELETED.value}
            }
            
            # Add filters
            if filters:
                query.update(await self._build_filters(filters))
            
            # Add permission filter
            if user_id:
                query = await self._add_permission_filter(query, user_id)
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Get documents with text score
            cursor = self.collection.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(page_size)
            
            documents = await cursor.to_list(length=page_size)
            
            # Convert to model instances
            items = [{{model_name}}(**doc) for doc in documents]
            
            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size
            
            result = {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "search_query": search_query
            }
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="search",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="search",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error searching documents: {e}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False,
                "search_query": search_query
            }
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        start_time = datetime.now()
        
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="aggregate",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=True
            )
            
            return results
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="aggregate",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error executing aggregation: {e}")
            return []
    
    async def bulk_create(self, documents: List[{{model_name}}], user_id: Optional[str] = None) -> List[{{model_name}}]:
        """Bulk create documents"""
        start_time = datetime.now()
        
        try:
            await self.ensure_indexes()
            
            # Prepare documents for insertion
            docs_to_insert = []
            for doc in documents:
                if user_id:
                    doc.created_by = PyObjectId(user_id)
                    doc.updated_by = PyObjectId(user_id)
                
                docs_to_insert.append(doc.dict(by_alias=True, exclude_none=False))
            
            # Insert documents
            result = await self.collection.insert_many(docs_to_insert, ordered=False)
            
            # Fetch created documents
            created_docs = await self.collection.find(
                {"_id": {"$in": result.inserted_ids}}
            ).to_list(length=None)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_collector.record_operation(
                operation="bulk_create",
                collection=self._get_collection_name(),
                processing_time=processing_time,
                success=True
            )
            
            return [{{model_name}}(**doc) for doc in created_docs]
            
        except Exception as e:
            await self.metrics_collector.record_operation(
                operation="bulk_create",
                collection=self._get_collection_name(),
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False
            )
            logger.error(f"Error bulk creating documents: {e}")
            raise DatabaseException(f"Bulk create failed: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            stats = await self.database.command("collStats", self._get_collection_name())
            
            # Get document count by status
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_counts = await self.aggregate(status_pipeline)
            
            # Get recent activity
            recent_pipeline = [
                {"$match": {"created_at": {"$gte": datetime.now() - timedelta(days=7)}}},
                {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            recent_activity = await self.aggregate(recent_pipeline)
            
            return {
                "collection_name": self._get_collection_name(),
                "total_documents": stats.get("count", 0),
                "storage_size": stats.get("storageSize", 0),
                "average_object_size": stats.get("avgObjSize", 0),
                "total_index_size": stats.get("totalIndexSize", 0),
                "status_counts": {item["_id"]: item["count"] for item in status_counts},
                "recent_activity": recent_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def _add_permission_filter(self, query: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add permission-based filtering to query"""
        if not ObjectId.is_valid(user_id):
            return query
        
        user_obj_id = ObjectId(user_id)
        
        # User can access documents they own or public documents
        permission_filter = {
            "$or": [
                {"owner_id": user_obj_id},
                {"created_by": user_obj_id},
                {"is_public": True},
                {f"permissions.{user_id}": {"$exists": True}}
            ]
        }
        
        if "$and" in query:
            query["$and"].append(permission_filter)
        else:
            query = {"$and": [query, permission_filter]}
        
        return query
    
    async def _build_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query from filters"""
        query = {}
        
        for key, value in filters.items():
            if key == "search":
                # Text search
                if value:
                    query["$text"] = {"$search": value}
            elif key == "tags":
                # Array contains
                if isinstance(value, list):
                    query["tags"] = {"$in": value}
                else:
                    query["tags"] = value
            elif key == "categories":
                # Array contains
                if isinstance(value, list):
                    query["categories"] = {"$in": value}
                else:
                    query["categories"] = value
            elif key == "date_from":
                # Date range
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$gte"] = value
            elif key == "date_to":
                # Date range
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$lte"] = value
            elif key.endswith("_id") and ObjectId.is_valid(str(value)):
                # ObjectId fields
                query[key] = ObjectId(value)
            else:
                # Direct match
                query[key] = value
        
        return query


# Dependency for FastAPI
async def get_{{model_name_lower}}_repository() -> {{model_name}}Repository:
    """Get {{model_name}} repository instance"""
    database = await get_mongodb_database()
    return {{model_name}}Repository(database)


# Template usage example
def create_{{model_name_lower}}_model_example():
    """Example of how to create and use the {{model_name}} model"""
    
    # Create a document
    document = {{model_name}}(
        name="Example Document",
        description="This is an example document",
        tags=["example", "template"],
        categories=["general"],
        is_public=True,
        content_type="text",
        content_data={"text": "Example content"}
    )
    
    return document


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "mongodb_model_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive MongoDB model with repository pattern",
    "required_parameters": [
        "model_name",
        "model_description",
        "model_name_lower",
        "collection_name",
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_fields",
        "custom_indexes",
        "custom_validators",
        "custom_methods"
    ],
    "dependencies": [
        "motor>=3.3.0",
        "pymongo>=4.5.0",
        "pydantic>=2.5.0",
        "bson>=0.5.10"
    ],
    "features": [
        "Async MongoDB operations",
        "Repository pattern",
        "Document validation",
        "Automatic indexing",
        "Soft delete support",
        "Optimistic locking",
        "Full-text search",
        "Aggregation support",
        "Bulk operations",
        "Permission-based filtering",
        "Audit trails",
        "Performance metrics"
    ]
}