"""
IA Influencer Agent - Advanced Data Repositories
===============================================

Enterprise-grade data access layer for indexing operations with
specialized repositories for vectors, fingerprints, search, and metadata.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, and_, or_, func, desc, asc
from redis.asyncio import Redis
import faiss
from elasticsearch.exceptions import NotFoundError

logger = logging.getLogger(__name__)


@dataclass
class IndexRecord:
    """Base index record structure"""
    content_id: str
    creator_id: str
    content_type: str
    title: str
    description: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    indexed_at: datetime
    fingerprint_hash: Optional[str] = None
    protection_level: str = "standard"
    licensing_info: Optional[Dict] = None


@dataclass
class VectorRecord:
    """Vector embedding record structure"""
    vector_id: str
    content_id: str
    embedding: List[float]
    embedding_type: str  # text, audio, visual, etc.
    dimension: int
    model_version: str
    similarity_threshold: float
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class FingerprintRecord:
    """Content fingerprint record structure"""
    fingerprint_id: str
    content_id: str
    fingerprint_type: str  # audio, image, video, text
    fingerprint_data: Dict[str, str]  # algorithm -> hash mapping
    algorithm_versions: Dict[str, str]
    similarity_scores: Dict[str, float]
    created_at: datetime
    updated_at: datetime


@dataclass
class SearchQuery:
    """Search query structure"""
    query_text: Optional[str] = None
    vector_query: Optional[List[float]] = None
    filters: Optional[Dict[str, Any]] = None
    content_types: Optional[List[str]] = None
    creator_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_range: Optional[Dict[str, datetime]] = None
    similarity_threshold: float = 0.8
    limit: int = 50
    offset: int = 0
    sort_by: str = "relevance"
    sort_order: str = "desc"


class BaseRepository(ABC):
    """Abstract base repository class"""
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def create(self, record: Any) -> str:
        """Create a new record"""
        self.logger.error(f"create method not implemented in {self.__class__.__name__}")
        return ""
    
    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[Any]:
        """Get record by ID"""
        self.logger.error(f"get_by_id method not implemented in {self.__class__.__name__}")
        return None
    
    @abstractmethod
    async def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing record"""
        self.logger.error(f"update method not implemented in {self.__class__.__name__}")
        return False
    
    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """Delete record"""
        self.logger.error(f"delete method not implemented in {self.__class__.__name__}")
        return False
    
    async def _cache_get(self, key: str) -> Optional[str]:
        """Get value from Redis cache"""
        try:
            value = await self.redis_client.get(key)
            return value.decode() if value else None
        except Exception as e:
            self.logger.warning(f"Cache get failed for {key}: {e}")
            return None
    
    async def _cache_set(self, key: str, value: str, expire: int = 3600) -> None:
        """Set value in Redis cache"""
        try:
            await self.redis_client.setex(key, expire, value)
        except Exception as e:
            self.logger.warning(f"Cache set failed for {key}: {e}")
    
    async def _cache_delete(self, key: str) -> None:
        """Delete value from Redis cache"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            self.logger.warning(f"Cache delete failed for {key}: {e}")


class IndexRepository(BaseRepository):
    """Repository for managing content index records"""
    
    async def create(self, record: IndexRecord) -> str:
        """Create new index record"""
        try:
            # Generate ID if not provided
            if not record.content_id:
                record.content_id = str(uuid.uuid4())
            
            # Prepare SQL insert
            query = text("""
                INSERT INTO content_index (
                    content_id, creator_id, content_type, title, description,
                    tags, metadata, created_at, updated_at, indexed_at,
                    fingerprint_hash, protection_level, licensing_info
                ) VALUES (
                    :content_id, :creator_id, :content_type, :title, :description,
                    :tags, :metadata, :created_at, :updated_at, :indexed_at,
                    :fingerprint_hash, :protection_level, :licensing_info
                )
            """)
            
            await self.db_session.execute(query, {
                "content_id": record.content_id,
                "creator_id": record.creator_id,
                "content_type": record.content_type,
                "title": record.title,
                "description": record.description,
                "tags": json.dumps(record.tags),
                "metadata": json.dumps(record.metadata),
                "created_at": record.created_at,
                "updated_at": record.updated_at,
                "indexed_at": record.indexed_at,
                "fingerprint_hash": record.fingerprint_hash,
                "protection_level": record.protection_level,
                "licensing_info": json.dumps(record.licensing_info) if record.licensing_info else None
            })
            
            await self.db_session.commit()
            
            # Cache the record
            cache_key = f"index:{record.content_id}"
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            # Update secondary indexes
            await self._update_secondary_indexes(record)
            
            self.logger.info(f"Created index record: {record.content_id}")
            return record.content_id
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to create index record: {e}")
            raise
    
    async def get_by_id(self, content_id: str) -> Optional[IndexRecord]:
        """Get index record by content ID"""
        try:
            # Try cache first
            cache_key = f"index:{content_id}"
            cached = await self._cache_get(cache_key)
            
            if cached:
                data = json.loads(cached)
                return IndexRecord(**data)
            
            # Query database
            query = text("""
                SELECT * FROM content_index WHERE content_id = :content_id
            """)
            
            result = await self.db_session.execute(query, {"content_id": content_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            # Convert row to IndexRecord
            record = IndexRecord(
                content_id=row.content_id,
                creator_id=row.creator_id,
                content_type=row.content_type,
                title=row.title,
                description=row.description,
                tags=json.loads(row.tags) if row.tags else [],
                metadata=json.loads(row.metadata) if row.metadata else {},
                created_at=row.created_at,
                updated_at=row.updated_at,
                indexed_at=row.indexed_at,
                fingerprint_hash=row.fingerprint_hash,
                protection_level=row.protection_level,
                licensing_info=json.loads(row.licensing_info) if row.licensing_info else None
            )
            
            # Update cache
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            return record
            
        except Exception as e:
            self.logger.error(f"Failed to get index record {content_id}: {e}")
            return None
    
    async def update(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update index record"""
        try:
            # Prepare update fields
            set_clauses = []
            params = {"content_id": content_id}
            
            for field, value in updates.items():
                if field in ["tags", "metadata", "licensing_info"]:
                    value = json.dumps(value) if value else None
                set_clauses.append(f"{field} = :{field}")
                params[field] = value
            
            if not set_clauses:
                return False
            
            # Add updated_at
            set_clauses.append("updated_at = :updated_at")
            params["updated_at"] = datetime.now(timezone.utc)
            
            query = text(f"""
                UPDATE content_index 
                SET {', '.join(set_clauses)}
                WHERE content_id = :content_id
            """)
            
            result = await self.db_session.execute(query, params)
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Invalidate cache
                cache_key = f"index:{content_id}"
                await self._cache_delete(cache_key)
                
                self.logger.info(f"Updated index record: {content_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to update index record {content_id}: {e}")
            return False
    
    async def delete(self, content_id: str) -> bool:
        """Delete index record"""
        try:
            query = text("DELETE FROM content_index WHERE content_id = :content_id")
            result = await self.db_session.execute(query, {"content_id": content_id})
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Remove from cache
                cache_key = f"index:{content_id}"
                await self._cache_delete(cache_key)
                
                # Remove from secondary indexes
                await self._remove_from_secondary_indexes(content_id)
                
                self.logger.info(f"Deleted index record: {content_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to delete index record {content_id}: {e}")
            return False
    
    async def search(self, query: SearchQuery) -> List[IndexRecord]:
        """Search index records with filters"""
        try:
            # Build SQL query
            conditions = []
            params = {}
            
            if query.content_types:
                conditions.append("content_type = ANY(:content_types)")
                params["content_types"] = query.content_types
            
            if query.creator_ids:
                conditions.append("creator_id = ANY(:creator_ids)")
                params["creator_ids"] = query.creator_ids
            
            if query.query_text:
                conditions.append("""
                    (title ILIKE :search_text OR description ILIKE :search_text)
                """)
                params["search_text"] = f"%{query.query_text}%"
            
            if query.date_range:
                if "start" in query.date_range:
                    conditions.append("created_at >= :start_date")
                    params["start_date"] = query.date_range["start"]
                if "end" in query.date_range:
                    conditions.append("created_at <= :end_date")
                    params["end_date"] = query.date_range["end"]
            
            # Build query
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Sorting
            sort_column = {
                "relevance": "indexed_at",
                "created_at": "created_at",
                "updated_at": "updated_at",
                "title": "title"
            }.get(query.sort_by, "indexed_at")
            
            sort_direction = "DESC" if query.sort_order == "desc" else "ASC"
            
            sql_query = text(f"""
                SELECT * FROM content_index 
                WHERE {where_clause}
                ORDER BY {sort_column} {sort_direction}
                LIMIT :limit OFFSET :offset
            """)
            
            params.update({
                "limit": query.limit,
                "offset": query.offset
            })
            
            result = await self.db_session.execute(sql_query, params)
            rows = result.fetchall()
            
            # Convert to IndexRecord objects
            records = []
            for row in rows:
                record = IndexRecord(
                    content_id=row.content_id,
                    creator_id=row.creator_id,
                    content_type=row.content_type,
                    title=row.title,
                    description=row.description,
                    tags=json.loads(row.tags) if row.tags else [],
                    metadata=json.loads(row.metadata) if row.metadata else {},
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    indexed_at=row.indexed_at,
                    fingerprint_hash=row.fingerprint_hash,
                    protection_level=row.protection_level,
                    licensing_info=json.loads(row.licensing_info) if row.licensing_info else None
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to search index records: {e}")
            return []
    
    async def get_by_creator(self, creator_id: str, limit: int = 100) -> List[IndexRecord]:
        """Get all records for a specific creator"""
        try:
            query = text("""
                SELECT * FROM content_index 
                WHERE creator_id = :creator_id
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = await self.db_session.execute(query, {
                "creator_id": creator_id,
                "limit": limit
            })
            rows = result.fetchall()
            
            records = []
            for row in rows:
                record = IndexRecord(
                    content_id=row.content_id,
                    creator_id=row.creator_id,
                    content_type=row.content_type,
                    title=row.title,
                    description=row.description,
                    tags=json.loads(row.tags) if row.tags else [],
                    metadata=json.loads(row.metadata) if row.metadata else {},
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    indexed_at=row.indexed_at,
                    fingerprint_hash=row.fingerprint_hash,
                    protection_level=row.protection_level,
                    licensing_info=json.loads(row.licensing_info) if row.licensing_info else None
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get records for creator {creator_id}: {e}")
            return []
    
    async def _update_secondary_indexes(self, record: IndexRecord) -> None:
        """Update Redis secondary indexes"""
        try:
            # Index by creator
            await self.redis_client.sadd(f"creator:{record.creator_id}:content", record.content_id)
            
            # Index by content type
            await self.redis_client.sadd(f"type:{record.content_type}:content", record.content_id)
            
            # Index by tags
            for tag in record.tags:
                await self.redis_client.sadd(f"tag:{tag}:content", record.content_id)
            
            # Index by date
            date_key = record.created_at.strftime("%Y-%m-%d")
            await self.redis_client.sadd(f"date:{date_key}:content", record.content_id)
            
        except Exception as e:
            self.logger.warning(f"Failed to update secondary indexes: {e}")
    
    async def _remove_from_secondary_indexes(self, content_id: str) -> None:
        """Remove from Redis secondary indexes"""
        try:
            # Get record first to know what to remove
            record = await self.get_by_id(content_id)
            if not record:
                return
            
            # Remove from creator index
            await self.redis_client.srem(f"creator:{record.creator_id}:content", content_id)
            
            # Remove from content type index
            await self.redis_client.srem(f"type:{record.content_type}:content", content_id)
            
            # Remove from tag indexes
            for tag in record.tags:
                await self.redis_client.srem(f"tag:{tag}:content", content_id)
            
            # Remove from date index
            date_key = record.created_at.strftime("%Y-%m-%d")
            await self.redis_client.srem(f"date:{date_key}:content", content_id)
            
        except Exception as e:
            self.logger.warning(f"Failed to remove from secondary indexes: {e}")


class VectorRepository(BaseRepository):
    """Repository for managing vector embeddings with FAISS integration"""
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis, faiss_index: faiss.Index = None):
        super().__init__(db_session, redis_client)
        self.faiss_index = faiss_index
        self.vector_mapping = {}  # vector_id -> faiss_index mapping
    
    async def create(self, record: VectorRecord) -> str:
        """Create new vector record"""
        try:
            # Generate ID if not provided
            if not record.vector_id:
                record.vector_id = str(uuid.uuid4())
            
            # Store in database
            query = text("""
                INSERT INTO vector_embeddings (
                    vector_id, content_id, embedding, embedding_type,
                    dimension, model_version, similarity_threshold,
                    created_at, metadata
                ) VALUES (
                    :vector_id, :content_id, :embedding, :embedding_type,
                    :dimension, :model_version, :similarity_threshold,
                    :created_at, :metadata
                )
            """)
            
            await self.db_session.execute(query, {
                "vector_id": record.vector_id,
                "content_id": record.content_id,
                "embedding": json.dumps(record.embedding),
                "embedding_type": record.embedding_type,
                "dimension": record.dimension,
                "model_version": record.model_version,
                "similarity_threshold": record.similarity_threshold,
                "created_at": record.created_at,
                "metadata": json.dumps(record.metadata)
            })
            
            await self.db_session.commit()
            
            # Add to FAISS index if available
            if self.faiss_index:
                vector_array = np.array(record.embedding, dtype=np.float32).reshape(1, -1)
                faiss_idx = self.faiss_index.ntotal
                self.faiss_index.add(vector_array)
                self.vector_mapping[record.vector_id] = faiss_idx
            
            # Cache the record
            cache_key = f"vector:{record.vector_id}"
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            self.logger.info(f"Created vector record: {record.vector_id}")
            return record.vector_id
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to create vector record: {e}")
            raise
    
    async def get_by_id(self, vector_id: str) -> Optional[VectorRecord]:
        """Get vector record by ID"""
        try:
            # Try cache first
            cache_key = f"vector:{vector_id}"
            cached = await self._cache_get(cache_key)
            
            if cached:
                data = json.loads(cached)
                data["embedding"] = json.loads(data["embedding"]) if isinstance(data["embedding"], str) else data["embedding"]
                return VectorRecord(**data)
            
            # Query database
            query = text("SELECT * FROM vector_embeddings WHERE vector_id = :vector_id")
            result = await self.db_session.execute(query, {"vector_id": vector_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            record = VectorRecord(
                vector_id=row.vector_id,
                content_id=row.content_id,
                embedding=json.loads(row.embedding),
                embedding_type=row.embedding_type,
                dimension=row.dimension,
                model_version=row.model_version,
                similarity_threshold=row.similarity_threshold,
                created_at=row.created_at,
                metadata=json.loads(row.metadata) if row.metadata else {}
            )
            
            # Update cache
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            return record
            
        except Exception as e:
            self.logger.error(f"Failed to get vector record {vector_id}: {e}")
            return None
    
    async def get_by_content_id(self, content_id: str) -> List[VectorRecord]:
        """Get all vector records for a content ID"""
        try:
            query = text("""
                SELECT * FROM vector_embeddings 
                WHERE content_id = :content_id
                ORDER BY created_at DESC
            """)
            
            result = await self.db_session.execute(query, {"content_id": content_id})
            rows = result.fetchall()
            
            records = []
            for row in rows:
                record = VectorRecord(
                    vector_id=row.vector_id,
                    content_id=row.content_id,
                    embedding=json.loads(row.embedding),
                    embedding_type=row.embedding_type,
                    dimension=row.dimension,
                    model_version=row.model_version,
                    similarity_threshold=row.similarity_threshold,
                    created_at=row.created_at,
                    metadata=json.loads(row.metadata) if row.metadata else {}
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get vectors for content {content_id}: {e}")
            return []
    
    async def similarity_search(self, query_vector: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        """Perform similarity search using FAISS"""
        try:
            if not self.faiss_index:
                raise ValueError("FAISS index not available")
            
            # Convert query vector to numpy array
            query_array = np.array(query_vector, dtype=np.float32).reshape(1, -1)
            
            # Search in FAISS
            scores, indices = self.faiss_index.search(query_array, top_k)
            
            # Map FAISS indices back to vector IDs
            results = []
            for score, faiss_idx in zip(scores[0], indices[0]):
                if faiss_idx == -1:  # No more results
                    break
                
                # Find vector_id from mapping
                vector_id = None
                for vid, fidx in self.vector_mapping.items():
                    if fidx == faiss_idx:
                        vector_id = vid
                        break
                
                if vector_id:
                    results.append((vector_id, float(score)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {e}")
            return []
    
    async def update(self, vector_id: str, updates: Dict[str, Any]) -> bool:
        """Update vector record"""
        try:
            # Prepare update fields
            set_clauses = []
            params = {"vector_id": vector_id}
            
            for field, value in updates.items():
                if field in ["embedding", "metadata"]:
                    value = json.dumps(value) if value else None
                set_clauses.append(f"{field} = :{field}")
                params[field] = value
            
            if not set_clauses:
                return False
            
            query = text(f"""
                UPDATE vector_embeddings 
                SET {', '.join(set_clauses)}
                WHERE vector_id = :vector_id
            """)
            
            result = await self.db_session.execute(query, params)
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Invalidate cache
                cache_key = f"vector:{vector_id}"
                await self._cache_delete(cache_key)
                
                self.logger.info(f"Updated vector record: {vector_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to update vector record {vector_id}: {e}")
            return False
    
    async def delete(self, vector_id: str) -> bool:
        """Delete vector record"""
        try:
            query = text("DELETE FROM vector_embeddings WHERE vector_id = :vector_id")
            result = await self.db_session.execute(query, {"vector_id": vector_id})
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Remove from cache
                cache_key = f"vector:{vector_id}"
                await self._cache_delete(cache_key)
                
                # Remove from FAISS mapping (FAISS itself doesn't support deletion)
                if vector_id in self.vector_mapping:
                    del self.vector_mapping[vector_id]
                
                self.logger.info(f"Deleted vector record: {vector_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to delete vector record {vector_id}: {e}")
            return False


class FingerprintRepository(BaseRepository):
    """Repository for managing content fingerprints"""
    
    async def create(self, record: FingerprintRecord) -> str:
        """Create new fingerprint record"""
        try:
            # Generate ID if not provided
            if not record.fingerprint_id:
                record.fingerprint_id = str(uuid.uuid4())
            
            query = text("""
                INSERT INTO content_fingerprints (
                    fingerprint_id, content_id, fingerprint_type,
                    fingerprint_data, algorithm_versions, similarity_scores,
                    created_at, updated_at
                ) VALUES (
                    :fingerprint_id, :content_id, :fingerprint_type,
                    :fingerprint_data, :algorithm_versions, :similarity_scores,
                    :created_at, :updated_at
                )
            """)
            
            await self.db_session.execute(query, {
                "fingerprint_id": record.fingerprint_id,
                "content_id": record.content_id,
                "fingerprint_type": record.fingerprint_type,
                "fingerprint_data": json.dumps(record.fingerprint_data),
                "algorithm_versions": json.dumps(record.algorithm_versions),
                "similarity_scores": json.dumps(record.similarity_scores),
                "created_at": record.created_at,
                "updated_at": record.updated_at
            })
            
            await self.db_session.commit()
            
            # Cache the record
            cache_key = f"fingerprint:{record.fingerprint_id}"
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            # Index fingerprint hashes for fast lookup
            await self._index_fingerprint_hashes(record)
            
            self.logger.info(f"Created fingerprint record: {record.fingerprint_id}")
            return record.fingerprint_id
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to create fingerprint record: {e}")
            raise
    
    async def get_by_id(self, fingerprint_id: str) -> Optional[FingerprintRecord]:
        """Get fingerprint record by ID"""
        try:
            # Try cache first
            cache_key = f"fingerprint:{fingerprint_id}"
            cached = await self._cache_get(cache_key)
            
            if cached:
                data = json.loads(cached)
                return FingerprintRecord(**data)
            
            # Query database
            query = text("SELECT * FROM content_fingerprints WHERE fingerprint_id = :fingerprint_id")
            result = await self.db_session.execute(query, {"fingerprint_id": fingerprint_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            record = FingerprintRecord(
                fingerprint_id=row.fingerprint_id,
                content_id=row.content_id,
                fingerprint_type=row.fingerprint_type,
                fingerprint_data=json.loads(row.fingerprint_data),
                algorithm_versions=json.loads(row.algorithm_versions),
                similarity_scores=json.loads(row.similarity_scores),
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            
            # Update cache
            await self._cache_set(cache_key, json.dumps(asdict(record), default=str))
            
            return record
            
        except Exception as e:
            self.logger.error(f"Failed to get fingerprint record {fingerprint_id}: {e}")
            return None
    
    async def get_by_content_id(self, content_id: str) -> List[FingerprintRecord]:
        """Get all fingerprint records for a content ID"""
        try:
            query = text("""
                SELECT * FROM content_fingerprints 
                WHERE content_id = :content_id
                ORDER BY created_at DESC
            """)
            
            result = await self.db_session.execute(query, {"content_id": content_id})
            rows = result.fetchall()
            
            records = []
            for row in rows:
                record = FingerprintRecord(
                    fingerprint_id=row.fingerprint_id,
                    content_id=row.content_id,
                    fingerprint_type=row.fingerprint_type,
                    fingerprint_data=json.loads(row.fingerprint_data),
                    algorithm_versions=json.loads(row.algorithm_versions),
                    similarity_scores=json.loads(row.similarity_scores),
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get fingerprints for content {content_id}: {e}")
            return []
    
    async def find_similar_fingerprints(self, fingerprint_data: Dict[str, str], 
                                      fingerprint_type: str) -> List[Tuple[str, float]]:
        """Find similar fingerprints"""
        try:
            results = []
            
            # For each algorithm in the query fingerprint
            for algorithm, query_hash in fingerprint_data.items():
                # Look for exact matches first
                exact_matches = await self.redis_client.smembers(f"fp:{algorithm}:{query_hash}")
                
                for content_id in exact_matches:
                    if isinstance(content_id, bytes):
                        content_id = content_id.decode()
                    results.append((content_id, 1.0))  # Exact match = 100% similarity
                
                # For perceptual hashes, also check for near matches
                if algorithm in ["phash", "dhash", "whash"]:
                    similar_matches = await self._find_similar_perceptual_hashes(
                        algorithm, query_hash
                    )
                    results.extend(similar_matches)
            
            # Remove duplicates and sort by similarity
            unique_results = {}
            for content_id, similarity in results:
                if content_id not in unique_results or similarity > unique_results[content_id]:
                    unique_results[content_id] = similarity
            
            sorted_results = sorted(unique_results.items(), key=lambda x: x[1], reverse=True)
            return sorted_results
            
        except Exception as e:
            self.logger.error(f"Failed to find similar fingerprints: {e}")
            return []
    
    async def _find_similar_perceptual_hashes(self, algorithm: str, query_hash: str) -> List[Tuple[str, float]]:
        """Find similar perceptual hashes using Hamming distance"""
        try:
            results = []
            threshold = 10  # Maximum Hamming distance for similarity
            
            # Get all hashes for this algorithm
            pattern = f"fp:{algorithm}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode()
                
                stored_hash = key.split(":")[-1]
                
                # Calculate Hamming distance
                hamming_distance = self._calculate_hamming_distance(query_hash, stored_hash)
                
                if hamming_distance <= threshold:
                    similarity = 1.0 - (hamming_distance / len(query_hash))
                    
                    # Get content IDs for this hash
                    content_ids = await self.redis_client.smembers(key)
                    for content_id in content_ids:
                        if isinstance(content_id, bytes):
                            content_id = content_id.decode()
                        results.append((content_id, similarity))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to find similar perceptual hashes: {e}")
            return []
    
    def _calculate_hamming_distance(self, hash1: str, hash2: str) -> int:
        """Calculate Hamming distance between two hashes"""
        if len(hash1) != len(hash2):
            return float('inf')
        
        distance = 0
        for c1, c2 in zip(hash1, hash2):
            if c1 != c2:
                distance += 1
        
        return distance
    
    async def _index_fingerprint_hashes(self, record: FingerprintRecord) -> None:
        """Index fingerprint hashes in Redis for fast lookup"""
        try:
            for algorithm, fingerprint_hash in record.fingerprint_data.items():
                key = f"fp:{algorithm}:{fingerprint_hash}"
                await self.redis_client.sadd(key, record.content_id)
                
        except Exception as e:
            self.logger.warning(f"Failed to index fingerprint hashes: {e}")
    
    async def update(self, fingerprint_id: str, updates: Dict[str, Any]) -> bool:
        """Update fingerprint record"""
        try:
            # Prepare update fields
            set_clauses = []
            params = {"fingerprint_id": fingerprint_id}
            
            for field, value in updates.items():
                if field in ["fingerprint_data", "algorithm_versions", "similarity_scores"]:
                    value = json.dumps(value) if value else None
                set_clauses.append(f"{field} = :{field}")
                params[field] = value
            
            if not set_clauses:
                return False
            
            # Add updated_at
            set_clauses.append("updated_at = :updated_at")
            params["updated_at"] = datetime.now(timezone.utc)
            
            query = text(f"""
                UPDATE content_fingerprints 
                SET {', '.join(set_clauses)}
                WHERE fingerprint_id = :fingerprint_id
            """)
            
            result = await self.db_session.execute(query, params)
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Invalidate cache
                cache_key = f"fingerprint:{fingerprint_id}"
                await self._cache_delete(cache_key)
                
                self.logger.info(f"Updated fingerprint record: {fingerprint_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to update fingerprint record {fingerprint_id}: {e}")
            return False
    
    async def delete(self, fingerprint_id: str) -> bool:
        """Delete fingerprint record"""
        try:
            # Get record to remove from indexes
            record = await self.get_by_id(fingerprint_id)
            
            query = text("DELETE FROM content_fingerprints WHERE fingerprint_id = :fingerprint_id")
            result = await self.db_session.execute(query, {"fingerprint_id": fingerprint_id})
            await self.db_session.commit()
            
            if result.rowcount > 0:
                # Remove from cache
                cache_key = f"fingerprint:{fingerprint_id}"
                await self._cache_delete(cache_key)
                
                # Remove from hash indexes
                if record:
                    await self._remove_fingerprint_hashes(record)
                
                self.logger.info(f"Deleted fingerprint record: {fingerprint_id}")
                return True
            
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Failed to delete fingerprint record {fingerprint_id}: {e}")
            return False
    
    async def _remove_fingerprint_hashes(self, record: FingerprintRecord) -> None:
        """Remove fingerprint hashes from Redis indexes"""
        try:
            for algorithm, fingerprint_hash in record.fingerprint_data.items():
                key = f"fp:{algorithm}:{fingerprint_hash}"
                await self.redis_client.srem(key, record.content_id)
                
                # Remove empty sets
                if await self.redis_client.scard(key) == 0:
                    await self.redis_client.delete(key)
                    
        except Exception as e:
            self.logger.warning(f"Failed to remove fingerprint hashes: {e}")


class SearchRepository:
    """Unified search repository combining all search capabilities"""
    
    def __init__(self, index_repo: IndexRepository, vector_repo: VectorRepository, 
                 fingerprint_repo: FingerprintRepository):
        self.index_repo = index_repo
        self.vector_repo = vector_repo
        self.fingerprint_repo = fingerprint_repo
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def unified_search(self, query: SearchQuery) -> Dict[str, Any]:
        """Perform unified search across all repository types"""
        try:
            results = {
                "text_results": [],
                "vector_results": [],
                "fingerprint_results": [],
                "total_results": 0,
                "query_time_ms": 0
            }
            
            start_time = datetime.now()
            
            # Text search in index
            if query.query_text:
                text_results = await self.index_repo.search(query)
                results["text_results"] = [asdict(record) for record in text_results]
            
            # Vector similarity search
            if query.vector_query:
                vector_matches = await self.vector_repo.similarity_search(
                    query.vector_query, query.limit
                )
                
                # Get full records for vector matches
                vector_results = []
                for vector_id, similarity in vector_matches:
                    vector_record = await self.vector_repo.get_by_id(vector_id)
                    if vector_record:
                        result_data = asdict(vector_record)
                        result_data["similarity_score"] = similarity
                        vector_results.append(result_data)
                
                results["vector_results"] = vector_results
            
            # Calculate total results
            results["total_results"] = (
                len(results["text_results"]) + 
                len(results["vector_results"])
            )
            
            # Calculate query time
            end_time = datetime.now()
            results["query_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform unified search: {e}")
            return {
                "text_results": [],
                "vector_results": [],
                "fingerprint_results": [],
                "total_results": 0,
                "query_time_ms": 0,
                "error": str(e)
            }
    
    async def find_duplicate_content(self, content_id: str) -> List[Dict[str, Any]]:
        """Find potential duplicate content using multiple detection methods"""
        try:
            duplicates = []
            
            # Get content fingerprints
            fingerprints = await self.fingerprint_repo.get_by_content_id(content_id)
            
            for fingerprint_record in fingerprints:
                # Find similar fingerprints
                similar_fingerprints = await self.fingerprint_repo.find_similar_fingerprints(
                    fingerprint_record.fingerprint_data,
                    fingerprint_record.fingerprint_type
                )
                
                for similar_content_id, similarity in similar_fingerprints:
                    if similar_content_id != content_id and similarity >= 0.8:
                        # Get full content record
                        content_record = await self.index_repo.get_by_id(similar_content_id)
                        if content_record:
                            duplicate_info = {
                                "content_id": similar_content_id,
                                "similarity": similarity,
                                "detection_method": "fingerprint",
                                "fingerprint_type": fingerprint_record.fingerprint_type,
                                "content_info": asdict(content_record)
                            }
                            duplicates.append(duplicate_info)
            
            # Get content vectors for similarity search
            vectors = await self.vector_repo.get_by_content_id(content_id)
            
            for vector_record in vectors:
                # Find similar vectors
                similar_vectors = await self.vector_repo.similarity_search(
                    vector_record.embedding, 20
                )
                
                for vector_id, similarity in similar_vectors:
                    vector_data = await self.vector_repo.get_by_id(vector_id)
                    if vector_data and vector_data.content_id != content_id and similarity >= 0.85:
                        # Get full content record
                        content_record = await self.index_repo.get_by_id(vector_data.content_id)
                        if content_record:
                            duplicate_info = {
                                "content_id": vector_data.content_id,
                                "similarity": similarity,
                                "detection_method": "vector_similarity",
                                "embedding_type": vector_record.embedding_type,
                                "content_info": asdict(content_record)
                            }
                            duplicates.append(duplicate_info)
            
            # Remove duplicates and sort by similarity
            unique_duplicates = {}
            for dup in duplicates:
                key = dup["content_id"]
                if key not in unique_duplicates or dup["similarity"] > unique_duplicates[key]["similarity"]:
                    unique_duplicates[key] = dup
            
            sorted_duplicates = sorted(
                unique_duplicates.values(), 
                key=lambda x: x["similarity"], 
                reverse=True
            )
            
            return sorted_duplicates
            
        except Exception as e:
            self.logger.error(f"Failed to find duplicate content: {e}")
            return []
    
    async def get_content_recommendations(self, content_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get content recommendations based on similarity"""
        try:
            recommendations = []
            
            # Get content record
            content_record = await self.index_repo.get_by_id(content_id)
            if not content_record:
                return []
            
            # Get similar content by tags
            tag_matches = set()
            for tag in content_record.tags:
                tag_query = SearchQuery(
                    tags=[tag],
                    content_types=[content_record.content_type],
                    limit=20
                )
                tag_results = await self.index_repo.search(tag_query)
                
                for result in tag_results:
                    if result.content_id != content_id:
                        tag_matches.add(result.content_id)
            
            # Get vector similarities
            vectors = await self.vector_repo.get_by_content_id(content_id)
            vector_matches = set()
            
            for vector_record in vectors:
                similar_vectors = await self.vector_repo.similarity_search(
                    vector_record.embedding, limit * 2
                )
                
                for vector_id, similarity in similar_vectors:
                    if similarity >= 0.7:  # Lower threshold for recommendations
                        vector_data = await self.vector_repo.get_by_id(vector_id)
                        if vector_data and vector_data.content_id != content_id:
                            vector_matches.add(vector_data.content_id)
            
            # Combine and rank recommendations
            all_matches = tag_matches.union(vector_matches)
            
            for match_id in list(all_matches)[:limit]:
                match_record = await self.index_repo.get_by_id(match_id)
                if match_record:
                    # Calculate relevance score
                    relevance = 0.0
                    
                    # Tag similarity
                    common_tags = set(content_record.tags).intersection(set(match_record.tags))
                    if content_record.tags:
                        tag_similarity = len(common_tags) / len(content_record.tags)
                        relevance += tag_similarity * 0.4
                    
                    # Creator bonus
                    if match_record.creator_id == content_record.creator_id:
                        relevance += 0.2
                    
                    # Content type match
                    if match_record.content_type == content_record.content_type:
                        relevance += 0.2
                    
                    # Recency bonus
                    time_diff = (datetime.now(timezone.utc) - match_record.created_at).days
                    if time_diff < 30:
                        relevance += 0.2
                    
                    recommendation = {
                        "content_id": match_id,
                        "relevance_score": relevance,
                        "content_info": asdict(match_record)
                    }
                    recommendations.append(recommendation)
            
            # Sort by relevance
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get content recommendations: {e}")
            return []
