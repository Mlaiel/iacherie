"""AWS S3 Storage Configuration for IA-Influencer Agent Platform
=============================================================

Professional AWS S3 storage configuration for multi-format content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError

@dataclass
class S3BucketConfig:
    """S3 bucket configuration for specific content types."""    
    name: str
    region: str
    public_read: bool = False
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    lifecycle_rules: Optional[Dict] = None

@dataclass
class S3Config:
    """    Comprehensive AWS S3 configuration for IA-Influencer Agent platform.
    Handles multi-format content storage with enterprise-grade security.
    """    
    # AWS Credentials
    access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID', '')
    secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    session_token: Optional[str] = os.getenv('AWS_SESSION_TOKEN')
    
    # Regional Configuration
    default_region: str = os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    
    # Content-specific buckets
    buckets: Dict[str, S3BucketConfig] = None
    
    # Performance settings
    multipart_threshold: int = 64 * 1024 * 1024  # 64MB
    multipart_chunksize: int = 16 * 1024 * 1024  # 16MB
    max_concurrency: int = 10
    max_bandwidth: Optional[int] = None
    
    # Security settings
    enable_encryption: bool = True
    kms_key_id: Optional[str] = os.getenv('AWS_KMS_KEY_ID')
    enable_ssl: bool = True
    signature_version: str = 's3v4'
    
    # Content handling
    enable_presigned_urls: bool = True
    presigned_url_expiration: int = 3600  # 1 hour
    
    def __post_init__(self):
        """Initialize bucket configurations if not provided."""        if self.buckets is None:
            self.buckets = self._get_default_bucket_config()
    
    def _get_default_bucket_config(self) -> Dict[str, S3BucketConfig]:
        """Default bucket configuration for different content types."""        env = os.getenv('ENVIRONMENT', 'development')
        base_name = f"ia-influencer-{env}"
        
        return {
            'audio': S3BucketConfig(
                name=f"{base_name}-audio",
                region=self.default_region,
                public_read=False,
                versioning_enabled=True,
                encryption_enabled=True,
                lifecycle_rules={
                    'audio_archival': {
                        'status': 'Enabled',
                        'transitions': [
                            {'days': 30, 'storage_class': 'STANDARD_IA'},
                            {'days': 365, 'storage_class': 'GLACIER'}
                        ]
                    }
                }
            ),
            'video': S3BucketConfig(
                name=f"{base_name}-video",
                region=self.default_region,
                public_read=False,
                versioning_enabled=True,
                encryption_enabled=True,
                lifecycle_rules={
                    'video_archival': {
                        'status': 'Enabled',
                        'transitions': [
                            {'days': 90, 'storage_class': 'STANDARD_IA'},
                            {'days': 730, 'storage_class': 'GLACIER'}
                        ]
                    }
                }
            ),
            'images': S3BucketConfig(
                name=f"{base_name}-images",
                region=self.default_region,
                public_read=True,  # For CDN delivery
                versioning_enabled=True,
                encryption_enabled=True,
                lifecycle_rules={
                    'image_optimization': {
                        'status': 'Enabled',
                        'transitions': [
                            {'days': 180, 'storage_class': 'STANDARD_IA'}
                        ]
                    }
                }
            ),
            'documents': S3BucketConfig(
                name=f"{base_name}-documents",
                region=self.default_region,
                public_read=False,
                versioning_enabled=True,
                encryption_enabled=True
            ),
            'backups': S3BucketConfig(
                name=f"{base_name}-backups",
                region=self.default_region,
                public_read=False,
                versioning_enabled=False,
                encryption_enabled=True,
                lifecycle_rules={
                    'backup_retention': {
                        'status': 'Enabled',
                        'expiration': {'days': 2555}  # 7 years
                    }
                }
            ),
            'ml_models': S3BucketConfig(
                name=f"{base_name}-ml-models",
                region=self.default_region,
                public_read=False,
                versioning_enabled=True,
                encryption_enabled=True
            ),
            'fingerprints': S3BucketConfig(
                name=f"{base_name}-fingerprints",
                region=self.default_region,
                public_read=False,
                versioning_enabled=True,
                encryption_enabled=True,
                lifecycle_rules={
                    'fingerprint_retention': {
                        'status': 'Enabled',
                        'transitions': [
                            {'days': 365, 'storage_class': 'GLACIER_IR'}
                        ]
                    }
                }
            )
        }
    
    def get_client(self) -> boto3.client:
        """Create and configure S3 client with optimized settings."""        config = boto3.session.Config(
            region_name=self.default_region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50,
            signature_version=self.signature_version
        )
        
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.session_token,
            config=config
        )
    
    def get_transfer_config(self) -> boto3.s3.transfer.TransferConfig:
        """Get optimized transfer configuration for large files."""        return boto3.s3.transfer.TransferConfig(
            multipart_threshold=self.multipart_threshold,
            multipart_chunksize=self.multipart_chunksize,
            max_concurrency=self.max_concurrency,
            max_bandwidth=self.max_bandwidth,
            use_threads=True
        )
    
    def validate_configuration(self) -> bool:
        """Validate S3 configuration and connectivity."""        try:
            client = self.get_client()
            client.list_buckets()
            return True
        except ClientError as e:
            print(f"S3 configuration validation failed: {e}")
            return False
    
    def get_bucket_name(self, content_type: str) -> str:
        """Get bucket name for specific content type."""        if content_type not in self.buckets:
            raise ValueError(f"Unknown content type: {content_type}")
        return self.buckets[content_type].name
    
    def get_content_types(self) -> List[str]:
        """Get list of supported content types."""        return list(self.buckets.keys())

# Global S3 configuration instance
s3_config = S3Config()
