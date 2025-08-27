"""
IA Influencer Agent - Content Database System
===========================================

Advanced content database management system for fingerprinting and content protection.
Provides scalable storage, indexing, and retrieval of content fingerprints and metadata.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from pathlib import Path
import numpy as np

# Database imports
import asyncpg
import aioredis
import motor.motor_asyncio
from elasticsearch import AsyncElasticsearch
import sqlite3
import aiosqlite

# Internal imports
from .config import FingerprintingSystemConfig
from .metadata import ContentMetadata, ContentType
from .audio_fingerprinter import AudioFingerprint
from .video_fingerprint import VideoFingerprint
from .image_fingerprint import ImageFingerprint
from .text_fingerprint import TextFingerprint

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    REDIS = "redis"
    SQLITE = "sqlite"


class IndexType(Enum):
    """Database index types"""
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    VECTOR = "vector"
    FULLTEXT = "fulltext"


class StorageFormat(Enum):
    """Content storage formats"""
    JSON = "json"
    BINARY = "binary"
    COMPRESSED = "compressed"
    ENCRYPTED = "encrypted"


@dataclass
class DatabaseConnection:
    """Database connection configuration"""
    db_type: DatabaseType
    connection_string: str
    pool_size: int = 10
    max_overflow: int = 20
    timeout: int = 30
    ssl_required: bool = False
    credentials: Dict[str, str] = field(default_factory=dict)
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentRecord:
    """Content database record"""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fingerprint_id: str = ""
    content_id: str = ""
    content_type: ContentType = ContentType.TEXT
    owner_id: str = ""
    
    # Fingerprint data
    audio_fingerprint: Optional[Dict[str, Any]] = None
    video_fingerprint: Optional[Dict[str, Any]] = None
    image_fingerprint: Optional[Dict[str, Any]] = None
    text_fingerprint: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Optional[ContentMetadata] = None
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Protection info
    protection_enabled: bool = True
    monitoring_active: bool = True
    copyright_info: Dict[str, Any] = field(default_factory=dict)
    licensing_info: Dict[str, Any] = field(default_factory=dict)
    
    # Vector embeddings for similarity search
    vector_embedding: Optional[bytes] = None
    embedding_dimension: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Status and flags
    status: str = "active"
    tags: List[str] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)


@dataclass
class QueryFilter:
    """Database query filter"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, like, exists
    value: Any
    case_sensitive: bool = True


@dataclass
class QueryOptions:
    """Database query options"""
    filters: List[QueryFilter] = field(default_factory=list)
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # asc, desc
    limit: Optional[int] = None
    offset: int = 0
    include_vectors: bool = False
    include_metadata: bool = True


