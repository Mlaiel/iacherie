"""Conversation Memory Storage Systems - Multi-Layer Storage Architecture

Enterprise storage systems for conversation memory including long-term database
storage, short-term caching, and vector storage for semantic search capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING: Unauthorized use strictly prohibited ⚠️
Contact: mlaiel@live.de
"""
import asyncio
import logging
import pickle
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from abc import ABC, abstractmethod

# Database and caching
import redis.asyncio as aioredis
from sqlalchemy import select, insert, update, delete, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Vector storage and AI
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Internal imports
from backend.core.database import get_async_session
from backend.core.config import settings
from backend.core.security import EncryptionManager
from backend.utils.cache import CacheManager
from backend.utils.metrics import MetricsCollector

from .models import (
    ConversationRecord,
    MemoryEntry,
    ConversationStatus,
    MemoryType
)

logger = logging.getLogger(__name__)


class StorageInterface(ABC):
    """Abstract interface for storage systems"""    
    @abstractmethod
    async def store(self, data: Any) -> bool:
        """Store data"""        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key"""        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data by key"""        pass
    
    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> List[Any]:
        """Search data"""        pass


class LongTermMemory(StorageInterface):
    """    PostgreSQL-based long-term memory storage
    
    Provides persistent storage for conversation records with full ACID
    compliance, indexing, and complex query capabilities.
    """    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.metrics = MetricsCollector("long_term_memory")
        self.connection_pool = None
        
        logger.info("LongTermMemory storage initialized")
    
    async def initialize(self):
        """Initialize database connections and indexes"""        try:
            # Create any missing indexes
            await self._ensure_indexes()
            logger.info("LongTermMemory database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize LongTermMemory: {e}")
            raise
    
    async def store(self, record: ConversationRecord) -> bool:
        """        Store conversation record in PostgreSQL
        
        Args:
            record: ConversationRecord to store
            
        Returns:
            Success status
        """        try:
            async with get_async_session() as session:
                # Encrypt conversation data if needed
                if record.conversation_data and not record.is_encrypted:
                    record.encrypt_content(self.encryption_manager)
                
                # Extract text for full-text search
                if record.conversation_data:
                    record.raw_content = self._extract_searchable_text(
                        record.conversation_data
                    )
                
                # Insert or update record
                existing = await session.get(ConversationRecord, record.id)
                if existing:
                    # Update existing record
                    for key, value in record.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    # Insert new record
                    session.add(record)
                
                await session.commit()
                
                self.metrics.increment("records_stored")
                logger.debug(f"Stored conversation record: {record.conversation_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to store conversation record: {e}")
            self.metrics.increment("storage_errors")
            return False
    
    async def retrieve(self, conversation_id: str) -> Optional[ConversationRecord]:
        """        Retrieve conversation record by ID
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationRecord or None
        """        try:
            async with get_async_session() as session:
                query = select(ConversationRecord).where(
                    ConversationRecord.conversation_id == conversation_id
                )
                
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                
                if record and record.is_encrypted:
                    # Decrypt content for use
                    record.decrypt_content(self.encryption_manager)
                
                self.metrics.increment("records_retrieved")
                return record
                
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            self.metrics.increment("retrieval_errors")
            return None
    
    async def get(self, conversation_id: str) -> Optional[ConversationRecord]:
        """Alias for retrieve method"""        return await self.retrieve(conversation_id)
    
    async def delete(self, conversation_id: str) -> bool:
        """        Delete conversation record
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Success status
        """        try:
            async with get_async_session() as session:
                query = delete(ConversationRecord).where(
                    ConversationRecord.conversation_id == conversation_id
                )
                
                result = await session.execute(query)
                await session.commit()
                
                deleted = result.rowcount > 0
                if deleted:
                    self.metrics.increment("records_deleted")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            self.metrics.increment("deletion_errors")
            return False
    
    async def search(self, query: Dict[str, Any]) -> List[ConversationRecord]:
        """        Search conversation records with complex queries
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation records
        """        try:
            async with get_async_session() as session:
                # Build query based on parameters
                db_query = select(ConversationRecord)
                
                # User filter
                if "user_id" in query:
                    db_query = db_query.where(
                        ConversationRecord.user_id == query["user_id"]
                    )
                
                # Content type filter
                if "content_type" in query:
                    db_query = db_query.where(
                        ConversationRecord.content_type == query["content_type"]
                    )
                
                # Status filter
                if "status" in query:
                    db_query = db_query.where(
                        ConversationRecord.status == query["status"]
                    )
                
                # Date range filter
                if "start_date" in query:
                    db_query = db_query.where(
                        ConversationRecord.timestamp >= query["start_date"]
                    )
                
                if "end_date" in query:
                    db_query = db_query.where(
                        ConversationRecord.timestamp <= query["end_date"]
                    )
                
                # Text search
                if "text_query" in query:
                    db_query = db_query.where(
                        ConversationRecord.raw_content.contains(query["text_query"])
                    )
                
                # Sentiment filter
                if "min_sentiment" in query:
                    db_query = db_query.where(
                        ConversationRecord.sentiment_score >= query["min_sentiment"]
                    )
                
                # Priority filter
                if "min_priority" in query:
                    db_query = db_query.where(
                        ConversationRecord.priority_score >= query["min_priority"]
                    )
                
                # Ordering
                order_by = query.get("order_by", "timestamp")
                order_dir = query.get("order_dir", "desc")
                
                if order_dir.lower() == "desc":
                    db_query = db_query.order_by(getattr(ConversationRecord, order_by).desc())
                else:
                    db_query = db_query.order_by(getattr(ConversationRecord, order_by))
                
                # Pagination
                limit = query.get("limit", 50)
                offset = query.get("offset", 0)
                
                db_query = db_query.limit(limit).offset(offset)
                
                # Execute query
                result = await session.execute(db_query)
                records = result.scalars().all()
                
                # Decrypt records if needed
                decrypted_records = []
                for record in records:
                    if record.is_encrypted:
                        record.decrypt_content(self.encryption_manager)
                    decrypted_records.append(record)
                
                self.metrics.increment("searches_performed")
                return decrypted_records
                
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            self.metrics.increment("search_errors")
            return []
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        content_type: Optional[str] = None
    ) -> List[ConversationRecord]:
        """        Get paginated conversations for a user
        
        Args:
            user_id: User identifier
            limit: Maximum records to return
            offset: Records to skip
            content_type: Optional content type filter
            
        Returns:
            List of conversation records
        """        query_params = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
            "order_by": "timestamp",
            "order_dir": "desc"
        }
        
        if content_type:
            query_params["content_type"] = content_type
        
        return await self.search(query_params)
    
    async def cleanup_before_date(self, cutoff_date: datetime) -> int:
        """        Clean up records before a specific date
        
        Args:
            cutoff_date: Date before which to delete records
            
        Returns:
            Number of records deleted
        """        try:
            async with get_async_session() as session:
                # First, archive records that are not already archived
                archive_query = update(ConversationRecord).where(
                    and_(
                        ConversationRecord.timestamp < cutoff_date,
                        ConversationRecord.status != ConversationStatus.ARCHIVED.value
                    )
                ).values(
                    status=ConversationStatus.ARCHIVED.value,
                    archived_at=datetime.now(timezone.utc)
                )
                
                await session.execute(archive_query)
                
                # Then delete very old archived records (beyond retention)
                old_cutoff = cutoff_date - timedelta(days=30)  # Additional grace period
                
                delete_query = delete(ConversationRecord).where(
                    and_(
                        ConversationRecord.timestamp < old_cutoff,
                        ConversationRecord.status == ConversationStatus.ARCHIVED.value
                    )
                )
                
                result = await session.execute(delete_query)
                await session.commit()
                
                deleted_count = result.rowcount
                self.metrics.gauge("records_cleaned", deleted_count)
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup records before {cutoff_date}: {e}")
            self.metrics.increment("cleanup_errors")
            return 0
    
    def _extract_searchable_text(self, conversation_data: Dict[str, Any]) -> str:
        """Extract searchable text from conversation data"""        text_parts = []
        
        if isinstance(conversation_data, dict):
            if "messages" in conversation_data:
                for message in conversation_data["messages"]:
                    if isinstance(message, dict) and "content" in message:
                        text_parts.append(str(message["content"]))
            
            # Extract other text fields
            for key in ["title", "description", "summary", "notes"]:
                if key in conversation_data:
                    text_parts.append(str(conversation_data[key]))
        
        return " ".join(text_parts)
    
    async def _ensure_indexes(self):
        """Ensure required database indexes exist"""        try:
            async with get_async_session() as session:
                # Create indexes for common queries
                indexes = [
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_id ON conversation_records(user_id);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_content_type ON conversation_records(content_type);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_timestamp ON conversation_records(timestamp);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_status ON conversation_records(status);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_priority ON conversation_records(priority_score);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_timestamp ON conversation_records(user_id, timestamp);",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_text_search ON conversation_records USING gin(to_tsvector('english', raw_content));"
                ]
                
                for index_sql in indexes:
                    try:
                        await session.execute(text(index_sql))
                        await session.commit()
                    except Exception as e:
                        # Index might already exist
                        logger.debug(f"Index creation info: {e}")
                        await session.rollback()
                
        except Exception as e:
            logger.error(f"Failed to ensure indexes: {e}")


