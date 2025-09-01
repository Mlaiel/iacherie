"""Enterprise Storage Service - S3/MinIO Integration for Content Storage

High-performance cloud storage service supporting AWS S3, MinIO, and other
S3-compatible storage backends for content fingerprints and media files.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- DevOps Engineer: Cloud infrastructure and storage optimization
- Storage Architect: Distributed storage systems and data lifecycle
- Security Engineer: Encryption and access control systems
- Database Administrator: Storage performance and optimization

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""
import asyncio
import logging
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json
import tempfile
import aiofiles
from urllib.parse import urlparse

# S3/MinIO imports
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    from botocore.config import Config
except ImportError:
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception
    Config = None
    logging.warning("boto3 not installed. S3 functionality will be limited.")

# Async S3 client
try:
    import aioboto3
except ImportError:
    aioboto3 = None
    logging.warning("aioboto3 not installed. Async S3 functionality will be limited.")

# Image processing for thumbnails
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    logging.warning("Pillow not installed. Image processing functionality will be limited.")

# Video processing for thumbnails
try:
    import cv2
except ImportError:
    cv2 = None
    logging.warning("OpenCV not installed. Video processing functionality will be limited.")

# Audio processing for waveforms
try:
    import librosa
    import matplotlib.pyplot as plt
    import io
except ImportError:
    librosa = None
    plt = None
    io = None
    logging.warning("Audio processing libraries not installed. Audio visualization will be limited.")

from ..core.exceptions import StorageException, ValidationException
from ..core.models import BaseModel
from ..core.config import get_settings


class StorageType(Enum):
    """Types of storage backends."""
    AWS_S3 = "aws_s3"
    MINIO = "minio"
    LOCAL_FILE = "local_file"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"


class FileType(Enum):
    """Types of files stored."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    FINGERPRINT = "fingerprint"
    METADATA = "metadata"
    THUMBNAIL = "thumbnail"
    WAVEFORM = "waveform"


class StorageClass(Enum):
    """Storage classes for cost optimization."""
    STANDARD = "STANDARD"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"


@dataclass
class StorageConfig:
    """Storage configuration."""
    storage_type: StorageType
    endpoint_url: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket_name: str = "ia-influencer-content"
    region: str = "us-east-1"
    use_ssl: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.mp3', '.wav', '.flac', '.aac', '.ogg',  # Audio
        '.mp4', '.avi', '.mov', '.mkv', '.webm',  # Video
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff',  # Images
        '.txt', '.md', '.html', '.json', '.xml',  # Text
        '.pdf', '.doc', '.docx'  # Documents
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "storage_type": self.storage_type.value,
            "endpoint_url": self.endpoint_url,
            "bucket_name": self.bucket_name,
            "region": self.region,
            "use_ssl": self.use_ssl,
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_extensions
        }


@dataclass
class StoredFile:
    """Stored file metadata."""
    file_id: str
    original_filename: str
    stored_key: str
    file_type: FileType
    content_type: str
    size: int
    checksum: str
    storage_url: str
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    storage_class: StorageClass = StorageClass.STANDARD
    encryption_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_id": self.file_id,
            "original_filename": self.original_filename,
            "stored_key": self.stored_key,
            "file_type": self.file_type.value,
            "content_type": self.content_type,
            "size": self.size,
            "checksum": self.checksum,
            "storage_url": self.storage_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "storage_class": self.storage_class.value,
            "encryption_enabled": self.encryption_enabled
        }


@dataclass
class FileIndex:
    """File index for search and metadata."""
    index_id: str
    file_id: str
    filename: str
    file_type: FileType
    content_type: str
    tags: List[str]
    metadata: Dict[str, Any]
    searchable_content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index_id": self.index_id,
            "file_id": self.file_id,
            "filename": self.filename,
            "file_type": self.file_type.value,
            "content_type": self.content_type,
            "tags": self.tags,
            "metadata": self.metadata,
            "searchable_content": self.searchable_content,
            "created_at": self.created_at.isoformat()
        }


