"""Content Storage Module - Professional Storage Backend Management System

Module de gestion des backends de stockage pour le contenu multimédia
dans la plateforme IA Influencer Agent avec support multi-cloud.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Storage Architect, Cloud Infrastructure Expert, Performance Optimization Specialist
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from enum import Enum
import logging
import hashlib
import asyncio
import aiofiles
import aiohttp
import json
from abc import ABC, abstractmethod
import mimetypes
import shutil
from urllib.parse import urlparse, urljoin
import uuid
import tempfile
import os

# Cloud storage imports (would be conditional based on availability)
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from google.cloud import storage as gcs
    from google.api_core import exceptions as gcs_exceptions
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

logger = logging.getLogger(__name__)

class StorageBackendType(Enum):
    """
Supported storage backend types"""

    LOCAL_FILESYSTEM = "local_filesystem"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    FTP_SERVER = "ftp_server"
    SFTP_SERVER = "sftp_server"
    WEBDAV = "webdav"
    NETWORK_SHARE = "network_share"
    DISTRIBUTED_FS = "distributed_fs"

class StorageAccessMode(Enum):
    """Storage access modes"""

    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"
    APPEND_ONLY = "append_only"

class StorageRedundancyLevel(Enum):
    """Storage redundancy and durability levels"""

    NONE = "none"
    LOCAL_REDUNDANT = "local_redundant"
    ZONE_REDUNDANT = "zone_redundant"
    GEO_REDUNDANT = "geo_redundant"
    READ_ACCESS_GEO = "read_access_geo"

class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""

    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    BROTLI = "brotli"
    ZSTD = "zstd"

class EncryptionType(Enum):
    """Supported encryption types"""

    NONE = "none"
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    SERVER_SIDE = "server_side"
    CLIENT_SIDE = "client_side"

@dataclass
class StorageConfiguration:
    """Storage backend configuration"""
    backend_type: StorageBackendType
    name: str
    endpoint_url: Optional[str] = None
    region: Optional[str] = None
    bucket_name: Optional[str] = None
    container_name: Optional[str] = None
    base_path: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    credentials_file: Optional[str] = None
    access_mode: StorageAccessMode = StorageAccessMode.READ_WRITE
    redundancy_level: StorageRedundancyLevel = StorageRedundancyLevel.LOCAL_REDUNDANT
    compression: CompressionAlgorithm = CompressionAlgorithm.NONE
    encryption: EncryptionType = EncryptionType.NONE
    max_file_size_gb: float = 10.0
    max_bandwidth_mbps: Optional[float] = None
    connection_timeout: int = 30
    retry_attempts: int = 3
    enable_versioning: bool = False
    enable_lifecycle_management: bool = False
    lifecycle_rules: Optional[Dict[str, Any]] = None
    custom_metadata: Optional[Dict[str, str]] = None
    tags: Optional[Dict[str, str]] = None

@dataclass
class StorageMetrics:
    """
Storage backend metrics and statistics"""
    total_files: int = 0
    total_size_bytes: int = 0
    available_space_bytes: Optional[int] = None
    used_space_bytes: Optional[int] = None
    read_operations: int = 0
    write_operations: int = 0
    delete_operations: int = 0
    error_count: int = 0
    average_response_time_ms: float = 0.0
    bandwidth_utilization_mbps: float = 0.0
    last_health_check: Optional[datetime] = None
    uptime_percentage: float = 100.0
    cost_current_month: float = 0.0
    performance_score: float = 1.0

@dataclass
class StorageOperation:
    """
Storage operation metadata"""
    operation_id: str
    operation_type: str  # upload, download, delete, copy, move
    file_path: str
    backend_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    transfer_speed_mbps: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

class StorageBackend(ABC):
    """
