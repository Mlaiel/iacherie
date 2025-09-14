"""
File Operation Utilities - Enterprise File Management System
===========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive file operation utilities supporting:
- Secure file operations with validation
- Enterprise-grade file management
- Cross-platform compatibility
- Async file operations for performance
- File system monitoring and health checks

Expert Roles Covered:
- Backend Senior: File system operations and management
- Security Expert: Secure file operations and validation
- DevOps Expert: File monitoring and system health
"""

import os
import sys
import shutil
import hashlib
import mimetypes
import tempfile
import asyncio
import aiofiles
import stat
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class FileOperationType(Enum):
    """File operation types for tracking and auditing"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    COMPRESS = "compress"
    DECOMPRESS = "decompress"


class FileSecurityLevel(Enum):
    """Security levels for file operations"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class FileMetadata:
    """File metadata information"""
    path: str
    name: str
    size: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    mime_type: str
    extension: str
    permissions: str
    owner: str
    group: str
    checksum: str
    security_level: FileSecurityLevel
    is_encrypted: bool = False
    compression_ratio: Optional[float] = None


@dataclass
class FileOperationResult:
    """Result of file operation"""
    success: bool
    operation: FileOperationType
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    metadata: Optional[FileMetadata] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    bytes_processed: Optional[int] = None


