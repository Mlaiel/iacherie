"""
File System Storage Provider
============================

Professional file system storage implementation for IA-Influencer-Agent platform.
Provides efficient file-based storage with hierarchical organization and indexing.

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
import os
import json
import pickle
import gzip
import bz2
import hashlib
import shutil
import aiofiles
import aiofiles.os
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import uuid
from dataclasses import asdict
import fcntl
import sqlite3
import aiosqlite

from .interfaces import (
    BaseStorageProvider, ContentStorageProvider, ViolationStorageProvider,
    StorageMetadata, QueryOptions, QueryFilter, StorageStats,
    StorageBackendType, CompressionType, DataFormat, StorageTransaction
)

logger = logging.getLogger(__name__)

class FileSystemStorageProvider(BaseStorageProvider):
    """
    Professional file system storage provider.
    
    Features:
    - Hierarchical directory organization
    - Multiple compression formats
    - File locking for concurrent access
    - Metadata indexing with SQLite
    - Atomic operations
    - Automatic cleanup and archiving
    - Performance optimization
    """
    
    def __init__(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ):
        """Initialize file system storage provider."""
        super().__init__(provider_id, StorageBackendType.FILE_SYSTEM, config)
        
        self.base_path = Path(config['base_path'])
        self.enable_compression = config.get('enable_compression', True)
        self.compression_type = CompressionType(config.get('compression_type', 'gzip'))
        self.enable_indexing = config.get('enable_indexing', True)
        self.max_files_per_directory = config.get('max_files_per_directory', 1000)
        self.enable_file_locking = config.get('enable_file_locking', True)
        self.enable_backup = config.get('enable_backup', False)
        self.backup_interval_hours = config.get('backup_interval_hours', 24)
        
        # Directory structure
        self.data_dir = self.base_path / "data"
        self.metadata_dir = self.base_path / "metadata"
        self.index_dir = self.base_path / "index"
        self.backup_dir = self.base_path / "backup"
        self.temp_dir = self.base_path / "temp"
        
        # Index database
        self.index_db_path = self.index_dir / "file_index.db"
        self.index_db = None
        
        # File locks
        self.file_locks: Dict[str, asyncio.Lock] = {}
        
        # Performance tracking
        self.operation_stats = {
            'reads': 0,
            'writes': 0,
            'deletes': 0,
            'total_time': 0.0,
            'errors': 0
        }
        
        logger.info(f"File system storage provider initialized: {provider_id}")
    
    async def connect(self) -> None:
        """Initialize file system storage."""



        try:
            # Create directory structure
            for directory in [self.data_dir, self.metadata_dir, self.index_dir, self.backup_dir, self.temp_dir]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize index database if enabled
            if self.enable_indexing:
                await self._initialize_index_database()
            
            self.is_connected = True
            logger.info(f"File system storage connected: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect file system storage {self.provider_id}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close file system storage."""



        try:
            # Close index database
            if self.index_db:
                await self.index_db.close()
                self.index_db = None
            
            # Clear file locks
            self.file_locks.clear()
            
            self.is_connected = False
            logger.info(f"File system storage disconnected: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting file system storage {self.provider_id}: {e}")
    
    async def health_check(self) -> bool:
        """Check file system health."""



        try:
            if not self.is_connected:
                return False
            
            # Check if directories are accessible
            test_file = self.temp_dir / f"health_check_{uuid.uuid4().hex[:8]}.tmp"
            
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("health_check")
            
            # Verify file exists and is readable
            if not test_file.exists():
                return False
            
            async with aiofiles.open(test_file, 'r') as f:
                content = await f.read()
                if content != "health_check":
                    return False
            
            # Clean up test file
            await aiofiles.os.remove(test_file)
            
            # Check index database if enabled
            if self.enable_indexing and self.index_db:
                async with self.index_db.execute("SELECT 1") as cursor:
                    result = await cursor.fetchone()
                    if not result or result[0] != 1:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"File system health check failed for {self.provider_id}: {e}")
            return False
    
    async def _initialize_index_database(self) -> None:
        """Initialize SQLite index database."""



        try:
            self.index_db = await aiosqlite.connect(str(self.index_db_path))
            
            # Create index tables
            await self.index_db.execute("""
                CREATE TABLE IF NOT EXISTS file_index (
                    record_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    metadata_path TEXT,
                    data_type TEXT,
                    platform TEXT,
                    content_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    size_bytes INTEGER,
                    compression_type TEXT,
                    format_type TEXT,
                    checksum TEXT,
                    tags TEXT
                )
            """)
            
            await self.index_db.execute("""
                CREATE INDEX IF NOT EXISTS idx_record_platform 
                ON file_index(platform)
            """)
            
            await self.index_db.execute("""
                CREATE INDEX IF NOT EXISTS idx_record_created 
                ON file_index(created_at)
            """)
            
            await self.index_db.execute("""
                CREATE INDEX IF NOT EXISTS idx_record_type 
                ON file_index(content_type)
            """)
            
            await self.index_db.commit()
            
            logger.info(f"Index database initialized: {self.index_db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize index database: {e}")
            raise
    
    def _get_file_path(self, record_id: str) -> Path:
        """Get file path for record ID using hierarchical directory structure."""
        # Create hierarchical path from record ID hash
        record_hash = hashlib.sha256(record_id.encode()).hexdigest()
        
        # Create 3-level hierarchy using first 6 characters
        level1 = record_hash[:2]
        level2 = record_hash[2:4]
        level3 = record_hash[4:6]
        
        directory = self.data_dir / level1 / level2 / level3
        return directory / f"{record_id}.data"
    
    def _get_metadata_path(self, record_id: str) -> Path:
        """Get metadata file path for record ID."""
        record_hash = hashlib.sha256(record_id.encode()).hexdigest()
        
        level1 = record_hash[:2]
        level2 = record_hash[2:4]
        level3 = record_hash[4:6]
        
        directory = self.metadata_dir / level1 / level2 / level3
        return directory / f"{record_id}.meta"
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using configured compression."""
        if not self.enable_compression:
            return data
        
        if self.compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif self.compression_type == CompressionType.BZIP2:
            return bz2.compress(data)
        else:
            return data
    
    def _decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompress data using configured compression."""
        if not self.enable_compression:
            return compressed_data
        
        if self.compression_type == CompressionType.GZIP:
            return gzip.decompress(compressed_data)
        elif self.compression_type == CompressionType.BZIP2:
            return bz2.decompress(compressed_data)
        else:
            return compressed_data
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data."""



        return hashlib.sha256(data).hexdigest()
    
    async def _get_file_lock(self, record_id: str) -> asyncio.Lock:
        """Get or create file lock for record."""
        if record_id not in self.file_locks:
            self.file_locks[record_id] = asyncio.Lock()
        return self.file_locks[record_id]
    
    async def _update_index(
        self,
        record_id: str,
        file_path: str,
        metadata_path: Optional[str] = None,
        metadata: Optional[StorageMetadata] = None,
        operation: str = "insert"
    ) -> None:
        """Update file index database."""
        if not self.enable_indexing or not self.index_db:
            return
        
        try:
            if operation == "insert" or operation == "update":
                # Extract metadata information
                data_type = "generic"
                platform = "crawler"
                content_type = None
                size_bytes = 0
                compression_type = self.compression_type.value if self.enable_compression else CompressionType.NONE.value
                format_type = DataFormat.BINARY.value
                checksum = None
                tags = None
                
                if metadata:
                    size_bytes = metadata.size_bytes or 0
                    compression_type = metadata.compression_type.value
                    format_type = metadata.format_type.value
                    checksum = metadata.checksum
                    tags = json.dumps(metadata.tags) if metadata.tags else None
                
                # Get file size if not provided
                if size_bytes == 0:
                    try:
                        stat = await aiofiles.os.stat(file_path)
                        size_bytes = stat.st_size
                    except:
                        pass
                
                await self.index_db.execute("""
                    INSERT OR REPLACE INTO file_index (
                        record_id, file_path, metadata_path, data_type, platform, content_type,
                        created_at, updated_at, size_bytes, compression_type, format_type, checksum, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record_id, file_path, metadata_path, data_type, platform, content_type,
                    datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                    size_bytes, compression_type, format_type, checksum, tags
                ))
                
            elif operation == "delete":
                await self.index_db.execute(
                    "DELETE FROM file_index WHERE record_id = ?",
                    (record_id,)
                )
            
            await self.index_db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update index for record {record_id}: {e}")
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Store a record to file system."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get file lock if enabled
            if self.enable_file_locking:
                lock = await self._get_file_lock(record_id)
                async with lock:
                    return await self._store_record_internal(record_id, data, metadata)
            else:
                return await self._store_record_internal(record_id, data, metadata)
            
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to store record {record_id}: {e}")
            return False
        finally:
            operation_time = asyncio.get_event_loop().time() - start_time
            self.operation_stats['writes'] += 1
            self.operation_stats['total_time'] += operation_time
    
    async def _store_record_internal(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Internal method to store record."""
        file_path = self._get_file_path(record_id)
        metadata_path = self._get_metadata_path(record_id)
        
        # Create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize and compress data
        if isinstance(data, (dict, list)):
            serialized_data = json.dumps(data).encode()
            format_type = DataFormat.JSON
        else:
            serialized_data = pickle.dumps(data)
            format_type = DataFormat.BINARY
        
        compressed_data = self._compress_data(serialized_data)
        checksum = self._calculate_checksum(compressed_data)
        
        # Create or update metadata
        if not metadata:
            metadata = StorageMetadata(
                record_id=record_id,
                created_at=datetime.utcnow(),
                size_bytes=len(compressed_data),
                compression_type=self.compression_type if self.enable_compression else CompressionType.NONE,
                format_type=format_type,
                checksum=checksum
            )
        else:
            metadata.updated_at = datetime.utcnow()
            metadata.size_bytes = len(compressed_data)
            metadata.checksum = checksum
        
        # Write data file atomically
        temp_file_path = file_path.with_suffix('.tmp')
        try:
            async with aiofiles.open(temp_file_path, 'wb') as f:
                await f.write(compressed_data)
                await f.fsync()  # Force write to disk
            
            # Atomic move
            await aiofiles.os.rename(temp_file_path, file_path)
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file_path.exists():
                await aiofiles.os.remove(temp_file_path)
            raise e
        
        # Write metadata file
        metadata_dict = asdict(metadata)
        metadata_dict['created_at'] = metadata.created_at.isoformat()
        if metadata.updated_at:
            metadata_dict['updated_at'] = metadata.updated_at.isoformat()
        metadata_dict['compression_type'] = metadata.compression_type.value
        metadata_dict['format_type'] = metadata.format_type.value
        
        temp_metadata_path = metadata_path.with_suffix('.tmp')
        try:
            async with aiofiles.open(temp_metadata_path, 'w') as f:
                await f.write(json.dumps(metadata_dict, indent=2))
                await f.fsync()
            
            await aiofiles.os.rename(temp_metadata_path, metadata_path)
            
        except Exception as e:
            if temp_metadata_path.exists():
                await aiofiles.os.remove(temp_metadata_path)
            logger.warning(f"Failed to write metadata for {record_id}: {e}")
        
        # Update index
        await self._update_index(
            record_id,
            str(file_path),
            str(metadata_path),
            metadata,
            "insert"
        )
        
        return True
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record from file system."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get file lock if enabled
            if self.enable_file_locking:
                lock = await self._get_file_lock(record_id)
                async with lock:
                    return await self._retrieve_record_internal(record_id, include_metadata)
            else:
                return await self._retrieve_record_internal(record_id, include_metadata)
            
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to retrieve record {record_id}: {e}")
            return None
        finally:
            operation_time = asyncio.get_event_loop().time() - start_time
            self.operation_stats['reads'] += 1
            self.operation_stats['total_time'] += operation_time
    
    async def _retrieve_record_internal(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Internal method to retrieve record."""
        file_path = self._get_file_path(record_id)
        metadata_path = self._get_metadata_path(record_id)
        
        # Check if file exists
        if not file_path.exists():
            return None
        
        # Read and decompress data
        async with aiofiles.open(file_path, 'rb') as f:
            compressed_data = await f.read()
        
        decompressed_data = self._decompress_data(compressed_data)
        
        # Load metadata if requested
        metadata = None
        if include_metadata and metadata_path.exists():
            try:
                async with aiofiles.open(metadata_path, 'r') as f:
                    metadata_dict = json.loads(await f.read())
                
                metadata = StorageMetadata(
                    record_id=metadata_dict['record_id'],
                    created_at=datetime.fromisoformat(metadata_dict['created_at']),
                    updated_at=datetime.fromisoformat(metadata_dict['updated_at']) if metadata_dict.get('updated_at') else None,
                    size_bytes=metadata_dict.get('size_bytes'),
                    compression_type=CompressionType(metadata_dict.get('compression_type', 'none')),
                    format_type=DataFormat(metadata_dict.get('format_type', 'binary')),
                    tags=metadata_dict.get('tags'),
                    checksum=metadata_dict.get('checksum'),
                    version=metadata_dict.get('version', 1)
                )
                
                # Verify checksum if available
                if metadata.checksum:
                    calculated_checksum = self._calculate_checksum(compressed_data)
                    if calculated_checksum != metadata.checksum:
                        logger.warning(f"Checksum mismatch for record {record_id}")
                
            except Exception as e:
                logger.warning(f"Failed to load metadata for {record_id}: {e}")
        
        # Deserialize data based on format
        try:
            if metadata and metadata.format_type == DataFormat.JSON:
                data = json.loads(decompressed_data.decode())
            else:
                data = pickle.loads(decompressed_data)
        except Exception as e:
            logger.error(f"Failed to deserialize data for {record_id}: {e}")
            return None
        
        return (data, metadata)
    
    async def store_batch(
        self,
        records: List[Tuple[str, Any, Optional[StorageMetadata]]]
    ) -> Dict[str, bool]:
        """Store multiple records in batch."""
        results = {}
        
        # Process records in parallel (with reasonable concurrency limit)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent file operations
        
        async def store_single_record(record_id, data, metadata):
            async with semaphore:
                success = await self.store_record(record_id, data, metadata)
                results[record_id] = success
        
        tasks = [
            store_single_record(record_id, data, metadata)
            for record_id, data, metadata in records
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def retrieve_batch(
        self,
        record_ids: List[str],
        include_metadata: bool = True
    ) -> Dict[str, Optional[Tuple[Any, Optional[StorageMetadata]]]]:
        """Retrieve multiple records in batch."""
        results = {}
        
        # Process records in parallel (with reasonable concurrency limit)
        semaphore = asyncio.Semaphore(20)  # Higher limit for reads
        
        async def retrieve_single_record(record_id):
            async with semaphore:
                result = await self.retrieve_record(record_id, include_metadata)
                results[record_id] = result
        
        tasks = [
            retrieve_single_record(record_id)
            for record_id in record_ids
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def query_records(
        self,
        options: QueryOptions
    ) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        """Query records using index database."""
        if not self.enable_indexing or not self.index_db:
            logger.warning("Indexing disabled, cannot perform efficient queries")
            return
        
        try:
            # Build SQL query
            query = "SELECT record_id FROM file_index WHERE 1=1"
            params = []
            
            # Apply filters
            for filter_item in options.filters:
                if filter_item.field in ['platform', 'content_type', 'data_type']:
                    if filter_item.operator == 'eq':
                        query += f" AND {filter_item.field} = ?"
                        params.append(filter_item.value)
                    elif filter_item.operator == 'contains':
                        query += f" AND {filter_item.field} LIKE ?"
                        params.append(f"%{filter_item.value}%")
                elif filter_item.field == 'created_at':
                    if filter_item.operator == 'gte':
                        query += " AND created_at >= ?"
                        params.append(filter_item.value.isoformat() if isinstance(filter_item.value, datetime) else filter_item.value)
                    elif filter_item.operator == 'lte':
                        query += " AND created_at <= ?"
                        params.append(filter_item.value.isoformat() if isinstance(filter_item.value, datetime) else filter_item.value)
            
            # Apply sorting
            if options.sort_by:
                query += f" ORDER BY {options.sort_by} {options.sort_order.upper()}"
            
            # Apply pagination
            if options.limit:
                query += f" LIMIT {options.limit}"
            if options.offset:
                query += f" OFFSET {options.offset}"
            
            # Execute query
            async with self.index_db.execute(query, params) as cursor:
                async for row in cursor:
                    record_id = row[0]
                    
                    # Retrieve actual record data
                    result = await self.retrieve_record(record_id, options.include_metadata)
                    if result:
                        data, metadata = result
                        yield (record_id, data, metadata)
                        
        except Exception as e:
            logger.error(f"Query operation failed: {e}")
    
    async def count_records(
        self,
        filters: Optional[List[QueryFilter]] = None
    ) -> int:
        """Count records matching filters."""
        if not self.enable_indexing or not self.index_db:
            # Fallback: count files in data directory
            try:
                count = 0
                for file_path in self.data_dir.rglob("*.data"):
                    count += 1
                return count
            except Exception as e:
                logger.error(f"Failed to count files: {e}")
                return 0
        
        try:
            query = "SELECT COUNT(*) FROM file_index WHERE 1=1"
            params = []
            
            if filters:
                for filter_item in filters:
                    if filter_item.field in ['platform', 'content_type', 'data_type']:
                        if filter_item.operator == 'eq':
                            query += f" AND {filter_item.field} = ?"
                            params.append(filter_item.value)
            
            async with self.index_db.execute(query, params) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Count operation failed: {e}")
            return 0
    
    async def update_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Update an existing record."""
        # For file system, update is the same as store
        return await self.store_record(record_id, data, metadata)
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a record from file system."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get file lock if enabled
            if self.enable_file_locking:
                lock = await self._get_file_lock(record_id)
                async with lock:
                    success = await self._delete_record_internal(record_id)
            else:
                success = await self._delete_record_internal(record_id)
            
            if success:
                # Remove lock
                self.file_locks.pop(record_id, None)
            
            return success
            
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to delete record {record_id}: {e}")
            return False
        finally:
            operation_time = asyncio.get_event_loop().time() - start_time
            self.operation_stats['deletes'] += 1
            self.operation_stats['total_time'] += operation_time
    
    async def _delete_record_internal(self, record_id: str) -> bool:
        """Internal method to delete record."""
        file_path = self._get_file_path(record_id)
        metadata_path = self._get_metadata_path(record_id)
        
        success = True
        
        # Delete data file
        if file_path.exists():
            try:
                await aiofiles.os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to delete data file for {record_id}: {e}")
                success = False
        
        # Delete metadata file
        if metadata_path.exists():
            try:
                await aiofiles.os.remove(metadata_path)
            except Exception as e:
                logger.warning(f"Failed to delete metadata file for {record_id}: {e}")
        
        # Update index
        await self._update_index(record_id, "", operation="delete")
        
        return success
    
    async def delete_batch(self, record_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple records in batch."""
        results = {}
        
        # Process deletions in parallel
        semaphore = asyncio.Semaphore(10)
        
        async def delete_single_record(record_id):
            async with semaphore:
                success = await self.delete_record(record_id)
                results[record_id] = success
        
        tasks = [
            delete_single_record(record_id)
            for record_id in record_ids
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists."""
        file_path = self._get_file_path(record_id)
        return file_path.exists()
    
    async def get_statistics(self) -> StorageStats:
        """Get storage statistics."""



        try:
            if self.enable_indexing and self.index_db:
                # Get statistics from index database
                async with self.index_db.execute("SELECT COUNT(*) FROM file_index") as cursor:
                    result = await cursor.fetchone()
                    total_records = result[0] if result else 0
                
                async with self.index_db.execute("SELECT COALESCE(SUM(size_bytes), 0) FROM file_index") as cursor:
                    result = await cursor.fetchone()
                    total_size = result[0] if result else 0
                
                # Today's statistics
                today = datetime.utcnow().date().isoformat()
                async with self.index_db.execute(
                    "SELECT COUNT(*) FROM file_index WHERE DATE(created_at) = ?",
                    (today,)
                ) as cursor:
                    result = await cursor.fetchone()
                    created_today = result[0] if result else 0
                
                async with self.index_db.execute(
                    "SELECT COUNT(*) FROM file_index WHERE DATE(updated_at) = ?",
                    (today,)
                ) as cursor:
                    result = await cursor.fetchone()
                    updated_today = result[0] if result else 0
                
            else:
                # Fallback: scan file system
                total_records = 0
                total_size = 0
                created_today = 0
                updated_today = 0
                
                today = datetime.utcnow().date()
                
                for file_path in self.data_dir.rglob("*.data"):
                    total_records += 1
                    
                    try:
                        stat = await aiofiles.os.stat(file_path)
                        total_size += stat.st_size
                        
                        # Check creation date
                        created_date = datetime.fromtimestamp(stat.st_ctime).date()
                        if created_date == today:
                            created_today += 1
                        
                        # Check modification date
                        modified_date = datetime.fromtimestamp(stat.st_mtime).date()
                        if modified_date == today:
                            updated_today += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to get stats for {file_path}: {e}")
            
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
        """Remove records older than specified date."""
        total_deleted = 0
        
        try:
            if self.enable_indexing and self.index_db:
                # Use index to find old records
                query = "SELECT record_id FROM file_index WHERE created_at < ? LIMIT ?"
                
                while True:
                    async with self.index_db.execute(query, (older_than.isoformat(), batch_size)) as cursor:
                        records = await cursor.fetchall()
                    
                    if not records:
                        break
                    
                    record_ids = [record[0] for record in records]
                    
                    # Delete records in batch
                    delete_results = await self.delete_batch(record_ids)
                    deleted_count = sum(1 for success in delete_results.values() if success)
                    total_deleted += deleted_count
                    
                    if len(records) < batch_size:
                        break
                        
            else:
                # Fallback: scan file system
                batch_count = 0
                batch_records = []
                
                for file_path in self.data_dir.rglob("*.data"):
                    try:
                        stat = await aiofiles.os.stat(file_path)
                        created_time = datetime.fromtimestamp(stat.st_ctime)
                        
                        if created_time < older_than:
                            # Extract record ID from filename
                            record_id = file_path.stem
                            batch_records.append(record_id)
                            batch_count += 1
                            
                            if batch_count >= batch_size:
                                # Delete batch
                                delete_results = await self.delete_batch(batch_records)
                                deleted_count = sum(1 for success in delete_results.values() if success)
                                total_deleted += deleted_count
                                
                                batch_records = []
                                batch_count = 0
                                
                    except Exception as e:
                        logger.warning(f"Failed to check file {file_path}: {e}")
                
                # Delete remaining records
                if batch_records:
                    delete_results = await self.delete_batch(batch_records)
                    deleted_count = sum(1 for success in delete_results.values() if success)
                    total_deleted += deleted_count
            
            logger.info(f"Cleaned up {total_deleted} old records from file system")
            return total_deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return total_deleted
    
    async def get_operation_statistics(self) -> Dict[str, Any]:
        """Get operation statistics."""
        total_operations = self.operation_stats['reads'] + self.operation_stats['writes'] + self.operation_stats['deletes']
        
        return {
            'total_operations': total_operations,
            'reads': self.operation_stats['reads'],
            'writes': self.operation_stats['writes'],
            'deletes': self.operation_stats['deletes'],
            'errors': self.operation_stats['errors'],
            'total_time': self.operation_stats['total_time'],
            'average_time': (
                self.operation_stats['total_time'] / total_operations
                if total_operations > 0 else 0.0
            ),
            'error_rate': (
                self.operation_stats['errors'] / total_operations
                if total_operations > 0 else 0.0
            )
        }

class FileSystemTransaction(StorageTransaction):
    """File system transaction implementation using temporary directory."""
    
    def __init__(self, transaction_id: str, storage_provider: FileSystemStorageProvider):
        """Initialize file system transaction."""
        super().__init__(transaction_id)
        self.storage_provider = storage_provider
        self.transaction_dir = storage_provider.temp_dir / f"transaction_{transaction_id}"
        self.operations_log = []
    
    async def begin(self) -> None:
        """Begin transaction by creating transaction directory."""



        try:
            self.transaction_dir.mkdir(exist_ok=True)
            logger.debug(f"File system transaction {self.transaction_id} started")
        except Exception as e:
            logger.error(f"Failed to begin transaction {self.transaction_id}: {e}")
            raise
    
    async def commit(self) -> bool:
        """Commit transaction by applying all operations."""



        try:
            # Apply all logged operations
            for operation in self.operations_log:
                operation_type = operation['type']
                operation_data = operation['data']
                
                if operation_type == 'store':
                    await self.storage_provider.store_record(
                        operation_data['record_id'],
                        operation_data['data'],
                        operation_data['metadata']
                    )
                elif operation_type == 'delete':
                    await self.storage_provider.delete_record(operation_data['record_id'])
                elif operation_type == 'update':
                    await self.storage_provider.update_record(
                        operation_data['record_id'],
                        operation_data['data'],
                        operation_data['metadata']
                    )
            
            # Clean up transaction directory
            if self.transaction_dir.exists():
                shutil.rmtree(self.transaction_dir)
            
            logger.debug(f"File system transaction {self.transaction_id} committed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit transaction {self.transaction_id}: {e}")
            await self.rollback()
            return False
        finally:
            self.is_active = False
    
    async def rollback(self) -> bool:
        """Rollback transaction by cleaning up transaction directory."""



        try:
            # Clean up transaction directory
            if self.transaction_dir.exists():
                shutil.rmtree(self.transaction_dir)
            
            logger.debug(f"File system transaction {self.transaction_id} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback transaction {self.transaction_id}: {e}")
            return False
        finally:
            self.is_active = False
    
    async def add_operation(
        self,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> None:
        """Add operation to transaction log."""
        if not self.is_active:
            raise RuntimeError("Transaction is not active")
        
        self.operations_log.append({
            'type': operation_type,
            'data': operation_data,
            'timestamp': datetime.utcnow().isoformat()
        })

# Export all file system storage classes
__all__ = [
    'FileSystemStorageProvider',
    'FileSystemTransaction'
]