class ShortTermMemory(StorageInterface):
    """    Redis-based short-term memory storage
    
    Provides fast caching for frequently accessed conversations
    and temporary storage for active conversations.
    """    
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.metrics = MetricsCollector("short_term_memory")
        self.redis_client = None
        
        logger.info("ShortTermMemory storage initialized")
    
    async def initialize(self):
        """Initialize Redis connection"""        try:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=False  # We'll handle encoding for pickle
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("ShortTermMemory Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to initialize ShortTermMemory: {e}")
            raise
    
    async def store(self, record: ConversationRecord) -> bool:
        """        Store conversation record in Redis cache
        
        Args:
            record: ConversationRecord to cache
            
        Returns:
            Success status
        """        try:
            if not self.redis_client:
                await self.initialize()
            
            # Serialize record
            key = f"conversation:{record.conversation_id}"
            serialized_data = pickle.dumps(record)
            
            # Store with TTL
            await self.redis_client.setex(
                key,
                self.ttl_seconds,
                serialized_data
            )
            
            # Also store user conversation list
            await self._update_user_conversation_list(
                record.user_id,
                record.conversation_id
            )
            
            self.metrics.increment("records_cached")
            logger.debug(f"Cached conversation: {record.conversation_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache conversation {record.conversation_id}: {e}")
            self.metrics.increment("cache_errors")
            return False
    
    async def retrieve(self, conversation_id: str) -> Optional[ConversationRecord]:
        """        Retrieve conversation record from cache
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationRecord or None
        """        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"conversation:{conversation_id}"
            serialized_data = await self.redis_client.get(key)
            
            if serialized_data:
                record = pickle.loads(serialized_data)
                self.metrics.increment("cache_hits")
                return record
            else:
                self.metrics.increment("cache_misses")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve cached conversation {conversation_id}: {e}")
            self.metrics.increment("cache_retrieval_errors")
            return None
    
    async def get(self, conversation_id: str) -> Optional[ConversationRecord]:
        """Alias for retrieve method"""        return await self.retrieve(conversation_id)
    
    async def delete(self, conversation_id: str) -> bool:
        """        Delete conversation record from cache
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Success status
        """        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"conversation:{conversation_id}"
            deleted = await self.redis_client.delete(key)
            
            if deleted:
                self.metrics.increment("records_deleted_from_cache")
            
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cached conversation {conversation_id}: {e}")
            self.metrics.increment("cache_deletion_errors")
            return False
    
    async def search(self, query: Dict[str, Any]) -> List[ConversationRecord]:
        """        Search cached conversations (limited search capabilities)
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation records
        """        try:
            if not self.redis_client:
                await self.initialize()
            
            results = []
            
            # Simple search by user_id (most common case)
            if "user_id" in query:
                user_conversations = await self._get_user_conversation_list(
                    query["user_id"]
                )
                
                # Retrieve each conversation and filter
                for conversation_id in user_conversations:
                    record = await self.retrieve(conversation_id)
                    if record and self._matches_query(record, query):
                        results.append(record)
            
            # Apply ordering and limits
            results = self._sort_and_limit_results(results, query)
            
            self.metrics.increment("cache_searches")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search cached conversations: {e}")
            self.metrics.increment("cache_search_errors")
            return []
    
    async def cleanup_expired(self) -> int:
        """        Clean up expired cache entries
        
        Returns:
            Number of entries cleaned
        """        try:
            if not self.redis_client:
                await self.initialize()
            
            # Redis automatically handles TTL expiration
            # We just need to clean up our tracking lists
            
            cleaned_count = 0
            
            # Clean up user conversation lists
            user_list_pattern = "user_conversations:*"
            async for key in self.redis_client.scan_iter(match=user_list_pattern):
                # Remove expired conversation IDs from user lists
                conversation_ids = await self.redis_client.lrange(key, 0, -1)
                
                for conv_id in conversation_ids:
                    conv_key = f"conversation:{conv_id.decode()}"
                    exists = await self.redis_client.exists(conv_key)
                    
                    if not exists:
                        # Remove from user list
                        await self.redis_client.lrem(key, 0, conv_id)
                        cleaned_count += 1
            
            self.metrics.gauge("cache_entries_cleaned", cleaned_count)
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache entries: {e}")
            self.metrics.increment("cache_cleanup_errors")
            return 0
    
    async def _update_user_conversation_list(self, user_id: str, conversation_id: str):
        """Update user's conversation list for faster lookup"""        try:
            key = f"user_conversations:{user_id}"
            
            # Add to front of list (most recent first)
            await self.redis_client.lpush(key, conversation_id)
            
            # Keep only last 100 conversations per user
            await self.redis_client.ltrim(key, 0, 99)
            
            # Set TTL for user list
            await self.redis_client.expire(key, self.ttl_seconds * 2)
            
        except Exception as e:
            logger.error(f"Failed to update user conversation list: {e}")
    
    async def _get_user_conversation_list(self, user_id: str) -> List[str]:
        """Get user's conversation list from cache"""        try:
            key = f"user_conversations:{user_id}"
            conversation_ids = await self.redis_client.lrange(key, 0, -1)
            
            return [conv_id.decode() for conv_id in conversation_ids]
            
        except Exception as e:
            logger.error(f"Failed to get user conversation list: {e}")
            return []
    
    def _matches_query(self, record: ConversationRecord, query: Dict[str, Any]) -> bool:
        """Check if record matches query parameters"""        
        # Content type filter
        if "content_type" in query:
            if record.content_type != query["content_type"]:
                return False
        
        # Status filter
        if "status" in query:
            if record.status != query["status"]:
                return False
        
        # Date range filters
        if "start_date" in query:
            if record.timestamp < query["start_date"]:
                return False
        
        if "end_date" in query:
            if record.timestamp > query["end_date"]:
                return False
        
        return True
    
    def _sort_and_limit_results(
        self,
        results: List[ConversationRecord],
        query: Dict[str, Any]
    ) -> List[ConversationRecord]:
        """Sort and limit search results"""        
        # Apply ordering
        order_by = query.get("order_by", "timestamp")
        order_dir = query.get("order_dir", "desc")
        
        if hasattr(ConversationRecord, order_by):
            reverse = order_dir.lower() == "desc"
            results.sort(
                key=lambda x: getattr(x, order_by, 0),
                reverse=reverse
            )
        
        # Apply limit and offset
        limit = query.get("limit", 50)
        offset = query.get("offset", 0)
        
        return results[offset:offset + limit]


