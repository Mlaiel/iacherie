"""Database Storage Provider
=========================

Professional database storage implementation for IA-Influencer-Agent platform.
Provides PostgreSQL, MySQL, and SQLite database storage capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import asyncpg
import aiomysql
import aiosqlite
from sqlalchemy import text, MetaData, Table, Column, String, Text, DateTime, Integer, Float, Boolean, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import pickle
import gzip
import bz2

from .interfaces import (
    ContentStorageProvider, ViolationStorageProvider, BaseStorageProvider,
    StorageMetadata, QueryOptions, QueryFilter, StorageStats,
    StorageBackendType, CompressionType, DataFormat, StorageTransaction
)

logger = logging.getLogger(__name__)

Base = declarative_base()

class CrawlerData(Base):
    """Database model for crawler data."""    __tablename__ = 'crawler_data'
    
    record_id = Column(String(255), primary_key=True)
    data_type = Column(String(50), nullable=False)
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50))
    raw_data = Column(Text)
    binary_data = Column(LargeBinary)
    metadata_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    size_bytes = Column(Integer)
    compression_type = Column(String(20))
    format_type = Column(String(20))
    checksum = Column(String(64))
    tags = Column(Text)
    version = Column(Integer, default=1)

class ContentRecord(Base):
    """Database model for content records."""    __tablename__ = 'content_records'
    
    content_id = Column(String(255), primary_key=True)
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(Text)
    description = Column(Text)
    author = Column(String(255))
    url = Column(Text)
    media_urls = Column(Text)  # JSON array
    metadata_json = Column(Text)
    fingerprint_hash = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    engagement_metrics = Column(Text)  # JSON
    protected_content = Column(Boolean, default=False)

class ViolationRecord(Base):
    """Database model for violation records."""    __tablename__ = 'violation_records'
    
    violation_id = Column(String(255), primary_key=True)
    original_content_id = Column(String(255), nullable=False)
    detected_content_id = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    similarity_score = Column(Float, nullable=False)
    violation_type = Column(String(50), nullable=False)
    status = Column(String(50), default='pending')
    evidence_data = Column(Text)  # JSON
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    dmca_notice_sent = Column(Boolean, default=False)
    takedown_successful = Column(Boolean, default=False)

class DatabaseStorageProvider(BaseStorageProvider):
    """    Professional database storage provider.
    
    Supports PostgreSQL, MySQL, and SQLite with advanced features:
    - Connection pooling and optimization
    - Query performance monitoring
    - Automatic schema management
    - Data compression and encryption
    - Transaction support
    - Connection failover
    """    
    def __init__(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ):
        """Initialize database storage provider."""        super().__init__(provider_id, StorageBackendType.DATABASE, config)
        
        self.database_url = config['database_url']
        self.database_type = config.get('database_type', 'postgresql')
        self.pool_size = config.get('pool_size', 10)
        self.max_overflow = config.get('max_overflow', 20)
        self.pool_timeout = config.get('pool_timeout', 30)
        self.pool_recycle = config.get('pool_recycle', 3600)
        
        # Engine and session management
        self.engine = None
        self.async_session_factory = None
        self.metadata = None
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'total_time': 0.0,
            'slow_queries': 0,
            'failed_queries': 0
        }
        
        # Configuration
        self.enable_compression = config.get('enable_compression', True)
        self.compression_type = CompressionType(config.get('compression_type', 'gzip'))
        self.enable_encryption = config.get('enable_encryption', False)
        self.encryption_key = config.get('encryption_key')
        
        logger.info(f"Database storage provider initialized: {provider_id}")
    
    async def connect(self) -> None:
        """Establish database connection."""        try:
            # Create async engine
            engine_kwargs = {
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
                'pool_timeout': self.pool_timeout,
                'pool_recycle': self.pool_recycle,
                'echo': self.config.get('echo_sql', False)
            }
            
            self.engine = create_async_engine(
                self.database_url,
                **engine_kwargs
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.is_connected = True
            logger.info(f"Connected to database: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to database {self.provider_id}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection."""        try:
            if self.engine:
                await self.engine.dispose()
                self.engine = None
                self.async_session_factory = None
            
            self.is_connected = False
            logger.info(f"Disconnected from database: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from database {self.provider_id}: {e}")
    
    async def health_check(self) -> bool:
        """Check database health."""        try:
            if not self.is_connected or not self.engine:
                return False
            
            async with self.async_session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
            
        except Exception as e:
            logger.error(f"Database health check failed for {self.provider_id}: {e}")
            return False
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data using configured compression."""        if not self.enable_compression:
            return pickle.dumps(data)
        
        pickled_data = pickle.dumps(data)
        
        if self.compression_type == CompressionType.GZIP:
            return gzip.compress(pickled_data)
        elif self.compression_type == CompressionType.BZIP2:
            return bz2.compress(pickled_data)
        else:
            return pickled_data
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data using configured compression."""        if not self.enable_compression:
            return pickle.loads(compressed_data)
        
        if self.compression_type == CompressionType.GZIP:
            decompressed = gzip.decompress(compressed_data)
        elif self.compression_type == CompressionType.BZIP2:
            decompressed = bz2.decompress(compressed_data)
        else:
            decompressed = compressed_data
        
        return pickle.loads(decompressed)
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data."""        return hashlib.sha256(data).hexdigest()
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Store a record in database."""        try:
            start_time = asyncio.get_event_loop().time()
            
            # Prepare data
            if isinstance(data, (dict, list)):
                raw_data = json.dumps(data)
                binary_data = None
                format_type = DataFormat.JSON.value
            else:
                raw_data = None
                binary_data = self._compress_data(data)
                format_type = DataFormat.BINARY.value
            
            # Calculate size and checksum
            if binary_data:
                size_bytes = len(binary_data)
                checksum = self._calculate_checksum(binary_data)
            else:
                size_bytes = len(raw_data.encode()) if raw_data else 0
                checksum = hashlib.sha256(raw_data.encode()).hexdigest() if raw_data else None
            
            # Prepare metadata
            metadata_json = None
            tags_json = None
            if metadata:
                metadata_dict = {
                    'created_at': metadata.created_at.isoformat(),
                    'format_type': metadata.format_type.value,
                    'compression_type': metadata.compression_type.value,
                    'version': metadata.version
                }
                metadata_json = json.dumps(metadata_dict)
                
                if metadata.tags:
                    tags_json = json.dumps(metadata.tags)
            
            # Store in database
            async with self.async_session_factory() as session:
                crawler_data = CrawlerData(
                    record_id=record_id,
                    data_type='generic',
                    platform='crawler',
                    raw_data=raw_data,
                    binary_data=binary_data,
                    metadata_json=metadata_json,
                    size_bytes=size_bytes,
                    compression_type=self.compression_type.value if self.enable_compression else CompressionType.NONE.value,
                    format_type=format_type,
                    checksum=checksum,
                    tags=tags_json
                )
                
                session.add(crawler_data)
                await session.commit()
            
            # Update performance stats
            query_time = asyncio.get_event_loop().time() - start_time
            self.query_stats['total_queries'] += 1
            self.query_stats['total_time'] += query_time
            
            if query_time > 1.0:  # Slow query threshold
                self.query_stats['slow_queries'] += 1
                logger.warning(f"Slow database operation: {query_time:.2f}s for record {record_id}")
            
            return True
            
        except Exception as e:
            self.query_stats['failed_queries'] += 1
            logger.error(f"Failed to store record {record_id}: {e}")
            return False
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record from database."""        try:
            start_time = asyncio.get_event_loop().time()
            
            async with self.async_session_factory() as session:
                result = await session.get(CrawlerData, record_id)
                
                if not result:
                    return None
                
                # Deserialize data
                if result.raw_data:
                    data = json.loads(result.raw_data)
                elif result.binary_data:
                    data = self._decompress_data(result.binary_data)
                else:
                    data = None
                
                # Parse metadata if requested
                metadata = None
                if include_metadata and result.metadata_json:
                    metadata_dict = json.loads(result.metadata_json)
                    
                    tags = None
                    if result.tags:
                        tags = json.loads(result.tags)
                    
                    metadata = StorageMetadata(
                        record_id=record_id,
                        created_at=datetime.fromisoformat(metadata_dict['created_at']),
                        updated_at=result.updated_at,
                        size_bytes=result.size_bytes,
                        compression_type=CompressionType(result.compression_type),
                        format_type=DataFormat(result.format_type),
                        tags=tags,
                        checksum=result.checksum,
                        version=result.version
                    )
            
            # Update performance stats
            query_time = asyncio.get_event_loop().time() - start_time
            self.query_stats['total_queries'] += 1
            self.query_stats['total_time'] += query_time
            
            return (data, metadata)
            
        except Exception as e:
            self.query_stats['failed_queries'] += 1
            logger.error(f"Failed to retrieve record {record_id}: {e}")
            return None
    
    async def store_batch(
        self,
        records: List[Tuple[str, Any, Optional[StorageMetadata]]]
    ) -> Dict[str, bool]:
        """Store multiple records in batch."""        results = {}
        
        try:
            async with self.async_session_factory() as session:
                for record_id, data, metadata in records:
                    try:
                        # Prepare data (similar to store_record)
                        if isinstance(data, (dict, list)):
                            raw_data = json.dumps(data)
                            binary_data = None
                            format_type = DataFormat.JSON.value
                        else:
                            raw_data = None
                            binary_data = self._compress_data(data)
                            format_type = DataFormat.BINARY.value
                        
                        # Calculate size and checksum
                        if binary_data:
                            size_bytes = len(binary_data)
                            checksum = self._calculate_checksum(binary_data)
                        else:
                            size_bytes = len(raw_data.encode()) if raw_data else 0
                            checksum = hashlib.sha256(raw_data.encode()).hexdigest() if raw_data else None
                        
                        # Prepare metadata
                        metadata_json = None
                        tags_json = None
                        if metadata:
                            metadata_dict = {
                                'created_at': metadata.created_at.isoformat(),
                                'format_type': metadata.format_type.value,
                                'compression_type': metadata.compression_type.value,
                                'version': metadata.version
                            }
                            metadata_json = json.dumps(metadata_dict)
                            
                            if metadata.tags:
                                tags_json = json.dumps(metadata.tags)
                        
                        crawler_data = CrawlerData(
                            record_id=record_id,
                            data_type='generic',
                            platform='crawler',
                            raw_data=raw_data,
                            binary_data=binary_data,
                            metadata_json=metadata_json,
                            size_bytes=size_bytes,
                            compression_type=self.compression_type.value if self.enable_compression else CompressionType.NONE.value,
                            format_type=format_type,
                            checksum=checksum,
                            tags=tags_json
                        )
                        
                        session.add(crawler_data)
                        results[record_id] = True
                        
                    except Exception as e:
                        logger.error(f"Failed to prepare record {record_id} for batch: {e}")
                        results[record_id] = False
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Batch store operation failed: {e}")
            # Mark all as failed if transaction fails
            for record_id, _, _ in records:
                if record_id not in results:
                    results[record_id] = False
        
        return results
    
    async def retrieve_batch(
        self,
        record_ids: List[str],
        include_metadata: bool = True
    ) -> Dict[str, Optional[Tuple[Any, Optional[StorageMetadata]]]]:
        """Retrieve multiple records in batch."""        results = {}
        
        try:
            async with self.async_session_factory() as session:
                # Query all records at once
                result = await session.execute(
                    text("SELECT * FROM crawler_data WHERE record_id = ANY(:ids)"),
                    {"ids": record_ids}
                )
                
                rows = result.fetchall()
                
                for row in rows:
                    try:
                        record_id = row.record_id
                        
                        # Deserialize data
                        if row.raw_data:
                            data = json.loads(row.raw_data)
                        elif row.binary_data:
                            data = self._decompress_data(row.binary_data)
                        else:
                            data = None
                        
                        # Parse metadata if requested
                        metadata = None
                        if include_metadata and row.metadata_json:
                            metadata_dict = json.loads(row.metadata_json)
                            
                            tags = None
                            if row.tags:
                                tags = json.loads(row.tags)
                            
                            metadata = StorageMetadata(
                                record_id=record_id,
                                created_at=datetime.fromisoformat(metadata_dict['created_at']),
                                updated_at=row.updated_at,
                                size_bytes=row.size_bytes,
                                compression_type=CompressionType(row.compression_type),
                                format_type=DataFormat(row.format_type),
                                tags=tags,
                                checksum=row.checksum,
                                version=row.version
                            )
                        
                        results[record_id] = (data, metadata)
                        
                    except Exception as e:
                        logger.error(f"Failed to deserialize record {row.record_id}: {e}")
                        results[row.record_id] = None
                
                # Mark missing records as None
                for record_id in record_ids:
                    if record_id not in results:
                        results[record_id] = None
                        
        except Exception as e:
            logger.error(f"Batch retrieve operation failed: {e}")
            # Mark all as None if query fails
            for record_id in record_ids:
                results[record_id] = None
        
        return results
    
    async def query_records(
        self,
        options: QueryOptions
    ) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        """Query records with filtering and pagination."""        try:
            async with self.async_session_factory() as session:
                # Build base query
                query = "SELECT * FROM crawler_data WHERE 1=1"
                params = {}
                
                # Apply filters
                for i, filter_item in enumerate(options.filters):
                    param_name = f"filter_{i}"
                    
                    if filter_item.operator == 'eq':
                        query += f" AND {filter_item.field} = :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'ne':
                        query += f" AND {filter_item.field} != :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'gt':
                        query += f" AND {filter_item.field} > :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'gte':
                        query += f" AND {filter_item.field} >= :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'lt':
                        query += f" AND {filter_item.field} < :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'lte':
                        query += f" AND {filter_item.field} <= :{param_name}"
                        params[param_name] = filter_item.value
                    elif filter_item.operator == 'contains':
                        query += f" AND {filter_item.field} LIKE :{param_name}"
                        params[param_name] = f"%{filter_item.value}%"
                
                # Apply sorting
                if options.sort_by:
                    query += f" ORDER BY {options.sort_by} {options.sort_order.upper()}"
                
                # Apply pagination
                if options.limit:
                    query += f" LIMIT {options.limit}"
                if options.offset:
                    query += f" OFFSET {options.offset}"
                
                # Execute query
                result = await session.execute(text(query), params)
                
                for row in result:
                    try:
                        record_id = row.record_id
                        
                        # Deserialize data
                        if row.raw_data:
                            data = json.loads(row.raw_data)
                        elif row.binary_data:
                            data = self._decompress_data(row.binary_data)
                        else:
                            data = None
                        
                        # Parse metadata if requested
                        metadata = None
                        if options.include_metadata and row.metadata_json:
                            metadata_dict = json.loads(row.metadata_json)
                            
                            tags = None
                            if row.tags:
                                tags = json.loads(row.tags)
                            
                            metadata = StorageMetadata(
                                record_id=record_id,
                                created_at=datetime.fromisoformat(metadata_dict['created_at']),
                                updated_at=row.updated_at,
                                size_bytes=row.size_bytes,
                                compression_type=CompressionType(row.compression_type),
                                format_type=DataFormat(row.format_type),
                                tags=tags,
                                checksum=row.checksum,
                                version=row.version
                            )
                        
                        yield (record_id, data, metadata)
                        
                    except Exception as e:
                        logger.error(f"Failed to process query result for record {row.record_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Query operation failed: {e}")
    
    async def count_records(
        self,
        filters: Optional[List[QueryFilter]] = None
    ) -> int:
        """Count records matching filters."""        try:
            async with self.async_session_factory() as session:
                query = "SELECT COUNT(*) FROM crawler_data WHERE 1=1"
                params = {}
                
                if filters:
                    for i, filter_item in enumerate(filters):
                        param_name = f"filter_{i}"
                        
                        if filter_item.operator == 'eq':
                            query += f" AND {filter_item.field} = :{param_name}"
                            params[param_name] = filter_item.value
                        elif filter_item.operator == 'contains':
                            query += f" AND {filter_item.field} LIKE :{param_name}"
                            params[param_name] = f"%{filter_item.value}%"
                
                result = await session.execute(text(query), params)
                return result.scalar() or 0
                
        except Exception as e:
            logger.error(f"Count operation failed: {e}")
            return 0
    
    async def update_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Update an existing record."""        try:
            async with self.async_session_factory() as session:
                crawler_data = await session.get(CrawlerData, record_id)
                
                if not crawler_data:
                    return False
                
                # Update data
                if isinstance(data, (dict, list)):
                    crawler_data.raw_data = json.dumps(data)
                    crawler_data.binary_data = None
                    crawler_data.format_type = DataFormat.JSON.value
                    size_bytes = len(crawler_data.raw_data.encode())
                    checksum = hashlib.sha256(crawler_data.raw_data.encode()).hexdigest()
                else:
                    crawler_data.raw_data = None
                    crawler_data.binary_data = self._compress_data(data)
                    crawler_data.format_type = DataFormat.BINARY.value
                    size_bytes = len(crawler_data.binary_data)
                    checksum = self._calculate_checksum(crawler_data.binary_data)
                
                crawler_data.size_bytes = size_bytes
                crawler_data.checksum = checksum
                crawler_data.updated_at = datetime.utcnow()
                crawler_data.version += 1
                
                # Update metadata if provided
                if metadata:
                    metadata_dict = {
                        'created_at': metadata.created_at.isoformat(),
                        'format_type': metadata.format_type.value,
                        'compression_type': metadata.compression_type.value,
                        'version': crawler_data.version
                    }
                    crawler_data.metadata_json = json.dumps(metadata_dict)
                    
                    if metadata.tags:
                        crawler_data.tags = json.dumps(metadata.tags)
                
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update record {record_id}: {e}")
            return False
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a record."""        try:
            async with self.async_session_factory() as session:
                crawler_data = await session.get(CrawlerData, record_id)
                
                if crawler_data:
                    await session.delete(crawler_data)
                    await session.commit()
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete record {record_id}: {e}")
            return False
    
    async def delete_batch(self, record_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple records in batch."""        results = {}
        
        try:
            async with self.async_session_factory() as session:
                result = await session.execute(
                    text("DELETE FROM crawler_data WHERE record_id = ANY(:ids) RETURNING record_id"),
                    {"ids": record_ids}
                )
                
                deleted_ids = [row[0] for row in result.fetchall()]
                
                for record_id in record_ids:
                    results[record_id] = record_id in deleted_ids
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Batch delete operation failed: {e}")
            for record_id in record_ids:
                results[record_id] = False
        
        return results
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists."""        try:
            async with self.async_session_factory() as session:
                result = await session.execute(
                    text("SELECT 1 FROM crawler_data WHERE record_id = :id LIMIT 1"),
                    {"id": record_id}
                )
                return result.scalar() is not None
                
        except Exception as e:
            logger.error(f"Failed to check existence of record {record_id}: {e}")
            return False
    
    async def get_statistics(self) -> StorageStats:
        """Get storage statistics."""        try:
            async with self.async_session_factory() as session:
                # Total records
                total_result = await session.execute(
                    text("SELECT COUNT(*) FROM crawler_data")
                )
                total_records = total_result.scalar() or 0
                
                # Total size
                size_result = await session.execute(
                    text("SELECT COALESCE(SUM(size_bytes), 0) FROM crawler_data")
                )
                total_size = size_result.scalar() or 0
                
                # Today's records
                today = datetime.utcnow().date()
                today_result = await session.execute(
                    text("SELECT COUNT(*) FROM crawler_data WHERE DATE(created_at) = :today"),
                    {"today": today}
                )
                created_today = today_result.scalar() or 0
                
                # Updated today
                updated_result = await session.execute(
                    text("SELECT COUNT(*) FROM crawler_data WHERE DATE(updated_at) = :today"),
                    {"today": today}
                )
                updated_today = updated_result.scalar() or 0
                
                # Average size
                avg_size = total_size / total_records if total_records > 0 else 0.0
                
                return StorageStats(
                    total_records=total_records,
                    total_size_bytes=total_size,
                    created_today=created_today,
                    updated_today=updated_today,
                    average_record_size=avg_size
                )
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return StorageStats(
                total_records=0,
                total_size_bytes=0,
                created_today=0,
                updated_today=0,
                average_record_size=0.0
            )
    
    async def cleanup_old_records(
        self,
        older_than: datetime,
        batch_size: int = 1000
    ) -> int:
        """Remove records older than specified date."""        total_deleted = 0
        
        try:
            async with self.async_session_factory() as session:
                while True:
                    # Delete in batches to avoid long-running transactions
                    result = await session.execute(
                        text("""                            DELETE FROM crawler_data 
                            WHERE created_at < :older_than 
                            AND record_id IN (
                                SELECT record_id FROM crawler_data 
                                WHERE created_at < :older_than 
                                LIMIT :batch_size
                            )
                            RETURNING record_id
                        """),
                        {
                            "older_than": older_than,
                            "batch_size": batch_size
                        }
                    )
                    
                    deleted_count = result.rowcount
                    total_deleted += deleted_count
                    
                    await session.commit()
                    
                    if deleted_count < batch_size:
                        break
                
                logger.info(f"Cleaned up {total_deleted} old records from database")
                return total_deleted
                
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return total_deleted

class DatabaseContentStorageProvider(ContentStorageProvider, DatabaseStorageProvider):
    """Content-specific database storage provider."""    
    async def store_content(
        self,
        content_id: str,
        platform: str,
        content_type: str,
        content_data: Dict[str, Any],
        media_files: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Store content with associated media files."""        try:
            async with self.async_session_factory() as session:
                # Prepare media URLs
                media_urls = []
                if media_files:
                    media_urls = [media.get('url', '') for media in media_files]
                
                content_record = ContentRecord(
                    content_id=content_id,
                    platform=platform,
                    content_type=content_type,
                    title=content_data.get('title', ''),
                    description=content_data.get('description', ''),
                    author=content_data.get('author', ''),
                    url=content_data.get('url', ''),
                    media_urls=json.dumps(media_urls),
                    metadata_json=json.dumps(content_data),
                    fingerprint_hash=content_data.get('fingerprint_hash'),
                    engagement_metrics=json.dumps(content_data.get('engagement', {})),
                    protected_content=content_data.get('protected', False)
                )
                
                session.add(content_record)
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to store content {content_id}: {e}")
            return False
    
    async def retrieve_content(
        self,
        content_id: str,
        include_media: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve content with optional media files."""        try:
            async with self.async_session_factory() as session:
                content = await session.get(ContentRecord, content_id)
                
                if not content:
                    return None
                
                result = {
                    'content_id': content.content_id,
                    'platform': content.platform,
                    'content_type': content.content_type,
                    'title': content.title,
                    'description': content.description,
                    'author': content.author,
                    'url': content.url,
                    'created_at': content.created_at.isoformat(),
                    'updated_at': content.updated_at.isoformat(),
                    'crawled_at': content.crawled_at.isoformat(),
                    'fingerprint_hash': content.fingerprint_hash,
                    'protected_content': content.protected_content
                }
                
                # Include metadata
                if content.metadata_json:
                    metadata = json.loads(content.metadata_json)
                    result['metadata'] = metadata
                
                # Include engagement metrics
                if content.engagement_metrics:
                    engagement = json.loads(content.engagement_metrics)
                    result['engagement'] = engagement
                
                # Include media URLs if requested
                if include_media and content.media_urls:
                    media_urls = json.loads(content.media_urls)
                    result['media_urls'] = media_urls
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to retrieve content {content_id}: {e}")
            return None
    
    async def query_content_by_platform(
        self,
        platform: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Query content by platform and date range."""        try:
            async with self.async_session_factory() as session:
                query = "SELECT * FROM content_records WHERE platform = :platform"
                params = {"platform": platform}
                
                if start_date:
                    query += " AND created_at >= :start_date"
                    params["start_date"] = start_date
                
                if end_date:
                    query += " AND created_at <= :end_date"
                    params["end_date"] = end_date
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                result = await session.execute(text(query), params)
                
                for row in result:
                    content_data = {
                        'content_id': row.content_id,
                        'platform': row.platform,
                        'content_type': row.content_type,
                        'title': row.title,
                        'description': row.description,
                        'author': row.author,
                        'url': row.url,
                        'created_at': row.created_at.isoformat(),
                        'updated_at': row.updated_at.isoformat(),
                        'crawled_at': row.crawled_at.isoformat(),
                        'fingerprint_hash': row.fingerprint_hash,
                        'protected_content': row.protected_content
                    }
                    
                    if row.metadata_json:
                        content_data['metadata'] = json.loads(row.metadata_json)
                    
                    if row.engagement_metrics:
                        content_data['engagement'] = json.loads(row.engagement_metrics)
                    
                    if row.media_urls:
                        content_data['media_urls'] = json.loads(row.media_urls)
                    
                    yield content_data
                    
        except Exception as e:
            logger.error(f"Failed to query content by platform {platform}: {e}")
    
    async def get_content_metrics(
        self,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get content metrics and analytics."""        try:
            async with self.async_session_factory() as session:
                # Build base query
                conditions = []
                params = {}
                
                if platform:
                    conditions.append("platform = :platform")
                    params["platform"] = platform
                
                if content_type:
                    conditions.append("content_type = :content_type")
                    params["content_type"] = content_type
                
                if date_range:
                    conditions.append("created_at BETWEEN :start_date AND :end_date")
                    params["start_date"] = date_range[0]
                    params["end_date"] = date_range[1]
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Total content count
                count_query = f"SELECT COUNT(*) FROM content_records WHERE {where_clause}"
                count_result = await session.execute(text(count_query), params)
                total_content = count_result.scalar() or 0
                
                # Protected content count
                protected_query = f"""                    SELECT COUNT(*) FROM content_records 
                    WHERE {where_clause} AND protected_content = true
                """                protected_result = await session.execute(text(protected_query), params)
                protected_content = protected_result.scalar() or 0
                
                # Content by platform
                platform_query = f"""                    SELECT platform, COUNT(*) as count 
                    FROM content_records 
                    WHERE {where_clause}
                    GROUP BY platform
                """                platform_result = await session.execute(text(platform_query), params)
                platform_stats = {row.platform: row.count for row in platform_result}
                
                # Content by type
                type_query = f"""                    SELECT content_type, COUNT(*) as count 
                    FROM content_records 
                    WHERE {where_clause}
                    GROUP BY content_type
                """                type_result = await session.execute(text(type_query), params)
                type_stats = {row.content_type: row.count for row in type_result}
                
                return {
                    'total_content': total_content,
                    'protected_content': protected_content,
                    'protection_rate': protected_content / total_content if total_content > 0 else 0.0,
                    'platform_distribution': platform_stats,
                    'content_type_distribution': type_stats,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get content metrics: {e}")
            return {}

class DatabaseViolationStorageProvider(ViolationStorageProvider, DatabaseStorageProvider):
    """Violation-specific database storage provider."""    
    async def store_violation(
        self,
        violation_id: str,
        original_content_id: str,
        detected_content_id: str,
        platform: str,
        similarity_score: float,
        violation_type: str,
        evidence: Dict[str, Any]
    ) -> bool:
        """Store a violation record."""        try:
            async with self.async_session_factory() as session:
                violation_record = ViolationRecord(
                    violation_id=violation_id,
                    original_content_id=original_content_id,
                    detected_content_id=detected_content_id,
                    platform=platform,
                    similarity_score=similarity_score,
                    violation_type=violation_type,
                    evidence_data=json.dumps(evidence)
                )
                
                session.add(violation_record)
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to store violation {violation_id}: {e}")
            return False
    
    async def update_violation_status(
        self,
        violation_id: str,
        status: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Update violation status and resolution."""        try:
            async with self.async_session_factory() as session:
                violation = await session.get(ViolationRecord, violation_id)
                
                if not violation:
                    return False
                
                violation.status = status
                if resolution_notes:
                    violation.resolution_notes = resolution_notes
                
                if status in ['resolved', 'dismissed']:
                    violation.resolved_at = datetime.utcnow()
                
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update violation status {violation_id}: {e}")
            return False
    
    async def get_violation_statistics(
        self,
        platform: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get violation statistics."""        try:
            async with self.async_session_factory() as session:
                # Build conditions
                conditions = []
                params = {}
                
                if platform:
                    conditions.append("platform = :platform")
                    params["platform"] = platform
                
                if date_range:
                    conditions.append("created_at BETWEEN :start_date AND :end_date")
                    params["start_date"] = date_range[0]
                    params["end_date"] = date_range[1]
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Total violations
                total_query = f"SELECT COUNT(*) FROM violation_records WHERE {where_clause}"
                total_result = await session.execute(text(total_query), params)
                total_violations = total_result.scalar() or 0
                
                # Violations by status
                status_query = f"""                    SELECT status, COUNT(*) as count 
                    FROM violation_records 
                    WHERE {where_clause}
                    GROUP BY status
                """                status_result = await session.execute(text(status_query), params)
                status_stats = {row.status: row.count for row in status_result}
                
                # Violations by type
                type_query = f"""                    SELECT violation_type, COUNT(*) as count 
                    FROM violation_records 
                    WHERE {where_clause}
                    GROUP BY violation_type
                """                type_result = await session.execute(text(type_query), params)
                type_stats = {row.violation_type: row.count for row in type_result}
                
                # Average similarity score
                avg_query = f"""                    SELECT AVG(similarity_score) 
                    FROM violation_records 
                    WHERE {where_clause}
                """                avg_result = await session.execute(text(avg_query), params)
                avg_similarity = avg_result.scalar() or 0.0
                
                return {
                    'total_violations': total_violations,
                    'status_distribution': status_stats,
                    'type_distribution': type_stats,
                    'average_similarity_score': float(avg_similarity),
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get violation statistics: {e}")
            return {}
    
    async def query_violations_by_content(
        self,
        content_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Query violations for specific content."""        try:
            async with self.async_session_factory() as session:
                query = """                    SELECT * FROM violation_records 
                    WHERE original_content_id = :content_id OR detected_content_id = :content_id
                    ORDER BY created_at DESC
                """                
                result = await session.execute(text(query), {"content_id": content_id})
                
                for row in result:
                    violation_data = {
                        'violation_id': row.violation_id,
                        'original_content_id': row.original_content_id,
                        'detected_content_id': row.detected_content_id,
                        'platform': row.platform,
                        'similarity_score': row.similarity_score,
                        'violation_type': row.violation_type,
                        'status': row.status,
                        'created_at': row.created_at.isoformat(),
                        'updated_at': row.updated_at.isoformat(),
                        'dmca_notice_sent': row.dmca_notice_sent,
                        'takedown_successful': row.takedown_successful
                    }
                    
                    if row.evidence_data:
                        violation_data['evidence'] = json.loads(row.evidence_data)
                    
                    if row.resolution_notes:
                        violation_data['resolution_notes'] = row.resolution_notes
                    
                    if row.resolved_at:
                        violation_data['resolved_at'] = row.resolved_at.isoformat()
                    
                    yield violation_data
                    
        except Exception as e:
            logger.error(f"Failed to query violations for content {content_id}: {e}")

class DatabaseTransaction(StorageTransaction):
    """Database transaction implementation."""    
    def __init__(self, transaction_id: str, session_factory):
        """Initialize database transaction."""        super().__init__(transaction_id)
        self.session_factory = session_factory
        self.session = None
    
    async def begin(self) -> None:
        """Begin transaction."""        self.session = self.session_factory()
        await self.session.begin()
        logger.debug(f"Database transaction {self.transaction_id} started")
    
    async def commit(self) -> bool:
        """Commit transaction."""        try:
            if self.session:
                await self.session.commit()
                logger.debug(f"Database transaction {self.transaction_id} committed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to commit transaction {self.transaction_id}: {e}")
            return False
        finally:
            if self.session:
                await self.session.close()
                self.session = None
                self.is_active = False
    
    async def rollback(self) -> bool:
        """Rollback transaction."""        try:
            if self.session:
                await self.session.rollback()
                logger.debug(f"Database transaction {self.transaction_id} rolled back")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to rollback transaction {self.transaction_id}: {e}")
            return False
        finally:
            if self.session:
                await self.session.close()
                self.session = None
                self.is_active = False
    
    async def add_operation(
        self,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> None:
        """Add operation to transaction."""        if not self.is_active:
            raise RuntimeError("Transaction is not active")
        
        self.operations.append({
            'type': operation_type,
            'data': operation_data,
            'timestamp': datetime.utcnow().isoformat()
        })

# Export all database storage classes
__all__ = [
    'DatabaseStorageProvider',
    'DatabaseContentStorageProvider',
    'DatabaseViolationStorageProvider',
    'DatabaseTransaction',
    'CrawlerData',
    'ContentRecord',
    'ViolationRecord'
]
