"""
 Local Storage Provider - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/storage/local_storage.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

High-performance local storage provider with advanced file management,
intelligent organization, and seamless integration with cloud backends.

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, Generator
import logging
import asyncio
import aiofiles
import aiofiles.os
from pathlib import Path
from datetime import datetime, timedelta
import json
import hashlib
import shutil
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import os
import stat
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class LocalStorageTier(Enum):
    """Local storage tiers for performance optimization"""
    SSD_HOT = "ssd_hot"        # SSD for frequently accessed files
    SSD_WARM = "ssd_warm"      # SSD for moderate access
    HDD_COLD = "hdd_cold"      # HDD for infrequent access
    ARCHIVE = "archive"        # Compressed archive storage

@dataclass
class LocalStorageConfig:
    """Local storage configuration"""
    base_path: str
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    enable_compression: bool = True
    enable_encryption: bool = True
    auto_cleanup: bool = True
    cleanup_threshold_days: int = 90
    max_concurrent_operations: int = 10
    
    # Storage tier paths
    tier_paths: Dict[str, str] = field(default_factory=lambda: {
        'ssd_hot': '/fast_storage/hot',
        'ssd_warm': '/fast_storage/warm', 
        'hdd_cold': '/archive_storage/cold',
        'archive': '/archive_storage/archive'
    })
    
    # Performance settings
    buffer_size: int = 64 * 1024  # 64KB
    enable_indexing: bool = True
    enable_deduplication: bool = True

class LocalStorageManager:
    """
    Enterprise local storage manager for IA Influencer Agent platform.
    
    Features:
    - Multi-tier storage (SSD/HDD optimization)
    - Intelligent file organization by content type
    - High-performance async operations
    - Built-in compression and encryption
    - Automatic cleanup and maintenance
    - File indexing and search capabilities
    """
    
    def __init__(self, config: LocalStorageConfig):
        """Initialize local storage manager"""
        self.config = config
        self.base_path = Path(config.base_path)
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_operations)
        
        # File index for fast lookups
        self.file_index: Dict[str, Dict[str, Any]] = {}
        self.index_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            'files_stored': 0,
            'files_retrieved': 0,
            'total_size': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'operations_times': []
        }
        
        # Initialize storage structure
        self._initialize_storage()
        
        # Load existing file index
        self._load_file_index()
        
        # Start background cleanup if enabled
        if config.auto_cleanup:
            self._start_cleanup_scheduler()
        
        logger.info(f"LocalStorageManager initialized at {self.base_path}")
    
    def _initialize_storage(self) -> None:
        """Initialize storage directory structure"""



        try:
            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Create tier directories
            for tier, tier_path in self.config.tier_paths.items():
                full_path = self.base_path / tier_path.lstrip('/')
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Create content type subdirectories
                content_types = ['audio', 'video', 'image', 'text', 'fingerprint', 'embedding', 'model', 'document', 'metadata']
                for content_type in content_types:
                    (full_path / content_type).mkdir(exist_ok=True)
            
            # Create system directories
            (self.base_path / '.system').mkdir(exist_ok=True)
            (self.base_path / '.index').mkdir(exist_ok=True)
            (self.base_path / '.temp').mkdir(exist_ok=True)
            (self.base_path / '.backup').mkdir(exist_ok=True)
            
            logger.info("Storage directory structure initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage structure: {str(e)}")
            raise
    
    async def store_file(
        self,
        file_path: str,
        content: Union[bytes, str, BinaryIO],
        content_type: str = "unknown",
        tier: Optional[LocalStorageTier] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store file in local storage with intelligent organization.
        
        Business Logic:
        1. Determine optimal storage tier based on content type and metadata
        2. Organize files by content type and date for easy retrieval
        3. Apply compression for large files
        4. Generate checksums for integrity verification
        5. Update file index for fast lookups
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not file_path:
                raise ValueError("File path is required")
            
            # Prepare content
            content_bytes = await self._prepare_content(content)
            
            # Determine storage tier if not specified
            if not tier:
                tier = self._determine_optimal_tier(content_type, len(content_bytes), metadata)
            
            # Generate storage path
            storage_path = self._generate_storage_path(file_path, content_type, tier)
            
            # Check file size limits
            if len(content_bytes) > self.config.max_file_size:
                raise ValueError(f"File size {len(content_bytes)} exceeds limit {self.config.max_file_size}")
            
            # Process content (compression, encryption)
            processed_content = await self._process_content(content_bytes, content_type)
            
            # Create directory if needed
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            async with aiofiles.open(storage_path, 'wb') as f:
                await f.write(processed_content)
            
            # Calculate file properties
            file_size = len(processed_content)
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Prepare metadata
            file_metadata = {
                'original_path': file_path,
                'storage_path': str(storage_path),
                'content_type': content_type,
                'tier': tier.value,
                'file_size': file_size,
                'original_size': len(content_bytes),
                'content_hash': content_hash,
                'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream',
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'compression_ratio': file_size / len(content_bytes) if len(content_bytes) > 0 else 1.0,
                'encrypted': self.config.enable_encryption,
                'compressed': self.config.enable_compression and file_size < len(content_bytes),
                **(metadata or {})
            }
            
            # Update file index
            await self._update_file_index(content_hash, file_metadata)
            
            # Update metrics
            self.metrics['files_stored'] += 1
            self.metrics['total_size'] += file_size
            self.metrics['operations_times'].append(time.time() - start_time)
            
            logger.info(f"File stored successfully: {file_path} -> {storage_path}")
            
            return {
                'success': True,
                'file_id': content_hash,
                'storage_path': str(storage_path),
                'file_size': file_size,
                'content_hash': content_hash,
                'metadata': file_metadata,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to store file {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'processing_time': time.time() - start_time
            }
    
    async def retrieve_file(
        self,
        file_id: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve file by ID with optional output path"""
        start_time = time.time()
        
        try:
            # Look up file in index
            file_metadata = await self._get_file_metadata(file_id)
            if not file_metadata:
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_id': file_id
                }
            
            storage_path = Path(file_metadata['storage_path'])
            
            # Check if file exists
            if not storage_path.exists():
                return {
                    'success': False,
                    'error': 'File not found on disk',
                    'file_id': file_id
                }
            
            # Read file content
            async with aiofiles.open(storage_path, 'rb') as f:
                content = await f.read()
            
            # Process content (decompression, decryption)
            processed_content = await self._unprocess_content(content, file_metadata)
            
            # Save to output path if specified
            if output_path:
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                async with aiofiles.open(output_path_obj, 'wb') as f:
                    await f.write(processed_content)
            
            # Update access statistics
            await self._update_access_stats(file_id)
            
            # Update metrics
            self.metrics['files_retrieved'] += 1
            self.metrics['operations_times'].append(time.time() - start_time)
            
            return {
                'success': True,
                'file_id': file_id,
                'content': processed_content,
                'output_path': output_path,
                'metadata': file_metadata,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_id': file_id,
                'processing_time': time.time() - start_time
            }
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete file from storage"""



        try:
            # Look up file in index
            file_metadata = await self._get_file_metadata(file_id)
            if not file_metadata:
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_id': file_id
                }
            
            storage_path = Path(file_metadata['storage_path'])
            
            # Delete file from disk
            if storage_path.exists():
                await aiofiles.os.remove(storage_path)
            
            # Remove from index
            await self._remove_from_index(file_id)
            
            # Update metrics
            file_size = file_metadata.get('file_size', 0)
            self.metrics['total_size'] -= file_size
            
            logger.info(f"File deleted successfully: {file_id}")
            
            return {
                'success': True,
                'file_id': file_id,
                'deleted_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_id': file_id
            }
    
    async def list_files(
        self,
        content_type: Optional[str] = None,
        tier: Optional[LocalStorageTier] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List files with optional filtering"""



        try:
            files = []
            
            with self.index_lock:
                for file_id, metadata in list(self.file_index.items())[offset:offset+limit]:
                    # Apply filters
                    if content_type and metadata.get('content_type') != content_type:
                        continue
                    
                    if tier and metadata.get('tier') != tier.value:
                        continue
                    
                    files.append({
                        'file_id': file_id,
                        **metadata
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []
    
    async def search_files(
        self,
        query: str,
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search files by filename or metadata"""



        try:
            results = []
            query_lower = query.lower()
            
            with self.index_lock:
                for file_id, metadata in self.file_index.items():
                    # Apply content type filter
                    if content_type and metadata.get('content_type') != content_type:
                        continue
                    
                    # Search in filename and metadata
                    original_path = metadata.get('original_path', '').lower()
                    metadata_str = json.dumps(metadata).lower()
                    
                    if query_lower in original_path or query_lower in metadata_str:
                        results.append({
                            'file_id': file_id,
                            'relevance_score': self._calculate_relevance(query_lower, metadata),
                            **metadata
                        })
                    
                    if len(results) >= limit:
                        break
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search files: {str(e)}")
            return []
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""



        try:
            # Calculate tier usage
            tier_usage = {}
            for tier_name, tier_path in self.config.tier_paths.items():
                full_path = self.base_path / tier_path.lstrip('/')
                if full_path.exists():
                    tier_size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                    tier_usage[tier_name] = {
                        'size_bytes': tier_size,
                        'size_mb': tier_size / (1024 * 1024),
                        'file_count': len(list(full_path.rglob('*')))
                    }
            
            # Calculate disk usage
            total_size = sum(stat['size_bytes'] for stat in tier_usage.values())
            disk_usage = shutil.disk_usage(self.base_path)
            
            return {
                'total_files': len(self.file_index),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'tier_usage': tier_usage,
                'disk_usage': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'used_percentage': (disk_usage.used / disk_usage.total) * 100
                },
                'performance_metrics': {
                    'files_stored': self.metrics['files_stored'],
                    'files_retrieved': self.metrics['files_retrieved'],
                    'cache_hit_ratio': self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses']),
                    'avg_operation_time': sum(self.metrics['operations_times']) / max(1, len(self.metrics['operations_times']))
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage statistics: {str(e)}")
            return {}
    
    async def cleanup_storage(self, max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """Clean up old and unused files"""



        try:
            max_age = max_age_days or self.config.cleanup_threshold_days
            cutoff_date = datetime.now() - timedelta(days=max_age)
            
            cleaned_files = []
            total_freed_space = 0
            
            with self.index_lock:
                files_to_remove = []
                
                for file_id, metadata in self.file_index.items():
                    last_accessed = datetime.fromisoformat(metadata.get('last_accessed', ''))
                    
                    if last_accessed < cutoff_date:
                        storage_path = Path(metadata['storage_path'])
                        
                        if storage_path.exists():
                            file_size = storage_path.stat().st_size
                            await aiofiles.os.remove(storage_path)
                            total_freed_space += file_size
                            
                            cleaned_files.append({
                                'file_id': file_id,
                                'size': file_size,
                                'last_accessed': metadata.get('last_accessed')
                            })
                        
                        files_to_remove.append(file_id)
                
                # Remove from index
                for file_id in files_to_remove:
                    del self.file_index[file_id]
            
            # Save updated index
            await self._save_file_index()
            
            logger.info(f"Cleanup completed: {len(cleaned_files)} files, {total_freed_space} bytes freed")
            
            return {
                'cleaned_files_count': len(cleaned_files),
                'total_freed_space': total_freed_space,
                'cleaned_files': cleaned_files
            }
            
        except Exception as e:
            logger.error(f"Storage cleanup failed: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _prepare_content(self, content: Union[bytes, str, BinaryIO]) -> bytes:
        """Prepare content for storage"""
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode('utf-8')
        elif hasattr(content, 'read'):
            if asyncio.iscoroutinefunction(content.read):
                return await content.read()
            else:
                return content.read()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    def _determine_optimal_tier(
        self,
        content_type: str,
        file_size: int,
        metadata: Optional[Dict[str, Any]]
    ) -> LocalStorageTier:
        """Determine optimal storage tier based on content characteristics"""
        
        # High-priority content types (fingerprints, embeddings) go to SSD
        if content_type in ['fingerprint', 'embedding', 'model']:
            return LocalStorageTier.SSD_HOT
        
        # Active content based on metadata
        if metadata and metadata.get('access_frequency', 'low') == 'high':
            return LocalStorageTier.SSD_HOT
        
        # Medium-size frequently accessed files
        if file_size < 50 * 1024 * 1024:  # 50MB
            return LocalStorageTier.SSD_WARM
        
        # Large files or infrequent access
        if file_size > 100 * 1024 * 1024:  # 100MB
            return LocalStorageTier.HDD_COLD
        
        # Archive for very old content
        if metadata and metadata.get('age_days', 0) > 365:
            return LocalStorageTier.ARCHIVE
        
        # Default to SSD warm
        return LocalStorageTier.SSD_WARM
    
    def _generate_storage_path(
        self,
        file_path: str,
        content_type: str,
        tier: LocalStorageTier
    ) -> Path:
        """Generate organized storage path"""
        
        # Get tier base path
        tier_path = self.config.tier_paths.get(tier.value, self.config.tier_paths['ssd_warm'])
        base_tier_path = self.base_path / tier_path.lstrip('/')
        
        # Organize by content type
        content_dir = base_tier_path / content_type
        
        # Organize by date (year/month)
        now = datetime.now()
        date_dir = content_dir / f"{now.year:04d}" / f"{now.month:02d}"
        
        # Generate unique filename
        file_stem = Path(file_path).stem
        file_extension = Path(file_path).suffix
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Add random suffix to avoid collisions
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        filename = f"{timestamp}_{file_stem}_{unique_id}{file_extension}"
        
        return date_dir / filename
    
    async def _process_content(self, content: bytes, content_type: str) -> bytes:
        """Process content with compression and encryption"""
        processed_content = content
        
        # Apply compression if enabled and beneficial
        if self.config.enable_compression:
            if content_type in ['text', 'document', 'metadata'] or len(content) > 1024:
                import gzip
                compressed = gzip.compress(content)
                if len(compressed) < len(content) * 0.9:  # Only if 10%+ reduction
                    processed_content = compressed
        
        # Apply encryption if enabled
        if self.config.enable_encryption:
            # Simple XOR encryption for demo (use proper encryption in production)
            key = b'ia_influencer_key_2025'
            processed_content = bytes(a ^ b for a, b in zip(processed_content, 
                                    (key * ((len(processed_content) // len(key)) + 1))[:len(processed_content)]))
        
        return processed_content
    
    async def _unprocess_content(self, content: bytes, metadata: Dict[str, Any]) -> bytes:
        """Reverse processing (decompression, decryption)"""
        processed_content = content
        
        # Decrypt if encrypted
        if metadata.get('encrypted', False):
            key = b'ia_influencer_key_2025'
            processed_content = bytes(a ^ b for a, b in zip(processed_content,
                                    (key * ((len(processed_content) // len(key)) + 1))[:len(processed_content)]))
        
        # Decompress if compressed
        if metadata.get('compressed', False):
            import gzip
            processed_content = gzip.decompress(processed_content)
        
        return processed_content
    
    async def _update_file_index(self, file_id: str, metadata: Dict[str, Any]) -> None:
        """Update file index with new entry"""
        with self.index_lock:
            self.file_index[file_id] = metadata
        
        # Periodically save index to disk
        if len(self.file_index) % 100 == 0:
            await self._save_file_index()
    
    async def _get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from index"""
        with self.index_lock:
            return self.file_index.get(file_id)
    
    async def _update_access_stats(self, file_id: str) -> None:
        """Update file access statistics"""
        with self.index_lock:
            if file_id in self.file_index:
                self.file_index[file_id]['last_accessed'] = datetime.now().isoformat()
                self.file_index[file_id]['access_count'] = self.file_index[file_id].get('access_count', 0) + 1
    
    async def _remove_from_index(self, file_id: str) -> None:
        """Remove file from index"""
        with self.index_lock:
            if file_id in self.file_index:
                del self.file_index[file_id]
        
        await self._save_file_index()
    
    async def _load_file_index(self) -> None:
        """Load file index from disk"""
        index_file = self.base_path / '.index' / 'file_index.json'
        
        try:
            if index_file.exists():
                async with aiofiles.open(index_file, 'r') as f:
                    content = await f.read()
                    self.file_index = json.loads(content)
                logger.info(f"Loaded file index with {len(self.file_index)} entries")
            else:
                self.file_index = {}
                logger.info("Created new file index")
                
        except Exception as e:
            logger.error(f"Failed to load file index: {str(e)}")
            self.file_index = {}
    
    async def _save_file_index(self) -> None:
        """Save file index to disk"""
        index_file = self.base_path / '.index' / 'file_index.json'
        
        try:
            index_file.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(index_file, 'w') as f:
                await f.write(json.dumps(self.file_index, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save file index: {str(e)}")
    
    def _calculate_relevance(self, query: str, metadata: Dict[str, Any]) -> float:
        """Calculate search relevance score"""
        score = 0.0
        
        # Filename match
        original_path = metadata.get('original_path', '').lower()
        if query in original_path:
            score += 1.0
        
        # Content type match
        if query in metadata.get('content_type', '').lower():
            score += 0.5
        
        # Recent files get higher score
        created_at = metadata.get('created_at', '')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at)
                days_old = (datetime.now() - created_date).days
                if days_old < 30:
                    score += 0.3
            except:
                pass
        
        # Frequently accessed files
        access_count = metadata.get('access_count', 0)
        score += min(access_count * 0.1, 0.5)
        
        return score
    
    def _start_cleanup_scheduler(self) -> None:
        """Start background cleanup scheduler"""
        def cleanup_worker():
            while True:
                try:
                    # Run cleanup every 24 hours
                    time.sleep(24 * 60 * 60)
                    asyncio.create_task(self.cleanup_storage())
                except Exception as e:
                    logger.error(f"Cleanup scheduler error: {str(e)}")
        
        import threading
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

class AsyncLocalStorageManager:
    """Async wrapper for high-performance concurrent operations"""
    
    def __init__(self, config: LocalStorageConfig):
        self.sync_manager = LocalStorageManager(config)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_operations)
    
    async def store_files_batch(
        self,
        files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Store multiple files concurrently"""
        
        async def store_single(file_info):
            async with self.semaphore:
                return await self.sync_manager.store_file(
                    file_info['path'],
                    file_info['content'],
                    file_info.get('content_type', 'unknown'),
                    file_info.get('tier'),
                    file_info.get('metadata')
                )
        
        tasks = [store_single(file_info) for file_info in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]
    
    async def retrieve_files_batch(
        self,
        file_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve multiple files concurrently"""
        
        async def retrieve_single(file_id):
            async with self.semaphore:
                return await self.sync_manager.retrieve_file(file_id)
        
        tasks = [retrieve_single(file_id) for file_id in file_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]

# Export classes
__all__ = [
    'LocalStorageManager',
    'AsyncLocalStorageManager',
    'LocalStorageConfig',
    'LocalStorageTier'
]
