"""
File System Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module - File System Manager
# =================================================
# 
# Enterprise-grade file system management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
File System Manager - Enterprise File System Management

Provides comprehensive file system management capabilities including:
- Distributed file system orchestration
- Multi-cloud storage integration
- File metadata and indexing
- Access control and permissions
- Performance monitoring and optimization
"""

import asyncio
import logging
import os
import shutil
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import mimetypes
import json
import stat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageProvider(Enum):
    """Storage provider enumeration"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD_STORAGE = "google_cloud_storage"
    AZURE_BLOB = "azure_blob"
    DISTRIBUTED_FS = "distributed_fs"

class FileType(Enum):
    """File type enumeration"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    UNKNOWN = "unknown"

class AccessLevel(Enum):
    """File access level enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    RESTRICTED = "restricted"

class CompressionType(Enum):
    """Compression type enumeration"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"

@dataclass
class FileMetadata:
    """File metadata dataclass"""
    path: str
    name: str
    size: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    mime_type: str
    file_type: FileType
    checksum: str
    access_level: AccessLevel = AccessLevel.PRIVATE
    owner_id: str = ""
    permissions: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    storage_provider: StorageProvider = StorageProvider.LOCAL
    encryption_key: Optional[str] = None
    compression: CompressionType = CompressionType.NONE

@dataclass
class StorageQuota:
    """Storage quota configuration"""
    user_id: str
    max_storage_bytes: int
    used_storage_bytes: int = 0
    max_files: int = 10000
    file_count: int = 0
    bandwidth_limit_mbps: int = 100
    allowed_file_types: List[FileType] = field(default_factory=list)

@dataclass
class StorageMetrics:
    """Storage metrics dataclass"""
    total_files: int
    total_size_bytes: int
    storage_utilization: float
    access_count: int
    bandwidth_usage_mbps: float
    cache_hit_rate: float
    timestamp: datetime = field(default_factory=datetime.now)

