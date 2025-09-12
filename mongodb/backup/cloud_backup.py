"""MongoDB Cloud Backup
====================

Cloud storage integration for MongoDB backups with encryption and compression.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import boto3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Cloud provider enumeration."""
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"

@dataclass
class CloudBackupConfig:
    """Cloud backup configuration."""
    provider: CloudProvider
    bucket_name: str
    region: str
    access_key: str
    secret_key: str
    encryption_key: Optional[str] = None

class CloudBackup:
    """Cloud backup integration with multiple providers."""
    
    def __init__(self, config: CloudBackupConfig):
        """Initialize cloud backup.
        
        Args:
            config: Cloud backup configuration
        """
        self.config = config
        self._client = self._create_client()
    
    def upload_backup(self, local_path: str, remote_key: str) -> bool:
        """Upload backup to cloud storage.
        
        Args:
            local_path: Local file path
            remote_key: Remote storage key
            
        Returns:
            True if upload successful
        """
        try:
            if self.config.provider == CloudProvider.AWS_S3:
                # Add server-side encryption for AWS S3
                extra_args = {'ServerSideEncryption': 'AES256'}
                if self.config.encryption_key:
                    extra_args = {
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': self.config.encryption_key
                    }
                self._client.upload_file(local_path, self.config.bucket_name, remote_key, ExtraArgs=extra_args)
                
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                with open(local_path, 'rb') as data:
                    blob_client = self._client.get_blob_client(container=self.config.bucket_name, blob=remote_key)
                    blob_client.upload_blob(data, overwrite=True)
                    
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                bucket = self._client.bucket(self.config.bucket_name)
                blob = bucket.blob(remote_key)
                blob.upload_from_filename(local_path)
            
            logger.info(f"Uploaded backup to cloud: {remote_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload backup: {e}")
            return False
    
    def download_backup(self, remote_key: str, local_path: str) -> bool:
        """Download backup from cloud storage.
        
        Args:
            remote_key: Remote storage key
            local_path: Local file path
            
        Returns:
            True if download successful
        """
        try:
            if self.config.provider == CloudProvider.AWS_S3:
                self._client.download_file(self.config.bucket_name, remote_key, local_path)
                
            elif self.config.provider == CloudProvider.AZURE_BLOB:
                blob_client = self._client.get_blob_client(container=self.config.bucket_name, blob=remote_key)
                with open(local_path, 'wb') as data:
                    blob_data = blob_client.download_blob()
                    data.write(blob_data.readall())
                    
            elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
                bucket = self._client.bucket(self.config.bucket_name)
                blob = bucket.blob(remote_key)
                blob.download_to_filename(local_path)
            
            logger.info(f"Downloaded backup from cloud: {remote_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download backup: {e}")
            return False
    
    def _create_client(self):
        """Create cloud provider client."""
        if self.config.provider == CloudProvider.AWS_S3:
            return boto3.client(
                's3',
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
        elif self.config.provider == CloudProvider.AZURE_BLOB:
            try:
                from azure.storage.blob import BlobServiceClient
                return BlobServiceClient(
                    account_url=f"https://{self.config.access_key}.blob.core.windows.net",
                    credential=self.config.secret_key
                )
            except ImportError:
                logger.error("Azure Blob Storage library not available. Install azure-storage-blob")
                raise NotImplementedError("Azure Blob Storage requires azure-storage-blob package")
        elif self.config.provider == CloudProvider.GOOGLE_CLOUD:
            try:
                from google.cloud import storage
                import json
                # For GCP, access_key would contain the service account JSON
                credentials_info = json.loads(self.config.access_key)
                return storage.Client.from_service_account_info(credentials_info)
            except ImportError:
                logger.error("Google Cloud Storage library not available. Install google-cloud-storage")
                raise NotImplementedError("Google Cloud Storage requires google-cloud-storage package")
            except json.JSONDecodeError:
                logger.error("Invalid Google Cloud credentials format")
                raise ValueError("Google Cloud credentials must be valid JSON")
        else:
            raise NotImplementedError(f"Provider {self.config.provider} not implemented")

__all__ = ['CloudBackup', 'CloudBackupConfig', 'CloudProvider']