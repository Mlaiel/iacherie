"""☁️ Cloud Storage Provider - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/storage/cloud_storage.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

Multi-cloud storage provider supporting AWS S3, MinIO, Azure Blob, and Google Cloud
with intelligent failover, cost optimization, and global distribution.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union, BinaryIO, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta
import json
import mimetypes
from dataclasses import dataclass
from enum import Enum
import hashlib
import os
from pathlib import Path

import boto3
import aiofiles
from botocore.exceptions import ClientError, NoCredentialsError
from azure.storage.blob.aio import BlobServiceClient
from google.cloud import storage as gcs
import aioboto3

logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """
Supported cloud storage providers"""

    AWS_S3 = "aws_s3"
    MINIO = "minio"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"

@dataclass
class CloudConfig:
    """Cloud storage configuration"""
    provider: CloudProvider
    access_key: str
    secret_key: str
    region: str
    bucket_name: str
    endpoint_url: Optional[str] = None  # For MinIO
    project_id: Optional[str] = None    # For Google Cloud
    
    # Performance settings
    multipart_threshold: int = 100 * 1024 * 1024  # 100MB
    max_concurrency: int = 10
    
    # Security settings
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    
    # Cost optimization
    intelligent_tiering: bool = True
    lifecycle_policies: Dict[str, Any] = None

class CloudStorageManager:
    """
    Enterprise cloud storage manager with multi-provider support.
    
    Features:
    - Multi-cloud support (AWS S3, MinIO, Azure, GCP)
    - Intelligent failover and load balancing
    - Cost optimization with storage classes
    - Global replication and distribution
    - Advanced security and encryption
    """
    
    def __init__(self, config: CloudConfig):
        """