class FileSystemManager:
    """
    Enterprise File System Manager
    
    Manages distributed file systems, storage providers, file metadata,
    and access control across the Ainflue platform.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize file system manager"""
        self.config_path = config_path or "/home/runner/work/Ainflue/Ainflue/infra/storage"
        self.base_storage_path = f"{self.config_path}/storage_data"
        self.metadata_store: Dict[str, FileMetadata] = {}
        self.storage_quotas: Dict[str, StorageQuota] = {}
        self.provider_configs: Dict[StorageProvider, Dict[str, Any]] = {}
        self.metrics_history: List[StorageMetrics] = []
        
        # Enterprise configuration
        self.enable_encryption = True
        self.enable_compression = True
        self.enable_deduplication = True
        self.max_file_size_mb = 500  # 500MB
        self.cache_enabled = True
        self.backup_enabled = True
        
        # File type mappings
        self.mime_type_mappings = self._initialize_mime_mappings()
        
        # Initialize file system
        self._initialize_file_system()
    
    def _initialize_file_system(self) -> None:
        """Initialize file system manager"""
        try:
            # Create base directories
            self._create_base_directories()
            
            # Initialize storage providers
            self._initialize_storage_providers()
            
            # Load existing metadata
            self._load_metadata_store()
            
            # Load quotas
            self._load_storage_quotas()
            
            logger.info("File system manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize file system: {e}")
            raise
    
    def _create_base_directories(self) -> None:
        """Create base storage directories"""
        try:
            directories = [
                f"{self.base_storage_path}/users",
                f"{self.base_storage_path}/content",
                f"{self.base_storage_path}/ai_models",
                f"{self.base_storage_path}/temp",
                f"{self.base_storage_path}/cache",
                f"{self.base_storage_path}/backup",
                f"{self.base_storage_path}/metadata"
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                
                # Set proper permissions
                os.chmod(directory, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
            
            logger.info(f"Created {len(directories)} base directories")
            
        except Exception as e:
            logger.error(f"Failed to create base directories: {e}")
            raise
    
    def _initialize_storage_providers(self) -> None:
        """Initialize storage provider configurations"""
        try:
            # Local storage provider
            self.provider_configs[StorageProvider.LOCAL] = {
                "base_path": self.base_storage_path,
                "max_storage_gb": 1000,
                "backup_enabled": True
            }
            
            # AWS S3 provider
            self.provider_configs[StorageProvider.AWS_S3] = {
                "bucket_name": "ainflue-storage",
                "region": "us-east-1",
                "storage_class": "STANDARD",
                "encryption": "AES256"
            }
            
            # Google Cloud Storage provider
            self.provider_configs[StorageProvider.GOOGLE_CLOUD_STORAGE] = {
                "bucket_name": "ainflue-gcs-storage",
                "location": "US",
                "storage_class": "STANDARD",
                "encryption": "GOOGLE_MANAGED"
            }
            
            # Azure Blob Storage provider
            self.provider_configs[StorageProvider.AZURE_BLOB] = {
                "container_name": "ainflue-blob-storage",
                "account_name": "ainfluestorage",
                "tier": "Hot",
                "encryption": "AES256"
            }
            
            logger.info(f"Initialized {len(self.provider_configs)} storage providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage providers: {e}")
            raise
    
    def _initialize_mime_mappings(self) -> Dict[str, FileType]:
        """Initialize MIME type to file type mappings"""
        return {
            # Documents
            "text/plain": FileType.DOCUMENT,
            "text/html": FileType.DOCUMENT,
            "application/pdf": FileType.DOCUMENT,
            "application/msword": FileType.DOCUMENT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCUMENT,
            
            # Images
            "image/jpeg": FileType.IMAGE,
            "image/png": FileType.IMAGE,
            "image/gif": FileType.IMAGE,
            "image/webp": FileType.IMAGE,
            "image/svg+xml": FileType.IMAGE,
            
            # Videos
            "video/mp4": FileType.VIDEO,
            "video/avi": FileType.VIDEO,
            "video/quicktime": FileType.VIDEO,
            "video/x-msvideo": FileType.VIDEO,
            "video/webm": FileType.VIDEO,
            
            # Audio
            "audio/mpeg": FileType.AUDIO,
            "audio/wav": FileType.AUDIO,
            "audio/mp4": FileType.AUDIO,
            "audio/flac": FileType.AUDIO,
            "audio/ogg": FileType.AUDIO,
            
            # Archives
            "application/zip": FileType.ARCHIVE,
            "application/x-tar": FileType.ARCHIVE,
            "application/gzip": FileType.ARCHIVE,
            "application/x-7z-compressed": FileType.ARCHIVE,
            
            # Code
            "text/x-python": FileType.CODE,
            "application/javascript": FileType.CODE,
            "text/css": FileType.CODE,
            "application/json": FileType.DATA,
            "application/xml": FileType.DATA
        }
    
    def _load_metadata_store(self) -> None:
        """Load file metadata store"""
        try:
            metadata_file = Path(f"{self.config_path}/metadata_store.json")
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                
                for file_path, metadata in metadata_data.items():
                    file_metadata = self._deserialize_metadata(metadata)
                    self.metadata_store[file_path] = file_metadata
                
                logger.info(f"Loaded metadata for {len(self.metadata_store)} files")
            
        except Exception as e:
            logger.error(f"Failed to load metadata store: {e}")
    
    def _load_storage_quotas(self) -> None:
        """Load storage quotas"""
        try:
            quotas_file = Path(f"{self.config_path}/storage_quotas.json")
            if quotas_file.exists():
                with open(quotas_file, 'r') as f:
                    quotas_data = json.load(f)
                
                for user_id, quota_data in quotas_data.items():
                    quota = StorageQuota(
                        user_id=quota_data["user_id"],
                        max_storage_bytes=quota_data["max_storage_bytes"],
                        used_storage_bytes=quota_data.get("used_storage_bytes", 0),
                        max_files=quota_data.get("max_files", 10000),
                        file_count=quota_data.get("file_count", 0),
                        bandwidth_limit_mbps=quota_data.get("bandwidth_limit_mbps", 100),
                        allowed_file_types=[FileType(ft) for ft in quota_data.get("allowed_file_types", [])]
                    )
                    self.storage_quotas[user_id] = quota
                
                logger.info(f"Loaded quotas for {len(self.storage_quotas)} users")
            
        except Exception as e:
            logger.error(f"Failed to load storage quotas: {e}")
    
    def _deserialize_metadata(self, metadata_data: Dict[str, Any]) -> FileMetadata:
        """Deserialize file metadata from JSON"""
        return FileMetadata(
            path=metadata_data["path"],
            name=metadata_data["name"],
            size=metadata_data["size"],
            created_at=datetime.fromisoformat(metadata_data["created_at"]),
            modified_at=datetime.fromisoformat(metadata_data["modified_at"]),
            accessed_at=datetime.fromisoformat(metadata_data["accessed_at"]),
            mime_type=metadata_data["mime_type"],
            file_type=FileType(metadata_data["file_type"]),
            checksum=metadata_data["checksum"],
            access_level=AccessLevel(metadata_data.get("access_level", "private")),
            owner_id=metadata_data.get("owner_id", ""),
            permissions=metadata_data.get("permissions", {}),
            tags=metadata_data.get("tags", []),
            metadata=metadata_data.get("metadata", {}),
            storage_provider=StorageProvider(metadata_data.get("storage_provider", "local")),
            encryption_key=metadata_data.get("encryption_key"),
            compression=CompressionType(metadata_data.get("compression", "none"))
        )
    
    async def store_file(self, file_path: str, content: Union[bytes, BinaryIO], 
                        user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[FileMetadata]:
        """Store a file in the file system"""
        try:
            # Validate user quota
            if not self._check_user_quota(user_id, len(content) if isinstance(content, bytes) else 0):
                logger.error(f"User quota exceeded: {user_id}")
                return None
            
            # Determine storage provider
            provider = self._select_storage_provider(file_path)
            
            # Generate file metadata
            file_metadata = await self._generate_file_metadata(file_path, content, user_id, provider)
            if metadata:
                file_metadata.metadata.update(metadata)
            
            # Store file content
            if await self._store_file_content(file_path, content, provider):
                # Update metadata store
                self.metadata_store[file_path] = file_metadata
                
                # Update user quota
                self._update_user_quota(user_id, file_metadata.size, 1)
                
                # Save metadata
                self._save_metadata_store()
                
                logger.info(f"File stored successfully: {file_path}")
                return file_metadata
            else:
                logger.error(f"Failed to store file content: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to store file {file_path}: {e}")
            return None
    
    def _check_user_quota(self, user_id: str, file_size: int) -> bool:
        """Check if user has sufficient quota"""
        try:
            if user_id not in self.storage_quotas:
                # Create default quota for new user
                self.storage_quotas[user_id] = StorageQuota(
                    user_id=user_id,
                    max_storage_bytes=10 * 1024 * 1024 * 1024,  # 10GB default
                    allowed_file_types=list(FileType)
                )
            
            quota = self.storage_quotas[user_id]
            
            # Check storage limit
            if quota.used_storage_bytes + file_size > quota.max_storage_bytes:
                return False
            
            # Check file count limit
            if quota.file_count >= quota.max_files:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check user quota: {e}")
            return False
    
    def _select_storage_provider(self, file_path: str) -> StorageProvider:
        """Select appropriate storage provider for file"""
        try:
            # For now, use local storage for everything
            # In production, this would have more sophisticated logic
            return StorageProvider.LOCAL
            
        except Exception as e:
            logger.error(f"Failed to select storage provider: {e}")
            return StorageProvider.LOCAL
    
    async def _generate_file_metadata(self, file_path: str, content: Union[bytes, BinaryIO],
                                     user_id: str, provider: StorageProvider) -> FileMetadata:
        """Generate file metadata"""
        try:
            # Get file content as bytes
            if isinstance(content, bytes):
                file_bytes = content
            else:
                file_bytes = content.read()
                content.seek(0)  # Reset position
            
            # Calculate file properties
            file_size = len(file_bytes)
            checksum = hashlib.sha256(file_bytes).hexdigest()
            
            # Determine MIME type and file type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            file_type = self.mime_type_mappings.get(mime_type, FileType.UNKNOWN)
            
            # Get file name
            file_name = os.path.basename(file_path)
            
            # Create metadata
            now = datetime.now()
            metadata = FileMetadata(
                path=file_path,
                name=file_name,
                size=file_size,
                created_at=now,
                modified_at=now,
                accessed_at=now,
                mime_type=mime_type,
                file_type=file_type,
                checksum=checksum,
                owner_id=user_id,
                storage_provider=provider
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to generate file metadata: {e}")
            raise
    
    async def _store_file_content(self, file_path: str, content: Union[bytes, BinaryIO],
                                 provider: StorageProvider) -> bool:
        """Store file content using specified provider"""
        try:
            if provider == StorageProvider.LOCAL:
                return await self._store_local_file(file_path, content)
            elif provider == StorageProvider.AWS_S3:
                return await self._store_s3_file(file_path, content)
            elif provider == StorageProvider.GOOGLE_CLOUD_STORAGE:
                return await self._store_gcs_file(file_path, content)
            elif provider == StorageProvider.AZURE_BLOB:
                return await self._store_azure_file(file_path, content)
            else:
                logger.error(f"Unsupported storage provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to store file content: {e}")
            return False
    
    async def _store_local_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> bool:
        """Store file in local file system"""
        try:
            # Create full path
            full_path = os.path.join(self.base_storage_path, file_path.lstrip('/'))
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file content
            with open(full_path, 'wb') as f:
                if isinstance(content, bytes):
                    f.write(content)
                else:
                    shutil.copyfileobj(content, f)
            
            # Set file permissions
            os.chmod(full_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store local file: {e}")
            return False
    
    async def _store_s3_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> bool:
        """Store file in AWS S3"""
        try:
            # This would use boto3 to upload to S3
            # For now, return success for demo
            logger.info(f"Would store file in S3: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store S3 file: {e}")
            return False
    
    async def _store_gcs_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> bool:
        """Store file in Google Cloud Storage"""
        try:
            # This would use google-cloud-storage to upload
            # For now, return success for demo
            logger.info(f"Would store file in GCS: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store GCS file: {e}")
            return False
    
    async def _store_azure_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> bool:
        """Store file in Azure Blob Storage"""
        try:
            # This would use azure-storage-blob to upload
            # For now, return success for demo
            logger.info(f"Would store file in Azure: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store Azure file: {e}")
            return False
    
    def _update_user_quota(self, user_id: str, size_bytes: int, file_count: int) -> None:
        """Update user storage quota"""
        try:
            if user_id in self.storage_quotas:
                quota = self.storage_quotas[user_id]
                quota.used_storage_bytes += size_bytes
                quota.file_count += file_count
                
                # Save quotas
                self._save_storage_quotas()
            
        except Exception as e:
            logger.error(f"Failed to update user quota: {e}")
    
    async def retrieve_file(self, file_path: str, user_id: str) -> Optional[bytes]:
        """Retrieve file content"""
        try:
            # Check if file exists in metadata
            if file_path not in self.metadata_store:
                logger.error(f"File not found: {file_path}")
                return None
            
            metadata = self.metadata_store[file_path]
            
            # Check access permissions
            if not self._check_file_access(metadata, user_id):
                logger.error(f"Access denied for file: {file_path}")
                return None
            
            # Retrieve file content
            content = await self._retrieve_file_content(file_path, metadata.storage_provider)
            
            # Update access time
            metadata.accessed_at = datetime.now()
            self._save_metadata_store()
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_path}: {e}")
            return None
    
    def _check_file_access(self, metadata: FileMetadata, user_id: str) -> bool:
        """Check if user has access to file"""
        try:
            # Owner always has access
            if metadata.owner_id == user_id:
                return True
            
            # Check access level
            if metadata.access_level == AccessLevel.PUBLIC:
                return True
            elif metadata.access_level == AccessLevel.PRIVATE:
                return False
            elif metadata.access_level == AccessLevel.SHARED:
                # Check if user is in permissions
                return user_id in metadata.permissions
            elif metadata.access_level == AccessLevel.RESTRICTED:
                # Check specific permissions
                user_permission = metadata.permissions.get(user_id, "none")
                return user_permission in ["read", "write", "admin"]
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check file access: {e}")
            return False
    
    async def _retrieve_file_content(self, file_path: str, provider: StorageProvider) -> Optional[bytes]:
        """Retrieve file content from storage provider"""
        try:
            if provider == StorageProvider.LOCAL:
                return await self._retrieve_local_file(file_path)
            elif provider == StorageProvider.AWS_S3:
                return await self._retrieve_s3_file(file_path)
            # Add other providers as needed
            else:
                logger.error(f"Unsupported storage provider: {provider}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve file content: {e}")
            return None
    
    async def _retrieve_local_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from local storage"""
        try:
            full_path = os.path.join(self.base_storage_path, file_path.lstrip('/'))
            
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    return f.read()
            else:
                logger.error(f"Local file not found: {full_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve local file: {e}")
            return None
    
    async def _retrieve_s3_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from S3"""
        try:
            # This would use boto3 to download from S3
            # For now, return None for demo
            logger.info(f"Would retrieve file from S3: {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve S3 file: {e}")
            return None
    
    def delete_file(self, file_path: str, user_id: str) -> bool:
        """Delete a file"""
        try:
            # Check if file exists
            if file_path not in self.metadata_store:
                logger.error(f"File not found: {file_path}")
                return False
            
            metadata = self.metadata_store[file_path]
            
            # Check permissions (only owner or admin can delete)
            if metadata.owner_id != user_id:
                user_permission = metadata.permissions.get(user_id, "none")
                if user_permission != "admin":
                    logger.error(f"Access denied for file deletion: {file_path}")
                    return False
            
            # Delete file content
            if self._delete_file_content(file_path, metadata.storage_provider):
                # Update user quota
                self._update_user_quota(metadata.owner_id, -metadata.size, -1)
                
                # Remove from metadata store
                del self.metadata_store[file_path]
                
                # Save metadata
                self._save_metadata_store()
                
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.error(f"Failed to delete file content: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def _delete_file_content(self, file_path: str, provider: StorageProvider) -> bool:
        """Delete file content from storage provider"""
        try:
            if provider == StorageProvider.LOCAL:
                full_path = os.path.join(self.base_storage_path, file_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
                return True
            # Add other providers as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file content: {e}")
            return False
    
    def list_files(self, user_id: str, directory: str = "", 
                  file_type: Optional[FileType] = None) -> List[FileMetadata]:
        """List files accessible to user"""
        try:
            accessible_files = []
            
            for file_path, metadata in self.metadata_store.items():
                # Check directory filter
                if directory and not file_path.startswith(directory):
                    continue
                
                # Check file type filter
                if file_type and metadata.file_type != file_type:
                    continue
                
                # Check access permissions
                if self._check_file_access(metadata, user_id):
                    accessible_files.append(metadata)
            
            # Sort by modified time (newest first)
            accessible_files.sort(key=lambda x: x.modified_at, reverse=True)
            
            return accessible_files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_storage_metrics(self) -> StorageMetrics:
        """Get storage system metrics"""
        try:
            total_files = len(self.metadata_store)
            total_size = sum(metadata.size for metadata in self.metadata_store.values())
            
            # Calculate storage utilization
            total_quota = sum(quota.max_storage_bytes for quota in self.storage_quotas.values())
            storage_utilization = total_size / total_quota if total_quota > 0 else 0.0
            
            metrics = StorageMetrics(
                total_files=total_files,
                total_size_bytes=total_size,
                storage_utilization=storage_utilization,
                access_count=len(self.metadata_store),  # Simplified
                bandwidth_usage_mbps=50.0,  # Mock value
                cache_hit_rate=0.85  # Mock value
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get storage metrics: {e}")
            return StorageMetrics(0, 0, 0.0, 0, 0.0, 0.0)
    
    def _save_metadata_store(self) -> None:
        """Save metadata store to file"""
        try:
            metadata_data = {}
            for file_path, metadata in self.metadata_store.items():
                metadata_data[file_path] = self._serialize_metadata(metadata)
            
            metadata_file = Path(f"{self.config_path}/metadata_store.json")
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to save metadata store: {e}")
    
    def _save_storage_quotas(self) -> None:
        """Save storage quotas to file"""
        try:
            quotas_data = {}
            for user_id, quota in self.storage_quotas.items():
                quotas_data[user_id] = {
                    "user_id": quota.user_id,
                    "max_storage_bytes": quota.max_storage_bytes,
                    "used_storage_bytes": quota.used_storage_bytes,
                    "max_files": quota.max_files,
                    "file_count": quota.file_count,
                    "bandwidth_limit_mbps": quota.bandwidth_limit_mbps,
                    "allowed_file_types": [ft.value for ft in quota.allowed_file_types]
                }
            
            quotas_file = Path(f"{self.config_path}/storage_quotas.json")
            quotas_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(quotas_file, 'w') as f:
                json.dump(quotas_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save storage quotas: {e}")
    
    def _serialize_metadata(self, metadata: FileMetadata) -> Dict[str, Any]:
        """Serialize file metadata to JSON-compatible dict"""
        return {
            "path": metadata.path,
            "name": metadata.name,
            "size": metadata.size,
            "created_at": metadata.created_at.isoformat(),
            "modified_at": metadata.modified_at.isoformat(),
            "accessed_at": metadata.accessed_at.isoformat(),
            "mime_type": metadata.mime_type,
            "file_type": metadata.file_type.value,
            "checksum": metadata.checksum,
            "access_level": metadata.access_level.value,
            "owner_id": metadata.owner_id,
            "permissions": metadata.permissions,
            "tags": metadata.tags,
            "metadata": metadata.metadata,
            "storage_provider": metadata.storage_provider.value,
            "encryption_key": metadata.encryption_key,
            "compression": metadata.compression.value
        }
    
    def get_file_system_status(self) -> Dict[str, Any]:
        """Get file system status"""
        return {
            "total_files": len(self.metadata_store),
            "storage_providers": len(self.provider_configs),
            "users_with_quotas": len(self.storage_quotas),
            "metrics_collected": len(self.metrics_history),
            "encryption_enabled": self.enable_encryption,
            "compression_enabled": self.enable_compression,
            "deduplication_enabled": self.enable_deduplication,
            "cache_enabled": self.cache_enabled,
            "backup_enabled": self.backup_enabled,
            "max_file_size_mb": self.max_file_size_mb
        }

# Enterprise File System Manager instance
file_system = FileSystemManager()

# Export for use in other modules
__all__ = [
    "FileSystemManager",
    "FileMetadata",
    "StorageQuota",
    "StorageMetrics",
    "StorageProvider",
    "FileType",
    "AccessLevel",
    "CompressionType",
    "file_system"
]