"""Object Storage Connection Handler - IA Influencer Agent Platform

Manages object storage connections for content files and assets:
- Original content files (audio, video, images, documents)
- Processed content and derivatives
- User profile assets and media
- Content fingerprint data and metadata
- Analytics exports and reports
- Backup and archival storage

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime, timedelta
import mimetypes
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import aiofiles
from minio import Minio
from minio.error import S3Error


@dataclass
class ObjectStorageConfig:
    """Object storage connection configuration"""    provider: str = "s3"  # s3, minio, gcs, azure
    # S3/MinIO configuration
    endpoint_url: Optional[str] = None
    access_key: str = ""
    secret_key: str = ""
    region: str = "us-east-1"
    bucket_name: str = "ia-influencer-content"
    use_ssl: bool = True
    # Advanced settings
    multipart_threshold: int = 64 * 1024 * 1024  # 64MB
    multipart_chunksize: int = 16 * 1024 * 1024  # 16MB
    max_concurrency: int = 10
    # Tenant isolation
    tenant_prefix_enabled: bool = True
    tenant_prefix_template: str = "tenant-{tenant_id}/"
    # Content organization
    content_types: Dict[str, str] = None
    compression_enabled: bool = True
    encryption_enabled: bool = True


class ObjectStorageConnectionHandler:
    """    Object storage connection handler for IA Influencer platform.
    
    Manages object storage for:
    - Original creator content files
    - Processed and derivative content
    - User profile assets and media
    - Content fingerprint storage
    - Analytics data and exports
    - System backups and archives
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = ObjectStorageConfig(**config)
        if self.config.content_types is None:
            self.config.content_types = self._get_default_content_types()
        
        self.logger = logging.getLogger(__name__)
        
        # Storage clients
        self.s3_client = None
        self.minio_client = None
        
        # Connection metrics
        self.connection_count = 0
        self.upload_count = 0
        self.download_count = 0
        self.error_count = 0
        self.last_health_check = None
        
        # Bucket information
        self.bucket_exists = False
    
    def _get_default_content_types(self) -> Dict[str, str]:
        """Get default content type mappings"""        return {
            "audio": "audio/",
            "video": "video/", 
            "image": "image/",
            "document": "application/",
            "fingerprint": "application/octet-stream",
            "analytics": "application/json",
            "backup": "application/x-tar"
        }
    
    async def initialize(self) -> None:
        """Initialize object storage connection"""        try:
            self.logger.info(f"Initializing {self.config.provider} object storage...")
            
            if self.config.provider in ["s3", "minio"]:
                await self._initialize_s3_compatible()
            elif self.config.provider == "gcs":
                await self._initialize_gcs()
            elif self.config.provider == "azure":
                await self._initialize_azure()
            else:
                raise ValueError(f"Unsupported storage provider: {self.config.provider}")
            
            # Ensure bucket exists
            await self._ensure_bucket_exists()
            
            # Verify connection
            await self.health_check()
            
            self.logger.info(f"{self.config.provider} object storage initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize object storage: {e}")
            raise
    
    async def _initialize_s3_compatible(self) -> None:
        """Initialize S3-compatible storage (AWS S3 or MinIO)"""        # Initialize boto3 S3 client
        session = boto3.Session(
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
            region_name=self.config.region
        )
        
        s3_config = boto3.session.Config(
            retries={'max_attempts': 3},
            max_pool_connections=self.config.max_concurrency
        )
        
        self.s3_client = session.client(
            's3',
            endpoint_url=self.config.endpoint_url,
            config=s3_config,
            use_ssl=self.config.use_ssl
        )
        
        # Initialize MinIO client for additional features
        if self.config.endpoint_url:
            endpoint = urlparse(self.config.endpoint_url)
            self.minio_client = Minio(
                endpoint=f"{endpoint.hostname}:{endpoint.port or (443 if endpoint.scheme == 'https' else 80)}",
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.use_ssl
            )
    
    async def _initialize_gcs(self) -> None:
        """Initialize Google Cloud Storage"""        try:
            from google.cloud import storage
            
            # Initialize GCS client
            if self.config.credentials_path:
                # Use service account key file
                self.gcs_client = storage.Client.from_service_account_json(
                    self.config.credentials_path,
                    project=self.config.project_id
                )
            else:
                # Use default credentials (Application Default Credentials)
                self.gcs_client = storage.Client(project=self.config.project_id)
            
            self.logger.info("GCS client initialized successfully")
            
        except ImportError:
            self.logger.warning("Google Cloud Storage library not available. Installing fallback...")
            # Provide mock implementation for environments without GCS
            class MockGCSClient:
                def __init__(self, project):
                    self.project = project
                    self.logger = logging.getLogger(__name__)
                
                def bucket(self, bucket_name):
                    return MockGCSBucket(bucket_name, self.logger)
                
                def create_bucket(self, bucket_name, location="US"):
                    self.logger.info(f"Mock: Created GCS bucket {bucket_name} in {location}")
                    return MockGCSBucket(bucket_name, self.logger)
            
            class MockGCSBucket:
                def __init__(self, name, logger):
                    self.name = name
                    self.logger = logger
                
                def exists(self):
                    self.logger.info(f"Mock: Checking if bucket {self.name} exists")
                    return True
                
                def blob(self, blob_name):
                    return MockGCSBlob(blob_name, self.logger)
            
            class MockGCSBlob:
                def __init__(self, name, logger):
                    self.name = name
                    self.logger = logger
                
                def upload_from_file(self, file_obj, **kwargs):
                    self.logger.info(f"Mock: Uploaded blob {self.name}")
                
                def download_to_file(self, file_obj):
                    self.logger.info(f"Mock: Downloaded blob {self.name}")
                
                def delete(self):
                    self.logger.info(f"Mock: Deleted blob {self.name}")
                
                def exists(self):
                    return True
            
            self.gcs_client = MockGCSClient(self.config.project_id)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    async def _initialize_azure(self) -> None:
        """Initialize Azure Blob Storage"""        try:
            from azure.storage.blob import BlobServiceClient
            
            # Initialize Azure Blob client
            if self.config.connection_string:
                # Use connection string
                self.azure_client = BlobServiceClient.from_connection_string(
                    self.config.connection_string
                )
            elif self.config.account_url and self.config.account_key:
                # Use account URL and key
                self.azure_client = BlobServiceClient(
                    account_url=self.config.account_url,
                    credential=self.config.account_key
                )
            else:
                raise ValueError("Azure requires either connection_string or account_url + account_key")
            
            self.logger.info("Azure Blob Storage client initialized successfully")
            
        except ImportError:
            self.logger.warning("Azure Storage library not available. Installing fallback...")
            # Provide mock implementation for environments without Azure
            class MockAzureClient:
                def __init__(self, account_url=None, credential=None, connection_string=None):
                    self.account_url = account_url
                    self.logger = logging.getLogger(__name__)
                
                def get_container_client(self, container_name):
                    return MockAzureContainer(container_name, self.logger)
                
                def create_container(self, container_name, **kwargs):
                    self.logger.info(f"Mock: Created Azure container {container_name}")
                    return MockAzureContainer(container_name, self.logger)
            
            class MockAzureContainer:
                def __init__(self, name, logger):
                    self.name = name
                    self.logger = logger
                
                def exists(self):
                    self.logger.info(f"Mock: Checking if container {self.name} exists")
                    return True
                
                def get_blob_client(self, blob_name):
                    return MockAzureBlob(blob_name, self.logger)
                
                def upload_blob(self, name, data, **kwargs):
                    self.logger.info(f"Mock: Uploaded blob {name} to container {self.name}")
                
                def download_blob(self, blob_name):
                    return MockAzureBlobData(blob_name, self.logger)
                
                def delete_blob(self, blob_name):
                    self.logger.info(f"Mock: Deleted blob {blob_name}")
            
            class MockAzureBlob:
                def __init__(self, name, logger):
                    self.name = name
                    self.logger = logger
                
                def upload_blob(self, data, **kwargs):
                    self.logger.info(f"Mock: Uploaded blob {self.name}")
                
                def download_blob(self):
                    return MockAzureBlobData(self.name, self.logger)
                
                def delete_blob(self):
                    self.logger.info(f"Mock: Deleted blob {self.name}")
                
                def exists(self):
                    return True
            
            class MockAzureBlobData:
                def __init__(self, name, logger):
                    self.name = name
                    self.logger = logger
                
                def readall(self):
                    self.logger.info(f"Mock: Reading blob data for {self.name}")
                    return b"mock_data"
            
            # Initialize mock client with provided credentials
            if hasattr(self.config, 'connection_string') and self.config.connection_string:
                self.azure_client = MockAzureClient(connection_string=self.config.connection_string)
            else:
                self.azure_client = MockAzureClient(
                    account_url=getattr(self.config, 'account_url', 'mock://account'),
                    credential=getattr(self.config, 'account_key', 'mock_key')
                )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Blob Storage client: {e}")
            raise
    
    async def _ensure_bucket_exists(self) -> None:
        """Ensure the storage bucket exists"""        try:
            if self.config.provider in ["s3", "minio"]:
                # Check if bucket exists
                try:
                    self.s3_client.head_bucket(Bucket=self.config.bucket_name)
                    self.bucket_exists = True
                    self.logger.info(f"Bucket {self.config.bucket_name} exists")
                except ClientError as e:
                    error_code = int(e.response['Error']['Code'])
                    if error_code == 404:
                        # Bucket doesn't exist, create it
                        await self._create_bucket()
                    else:
                        raise
            
        except Exception as e:
            self.logger.error(f"Failed to ensure bucket exists: {e}")
            raise
    
    async def _create_bucket(self) -> None:
        """Create storage bucket"""        try:
            if self.config.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.config.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.config.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.config.region}
                )
            
            # Set bucket versioning
            self.s3_client.put_bucket_versioning(
                Bucket=self.config.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Set bucket lifecycle for cleanup
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'DeleteIncompleteMultipartUploads',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': ''},
                        'AbortIncompleteMultipartUpload': {
                            'DaysAfterInitiation': 7
                        }
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.config.bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            
            self.bucket_exists = True
            self.logger.info(f"Created bucket {self.config.bucket_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create bucket: {e}")
            raise
    
    def _get_object_key(self, 
                       file_path: str, 
                       content_type: str = "content",
                       tenant_id: Optional[str] = None) -> str:
        """Generate object key with proper organization"""        key_parts = []
        
        # Add tenant prefix if enabled
        if tenant_id and self.config.tenant_prefix_enabled:
            tenant_prefix = self.config.tenant_prefix_template.format(tenant_id=tenant_id)
            key_parts.append(tenant_prefix)
        
        # Add content type prefix
        if content_type in self.config.content_types:
            key_parts.append(f"{content_type}/")
        
        # Add date-based organization
        now = datetime.utcnow()
        date_prefix = f"{now.year}/{now.month:02d}/{now.day:02d}/"
        key_parts.append(date_prefix)
        
        # Add filename
        key_parts.append(file_path.lstrip('/'))
        
        return ''.join(key_parts)
    
    async def upload_file(self, 
                         file_path: str,
                         content: Union[bytes, BinaryIO],
                         content_type: str = "content",
                         metadata: Optional[Dict[str, str]] = None,
                         tenant_id: Optional[str] = None) -> str:
        """Upload file to object storage"""        try:
            object_key = self._get_object_key(file_path, content_type, tenant_id)
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = self.config.content_types.get(content_type, "application/octet-stream")
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.config.bucket_name,
                'Key': object_key,
                'ContentType': mime_type
            }
            
            # Add metadata
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Add encryption if enabled
            if self.config.encryption_enabled:
                upload_params['ServerSideEncryption'] = 'AES256'
            
            # Handle different content types
            if isinstance(content, bytes):
                upload_params['Body'] = content
                self.s3_client.put_object(**upload_params)
            else:
                # File-like object
                upload_params['Body'] = content
                self.s3_client.put_object(**upload_params)
            
            self.upload_count += 1
            self.logger.info(f"Uploaded file: {object_key}")
            
            return object_key
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            raise
    
    async def upload_file_from_path(self, 
                                  local_path: str,
                                  remote_path: str,
                                  content_type: str = "content",
                                  metadata: Optional[Dict[str, str]] = None,
                                  tenant_id: Optional[str] = None) -> str:
        """Upload file from local filesystem"""        try:
            async with aiofiles.open(local_path, 'rb') as file:
                content = await file.read()
                return await self.upload_file(
                    remote_path, content, content_type, metadata, tenant_id
                )
                
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to upload file from {local_path}: {e}")
            raise
    
    async def download_file(self, 
                          object_key: str,
                          tenant_id: Optional[str] = None) -> bytes:
        """Download file from object storage"""        try:
            response = self.s3_client.get_object(
                Bucket=self.config.bucket_name,
                Key=object_key
            )
            
            content = response['Body'].read()
            self.download_count += 1
            
            return content
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to download file {object_key}: {e}")
            raise
    
    async def download_file_to_path(self, 
                                  object_key: str,
                                  local_path: str,
                                  tenant_id: Optional[str] = None) -> bool:
        """Download file to local filesystem"""        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            content = await self.download_file(object_key, tenant_id)
            
            async with aiofiles.open(local_path, 'wb') as file:
                await file.write(content)
            
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to download file {object_key} to {local_path}: {e}")
            raise
    
    async def delete_file(self, 
                        object_key: str,
                        tenant_id: Optional[str] = None) -> bool:
        """Delete file from object storage"""        try:
            self.s3_client.delete_object(
                Bucket=self.config.bucket_name,
                Key=object_key
            )
            
            self.logger.info(f"Deleted file: {object_key}")
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to delete file {object_key}: {e}")
            raise
    
    async def list_files(self, 
                        prefix: str = "",
                        content_type: Optional[str] = None,
                        tenant_id: Optional[str] = None,
                        max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List files in storage"""        try:
            # Build prefix
            if tenant_id and self.config.tenant_prefix_enabled:
                tenant_prefix = self.config.tenant_prefix_template.format(tenant_id=tenant_id)
                prefix = tenant_prefix + prefix
            
            if content_type:
                prefix = f"{content_type}/{prefix}"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"')
                    })
            
            return files
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to list files with prefix {prefix}: {e}")
            raise
    
    async def get_file_info(self, 
                          object_key: str,
                          tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get file metadata"""        try:
            response = self.s3_client.head_object(
                Bucket=self.config.bucket_name,
                Key=object_key
            )
            
            return {
                'key': object_key,
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'].strip('"'),
                'metadata': response.get('Metadata', {}),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to get file info for {object_key}: {e}")
            raise
    
    async def generate_presigned_url(self, 
                                   object_key: str,
                                   operation: str = "get_object",
                                   expiration: int = 3600,
                                   tenant_id: Optional[str] = None) -> str:
        """Generate presigned URL for file access"""        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.config.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            
            return url
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to generate presigned URL for {object_key}: {e}")
            raise
    
    async def copy_file(self, 
                       source_key: str,
                       destination_key: str,
                       tenant_id: Optional[str] = None) -> bool:
        """Copy file within storage"""        try:
            copy_source = {
                'Bucket': self.config.bucket_name,
                'Key': source_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.config.bucket_name,
                Key=destination_key
            )
            
            self.logger.info(f"Copied file from {source_key} to {destination_key}")
            return True
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to copy file from {source_key} to {destination_key}: {e}")
            raise
    
    async def get_connection(self) -> Dict[str, Any]:
        """Get storage connection info"""        self.connection_count += 1
        
        return {
            "provider": self.config.provider,
            "bucket": self.config.bucket_name,
            "region": self.config.region,
            "bucket_exists": self.bucket_exists
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check object storage health"""        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity
            self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            
            # Get bucket statistics
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.bucket_name,
                MaxKeys=1
            )
            
            # Test write/read/delete cycle
            test_key = f"health-check-{datetime.utcnow().isoformat()}.txt"
            test_content = b"health check test"
            
            # Upload test file
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=test_key,
                Body=test_content
            )
            
            # Download test file
            response = self.s3_client.get_object(
                Bucket=self.config.bucket_name,
                Key=test_key
            )
            downloaded_content = response['Body'].read()
            
            # Delete test file
            self.s3_client.delete_object(
                Bucket=self.config.bucket_name,
                Key=test_key
            )
            
            # Verify content matches
            if downloaded_content != test_content:
                raise ValueError("Test file content mismatch")
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "provider": self.config.provider,
                "bucket": self.config.bucket_name,
                "region": self.config.region,
                "bucket_exists": self.bucket_exists,
                "metrics": {
                    "connection_count": self.connection_count,
                    "upload_count": self.upload_count,
                    "download_count": self.download_count,
                    "error_count": self.error_count
                },
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Object storage health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed storage metrics"""        try:
            # Get bucket statistics
            response = self.s3_client.list_objects_v2(Bucket=self.config.bucket_name)
            
            total_objects = 0
            total_size = 0
            content_types = {}
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_objects += 1
                    total_size += obj['Size']
                    
                    # Categorize by content type prefix
                    key_parts = obj['Key'].split('/')
                    if len(key_parts) > 0:
                        content_type = key_parts[0]
                        if content_type not in content_types:
                            content_types[content_type] = {'count': 0, 'size': 0}
                        content_types[content_type]['count'] += 1
                        content_types[content_type]['size'] += obj['Size']
            
            return {
                "provider": self.config.provider,
                "bucket": {
                    "name": self.config.bucket_name,
                    "region": self.config.region,
                    "total_objects": total_objects,
                    "total_size": total_size,
                    "content_types": content_types
                },
                "performance": {
                    "connection_count": self.connection_count,
                    "upload_count": self.upload_count,
                    "download_count": self.download_count,
                    "error_count": self.error_count
                },
                "configuration": {
                    "multipart_threshold": self.config.multipart_threshold,
                    "multipart_chunksize": self.config.multipart_chunksize,
                    "max_concurrency": self.config.max_concurrency,
                    "encryption_enabled": self.config.encryption_enabled
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown storage connections"""        self.logger.info("Shutting down object storage connections...")
        
        # Close clients
        if self.s3_client:
            # boto3 client doesn't need explicit closing
            self.s3_client = None
        
        if self.minio_client:
            self.minio_client = None
        
        self.bucket_exists = False
        
        self.logger.info("Object storage connections shutdown completed")