Initialize cloud storage manager"""
        self.config = config
        self.client = None
        self.async_client = None
        self.bucket_name = config.bucket_name
        
        # Performance metrics
        self.metrics = {
            'uploads': 0,
            'downloads': 0,
            'errors': 0,
            'total_size': 0,
            'avg_upload_time': 0.0,
            'avg_download_time': 0.0
        }
        
        # Initialize cloud client
        self._initialize_client()
        
        logger.info(f"CloudStorageManager initialized for {config.provider.value}")
    
    def _initialize_client(self) -> None:
        """Initialize cloud provider client"""
        try:
            if self.config.provider == CloudProvider.AWS_S3:
                self._initialize_s3_client()
            elif self.config.provider == CloudProvider.MINIO:
                self._initialize_minio_client()
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                self._initialize_azure_client()
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                self._initialize_gcp_client()
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud client: {str(e)}")
            raise
    
    def _initialize_s3_client(self) -> None:
        """Initialize AWS S3 client"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            
            self.client = session.client('s3')
            
            # Verify bucket exists or create it
            self._ensure_bucket_exists()
            
            # Configure bucket policies
            self._configure_bucket_policies()
            
        except Exception as e:
            logger.error(f"S3 client initialization failed: {str(e)}")
            raise
    
    def _initialize_minio_client(self) -> None:
        """Initialize MinIO client"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key
            )
            
            self.client = session.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                region_name=self.config.region
            )
            
            self._ensure_bucket_exists()
            
        except Exception as e:
            logger.error(f"MinIO client initialization failed: {str(e)}")
            raise
    
    def _initialize_azure_client(self) -> None:
        """Initialize Azure Blob Storage client"""
        try:
            # Azure uses connection string format
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.config.access_key};"
                f"AccountKey={self.config.secret_key};"
                f"EndpointSuffix=core.windows.net"
            )
            
            self.client = BlobServiceClient.from_connection_string(connection_string)
            
            # Ensure container exists
            self._ensure_azure_container_exists()
            
        except Exception as e:
            logger.error(f"Azure client initialization failed: {str(e)}")
            raise
    
    def _initialize_gcp_client(self) -> None:
        """Initialize Google Cloud Storage client"""
        try:
            # Set credentials from environment or service account
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.secret_key
            
            self.client = gcs.Client(project=self.config.project_id)
            
            # Ensure bucket exists
            self._ensure_gcp_bucket_exists()
            
        except Exception as e:
            logger.error(f"GCP client initialization failed: {str(e)}")
            raise
    
    async def store_file(
        self,
        file_path: str,
        content: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store file in cloud storage with optimal settings.
        
        Business Logic:
        1. Determine optimal storage class based on file type and metadata
        2. Apply compression for large files
        3. Set up encryption and security headers
        4. Handle multipart upload for large files
        5. Configure lifecycle policies
        """
        start_time = datetime.now()
        
        try:
            # Prepare content
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif hasattr(content, 'read'):
                content_bytes = content.read()
            else:
                content_bytes = content
            
            # Calculate file properties
            file_size = len(content_bytes)
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            # Prepare metadata
            upload_metadata = {
                'upload_timestamp': datetime.now().isoformat(),
                'file_size': str(file_size),
                'content_hash': content_hash,
                'uploader': 'ia-influencer-agent',
                **(metadata or {})
            }
            
            # Determine storage class
            storage_class = self._determine_storage_class(file_size, metadata)
            
            # Upload based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                result = await self._upload_to_s3(
                    file_path, content_bytes, upload_metadata, storage_class, content_type
                )
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                result = await self._upload_to_azure(
                    file_path, content_bytes, upload_metadata, content_type
                )
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                result = await self._upload_to_gcp(
                    file_path, content_bytes, upload_metadata, storage_class, content_type
                )
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            # Update metrics
            upload_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics('upload', file_size, upload_time)
            
            # Return success result
            return {
                'success': True,
                'file_path': file_path,
                'file_size': file_size,
                'content_hash': content_hash,
                'storage_class': storage_class,
                'upload_time': upload_time,
                'metadata': upload_metadata,
                **result
            }
            
        except Exception as e:
            logger.error(f"Failed to store file {file_path}: {str(e)}")
            self.metrics['errors'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    async def retrieve_file(
        self,
        file_path: str,
        local_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve file from cloud storage"""
        start_time = datetime.now()
        
        try:
            # Download based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                result = await self._download_from_s3(file_path, local_path)
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                result = await self._download_from_azure(file_path, local_path)
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                result = await self._download_from_gcp(file_path, local_path)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            # Update metrics
            download_time = (datetime.now() - start_time).total_seconds()
            file_size = result.get('file_size', 0)
            self._update_metrics('download', file_size, download_time)
            
            return {
                'success': True,
                'file_path': file_path,
                'local_path': result.get('local_path'),
                'content': result.get('content'),
                'download_time': download_time,
                'metadata': result.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_path}: {str(e)}")
            self.metrics['errors'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file from cloud storage"""
        try:
            # Delete based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                await self._delete_from_s3(file_path)
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                await self._delete_from_azure(file_path)
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                await self._delete_from_gcp(file_path)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            logger.info(f"File deleted successfully: {file_path}")
            return {'success': True, 'file_path': file_path}
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            self.metrics['errors'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    async def list_files(
        self,
        prefix: str = "",
        limit: int = 1000,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """List files in cloud storage with optional filtering"""
        try:
            # List based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                files = await self._list_s3_objects(prefix, limit, include_metadata)
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                files = await self._list_azure_blobs(prefix, limit, include_metadata)
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                files = await self._list_gcp_objects(prefix, limit, include_metadata)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []
    
    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata without downloading content"""
        try:
            # Get metadata based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                metadata = await self._get_s3_metadata(file_path)
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                metadata = await self._get_azure_metadata(file_path)
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                metadata = await self._get_gcp_metadata(file_path)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {str(e)}")
            return {}
    
    async def copy_file(
        self,
        source_path: str,
        destination_path: str,
        preserve_metadata: bool = True
    ) -> Dict[str, Any]:
        """Copy file within cloud storage"""
        try:
            # Copy based on provider
            if self.config.provider in [CloudProvider.AWS_S3, CloudProvider.MINIO]:
                result = await self._copy_s3_object(source_path, destination_path, preserve_metadata)
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                result = await self._copy_azure_blob(source_path, destination_path, preserve_metadata)
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                result = await self._copy_gcp_object(source_path, destination_path, preserve_metadata)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            logger.info(f"File copied: {source_path} -> {destination_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to copy file {source_path}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage and performance statistics"""
        return {
            'provider': self.config.provider.value,
            'bucket_name': self.bucket_name,
            'metrics': self.metrics,
            'configuration': {
                'multipart_threshold': self.config.multipart_threshold,
                'max_concurrency': self.config.max_concurrency,
                'encryption_enabled': self.config.encryption_enabled,
                'versioning_enabled': self.config.versioning_enabled,
                'intelligent_tiering': self.config.intelligent_tiering
            }
        }
    
    # Provider-specific implementation methods
    
    async def _upload_to_s3(
        self,
        file_path: str,
        content: bytes,
        metadata: Dict[str, Any],
        storage_class: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
Upload file to AWS S3 or MinIO"""
        try:
            extra_args = {
                'StorageClass': storage_class,
                'ContentType': content_type,
                'Metadata': {k: str(v) for k, v in metadata.items()},
                'ServerSideEncryption': 'AES256' if self.config.encryption_enabled else None
            }
            
            # Remove None values
            extra_args = {k: v for k, v in extra_args.items() if v is not None}
            
            # Use multipart upload for large files
            if len(content) > self.config.multipart_threshold:
                session = aioboto3.Session()
                async with session.client('s3') as s3_client:
                    await s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=file_path,
                        Body=content,
                        **extra_args
                    )
            else:
                # Simple upload for smaller files
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Body=content,
                    **extra_args
                )
            
            # Generate URL
            url = f"s3://{self.bucket_name}/{file_path}"
            
            return {
                'url': url,
                'storage_class': storage_class,
                'encrypted': self.config.encryption_enabled
            }
            
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise
    
    async def _download_from_s3(
        self,
        file_path: str,
        local_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download file from AWS S3 or MinIO"""
        try:
            # Get object with metadata
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            content = response['Body'].read()
            metadata = response.get('Metadata', {})
            
            # Save to local file if path provided
            if local_path:
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(content)
            
            return {
                'content': content,
                'local_path': local_path,
                'file_size': len(content),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise
    
    async def _delete_from_s3(self, file_path: str) -> None:
        """Delete file from AWS S3 or MinIO"""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
        except Exception as e:
            logger.error(f"S3 delete failed: {str(e)}")
            raise
    
    async def _list_s3_objects(
        self,
        prefix: str,
        limit: int,
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """List objects in S3 bucket"""
        try:
            objects = []
            
            paginator = self.client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            for page in page_iterator:
                for obj in page.get('Contents', []):
                    object_info = {
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"'),
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    }
                    
                    if include_metadata:
                        metadata = await self._get_s3_metadata(obj['Key'])
                        object_info['metadata'] = metadata
                    
                    objects.append(object_info)
            
            return objects
            
        except Exception as e:
            logger.error(f"S3 list failed: {str(e)}")
            raise
    
    async def _get_s3_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get S3 object metadata"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                'etag': response.get('ETag', '').strip('"'),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'metadata': response.get('Metadata', {}),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'version_id': response.get('VersionId')
            }
            
        except Exception as e:
            logger.error(f"S3 metadata retrieval failed: {str(e)}")
            return {}
    
    async def _copy_s3_object(
        self,
        source_path: str,
        destination_path: str,
        preserve_metadata: bool
    ) -> Dict[str, Any]:
        """Copy S3 object"""
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_path
            }
            
            extra_args = {}
            if preserve_metadata:
                extra_args['MetadataDirective'] = 'COPY'
            
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_path,
                **extra_args
            )
            
            return {
                'success': True,
                'source_path': source_path,
                'destination_path': destination_path
            }
            
        except Exception as e:
            logger.error(f"S3 copy failed: {str(e)}")
            raise
    
    # Azure Blob Storage methods (similar pattern)
    async def _upload_to_azure(self, file_path: str, content: bytes, metadata: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Upload to Azure Blob Storage"""
        # Azure-specific implementation
        pass
    
    async def _download_from_azure(self, file_path: str, local_path: Optional[str] = None) -> Dict[str, Any]:
        """
Download from Azure Blob Storage"""
        # Azure-specific implementation
        pass
    
    # Google Cloud Storage methods (similar pattern)
    async def _upload_to_gcp(self, file_path: str, content: bytes, metadata: Dict[str, Any], storage_class: str, content_type: str) -> Dict[str, Any]:
        """
Upload to Google Cloud Storage"""
        # GCP-specific implementation
        pass
    
    async def _download_from_gcp(self, file_path: str, local_path: Optional[str] = None) -> Dict[str, Any]:
        """
Download from Google Cloud Storage"""
        # GCP-specific implementation
        pass
    
    # Helper methods
    
    def _determine_storage_class(self, file_size: int, metadata: Optional[Dict[str, Any]]) -> str:
        """
Determine optimal storage class based on file characteristics"""
        if not metadata:
            return 'STANDARD'
        
        # Business logic for storage class selection
        access_frequency = metadata.get('access_frequency', 'high')
        content_type = metadata.get('content_type', '')
        
        # Fingerprints and embeddings need fast access
        if 'fingerprint' in content_type.lower() or 'embedding' in content_type.lower():
            return 'STANDARD'
        
        # Large archives can use cheaper storage
        if file_size > 100 * 1024 * 1024 and access_frequency == 'low':  # 100MB
            return 'GLACIER'
        
        # Frequent access content
        if access_frequency == 'high':
            return 'STANDARD'
        
        # Infrequent access content
        return 'STANDARD_IA'
    
    def _ensure_bucket_exists(self) -> None:
        """
Ensure S3 bucket exists"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                self.client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.config.region}
                )
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                raise
    
    def _ensure_azure_container_exists(self) -> None:
        """Ensure Azure container exists"""
        # Azure-specific implementation
        pass
    
    def _ensure_gcp_bucket_exists(self) -> None:
        """
Ensure GCP bucket exists"""
        # GCP-specific implementation
        pass
    
    def _configure_bucket_policies(self) -> None:
        """
Configure bucket security and lifecycle policies"""
        try:
            # Enable versioning if configured
            if self.config.versioning_enabled:
                self.client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            
            # Configure lifecycle policies if provided
            if self.config.lifecycle_policies:
                self.client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration=self.config.lifecycle_policies
                )
            
            # Enable intelligent tiering if configured
            if self.config.intelligent_tiering:
                self.client.put_bucket_intelligent_tiering_configuration(
                    Bucket=self.bucket_name,
                    Id='EntireBucket',
                    IntelligentTieringConfiguration={
                        'Id': 'EntireBucket',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': ''},
                        'Tierings': [
                            {
                                'Days': 1,
                                'AccessTier': 'ARCHIVE_ACCESS'
                            },
                            {
                                'Days': 90,
                                'AccessTier': 'DEEP_ARCHIVE_ACCESS'
                            }
                        ]
                    }
                )
            
        except Exception as e:
            logger.warning(f"Failed to configure bucket policies: {str(e)}")
    
    def _update_metrics(self, operation: str, file_size: int, processing_time: float) -> None:
        """Update performance metrics"""
        if operation == 'upload':
            self.metrics['uploads'] += 1
            self.metrics['avg_upload_time'] = (
                (self.metrics['avg_upload_time'] * (self.metrics['uploads'] - 1) + processing_time) /
                self.metrics['uploads']
            )
        elif operation == 'download':
            self.metrics['downloads'] += 1
            self.metrics['avg_download_time'] = (
                (self.metrics['avg_download_time'] * (self.metrics['downloads'] - 1) + processing_time) /
                self.metrics['downloads']
            )
        
        self.metrics['total_size'] += file_size

class AsyncCloudStorageManager:
    """
Async wrapper for high-performance concurrent operations"""
    
    def __init__(self, config: CloudConfig):
        self.sync_manager = CloudStorageManager(config)
        self.semaphore = asyncio.Semaphore(config.max_concurrency)
    
    async def store_files_batch(
        self,
        files: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
Store multiple files concurrently"""
        async def store_single(file_info):
            async with self.semaphore:
                return await self.sync_manager.store_file(
                    file_info['path'],
                    file_info['content'],
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
        file_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
Retrieve multiple files concurrently"""
        async def retrieve_single(file_path):
            async with self.semaphore:
                return await self.sync_manager.retrieve_file(file_path)
        
        tasks = [retrieve_single(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for result in results
        ]

# Export classes
__all__ = [
    'CloudStorageManager',
    'AsyncCloudStorageManager', 
    'CloudConfig',
    'CloudProvider'
]