@dataclass
class DatabaseStats:
    """Database statistics"""
    total_records: int = 0
    records_by_type: Dict[str, int] = field(default_factory=dict)
    records_by_owner: Dict[str, int] = field(default_factory=dict)
    storage_size_bytes: int = 0
    index_size_bytes: int = 0
    avg_query_time_ms: float = 0.0
    total_queries: int = 0
    cache_hit_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ContentDatabaseManager:
    """Advanced content database management system"""
    
    def __init__(self, config: FingerprintingSystemConfig):
        self.config = config
        
        # Database connections
        self.connections: Dict[DatabaseType, Any] = {}
        self.primary_db: Optional[DatabaseType] = None
        
        # Caching
        self.redis_client: Optional[aioredis.Redis] = None
        self.cache_ttl = 3600  # 1 hour
        
        # Connection pools
        self.connection_pools: Dict[DatabaseType, Any] = {}
        
        # Statistics
        self.stats = DatabaseStats()
        
        # Schema management
        self.schema_version = "1.0.0"
        self.migration_history: List[str] = []
        
        logger.info("Content Database Manager initialized")
    
    async def initialize(self):
        """Initialize database connections and schema"""
        try:
            # Initialize primary database (PostgreSQL)
            await self._initialize_postgresql()
            
            # Initialize secondary databases
            await self._initialize_mongodb()
            await self._initialize_elasticsearch()
            await self._initialize_redis()
            
            # Create schema if needed
            await self._ensure_schema()
            
            # Update statistics
            await self._update_statistics()
            
            logger.info("Database system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database system: {str(e)}")
            raise
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            db_url = getattr(self.config, 'postgresql_url', 
                           'postgresql://localhost:5432/fingerprinting')
            
            self.connection_pools[DatabaseType.POSTGRESQL] = await asyncpg.create_pool(
                db_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            self.primary_db = DatabaseType.POSTGRESQL
            self.connections[DatabaseType.POSTGRESQL] = self.connection_pools[DatabaseType.POSTGRESQL]
            
            logger.info("PostgreSQL connection initialized")
            
        except Exception as e:
            logger.warning(f"PostgreSQL initialization failed: {str(e)}")
    
    async def _initialize_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            mongo_url = getattr(self.config, 'mongodb_url', 
                              'mongodb://localhost:27017/fingerprinting')
            
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.get_database()
            
            self.connections[DatabaseType.MONGODB] = db
            
            logger.info("MongoDB connection initialized")
            
        except Exception as e:
            logger.warning(f"MongoDB initialization failed: {str(e)}")
    
    async def _initialize_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        try:
            es_url = getattr(self.config, 'elasticsearch_url', 
                           'http://localhost:9200')
            
            client = AsyncElasticsearch([es_url])
            
            # Test connection
            if await client.ping():
                self.connections[DatabaseType.ELASTICSEARCH] = client
                logger.info("Elasticsearch connection initialized")
            else:
                logger.warning("Elasticsearch ping failed")
                
        except Exception as e:
            logger.warning(f"Elasticsearch initialization failed: {str(e)}")
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_url = getattr(self.config, 'redis_url', 
                              'redis://localhost:6379')
            
            self.redis_client = await aioredis.from_url(
                redis_url, 
                decode_responses=True
            )
            
            self.connections[DatabaseType.REDIS] = self.redis_client
            
            logger.info("Redis connection initialized")
            
        except Exception as e:
            logger.warning(f"Redis initialization failed: {str(e)}")
    
    async def _ensure_schema(self):
        """Ensure database schema exists"""
        if DatabaseType.POSTGRESQL in self.connections:
            await self._create_postgresql_schema()
        
        if DatabaseType.MONGODB in self.connections:
            await self._create_mongodb_schema()
        
        if DatabaseType.ELASTICSEARCH in self.connections:
            await self._create_elasticsearch_schema()
    
    async def _create_postgresql_schema(self):
        """Create PostgreSQL schema"""
        try:
            pool = self.connections[DatabaseType.POSTGRESQL]
            
            async with pool.acquire() as conn:
                # Create main content table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS content_records (
                        record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        fingerprint_id VARCHAR(255) UNIQUE NOT NULL,
                        content_id VARCHAR(255) NOT NULL,
                        content_type VARCHAR(50) NOT NULL,
                        owner_id VARCHAR(255) NOT NULL,
                        
                        audio_fingerprint JSONB,
                        video_fingerprint JSONB,
                        image_fingerprint JSONB,
                        text_fingerprint JSONB,
                        
                        metadata JSONB,
                        technical_metadata JSONB DEFAULT '{}',
                        custom_metadata JSONB DEFAULT '{}',
                        
                        protection_enabled BOOLEAN DEFAULT TRUE,
                        monitoring_active BOOLEAN DEFAULT TRUE,
                        copyright_info JSONB DEFAULT '{}',
                        licensing_info JSONB DEFAULT '{}',
                        
                        vector_embedding BYTEA,
                        embedding_dimension INTEGER DEFAULT 0,
                        
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_accessed TIMESTAMP WITH TIME ZONE,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        
                        status VARCHAR(50) DEFAULT 'active',
                        tags TEXT[] DEFAULT '{}',
                        flags JSONB DEFAULT '{}'
                    )
                """)
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_content_fingerprint_id ON content_records(fingerprint_id)",
                    "CREATE INDEX IF NOT EXISTS idx_content_id ON content_records(content_id)",
                    "CREATE INDEX IF NOT EXISTS idx_content_type ON content_records(content_type)",
                    "CREATE INDEX IF NOT EXISTS idx_owner_id ON content_records(owner_id)",
                    "CREATE INDEX IF NOT EXISTS idx_created_at ON content_records(created_at)",
                    "CREATE INDEX IF NOT EXISTS idx_status ON content_records(status)",
                    "CREATE INDEX IF NOT EXISTS idx_protection_enabled ON content_records(protection_enabled)",
                    "CREATE INDEX IF NOT EXISTS idx_content_tags ON content_records USING GIN(tags)",
                    "CREATE INDEX IF NOT EXISTS idx_metadata ON content_records USING GIN(metadata)",
                    "CREATE INDEX IF NOT EXISTS idx_custom_metadata ON content_records USING GIN(custom_metadata)"
                ]
                
                for index_sql in indexes:
                    await conn.execute(index_sql)
                
                # Create similarity search function
                await conn.execute("""
                    CREATE OR REPLACE FUNCTION cosine_similarity(a BYTEA, b BYTEA)
                    RETURNS FLOAT AS $$
                    BEGIN
                        -- This would implement actual cosine similarity
                        -- For now, return a placeholder
                        RETURN 0.5;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                logger.info("PostgreSQL schema created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL schema: {str(e)}")
    
    async def _create_mongodb_schema(self):
        """Create MongoDB schema"""
        try:
            db = self.connections[DatabaseType.MONGODB]
            collection = db.content_records
            
            # Create indexes
            await collection.create_index("fingerprint_id", unique=True)
            await collection.create_index("content_id")
            await collection.create_index("content_type")
            await collection.create_index("owner_id")
            await collection.create_index("created_at")
            await collection.create_index("status")
            await collection.create_index("tags")
            await collection.create_index([("metadata", "text")])
            
            logger.info("MongoDB schema created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB schema: {str(e)}")
    
    async def _create_elasticsearch_schema(self):
        """Create Elasticsearch schema"""
        try:
            es = self.connections[DatabaseType.ELASTICSEARCH]
            
            # Create index with mapping
            mapping = {
                "mappings": {
                    "properties": {
                        "record_id": {"type": "keyword"},
                        "fingerprint_id": {"type": "keyword"},
                        "content_id": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "owner_id": {"type": "keyword"},
                        "metadata": {"type": "object"},
                        "technical_metadata": {"type": "object"},
                        "custom_metadata": {"type": "object"},
                        "copyright_info": {"type": "object"},
                        "vector_embedding": {"type": "dense_vector", "dims": 512},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "status": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "full_text": {"type": "text", "analyzer": "standard"}
                    }
                }
            }
            
            await es.indices.create(
                index="content_records", 
                body=mapping, 
                ignore=400  # Ignore if already exists
            )
            
            logger.info("Elasticsearch schema created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch schema: {str(e)}")
    
    async def store_content_record(self, record: ContentRecord) -> str:
        """Store content record in database"""
        try:
            record.updated_at = datetime.utcnow()
            
            # Store in primary database
            if self.primary_db == DatabaseType.POSTGRESQL:
                record_id = await self._store_postgresql_record(record)
            else:
                record_id = await self._store_fallback_record(record)
            
            # Store in secondary databases for redundancy
            await self._store_secondary_records(record)
            
            # Cache the record
            await self._cache_record(record)
            
            # Update statistics
            self.stats.total_records += 1
            self.stats.records_by_type[record.content_type.value] = \
                self.stats.records_by_type.get(record.content_type.value, 0) + 1
            
            logger.info(f"Content record stored: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to store content record: {str(e)}")
            raise
    
    async def _store_postgresql_record(self, record: ContentRecord) -> str:
        """Store record in PostgreSQL"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            # Convert fingerprints to JSON
            audio_fp = json.dumps(record.audio_fingerprint) if record.audio_fingerprint else None
            video_fp = json.dumps(record.video_fingerprint) if record.video_fingerprint else None
            image_fp = json.dumps(record.image_fingerprint) if record.image_fingerprint else None
            text_fp = json.dumps(record.text_fingerprint) if record.text_fingerprint else None
            
            # Convert metadata
            metadata_json = json.dumps(record.metadata.to_dict()) if record.metadata else None
            
            result = await conn.fetchrow("""
                INSERT INTO content_records (
                    record_id, fingerprint_id, content_id, content_type, owner_id,
                    audio_fingerprint, video_fingerprint, image_fingerprint, text_fingerprint,
                    metadata, technical_metadata, custom_metadata,
                    protection_enabled, monitoring_active, copyright_info, licensing_info,
                    vector_embedding, embedding_dimension,
                    created_at, updated_at, expires_at,
                    status, tags, flags
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
                    $17, $18, $19, $20, $21, $22, $23, $24
                ) RETURNING record_id
            """,
                record.record_id, record.fingerprint_id, record.content_id, 
                record.content_type.value, record.owner_id,
                audio_fp, video_fp, image_fp, text_fp,
                metadata_json, json.dumps(record.technical_metadata), 
                json.dumps(record.custom_metadata),
                record.protection_enabled, record.monitoring_active,
                json.dumps(record.copyright_info), json.dumps(record.licensing_info),
                record.vector_embedding, record.embedding_dimension,
                record.created_at, record.updated_at, record.expires_at,
                record.status, record.tags, json.dumps(record.flags)
            )
            
            return str(result['record_id'])
    
    async def _store_fallback_record(self, record: ContentRecord) -> str:
        """Store record using fallback method (SQLite)"""
        # This would implement SQLite storage as fallback
        logger.warning("Using fallback storage method")
        return record.record_id
    
    async def _store_secondary_records(self, record: ContentRecord):
        """Store record in secondary databases"""
        # MongoDB storage
        if DatabaseType.MONGODB in self.connections:
            try:
                db = self.connections[DatabaseType.MONGODB]
                collection = db.content_records
                
                doc = asdict(record)
                doc['_id'] = record.record_id
                doc['created_at'] = record.created_at.isoformat()
                doc['updated_at'] = record.updated_at.isoformat()
                if record.expires_at:
                    doc['expires_at'] = record.expires_at.isoformat()
                if record.metadata:
                    doc['metadata'] = record.metadata.to_dict()
                
                await collection.insert_one(doc)
                
            except Exception as e:
                logger.warning(f"MongoDB secondary storage failed: {str(e)}")
        
        # Elasticsearch storage
        if DatabaseType.ELASTICSEARCH in self.connections:
            try:
                es = self.connections[DatabaseType.ELASTICSEARCH]
                
                doc = {
                    'record_id': record.record_id,
                    'fingerprint_id': record.fingerprint_id,
                    'content_id': record.content_id,
                    'content_type': record.content_type.value,
                    'owner_id': record.owner_id,
                    'metadata': record.metadata.to_dict() if record.metadata else {},
                    'technical_metadata': record.technical_metadata,
                    'custom_metadata': record.custom_metadata,
                    'copyright_info': record.copyright_info,
                    'created_at': record.created_at.isoformat(),
                    'updated_at': record.updated_at.isoformat(),
                    'status': record.status,
                    'tags': record.tags
                }
                
                if record.vector_embedding:
                    # Convert bytes to list for Elasticsearch
                    vector = np.frombuffer(record.vector_embedding, dtype=np.float32)
                    doc['vector_embedding'] = vector.tolist()
                
                await es.index(
                    index="content_records",
                    id=record.record_id,
                    body=doc
                )
                
            except Exception as e:
                logger.warning(f"Elasticsearch secondary storage failed: {str(e)}")
    
    async def _cache_record(self, record: ContentRecord):
        """Cache record in Redis"""
        if self.redis_client:
            try:
                cache_key = f"content_record:{record.fingerprint_id}"
                record_dict = asdict(record)
                
                # Convert datetime objects to strings
                for key, value in record_dict.items():
                    if isinstance(value, datetime):
                        record_dict[key] = value.isoformat()
                
                await self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(record_dict, default=str)
                )
                
            except Exception as e:
                logger.warning(f"Cache storage failed: {str(e)}")
    
    async def get_content_record(self, fingerprint_id: str) -> Optional[ContentRecord]:
        """Retrieve content record by fingerprint ID"""
        try:
            # Try cache first
            cached_record = await self._get_cached_record(fingerprint_id)
            if cached_record:
                return cached_record
            
            # Query primary database
            if self.primary_db == DatabaseType.POSTGRESQL:
                record = await self._get_postgresql_record(fingerprint_id)
            else:
                record = await self._get_fallback_record(fingerprint_id)
            
            if record:
                # Update cache
                await self._cache_record(record)
                # Update access time
                record.last_accessed = datetime.utcnow()
                await self._update_access_time(fingerprint_id)
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to retrieve content record: {str(e)}")
            return None
    
    async def _get_cached_record(self, fingerprint_id: str) -> Optional[ContentRecord]:
        """Get record from cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"content_record:{fingerprint_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                record_dict = json.loads(cached_data)
                # TODO: Convert back to ContentRecord object
                # This would require proper deserialization logic
                return None  # Placeholder
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {str(e)}")
        
        return None
    
    async def _get_postgresql_record(self, fingerprint_id: str) -> Optional[ContentRecord]:
        """Get record from PostgreSQL"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM content_records 
                WHERE fingerprint_id = $1
            """, fingerprint_id)
            
            if row:
                # Convert row to ContentRecord
                record = ContentRecord(
                    record_id=str(row['record_id']),
                    fingerprint_id=row['fingerprint_id'],
                    content_id=row['content_id'],
                    content_type=ContentType(row['content_type']),
                    owner_id=row['owner_id'],
                    audio_fingerprint=json.loads(row['audio_fingerprint']) if row['audio_fingerprint'] else None,
                    video_fingerprint=json.loads(row['video_fingerprint']) if row['video_fingerprint'] else None,
                    image_fingerprint=json.loads(row['image_fingerprint']) if row['image_fingerprint'] else None,
                    text_fingerprint=json.loads(row['text_fingerprint']) if row['text_fingerprint'] else None,
                    technical_metadata=json.loads(row['technical_metadata']) if row['technical_metadata'] else {},
                    custom_metadata=json.loads(row['custom_metadata']) if row['custom_metadata'] else {},
                    protection_enabled=row['protection_enabled'],
                    monitoring_active=row['monitoring_active'],
                    copyright_info=json.loads(row['copyright_info']) if row['copyright_info'] else {},
                    licensing_info=json.loads(row['licensing_info']) if row['licensing_info'] else {},
                    vector_embedding=row['vector_embedding'],
                    embedding_dimension=row['embedding_dimension'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_accessed=row['last_accessed'],
                    expires_at=row['expires_at'],
                    status=row['status'],
                    tags=row['tags'] or [],
                    flags=json.loads(row['flags']) if row['flags'] else {}
                )
                
                # Parse metadata if exists
                if row['metadata']:
                    metadata_dict = json.loads(row['metadata'])
                    # TODO: Convert to ContentMetadata object
                    # record.metadata = ContentMetadata.from_dict(metadata_dict)
                
                return record
        
        return None
    
    async def _get_fallback_record(self, fingerprint_id: str) -> Optional[ContentRecord]:
        """Get record using fallback method"""
        # This would implement SQLite or file-based retrieval
        return None
    
    async def query_content_records(
        self, 
        options: QueryOptions
    ) -> List[ContentRecord]:
        """Query content records with filters"""
        try:
            if self.primary_db == DatabaseType.POSTGRESQL:
                return await self._query_postgresql_records(options)
            else:
                return await self._query_fallback_records(options)
                
        except Exception as e:
            logger.error(f"Failed to query content records: {str(e)}")
            return []
    
    async def _query_postgresql_records(self, options: QueryOptions) -> List[ContentRecord]:
        """Query PostgreSQL records"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        # Build query
        where_clauses = []
        params = []
        param_count = 0
        
        for filter_item in options.filters:
            param_count += 1
            if filter_item.operator == 'eq':
                where_clauses.append(f"{filter_item.field} = ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'ne':
                where_clauses.append(f"{filter_item.field} != ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'gt':
                where_clauses.append(f"{filter_item.field} > ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'gte':
                where_clauses.append(f"{filter_item.field} >= ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'lt':
                where_clauses.append(f"{filter_item.field} < ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'lte':
                where_clauses.append(f"{filter_item.field} <= ${param_count}")
                params.append(filter_item.value)
            elif filter_item.operator == 'in':
                placeholders = ','.join([f"${i}" for i in range(param_count, param_count + len(filter_item.value))])
                where_clauses.append(f"{filter_item.field} IN ({placeholders})")
                params.extend(filter_item.value)
                param_count += len(filter_item.value) - 1
            elif filter_item.operator == 'like':
                where_clauses.append(f"{filter_item.field} LIKE ${param_count}")
                params.append(filter_item.value)
        
        # Build complete query
        query = "SELECT * FROM content_records"
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        if options.sort_by:
            query += f" ORDER BY {options.sort_by} {options.sort_order.upper()}"
        
        if options.limit:
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(options.limit)
        
        if options.offset > 0:
            param_count += 1
            query += f" OFFSET ${param_count}"
            params.append(options.offset)
        
        # Execute query
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            records = []
            for row in rows:
                # Convert row to ContentRecord (similar to _get_postgresql_record)
                record = self._row_to_content_record(row)
                records.append(record)
            
            return records
    
    def _row_to_content_record(self, row) -> ContentRecord:
        """Convert database row to ContentRecord"""
        # This would implement the conversion logic
        # Similar to _get_postgresql_record but as a separate method
        return ContentRecord(
            record_id=str(row['record_id']),
            fingerprint_id=row['fingerprint_id'],
            content_id=row['content_id'],
            content_type=ContentType(row['content_type']),
            owner_id=row['owner_id']
            # ... other fields
        )
    
    async def _query_fallback_records(self, options: QueryOptions) -> List[ContentRecord]:
        """Query records using fallback method"""
        # This would implement SQLite or file-based querying
        return []
    
    async def update_content_record(
        self, 
        fingerprint_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update content record"""
        try:
            updates['updated_at'] = datetime.utcnow()
            
            if self.primary_db == DatabaseType.POSTGRESQL:
                success = await self._update_postgresql_record(fingerprint_id, updates)
            else:
                success = await self._update_fallback_record(fingerprint_id, updates)
            
            if success:
                # Update cache
                await self._invalidate_cache(fingerprint_id)
                
                # Update secondary databases
                await self._update_secondary_records(fingerprint_id, updates)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update content record: {str(e)}")
            return False
    
    async def _update_postgresql_record(
        self, 
        fingerprint_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update PostgreSQL record"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        # Build update query
        set_clauses = []
        params = []
        param_count = 0
        
        for field, value in updates.items():
            param_count += 1
            set_clauses.append(f"{field} = ${param_count}")
            
            # Handle JSON fields
            if field in ['metadata', 'technical_metadata', 'custom_metadata', 
                        'copyright_info', 'licensing_info', 'flags']:
                params.append(json.dumps(value))
            else:
                params.append(value)
        
        param_count += 1
        params.append(fingerprint_id)
        
        query = f"""
            UPDATE content_records 
            SET {', '.join(set_clauses)}
            WHERE fingerprint_id = ${param_count}
        """
        
        async with pool.acquire() as conn:
            result = await conn.execute(query, *params)
            return result == "UPDATE 1"
    
    async def _update_fallback_record(
        self, 
        fingerprint_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update record using fallback method"""
        # This would implement SQLite or file-based updates
        return False
    
    async def _update_secondary_records(
        self, 
        fingerprint_id: str, 
        updates: Dict[str, Any]
    ):
        """Update records in secondary databases"""
        # MongoDB update
        if DatabaseType.MONGODB in self.connections:
            try:
                db = self.connections[DatabaseType.MONGODB]
                collection = db.content_records
                
                await collection.update_one(
                    {'fingerprint_id': fingerprint_id},
                    {'$set': updates}
                )
                
            except Exception as e:
                logger.warning(f"MongoDB update failed: {str(e)}")
        
        # Elasticsearch update
        if DatabaseType.ELASTICSEARCH in self.connections:
            try:
                es = self.connections[DatabaseType.ELASTICSEARCH]
                
                await es.update(
                    index="content_records",
                    id=fingerprint_id,
                    body={'doc': updates}
                )
                
            except Exception as e:
                logger.warning(f"Elasticsearch update failed: {str(e)}")
    
    async def delete_content_record(self, fingerprint_id: str) -> bool:
        """Delete content record"""
        try:
            if self.primary_db == DatabaseType.POSTGRESQL:
                success = await self._delete_postgresql_record(fingerprint_id)
            else:
                success = await self._delete_fallback_record(fingerprint_id)
            
            if success:
                # Remove from cache
                await self._invalidate_cache(fingerprint_id)
                
                # Delete from secondary databases
                await self._delete_secondary_records(fingerprint_id)
                
                # Update statistics
                self.stats.total_records = max(0, self.stats.total_records - 1)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete content record: {str(e)}")
            return False
    
    async def _delete_postgresql_record(self, fingerprint_id: str) -> bool:
        """Delete PostgreSQL record"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM content_records WHERE fingerprint_id = $1",
                fingerprint_id
            )
            return result == "DELETE 1"
    
    async def _delete_fallback_record(self, fingerprint_id: str) -> bool:
        """Delete record using fallback method"""
        return False
    
    async def _delete_secondary_records(self, fingerprint_id: str):
        """Delete records from secondary databases"""
        # MongoDB deletion
        if DatabaseType.MONGODB in self.connections:
            try:
                db = self.connections[DatabaseType.MONGODB]
                collection = db.content_records
                
                await collection.delete_one({'fingerprint_id': fingerprint_id})
                
            except Exception as e:
                logger.warning(f"MongoDB deletion failed: {str(e)}")
        
        # Elasticsearch deletion
        if DatabaseType.ELASTICSEARCH in self.connections:
            try:
                es = self.connections[DatabaseType.ELASTICSEARCH]
                
                await es.delete(
                    index="content_records",
                    id=fingerprint_id
                )
                
            except Exception as e:
                logger.warning(f"Elasticsearch deletion failed: {str(e)}")
    
    async def find_similar_content(
        self, 
        vector_embedding: bytes, 
        threshold: float = 0.8,
        limit: int = 10
    ) -> List[Tuple[ContentRecord, float]]:
        """Find similar content using vector similarity"""
        try:
            if DatabaseType.ELASTICSEARCH in self.connections:
                return await self._find_similar_elasticsearch(vector_embedding, threshold, limit)
            elif self.primary_db == DatabaseType.POSTGRESQL:
                return await self._find_similar_postgresql(vector_embedding, threshold, limit)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to find similar content: {str(e)}")
            return []
    
    async def _find_similar_elasticsearch(
        self, 
        vector_embedding: bytes, 
        threshold: float, 
        limit: int
    ) -> List[Tuple[ContentRecord, float]]:
        """Find similar content using Elasticsearch"""
        es = self.connections[DatabaseType.ELASTICSEARCH]
        
        # Convert bytes to vector
        query_vector = np.frombuffer(vector_embedding, dtype=np.float32).tolist()
        
        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector_embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            "size": limit
        }
        
        response = await es.search(index="content_records", body=query)
        
        results = []
        for hit in response['hits']['hits']:
            similarity = (hit['_score'] - 1.0)  # Convert back from Elasticsearch score
            if similarity >= threshold:
                # Convert hit to ContentRecord
                record = self._hit_to_content_record(hit['_source'])
                results.append((record, similarity))
        
        return results
    
    async def _find_similar_postgresql(
        self, 
        vector_embedding: bytes, 
        threshold: float, 
        limit: int
    ) -> List[Tuple[ContentRecord, float]]:
        """Find similar content using PostgreSQL"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            # This would use a more sophisticated similarity function
            rows = await conn.fetch("""
                SELECT *, cosine_similarity(vector_embedding, $1) as similarity
                FROM content_records
                WHERE vector_embedding IS NOT NULL
                AND cosine_similarity(vector_embedding, $1) >= $2
                ORDER BY similarity DESC
                LIMIT $3
            """, vector_embedding, threshold, limit)
            
            results = []
            for row in rows:
                record = self._row_to_content_record(row)
                similarity = float(row['similarity'])
                results.append((record, similarity))
            
            return results
    
    def _hit_to_content_record(self, hit_source: Dict[str, Any]) -> ContentRecord:
        """Convert Elasticsearch hit to ContentRecord"""
        # This would implement the conversion logic
        return ContentRecord(
            record_id=hit_source.get('record_id', ''),
            fingerprint_id=hit_source.get('fingerprint_id', ''),
            content_id=hit_source.get('content_id', ''),
            content_type=ContentType(hit_source.get('content_type', 'text')),
            owner_id=hit_source.get('owner_id', '')
            # ... other fields
        )
    
    async def _update_access_time(self, fingerprint_id: str):
        """Update last access time for record"""
        await self.update_content_record(
            fingerprint_id,
            {'last_accessed': datetime.utcnow()}
        )
    
    async def _invalidate_cache(self, fingerprint_id: str):
        """Invalidate cached record"""
        if self.redis_client:
            try:
                cache_key = f"content_record:{fingerprint_id}"
                await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Cache invalidation failed: {str(e)}")
    
    async def _update_statistics(self):
        """Update database statistics"""
        try:
            if self.primary_db == DatabaseType.POSTGRESQL:
                await self._update_postgresql_stats()
            
            self.stats.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {str(e)}")
    
    async def _update_postgresql_stats(self):
        """Update PostgreSQL statistics"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            # Total records
            total = await conn.fetchval("SELECT COUNT(*) FROM content_records")
            self.stats.total_records = total
            
            # Records by type
            type_counts = await conn.fetch("""
                SELECT content_type, COUNT(*) as count
                FROM content_records
                GROUP BY content_type
            """)
            self.stats.records_by_type = {
                row['content_type']: row['count'] for row in type_counts
            }
            
            # Records by owner
            owner_counts = await conn.fetch("""
                SELECT owner_id, COUNT(*) as count
                FROM content_records
                GROUP BY owner_id
                ORDER BY count DESC
                LIMIT 100
            """)
            self.stats.records_by_owner = {
                row['owner_id']: row['count'] for row in owner_counts
            }
    
    async def get_statistics(self) -> DatabaseStats:
        """Get current database statistics"""
        await self._update_statistics()
        return self.stats
    
    async def cleanup_expired_records(self) -> int:
        """Clean up expired records"""
        try:
            current_time = datetime.utcnow()
            
            if self.primary_db == DatabaseType.POSTGRESQL:
                deleted_count = await self._cleanup_postgresql_expired(current_time)
            else:
                deleted_count = 0
            
            logger.info(f"Cleaned up {deleted_count} expired records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired records: {str(e)}")
            return 0
    
    async def _cleanup_postgresql_expired(self, current_time: datetime) -> int:
        """Clean up expired PostgreSQL records"""
        pool = self.connections[DatabaseType.POSTGRESQL]
        
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM content_records
                WHERE expires_at IS NOT NULL AND expires_at < $1
            """, current_time)
            
            # Extract number from result string like "DELETE 5"
            return int(result.split()[-1]) if result.startswith("DELETE") else 0
    
    async def close(self):
        """Close all database connections"""
        try:
            # Close PostgreSQL pool
            if DatabaseType.POSTGRESQL in self.connection_pools:
                await self.connection_pools[DatabaseType.POSTGRESQL].close()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close Elasticsearch connection
            if DatabaseType.ELASTICSEARCH in self.connections:
                await self.connections[DatabaseType.ELASTICSEARCH].close()
            
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")


# Global content database manager instance
_content_db_manager: Optional[ContentDatabaseManager] = None


def get_content_database_manager(config: Optional[FingerprintingSystemConfig] = None) -> ContentDatabaseManager:
    """Get or create content database manager instance"""
    global _content_db_manager
    
    if _content_db_manager is None:
        if config is None:
            from .config import get_config
            config = get_config()
        _content_db_manager = ContentDatabaseManager(config)
    
    return _content_db_manager


def reset_content_database_manager():
    """Reset content database manager (for testing)"""
    global _content_db_manager
    if _content_db_manager:
        asyncio.create_task(_content_db_manager.close())
    _content_db_manager = None


# Convenience functions
async def store_fingerprint(
    fingerprint_id: str,
    content_id: str,
    content_type: ContentType,
    owner_id: str,
    fingerprint_data: Dict[str, Any],
    metadata: Optional[ContentMetadata] = None,
    **kwargs
) -> str:
    """Store fingerprint convenience function"""
    manager = get_content_database_manager()
    
    record = ContentRecord(
        fingerprint_id=fingerprint_id,
        content_id=content_id,
        content_type=content_type,
        owner_id=owner_id,
        metadata=metadata,
        **kwargs
    )
    
    # Set appropriate fingerprint data based on content type
    if content_type == ContentType.AUDIO:
        record.audio_fingerprint = fingerprint_data
    elif content_type == ContentType.VIDEO:
        record.video_fingerprint = fingerprint_data
    elif content_type == ContentType.IMAGE:
        record.image_fingerprint = fingerprint_data
    elif content_type == ContentType.TEXT:
        record.text_fingerprint = fingerprint_data
    
    return await manager.store_content_record(record)


async def find_fingerprint(fingerprint_id: str) -> Optional[ContentRecord]:
    """Find fingerprint convenience function"""
    manager = get_content_database_manager()
    return await manager.get_content_record(fingerprint_id)
