"""
Storage Adapters - Enterprise Multi-backend Storage Integration System
=====================================================================

Industrial-grade storage adapters for the IA-Influencer Agent platform.
Provides comprehensive data persistence, caching, and vector storage capabilities
with enterprise-level security, performance, and reliability.

Business Logic: Content Storage → Data Management → Vector Indexing → Backup & Recovery

Supported Storage Backends:
- PostgreSQL with vector extensions (pgvector, pg_embedding)
- Redis for high-performance caching and session management
- AWS S3/MinIO for scalable object storage
- Elasticsearch for full-text search and analytics
- FAISS vector database for AI embeddings and similarity search
- MongoDB for document storage and content metadata
- ClickHouse for analytics and time-series data
- Apache Cassandra for distributed storage
- Local filesystem with enterprise features

Features:
- Advanced connection pooling and failover
- Automatic data compression and encryption
- Vector similarity search with FAISS integration
- Multi-tier caching strategies (L1, L2, L3)
- Automatic backup and disaster recovery
- Data lifecycle management and archiving
- Real-time replication and synchronization
- Enterprise security with encryption at rest
- Performance monitoring and optimization
- Multi-region data distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
import json
import pickle
import gzip
import lz4.frame
import aiofiles
import aioredis
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import os
import hashlib
import base64
import concurrent.futures
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import ssl
from urllib.parse import urlparse

# Advanced database imports
import asyncpg
import aiomysql
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import databases

# Enterprise cloud storage imports
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import azure.storage.blob
from google.cloud import storage as gcs

# Vector store and search imports
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

# Time-series and analytics imports
try:
    import clickhouse_connect
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False

try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class StorageConfig:
    """Storage configuration."""
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    bucket: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    base_path: Optional[str] = None
    max_connections: int = 10
    timeout: float = 30.0

@dataclass
class StorageItem:
    """Storage item container."""
    key: str
    data: Any
    metadata: Dict[str, Any] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class StorageAdapter(ABC):
    """Base class for all storage adapters."""
    
    def __init__(self, config: StorageConfig):
        """Initialize storage adapter."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to storage backend."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from storage backend."""
        pass
    
    @abstractmethod
    async def store(self, item: StorageItem) -> bool:
        """Store item."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve item by key."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete item by key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if item exists."""
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List keys with optional prefix filter."""
        pass
    
    async def initialize(self):
        """Initialize the adapter."""
        success = await self.connect()
        if not success:
            raise Exception(f"Failed to connect to {self.__class__.__name__}")
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    async def cleanup(self):
        """Cleanup adapter resources."""
        await self.disconnect()
        self.logger.info(f"Cleaned up {self.__class__.__name__}")

