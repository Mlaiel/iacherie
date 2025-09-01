"""Object Storage Provider
=======================

Professional object storage implementation for IA-Influencer-Agent platform.
Provides AWS S3, MinIO, and Azure Blob storage capabilities for large files.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import json
import pickle
import gzip
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple, BinaryIO
from datetime import datetime, timedelta
import uuid
from dataclasses import asdict
import boto3
import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError
import io
from pathlib import Path

from .interfaces import (
    BaseStorageProvider, ContentStorageProvider, StorageMetadata,
    QueryOptions, QueryFilter, StorageStats, StorageBackendType,
    CompressionType, DataFormat
)

logger = logging.getLogger(__name__)

class S3ObjectStorageProvider(BaseStorageProvider):
    """
    Professional S3-compatible object storage provider.
    
    Features:
    - AWS S3 and MinIO compatibility
    - Multipart upload for large files
    - Server-side encryption
    - Lifecycle management
    - Versioning support
    - Performance optimization
    - Metadata management
    - Access control
    """
    
    def __init__(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ):
        """Initialize S3 object storage provider."""
        super().__init__(provider_id, StorageBackendType.OBJECT_STORAGE, config)
        
        self.bucket_name = config['bucket_name']
        self.aws_access_key_id = config.get('aws_access_key_id')
        self.aws_secret_access_key = config.get('aws_secret_access_key')
        self.aws_session_token = config.get('aws_session_token')
        self.region_name = config.get('region_name', 'us-east-1')
        self.endpoint_url = config.get('endpoint_url')  # For MinIO or custom S3
        
        # Storage configuration
        self.key_prefix = config.get('key_prefix', f'crawler/{provider_id}/')
        self.enable_encryption = config.get('enable_encryption', True)
        self.encryption_key = config.get('encryption_key')
        self.storage_class = config.get('storage_class', 'STANDARD')
        self.enable_versioning = config.get('enable_versioning', False)
        self.enable_compression = config.get('enable_compression', True)
        self.compression_type = CompressionType(config.get('compression_type', 'gzip'))
        
        # Performance settings
        self.multipart_threshold = config.get('multipart_threshold', 64 * 1024 * 1024)  # 64MB
        self.multipart_chunksize = config.get('multipart_chunksize', 16 * 1024 * 1024)  # 16MB
        self.max_concurrency = config.get('max_concurrency', 10)
        
        # S3 clients
        self.s3_client = None
        self.s3_resource = None
        self.session = None
        
        # Performance tracking
        self.operation_stats = {
            'uploads': 0,
            'downloads': 0,
            'deletes': 0,
            'total_bytes_uploaded': 0,
            'total_bytes_downloaded': 0,
            'total_time': 0.0,
            'errors': 0
        }
        
        logger.info(f"S3 object storage provider initialized: {provider_id}")
    
    async def connect(self) -> None:
        """Establish S3 connection."""
        try:
            # Create async boto3 session
            self.session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
                region_name=self.region_name
            )
            
            # Create S3 client
            client_kwargs = {}
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            
            self.s3_client = await self.session.client('s3', **client_kwargs).__aenter__()
            
            # Test connection by checking bucket access
            try:
                await self.s3_client.head_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Bucket doesn't exist, create it
                    await self._create_bucket()
                else:
                    raise e
            
            # Configure bucket if needed
            await self._configure_bucket()
            
            self.is_connected = True
            logger.info(f"Connected to S3 storage: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to S3 storage {self.provider_id}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close S3 connection."""
        try:
            if self.s3_client:
                await self.s3_client.__aexit__(None, None, None)
                self.s3_client = None
            
            self.s3_resource = None
            self.session = None
            
            self.is_connected = False
            logger.info(f"Disconnected from S3 storage: {self.provider_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from S3 storage {self.provider_id}: {e}")
    
    async def health_check(self) -> bool:
        """Check S3 storage health."""
        try:
            if not self.is_connected or not self.s3_client:
                return False
            
            # Test access to bucket
            await self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
            
        except Exception as e:
            logger.error(f"S3 health check failed for {self.provider_id}: {e}")
            return False
    
    async def _create_bucket(self) -> None:
        """Create S3 bucket if it doesn't exist."""
        try:
            if self.region_name == 'us-east-1':
                # us-east-1 doesn't require LocationConstraint
                await self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                await self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region_name
                    }
                )
            
            logger.info(f"Created S3 bucket: {self.bucket_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                raise e
    
    async def _configure_bucket(self) -> None:
        """Configure S3 bucket settings."""
        try:
            # Enable versioning if requested
            if self.enable_versioning:
                await self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={
                        'Status': 'Enabled'
                    }
                )
            
            # Set bucket encryption if enabled
            if self.enable_encryption:
                encryption_config = {
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
                
                if self.encryption_key:
                    encryption_config['Rules'][0]['ApplyServerSideEncryptionByDefault'] = {
                        'SSEAlgorithm': 'aws:kms',
                        'KMSMasterKeyID': self.encryption_key
                    }
                
                await self.s3_client.put_bucket_encryption(
                    Bucket=self.bucket_name,
                    ServerSideEncryptionConfiguration=encryption_config
                )
            
            logger.info(f"Configured S3 bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.warning(f"Failed to configure S3 bucket {self.bucket_name}: {e}")
    
    def _get_object_key(self, record_id: str) -> str:
        """Get S3 object key for record ID."""
        # Create hierarchical key structure
        record_hash = hashlib.sha256(record_id.encode()).hexdigest()
        
        # Create 3-level hierarchy
        level1 = record_hash[:2]
        level2 = record_hash[2:4]
        level3 = record_hash[4:6]
        
        return f"{self.key_prefix}{level1}/{level2}/{level3}/{record_id}.data"
    
    def _get_metadata_key(self, record_id: str) -> str:
        """Get S3 metadata key for record ID."""
        record_hash = hashlib.sha256(record_id.encode()).hexdigest()
        
        level1 = record_hash[:2]
        level2 = record_hash[2:4]
        level3 = record_hash[4:6]
        
        return f"{self.key_prefix}{level1}/{level2}/{level3}/{record_id}.meta"
    
    def _prepare_data(self, data: Any) -> Tuple[bytes, str]:
        """Prepare data for storage and determine content type."""
        # Serialize data
        if isinstance(data, (dict, list)):
            serialized_data = json.dumps(data).encode()
            content_type = 'application/json'
        elif isinstance(data, str):
            serialized_data = data.encode()
            content_type = 'text/plain'
        elif isinstance(data, bytes):
            serialized_data = data
            content_type = 'application/octet-stream'
        else:
            serialized_data = pickle.dumps(data)
            content_type = 'application/octet-stream'
        
        # Compress if enabled and beneficial
        if (self.enable_compression and 
            len(serialized_data) > 1024):  # Only compress if > 1KB
            
            if self.compression_type == CompressionType.GZIP:
                serialized_data = gzip.compress(serialized_data)
                content_type = 'application/gzip'
        
        return serialized_data, content_type
    
    def _decompress_data(self, data: bytes, content_type: str) -> bytes:
        """Decompress data if needed."""
        if content_type == 'application/gzip':
            return gzip.decompress(data)
        return data
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Store a record in S3."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            object_key = self._get_object_key(record_id)
            metadata_key = self._get_metadata_key(record_id)
            
            # Prepare data
            prepared_data, content_type = self._prepare_data(data)
            data_size = len(prepared_data)
            
            # Calculate checksum
            checksum = hashlib.sha256(prepared_data).hexdigest()
            
            # Prepare S3 metadata
            s3_metadata = {
                'record-id': record_id,
                'stored-at': datetime.utcnow().isoformat(),
                'checksum': checksum,
                'original-size': str(data_size),
                'compressed': str(self.enable_compression and content_type == 'application/gzip')
            }
            
            if metadata:
                s3_metadata.update({
                    'created-at': metadata.created_at.isoformat(),
                    'version': str(metadata.version),
                    'format-type': metadata.format_type.value,
                    'compression-type': metadata.compression_type.value
                })
                
                if metadata.tags:
                    # S3 metadata values must be strings
                    for key, value in metadata.tags.items():
                        s3_metadata[f'tag-{key}'] = str(value)
            
            # Upload data object
            upload_kwargs = {
                'Bucket': self.bucket_name,
                'Key': object_key,
                'Body': prepared_data,
                'ContentType': content_type,
                'Metadata': s3_metadata,
                'StorageClass': self.storage_class
            }
            
            # Use multipart upload for large files
            if data_size > self.multipart_threshold:
                await self._multipart_upload(upload_kwargs, prepared_data)
            else:
                await self.s3_client.put_object(**upload_kwargs)
            
            # Store metadata separately
            if metadata:
                metadata_dict = asdict(metadata)
                metadata_dict['created_at'] = metadata.created_at.isoformat()
                if metadata.updated_at:
                    metadata_dict['updated_at'] = metadata.updated_at.isoformat()
                metadata_dict['compression_type'] = metadata.compression_type.value
                metadata_dict['format_type'] = metadata.format_type.value
                
                metadata_json = json.dumps(metadata_dict, indent=2)
                
                await self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=metadata_key,
                    Body=metadata_json.encode(),
                    ContentType='application/json',
                    StorageClass=self.storage_class
                )
            
            # Update stats
            operation_time = asyncio.get_event_loop().time() - start_time
            self.operation_stats['uploads'] += 1
            self.operation_stats['total_bytes_uploaded'] += data_size
            self.operation_stats['total_time'] += operation_time
            
            return True
            
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to store record {record_id} in S3: {e}")
            return False
    
    async def _multipart_upload(
        self,
        upload_kwargs: Dict[str, Any],
        data: bytes
    ) -> None:
        """Perform multipart upload for large files."""
        bucket = upload_kwargs['Bucket']
        key = upload_kwargs['Key']
        
        # Initiate multipart upload
        create_kwargs = {
            'Bucket': bucket,
            'Key': key,
            'ContentType': upload_kwargs['ContentType'],
            'Metadata': upload_kwargs['Metadata'],
            'StorageClass': upload_kwargs['StorageClass']
        }
        
        response = await self.s3_client.create_multipart_upload(**create_kwargs)
        upload_id = response['UploadId']
        
        try:
            # Upload parts
            parts = []
            part_number = 1
            offset = 0
            
            while offset < len(data):
                chunk = data[offset:offset + self.multipart_chunksize]
                
                part_response = await self.s3_client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk
                )
                
                parts.append({
                    'ETag': part_response['ETag'],
                    'PartNumber': part_number
                })
                
                part_number += 1
                offset += self.multipart_chunksize
            
            # Complete multipart upload
            await self.s3_client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
        except Exception as e:
            # Abort multipart upload on error
            try:
                await self.s3_client.abort_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                    UploadId=upload_id
                )
            except:
                pass
            raise e
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record from S3."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            object_key = self._get_object_key(record_id)
            metadata_key = self._get_metadata_key(record_id)
            
            # Get object
            response = await self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            # Read data
            data_bytes = await response['Body'].read()
            content_type = response.get('ContentType', 'application/octet-stream')
            
            # Update download stats
            operation_time = asyncio.get_event_loop().time() - start_time
            self.operation_stats['downloads'] += 1
            self.operation_stats['total_bytes_downloaded'] += len(data_bytes)
            self.operation_stats['total_time'] += operation_time
            
            # Decompress if needed
            decompressed_data = self._decompress_data(data_bytes, content_type)
            
            # Deserialize data
            if content_type == 'application/json':
                data = json.loads(decompressed_data.decode())
            elif content_type == 'text/plain':
                data = decompressed_data.decode()
            elif content_type in ['application/octet-stream', 'application/gzip']:
                try:
                    data = pickle.loads(decompressed_data)
                except:
                    data = decompressed_data
            else:
                data = decompressed_data
            
            # Load metadata if requested
            metadata = None
            if include_metadata:
                try:
                    # Try to get separate metadata file
                    metadata_response = await self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=metadata_key
                    )
                    
                    metadata_json = await metadata_response['Body'].read()
                    metadata_dict = json.loads(metadata_json.decode())
                    
                    metadata = StorageMetadata(
                        record_id=metadata_dict['record_id'],
                        created_at=datetime.fromisoformat(metadata_dict['created_at']),
                        updated_at=datetime.fromisoformat(metadata_dict['updated_at']) if metadata_dict.get('updated_at') else None,
                        size_bytes=metadata_dict.get('size_bytes'),
                        compression_type=CompressionType(metadata_dict.get('compression_type', 'none')),
                        format_type=DataFormat(metadata_dict.get('format_type', 'binary')),
                        tags=metadata_dict.get('tags'),
                        checksum=metadata_dict.get('checksum'),
                        version=metadata_dict.get('version', 1)
                    )
                    
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        logger.warning(f"Failed to load metadata for {record_id}: {e}")
                    
                    # Fallback to S3 object metadata
                    s3_metadata = response.get('Metadata', {})
                    if s3_metadata:
                        metadata = StorageMetadata(
                            record_id=record_id,
                            created_at=datetime.fromisoformat(s3_metadata.get('stored-at', datetime.utcnow().isoformat())),
                            size_bytes=len(data_bytes),
                            compression_type=CompressionType.GZIP if s3_metadata.get('compressed') == 'true' else CompressionType.NONE,
                            format_type=DataFormat.JSON if content_type == 'application/json' else DataFormat.BINARY,
                            checksum=s3_metadata.get('checksum'),
                            version=int(s3_metadata.get('version', 1))
                        )
            
            return (data, metadata)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                self.operation_stats['errors'] += 1
                logger.error(f"Failed to retrieve record {record_id} from S3: {e}")
                return None
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to retrieve record {record_id} from S3: {e}")
            return None
    
    async def store_batch(
        self,
        records: List[Tuple[str, Any, Optional[StorageMetadata]]]
    ) -> Dict[str, bool]:
        """Store multiple records in batch."""
        results = {}
        
        # Process uploads with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def store_single_record(record_id, data, metadata):
            async with semaphore:
                success = await self.store_record(record_id, data, metadata)
                results[record_id] = success
        
        tasks = [
            store_single_record(record_id, data, metadata)
            for record_id, data, metadata in records
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def retrieve_batch(
        self,
        record_ids: List[str],
        include_metadata: bool = True
    ) -> Dict[str, Optional[Tuple[Any, Optional[StorageMetadata]]]]:
        """Retrieve multiple records in batch."""
        results = {}
        
        # Process downloads with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def retrieve_single_record(record_id):
            async with semaphore:
                result = await self.retrieve_record(record_id, include_metadata)
                results[record_id] = result
        
        tasks = [
            retrieve_single_record(record_id)
            for record_id in record_ids
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a record from S3."""
        try:
            object_key = self._get_object_key(record_id)
            metadata_key = self._get_metadata_key(record_id)
            
            # Delete both data and metadata objects
            delete_objects = [
                {'Key': object_key},
                {'Key': metadata_key}
            ]
            
            response = await self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': delete_objects, 'Quiet': True}
            )
            
            # Check for errors
            errors = response.get('Errors', [])
            if errors:
                # Log errors but don't fail if only metadata deletion failed
                for error in errors:
                    if error['Key'] == object_key:
                        logger.error(f"Failed to delete object {object_key}: {error}")
                        return False
                    else:
                        logger.warning(f"Failed to delete metadata {error['Key']}: {error}")
            
            self.operation_stats['deletes'] += 1
            return True
            
        except Exception as e:
            self.operation_stats['errors'] += 1
            logger.error(f"Failed to delete record {record_id} from S3: {e}")
            return False
    
    async def delete_batch(self, record_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple records in batch."""
        results = {}
        
        try:
            # Prepare delete requests
            delete_objects = []
            for record_id in record_ids:
                object_key = self._get_object_key(record_id)
                metadata_key = self._get_metadata_key(record_id)
                
                delete_objects.extend([
                    {'Key': object_key},
                    {'Key': metadata_key}
                ])
            
            # S3 delete_objects has a limit of 1000 objects per request
            batch_size = 1000
            
            for i in range(0, len(delete_objects), batch_size):
                batch = delete_objects[i:i + batch_size]
                
                response = await self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': batch, 'Quiet': False}
                )
                
                # Process results
                deleted_keys = {obj['Key'] for obj in response.get('Deleted', [])}
                error_keys = {obj['Key'] for obj in response.get('Errors', [])}
                
                for record_id in record_ids:
                    object_key = self._get_object_key(record_id)
                    
                    if object_key in deleted_keys:
                        results[record_id] = True
                        self.operation_stats['deletes'] += 1
                    elif object_key in error_keys:
                        results[record_id] = False
            
            # Set results for any unprocessed records
            for record_id in record_ids:
                if record_id not in results:
                    results[record_id] = False
                    
        except Exception as e:
            logger.error(f"Batch delete operation failed: {e}")
            for record_id in record_ids:
                results[record_id] = False
        
        return results
    
    async def exists(self, record_id: str) -> bool:
        """Check if record exists in S3."""
        try:
            object_key = self._get_object_key(record_id)
            
            await self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Failed to check existence of record {record_id}: {e}")
                return False
    
    async def query_records(
        self,
        options: QueryOptions
    ) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        """Query records using S3 list operations."""
        try:
            # List objects with prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.key_prefix
            )
            
            count = 0
            
            async for page in page_iterator:
                contents = page.get('Contents', [])
                
                for obj in contents:
                    if count >= (options.limit or float('inf')):
                        return
                    
                    key = obj['Key']
                    
                    # Skip metadata files
                    if key.endswith('.meta'):
                        continue
                    
                    # Extract record ID from key
                    try:
                        record_id = key.split('/')[-1].replace('.data', '')
                        
                        # Apply filters if any
                        if options.filters:
                            # Simple filtering based on object metadata
                            obj_metadata = await self.s3_client.head_object(
                                Bucket=self.bucket_name,
                                Key=key
                            )
                            
                            skip_record = False
                            for filter_item in options.filters:
                                if filter_item.field == 'created_at':
                                    obj_date = obj_metadata['LastModified'].replace(tzinfo=None)
                                    filter_date = filter_item.value
                                    
                                    if filter_item.operator == 'gte' and obj_date < filter_date:
                                        skip_record = True
                                        break
                                    elif filter_item.operator == 'lte' and obj_date > filter_date:
                                        skip_record = True
                                        break
                            
                            if skip_record:
                                continue
                        
                        # Retrieve record
                        result = await self.retrieve_record(record_id, options.include_metadata)
                        if result:
                            data, metadata = result
                            yield (record_id, data, metadata)
                            count += 1
                            
                    except Exception as e:
                        logger.error(f"Failed to process S3 object {key}: {e}")
                        
        except Exception as e:
            logger.error(f"Query operation failed: {e}")
    
    async def count_records(
        self,
        filters: Optional[List[QueryFilter]] = None
    ) -> int:
        """Count records in S3."""
        try:
            count = 0
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.key_prefix
            )
            
            async for page in page_iterator:
                contents = page.get('Contents', [])
                
                for obj in contents:
                    key = obj['Key']
                    
                    # Skip metadata files
                    if not key.endswith('.meta'):
                        count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Count operation failed: {e}")
            return 0
    
    async def update_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None
    ) -> bool:
        """Update an existing record (same as store for object storage)."""
        return await self.store_record(record_id, data, metadata)
    
    async def get_statistics(self) -> StorageStats:
        """Get S3 storage statistics."""
        try:
            total_records = 0
            total_size = 0
            today = datetime.utcnow().date()
            created_today = 0
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.key_prefix
            )
            
            async for page in page_iterator:
                contents = page.get('Contents', [])
                
                for obj in contents:
                    key = obj['Key']
                    
                    # Skip metadata files
                    if not key.endswith('.meta'):
                        total_records += 1
                        total_size += obj['Size']
                        
                        # Check if created today
                        obj_date = obj['LastModified'].replace(tzinfo=None).date()
                        if obj_date == today:
                            created_today += 1
            
            avg_size = total_size / total_records if total_records > 0 else 0.0
            
            return StorageStats(
                total_records=total_records,
                total_size_bytes=total_size,
                created_today=created_today,
                updated_today=0,  # Not easily trackable in S3
                average_record_size=avg_size
            )
            
        except Exception as e:
            logger.error(f"Failed to get S3 statistics: {e}")
            return StorageStats(
                total_records=0,
                total_size_bytes=0,
                created_today=0,
                updated_today=0,
                average_record_size=0.0
            )
    
    async def cleanup_old_records(
        self,
        older_than: datetime,
        batch_size: int = 1000
    ) -> int:
        """Remove records older than specified date."""
        total_deleted = 0
        
        try:
            delete_keys = []
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.key_prefix
            )
            
            async for page in page_iterator:
                contents = page.get('Contents', [])
                
                for obj in contents:
                    key = obj['Key']
                    obj_date = obj['LastModified'].replace(tzinfo=None)
                    
                    if obj_date < older_than:
                        delete_keys.append({'Key': key})
                        
                        if len(delete_keys) >= batch_size:
                            # Delete batch
                            response = await self.s3_client.delete_objects(
                                Bucket=self.bucket_name,
                                Delete={'Objects': delete_keys, 'Quiet': True}
                            )
                            
                            deleted_count = len(response.get('Deleted', []))
                            total_deleted += deleted_count
                            delete_keys = []
            
            # Delete remaining keys
            if delete_keys:
                response = await self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': delete_keys, 'Quiet': True}
                )
                
                deleted_count = len(response.get('Deleted', []))
                total_deleted += deleted_count
            
            logger.info(f"Cleaned up {total_deleted} old records from S3")
            return total_deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return total_deleted
    
    async def get_operation_statistics(self) -> Dict[str, Any]:
        """Get detailed operation statistics."""
        total_operations = (
            self.operation_stats['uploads'] + 
            self.operation_stats['downloads'] + 
            self.operation_stats['deletes']
        )
        
        return {
            'total_operations': total_operations,
            'uploads': self.operation_stats['uploads'],
            'downloads': self.operation_stats['downloads'],
            'deletes': self.operation_stats['deletes'],
            'errors': self.operation_stats['errors'],
            'total_bytes_uploaded': self.operation_stats['total_bytes_uploaded'],
            'total_bytes_downloaded': self.operation_stats['total_bytes_downloaded'],
            'total_time': self.operation_stats['total_time'],
            'average_time': (
                self.operation_stats['total_time'] / total_operations
                if total_operations > 0 else 0.0
            ),
            'error_rate': (
                self.operation_stats['errors'] / total_operations
                if total_operations > 0 else 0.0
            ),
            'upload_throughput_mbps': (
                (self.operation_stats['total_bytes_uploaded'] / (1024 * 1024)) / 
                max(self.operation_stats['total_time'], 1)
            ),
            'download_throughput_mbps': (
                (self.operation_stats['total_bytes_downloaded'] / (1024 * 1024)) / 
                max(self.operation_stats['total_time'], 1)
            )
        }