Abstract base class for storage backends"""
    
    def __init__(self, config: StorageConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = StorageMetrics()
        self._client = None
        self._is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        try:
            logger.info(f"Executing connect")
            
            # Implementation for connect
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing disconnect")
            
            # Implementation for disconnect
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"disconnect completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing upload_file")
            
            # Implementation for upload_file
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing download_file")
            
            # Implementation for download_file
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"download_file completed successfully")
            return result
            
        except Exception as e:
        try:
                    async with self.db_session() as session:
                        # Database operation
                        result = await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"Database operation delete_file completed")
                        return True
                
                except Exception as e:
        try:
            logger.info(f"Executing list_files")
            
            # Implementation for list_files
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing file_exists")
            
            # Implementation for file_exists
            # TODO: Add specific business logic here
        try:
                    # Request validation
                    if not remote_path:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_file_metadata_request(remote_path)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
            logger.info(f"Executing health_check")
            
            # Implementation for health_check
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"health_check completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"health_check failed: {e}")
            raise
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_file_metadata failed: {e}")
                    return {"status": "error", "message": str(e)}
            logger.info(f"file_exists completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"file_exists failed: {e}")
            raise
            logger.info(f"list_files completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"list_files failed: {e}")
            raise
                    raise
            raise
            logger.error(f"upload_file failed: {e}")
            raise
            logger.info(f"connect completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"connect failed: {e}")
            raise
    @abstractmethod
    async def disconnect(self):
        """
Disconnect from the storage backend"""
        pass
    
    @abstractmethod
    async def upload_file(
        self, 
        local_path: Union[str, Path], 
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> StorageOperation:
        """
Upload a file to the storage backend"""
        pass
    
    @abstractmethod
    async def download_file(
        self, 
        remote_path: str, 
        local_path: Union[str, Path]
    ) -> StorageOperation:
        """
Download a file from the storage backend"""
        pass
    
    @abstractmethod
    async def delete_file(self, remote_path: str) -> StorageOperation:
        """
Delete a file from the storage backend"""
        pass
    
    @abstractmethod
    async def list_files(
        self, 
        path_prefix: str = "", 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List files in the storage backend"""
        pass
    
    @abstractmethod
    async def file_exists(self, remote_path: str) -> bool:
        """
Check if a file exists in the storage backend"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, remote_path: str) -> Dict[str, Any]:
        """
Get metadata for a file"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
Perform health check on the storage backend"""
        pass
    
    async def copy_file(
        self, 
        source_path: str, 
        destination_path: str
    ) -> StorageOperation:
        """
Copy a file within the storage backend"""
        # Default implementation using download/upload
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="copy",
            file_path=f"{source_path} -> {destination_path}",
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            # Create temporary file for intermediate storage
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Download source to temporary location
                await self.download_file(source_path, temp_path)
                
                # Upload to destination
                await self.upload_file(temp_path, destination_path)
                
                operation.completed_at = datetime.now(timezone.utc)
                return operation
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            raise
    
    def get_metrics(self) -> StorageMetrics:
        """Get current storage metrics"""
        return self.metrics
    
    def update_metrics(self, operation: StorageOperation):
        """
Update metrics based on completed operation"""
        if operation.operation_type == "upload":
            self.metrics.write_operations += 1
        elif operation.operation_type == "download":
            self.metrics.read_operations += 1
        elif operation.operation_type == "delete":
            self.metrics.delete_operations += 1
        
        if operation.error_message:
            self.metrics.error_count += 1
        
        if operation.transfer_speed_mbps:
            # Update average response time (simplified)
            self.metrics.average_response_time_ms = (
                (self.metrics.average_response_time_ms + 
                 (1000 / operation.transfer_speed_mbps)) / 2
            )

class LocalFilesystemBackend(StorageBackend):
    """Local filesystem storage backend"""
    
    async def connect(self) -> bool:
        """
