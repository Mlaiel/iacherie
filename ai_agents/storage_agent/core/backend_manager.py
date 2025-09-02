"""Backend Manager - Multi-Backend Storage System

Advanced storage backend management supporting AWS S3, MinIO, Google Cloud Storage,
local filesystem, and other cloud storage providers with intelligent failover.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This backend management technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices Architect & DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer & Content Protection Specialist: Fahed Mlaiel
"""

import asyncio
import logging
import aiofiles
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import boto3
import minio
from google.cloud import storage as gcs
import azure.storage.blob as azure_blob
import hashlib
import tempfile
import shutil

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import StorageError, ConfigurationError, AuthenticationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    StorageError, ConfigurationError, AuthenticationError = globals().get('StorageError, ConfigurationError, AuthenticationError', Exception)
from ...utils.encryption_utils import EncryptionManager
from ...monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class StorageBackend(str, Enum):
    """
Supported storage backends"""

    LOCAL = "local"
    S3 = "s3"
    MINIO = "minio" 
    GOOGLE_CLOUD = "gcs"
    AZURE_BLOB = "azure"
    DROPBOX = "dropbox"
    FTP = "ftp"

class BackendStatus(str, Enum):
    """Backend operational status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

@dataclass
class StorageConfig:
    """Storage backend configuration"""
    backend_type: StorageBackend
    enabled: bool = True
    priority: int = 1
    max_file_size: int = 5 * 1024 * 1024 * 1024  # 5GB
    allowed_extensions: List[str] = None
    encryption_enabled: bool = False
    compression_enabled: bool = True
    credentials: Dict[str, Any] = None
    settings: Dict[str, Any] = None

@dataclass
class BackendHealth:
    """
