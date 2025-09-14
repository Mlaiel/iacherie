"""
Ainflue Core Platform - File Storage Core
=========================================

Enterprise-grade file storage system with multi-provider support, 
content deduplication, metadata management, and advanced file operations.
Provides unified file storage across cloud and local systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import logging
import mimetypes
import os
import time
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import aiofiles

logger = logging.getLogger(__name__)

class StorageProvider(str, Enum):
    """Supported storage providers"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    MINIO = "minio"

class FileStatus(str, Enum):
    """File status"""
    UPLOADING = "uploading"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    CORRUPTED = "corrupted"

class AccessLevel(str, Enum):
    """File access levels"""
    PRIVATE = "private"
    PUBLIC_READ = "public_read"
    PUBLIC_WRITE = "public_write"
    AUTHENTICATED = "authenticated"

@dataclass
class FileMetadata:
    """File metadata"""
    file_id: str
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    file_hash: str
    storage_provider: StorageProvider
    storage_path: str
    access_level: AccessLevel = AccessLevel.PRIVATE
    status: FileStatus = FileStatus.ACTIVE
    owner_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    upload_date: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    version: int = 1

@dataclass
class StorageQuota:
    """Storage quota information"""
    user_id: str
    total_limit: int  # bytes
    used_space: int = 0
    file_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StorageMetrics:
    """File storage metrics"""
    total_files: int = 0
    total_size: int = 0
    uploads_today: int = 0
    downloads_today: int = 0
    storage_providers_active: int = 0
    deduplication_savings: int = 0
    avg_upload_time: float = 0.0
    avg_download_time: float = 0.0