Connect to local filesystem"""
        try:
            self.base_path = Path(self.config.base_path or "/tmp/content_storage")
            self.base_path.mkdir(parents=True, exist_ok=True)
            self._is_connected = True
            self.logger.info(f"Connected to local filesystem: {self.base_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to local filesystem: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from local filesystem"""
        self._is_connected = False
        self.logger.info("Disconnected from local filesystem")
    
    async def upload_file(
        self, 
        local_path: Union[str, Path], 
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> StorageOperation:
        """Upload file to local filesystem"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="upload",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            source_path = Path(local_path)
            target_path = self.base_path / remote_path.lstrip('/')
            
            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            operation.file_size_bytes = target_path.stat().st_size
            operation.completed_at = datetime.now(timezone.utc)
            
            # Store metadata if provided
            if metadata:
                metadata_path = target_path.with_suffix(target_path.suffix + '.metadata')
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata))
            
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def download_file(
        self, 
        remote_path: str, 
        local_path: Union[str, Path]
    ) -> StorageOperation:
        """Download file from local filesystem"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="download",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            source_path = self.base_path / remote_path.lstrip('/')
            target_path = Path(local_path)
            
            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            operation.file_size_bytes = source_path.stat().st_size
            operation.completed_at = datetime.now(timezone.utc)
            
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def delete_file(self, remote_path: str) -> StorageOperation:
        """Delete file from local filesystem"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="delete",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            file_path = self.base_path / remote_path.lstrip('/')
            
            if file_path.exists():
                file_path.unlink()
                
                # Also remove metadata file if it exists
                metadata_path = file_path.with_suffix(file_path.suffix + '.metadata')
                if metadata_path.exists():
                    metadata_path.unlink()
            
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def list_files(
        self, 
        path_prefix: str = "", 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List files in local filesystem"""
        try:
            search_path = self.base_path / path_prefix.lstrip('/')
            files = []
            
            if search_path.exists():
                for file_path in search_path.rglob('*'):
                    if file_path.is_file() and not file_path.name.endswith('.metadata'):
                        relative_path = file_path.relative_to(self.base_path)
                        stat = file_path.stat()
                        
                        files.append({
                            'path': str(relative_path),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                            'type': mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
                        })
                        
                        if limit and len(files) >= limit:
                            break
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    async def file_exists(self, remote_path: str) -> bool:
        """Check if file exists in local filesystem"""
        try:
            file_path = self.base_path / remote_path.lstrip('/')
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
    
    async def get_file_metadata(self, remote_path: str) -> Dict[str, Any]:
        """
Get file metadata from local filesystem"""
        try:
            file_path = self.base_path / remote_path.lstrip('/')
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {remote_path}")
            
            stat = file_path.stat()
            metadata = {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime, timezone.utc),
                'modified': datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                'type': mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
            }
            
            # Load custom metadata if exists
            metadata_path = file_path.with_suffix(file_path.suffix + '.metadata')
            if metadata_path.exists():
                async with aiofiles.open(metadata_path, 'r') as f:
                    custom_metadata = json.loads(await f.read())
                    metadata.update(custom_metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get file metadata: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on local filesystem"""
        try:
            # Check if base path is accessible
            if not self.base_path.exists():
                return {
                    'status': 'unhealthy',
                    'error': 'Base path does not exist'
                }
            
            # Check disk space
            stat = shutil.disk_usage(self.base_path)
            
            # Test write capability
            test_file = self.base_path / '.health_check'
            test_file.write_text('health_check')
            test_file.unlink()
            
            self.metrics.last_health_check = datetime.now(timezone.utc)
            
            return {
                'status': 'healthy',
                'total_space': stat.total,
                'used_space': stat.used,
                'free_space': stat.free,
                'base_path': str(self.base_path)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

class AWSS3Backend(StorageBackend):
    """
AWS S3 storage backend"""
    
    def __init__(self, config: StorageConfiguration):
        super().__init__(config)
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for AWS S3 backend")
    
    async def connect(self) -> bool:
        """Connect to AWS S3"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            
            self._client = session.client(
                's3',
                endpoint_url=self.config.endpoint_url
            )
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.head_bucket, Bucket=self.config.bucket_name
            )
            
            self._is_connected = True
            self.logger.info(f"Connected to AWS S3 bucket: {self.config.bucket_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to AWS S3: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from AWS S3"""
        self._client = None
        self._is_connected = False
        self.logger.info("Disconnected from AWS S3")
    
    async def upload_file(
        self, 
        local_path: Union[str, Path], 
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> StorageOperation:
        """Upload file to AWS S3"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="upload",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            key = f"{self.config.base_path or ''}/{remote_path}".strip('/')
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Detect content type
            content_type = mimetypes.guess_type(str(local_path))[0]
            if content_type:
                extra_args['ContentType'] = content_type
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._client.upload_file,
                str(local_path),
                self.config.bucket_name,
                key,
                extra_args
            )
            
            operation.file_size_bytes = Path(local_path).stat().st_size
            operation.completed_at = datetime.now(timezone.utc)
            
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def download_file(
        self, 
        remote_path: str, 
        local_path: Union[str, Path]
    ) -> StorageOperation:
        """Download file from AWS S3"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="download",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            key = f"{self.config.base_path or ''}/{remote_path}".strip('/')
            
            # Create parent directories
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._client.download_file,
                self.config.bucket_name,
                key,
                str(local_path)
            )
            
            operation.file_size_bytes = Path(local_path).stat().st_size
            operation.completed_at = datetime.now(timezone.utc)
            
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def delete_file(self, remote_path: str) -> StorageOperation:
        """Delete file from AWS S3"""
        operation = StorageOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="delete",
            file_path=remote_path,
            backend_name=self.config.name,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            key = f"{self.config.base_path or ''}/{remote_path}".strip('/')
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._client.delete_object,
                Bucket=self.config.bucket_name,
                Key=key
            )
            
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            return operation
            
        except Exception as e:
            operation.error_message = str(e)
            operation.completed_at = datetime.now(timezone.utc)
            self.update_metrics(operation)
            raise
    
    async def list_files(
        self, 
        path_prefix: str = "", 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List files in AWS S3"""
        try:
            prefix = f"{self.config.base_path or ''}/{path_prefix}".strip('/')
            
            kwargs = {
                'Bucket': self.config.bucket_name,
                'Prefix': prefix
            }
            
            if limit:
                kwargs['MaxKeys'] = limit
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.list_objects_v2, **kwargs
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'path': obj['Key'].replace(prefix, '').lstrip('/'),
                    'size': obj['Size'],
                    'modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list S3 files: {e}")
            return []
    
    async def file_exists(self, remote_path: str) -> bool:
        """Check if file exists in AWS S3"""
        try:
            key = f"{self.config.base_path or ''}/{remote_path}".strip('/')
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._client.head_object,
                Bucket=self.config.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    async def get_file_metadata(self, remote_path: str) -> Dict[str, Any]:
        """Get file metadata from AWS S3"""
        try:
            key = f"{self.config.base_path or ''}/{remote_path}".strip('/')
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self._client.head_object,
                Bucket=self.config.bucket_name,
                Key=key
            )
            
            return {
                'size': response['ContentLength'],
                'modified': response['LastModified'],
                'etag': response['ETag'].strip('"'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get S3 file metadata: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on AWS S3"""
        try:
            # Test bucket access
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.head_bucket, Bucket=self.config.bucket_name
            )
            
            self.metrics.last_health_check = datetime.now(timezone.utc)
            
            return {
                'status': 'healthy',
                'bucket': self.config.bucket_name,
                'region': self.config.region
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

class StorageManager:
    """
Main storage manager for handling multiple storage backends"""
    
    def __init__(self, configurations: List[StorageConfiguration]):
        """
        Initialize storage manager with multiple backends
        
        Args:
            configurations: List of storage backend configurations
        """
        self.logger = logging.getLogger(f"{__name__}.StorageManager")
        self.backends: Dict[str, StorageBackend] = {}
        self.primary_backend: Optional[str] = None
        self.load_balancing_strategy = "round_robin"
        self._current_backend_index = 0
        
        # Initialize backends
        for config in configurations:
            self._create_backend(config)
    
    def _create_backend(self, config: StorageConfiguration):
        """Create a storage backend based on configuration"""
        try:
            if config.backend_type == StorageBackendType.LOCAL_FILESYSTEM:
                backend = LocalFilesystemBackend(config)
            elif config.backend_type == StorageBackendType.AWS_S3:
                backend = AWSS3Backend(config)
            else:
                raise ValueError(f"Unsupported backend type: {config.backend_type}")
            
            self.backends[config.name] = backend
            
            # Set first backend as primary if not set
            if self.primary_backend is None:
                self.primary_backend = config.name
                
            self.logger.info(f"Created storage backend: {config.name} ({config.backend_type})")
            
        except Exception as e:
            self.logger.error(f"Failed to create backend {config.name}: {e}")
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all storage backends"""
        results = {}
        
        for name, backend in self.backends.items():
            try:
                results[name] = await backend.connect()
            except Exception as e:
                self.logger.error(f"Failed to connect to backend {name}: {e}")
                results[name] = False
        
        return results
    
    async def disconnect_all(self):
        """Disconnect from all storage backends"""
        for name, backend in self.backends.items():
            try:
                await backend.disconnect()
            except Exception as e:
                self.logger.error(f"Failed to disconnect from backend {name}: {e}")
    
    def get_backend(self, name: Optional[str] = None) -> StorageBackend:
        """Get a specific backend or use load balancing"""
        if name:
            if name not in self.backends:
                raise ValueError(f"Backend not found: {name}")
            return self.backends[name]
        
        # Use load balancing strategy
        if self.load_balancing_strategy == "round_robin":
            backend_names = list(self.backends.keys())
            if not backend_names:
                raise ValueError("No backends available")
            
            backend_name = backend_names[self._current_backend_index % len(backend_names)]
            self._current_backend_index += 1
            return self.backends[backend_name]
        
        # Fallback to primary backend
        if self.primary_backend:
            return self.backends[self.primary_backend]
        
        raise ValueError("No backends available")
    
    async def upload_with_redundancy(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        redundancy_level: int = 2,
        metadata: Optional[Dict[str, str]] = None
    ) -> List[StorageOperation]:
        """Upload file to multiple backends for redundancy"""
        operations = []
        backend_names = list(self.backends.keys())
        
        # Limit redundancy to available backends
        redundancy_level = min(redundancy_level, len(backend_names))
        
        for i in range(redundancy_level):
            backend = self.backends[backend_names[i]]
            try:
                operation = await backend.upload_file(local_path, remote_path, metadata)
                operations.append(operation)
            except Exception as e:
                self.logger.error(f"Failed to upload to backend {backend_names[i]}: {e}")
        
        return operations
    
    async def download_with_fallback(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        preferred_backend: Optional[str] = None
    ) -> StorageOperation:
        """Download file with fallback to other backends"""
        # Try preferred backend first
        if preferred_backend and preferred_backend in self.backends:
            try:
                return await self.backends[preferred_backend].download_file(remote_path, local_path)
            except Exception as e:
                self.logger.warning(f"Failed to download from preferred backend {preferred_backend}: {e}")
        
        # Try all backends
        for name, backend in self.backends.items():
            if name == preferred_backend:
                continue  # Already tried
            
            try:
                return await backend.download_file(remote_path, local_path)
            except Exception as e:
                self.logger.warning(f"Failed to download from backend {name}: {e}")
        
        raise Exception("Failed to download from any backend")
    
    async def sync_between_backends(
        self,
        source_backend: str,
        target_backend: str,
        path_prefix: str = ""
    ) -> Dict[str, Any]:
        """Synchronize files between two backends"""
        if source_backend not in self.backends or target_backend not in self.backends:
            raise ValueError("Invalid backend names")
        
        source = self.backends[source_backend]
        target = self.backends[target_backend]
        
        sync_stats = {
            "files_checked": 0,
            "files_copied": 0,
            "files_skipped": 0,
            "errors": []
        }
        
        try:
            # List files in source backend
            source_files = await source.list_files(path_prefix)
            
            for file_info in source_files:
                sync_stats["files_checked"] += 1
                file_path = file_info['path']
                
                try:
                    # Check if file exists in target
                    if await target.file_exists(file_path):
                        # Compare metadata to decide if update is needed
                        source_meta = await source.get_file_metadata(file_path)
                        target_meta = await target.get_file_metadata(file_path)
                        
                        if source_meta.get('size') == target_meta.get('size'):
                            sync_stats["files_skipped"] += 1
                            continue
                    
                    # Copy file via temporary local storage
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        await source.download_file(file_path, temp_path)
                        await target.upload_file(temp_path, file_path)
                        sync_stats["files_copied"] += 1
                        
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                
                except Exception as e:
                    error_msg = f"Failed to sync {file_path}: {e}"
                    self.logger.error(error_msg)
                    sync_stats["errors"].append(error_msg)
        
        except Exception as e:
            sync_stats["errors"].append(f"Sync operation failed: {e}")
        
        return sync_stats
    
    async def get_comprehensive_metrics(self) -> Dict[str, StorageMetrics]:
        """Get metrics from all backends"""
        metrics = {}
        
        for name, backend in self.backends.items():
            metrics[name] = backend.get_metrics()
        
        return metrics
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
Perform health check on all backends"""
        results = {}
        
        for name, backend in self.backends.items():
            try:
                results[name] = await backend.health_check()
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def get_backend_info(self) -> Dict[str, Dict[str, Any]]:
        """
Get information about all configured backends"""
        info = {}
        
        for name, backend in self.backends.items():
            info[name] = {
                'type': backend.config.backend_type.value,
                'access_mode': backend.config.access_mode.value,
                'redundancy_level': backend.config.redundancy_level.value,
                'max_file_size_gb': backend.config.max_file_size_gb,
                'connected': backend._is_connected,
                'metrics': backend.get_metrics()
            }
        
        return info