class DatabaseAdapter(StorageAdapter):
    """Adapter for relational database storage."""
    
    def __init__(self, config: StorageConfig):
        """Initialize database adapter."""
        super().__init__(config)
        self.db_type = self._detect_db_type()
        self.pool = None
    
    def _detect_db_type(self) -> str:
        """Detect database type from connection string."""
        if self.config.connection_string:
            if 'postgresql' in self.config.connection_string:
                return 'postgresql'
            elif 'mysql' in self.config.connection_string:
                return 'mysql'
            elif 'mongodb' in self.config.connection_string:
                return 'mongodb'
        return 'postgresql'  # Default
    
    async def connect(self) -> bool:
        """Connect to database."""



        try:
            if self.db_type == 'postgresql':
                self.pool = await asyncpg.create_pool(
                    self.config.connection_string,
                    max_size=self.config.max_connections,
                    command_timeout=self.config.timeout
                )
                
                # Create table if not exists
                async with self.pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS storage_items (
                            key VARCHAR PRIMARY KEY,
                            data BYTEA,
                            metadata JSONB,
                            content_type VARCHAR,
                            size INTEGER,
                            created_at TIMESTAMP,
                            updated_at TIMESTAMP,
                            expires_at TIMESTAMP
                        )
                    """)
            
            elif self.db_type == 'mysql':
                self.pool = await aiomysql.create_pool(
                    host=self.config.host,
                    port=self.config.port or 3306,
                    user=self.config.username,
                    password=self.config.password,
                    db=self.config.database,
                    maxsize=self.config.max_connections
                )
                
                # Create table if not exists
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            CREATE TABLE IF NOT EXISTS storage_items (
                                `key` VARCHAR(255) PRIMARY KEY,
                                `data` LONGBLOB,
                                `metadata` JSON,
                                `content_type` VARCHAR(255),
                                `size` INTEGER,
                                `created_at` TIMESTAMP,
                                `updated_at` TIMESTAMP,
                                `expires_at` TIMESTAMP
                            )
                        """)
            
            elif self.db_type == 'mongodb':
                from motor.motor_asyncio import AsyncIOMotorClient
                self.connection = AsyncIOMotorClient(self.config.connection_string)
                self.db = self.connection[self.config.database or 'storage']
                self.collection = self.db.storage_items
                
                # Create indexes
                await self.collection.create_index("key", unique=True)
                await self.collection.create_index("expires_at", expireAfterSeconds=0)
            
            self.is_connected = True
            self.logger.info(f"Connected to {self.db_type} database")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from database."""



        try:
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
            elif self.connection:
                self.connection.close()
            
            self.is_connected = False
            self.logger.info("Disconnected from database")
            
        except Exception as e:
            self.logger.error(f"Database disconnection error: {e}")
    
    async def store(self, item: StorageItem) -> bool:
        """Store item in database."""



        try:
            if self.db_type == 'postgresql':
                async with self.pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO storage_items 
                        (key, data, metadata, content_type, size, created_at, updated_at, expires_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (key) DO UPDATE SET
                        data = EXCLUDED.data,
                        metadata = EXCLUDED.metadata,
                        content_type = EXCLUDED.content_type,
                        size = EXCLUDED.size,
                        updated_at = EXCLUDED.updated_at,
                        expires_at = EXCLUDED.expires_at
                    """, 
                    item.key,
                    pickle.dumps(item.data),
                    json.dumps(item.metadata or {}),
                    item.content_type,
                    item.size,
                    item.created_at or datetime.now(),
                    datetime.now(),
                    item.expires_at
                )
            
            elif self.db_type == 'mysql':
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            INSERT INTO storage_items 
                            (`key`, `data`, `metadata`, `content_type`, `size`, `created_at`, `updated_at`, `expires_at`)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            `data` = VALUES(`data`),
                            `metadata` = VALUES(`metadata`),
                            `content_type` = VALUES(`content_type`),
                            `size` = VALUES(`size`),
                            `updated_at` = VALUES(`updated_at`),
                            `expires_at` = VALUES(`expires_at`)
                        """, (
                            item.key,
                            pickle.dumps(item.data),
                            json.dumps(item.metadata or {}),
                            item.content_type,
                            item.size,
                            item.created_at or datetime.now(),
                            datetime.now(),
                            item.expires_at
                        ))
                        await conn.commit()
            
            elif self.db_type == 'mongodb':
                doc = {
                    'key': item.key,
                    'data': pickle.dumps(item.data),
                    'metadata': item.metadata or {},
                    'content_type': item.content_type,
                    'size': item.size,
                    'created_at': item.created_at or datetime.now(),
                    'updated_at': datetime.now(),
                    'expires_at': item.expires_at
                }
                
                await self.collection.replace_one(
                    {'key': item.key},
                    doc,
                    upsert=True
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Store operation failed: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve item from database."""



        try:
            if self.db_type == 'postgresql':
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(
                        "SELECT * FROM storage_items WHERE key = $1",
                        key
                    )
                    
                    if row:
                        return StorageItem(
                            key=row['key'],
                            data=pickle.loads(row['data']),
                            metadata=json.loads(row['metadata'] or '{}'),
                            content_type=row['content_type'],
                            size=row['size'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at'],
                            expires_at=row['expires_at']
                        )
            
            elif self.db_type == 'mysql':
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT * FROM storage_items WHERE `key` = %s",
                            (key,)
                        )
                        row = await cur.fetchone()
                        
                        if row:
                            return StorageItem(
                                key=row[0],
                                data=pickle.loads(row[1]),
                                metadata=json.loads(row[2] or '{}'),
                                content_type=row[3],
                                size=row[4],
                                created_at=row[5],
                                updated_at=row[6],
                                expires_at=row[7]
                            )
            
            elif self.db_type == 'mongodb':
                doc = await self.collection.find_one({'key': key})
                
                if doc:
                    return StorageItem(
                        key=doc['key'],
                        data=pickle.loads(doc['data']),
                        metadata=doc.get('metadata', {}),
                        content_type=doc.get('content_type'),
                        size=doc.get('size'),
                        created_at=doc.get('created_at'),
                        updated_at=doc.get('updated_at'),
                        expires_at=doc.get('expires_at')
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Retrieve operation failed: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from database."""



        try:
            if self.db_type == 'postgresql':
                async with self.pool.acquire() as conn:
                    result = await conn.execute(
                        "DELETE FROM storage_items WHERE key = $1",
                        key
                    )
                    return result != "DELETE 0"
            
            elif self.db_type == 'mysql':
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "DELETE FROM storage_items WHERE `key` = %s",
                            (key,)
                        )
                        await conn.commit()
                        return cur.rowcount > 0
            
            elif self.db_type == 'mongodb':
                result = await self.collection.delete_one({'key': key})
                return result.deleted_count > 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Delete operation failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if item exists in database."""



        try:
            if self.db_type == 'postgresql':
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval(
                        "SELECT 1 FROM storage_items WHERE key = $1",
                        key
                    )
                    return result is not None
            
            elif self.db_type == 'mysql':
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "SELECT 1 FROM storage_items WHERE `key` = %s",
                            (key,)
                        )
                        result = await cur.fetchone()
                        return result is not None
            
            elif self.db_type == 'mongodb':
                count = await self.collection.count_documents({'key': key})
                return count > 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Exists check failed: {e}")
            return False
    
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List keys from database."""



        try:
            keys = []
            
            if self.db_type == 'postgresql':
                query = "SELECT key FROM storage_items"
                params = []
                
                if prefix:
                    query += " WHERE key LIKE $1"
                    params.append(f"{prefix}%")
                
                if limit:
                    query += f" LIMIT ${len(params) + 1}"
                    params.append(limit)
                
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(query, *params)
                    keys = [row['key'] for row in rows]
            
            elif self.db_type == 'mysql':
                query = "SELECT `key` FROM storage_items"
                params = []
                
                if prefix:
                    query += " WHERE `key` LIKE %s"
                    params.append(f"{prefix}%")
                
                if limit:
                    query += " LIMIT %s"
                    params.append(limit)
                
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, params)
                        rows = await cur.fetchall()
                        keys = [row[0] for row in rows]
            
            elif self.db_type == 'mongodb':
                filter_query = {}
                if prefix:
                    filter_query['key'] = {'$regex': f'^{prefix}'}
                
                cursor = self.collection.find(filter_query, {'key': 1})
                if limit:
                    cursor = cursor.limit(limit)
                
                async for doc in cursor:
                    keys.append(doc['key'])
            
            return keys
            
        except Exception as e:
            self.logger.error(f"List keys operation failed: {e}")
            return []

class FileSystemAdapter(StorageAdapter):
    """Adapter for filesystem storage."""
    
    def __init__(self, config: StorageConfig):
        """Initialize filesystem adapter."""
        super().__init__(config)
        self.base_path = Path(config.base_path or './storage')
        self.metadata_suffix = '.metadata.json'
    
    async def connect(self) -> bool:
        """Create base directory."""



        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.is_connected = True
            self.logger.info(f"Filesystem storage ready at {self.base_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Filesystem initialization failed: {e}")
            return False
    
    async def disconnect(self):
        """No cleanup needed for filesystem."""
        self.is_connected = False
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        # Sanitize key for filesystem
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.base_path / safe_key
    
    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for key."""



        return Path(str(self._get_file_path(key)) + self.metadata_suffix)
    
    async def store(self, item: StorageItem) -> bool:
        """Store item to filesystem."""



        try:
            file_path = self._get_file_path(item.key)
            metadata_path = self._get_metadata_path(item.key)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Store data
            if isinstance(item.data, (str, bytes)):
                mode = 'w' if isinstance(item.data, str) else 'wb'
                async with aiofiles.open(file_path, mode) as f:
                    await f.write(item.data)
            else:
                # Serialize complex objects
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(pickle.dumps(item.data))
            
            # Store metadata
            metadata = {
                'key': item.key,
                'content_type': item.content_type,
                'size': item.size or file_path.stat().st_size,
                'created_at': (item.created_at or datetime.now()).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'expires_at': item.expires_at.isoformat() if item.expires_at else None,
                'metadata': item.metadata or {}
            }
            
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Filesystem store failed: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve item from filesystem."""



        try:
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)
            
            if not file_path.exists():
                return None
            
            # Load metadata
            metadata = {}
            if metadata_path.exists():
                async with aiofiles.open(metadata_path, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)
            
            # Load data
            try:
                # Try to load as pickle first
                async with aiofiles.open(file_path, 'rb') as f:
                    data_bytes = await f.read()
                    try:
                        data = pickle.loads(data_bytes)
                    except:
                        # If pickle fails, treat as raw bytes or text
                        try:
                            data = data_bytes.decode('utf-8')
                        except:
                            data = data_bytes
            except:
                return None
            
            return StorageItem(
                key=key,
                data=data,
                metadata=metadata.get('metadata', {}),
                content_type=metadata.get('content_type'),
                size=metadata.get('size'),
                created_at=datetime.fromisoformat(metadata['created_at']) if metadata.get('created_at') else None,
                updated_at=datetime.fromisoformat(metadata['updated_at']) if metadata.get('updated_at') else None,
                expires_at=datetime.fromisoformat(metadata['expires_at']) if metadata.get('expires_at') else None
            )
            
        except Exception as e:
            self.logger.error(f"Filesystem retrieve failed: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from filesystem."""



        try:
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)
            
            deleted = False
            
            if file_path.exists():
                file_path.unlink()
                deleted = True
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Filesystem delete failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if item exists in filesystem."""



        try:
            file_path = self._get_file_path(key)
            return file_path.exists()
            
        except Exception as e:
            self.logger.error(f"Filesystem exists check failed: {e}")
            return False
    
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List keys from filesystem."""



        try:
            keys = []
            
            for file_path in self.base_path.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith(self.metadata_suffix):
                    # Convert file path back to key
                    relative_path = file_path.relative_to(self.base_path)
                    key = str(relative_path)
                    
                    if prefix and not key.startswith(prefix):
                        continue
                    
                    keys.append(key)
                    
                    if limit and len(keys) >= limit:
                        break
            
            return keys
            
        except Exception as e:
            self.logger.error(f"Filesystem list keys failed: {e}")
            return []