class VectorStore:
    """    FAISS-based vector storage for semantic search
    
    Provides vector indexing and similarity search capabilities
    for conversation embeddings.
    """    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.metrics = MetricsCollector("vector_store")
        
        # FAISS index
        self.index = None
        self.conversation_ids = []  # Map index positions to conversation IDs
        self.metadata = {}  # Store metadata for each vector
        
        # Embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info(f"VectorStore initialized with dimension {dimension}")
    
    async def initialize(self):
        """Initialize FAISS index"""        try:
            # Create FAISS index for similarity search
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Load existing vectors if available
            await self._load_existing_vectors()
            
            logger.info("VectorStore FAISS index initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorStore: {e}")
            raise
    
    async def add_vector(
        self,
        conversation_id: str,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Add vector to index
        
        Args:
            conversation_id: Conversation identifier
            vector: Embedding vector
            metadata: Optional metadata
            
        Returns:
            Success status
        """        try:
            if self.index is None:
                await self.initialize()
            
            # Normalize vector for cosine similarity
            vector = vector.astype(np.float32)
            vector = vector / np.linalg.norm(vector)
            
            # Add to index
            self.index.add(vector.reshape(1, -1))
            
            # Track conversation ID and metadata
            self.conversation_ids.append(conversation_id)
            if metadata:
                self.metadata[conversation_id] = metadata
            
            self.metrics.increment("vectors_added")
            logger.debug(f"Added vector for conversation: {conversation_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector for conversation {conversation_id}: {e}")
            self.metrics.increment("vector_add_errors")
            return False
    
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            user_id: Optional user filter
            limit: Optional additional limit
            
        Returns:
            List of similar conversations with scores
        """        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Normalize query vector
            query_vector = query_vector.astype(np.float32)
            query_vector = query_vector / np.linalg.norm(query_vector)
            
            # Search index
            scores, indices = self.index.search(
                query_vector.reshape(1, -1),
                min(k, self.index.ntotal)
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= len(self.conversation_ids):
                    continue
                
                conversation_id = self.conversation_ids[idx]
                metadata = self.metadata.get(conversation_id, {})
                
                # Filter by user_id if specified
                if user_id and metadata.get("user_id") != user_id:
                    continue
                
                result = {
                    "conversation_id": conversation_id,
                    "similarity_score": float(score),
                    "metadata": metadata
                }
                
                results.append(result)
            
            # Apply additional limit if specified
            if limit:
                results = results[:limit]
            
            self.metrics.increment("vector_searches")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            self.metrics.increment("vector_search_errors")
            return []
    
    async def remove_vector(self, conversation_id: str) -> bool:
        """        Remove vector from index
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Success status
        """        try:
            # Find index position
            if conversation_id not in self.conversation_ids:
                return False
            
            idx = self.conversation_ids.index(conversation_id)
            
            # Remove from tracking
            self.conversation_ids.pop(idx)
            self.metadata.pop(conversation_id, None)
            
            # Note: FAISS doesn't support efficient single vector removal
            # In production, would rebuild index periodically
            
            self.metrics.increment("vectors_removed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove vector for conversation {conversation_id}: {e}")
            self.metrics.increment("vector_remove_errors")
            return False
    
    async def cleanup_before_date(self, cutoff_date: datetime) -> int:
        """        Clean up vectors before a specific date
        
        Args:
            cutoff_date: Date before which to remove vectors
            
        Returns:
            Number of vectors removed
        """        try:
            removed_count = 0
            conversations_to_remove = []
            
            # Find conversations to remove based on metadata timestamps
            for conversation_id, metadata in self.metadata.items():
                timestamp_str = metadata.get("timestamp")
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if timestamp < cutoff_date:
                            conversations_to_remove.append(conversation_id)
                    except ValueError:
                        # Invalid timestamp format
                        continue
            
            # Remove vectors
            for conversation_id in conversations_to_remove:
                if await self.remove_vector(conversation_id):
                    removed_count += 1
            
            self.metrics.gauge("vectors_cleaned", removed_count)
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup vectors before {cutoff_date}: {e}")
            self.metrics.increment("vector_cleanup_errors")
            return 0
    
    async def _load_existing_vectors(self):
        """Load existing vectors from persistent storage"""        # In production, would load from file or database
        # This is a simplified version
        pass
    
    async def save_index(self, file_path: str) -> bool:
        """Save FAISS index to file"""        try:
            if self.index:
                faiss.write_index(self.index, file_path)
                
                # Save metadata separately
                metadata_file = file_path.replace('.index', '_metadata.json')
                with open(metadata_file, 'w') as f:
                    json.dump({
                        'conversation_ids': self.conversation_ids,
                        'metadata': self.metadata
                    }, f)
                
                return True
            
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")
            return False
    
    async def load_index(self, file_path: str) -> bool:
        """Load FAISS index from file"""        try:
            self.index = faiss.read_index(file_path)
            
            # Load metadata
            metadata_file = file_path.replace('.index', '_metadata.json')
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                self.conversation_ids = data.get('conversation_ids', [])
                self.metadata = data.get('metadata', {})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            return False


class ConversationDatabase:
    """    Unified database interface for conversation storage
    
    Provides a unified interface for all conversation database operations
    across different storage systems.
    """    
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.short_term_memory = ShortTermMemory()
        self.vector_store = VectorStore()
        self.metrics = MetricsCollector("conversation_database")
        
        logger.info("ConversationDatabase unified interface initialized")
    
    async def initialize(self):
        """Initialize all storage systems"""        await asyncio.gather(
            self.long_term_memory.initialize(),
            self.short_term_memory.initialize(),
            self.vector_store.initialize()
        )
        
        logger.info("ConversationDatabase all storage systems initialized")
    
    async def store_conversation(
        self,
        record: ConversationRecord,
        store_vector: bool = True
    ) -> bool:
        """        Store conversation across all storage systems
        
        Args:
            record: ConversationRecord to store
            store_vector: Whether to generate and store vector embedding
            
        Returns:
            Success status
        """        try:
            # Store in long-term database
            db_success = await self.long_term_memory.store(record)
            
            # Cache in short-term memory
            cache_success = await self.short_term_memory.store(record)
            
            # Generate and store vector embedding if requested
            vector_success = True
            if store_vector and record.conversation_data:
                text_content = self.long_term_memory._extract_searchable_text(
                    record.conversation_data
                )
                
                if text_content.strip():
                    embedding = self.vector_store.embedding_model.encode(text_content)
                    vector_success = await self.vector_store.add_vector(
                        record.conversation_id,
                        embedding,
                        metadata={
                            "user_id": record.user_id,
                            "content_type": record.content_type,
                            "timestamp": record.timestamp.isoformat()
                        }
                    )
            
            # Consider successful if at least the main database storage succeeds
            success = db_success
            
            if success:
                self.metrics.increment("conversations_stored")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store conversation {record.conversation_id}: {e}")
            self.metrics.increment("storage_errors")
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        """        Get conversation from the fastest available source
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationRecord or None
        """        # Try cache first
        record = await self.short_term_memory.get(conversation_id)
        
        if not record:
            # Fallback to database
            record = await self.long_term_memory.get(conversation_id)
            
            if record:
                # Update cache for future access
                await self.short_term_memory.store(record)
        
        return record


class MemoryCache:
    """    Specialized caching system for memory entries
    
    Provides intelligent caching for conversation memory entries
    with automatic expiration and importance-based retention.
    """    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.cache: Dict[str, MemoryEntry] = {}
        self.access_tracker: Dict[str, int] = {}
        self.metrics = MetricsCollector("memory_cache")
        
        logger.info(f"MemoryCache initialized with capacity {max_entries}")
    
    async def store_entry(self, entry: MemoryEntry) -> bool:
        """        Store memory entry in cache
        
        Args:
            entry: MemoryEntry to store
            
        Returns:
            Success status
        """        try:
            # Check if cache is full
            if len(self.cache) >= self.max_entries:
                await self._evict_entries()
            
            # Store entry
            self.cache[entry.entry_id] = entry
            self.access_tracker[entry.entry_id] = 1
            
            self.metrics.increment("entries_stored")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory entry {entry.entry_id}: {e}")
            self.metrics.increment("storage_errors")
            return False
    
    async def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """        Get memory entry from cache
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            MemoryEntry or None
        """        try:
            entry = self.cache.get(entry_id)
            
            if entry:
                # Update access tracking
                entry.update_access()
                self.access_tracker[entry_id] = self.access_tracker.get(entry_id, 0) + 1
                
                self.metrics.increment("cache_hits")
                return entry
            else:
                self.metrics.increment("cache_misses")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get memory entry {entry_id}: {e}")
            self.metrics.increment("retrieval_errors")
            return None
    
    async def _evict_entries(self):
        """Evict least important entries from cache"""        try:
            # Calculate eviction scores
            eviction_candidates = []
            
            for entry_id, entry in self.cache.items():
                if entry.is_expired():
                    # Expired entries have highest priority for eviction
                    score = 0
                else:
                    # Calculate retention score (higher = keep longer)
                    retention_score = entry.calculate_retention_score()
                    access_count = self.access_tracker.get(entry_id, 0)
                    
                    # Lower score = higher eviction priority
                    score = retention_score + (access_count * 0.1)
                
                eviction_candidates.append((entry_id, score))
            
            # Sort by score (lowest first = highest eviction priority)
            eviction_candidates.sort(key=lambda x: x[1])
            
            # Evict bottom 20% of entries
            evict_count = max(1, len(eviction_candidates) // 5)
            
            for entry_id, _ in eviction_candidates[:evict_count]:
                del self.cache[entry_id]
                del self.access_tracker[entry_id]
            
            self.metrics.gauge("entries_evicted", evict_count)
            
        except Exception as e:
            logger.error(f"Failed to evict cache entries: {e}")
            self.metrics.increment("eviction_errors")


# Export all storage classes
__all__ = [
    "StorageInterface",
    "LongTermMemory", 
    "ShortTermMemory",
    "VectorStore",
    "ConversationDatabase",
    "MemoryCache"
]
