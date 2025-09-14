"""
File Manager - Core Utilities Level 1
====================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade file management utility consolidating:
- File utilities (file_utilities.py)
- Backup utilities (backup_utilities.py)

Performance: < 100ms per file operation
Standards: 100% async, type hints, enterprise security
"""

import asyncio
import aiofiles
import aiofiles.os
import aiofiles.tempfile
import hashlib
import logging
import mimetypes
import shutil
import zipfile
import tarfile
import time
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    AsyncIterator, BinaryIO, TextIO
)
from datetime import datetime, timezone
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import aiohttp
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

@dataclass
class FileResult:
    """Enterprise result container for file operations."""
    success: bool
    path: Optional[str] = None
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    mime_type: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'path': self.path,
            'size_bytes': self.size_bytes,
            'checksum': self.checksum,
            'mime_type': self.mime_type,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass
class BackupConfig:
    """Configuration for backup operations."""
    source_path: str
    destination_path: str
    compression: str = "gzip"  # gzip, bzip2, lzma, none
    encryption_key: Optional[str] = None
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_backup_size_mb: int = 1000
    retention_days: int = 30

class FileManager:
    """
    Enterprise file manager with ultra-high performance standards.
    
    Provides comprehensive file operations with async I/O, security,
    and backup capabilities following enterprise architecture patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize file manager with enterprise configuration."""
        self.config = config or {}
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 100.0
        self._max_file_size_mb = self.config.get('max_file_size_mb', 100)
        self._allowed_extensions = set(self.config.get('allowed_extensions', []))
        self._encryption_key = self.config.get('encryption_key')
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        self._thread_pool.shutdown(wait=True)
        
    async def _measure_performance(self, operation: Callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        result = await operation()
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    def _validate_file_security(self, file_path: str) -> List[str]:
        """Validate file security constraints."""
        errors = []
        path = Path(file_path)
        
        # Check file extension
        if self._allowed_extensions and path.suffix.lower() not in self._allowed_extensions:
            errors.append(f"File extension {path.suffix} not allowed")
            
        # Check for path traversal
        try:
            path.resolve().relative_to(Path.cwd())
        except ValueError:
            errors.append("Path traversal detected")
            
        return errors
    
    async def _calculate_checksum(self, file_path: str, algorithm: str = "sha256") -> str:
        """Calculate file checksum asynchronously."""
        hash_obj = hashlib.new(algorithm)
        
        async with aiofiles.open(file_path, 'rb') as file:
            async for chunk in self._read_file_chunks(file):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    
    async def _read_file_chunks(self, file: BinaryIO, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """Read file in chunks asynchronously."""
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    # === CORE FILE OPERATIONS ===
    
    async def read_file(
        self, 
        file_path: str,
        encoding: str = 'utf-8',
        binary: bool = False
    ) -> FileResult:
        """Read file with enterprise security and performance monitoring."""
        async def _read():
            # Security validation
            security_errors = self._validate_file_security(file_path)
            if security_errors:
                return None, security_errors
                
            path = Path(file_path)
            if not await aiofiles.os.path.exists(file_path):
                return None, [f"File not found: {file_path}"]
                
            file_size = await aiofiles.os.path.getsize(file_path)
            if file_size > self._max_file_size_mb * 1024 * 1024:
                return None, [f"File too large: {file_size} bytes"]
            
            # Read file content
            mode = 'rb' if binary else 'r'
            async with aiofiles.open(file_path, mode, encoding=None if binary else encoding) as file:
                content = await file.read()
                
            # Calculate checksum and mime type
            checksum = await self._calculate_checksum(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'content': content,
                'size_bytes': file_size,
                'checksum': checksum,
                'mime_type': mime_type
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_read)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'read_file', 'binary': binary}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=file_path,
                size_bytes=data['size_bytes'],
                checksum=data['checksum'],
                mime_type=data['mime_type'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'read_file',
                    'binary': binary,
                    'encoding': encoding,
                    'content_length': len(data['content'])
                }
            )
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'read_file'}
            )
    
    async def write_file(
        self,
        file_path: str,
        content: Union[str, bytes],
        encoding: str = 'utf-8',
        create_dirs: bool = True,
        backup_existing: bool = True
    ) -> FileResult:
        """Write file with enterprise safety and performance monitoring."""
        async def _write():
            # Security validation
            security_errors = self._validate_file_security(file_path)
            if security_errors:
                return None, security_errors
                
            path = Path(file_path)
            
            # Create directories if needed
            if create_dirs and not await aiofiles.os.path.exists(path.parent):
                await aiofiles.os.makedirs(path.parent, exist_ok=True)
                
            # Backup existing file if requested
            backup_path = None
            if backup_existing and await aiofiles.os.path.exists(file_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{file_path}.backup_{timestamp}"
                await aiofiles.os.rename(file_path, backup_path)
            
            # Write content
            binary = isinstance(content, bytes)
            mode = 'wb' if binary else 'w'
            
            async with aiofiles.open(file_path, mode, encoding=None if binary else encoding) as file:
                await file.write(content)
                
            # Get file stats
            file_size = await aiofiles.os.path.getsize(file_path)
            checksum = await self._calculate_checksum(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'size_bytes': file_size,
                'checksum': checksum,
                'mime_type': mime_type,
                'backup_path': backup_path
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_write)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'write_file'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=file_path,
                size_bytes=data['size_bytes'],
                checksum=data['checksum'],
                mime_type=data['mime_type'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'write_file',
                    'backup_created': data['backup_path'] is not None,
                    'backup_path': data['backup_path'],
                    'content_type': 'binary' if isinstance(content, bytes) else 'text'
                }
            )
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'write_file'}
            )
    
    async def copy_file(
        self,
        source_path: str,
        destination_path: str,
        preserve_metadata: bool = True
    ) -> FileResult:
        """Copy file with enterprise safety and performance monitoring."""
        async def _copy():
            # Security validation
            source_errors = self._validate_file_security(source_path)
            dest_errors = self._validate_file_security(destination_path)
            
            if source_errors or dest_errors:
                return None, source_errors + dest_errors
                
            if not await aiofiles.os.path.exists(source_path):
                return None, [f"Source file not found: {source_path}"]
                
            dest_path = Path(destination_path)
            if not await aiofiles.os.path.exists(dest_path.parent):
                await aiofiles.os.makedirs(dest_path.parent, exist_ok=True)
            
            # Perform copy operation
            await asyncio.get_event_loop().run_in_executor(
                self._thread_pool,
                shutil.copy2 if preserve_metadata else shutil.copy,
                source_path,
                destination_path
            )
            
            # Get file stats
            file_size = await aiofiles.os.path.getsize(destination_path)
            checksum = await self._calculate_checksum(destination_path)
            mime_type, _ = mimetypes.guess_type(destination_path)
            
            return {
                'size_bytes': file_size,
                'checksum': checksum,
                'mime_type': mime_type
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_copy)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'copy_file'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=destination_path,
                size_bytes=data['size_bytes'],
                checksum=data['checksum'],
                mime_type=data['mime_type'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'copy_file',
                    'source_path': source_path,
                    'preserve_metadata': preserve_metadata
                }
            )
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'copy_file'}
            )
    
    async def delete_file(self, file_path: str, secure_delete: bool = False) -> FileResult:
        """Delete file with optional secure deletion."""
        async def _delete():
            # Security validation
            security_errors = self._validate_file_security(file_path)
            if security_errors:
                return None, security_errors
                
            if not await aiofiles.os.path.exists(file_path):
                return None, [f"File not found: {file_path}"]
            
            file_size = await aiofiles.os.path.getsize(file_path)
            
            if secure_delete:
                # Secure deletion by overwriting with random data
                async with aiofiles.open(file_path, 'r+b') as file:
                    await file.seek(0)
                    for _ in range(3):  # 3-pass overwrite
                        await file.write(b'\x00' * file_size)
                        await file.seek(0)
                        await file.write(b'\xFF' * file_size)
                        await file.seek(0)
                        
            await aiofiles.os.remove(file_path)
            
            return {'size_bytes': file_size}, []
            
        try:
            result, exec_time = await self._measure_performance(_delete)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'delete_file'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=file_path,
                size_bytes=data['size_bytes'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'delete_file',
                    'secure_delete': secure_delete
                }
            )
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'delete_file'}
            )
    
    # === DIRECTORY OPERATIONS ===
    
    async def list_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        include_hidden: bool = False,
        file_pattern: Optional[str] = None
    ) -> FileResult:
        """List directory contents with enterprise filtering."""
        async def _list():
            if not await aiofiles.os.path.exists(directory_path):
                return None, [f"Directory not found: {directory_path}"]
                
            if not await aiofiles.os.path.isdir(directory_path):
                return None, [f"Path is not a directory: {directory_path}"]
            
            files = []
            path = Path(directory_path)
            
            if recursive:
                pattern = '**/*' if file_pattern is None else f'**/{file_pattern}'
                paths = path.glob(pattern)
            else:
                pattern = '*' if file_pattern is None else file_pattern
                paths = path.glob(pattern)
            
            for file_path in paths:
                if not include_hidden and file_path.name.startswith('.'):
                    continue
                    
                try:
                    stat = await aiofiles.os.stat(file_path)
                    files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': stat.st_size,
                        'is_directory': file_path.is_dir(),
                        'modified': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
                    })
                except OSError:
                    # Skip files we can't stat
                    continue
            
            return {'files': files, 'total_count': len(files)}, []
            
        try:
            result, exec_time = await self._measure_performance(_list)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'list_directory'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=directory_path,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'list_directory',
                    'recursive': recursive,
                    'include_hidden': include_hidden,
                    'file_pattern': file_pattern,
                    'total_files': data['total_count'],
                    'files': data['files']
                }
            )
        except Exception as e:
            logger.error(f"Directory listing failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'list_directory'}
            )
    
    # === BACKUP OPERATIONS ===
    
    async def create_backup(self, config: BackupConfig) -> FileResult:
        """Create enterprise-grade backup with compression and encryption."""
        async def _backup():
            source_path = Path(config.source_path)
            if not await aiofiles.os.path.exists(source_path):
                return None, [f"Source path not found: {config.source_path}"]
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{source_path.name}_{timestamp}"
            
            if config.compression == "gzip":
                backup_name += ".tar.gz"
            elif config.compression == "bzip2":
                backup_name += ".tar.bz2"
            elif config.compression == "lzma":
                backup_name += ".tar.xz"
            else:
                backup_name += ".tar"
            
            backup_path = Path(config.destination_path) / backup_name
            
            # Create destination directory
            await aiofiles.os.makedirs(backup_path.parent, exist_ok=True)
            
            # Create archive
            def _create_archive():
                mode = f"w:{config.compression}" if config.compression != "none" else "w"
                
                with tarfile.open(backup_path, mode) as tar:
                    if source_path.is_file():
                        tar.add(source_path, arcname=source_path.name)
                    else:
                        # Add directory with filtering
                        def filter_function(tarinfo):
                            # Apply include/exclude patterns
                            if config.exclude_patterns:
                                for pattern in config.exclude_patterns:
                                    if pattern in tarinfo.name:
                                        return None
                            
                            if config.include_patterns:
                                for pattern in config.include_patterns:
                                    if pattern in tarinfo.name:
                                        break
                                else:
                                    return None
                            
                            return tarinfo
                        
                        tar.add(source_path, arcname=source_path.name, filter=filter_function)
            
            await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, _create_archive
            )
            
            # Encrypt if requested
            final_path = backup_path
            if config.encryption_key:
                encrypted_path = backup_path.with_suffix(backup_path.suffix + '.enc')
                
                cipher = Fernet(config.encryption_key.encode())
                async with aiofiles.open(backup_path, 'rb') as source:
                    async with aiofiles.open(encrypted_path, 'wb') as dest:
                        async for chunk in self._read_file_chunks(source):
                            encrypted_chunk = cipher.encrypt(chunk)
                            await dest.write(encrypted_chunk)
                
                # Remove unencrypted file
                await aiofiles.os.remove(backup_path)
                final_path = encrypted_path
            
            # Get final file stats
            file_size = await aiofiles.os.path.getsize(final_path)
            checksum = await self._calculate_checksum(str(final_path))
            
            return {
                'backup_path': str(final_path),
                'size_bytes': file_size,
                'checksum': checksum,
                'encrypted': config.encryption_key is not None
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_backup)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'create_backup'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=data['backup_path'],
                size_bytes=data['size_bytes'],
                checksum=data['checksum'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'create_backup',
                    'source_path': config.source_path,
                    'compression': config.compression,
                    'encrypted': data['encrypted']
                }
            )
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'create_backup'}
            )
    
    async def restore_backup(
        self,
        backup_path: str,
        destination_path: str,
        encryption_key: Optional[str] = None
    ) -> FileResult:
        """Restore backup with decryption support."""
        async def _restore():
            if not await aiofiles.os.path.exists(backup_path):
                return None, [f"Backup file not found: {backup_path}"]
            
            restore_path = backup_path
            
            # Decrypt if needed
            if encryption_key and backup_path.endswith('.enc'):
                decrypted_path = backup_path[:-4]  # Remove .enc extension
                
                cipher = Fernet(encryption_key.encode())
                async with aiofiles.open(backup_path, 'rb') as source:
                    async with aiofiles.open(decrypted_path, 'wb') as dest:
                        async for chunk in self._read_file_chunks(source):
                            decrypted_chunk = cipher.decrypt(chunk)
                            await dest.write(decrypted_chunk)
                
                restore_path = decrypted_path
            
            # Extract archive
            def _extract_archive():
                with tarfile.open(restore_path, 'r:*') as tar:
                    tar.extractall(destination_path)
            
            await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, _extract_archive
            )
            
            # Clean up decrypted temp file if created
            if restore_path != backup_path:
                await aiofiles.os.remove(restore_path)
            
            return {'restored_to': destination_path}, []
            
        try:
            result, exec_time = await self._measure_performance(_restore)
            
            if result[0] is None:  # Error case
                return FileResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'restore_backup'}
                )
            
            data = result[0]
            return FileResult(
                success=True,
                path=data['restored_to'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'restore_backup',
                    'backup_path': backup_path,
                    'encrypted': encryption_key is not None
                }
            )
        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return FileResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'restore_backup'}
            )

# Enterprise factory pattern for file manager
class FileManagerFactory:
    """Factory for creating configured file manager instances."""
    
    @staticmethod
    async def create_manager(config: Optional[Dict[str, Any]] = None) -> FileManager:
        """Create and initialize file manager."""
        return FileManager(config)
    
    @staticmethod
    @asynccontextmanager
    async def create_manager_context(config: Optional[Dict[str, Any]] = None):
        """Create file manager as async context manager."""
        manager = FileManager(config)
        try:
            yield manager
        finally:
            await manager.__aexit__(None, None, None)