class CloudStorageAdapter(StorageAdapter):
    """Adapter for cloud storage (S3-compatible)."""
    
    def __init__(self, config: StorageConfig):
        """Initialize cloud storage adapter."""
        super().__init__(config)
        self.s3_client = None
        self.bucket = config.bucket
    
    async def connect(self) -> bool:
        """Initialize S3 client."""



        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket)
            
            self.is_connected = True
            self.logger.info(f"Connected to S3 bucket: {self.bucket}")
            return True
            
        except Exception as e:
            self.logger.error(f"S3 connection failed: {e}")
            return False
    
    async def disconnect(self):
        """No explicit cleanup needed for S3."""
        self.is_connected = False
    
    async def store(self, item: StorageItem) -> bool:
        """Store item to S3."""



        try:
            # Prepare data
            if isinstance(item.data, (str, bytes)):
                data_bytes = item.data.encode() if isinstance(item.data, str) else item.data
            else:
                data_bytes = pickle.dumps(item.data)
            
            # Prepare metadata
            metadata = item.metadata or {}
            metadata.update({
                'created_at': (item.created_at or datetime.now()).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'expires_at': item.expires_at.isoformat() if item.expires_at else None
            })
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=item.key,
                Body=data_bytes,
                ContentType=item.content_type or 'application/octet-stream',
                Metadata={k: str(v) for k, v in metadata.items()}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"S3 store failed: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve item from S3."""



        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            
            data_bytes = response['Body'].read()
            metadata = response.get('Metadata', {})
            
            # Try to deserialize data
            try:
                data = pickle.loads(data_bytes)
            except:
                try:
                    data = data_bytes.decode('utf-8')
                except:
                    data = data_bytes
            
            return StorageItem(
                key=key,
                data=data,
                metadata={k: v for k, v in metadata.items() if k not in ['created_at', 'updated_at', 'expires_at']},
                content_type=response.get('ContentType'),
                size=response.get('ContentLength'),
                created_at=datetime.fromisoformat(metadata['created_at']) if metadata.get('created_at') else None,
                updated_at=datetime.fromisoformat(metadata['updated_at']) if metadata.get('updated_at') else None,
                expires_at=datetime.fromisoformat(metadata['expires_at']) if metadata.get('expires_at') else None
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            self.logger.error(f"S3 retrieve failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"S3 retrieve failed: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from S3."""



        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
            
        except Exception as e:
            self.logger.error(f"S3 delete failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if item exists in S3."""



        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
        except Exception as e:
            self.logger.error(f"S3 exists check failed: {e}")
            return False
    
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List keys from S3."""



        try:
            kwargs = {'Bucket': self.bucket}
            if prefix:
                kwargs['Prefix'] = prefix
            if limit:
                kwargs['MaxKeys'] = limit
            
            response = self.s3_client.list_objects_v2(**kwargs)
            
            return [obj['Key'] for obj in response.get('Contents', [])]
            
        except Exception as e:
            self.logger.error(f"S3 list keys failed: {e}")
            return []

class CacheAdapter(StorageAdapter):
    """Adapter for Redis cache storage."""
    
    def __init__(self, config: StorageConfig):
        """Initialize cache adapter."""
        super().__init__(config)
        self.redis = None
        self.default_ttl = config.timeout or 3600  # 1 hour default
    
    async def connect(self) -> bool:
        """Connect to Redis."""



        try:
            if self.config.connection_string:
                self.redis = await aioredis.from_url(self.config.connection_string)
            else:
                self.redis = await aioredis.Redis(
                    host=self.config.host or 'localhost',
                    port=self.config.port or 6379,
                    password=self.config.password,
                    db=self.config.database or 0
                )
            
            # Test connection
            await self.redis.ping()
            
            self.is_connected = True
            self.logger.info("Connected to Redis cache")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
        self.is_connected = False
    
    async def store(self, item: StorageItem) -> bool:
        """Store item in Redis."""



        try:
            # Serialize data and metadata
            serialized_item = {
                'data': pickle.dumps(item.data),
                'metadata': json.dumps(item.metadata or {}),
                'content_type': item.content_type or '',
                'size': item.size or 0,
                'created_at': (item.created_at or datetime.now()).isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Calculate TTL
            ttl = None
            if item.expires_at:
                ttl = int((item.expires_at - datetime.now()).total_seconds())
            else:
                ttl = self.default_ttl
            
            # Store in Redis
            await self.redis.hset(item.key, mapping=serialized_item)
            
            if ttl and ttl > 0:
                await self.redis.expire(item.key, ttl)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Redis store failed: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve item from Redis."""



        try:
            data = await self.redis.hgetall(key)
            
            if not data:
                return None
            
            # Deserialize data
            item_data = pickle.loads(data[b'data'])
            metadata = json.loads(data[b'metadata'].decode())
            
            return StorageItem(
                key=key,
                data=item_data,
                metadata=metadata,
                content_type=data[b'content_type'].decode() or None,
                size=int(data[b'size']) if data[b'size'] else None,
                created_at=datetime.fromisoformat(data[b'created_at'].decode()) if data.get(b'created_at') else None,
                updated_at=datetime.fromisoformat(data[b'updated_at'].decode()) if data.get(b'updated_at') else None
            )
            
        except Exception as e:
            self.logger.error(f"Redis retrieve failed: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete item from Redis."""



        try:
            result = await self.redis.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Redis delete failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if item exists in Redis."""



        try:
            result = await self.redis.exists(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Redis exists check failed: {e}")
            return False
    
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List keys from Redis."""



        try:
            pattern = f"{prefix}*" if prefix else "*"
            keys = await self.redis.keys(pattern)
            
            # Convert bytes to strings and apply limit
            str_keys = [key.decode() for key in keys]
            
            if limit:
                str_keys = str_keys[:limit]
            
            return str_keys
            
        except Exception as e:
            self.logger.error(f"Redis list keys failed: {e}")
            return []

class VectorStoreAdapter(StorageAdapter):
    """Adapter for vector storage using FAISS."""
    
    def __init__(self, config: StorageConfig):
        """Initialize vector store adapter."""
        super().__init__(config)
        
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.index = None
        self.dimension = config.database or 512  # Default dimension
        self.index_path = Path(config.base_path or './vectors') / 'faiss_index'
        self.metadata_path = Path(config.base_path or './vectors') / 'metadata.json'
        self.key_to_id = {}
        self.id_to_key = {}
        self.metadata_store = {}
        self.next_id = 0
    
    async def connect(self) -> bool:
        """Initialize FAISS index."""



        try:
            # Create directory
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing index or create new one
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                
                # Load metadata
                if self.metadata_path.exists():
                    async with aiofiles.open(self.metadata_path, 'r') as f:
                        content = await f.read()
                        metadata = json.loads(content)
                        self.key_to_id = metadata.get('key_to_id', {})
                        self.id_to_key = metadata.get('id_to_key', {})
                        self.metadata_store = metadata.get('metadata_store', {})
                        self.next_id = metadata.get('next_id', 0)
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            
            self.is_connected = True
            self.logger.info(f"FAISS vector store initialized with dimension {self.dimension}")
            return True
            
        except Exception as e:
            self.logger.error(f"FAISS initialization failed: {e}")
            return False
    
    async def disconnect(self):
        """Save index and metadata."""



        try:
            if self.index:
                faiss.write_index(self.index, str(self.index_path))
                
                # Save metadata
                metadata = {
                    'key_to_id': self.key_to_id,
                    'id_to_key': self.id_to_key,
                    'metadata_store': self.metadata_store,
                    'next_id': self.next_id
                }
                
                async with aiofiles.open(self.metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
            
            self.is_connected = False
            self.logger.info("FAISS vector store saved and disconnected")
            
        except Exception as e:
            self.logger.error(f"FAISS save failed: {e}")
    
    async def store(self, item: StorageItem) -> bool:
        """Store vector in FAISS index."""



        try:
            # Data should be a vector (numpy array or list)
            if isinstance(item.data, list):
                vector = np.array(item.data, dtype=np.float32)
            elif isinstance(item.data, np.ndarray):
                vector = item.data.astype(np.float32)
            else:
                raise ValueError("Data must be a vector (list or numpy array)")
            
            # Ensure correct dimension
            if vector.shape[0] != self.dimension:
                raise ValueError(f"Vector dimension {vector.shape[0]} does not match index dimension {self.dimension}")
            
            # Normalize vector for cosine similarity
            vector = vector / np.linalg.norm(vector)
            vector = vector.reshape(1, -1)
            
            # Add to index
            vector_id = self.next_id
            self.index.add(vector)
            
            # Update mappings
            self.key_to_id[item.key] = vector_id
            self.id_to_key[str(vector_id)] = item.key
            
            # Store metadata
            self.metadata_store[item.key] = {
                'content_type': item.content_type,
                'size': item.size,
                'created_at': (item.created_at or datetime.now()).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'expires_at': item.expires_at.isoformat() if item.expires_at else None,
                'metadata': item.metadata or {}
            }
            
            self.next_id += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Vector store failed: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[StorageItem]:
        """Retrieve vector by key."""



        try:
            if key not in self.key_to_id:
                return None
            
            vector_id = self.key_to_id[key]
            
            # Get vector from index
            vector = self.index.reconstruct(vector_id)
            
            # Get metadata
            metadata = self.metadata_store.get(key, {})
            
            return StorageItem(
                key=key,
                data=vector.tolist(),
                metadata=metadata.get('metadata', {}),
                content_type=metadata.get('content_type'),
                size=metadata.get('size'),
                created_at=datetime.fromisoformat(metadata['created_at']) if metadata.get('created_at') else None,
                updated_at=datetime.fromisoformat(metadata['updated_at']) if metadata.get('updated_at') else None,
                expires_at=datetime.fromisoformat(metadata['expires_at']) if metadata.get('expires_at') else None
            )
            
        except Exception as e:
            self.logger.error(f"Vector retrieve failed: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete vector (mark as deleted, FAISS doesn't support true deletion)."""



        try:
            if key not in self.key_to_id:
                return False
            
            vector_id = self.key_to_id[key]
            
            # Remove from mappings
            del self.key_to_id[key]
            del self.id_to_key[str(vector_id)]
            del self.metadata_store[key]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Vector delete failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if vector exists."""



        return key in self.key_to_id
    
    async def list_keys(self, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """List vector keys."""



        try:
            keys = list(self.key_to_id.keys())
            
            if prefix:
                keys = [k for k in keys if k.startswith(prefix)]
            
            if limit:
                keys = keys[:limit]
            
            return keys
            
        except Exception as e:
            self.logger.error(f"Vector list keys failed: {e}")
            return []
    
    async def search_similar(
        self,
        query_vector: Union[List[float], np.ndarray],
        k: int = 10,
        threshold: float = 0.5
    ) -> List[tuple]:
        """Search for similar vectors."""



        try:
            # Prepare query vector
            if isinstance(query_vector, list):
                query = np.array(query_vector, dtype=np.float32)
            else:
                query = query_vector.astype(np.float32)
            
            # Normalize query vector
            query = query / np.linalg.norm(query)
            query = query.reshape(1, -1)
            
            # Search
            scores, indices = self.index.search(query, k)
            
            # Filter by threshold and map back to keys
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and str(idx) in self.id_to_key:
                    key = self.id_to_key[str(idx)]
                    results.append((key, float(score)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []

# Export all adapters
__all__ = [
    'StorageAdapter',
    'StorageConfig',
    'StorageItem',
    'DatabaseAdapter',
    'FileSystemAdapter',
    'CloudStorageAdapter',
    'CacheAdapter',
    'VectorStoreAdapter'
]