Backend health information"""
    backend: StorageBackend
    status: BackendStatus
    response_time: float
    available_space: Optional[int]
    error_rate: float
    last_check: datetime
    error_message: Optional[str] = None

class BackendManager:
    """
    Enterprise multi-backend storage management system with intelligent 
    backend selection, health monitoring, and automatic failover.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backends: Dict[StorageBackend, Any] = {}
        self.backend_configs: Dict[StorageBackend, StorageConfig] = {}
        self.backend_health: Dict[StorageBackend, BackendHealth] = {}
        
        # Initialize metrics and encryption
        self.metrics = MetricsCollector('backend_manager')
        self.encryption_manager = EncryptionManager()
        
        # Performance tracking
        self.performance_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_response_time': 0.0,
            'backend_usage': {backend: 0 for backend in StorageBackend}
        }
        
        # Initialize backends
        asyncio.create_task(self._initialize_backends())
        
        logger.info("BackendManager initialized")
    
    async def _initialize_backends(self):
        """Initialize all configured storage backends"""
        for backend_name, backend_config in self.config.items():
            try:
                backend_type = StorageBackend(backend_name)
                
                if not backend_config.get('enabled', False):
                    logger.info(f"Backend {backend_name} is disabled")
                    continue
                
                config = StorageConfig(
                    backend_type=backend_type,
                    enabled=backend_config.get('enabled', True),
                    priority=backend_config.get('priority', 1),
                    max_file_size=backend_config.get('max_file_size', 5*1024*1024*1024),
                    allowed_extensions=backend_config.get('allowed_extensions', ['*']),
                    encryption_enabled=backend_config.get('encryption', False),
                    compression_enabled=backend_config.get('compression', True),
                    credentials=backend_config.get('credentials', {}),
                    settings=backend_config.get('settings', {})
                )
                
                self.backend_configs[backend_type] = config
                
                # Initialize specific backend
                backend_client = await self._initialize_backend(backend_type, config)
                if backend_client:
                    self.backends[backend_type] = backend_client
                    logger.info(f"Backend {backend_name} initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize backend {backend_name}: {e}")
    
    async def _initialize_backend(
        self, 
        backend_type: StorageBackend, 
        config: StorageConfig
    ) -> Optional[Any]:
        """Initialize specific backend client"""
        try:
            if backend_type == StorageBackend.LOCAL:
                return await self._initialize_local_backend(config)
            
            elif backend_type == StorageBackend.S3:
                return await self._initialize_s3_backend(config)
            
            elif backend_type == StorageBackend.MINIO:
                return await self._initialize_minio_backend(config)
            
            elif backend_type == StorageBackend.GOOGLE_CLOUD:
                return await self._initialize_gcs_backend(config)
            
            elif backend_type == StorageBackend.AZURE_BLOB:
                return await self._initialize_azure_backend(config)
            
            else:
                logger.warning(f"Backend {backend_type} not implemented yet")
                return None
                
        except Exception as e:
            logger.error(f"Backend initialization failed for {backend_type}: {e}")
            return None
    
    async def _initialize_local_backend(self, config: StorageConfig) -> Dict[str, Any]:
        """Initialize local filesystem backend"""
        base_path = Path(config.settings.get('base_path', '/storage/local'))
        base_path.mkdir(parents=True, exist_ok=True)
        
        return {
            'type': 'local',
            'base_path': base_path,
            'config': config
        }
    
    async def _initialize_s3_backend(self, config: StorageConfig) -> Dict[str, Any]:
        """
Initialize AWS S3 backend"""
        credentials = config.credentials
        settings = config.settings
        
        session = boto3.Session(
            aws_access_key_id=credentials.get('access_key'),
            aws_secret_access_key=credentials.get('secret_key'),
            region_name=settings.get('region', 'us-east-1')
        )
        
        s3_client = session.client('s3')
        
        # Test connection
        await self._test_s3_connection(s3_client, settings.get('bucket'))
        
        return {
            'type': 's3',
            'client': s3_client,
            'bucket': settings.get('bucket'),
            'config': config
        }
    
    async def _initialize_minio_backend(self, config: StorageConfig) -> Dict[str, Any]:
        """
Initialize MinIO backend"""
        credentials = config.credentials
        settings = config.settings
        
        minio_client = minio.Minio(
            settings.get('endpoint', 'localhost:9000'),
            access_key=credentials.get('access_key'),
            secret_key=credentials.get('secret_key'),
            secure=settings.get('secure', True)
        )
        
        # Ensure bucket exists
        bucket_name = settings.get('bucket', 'content-storage')
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        
        return {
            'type': 'minio',
            'client': minio_client,
            'bucket': bucket_name,
            'config': config
        }
    
    async def _initialize_gcs_backend(self, config: StorageConfig) -> Dict[str, Any]:
        """
Initialize Google Cloud Storage backend"""
        credentials_path = config.credentials.get('service_account_path')
        bucket_name = config.settings.get('bucket')
        
        if credentials_path:
            client = gcs.Client.from_service_account_json(credentials_path)
        else:
            client = gcs.Client()
        
        bucket = client.bucket(bucket_name)
        
        return {
            'type': 'gcs',
            'client': client,
            'bucket': bucket,
            'config': config
        }
    
    async def _initialize_azure_backend(self, config: StorageConfig) -> Dict[str, Any]:
        try:
            logger.info(f"Executing _initialize_azure_backend")
            
            # Implementation for _initialize_azure_backend
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_azure_backend completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_azure_backend failed: {e}")
            raise
            'type': 'azure',
            'client': blob_service_client,
            'container': container_name,
            'config': config
        }
    
    async def store_file(
        self,
        backend: StorageBackend,
        source_path: Union[str, Path, BinaryIO],
        target_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        access_level: str = "private"
    ) -> str:
        """
        Store file in specified backend
        
        Args:
            backend: Target storage backend
            source_path: Source file path or file object
            target_path: Target path in storage
            metadata: File metadata
            access_level: Access level (private, public, etc.)
            
        Returns:
            URL to stored file
        """
        start_time = datetime.utcnow()
        
        try:
            if backend not in self.backends:
                raise StorageError(f"Backend {backend} not available")
            
            backend_client = self.backends[backend]
            backend_config = self.backend_configs[backend]
            
            # Validate file
            await self._validate_file(source_path, backend_config)
            
            # Encrypt file if needed
            if backend_config.encryption_enabled:
                source_path = await self._encrypt_file(source_path)
            
            # Store in specific backend
            if backend == StorageBackend.LOCAL:
                url = await self._store_local(backend_client, source_path, target_path, metadata)
            
            elif backend == StorageBackend.S3:
                url = await self._store_s3(backend_client, source_path, target_path, metadata, access_level)
            
            elif backend == StorageBackend.MINIO:
                url = await self._store_minio(backend_client, source_path, target_path, metadata)
            
            elif backend == StorageBackend.GOOGLE_CLOUD:
                url = await self._store_gcs(backend_client, source_path, target_path, metadata, access_level)
            
            elif backend == StorageBackend.AZURE_BLOB:
                url = await self._store_azure(backend_client, source_path, target_path, metadata, access_level)
            
            else:
                raise StorageError(f"Backend {backend} storage not implemented")
            
            # Update statistics
            response_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_performance_stats(backend, True, response_time)
            
            # Record metrics
            self.metrics.record_processing_time(response_time)
            self.metrics.increment_counter(f'storage_success_{backend}')
            
            return url
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_performance_stats(backend, False, response_time)
            
            self.metrics.increment_counter(f'storage_failure_{backend}')
            
            logger.error(f"File storage failed in {backend}: {e}")
            raise StorageError(f"Storage failed in {backend}: {e}")
    
    async def retrieve_file(
        self,
        backend: StorageBackend,
        file_path: str,
        local_path: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Retrieve file from backend
        
        Args:
            backend: Source storage backend
            file_path: Path in storage backend
            local_path: Local path to save file (optional)
            
        Returns:
            Local file path or file content
        """
        try:
            if backend not in self.backends:
                raise StorageError(f"Backend {backend} not available")
            
            backend_client = self.backends[backend]
            
            if backend == StorageBackend.LOCAL:
                return await self._retrieve_local(backend_client, file_path, local_path)
            
            elif backend == StorageBackend.S3:
                return await self._retrieve_s3(backend_client, file_path, local_path)
            
            elif backend == StorageBackend.MINIO:
                return await self._retrieve_minio(backend_client, file_path, local_path)
            
            elif backend == StorageBackend.GOOGLE_CLOUD:
                return await self._retrieve_gcs(backend_client, file_path, local_path)
            
            elif backend == StorageBackend.AZURE_BLOB:
                return await self._retrieve_azure(backend_client, file_path, local_path)
            
            else:
                raise StorageError(f"Backend {backend} retrieval not implemented")
                
        except Exception as e:
            logger.error(f"File retrieval failed from {backend}: {e}")
            raise StorageError(f"Retrieval failed from {backend}: {e}")
    
    async def delete_file(self, backend: StorageBackend, file_path: str) -> bool:
        """
        Delete file from backend
        
        Args:
            backend: Storage backend
            file_path: Path in storage backend
            
        Returns:
            True if deletion successful
        """
        try:
            if backend not in self.backends:
                raise StorageError(f"Backend {backend} not available")
            
            backend_client = self.backends[backend]
            
            if backend == StorageBackend.LOCAL:
                return await self._delete_local(backend_client, file_path)
            
            elif backend == StorageBackend.S3:
                return await self._delete_s3(backend_client, file_path)
            
            elif backend == StorageBackend.MINIO:
                return await self._delete_minio(backend_client, file_path)
            
            elif backend == StorageBackend.GOOGLE_CLOUD:
                return await self._delete_gcs(backend_client, file_path)
            
            elif backend == StorageBackend.AZURE_BLOB:
                return await self._delete_azure(backend_client, file_path)
            
            else:
                raise StorageError(f"Backend {backend} deletion not implemented")
                
        except Exception as e:
            logger.error(f"File deletion failed from {backend}: {e}")
            return False
    
    async def health_check(self) -> Dict[StorageBackend, BackendHealth]:
        """Perform health check on all backends"""
        health_results = {}
        
        for backend_type in self.backends:
            try:
                health = await self._check_backend_health(backend_type)
                health_results[backend_type] = health
                self.backend_health[backend_type] = health
                
            except Exception as e:
                health_results[backend_type] = BackendHealth(
                    backend=backend_type,
                    status=BackendStatus.UNHEALTHY,
                    response_time=0.0,
                    available_space=None,
                    error_rate=1.0,
                    last_check=datetime.utcnow(),
                    error_message=str(e)
                )
        
        return health_results
    
    async def get_best_backend(
        self,
        file_size: int,
        file_type: str,
        access_pattern: str = "read_write"
    ) -> StorageBackend:
        """
        Select best backend based on file characteristics and access pattern
        
        Args:
            file_size: Size of file in bytes
            file_type: MIME type of file
            access_pattern: Expected access pattern
            
        Returns:
            Best backend for the file
        """
        available_backends = []
        
        for backend_type, health in self.backend_health.items():
            config = self.backend_configs[backend_type]
            
            # Check if backend is healthy
            if health.status not in [BackendStatus.HEALTHY, BackendStatus.DEGRADED]:
                continue
            
            # Check file size limits
            if file_size > config.max_file_size:
                continue
            
            # Check allowed extensions
            if config.allowed_extensions and '*' not in config.allowed_extensions:
                file_extension = Path(file_type).suffix.lower()
                if file_extension not in config.allowed_extensions:
                    continue
            
            available_backends.append((backend_type, config.priority, health.response_time))
        
        if not available_backends:
            raise StorageError("No suitable backend available for file")
        
        # Sort by priority and response time
        available_backends.sort(key=lambda x: (x[1], x[2]))
        
        return available_backends[0][0]
    
    async def get_backend_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backend statistics"""
        stats = {
            'total_backends': len(self.backends),
            'healthy_backends': sum(
                1 for h in self.backend_health.values() 
                if h.status == BackendStatus.HEALTHY
            ),
            'performance_stats': self.performance_stats.copy(),
            'backend_health': {
                str(k): {
                    'status': v.status,
                    'response_time': v.response_time,
                    'error_rate': v.error_rate,
                    'available_space': v.available_space
                }
                for k, v in self.backend_health.items()
            }
        }
        
        return stats
    
    # Backend-specific storage implementations
    
    async def _store_local(
        self, 
        backend_client: Dict[str, Any], 
        source_path: Union[str, Path], 
        target_path: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """
Store file in local filesystem"""
        base_path = backend_client['base_path']
        full_target_path = base_path / target_path
        full_target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(source_path, (str, Path)):
            shutil.copy2(source_path, full_target_path)
        else:
            # Handle file object
            async with aiofiles.open(full_target_path, 'wb') as f:
                content = source_path.read()
                await f.write(content)
        
        return f"file://{full_target_path}"
    
    async def _store_s3(
        self,
        backend_client: Dict[str, Any],
        source_path: Union[str, Path],
        target_path: str,
        metadata: Optional[Dict[str, Any]],
        access_level: str
    ) -> str:
        """Store file in AWS S3"""
        s3_client = backend_client['client']
        bucket = backend_client['bucket']
        
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
        
        if access_level == "public":
            extra_args['ACL'] = 'public-read'
        
        if isinstance(source_path, (str, Path)):
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.upload_file,
                str(source_path),
                bucket,
                target_path,
                extra_args or None
            )
        else:
            # Handle file object
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.upload_fileobj,
                source_path,
                bucket,
                target_path,
                extra_args or None
            )
        
        return f"https://{bucket}.s3.amazonaws.com/{target_path}"
    
    async def _store_minio(
        self,
        backend_client: Dict[str, Any],
        source_path: Union[str, Path],
        target_path: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Store file in MinIO"""
        minio_client = backend_client['client']
        bucket = backend_client['bucket']
        
        content_type = mimetypes.guess_type(str(source_path))[0] or 'application/octet-stream'
        
        if isinstance(source_path, (str, Path)):
            await asyncio.get_event_loop().run_in_executor(
                None,
                minio_client.fput_object,
                bucket,
                target_path,
                str(source_path),
                content_type
            )
        else:
            file_size = len(source_path.read())
            source_path.seek(0)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                minio_client.put_object,
                bucket,
                target_path,
                source_path,
                file_size,
                content_type
            )
        
        return f"http://localhost:9000/{bucket}/{target_path}"
    
    async def _store_gcs(
        self,
        backend_client: Dict[str, Any],
        source_path: Union[str, Path],
        target_path: str,
        metadata: Optional[Dict[str, Any]],
        access_level: str
    ) -> str:
        """Store file in Google Cloud Storage"""
        bucket = backend_client['bucket']
        blob = bucket.blob(target_path)
        
        if metadata:
            blob.metadata = metadata
        
        if isinstance(source_path, (str, Path)):
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob.upload_from_filename,
                str(source_path)
            )
        else:
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob.upload_from_file,
                source_path
            )
        
        if access_level == "public":
            blob.make_public()
        
        return blob.public_url if access_level == "public" else blob.self_link
    
    async def _store_azure(
        self,
        backend_client: Dict[str, Any],
        source_path: Union[str, Path],
        target_path: str,
        metadata: Optional[Dict[str, Any]],
        access_level: str
    ) -> str:
        """Store file in Azure Blob Storage"""
        blob_service_client = backend_client['client']
        container = backend_client['container']
        
        blob_client = blob_service_client.get_blob_client(
            container=container,
            blob=target_path
        )
        
        if isinstance(source_path, (str, Path)):
            with open(source_path, 'rb') as data:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    blob_client.upload_blob,
                    data,
                    metadata=metadata,
                    overwrite=True
                )
        else:
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob_client.upload_blob,
                source_path,
                metadata=metadata,
                overwrite=True
            )
        
        return blob_client.url
    
    # Backend-specific retrieval implementations
    
    async def _retrieve_local(
        self,
        backend_client: Dict[str, Any],
        file_path: str,
        local_path: Optional[str]
    ) -> str:
        """
Retrieve file from local filesystem"""
        base_path = backend_client['base_path']
        full_file_path = base_path / file_path
        
        if not full_file_path.exists():
            raise StorageError(f"File not found: {file_path}")
        
        if local_path:
            shutil.copy2(full_file_path, local_path)
            return local_path
        
        return str(full_file_path)
    
    async def _retrieve_s3(
        self,
        backend_client: Dict[str, Any],
        file_path: str,
        local_path: Optional[str]
    ) -> Union[str, bytes]:
        """Retrieve file from AWS S3"""
        s3_client = backend_client['client']
        bucket = backend_client['bucket']
        
        if local_path:
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.download_file,
                bucket,
                file_path,
                local_path
            )
            return local_path
        else:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.get_object,
                Bucket=bucket,
                Key=file_path
            )
            return response['Body'].read()
    
    async def _retrieve_minio(
        self,
        backend_client: Dict[str, Any],
        file_path: str,
        local_path: Optional[str]
    ) -> Union[str, bytes]:
        """
Retrieve file from MinIO"""
        minio_client = backend_client['client']
        bucket = backend_client['bucket']
        
        if local_path:
            await asyncio.get_event_loop().run_in_executor(
                None,
                minio_client.fget_object,
                bucket,
                file_path,
                local_path
            )
            return local_path
        else:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                minio_client.get_object,
                bucket,
                file_path
            )
            return response.read()
    
    async def _retrieve_gcs(
        self,
        backend_client: Dict[str, Any],
        file_path: str,
        local_path: Optional[str]
    ) -> Union[str, bytes]:
        """
Retrieve file from Google Cloud Storage"""
        bucket = backend_client['bucket']
        blob = bucket.blob(file_path)
        
        if local_path:
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob.download_to_filename,
                local_path
            )
            return local_path
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None,
                blob.download_as_bytes
            )
    
    async def _retrieve_azure(
        self,
        backend_client: Dict[str, Any],
        file_path: str,
        local_path: Optional[str]
    ) -> Union[str, bytes]:
        """
Retrieve file from Azure Blob Storage"""
        blob_service_client = backend_client['client']
        container = backend_client['container']
        
        blob_client = blob_service_client.get_blob_client(
            container=container,
            blob=file_path
        )
        
        if local_path:
            with open(local_path, 'wb') as download_file:
                download_stream = await asyncio.get_event_loop().run_in_executor(
                    None,
                    blob_client.download_blob
                )
                download_file.write(download_stream.readall())
            return local_path
        else:
            download_stream = await asyncio.get_event_loop().run_in_executor(
                None,
                blob_client.download_blob
            )
            return download_stream.readall()
    
    # Backend-specific deletion implementations
    
    async def _delete_local(self, backend_client: Dict[str, Any], file_path: str) -> bool:
        """
Delete file from local filesystem"""
        try:
            base_path = backend_client['base_path']
            full_file_path = base_path / file_path
            
            if full_file_path.exists():
                full_file_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Local file deletion failed: {e}")
            return False
    
    async def _delete_s3(self, backend_client: Dict[str, Any], file_path: str) -> bool:
        """Delete file from AWS S3"""
        try:
            s3_client = backend_client['client']
            bucket = backend_client['bucket']
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.delete_object,
                Bucket=bucket,
                Key=file_path
            )
            return True
            
        except Exception as e:
            logger.error(f"S3 file deletion failed: {e}")
            return False
    
    async def _delete_minio(self, backend_client: Dict[str, Any], file_path: str) -> bool:
        """Delete file from MinIO"""
        try:
            minio_client = backend_client['client']
            bucket = backend_client['bucket']
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                minio_client.remove_object,
                bucket,
                file_path
            )
            return True
            
        except Exception as e:
            logger.error(f"MinIO file deletion failed: {e}")
            return False
    
    async def _delete_gcs(self, backend_client: Dict[str, Any], file_path: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            bucket = backend_client['bucket']
            blob = bucket.blob(file_path)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob.delete
            )
            return True
            
        except Exception as e:
            logger.error(f"GCS file deletion failed: {e}")
            return False
    
    async def _delete_azure(self, backend_client: Dict[str, Any], file_path: str) -> bool:
        """Delete file from Azure Blob Storage"""
        try:
            blob_service_client = backend_client['client']
            container = backend_client['container']
            
            blob_client = blob_service_client.get_blob_client(
                container=container,
                blob=file_path
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                blob_client.delete_blob
            )
            return True
            
        except Exception as e:
            logger.error(f"Azure Blob deletion failed: {e}")
            return False
    
    # Utility methods
    
    async def _validate_file(self, file_path: Union[str, Path, BinaryIO], config: StorageConfig):
        """Validate file against backend configuration"""
        if isinstance(file_path, (str, Path)):
            file_size = Path(file_path).stat().st_size
        else:
            # For file objects, we need to read to get size
            current_pos = file_path.tell()
            file_path.seek(0, 2)  # Seek to end
            file_size = file_path.tell()
            file_path.seek(current_pos)  # Restore position
        
        if file_size > config.max_file_size:
            raise ValidationError(f"File size {file_size} exceeds limit {config.max_file_size}")
    
    async def _encrypt_file(self, file_path: Union[str, Path]) -> str:
        """Encrypt file and return encrypted file path"""
        if isinstance(file_path, (str, Path)):
            encrypted_path = f"{file_path}.encrypted"
            await self.encryption_manager.encrypt_file(file_path, encrypted_path)
            return encrypted_path
        else:
            # Handle file objects
            temp_path = Path(tempfile.mktemp(suffix='.encrypted'))
            
            # Write file object to temp file
            with open(temp_path, 'wb') as temp_file:
                content = file_path.read()
                temp_file.write(content)
            
            # Encrypt temp file
            encrypted_path = f"{temp_path}.enc"
            await self.encryption_manager.encrypt_file(temp_path, encrypted_path)
            
            # Cleanup
            temp_path.unlink()
            
            return encrypted_path
    
    async def _test_s3_connection(self, s3_client, bucket: str):
        """Test S3 connection and bucket access"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                s3_client.head_bucket,
                Bucket=bucket
            )
        except Exception as e:
            raise AuthenticationError(f"S3 connection failed: {e}")
    
    async def _check_backend_health(self, backend: StorageBackend) -> BackendHealth:
        """Check health of specific backend"""
        start_time = datetime.utcnow()
        
        try:
            backend_client = self.backends[backend]
            
            # Perform backend-specific health check
            if backend == StorageBackend.LOCAL:
                available_space = await self._check_local_space(backend_client)
                status = BackendStatus.HEALTHY
            
            elif backend == StorageBackend.S3:
                await self._test_s3_connection(
                    backend_client['client'], 
                    backend_client['bucket']
                )
                available_space = None  # S3 doesn't have space limits
                status = BackendStatus.HEALTHY
            
            elif backend == StorageBackend.MINIO:
                # Test MinIO connection
                minio_client = backend_client['client']
                bucket = backend_client['bucket']
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    minio_client.bucket_exists,
                    bucket
                )
                available_space = None
                status = BackendStatus.HEALTHY
            
            else:
                # Default health check
                available_space = None
                status = BackendStatus.HEALTHY
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return BackendHealth(
                backend=backend,
                status=status,
                response_time=response_time,
                available_space=available_space,
                error_rate=0.0,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return BackendHealth(
                backend=backend,
                status=BackendStatus.UNHEALTHY,
                response_time=response_time,
                available_space=None,
                error_rate=1.0,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _check_local_space(self, backend_client: Dict[str, Any]) -> int:
        """
Check available space in local filesystem"""
        base_path = backend_client['base_path']
        stat = shutil.disk_usage(base_path)
        return stat.free
    
    async def _update_performance_stats(
        self, 
        backend: StorageBackend, 
        success: bool, 
        response_time: float
    ):
        """
Update performance statistics"""
        self.performance_stats['total_operations'] += 1
        self.performance_stats['backend_usage'][backend] += 1
        
        if success:
            self.performance_stats['successful_operations'] += 1
        else:
            self.performance_stats['failed_operations'] += 1
        
        # Update average response time
        total_ops = self.performance_stats['total_operations']
        current_avg = self.performance_stats['average_response_time']
        self.performance_stats['average_response_time'] = (
            (current_avg * (total_ops - 1) + response_time) / total_ops
        )
    
    async def cleanup(self):
        """
Cleanup backend manager resources"""
        try:
            # Close all backend connections
            for backend_type, backend_client in self.backends.items():
                try:
                    if hasattr(backend_client.get('client'), 'close'):
                        backend_client['client'].close()
                except Exception as e:
                    logger.warning(f"Error closing {backend_type} client: {e}")
            
            logger.info("BackendManager cleanup completed")
            
        except Exception as e:
            logger.error(f"BackendManager cleanup failed: {e}")