class FileUtilities:
    """
    Enterprise-grade file operation utilities with security and performance optimization.
    
    Features:
    - Secure file operations with validation
    - Async file operations for better performance
    - File system monitoring and health checks
    - Comprehensive error handling and logging
    - Cross-platform compatibility
    - File metadata extraction and management
    """
    
    def __init__(self, 
                 base_path -> None: Optional[str] = None,
                 security_level -> None: FileSecurityLevel = FileSecurityLevel.INTERNAL,
                 max_file_size -> None: int = 100 * 1024 * 1024,  # 100MB
                 allowed_extensions -> None: Optional[List[str]] = None,
                 temp_dir -> None: Optional[str] = None) -> None:
        """
        Initialize file utilities with configuration
        
        Args:
            base_path: Base directory for file operations
            security_level: Default security level for operations
            max_file_size: Maximum allowed file size in bytes
            allowed_extensions: List of allowed file extensions
            temp_dir: Temporary directory for file operations
        """
        try:
            logger.info("Initializing FileUtilities")
            
            # Configuration
            self.base_path = Path(base_path) if base_path else Path.cwd()
            self.security_level = security_level
            self.max_file_size = max_file_size
            self.allowed_extensions = allowed_extensions or []
            self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
            
            # Ensure base directories exist
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Operation tracking
            self.operations_log: List[FileOperationResult] = []
            self.operation_stats = {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "bytes_processed": 0
            }
            
            # Security settings
            self.forbidden_paths = {'/etc', '/bin', '/usr/bin', '/sbin', '/usr/sbin'}
            self.dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif'}
            
            logger.info("FileUtilities initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FileUtilities: {e}")
            raise

    async def create_file(self, 
                         file_path: str,
                         content: Union[str, bytes] = "",
                         encoding: str = "utf-8",
                         permissions: Optional[int] = None,
                         security_level: Optional[FileSecurityLevel] = None) -> FileOperationResult:
        """
        Create a new file with content
        
        Args:
            file_path: Path to the file to create
            content: Content to write to the file
            encoding: Text encoding (for string content)
            permissions: File permissions (octal)
            security_level: Security level for the file
            
        Returns:
            FileOperationResult with operation details
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Creating file: {file_path}")
            
            # Validate file path
            if not self._validate_path(file_path):
                raise ValueError(f"Invalid or forbidden file path: {file_path}")
            
            # Security validation
            security_level = security_level or self.security_level
            if not self._validate_security_level(file_path, security_level):
                raise ValueError(f"Security validation failed for {file_path}")
            
            # Validate content size
            content_size = len(content.encode(encoding) if isinstance(content, str) else content)
            if content_size > self.max_file_size:
                raise ValueError(f"Content size {content_size} exceeds maximum {self.max_file_size}")
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file asynchronously
            if isinstance(content, str):
                async with aiofiles.open(path, 'w', encoding=encoding) as f:
                    await f.write(content)
            else:
                async with aiofiles.open(path, 'wb') as f:
                    await f.write(content)
            
            # Set permissions if specified
            if permissions:
                os.chmod(path, permissions)
            
            # Generate metadata
            metadata = await self.get_file_metadata(str(path))
            
            # Record operation
            execution_time = (datetime.now() - start_time).total_seconds()
            result = FileOperationResult(
                success=True,
                operation=FileOperationType.CREATE,
                destination_path=str(path),
                metadata=metadata,
                execution_time=execution_time,
                bytes_processed=content_size
            )
            
            self._record_operation(result)
            logger.info(f"File created successfully: {file_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = FileOperationResult(
                success=False,
                operation=FileOperationType.CREATE,
                destination_path=file_path,
                error_message=str(e),
                execution_time=execution_time
            )
            self._record_operation(error_result)
            logger.error(f"Failed to create file {file_path}: {e}")
            return error_result

    async def read_file(self, 
                       file_path: str,
                       encoding: str = "utf-8",
                       as_bytes: bool = False) -> Tuple[bool, Union[str, bytes, None]]:
        """
        Read file content asynchronously
        
        Args:
            file_path: Path to the file to read
            encoding: Text encoding (for text files)
            as_bytes: Whether to return content as bytes
            
        Returns:
            Tuple of (success, content)
        """
        try:
            logger.info(f"Reading file: {file_path}")
            
            # Validate file path
            if not self._validate_path(file_path, check_exists=True):
                raise ValueError(f"Invalid or non-existent file path: {file_path}")
            
            path = Path(file_path)
            
            if as_bytes:
                async with aiofiles.open(path, 'rb') as f:
                    content = await f.read()
            else:
                async with aiofiles.open(path, 'r', encoding=encoding) as f:
                    content = await f.read()
            
            logger.info(f"File read successfully: {file_path}")
            return True, content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return False, None

    async def update_file(self,
                         file_path: str,
                         content: Union[str, bytes],
                         encoding: str = "utf-8",
                         append: bool = False) -> FileOperationResult:
        """
        Update existing file content
        
        Args:
            file_path: Path to the file to update
            content: New content for the file
            encoding: Text encoding (for string content)
            append: Whether to append content instead of overwriting
            
        Returns:
            FileOperationResult with operation details
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Updating file: {file_path}")
            
            # Validate file path
            if not self._validate_path(file_path, check_exists=True):
                raise ValueError(f"Invalid or non-existent file path: {file_path}")
            
            path = Path(file_path)
            
            # Validate content size
            content_size = len(content.encode(encoding) if isinstance(content, str) else content)
            if content_size > self.max_file_size:
                raise ValueError(f"Content size {content_size} exceeds maximum {self.max_file_size}")
            
            # Write file asynchronously
            mode = 'a' if append else 'w'
            if isinstance(content, str):
                async with aiofiles.open(path, mode, encoding=encoding) as f:
                    await f.write(content)
            else:
                mode = 'ab' if append else 'wb'
                async with aiofiles.open(path, mode) as f:
                    await f.write(content)
            
            # Generate metadata
            metadata = await self.get_file_metadata(str(path))
            
            # Record operation
            execution_time = (datetime.now() - start_time).total_seconds()
            result = FileOperationResult(
                success=True,
                operation=FileOperationType.UPDATE,
                destination_path=str(path),
                metadata=metadata,
                execution_time=execution_time,
                bytes_processed=content_size
            )
            
            self._record_operation(result)
            logger.info(f"File updated successfully: {file_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = FileOperationResult(
                success=False,
                operation=FileOperationType.UPDATE,
                destination_path=file_path,
                error_message=str(e),
                execution_time=execution_time
            )
            self._record_operation(error_result)
            logger.error(f"Failed to update file {file_path}: {e}")
            return error_result

    async def delete_file(self, file_path: str) -> FileOperationResult:
        """
        Delete a file securely
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            FileOperationResult with operation details
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Deleting file: {file_path}")
            
            # Validate file path
            if not self._validate_path(file_path, check_exists=True):
                raise ValueError(f"Invalid or non-existent file path: {file_path}")
            
            path = Path(file_path)
            
            # Get metadata before deletion
            metadata = await self.get_file_metadata(str(path))
            file_size = metadata.size if metadata else 0
            
            # Secure deletion (overwrite before delete for sensitive files)
            if self.security_level in [FileSecurityLevel.CONFIDENTIAL, FileSecurityLevel.RESTRICTED]:
                await self._secure_delete(path)
            else:
                os.unlink(path)
            
            # Record operation
            execution_time = (datetime.now() - start_time).total_seconds()
            result = FileOperationResult(
                success=True,
                operation=FileOperationType.DELETE,
                source_path=str(path),
                metadata=metadata,
                execution_time=execution_time,
                bytes_processed=file_size
            )
            
            self._record_operation(result)
            logger.info(f"File deleted successfully: {file_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = FileOperationResult(
                success=False,
                operation=FileOperationType.DELETE,
                source_path=file_path,
                error_message=str(e),
                execution_time=execution_time
            )
            self._record_operation(error_result)
            logger.error(f"Failed to delete file {file_path}: {e}")
            return error_result

    async def copy_file(self, 
                       source_path: str,
                       destination_path: str,
                       preserve_metadata: bool = True) -> FileOperationResult:
        """
        Copy a file to a new location
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination
            preserve_metadata: Whether to preserve file metadata
            
        Returns:
            FileOperationResult with operation details
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Copying file from {source_path} to {destination_path}")
            
            # Validate paths
            if not self._validate_path(source_path, check_exists=True):
                raise ValueError(f"Invalid or non-existent source path: {source_path}")
            
            if not self._validate_path(destination_path):
                raise ValueError(f"Invalid destination path: {destination_path}")
            
            src_path = Path(source_path)
            dst_path = Path(destination_path)
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if preserve_metadata:
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)
            
            # Generate metadata
            metadata = await self.get_file_metadata(str(dst_path))
            file_size = metadata.size if metadata else 0
            
            # Record operation
            execution_time = (datetime.now() - start_time).total_seconds()
            result = FileOperationResult(
                success=True,
                operation=FileOperationType.COPY,
                source_path=str(src_path),
                destination_path=str(dst_path),
                metadata=metadata,
                execution_time=execution_time,
                bytes_processed=file_size
            )
            
            self._record_operation(result)
            logger.info(f"File copied successfully from {source_path} to {destination_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = FileOperationResult(
                success=False,
                operation=FileOperationType.COPY,
                source_path=source_path,
                destination_path=destination_path,
                error_message=str(e),
                execution_time=execution_time
            )
            self._record_operation(error_result)
            logger.error(f"Failed to copy file from {source_path} to {destination_path}: {e}")
            return error_result

    async def move_file(self, 
                       source_path: str,
                       destination_path: str) -> FileOperationResult:
        """
        Move a file to a new location
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination
            
        Returns:
            FileOperationResult with operation details
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Moving file from {source_path} to {destination_path}")
            
            # Validate paths
            if not self._validate_path(source_path, check_exists=True):
                raise ValueError(f"Invalid or non-existent source path: {source_path}")
            
            if not self._validate_path(destination_path):
                raise ValueError(f"Invalid destination path: {destination_path}")
            
            src_path = Path(source_path)
            dst_path = Path(destination_path)
            
            # Get metadata before move
            metadata = await self.get_file_metadata(str(src_path))
            file_size = metadata.size if metadata else 0
            
            # Create destination directory if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(src_path), str(dst_path))
            
            # Update metadata with new path
            if metadata:
                metadata.path = str(dst_path)
                metadata.name = dst_path.name
            
            # Record operation
            execution_time = (datetime.now() - start_time).total_seconds()
            result = FileOperationResult(
                success=True,
                operation=FileOperationType.MOVE,
                source_path=str(src_path),
                destination_path=str(dst_path),
                metadata=metadata,
                execution_time=execution_time,
                bytes_processed=file_size
            )
            
            self._record_operation(result)
            logger.info(f"File moved successfully from {source_path} to {destination_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = FileOperationResult(
                success=False,
                operation=FileOperationType.MOVE,
                source_path=source_path,
                destination_path=destination_path,
                error_message=str(e),
                execution_time=execution_time
            )
            self._record_operation(error_result)
            logger.error(f"Failed to move file from {source_path} to {destination_path}: {e}")
            return error_result

    async def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """
        Get comprehensive metadata for a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileMetadata object or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            stat_info = path.stat()
            
            # Basic file information
            size = stat_info.st_size
            created_at = datetime.fromtimestamp(stat_info.st_ctime)
            modified_at = datetime.fromtimestamp(stat_info.st_mtime)
            accessed_at = datetime.fromtimestamp(stat_info.st_atime)
            
            # MIME type detection
            mime_type, _ = mimetypes.guess_type(str(path))
            mime_type = mime_type or "application/octet-stream"
            
            # File extension
            extension = path.suffix.lower()
            
            # Permissions
            permissions = oct(stat_info.st_mode)[-3:]
            
            # Owner and group (Unix-like systems)
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
            except (ImportError, KeyError):
                owner = str(stat_info.st_uid)
                group = str(stat_info.st_gid)
            
            # Calculate checksum
            checksum = await self._calculate_checksum(path)
            
            # Determine security level based on path and extension
            security_level = self._determine_security_level(path)
            
            # Check if file is encrypted (basic check)
            is_encrypted = await self._check_if_encrypted(path)
            
            return FileMetadata(
                path=str(path),
                name=path.name,
                size=size,
                created_at=created_at,
                modified_at=modified_at,
                accessed_at=accessed_at,
                mime_type=mime_type,
                extension=extension,
                permissions=permissions,
                owner=owner,
                group=group,
                checksum=checksum,
                security_level=security_level,
                is_encrypted=is_encrypted
            )
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return None

    async def list_files(self, 
                        directory: str,
                        recursive: bool = False,
                        pattern: Optional[str] = None,
                        include_metadata: bool = False) -> List[Union[str, FileMetadata]]:
        """
        List files in a directory
        
        Args:
            directory: Directory path to list
            recursive: Whether to list files recursively
            pattern: Glob pattern to filter files
            include_metadata: Whether to include file metadata
            
        Returns:
            List of file paths or FileMetadata objects
        """
        try:
            logger.info(f"Listing files in directory: {directory}")
            
            path = Path(directory)
            
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Directory does not exist: {directory}")
            
            files = []
            
            if recursive:
                if pattern:
                    file_paths = path.rglob(pattern)
                else:
                    file_paths = path.rglob("*")
            else:
                if pattern:
                    file_paths = path.glob(pattern)
                else:
                    file_paths = path.glob("*")
            
            for file_path in file_paths:
                if file_path.is_file():
                    if include_metadata:
                        metadata = await self.get_file_metadata(str(file_path))
                        if metadata:
                            files.append(metadata)
                    else:
                        files.append(str(file_path))
            
            logger.info(f"Found {len(files)} files in {directory}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return []

    def get_operation_stats(self) -> Dict[str, Any]:
        """
        Get file operation statistics
        
        Returns:
            Dictionary with operation statistics
        """
        return {
            **self.operation_stats,
            "recent_operations": self.operations_log[-10:],  # Last 10 operations
            "error_rate": (self.operation_stats["failed_operations"] / 
                          max(self.operation_stats["total_operations"], 1)),
            "average_execution_time": self._calculate_average_execution_time(),
            "total_bytes_processed": self.operation_stats["bytes_processed"]
        }

    # Private helper methods
    def _validate_path(self, file_path: str, check_exists: bool = False) -> bool:
        """Validate file path for security and sanity"""
        try:
            path = Path(file_path).resolve()
            
            # Check if path is within allowed base path
            if self.base_path and not str(path).startswith(str(self.base_path.resolve())):
                # Allow temp directory
                if not str(path).startswith(str(self.temp_dir.resolve())):
                    return False
            
            # Check for forbidden paths
            for forbidden in self.forbidden_paths:
                if str(path).startswith(forbidden):
                    return False
            
            # Check for dangerous extensions
            if path.suffix.lower() in self.dangerous_extensions:
                return False
            
            # Check if file exists (if required)
            if check_exists and not path.exists():
                return False
            
            # Check allowed extensions
            if self.allowed_extensions and path.suffix.lower() not in self.allowed_extensions:
                return False
            
            return True
            
        except Exception:
            return False

    def _validate_security_level(self, file_path: str, security_level: FileSecurityLevel) -> bool:
        """Validate security level requirements"""
        # Add security level validation logic here
        # For now, basic validation
        path = Path(file_path)
        
        # Restricted files must be in secure directories
        if security_level == FileSecurityLevel.RESTRICTED:
            secure_dirs = {'secure', 'restricted', 'confidential'}
            if not any(part in secure_dirs for part in path.parts):
                return False
        
        return True

    async def _secure_delete(self, path -> None: Path) -> None:
        """Securely delete a file by overwriting it first"""
        try:
            # Get file size
            file_size = path.stat().st_size
            
            # Overwrite with random data multiple times
            with open(path, 'rb+') as f:
                for _ in range(3):  # 3 passes
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.unlink(path)
            
        except Exception as e:
            logger.error(f"Secure delete failed for {path}: {e}")
            # Fallback to regular delete
            os.unlink(path)

    async def _calculate_checksum(self, path: Path, algorithm: str = "sha256") -> str:
        """Calculate file checksum"""
        try:
            hash_func = hashlib.new(algorithm)
            
            async with aiofiles.open(path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {path}: {e}")
            return ""

    def _determine_security_level(self, path: Path) -> FileSecurityLevel:
        """Determine security level based on file path and extension"""
        path_str = str(path).lower()
        
        if any(word in path_str for word in ['secret', 'confidential', 'private']):
            return FileSecurityLevel.CONFIDENTIAL
        elif any(word in path_str for word in ['restricted', 'secure']):
            return FileSecurityLevel.RESTRICTED
        elif any(word in path_str for word in ['internal', 'company']):
            return FileSecurityLevel.INTERNAL
        else:
            return FileSecurityLevel.PUBLIC

    async def _check_if_encrypted(self, path: Path) -> bool:
        """Basic check to determine if file might be encrypted"""
        try:
            # Read first few bytes to check for encryption headers
            async with aiofiles.open(path, 'rb') as f:
                header = await f.read(16)
            
            # Check for common encryption signatures
            encryption_signatures = [
                b'-----BEGIN PGP',
                b'\x00\x00\x00\x20ftypM4A',  # Encrypted M4A
                b'ENCRYPTED',
            ]
            
            return any(sig in header for sig in encryption_signatures)
            
        except Exception:
            return False

    def _record_operation(self, result -> None: FileOperationResult) -> None:
        """Record file operation for statistics"""
        self.operations_log.append(result)
        
        # Keep only last 1000 operations
        if len(self.operations_log) > 1000:
            self.operations_log = self.operations_log[-1000:]
        
        # Update statistics
        self.operation_stats["total_operations"] += 1
        
        if result.success:
            self.operation_stats["successful_operations"] += 1
        else:
            self.operation_stats["failed_operations"] += 1
        
        if result.bytes_processed:
            self.operation_stats["bytes_processed"] += result.bytes_processed

    def _calculate_average_execution_time(self) -> float:
        """Calculate average execution time for operations"""
        if not self.operations_log:
            return 0.0
        
        times = [op.execution_time for op in self.operations_log if op.execution_time]
        return sum(times) / len(times) if times else 0.0


# Utility functions for common file operations
async def ensure_directory(directory_path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


async def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return None


async def is_file_readable(file_path: str) -> bool:
    """
    Check if file is readable
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is readable
    """
    try:
        path = Path(file_path)
        return path.exists() and os.access(path, os.R_OK)
    except Exception:
        return False


async def is_file_writable(file_path: str) -> bool:
    """
    Check if file is writable
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is writable
    """
    try:
        path = Path(file_path)
        if path.exists():
            return os.access(path, os.W_OK)
        else:
            # Check if parent directory is writable
            return os.access(path.parent, os.W_OK)
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    import re
    
    # Remove or replace dangerous characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    safe_name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_name)
    
    # Limit length
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:255-len(ext)] + ext
    
    return safe_name


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Generate a unique filename in a directory
    
    Args:
        directory: Directory path
        filename: Desired filename
        
    Returns:
        Unique filename
    """
    path = Path(directory) / filename
    
    if not path.exists():
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while path.exists():
        new_filename = f"{name}_{counter}{ext}"
        path = Path(directory) / new_filename
        counter += 1
    
    return path.name