class S3ContentStorageProvider(ContentStorageProvider, S3ObjectStorageProvider):
    """Content-specific S3 storage provider for media files."""
    
    async def store_content(
        self,
        content_id: str,
        platform: str,
        content_type: str,
        content_data: Dict[str, Any],
        media_files: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Store content with associated media files."""
        try:
            # Store main content data
            content_metadata = StorageMetadata(
                record_id=content_id,
                created_at=datetime.utcnow(),
                format_type=DataFormat.JSON,
                tags={
                    'platform': platform,
                    'content_type': content_type,
                    'has_media': str(bool(media_files))
                }
            )
            
            success = await self.store_record(content_id, content_data, content_metadata)
            
            if not success:
                return False
            
            # Store media files if provided
            if media_files:
                for i, media_file in enumerate(media_files):
                    media_id = f"{content_id}_media_{i}"
                    
                    # Determine media type and prepare data
                    if 'data' in media_file:
                        media_data = media_file['data']
                    elif 'url' in media_file:
                        # For URLs, store metadata only
                        media_data = {
                            'url': media_file['url'],
                            'type': media_file.get('type', 'unknown'),
                            'size': media_file.get('size'),
                            'duration': media_file.get('duration')
                        }
                    else:
                        continue
                    
                    media_metadata = StorageMetadata(
                        record_id=media_id,
                        created_at=datetime.utcnow(),
                        format_type=DataFormat.BINARY if 'data' in media_file else DataFormat.JSON,
                        tags={
                            'parent_content_id': content_id,
                            'media_type': media_file.get('type', 'unknown'),
                            'platform': platform
                        }
                    )
                    
                    await self.store_record(media_id, media_data, media_metadata)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store content {content_id}: {e}")
            return False
    
    async def retrieve_content(
        self,
        content_id: str,
        include_media: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve content with optional media files."""
        try:
            # Get main content
            result = await self.retrieve_record(content_id, include_metadata=True)
            
            if not result:
                return None
            
            content_data, metadata = result
            
            # Prepare result
            result_data = {
                'content_id': content_id,
                'data': content_data,
                'metadata': asdict(metadata) if metadata else None
            }
            
            # Get media files if requested
            if include_media:
                media_files = []
                
                # Query for media files using prefix
                async for record_id, media_data, media_metadata in self.query_records(
                    QueryOptions(
                        filters=[
                            QueryFilter('tags.parent_content_id', 'eq', content_id)
                        ],
                        include_metadata=True
                    )
                ):
                    if record_id.startswith(f"{content_id}_media_"):
                        media_info = {
                            'media_id': record_id,
                            'data': media_data,
                            'metadata': asdict(media_metadata) if media_metadata else None
                        }
                        media_files.append(media_info)
                
                result_data['media_files'] = media_files
            
            return result_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve content {content_id}: {e}")
            return None

# Export all object storage classes
__all__ = [
    'S3ObjectStorageProvider',
    'S3ContentStorageProvider'
]