class StorageProvider:
    """Base storage provider interface."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def upload_file(
        self, 
        content: bytes, 
        key: str, 
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload file to storage with basic validation and error handling.
        
        Args:
            content: File content as bytes
            key: Storage key/path for the file
            content_type: MIME type of the content
            metadata: Optional metadata to store with the file
            
        Returns:
            str: Storage URL or identifier for the uploaded file
        """
        # Basic implementation for providers that don't override this method
        # Log the operation for development/debugging
        self.logger.info(f"Mock upload: {key} ({len(content)} bytes) of type {content_type}")
        
        # Validate inputs
        if not content:
            raise ValueError("Content cannot be empty")
        if not key:
            raise ValueError("Storage key cannot be empty")
        if not content_type:
            raise ValueError("Content type cannot be empty")
        
        # Check file size against config limits
        if len(content) > self.config.max_file_size:
            raise ValueError(f"File size {len(content)} exceeds maximum {self.config.max_file_size}")
        
        # For base implementation, return a mock URL
        # Real storage providers should override this method
        mock_url = f"mock://{self.config.bucket_name}/{key}"
        
        self.logger.warning(f"Using mock storage URL: {mock_url}. Implement upload_file() in storage provider subclass.")
        return mock_url
        
    async def download_file(self, key: str) -> bytes:
        """
        Download file from storage with error handling.
        
        Args:
            key: Storage key/path for the file
            
        Returns:
            bytes: File content
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock download: {key}")
        
        if not key:
            raise ValueError("Storage key cannot be empty")
        
        # For base implementation, return mock content
        # Real storage providers should override this method
        mock_content = f"Mock file content for key: {key}".encode('utf-8')
        
        self.logger.warning(f"Using mock file content for key: {key}. Implement download_file() in storage provider subclass.")
        return mock_content
        
    async def delete_file(self, key: str) -> bool:
        """
        Delete file from storage with error handling.
        
        Args:
            key: Storage key/path for the file
            
        Returns:
            bool: True if deletion was successful
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock delete: {key}")
        
        if not key:
            raise ValueError("Storage key cannot be empty")
        
        # For base implementation, return success
        # Real storage providers should override this method
        self.logger.warning(f"Mock deletion of key: {key}. Implement delete_file() in storage provider subclass.")
        return True
        
    async def file_exists(self, key: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            key: Storage key/path for the file
            
        Returns:
            bool: True if file exists
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock exists check: {key}")
        
        if not key:
            return False
        
        # For base implementation, return True for demonstration
        # Real storage providers should override this method
        self.logger.warning(f"Mock existence check for key: {key}. Implement file_exists() in storage provider subclass.")
        return True
        
    async def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """
        Get file metadata with basic implementation.
        
        Args:
            key: Storage key/path for the file
            
        Returns:
            Dict[str, Any]: File metadata
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock metadata retrieval: {key}")
        
        if not key:
            raise ValueError("Storage key cannot be empty")
        
        # For base implementation, return mock metadata
        # Real storage providers should override this method
        mock_metadata = {
            "key": key,
            "size": 1024,
            "content_type": "application/octet-stream",
            "created": datetime.utcnow().isoformat(),
            "last_modified": datetime.utcnow().isoformat(),
            "etag": f"mock-etag-{hash(key)}",
            "storage_provider": self.__class__.__name__,
            "note": "Mock metadata - implement get_file_metadata() in storage provider subclass"
        }
        
        self.logger.warning(f"Using mock metadata for key: {key}. Implement get_file_metadata() in storage provider subclass.")
        return mock_metadata
        
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        List files with optional prefix.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List[Dict[str, Any]]: List of file information
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock file listing with prefix: {prefix}")
        
        # For base implementation, return mock file list
        # Real storage providers should override this method
        mock_files = [
            {
                "key": f"{prefix}mock-file-1.txt",
                "size": 1024,
                "last_modified": datetime.utcnow().isoformat(),
                "etag": "mock-etag-1"
            },
            {
                "key": f"{prefix}mock-file-2.jpg",
                "size": 2048,
                "last_modified": datetime.utcnow().isoformat(),
                "etag": "mock-etag-2"
            }
        ]
        
        self.logger.warning(f"Using mock file listing. Implement list_files() in storage provider subclass.")
        return mock_files
        
    async def generate_presigned_url(
        self, 
        key: str, 
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """
        Generate presigned URL with basic implementation.
        
        Args:
            key: Storage key/path for the file
            expiration: URL expiration time in seconds
            method: HTTP method for the URL
            
        Returns:
            str: Presigned URL
        """
        # Basic implementation for providers that don't override this method
        self.logger.info(f"Mock presigned URL generation: {key}")
        
        if not key:
            raise ValueError("Storage key cannot be empty")
        
        # For base implementation, return mock URL with expiration info
        # Real storage providers should override this method
        import time
        expiry_timestamp = int(time.time()) + expiration
        mock_url = f"mock://{self.config.bucket_name}/{key}?expires={expiry_timestamp}&method={method}"
        
        self.logger.warning(f"Using mock presigned URL: {mock_url}. Implement generate_presigned_url() in storage provider subclass.")
        return mock_url


class S3StorageProvider(StorageProvider):
    """AWS S3 and MinIO compatible storage provider."""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        
        if not boto3 or not aioboto3:
            raise StorageException("boto3 and aioboto3 are required for S3 storage")
            
        # Configure S3 client
        self.s3_config = Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'path'
            },
            max_pool_connections=50
        )
        
        # Session for async operations
        self.session = None
        
    async def _get_session(self):
        """Get or create aioboto3 session."""
        if self.session is None:
            self.session = aioboto3.Session()
        return self.session
        
    async def _get_client(self):
        """Get S3 client."""
        session = await self._get_session()
        
        client_kwargs = {
            'service_name': 's3',
            'region_name': self.config.region,
            'config': self.s3_config
        }
        
        # Add credentials if provided
        if self.config.access_key and self.config.secret_key:
            client_kwargs.update({
                'aws_access_key_id': self.config.access_key,
                'aws_secret_access_key': self.config.secret_key
            })
            
        # Add endpoint URL for MinIO
        if self.config.endpoint_url:
            client_kwargs['endpoint_url'] = self.config.endpoint_url
            
        return session.client(**client_kwargs)
        
    async def upload_file(
        self, 
        content: bytes, 
        key: str, 
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to S3/MinIO."""
        try:
            async with await self._get_client() as s3_client:
                # Prepare upload parameters
                upload_params = {
                    'Bucket': self.config.bucket_name,
                    'Key': key,
                    'Body': content,
                    'ContentType': content_type,
                    'StorageClass': StorageClass.STANDARD.value
                }
                
                # Add metadata
                if metadata:
                    # S3 metadata keys must be prefixed with 'x-amz-meta-'
                    s3_metadata = {
                        f"x-amz-meta-{k}": str(v) for k, v in metadata.items()
                    }
                    upload_params['Metadata'] = s3_metadata
                    
                # Enable server-side encryption
                if self.config.use_ssl:
                    upload_params['ServerSideEncryption'] = 'AES256'
                    
                # Upload file
                await s3_client.put_object(**upload_params)
                
                # Generate storage URL
                storage_url = f"{self.config.endpoint_url or 'https://s3.amazonaws.com'}/{self.config.bucket_name}/{key}"
                
                self.logger.info(f"Successfully uploaded file to {storage_url}")
                return storage_url
                
        except Exception as e:
            self.logger.error(f"Failed to upload file {key}: {e}")
            raise StorageException(f"Upload failed: {str(e)}")
            
    async def download_file(self, key: str) -> bytes:
        """Download file from S3/MinIO."""
        try:
            async with await self._get_client() as s3_client:
                response = await s3_client.get_object(
                    Bucket=self.config.bucket_name,
                    Key=key
                )
                
                # Read content
                content = await response['Body'].read()
                
                self.logger.info(f"Successfully downloaded file {key}")
                return content
                
        except Exception as e:
            self.logger.error(f"Failed to download file {key}: {e}")
            raise StorageException(f"Download failed: {str(e)}")
            
    async def delete_file(self, key: str) -> bool:
        """Delete file from S3/MinIO."""
        try:
            async with await self._get_client() as s3_client:
                await s3_client.delete_object(
                    Bucket=self.config.bucket_name,
                    Key=key
                )
                
                self.logger.info(f"Successfully deleted file {key}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete file {key}: {e}")
            return False
            
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in S3/MinIO."""
        try:
            async with await self._get_client() as s3_client:
                await s3_client.head_object(
                    Bucket=self.config.bucket_name,
                    Key=key
                )
                return True
                
        except Exception:
            return False
            
    async def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """Get file metadata from S3/MinIO."""
        try:
            async with await self._get_client() as s3_client:
                response = await s3_client.head_object(
                    Bucket=self.config.bucket_name,
                    Key=key
                )
                
                # Extract metadata
                metadata = {
                    'size': response.get('ContentLength', 0),
                    'content_type': response.get('ContentType', ''),
                    'last_modified': response.get('LastModified'),
                    'etag': response.get('ETag', '').strip('"')
                }
                
                # Extract custom metadata
                s3_metadata = response.get('Metadata', {})
                for k, v in s3_metadata.items():
                    # Remove 'x-amz-meta-' prefix
                    clean_key = k.replace('x-amz-meta-', '') if k.startswith('x-amz-meta-') else k
                    metadata[clean_key] = v
                    
                return metadata
                
        except Exception as e:
            self.logger.error(f"Failed to get metadata for file {key}: {e}")
            raise StorageException(f"Metadata retrieval failed: {str(e)}")
            
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files with optional prefix."""
        try:
            async with await self._get_client() as s3_client:
                paginator = s3_client.get_paginator('list_objects_v2')
                
                page_iterator = paginator.paginate(
                    Bucket=self.config.bucket_name,
                    Prefix=prefix
                )
                
                files = []
                async for page in page_iterator:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            files.append({
                                'key': obj['Key'],
                                'size': obj['Size'],
                                'last_modified': obj['LastModified'],
                                'etag': obj['ETag'].strip('"')
                            })
                            
                return files
                
        except Exception as e:
            self.logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise StorageException(f"File listing failed: {str(e)}")
            
    async def generate_presigned_url(
        self, 
        key: str, 
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """Generate presigned URL for file access."""
        try:
            async with await self._get_client() as s3_client:
                url = await s3_client.generate_presigned_url(
                    ClientMethod='get_object' if method == 'GET' else 'put_object',
                    Params={
                        'Bucket': self.config.bucket_name,
                        'Key': key
                    },
                    ExpiresIn=expiration
                )
                
                return url
                
        except Exception as e:
            self.logger.error(f"Failed to generate presigned URL for {key}: {e}")
            raise StorageException(f"Presigned URL generation failed: {str(e)}")


class LocalStorageProvider(StorageProvider):
    """Local file system storage provider."""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.bucket_name)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    async def upload_file(
        self, 
        content: bytes, 
        key: str, 
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to local storage."""
        try:
            file_path = self.base_path / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
                
            # Write metadata
            if metadata:
                metadata_path = file_path.with_suffix(file_path.suffix + '.metadata.json')
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
                    
            storage_url = f"file://{file_path.absolute()}"
            self.logger.info(f"Successfully uploaded file to {storage_url}")
            return storage_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload file {key}: {e}")
            raise StorageException(f"Upload failed: {str(e)}")
            
    async def download_file(self, key: str) -> bytes:
        """Download file from local storage."""
        try:
            file_path = self.base_path / key
            
            if not file_path.exists():
                raise StorageException(f"File not found: {key}")
                
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                
            self.logger.info(f"Successfully downloaded file {key}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to download file {key}: {e}")
            raise StorageException(f"Download failed: {str(e)}")
            
    async def delete_file(self, key: str) -> bool:
        """Delete file from local storage."""
        try:
            file_path = self.base_path / key
            
            if file_path.exists():
                file_path.unlink()
                
                # Delete metadata file if exists
                metadata_path = file_path.with_suffix(file_path.suffix + '.metadata.json')
                if metadata_path.exists():
                    metadata_path.unlink()
                    
                self.logger.info(f"Successfully deleted file {key}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {key}: {e}")
            return False
            
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in local storage."""
        file_path = self.base_path / key
        return file_path.exists()
        
    async def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """Get file metadata from local storage."""
        try:
            file_path = self.base_path / key
            
            if not file_path.exists():
                raise StorageException(f"File not found: {key}")
                
            # Basic file stats
            stat = file_path.stat()
            metadata = {
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime)
            }
            
            # Load custom metadata
            metadata_path = file_path.with_suffix(file_path.suffix + '.metadata.json')
            if metadata_path.exists():
                async with aiofiles.open(metadata_path, 'r') as f:
                    custom_metadata = json.loads(await f.read())
                    metadata.update(custom_metadata)
                    
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata for file {key}: {e}")
            raise StorageException(f"Metadata retrieval failed: {str(e)}")
            
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files with optional prefix."""
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path
            
            if search_path.is_dir():
                for file_path in search_path.rglob('*'):
                    if file_path.is_file() and not file_path.name.endswith('.metadata.json'):
                        relative_key = str(file_path.relative_to(self.base_path))
                        stat = file_path.stat()
                        
                        files.append({
                            'key': relative_key,
                            'size': stat.st_size,
                            'last_modified': datetime.fromtimestamp(stat.st_mtime)
                        })
                        
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise StorageException(f"File listing failed: {str(e)}")
            
    async def generate_presigned_url(
        self, 
        key: str, 
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """Generate file URL (local files don't need presigning)."""
        file_path = self.base_path / key
        return f"file://{file_path.absolute()}"


class IndexManager:
    """File index manager for search and metadata."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.indices: Dict[str, FileIndex] = {}
        
    async def add_file_index(self, file_index: FileIndex):
        """Add file to index."""
        self.indices[file_index.file_id] = file_index
        self.logger.info(f"Added file index for {file_index.file_id}")
        
    async def remove_file_index(self, file_id: str) -> bool:
        """Remove file from index."""
        if file_id in self.indices:
            del self.indices[file_id]
            self.logger.info(f"Removed file index for {file_id}")
            return True
        return False
        
    async def search_files(
        self,
        query: str,
        file_types: Optional[List[FileType]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[FileIndex]:
        """Search files by query, type, and tags."""
        results = []
        
        for index in self.indices.values():
            # Filter by file type
            if file_types and index.file_type not in file_types:
                continue
                
            # Filter by tags
            if tags and not any(tag in index.tags for tag in tags):
                continue
                
            # Text search in filename and searchable content
            if query.lower() in index.filename.lower() or query.lower() in index.searchable_content.lower():
                results.append(index)
                
            if len(results) >= limit:
                break
                
        return results
        
    async def get_file_index(self, file_id: str) -> Optional[FileIndex]:
        """Get file index by ID."""
        return self.indices.get(file_id)
        
    async def update_file_index(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """Update file index."""
        if file_id in self.indices:
            index = self.indices[file_id]
            for key, value in updates.items():
                if hasattr(index, key):
                    setattr(index, key, value)
            return True
        return False
        
    async def get_index_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        stats = {
            "total_files": len(self.indices),
            "files_by_type": {},
            "total_size": 0
        }
        
        for index in self.indices.values():
            # Count by file type
            type_name = index.file_type.value
            stats["files_by_type"][type_name] = stats["files_by_type"].get(type_name, 0) + 1
            
        return stats


class EnterpriseStorageService:
    """Enterprise storage service with multi-backend support."""
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage provider
        self.provider = self._create_provider()
        
        # Initialize index manager
        self.index_manager = IndexManager()
        
        # File processing capabilities
        self._initialize_processors()
        
    def _get_default_config(self) -> StorageConfig:
        """Get default storage configuration."""
        settings = get_settings()
        
        # Determine storage type from settings
        storage_type = StorageType.LOCAL_FILE
        if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
            storage_type = StorageType.AWS_S3
        elif hasattr(settings, 'MINIO_ENDPOINT') and settings.MINIO_ENDPOINT:
            storage_type = StorageType.MINIO
            
        return StorageConfig(
            storage_type=storage_type,
            endpoint_url=getattr(settings, 'MINIO_ENDPOINT', None),
            access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None) or getattr(settings, 'MINIO_ACCESS_KEY', None),
            secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) or getattr(settings, 'MINIO_SECRET_KEY', None),
            bucket_name=getattr(settings, 'STORAGE_BUCKET', 'ia-influencer-content'),
            region=getattr(settings, 'AWS_REGION', 'us-east-1')
        )
        
    def _create_provider(self) -> StorageProvider:
        """Create storage provider based on configuration."""
        if self.config.storage_type in [StorageType.AWS_S3, StorageType.MINIO]:
            return S3StorageProvider(self.config)
        else:
            return LocalStorageProvider(self.config)
            
    def _initialize_processors(self):
        """Initialize file processors."""
        self.processors = {
            FileType.IMAGE: self._process_image,
            FileType.VIDEO: self._process_video,
            FileType.AUDIO: self._process_audio,
            FileType.TEXT: self._process_text
        }
        
    def _detect_file_type(self, filename: str, content_type: str) -> FileType:
        """Detect file type from filename and content type."""
        extension = Path(filename).suffix.lower()
        
        # Audio files
        if extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg'] or content_type.startswith('audio/'):
            return FileType.AUDIO
            
        # Video files
        if extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm'] or content_type.startswith('video/'):
            return FileType.VIDEO
            
        # Image files
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff'] or content_type.startswith('image/'):
            return FileType.IMAGE
            
        # Text files
        if extension in ['.txt', '.md', '.html', '.json', '.xml'] or content_type.startswith('text/'):
            return FileType.TEXT
            
        # Documents
        if extension in ['.pdf', '.doc', '.docx']:
            return FileType.DOCUMENT
            
        # Default to document
        return FileType.DOCUMENT
        
    async def _process_image(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process image file to extract metadata and create thumbnails."""
        metadata = {"type": "image"}
        
        if Image:
            try:
                with tempfile.NamedTemporaryFile() as tmp_file:
                    tmp_file.write(content)
                    tmp_file.flush()
                    
                    with Image.open(tmp_file.name) as img:
                        metadata.update({
                            "width": img.width,
                            "height": img.height,
                            "format": img.format,
                            "mode": img.mode
                        })
                        
                        # Create thumbnail
                        thumbnail = img.copy()
                        thumbnail.thumbnail((200, 200))
                        
                        # Save thumbnail to bytes
                        with tempfile.NamedTemporaryFile(suffix='.jpg') as thumb_file:
                            thumbnail.save(thumb_file.name, 'JPEG', quality=85)
                            thumb_file.seek(0)
                            thumbnail_content = thumb_file.read()
                            
                            # Store thumbnail
                            thumbnail_key = f"thumbnails/{Path(filename).stem}_thumb.jpg"
                            await self.provider.upload_file(
                                thumbnail_content,
                                thumbnail_key,
                                "image/jpeg"
                            )
                            
                            metadata["thumbnail_url"] = thumbnail_key
                            
            except Exception as e:
                self.logger.error(f"Failed to process image {filename}: {e}")
                
        return metadata
        
    async def _process_video(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process video file to extract metadata and create thumbnails."""
        metadata = {"type": "video"}
        
        if cv2:
            try:
                with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix) as tmp_file:
                    tmp_file.write(content)
                    tmp_file.flush()
                    
                    # Open video
                    cap = cv2.VideoCapture(tmp_file.name)
                    
                    if cap.isOpened():
                        # Get video properties
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        duration = frame_count / fps if fps > 0 else 0
                        
                        metadata.update({
                            "width": width,
                            "height": height,
                            "fps": fps,
                            "frame_count": frame_count,
                            "duration": duration
                        })
                        
                        # Extract thumbnail from middle frame
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
                        ret, frame = cap.read()
                        
                        if ret:
                            # Convert to JPEG
                            _, buffer = cv2.imencode('.jpg', frame)
                            thumbnail_content = buffer.tobytes()
                            
                            # Store thumbnail
                            thumbnail_key = f"thumbnails/{Path(filename).stem}_thumb.jpg"
                            await self.provider.upload_file(
                                thumbnail_content,
                                thumbnail_key,
                                "image/jpeg"
                            )
                            
                            metadata["thumbnail_url"] = thumbnail_key
                            
                    cap.release()
                    
            except Exception as e:
                self.logger.error(f"Failed to process video {filename}: {e}")
                
        return metadata
        
    async def _process_audio(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process audio file to extract metadata and create waveforms."""
        metadata = {"type": "audio"}
        
        if librosa and plt and io:
            try:
                with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix) as tmp_file:
                    tmp_file.write(content)
                    tmp_file.flush()
                    
                    # Load audio
                    y, sr = librosa.load(tmp_file.name)
                    
                    # Extract metadata
                    duration = librosa.get_duration(y=y, sr=sr)
                    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                    
                    metadata.update({
                        "duration": duration,
                        "sample_rate": sr,
                        "tempo": float(tempo),
                        "channels": 1 if y.ndim == 1 else y.shape[1]
                    })
                    
                    # Create waveform visualization
                    plt.figure(figsize=(12, 4))
                    librosa.display.waveshow(y, sr=sr)
                    plt.title(f'Waveform - {filename}')
                    
                    # Save to bytes
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    waveform_content = img_buffer.getvalue()
                    
                    # Store waveform
                    waveform_key = f"waveforms/{Path(filename).stem}_waveform.png"
                    await self.provider.upload_file(
                        waveform_content,
                        waveform_key,
                        "image/png"
                    )
                    
                    metadata["waveform_url"] = waveform_key
                    
            except Exception as e:
                self.logger.error(f"Failed to process audio {filename}: {e}")
                
        return metadata
        
    async def _process_text(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process text file to extract metadata."""
        metadata = {"type": "text"}
        
        try:
            # Decode text content
            text_content = content.decode('utf-8')
            
            metadata.update({
                "character_count": len(text_content),
                "word_count": len(text_content.split()),
                "line_count": len(text_content.splitlines())
            })
            
            # Extract searchable content (first 1000 characters)
            metadata["searchable_content"] = text_content[:1000]
            
        except Exception as e:
            self.logger.error(f"Failed to process text file {filename}: {e}")
            
        return metadata
        
    def _generate_file_key(self, filename: str, file_type: FileType, user_id: Optional[str] = None) -> str:
        """Generate storage key for file."""
        # Create timestamp-based directory structure
        now = datetime.utcnow()
        date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        # Add user ID if provided
        if user_id:
            date_path = f"users/{user_id}/{date_path}"
            
        # Add file type directory
        type_path = f"{file_type.value}s"
        
        # Generate unique filename
        file_hash = hashlib.md5(f"{filename}{now.isoformat()}".encode()).hexdigest()[:8]
        name, ext = Path(filename).stem, Path(filename).suffix
        unique_filename = f"{name}_{file_hash}{ext}"
        
        return f"{date_path}/{type_path}/{unique_filename}"
        
    async def store_file(
        self,
        content: bytes,
        filename: str,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> StoredFile:
        """Store file with automatic processing and indexing."""
        try:
            # Validate file size
            if len(content) > self.config.max_file_size:
                raise StorageException(f"File size {len(content)} exceeds maximum {self.config.max_file_size}")
                
            # Validate file extension
            extension = Path(filename).suffix.lower()
            if extension not in self.config.allowed_extensions:
                raise StorageException(f"File extension {extension} not allowed")
                
            # Detect content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                content_type = content_type or 'application/octet-stream'
                
            # Detect file type
            file_type = self._detect_file_type(filename, content_type)
            
            # Generate storage key
            storage_key = self._generate_file_key(filename, file_type, user_id)
            
            # Calculate checksum
            checksum = hashlib.sha256(content).hexdigest()
            
            # Process file to extract metadata
            processing_metadata = await self.processors.get(file_type, lambda c, f: {})(content, filename)
            
            # Combine metadata
            combined_metadata = {
                **(metadata or {}),
                **processing_metadata,
                "original_filename": filename,
                "checksum": checksum,
                "file_type": file_type.value,
                "user_id": user_id,
                "tags": tags or []
            }
            
            # Upload file to storage
            storage_url = await self.provider.upload_file(
                content,
                storage_key,
                content_type,
                combined_metadata
            )
            
            # Create stored file record
            file_id = str(hashlib.md5(storage_key.encode()).hexdigest())
            stored_file = StoredFile(
                file_id=file_id,
                original_filename=filename,
                stored_key=storage_key,
                file_type=file_type,
                content_type=content_type,
                size=len(content),
                checksum=checksum,
                storage_url=storage_url,
                metadata=combined_metadata
            )
            
            # Add to index
            file_index = FileIndex(
                index_id=file_id,
                file_id=file_id,
                filename=filename,
                file_type=file_type,
                content_type=content_type,
                tags=tags or [],
                metadata=combined_metadata,
                searchable_content=combined_metadata.get("searchable_content", filename)
            )
            
            await self.index_manager.add_file_index(file_index)
            
            self.logger.info(f"Successfully stored file {filename} as {storage_key}")
            return stored_file
            
        except Exception as e:
            self.logger.error(f"Failed to store file {filename}: {e}")
            raise StorageException(f"File storage failed: {str(e)}")
            
    async def retrieve_file(self, file_id: str) -> Tuple[bytes, StoredFile]:
        """Retrieve file by ID."""
        try:
            # Get file index
            file_index = await self.index_manager.get_file_index(file_id)
            if not file_index:
                raise StorageException(f"File not found: {file_id}")
                
            # Get storage key from metadata
            storage_key = file_index.metadata.get("stored_key")
            if not storage_key:
                raise StorageException(f"Storage key not found for file {file_id}")
                
            # Download file content
            content = await self.provider.download_file(storage_key)
            
            # Create StoredFile record
            stored_file = StoredFile(
                file_id=file_id,
                original_filename=file_index.filename,
                stored_key=storage_key,
                file_type=file_index.file_type,
                content_type=file_index.content_type,
                size=len(content),
                checksum=file_index.metadata.get("checksum", ""),
                storage_url=f"{self.config.endpoint_url}/{self.config.bucket_name}/{storage_key}",
                metadata=file_index.metadata
            )
            
            self.logger.info(f"Successfully retrieved file {file_id}")
            return content, stored_file
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve file {file_id}: {e}")
            raise StorageException(f"File retrieval failed: {str(e)}")
            
    async def delete_file(self, file_id: str) -> bool:
        """Delete file by ID."""
        try:
            # Get file index
            file_index = await self.index_manager.get_file_index(file_id)
            if not file_index:
                return False
                
            # Get storage key
            storage_key = file_index.metadata.get("stored_key")
            if storage_key:
                # Delete from storage
                await self.provider.delete_file(storage_key)
                
                # Delete associated files (thumbnails, waveforms)
                for meta_key, meta_value in file_index.metadata.items():
                    if meta_key.endswith('_url') and isinstance(meta_value, str):
                        try:
                            await self.provider.delete_file(meta_value)
                        except Exception:
                            pass  # Continue if associated file deletion fails
                            
            # Remove from index
            await self.index_manager.remove_file_index(file_id)
            
            self.logger.info(f"Successfully deleted file {file_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_id}: {e}")
            return False
            
    async def search_files(
        self,
        query: str,
        file_types: Optional[List[FileType]] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[FileIndex]:
        """Search files with filters."""
        results = await self.index_manager.search_files(query, file_types, tags, limit)
        
        # Filter by user_id if provided
        if user_id:
            results = [r for r in results if r.metadata.get("user_id") == user_id]
            
        return results
        
    async def generate_download_url(
        self, 
        file_id: str, 
        expiration: int = 3600
    ) -> str:
        """Generate temporary download URL for file."""
        try:
            file_index = await self.index_manager.get_file_index(file_id)
            if not file_index:
                raise StorageException(f"File not found: {file_id}")
                
            storage_key = file_index.metadata.get("stored_key")
            if not storage_key:
                raise StorageException(f"Storage key not found for file {file_id}")
                
            return await self.provider.generate_presigned_url(
                storage_key,
                expiration,
                "GET"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate download URL for {file_id}: {e}")
            raise StorageException(f"URL generation failed: {str(e)}")
            
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            # Get index statistics
            index_stats = await self.index_manager.get_index_statistics()
            
            # Get provider-specific statistics
            provider_stats = {}
            if hasattr(self.provider, 'get_statistics'):
                provider_stats = await self.provider.get_statistics()
                
            return {
                **index_stats,
                **provider_stats,
                "storage_type": self.config.storage_type.value,
                "bucket_name": self.config.bucket_name,
                "max_file_size": self.config.max_file_size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage statistics: {e}")
            return {}


# Global service instance
_storage_service = None

def get_storage_service() -> EnterpriseStorageService:
    """Get global storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = EnterpriseStorageService()
    return _storage_service
