"""
Google Cloud Storage Configuration for IA-Influencer Agent Platform
===================================================================

Professional Google Cloud Storage configuration for scalable content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core import exceptions

@dataclass
class GCSBucketConfig:
    """Google Cloud Storage bucket configuration for specific content types."""
    
    name: str
    location: str = 'EU'
    storage_class: str = 'STANDARD'  # STANDARD, NEARLINE, COLDLINE, ARCHIVE
    public_read: bool = False
    uniform_bucket_level_access: bool = True
    versioning_enabled: bool = True
    lifecycle_rules: Optional[List[Dict]] = None

@dataclass
class GCSConfig:
    """
    Comprehensive Google Cloud Storage configuration for IA-Influencer Agent platform.
    Provides enterprise-grade object storage with intelligent tiering.
    """
    
    # GCP Project and Authentication
    project_id: str = os.getenv('GCP_PROJECT_ID', '')
    credentials_path: str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    credentials_json: str = os.getenv('GCP_CREDENTIALS_JSON', '')
    
    # Default settings
    default_location: str = os.getenv('GCS_DEFAULT_LOCATION', 'EU')
    default_storage_class: str = 'STANDARD'
    
    # Bucket configurations
    buckets: Dict[str, GCSBucketConfig] = None
    
    # Performance settings
    chunk_size: int = 256 * 1024  # 256KB chunks for resumable uploads
    timeout: int = 300  # 5 minutes
    retry_attempts: int = 3
    
    # Security settings
    enable_encryption: bool = True
    kms_key_name: Optional[str] = os.getenv('GCS_KMS_KEY_NAME')
    enable_uniform_access: bool = True
    
    # Content delivery
    enable_cdn: bool = True
    cdn_cache_control: str = "public, max-age=31536000"  # 1 year
    
    def __post_init__(self):
        """Initialize bucket configurations if not provided."""
        if self.buckets is None:
            self.buckets = self._get_default_bucket_config()
    
    def _get_default_bucket_config(self) -> Dict[str, GCSBucketConfig]:
        """Default bucket configuration for different content types."""
        env = os.getenv('ENVIRONMENT', 'development')
        project_prefix = self.project_id.replace('_', '-').lower()
        
        return {
            'audio_content': GCSBucketConfig(
                name=f"{project_prefix}-audio-{env}",
                location=self.default_location,
                storage_class='STANDARD',
                public_read=False,
                versioning_enabled=True,
                lifecycle_rules=[
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
                        'condition': {'age': 30}
                    },
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'COLDLINE'},
                        'condition': {'age': 365}
                    }
                ]
            ),
            'video_content': GCSBucketConfig(
                name=f"{project_prefix}-video-{env}",
                location=self.default_location,
                storage_class='STANDARD',
                public_read=False,
                versioning_enabled=True,
                lifecycle_rules=[
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
                        'condition': {'age': 90}
                    },
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'ARCHIVE'},
                        'condition': {'age': 730}
                    }
                ]
            ),
            'image_content': GCSBucketConfig(
                name=f"{project_prefix}-images-{env}",
                location=self.default_location,
                storage_class='STANDARD',
                public_read=True,  # For CDN delivery
                versioning_enabled=True,
                lifecycle_rules=[
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
                        'condition': {'age': 180}
                    }
                ]
            ),
            'document_storage': GCSBucketConfig(
                name=f"{project_prefix}-documents-{env}",
                location=self.default_location,
                storage_class='STANDARD',
                public_read=False,
                versioning_enabled=True
            ),
            'ml_models': GCSBucketConfig(
                name=f"{project_prefix}-ml-models-{env}",
                location=self.default_location,
                storage_class='NEARLINE',  # Models accessed less frequently
                public_read=False,
                versioning_enabled=True
            ),
            'fingerprint_storage': GCSBucketConfig(
                name=f"{project_prefix}-fingerprints-{env}",
                location=self.default_location,
                storage_class='COLDLINE',  # Long-term storage
                public_read=False,
                versioning_enabled=True,
                lifecycle_rules=[
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'ARCHIVE'},
                        'condition': {'age': 365}
                    }
                ]
            ),
            'user_uploads': GCSBucketConfig(
                name=f"{project_prefix}-uploads-{env}",
                location=self.default_location,
                storage_class='STANDARD',
                public_read=False,
                versioning_enabled=False,  # Temporary storage
                lifecycle_rules=[
                    {
                        'action': {'type': 'Delete'},
                        'condition': {'age': 30}  # Auto-delete after 30 days
                    }
                ]
            ),
            'backup_storage': GCSBucketConfig(
                name=f"{project_prefix}-backups-{env}",
                location=self.default_location,
                storage_class='ARCHIVE',  # Cheapest for backups
                public_read=False,
                versioning_enabled=False,
                lifecycle_rules=[
                    {
                        'action': {'type': 'Delete'},
                        'condition': {'age': 2555}  # 7 years retention
                    }
                ]
            ),
            'analytics_data': GCSBucketConfig(
                name=f"{project_prefix}-analytics-{env}",
                location=self.default_location,
                storage_class='NEARLINE',
                public_read=False,
                versioning_enabled=False,
                lifecycle_rules=[
                    {
                        'action': {'type': 'SetStorageClass', 'storageClass': 'COLDLINE'},
                        'condition': {'age': 90}
                    },
                    {
                        'action': {'type': 'Delete'},
                        'condition': {'age': 1095}  # 3 years
                    }
                ]
            )
        }
    
    def get_credentials(self) -> service_account.Credentials:
        """Get Google Cloud credentials from various sources."""
        if self.credentials_json:
            # Load from JSON string (environment variable)
            credentials_info = json.loads(self.credentials_json)
            return service_account.Credentials.from_service_account_info(
                credentials_info
            )
        elif self.credentials_path and os.path.exists(self.credentials_path):
            # Load from file path
            return service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
        else:
            # Use default credentials (ADC)
            return None
    
    def get_client(self) -> storage.Client:
        """Create and configure Google Cloud Storage client."""
        credentials = self.get_credentials()
        
        if credentials:
            return storage.Client(
                project=self.project_id,
                credentials=credentials
            )
        else:
            # Use Application Default Credentials
            return storage.Client(project=self.project_id)
    
    def validate_configuration(self) -> bool:
        """Validate GCS configuration and connectivity."""



        try:
            client = self.get_client()
            # Test connectivity by listing buckets
            list(client.list_buckets(max_results=1))
            return True
        except exceptions.GoogleAPIError as e:
            print(f"GCS configuration validation failed: {e}")
            return False
    
    def get_bucket_name(self, content_type: str) -> str:
        """Get bucket name for specific content type."""
        # Map content types to bucket keys
        content_mapping = {
            'audio': 'audio_content',
            'video': 'video_content',
            'image': 'image_content',
            'document': 'document_storage',
            'model': 'ml_models',
            'fingerprint': 'fingerprint_storage',
            'upload': 'user_uploads',
            'backup': 'backup_storage',
            'analytics': 'analytics_data'
        }
        
        bucket_key = content_mapping.get(content_type, 'user_uploads')
        return self.buckets[bucket_key].name
    
    def get_content_types(self) -> List[str]:
        """Get list of supported content types."""



        return ['audio', 'video', 'image', 'document', 'model', 
                'fingerprint', 'upload', 'backup', 'analytics']
    
    def get_storage_class_for_content(self, content_type: str) -> str:
        """Get appropriate storage class for content type."""
        bucket_name = self.get_bucket_name(content_type)
        for bucket_config in self.buckets.values():
            if bucket_config.name == bucket_name:
                return bucket_config.storage_class
        return self.default_storage_class
    
    def get_signed_url_config(self) -> Dict[str, Any]:
        """Get configuration for signed URL generation."""



        return {
            'method': 'GET',
            'expiration': 3600,  # 1 hour
            'version': 'v4',
            'credentials': self.get_credentials()
        }
    
    def get_transfer_manager_config(self) -> Dict[str, Any]:
        """Get configuration for transfer manager (large file uploads)."""



        return {
            'chunk_size': self.chunk_size,
            'timeout': self.timeout,
            'max_workers': 8,
            'use_threads': True
        }
    
    def get_bucket_iam_policy(self, bucket_name: str) -> Dict[str, Any]:
        """Get IAM policy template for bucket security."""



        return {
            'bindings': [
                {
                    'role': 'roles/storage.objectViewer',
                    'members': [
                        f'serviceAccount:{self.project_id}@appspot.gserviceaccount.com'
                    ]
                },
                {
                    'role': 'roles/storage.objectCreator',
                    'members': [
                        f'serviceAccount:{self.project_id}@appspot.gserviceaccount.com'
                    ]
                }
            ]
        }

# Global GCS configuration instance
gcs_config = GCSConfig()