class FileStorageCore:
    """Enterprise file storage system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize file storage core"""
        self.level = level
        self.files: Dict[str, FileMetadata] = {}
        self.file_hashes: Dict[str, str] = {}  # hash -> file_id for deduplication
        self.storage_providers: Dict[str, Dict[str, Any]] = {}
        self.quotas: Dict[str, StorageQuota] = {}
        self.metrics = StorageMetrics()
        
        # Configuration
        self.config = {
            "default_provider": StorageProvider.LOCAL,
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "allowed_types": ["image/*", "video/*", "audio/*", "text/*", "application/pdf"],
            "chunk_size": 8192,
            "enable_deduplication": True,
            "auto_backup": True,
            "compression_enabled": False,
            "virus_scanning": False,
            "default_expiry_days": 365
        }
        
        # Local storage paths
        self.local_storage_path = Path("storage")
        self.temp_path = Path("temp")
        
        # Initialize local storage
        self._initialize_local_storage()
        
        logger.info(f"💾 File Storage Core initialized - Level: {level}")

    def _initialize_local_storage(self) -> None:
        """Initialize local storage directories"""
        
        self.local_storage_path.mkdir(exist_ok=True)
        self.temp_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        for subdir in ["files", "thumbnails", "backups", "temp"]:
            (self.local_storage_path / subdir).mkdir(exist_ok=True)

    async def configure_provider(
        self,
        provider -> None: StorageProvider,
        config -> None: Dict[str, Any]
    ) -> None:
        """Configure storage provider"""
        
        # Validate configuration
        if provider == StorageProvider.AWS_S3:
            required_keys = ["bucket", "region", "access_key_id", "secret_access_key"]
        elif provider == StorageProvider.AZURE_BLOB:
            required_keys = ["account_name", "account_key", "container"]
        elif provider == StorageProvider.GOOGLE_CLOUD:
            required_keys = ["project_id", "bucket", "credentials_path"]
        elif provider == StorageProvider.MINIO:
            required_keys = ["endpoint", "access_key", "secret_key", "bucket"]
        else:
            required_keys = []
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key for {provider.value}: {key}")
        
        self.storage_providers[provider.value] = config
        self.metrics.storage_providers_active = len(self.storage_providers)
        
        logger.info(f"Configured storage provider: {provider.value}")

    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: Optional[str] = None,
        owner_id: Optional[str] = None,
        access_level: AccessLevel = AccessLevel.PRIVATE,
        tags: Optional[List[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        provider: Optional[StorageProvider] = None
    ) -> str:
        """Upload file to storage"""
        
        start_time = time.time()
        
        try:
            # Read file data if it's a file-like object
            if hasattr(file_data, 'read'):
                file_data = file_data.read()
            
            # Validate file
            await self._validate_file(file_data, filename, content_type)
            
            # Check quota
            if owner_id:
                await self._check_quota(owner_id, len(file_data))
            
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Check for duplicate
            if self.config["enable_deduplication"] and file_hash in self.file_hashes:
                existing_file_id = self.file_hashes[file_hash]
                logger.info(f"File deduplicated: {filename} -> {existing_file_id}")
                self.metrics.deduplication_savings += len(file_data)
                return existing_file_id
            
            # Generate file ID and stored filename
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            stored_filename = f"{file_id}{file_extension}"
            
            # Determine content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                content_type = content_type or "application/octet-stream"
            
            # Select storage provider
            storage_provider = provider or StorageProvider(self.config["default_provider"])
            
            # Store file
            storage_path = await self._store_file(
                file_data, stored_filename, storage_provider
            )
            
            # Create metadata
            metadata = FileMetadata(
                file_id=file_id,
                original_filename=filename,
                stored_filename=stored_filename,
                content_type=content_type,
                file_size=len(file_data),
                file_hash=file_hash,
                storage_provider=storage_provider,
                storage_path=storage_path,
                access_level=access_level,
                owner_id=owner_id,
                tags=tags or [],
                custom_metadata=custom_metadata or {}
            )
            
            # Store metadata
            self.files[file_id] = metadata
            self.file_hashes[file_hash] = file_id
            
            # Update quota
            if owner_id:
                await self._update_quota(owner_id, len(file_data), 1)
            
            # Update metrics
            self.metrics.total_files += 1
            self.metrics.total_size += len(file_data)
            self.metrics.uploads_today += 1
            
            upload_time = time.time() - start_time
            self.metrics.avg_upload_time = (
                self.metrics.avg_upload_time * 0.9 + upload_time * 0.1
            )
            
            logger.info(f"Uploaded file {filename} -> {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise

    async def _validate_file(
        self,
        file_data -> None: bytes,
        filename -> None: str,
        content_type -> None: Optional[str]
    ) -> None:
        """Validate file before upload"""
        
        # Check file size
        if len(file_data) > self.config["max_file_size"]:
            raise ValueError(f"File too large: {len(file_data)} > {self.config['max_file_size']}")
        
        # Check file type
        if content_type:
            allowed = False
            for allowed_type in self.config["allowed_types"]:
                if allowed_type.endswith("*"):
                    if content_type.startswith(allowed_type[:-1]):
                        allowed = True
                        break
                elif content_type == allowed_type:
                    allowed = True
                    break
            
            if not allowed:
                raise ValueError(f"File type not allowed: {content_type}")
        
        # Check for empty file
        if len(file_data) == 0:
            raise ValueError("File is empty")

    async def _check_quota(self, user_id -> None: str, file_size -> None: int) -> None:
        """Check user storage quota"""
        
        quota = self.quotas.get(user_id)
        if not quota:
            # Create default quota
            quota = StorageQuota(
                user_id=user_id,
                total_limit=1024 * 1024 * 1024  # 1GB default
            )
            self.quotas[user_id] = quota
        
        if quota.used_space + file_size > quota.total_limit:
            raise ValueError(f"Storage quota exceeded: {quota.used_space + file_size} > {quota.total_limit}")

    async def _update_quota(self, user_id -> None: str, size_delta -> None: int, file_delta -> None: int) -> None:
        """Update user storage quota"""
        
        quota = self.quotas.get(user_id)
        if quota:
            quota.used_space += size_delta
            quota.file_count += file_delta
            quota.last_updated = datetime.utcnow()

    async def _store_file(
        self,
        file_data: bytes,
        stored_filename: str,
        provider: StorageProvider
    ) -> str:
        """Store file using specified provider"""
        
        if provider == StorageProvider.LOCAL:
            return await self._store_local(file_data, stored_filename)
        elif provider == StorageProvider.AWS_S3:
            return await self._store_s3(file_data, stored_filename)
        elif provider == StorageProvider.AZURE_BLOB:
            return await self._store_azure(file_data, stored_filename)
        elif provider == StorageProvider.GOOGLE_CLOUD:
            return await self._store_gcs(file_data, stored_filename)
        elif provider == StorageProvider.MINIO:
            return await self._store_minio(file_data, stored_filename)
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")

    async def _store_local(self, file_data: bytes, stored_filename: str) -> str:
        """Store file locally"""
        
        file_path = self.local_storage_path / "files" / stored_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
        
        return str(file_path)

    async def _store_s3(self, file_data: bytes, stored_filename: str) -> str:
        """Store file in AWS S3"""
        
        # Placeholder for S3 implementation
        # In production, would use boto3 or aioboto3
        
        config = self.storage_providers.get("aws_s3")
        if not config:
            raise ValueError("AWS S3 not configured")
        
        # Mock S3 storage path
        s3_path = f"s3://{config['bucket']}/{stored_filename}"
        
        # For now, store locally as fallback
        return await self._store_local(file_data, stored_filename)

    async def _store_azure(self, file_data: bytes, stored_filename: str) -> str:
        """Store file in Azure Blob Storage"""
        
        # Placeholder for Azure implementation
        config = self.storage_providers.get("azure_blob")
        if not config:
            raise ValueError("Azure Blob Storage not configured")
        
        azure_path = f"https://{config['account_name']}.blob.core.windows.net/{config['container']}/{stored_filename}"
        
        # For now, store locally as fallback
        return await self._store_local(file_data, stored_filename)

    async def _store_gcs(self, file_data: bytes, stored_filename: str) -> str:
        """Store file in Google Cloud Storage"""
        
        # Placeholder for GCS implementation
        config = self.storage_providers.get("google_cloud")
        if not config:
            raise ValueError("Google Cloud Storage not configured")
        
        gcs_path = f"gs://{config['bucket']}/{stored_filename}"
        
        # For now, store locally as fallback
        return await self._store_local(file_data, stored_filename)

    async def _store_minio(self, file_data: bytes, stored_filename: str) -> str:
        """Store file in MinIO"""
        
        # Placeholder for MinIO implementation
        config = self.storage_providers.get("minio")
        if not config:
            raise ValueError("MinIO not configured")
        
        minio_path = f"{config['endpoint']}/{config['bucket']}/{stored_filename}"
        
        # For now, store locally as fallback
        return await self._store_local(file_data, stored_filename)

    async def download_file(self, file_id: str) -> bytes:
        """Download file by ID"""
        
        start_time = time.time()
        
        try:
            metadata = self.files.get(file_id)
            if not metadata:
                raise ValueError(f"File {file_id} not found")
            
            if metadata.status != FileStatus.ACTIVE:
                raise ValueError(f"File {file_id} is not active (status: {metadata.status})")
            
            # Download from provider
            file_data = await self._download_from_provider(metadata)
            
            # Update access time
            metadata.last_accessed = datetime.utcnow()
            
            # Update metrics
            self.metrics.downloads_today += 1
            download_time = time.time() - start_time
            self.metrics.avg_download_time = (
                self.metrics.avg_download_time * 0.9 + download_time * 0.1
            )
            
            logger.debug(f"Downloaded file {file_id}")
            return file_data
            
        except Exception as e:
            logger.error(f"File download failed: {str(e)}")
            raise

    async def _download_from_provider(self, metadata: FileMetadata) -> bytes:
        """Download file from storage provider"""
        
        if metadata.storage_provider == StorageProvider.LOCAL:
            return await self._download_local(metadata.storage_path)
        else:
            # For other providers, implement specific download logic
            # For now, fallback to local storage
            local_path = self.local_storage_path / "files" / metadata.stored_filename
            return await self._download_local(str(local_path))

    async def _download_local(self, file_path: str) -> bytes:
        """Download file from local storage"""
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

    async def get_file_url(
        self,
        file_id: str,
        expiry_seconds: int = 3600
    ) -> str:
        """Get temporary URL for file access"""
        
        metadata = self.files.get(file_id)
        if not metadata:
            raise ValueError(f"File {file_id} not found")
        
        if metadata.access_level == AccessLevel.PUBLIC_READ:
            # Generate public URL
            if metadata.storage_provider == StorageProvider.LOCAL:
                return f"/files/{file_id}"
            else:
                # For cloud providers, would generate signed URLs
                return f"/files/{file_id}"
        else:
            # Generate signed URL
            expiry_time = datetime.utcnow() + timedelta(seconds=expiry_seconds)
            signature = self._generate_url_signature(file_id, expiry_time)
            
            return f"/files/{file_id}?expires={int(expiry_time.timestamp())}&signature={signature}"

    def _generate_url_signature(self, file_id: str, expiry_time: datetime) -> str:
        """Generate URL signature for secure access"""
        
        # Simple signature generation
        # In production, would use proper signing mechanism
        data = f"{file_id}:{int(expiry_time.timestamp())}"
        return hashlib.md5(data.encode()).hexdigest()

    async def delete_file(self, file_id: str, permanent: bool = False) -> bool:
        """Delete file"""
        
        try:
            metadata = self.files.get(file_id)
            if not metadata:
                raise ValueError(f"File {file_id} not found")
            
            if permanent:
                # Permanently delete file
                await self._delete_from_provider(metadata)
                
                # Remove from storage
                del self.files[file_id]
                if metadata.file_hash in self.file_hashes:
                    del self.file_hashes[metadata.file_hash]
                
                # Update quota
                if metadata.owner_id:
                    await self._update_quota(metadata.owner_id, -metadata.file_size, -1)
                
                # Update metrics
                self.metrics.total_files -= 1
                self.metrics.total_size -= metadata.file_size
                
            else:
                # Soft delete
                metadata.status = FileStatus.DELETED
                metadata.expiry_date = datetime.utcnow() + timedelta(days=30)
            
            logger.info(f"Deleted file {file_id} (permanent: {permanent})")
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False

    async def _delete_from_provider(self, metadata -> None: FileMetadata) -> None:
        """Delete file from storage provider"""
        
        if metadata.storage_provider == StorageProvider.LOCAL:
            try:
                os.remove(metadata.storage_path)
            except FileNotFoundError:
                pass  # Already deleted
        else:
            # For other providers, implement specific deletion logic
            pass

    async def list_files(
        self,
        owner_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        content_type: Optional[str] = None,
        status: Optional[FileStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FileMetadata]:
        """List files with filters"""
        
        files = list(self.files.values())
        
        # Apply filters
        if owner_id:
            files = [f for f in files if f.owner_id == owner_id]
        
        if tags:
            files = [f for f in files if any(tag in f.tags for tag in tags)]
        
        if content_type:
            files = [f for f in files if f.content_type.startswith(content_type)]
        
        if status:
            files = [f for f in files if f.status == status]
        
        # Sort by upload date (newest first)
        files.sort(key=lambda x: x.upload_date, reverse=True)
        
        # Apply pagination
        return files[offset:offset + limit]

    async def cleanup_expired_files(self) -> None:
        """Clean up expired files"""
        
        current_time = datetime.utcnow()
        expired_files = []
        
        for file_id, metadata in self.files.items():
            if (metadata.expiry_date and 
                metadata.expiry_date < current_time and
                metadata.status == FileStatus.DELETED):
                expired_files.append(file_id)
        
        # Permanently delete expired files
        for file_id in expired_files:
            await self.delete_file(file_id, permanent=True)
        
        if expired_files:
            logger.info(f"Cleaned up {len(expired_files)} expired files")

    def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID"""
        return self.files.get(file_id)

    def get_storage_quota(self, user_id: str) -> Optional[StorageQuota]:
        """Get user storage quota"""
        return self.quotas.get(user_id)

    async def set_storage_quota(
        self,
        user_id -> None: str,
        total_limit -> None: int
    ) -> None:
        """Set user storage quota"""
        
        quota = self.quotas.get(user_id)
        if quota:
            quota.total_limit = total_limit
            quota.last_updated = datetime.utcnow()
        else:
            self.quotas[user_id] = StorageQuota(
                user_id=user_id,
                total_limit=total_limit
            )

    def get_metrics(self) -> StorageMetrics:
        """Get storage metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for file storage system"""
        try:
            # Test file operations
            test_data = b"test file content"
            
            # Test upload
            file_id = await self.upload_file(
                test_data,
                "test.txt",
                "text/plain"
            )
            
            # Test download
            downloaded_data = await self.download_file(file_id)
            
            # Test deletion
            await self.delete_file(file_id, permanent=True)
            
            # Verify data integrity
            return downloaded_data == test_data
            
        except Exception as e:
            logger.error(f"File storage health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "FileStorageCore", "FileMetadata", "StorageQuota", "StorageMetrics",
    "StorageProvider", "FileStatus", "AccessLevel"
]

logger.info("💾 File Storage Core module loaded")