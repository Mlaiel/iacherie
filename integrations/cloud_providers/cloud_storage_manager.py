"""
AINFLUE INTEGRATIONS - CLOUD STORAGE MANAGER
===========================================

Enterprise multi-cloud storage integration for creator economy platform.
Combines multiple expert roles for comprehensive cloud storage management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/cloud_providers)

Expert Roles Applied:
- Lead Dev IA: AI-powered storage optimization, intelligent file management
- Backend Senior: Robust multi-cloud architecture, scalable storage patterns
- ML Engineer: Performance analytics, predictive storage needs, cost optimization
- DBA: Metadata management, indexing strategies, backup optimization
- Security: Encryption, access control, compliance validation, data protection
- Microservices: Distributed storage, service communication, event-driven sync
- Audio Engineer: Media optimization, streaming support, format conversion
- DevOps: Automated backup, monitoring, performance optimization, cost tracking
- IA Prompt Engineer: AI-driven storage recommendations, intelligent data lifecycle

Business Logic Integration:
Creator → Upload → Multi-Cloud Storage → AI Processing → Content Protection → Distribution → Analytics
"""

import asyncio
import base64
import hashlib
import json
import logging
import mimetypes
import os
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple, IO
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from pydantic import BaseModel, Field, validator

# Cloud Storage Libraries
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient
import cloudinary
import cloudinary.uploader

# Security and Encryption
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
STORAGE_OPERATIONS = Counter('cloud_storage_operations_total', 'Total storage operations', ['provider', 'operation'])
UPLOAD_DURATION = Histogram('cloud_storage_upload_duration_seconds', 'Upload duration', ['provider'])
DOWNLOAD_DURATION = Histogram('cloud_storage_download_duration_seconds', 'Download duration', ['provider'])
STORAGE_USAGE = Gauge('cloud_storage_usage_bytes', 'Storage usage in bytes', ['provider', 'bucket'])
ERROR_COUNTER = Counter('cloud_storage_errors_total', 'Storage errors', ['provider', 'error_type'])
COST_TRACKER = Gauge('cloud_storage_cost_estimate', 'Estimated storage costs', ['provider'])

class CloudProvider(Enum):
    """Supported cloud storage providers"""
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    CLOUDINARY = "cloudinary"
    FIREBASE_STORAGE = "firebase_storage"

class StorageClass(Enum):
    """Storage class options"""
    STANDARD = "standard"
    REDUCED_REDUNDANCY = "reduced_redundancy"
    INFREQUENT_ACCESS = "infrequent_access"
    ARCHIVE = "archive"
    DEEP_ARCHIVE = "deep_archive"

class FileType(Enum):
    """File types for optimization"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"

@dataclass
class StorageFile:
    """Storage file metadata"""
    file_id: str
    filename: str
    content_type: str
    file_size: int
    file_type: FileType
    provider: CloudProvider
    bucket: str
    key: str
    url: str
    etag: str
    checksum: str
    encryption_key: Optional[str] = None
    metadata: Dict[str, Any] = None
    storage_class: StorageClass = StorageClass.STANDARD
    uploaded_at: datetime = None
    last_accessed: datetime = None
    expiry_date: Optional[datetime] = None

@dataclass
class StorageProvider:
    """Storage provider configuration"""
    provider: CloudProvider
    enabled: bool
    priority: int
    config: Dict[str, Any]
    cost_per_gb: float
    transfer_cost_per_gb: float
    max_file_size: int
    supported_file_types: List[FileType]

class CloudStorageConfig(BaseModel):
    """Configuration for cloud storage integration"""
    # Multi-Cloud Configuration
    primary_provider: CloudProvider = Field(default=CloudProvider.AWS_S3, description="Primary storage provider")
    backup_providers: List[CloudProvider] = Field(
        default=[CloudProvider.GOOGLE_CLOUD],
        description="Backup storage providers"
    )
    
    # AWS S3 Configuration
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_bucket: str = Field(default="ainflue-content", description="AWS S3 bucket")
    
    # Google Cloud Configuration
    gcp_project_id: Optional[str] = Field(default=None, description="GCP project ID")
    gcp_credentials_path: Optional[str] = Field(default=None, description="GCP credentials JSON path")
    gcp_bucket: str = Field(default="ainflue-content-gcp", description="GCP storage bucket")
    
    # Azure Configuration
    azure_account_name: Optional[str] = Field(default=None, description="Azure storage account name")
    azure_account_key: Optional[str] = Field(default=None, description="Azure account key")
    azure_container: str = Field(default="ainflue-content", description="Azure blob container")
    
    # Cloudinary Configuration
    cloudinary_cloud_name: Optional[str] = Field(default=None, description="Cloudinary cloud name")
    cloudinary_api_key: Optional[str] = Field(default=None, description="Cloudinary API key")
    cloudinary_api_secret: Optional[str] = Field(default=None, description="Cloudinary API secret")
    
    # Storage Optimization
    enable_compression: bool = Field(default=True, description="Enable file compression")
    enable_deduplication: bool = Field(default=True, description="Enable file deduplication")
    auto_backup: bool = Field(default=True, description="Enable automatic backup to secondary providers")
    sync_across_providers: bool = Field(default=False, description="Sync files across all providers")
    
    # Security Configuration
    enable_encryption: bool = Field(default=True, description="Enable file encryption")
    encryption_key: str = Field(default="default-encryption-key", description="Encryption key")
    enable_versioning: bool = Field(default=True, description="Enable file versioning")
    
    # Performance Configuration
    concurrent_uploads: int = Field(default=5, description="Maximum concurrent uploads")
    chunk_size: int = Field(default=8 * 1024 * 1024, description="Upload chunk size (8MB)")
    connection_timeout: int = Field(default=30, description="Connection timeout")
    
    # Cost Optimization
    auto_tier_files: bool = Field(default=True, description="Automatically tier files based on access patterns")
    delete_after_days: Optional[int] = Field(default=None, description="Auto-delete files after N days")
    archive_after_days: int = Field(default=365, description="Archive files after N days")
    
    # Content Delivery
    enable_cdn: bool = Field(default=True, description="Enable CDN for content delivery")
    cdn_domain: Optional[str] = Field(default=None, description="Custom CDN domain")
    
    @validator('concurrent_uploads')
    def validate_concurrent_uploads(cls, v):
        if v <= 0 or v > 20:
            raise ValueError("Concurrent uploads must be between 1 and 20")
        return v

class CloudStorageSecurityManager:
    """Security manager for cloud storage - Security Expert role"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self.cipher_suite = None
        if config.enable_encryption:
            self.cipher_suite = self._create_cipher_suite()
    
    def _create_cipher_suite(self) -> Fernet:
        """Create encryption cipher suite"""
        password = self.config.encryption_key.encode()
        salt = b"ainflue_storage_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    async def encrypt_file(self, file_data: bytes) -> Tuple[bytes, str]:
        """Encrypt file data"""
        if not self.cipher_suite:
            return file_data, ""
        
        try:
            encrypted_data = self.cipher_suite.encrypt(file_data)
            encryption_key = base64.urlsafe_b64encode(self.cipher_suite._signing_key).decode()
            return encrypted_data, encryption_key
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    async def decrypt_file(self, encrypted_data: bytes, encryption_key: str) -> bytes:
        """Decrypt file data"""
        if not encryption_key:
            return encrypted_data
        
        try:
            key = base64.urlsafe_b64decode(encryption_key.encode())
            cipher_suite = Fernet(key)
            return cipher_suite.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise
    
    def validate_file_access(self, user_id: str, file_id: str, operation: str) -> bool:
        """Validate file access permissions"""
        # Simplified access control - in real implementation would check database
        try:
            # Basic validation logic
            if operation in ["read", "download"]:
                return True  # Allow read operations for now
            elif operation in ["write", "delete"]:
                return True  # Would check if user owns the file
            
            return False
        except Exception as e:
            logger.error(f"Access validation failed: {e}")
            return False
    
    def calculate_file_checksum(self, file_data: bytes) -> str:
        """Calculate file checksum for integrity verification"""
        return hashlib.sha256(file_data).hexdigest()
    
    def validate_file_type(self, filename: str, allowed_types: List[str] = None) -> bool:
        """Validate file type based on extension and content"""
        if not allowed_types:
            allowed_types = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.pdf', '.doc', '.docx']
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in allowed_types
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        return sanitized

class CloudStorageMLOptimizer:
    """ML-powered storage optimization - ML Engineer + Lead Dev IA roles"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self.access_patterns = {}
        
    async def optimize_storage_strategy(self, file_metadata: Dict, access_history: List[Dict]) -> Dict[str, Any]:
        """AI-powered storage strategy optimization"""
        optimization = {
            "recommended_provider": self.config.primary_provider.value,
            "recommended_storage_class": StorageClass.STANDARD.value,
            "estimated_cost": 0.0,
            "access_prediction": {},
            "recommendations": []
        }
        
        try:
            file_size = file_metadata.get("file_size", 0)
            file_type = file_metadata.get("file_type", FileType.OTHER.value)
            
            # Analyze access patterns
            if access_history:
                access_analysis = self._analyze_access_patterns(access_history)
                optimization["access_prediction"] = access_analysis
                
                # Recommend storage class based on access frequency
                if access_analysis.get("access_frequency", 0) < 1:  # Less than 1 access per month
                    optimization["recommended_storage_class"] = StorageClass.INFREQUENT_ACCESS.value
                elif access_analysis.get("days_since_last_access", 0) > 365:
                    optimization["recommended_storage_class"] = StorageClass.ARCHIVE.value
            
            # Optimize provider selection based on file type and size
            if file_type in [FileType.IMAGE.value, FileType.VIDEO.value]:
                optimization["recommended_provider"] = CloudProvider.CLOUDINARY.value
                optimization["recommendations"].append("Use Cloudinary for media files with automatic optimization")
            elif file_size > 100 * 1024 * 1024:  # Files > 100MB
                optimization["recommended_provider"] = CloudProvider.AWS_S3.value
                optimization["recommendations"].append("Use AWS S3 for large files with multipart upload")
            
            # Cost estimation
            estimated_cost = self._estimate_storage_cost(file_size, optimization["recommended_storage_class"])
            optimization["estimated_cost"] = estimated_cost
            
            # Performance recommendations
            if file_type == FileType.VIDEO.value:
                optimization["recommendations"].append("Enable video transcoding for multiple qualities")
            elif file_type == FileType.IMAGE.value:
                optimization["recommendations"].append("Enable automatic image optimization and format conversion")
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {e}")
            optimization["error"] = str(e)
        
        return optimization
    
    def _analyze_access_patterns(self, access_history: List[Dict]) -> Dict[str, Any]:
        """Analyze file access patterns"""
        if not access_history:
            return {"access_frequency": 0, "days_since_last_access": 365}
        
        # Calculate access frequency (accesses per month)
        total_days = (datetime.utcnow() - datetime.fromisoformat(access_history[0]["timestamp"])).days
        access_frequency = len(access_history) / max(total_days / 30, 1)
        
        # Days since last access
        last_access = max(datetime.fromisoformat(entry["timestamp"]) for entry in access_history)
        days_since_last_access = (datetime.utcnow() - last_access).days
        
        # Access pattern analysis
        hourly_distribution = {}
        for entry in access_history:
            hour = datetime.fromisoformat(entry["timestamp"]).hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 12
        
        return {
            "access_frequency": access_frequency,
            "days_since_last_access": days_since_last_access,
            "total_accesses": len(access_history),
            "peak_access_hour": peak_hour,
            "access_distribution": hourly_distribution
        }
    
    def _estimate_storage_cost(self, file_size_bytes: int, storage_class: str) -> float:
        """Estimate monthly storage cost"""
        file_size_gb = file_size_bytes / (1024 ** 3)
        
        # Cost per GB per month for different storage classes
        cost_map = {
            StorageClass.STANDARD.value: 0.023,
            StorageClass.INFREQUENT_ACCESS.value: 0.0125,
            StorageClass.ARCHIVE.value: 0.004,
            StorageClass.DEEP_ARCHIVE.value: 0.00099
        }
        
        cost_per_gb = cost_map.get(storage_class, 0.023)
        return file_size_gb * cost_per_gb
    
    async def predict_storage_needs(self, usage_history: List[Dict]) -> Dict[str, Any]:
        """Predict future storage needs"""
        prediction = {
            "predicted_growth_gb": 0.0,
            "predicted_cost": 0.0,
            "capacity_planning": {},
            "recommendations": []
        }
        
        try:
            if len(usage_history) < 2:
                return prediction
            
            # Calculate growth trend
            monthly_usage = {}
            for entry in usage_history:
                month = entry["timestamp"][:7]  # YYYY-MM
                monthly_usage[month] = entry.get("total_size_gb", 0)
            
            months = sorted(monthly_usage.keys())
            if len(months) >= 2:
                recent_usage = monthly_usage[months[-1]]
                previous_usage = monthly_usage[months[-2]]
                growth_rate = (recent_usage - previous_usage) / max(previous_usage, 1)
                
                # Predict next 6 months
                predicted_growth = recent_usage * growth_rate * 6
                prediction["predicted_growth_gb"] = max(0, predicted_growth)
                
                # Estimate cost
                prediction["predicted_cost"] = predicted_growth * 0.023  # Standard storage cost
                
                # Capacity planning
                prediction["capacity_planning"] = {
                    "current_usage_gb": recent_usage,
                    "growth_rate_monthly": growth_rate,
                    "recommended_capacity_gb": recent_usage + predicted_growth * 1.2,  # 20% buffer
                    "storage_optimization_potential": self._calculate_optimization_potential(monthly_usage)
                }
                
                # Generate recommendations
                if growth_rate > 0.5:  # 50% monthly growth
                    prediction["recommendations"].append("High growth rate detected - consider archive policies")
                elif growth_rate < 0:
                    prediction["recommendations"].append("Storage usage declining - review retention policies")
                
                if predicted_growth > 1000:  # > 1TB growth
                    prediction["recommendations"].append("Large storage growth predicted - consider cost optimization")
            
        except Exception as e:
            logger.error(f"Storage prediction failed: {e}")
            prediction["error"] = str(e)
        
        return prediction
    
    def _calculate_optimization_potential(self, monthly_usage: Dict) -> float:
        """Calculate storage optimization potential percentage"""
        if len(monthly_usage) < 3:
            return 0.0
        
        # Simple calculation based on usage variance
        usage_values = list(monthly_usage.values())
        avg_usage = sum(usage_values) / len(usage_values)
        max_usage = max(usage_values)
        
        # Optimization potential based on peak vs average usage
        optimization_potential = ((max_usage - avg_usage) / max_usage) * 100 if max_usage > 0 else 0
        return min(optimization_potential, 50)  # Cap at 50%

class CloudStorageProvider:
    """Base class for cloud storage providers - Backend Senior role"""
    
    def __init__(self, provider: CloudProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize provider client"""
        raise NotImplementedError
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str, metadata: Dict = None) -> str:
        """Upload file to storage"""
        raise NotImplementedError
    
    async def download_file(self, key: str) -> bytes:
        """Download file from storage"""
        raise NotImplementedError
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage"""
        raise NotImplementedError
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Get presigned URL for file"""
        raise NotImplementedError
    
    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[Dict]:
        """List files in storage"""
        raise NotImplementedError

class AWSS3Provider(CloudStorageProvider):
    """AWS S3 storage provider implementation"""
    
    async def initialize(self) -> bool:
        """Initialize AWS S3 client"""
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.config.get('access_key_id'),
                aws_secret_access_key=self.config.get('secret_access_key'),
                region_name=self.config.get('region', 'us-east-1')
            )
            
            # Test connection
            self.client.head_bucket(Bucket=self.config['bucket'])
            logger.info("AWS S3 provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"AWS S3 initialization failed: {e}")
            return False
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str, metadata: Dict = None) -> str:
        """Upload file to S3"""
        try:
            with UPLOAD_DURATION.labels(provider="aws_s3").time():
                extra_args = {
                    'ContentType': content_type,
                    'Metadata': metadata or {}
                }
                
                # Upload file
                self.client.put_object(
                    Bucket=self.config['bucket'],
                    Key=key,
                    Body=file_data,
                    **extra_args
                )
                
                # Generate URL
                url = f"https://{self.config['bucket']}.s3.{self.config.get('region', 'us-east-1')}.amazonaws.com/{key}"
                
                STORAGE_OPERATIONS.labels(provider="aws_s3", operation="upload").inc()
                return url
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            ERROR_COUNTER.labels(provider="aws_s3", error_type="upload").inc()
            raise
    
    async def download_file(self, key: str) -> bytes:
        """Download file from S3"""
        try:
            with DOWNLOAD_DURATION.labels(provider="aws_s3").time():
                response = self.client.get_object(Bucket=self.config['bucket'], Key=key)
                data = response['Body'].read()
                
                STORAGE_OPERATIONS.labels(provider="aws_s3", operation="download").inc()
                return data
        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            ERROR_COUNTER.labels(provider="aws_s3", error_type="download").inc()
            raise
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.config['bucket'], Key=key)
            STORAGE_OPERATIONS.labels(provider="aws_s3", operation="delete").inc()
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            ERROR_COUNTER.labels(provider="aws_s3", error_type="delete").inc()
            return False
    
    async def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Get presigned URL for S3 file"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config['bucket'], 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"S3 URL generation failed: {e}")
            raise

class GoogleCloudProvider(CloudStorageProvider):
    """Google Cloud Storage provider implementation"""
    
    async def initialize(self) -> bool:
        """Initialize Google Cloud Storage client"""
        try:
            if self.config.get('credentials_path'):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config['credentials_path']
            
            self.client = gcs.Client(project=self.config.get('project_id'))
            self.bucket = self.client.bucket(self.config['bucket'])
            
            # Test connection
            if not self.bucket.exists():
                logger.error("GCS bucket does not exist")
                return False
            
            logger.info("Google Cloud Storage provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"GCS initialization failed: {e}")
            return False
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str, metadata: Dict = None) -> str:
        """Upload file to GCS"""
        try:
            with UPLOAD_DURATION.labels(provider="google_cloud").time():
                blob = self.bucket.blob(key)
                blob.content_type = content_type
                
                if metadata:
                    blob.metadata = metadata
                
                blob.upload_from_string(file_data)
                
                STORAGE_OPERATIONS.labels(provider="google_cloud", operation="upload").inc()
                return f"gs://{self.config['bucket']}/{key}"
        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            ERROR_COUNTER.labels(provider="google_cloud", error_type="upload").inc()
            raise

class CloudinaryProvider(CloudStorageProvider):
    """Cloudinary storage provider implementation for media files"""
    
    async def initialize(self) -> bool:
        """Initialize Cloudinary client"""
        try:
            cloudinary.config(
                cloud_name=self.config.get('cloud_name'),
                api_key=self.config.get('api_key'),
                api_secret=self.config.get('api_secret'),
                secure=True
            )
            
            logger.info("Cloudinary provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Cloudinary initialization failed: {e}")
            return False
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str, metadata: Dict = None) -> str:
        """Upload file to Cloudinary"""
        try:
            with UPLOAD_DURATION.labels(provider="cloudinary").time():
                # Determine resource type
                resource_type = "image"
                if content_type.startswith("video/"):
                    resource_type = "video"
                elif content_type.startswith("audio/"):
                    resource_type = "video"  # Cloudinary uses 'video' for audio files
                
                upload_result = cloudinary.uploader.upload(
                    file_data,
                    public_id=key,
                    resource_type=resource_type,
                    context=metadata or {}
                )
                
                STORAGE_OPERATIONS.labels(provider="cloudinary", operation="upload").inc()
                return upload_result.get('secure_url', upload_result.get('url'))
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            ERROR_COUNTER.labels(provider="cloudinary", error_type="upload").inc()
            raise

class MultiCloudStorageManager:
    """Multi-cloud storage manager - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self.providers = {}
        self.security_manager = CloudStorageSecurityManager(config)
        self.ml_optimizer = CloudStorageMLOptimizer(config)
        
        # File registry for tracking across providers
        self.file_registry = {}
        
    async def initialize(self) -> bool:
        """Initialize all configured storage providers"""
        try:
            logger.info("Initializing multi-cloud storage manager")
            
            # Initialize AWS S3
            if self.config.aws_access_key_id and self.config.aws_secret_access_key:
                s3_config = {
                    'access_key_id': self.config.aws_access_key_id,
                    'secret_access_key': self.config.aws_secret_access_key,
                    'region': self.config.aws_region,
                    'bucket': self.config.aws_bucket
                }
                s3_provider = AWSS3Provider(CloudProvider.AWS_S3, s3_config)
                if await s3_provider.initialize():
                    self.providers[CloudProvider.AWS_S3] = s3_provider
            
            # Initialize Google Cloud Storage
            if self.config.gcp_project_id:
                gcs_config = {
                    'project_id': self.config.gcp_project_id,
                    'credentials_path': self.config.gcp_credentials_path,
                    'bucket': self.config.gcp_bucket
                }
                gcs_provider = GoogleCloudProvider(CloudProvider.GOOGLE_CLOUD, gcs_config)
                if await gcs_provider.initialize():
                    self.providers[CloudProvider.GOOGLE_CLOUD] = gcs_provider
            
            # Initialize Cloudinary
            if self.config.cloudinary_cloud_name:
                cloudinary_config = {
                    'cloud_name': self.config.cloudinary_cloud_name,
                    'api_key': self.config.cloudinary_api_key,
                    'api_secret': self.config.cloudinary_api_secret
                }
                cloudinary_provider = CloudinaryProvider(CloudProvider.CLOUDINARY, cloudinary_config)
                if await cloudinary_provider.initialize():
                    self.providers[CloudProvider.CLOUDINARY] = cloudinary_provider
            
            logger.info(f"Initialized {len(self.providers)} storage providers")
            return len(self.providers) > 0
            
        except Exception as e:
            logger.error(f"Multi-cloud storage initialization failed: {e}")
            return False
    
    async def upload_file(self, file_data: bytes, filename: str, creator_id: str, 
                         file_type: FileType = None, metadata: Dict = None) -> StorageFile:
        """Upload file with intelligent provider selection and optimization"""
        file_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Sanitize filename
            safe_filename = self.security_manager.sanitize_filename(filename)
            
            # Determine file type if not provided
            if not file_type:
                file_type = self._determine_file_type(safe_filename)
            
            # Validate file
            if not self.security_manager.validate_file_type(safe_filename):
                raise ValueError(f"File type not allowed: {safe_filename}")
            
            # Calculate checksum
            checksum = self.security_manager.calculate_file_checksum(file_data)
            
            # Check for deduplication
            if self.config.enable_deduplication:
                existing_file = await self._check_duplicate(checksum)
                if existing_file:
                    logger.info(f"File deduplicated: {checksum}")
                    return existing_file
            
            # Encrypt file if enabled
            encryption_key = ""
            if self.config.enable_encryption:
                file_data, encryption_key = await self.security_manager.encrypt_file(file_data)
            
            # Get ML optimization recommendations
            file_metadata = {
                "file_size": len(file_data),
                "file_type": file_type.value,
                "filename": safe_filename
            }
            optimization = await self.ml_optimizer.optimize_storage_strategy(file_metadata, [])
            
            # Select optimal provider
            provider = self._select_provider(file_type, len(file_data), optimization)
            
            # Generate storage key
            key = f"{creator_id}/{datetime.utcnow().strftime('%Y/%m/%d')}/{file_id}_{safe_filename}"
            
            # Upload to primary provider
            content_type = mimetypes.guess_type(safe_filename)[0] or 'application/octet-stream'
            upload_metadata = {
                'creator_id': creator_id,
                'file_id': file_id,
                'original_filename': filename,
                'checksum': checksum,
                **(metadata or {})
            }
            
            url = await provider.upload_file(file_data, key, content_type, upload_metadata)
            
            # Create storage file object
            storage_file = StorageFile(
                file_id=file_id,
                filename=safe_filename,
                content_type=content_type,
                file_size=len(file_data),
                file_type=file_type,
                provider=provider.provider,
                bucket=provider.config.get('bucket', ''),
                key=key,
                url=url,
                etag="",  # Would be set by provider
                checksum=checksum,
                encryption_key=encryption_key,
                metadata=upload_metadata,
                uploaded_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            
            # Register file
            self.file_registry[file_id] = storage_file
            
            # Backup to secondary providers if enabled
            if self.config.auto_backup:
                asyncio.create_task(self._backup_file(storage_file, file_data))
            
            processing_time = time.time() - start_time
            logger.info(f"File uploaded successfully: {file_id} in {processing_time:.2f}s")
            
            return storage_file
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            ERROR_COUNTER.labels(provider="multi_cloud", error_type="upload").inc()
            raise
    
    async def download_file(self, file_id: str, user_id: str = None) -> Tuple[bytes, StorageFile]:
        """Download file with access control and optimization"""
        try:
            # Get file metadata
            storage_file = self.file_registry.get(file_id)
            if not storage_file:
                raise FileNotFoundError(f"File not found: {file_id}")
            
            # Validate access
            if user_id and not self.security_manager.validate_file_access(user_id, file_id, "read"):
                raise PermissionError("Access denied")
            
            # Get provider
            provider = self.providers.get(storage_file.provider)
            if not provider:
                raise ValueError(f"Provider not available: {storage_file.provider}")
            
            # Download file
            file_data = await provider.download_file(storage_file.key)
            
            # Decrypt if encrypted
            if storage_file.encryption_key:
                file_data = await self.security_manager.decrypt_file(file_data, storage_file.encryption_key)
            
            # Update access timestamp
            storage_file.last_accessed = datetime.utcnow()
            
            # Track access for ML optimization
            await self._track_file_access(file_id, user_id, "download")
            
            logger.info(f"File downloaded successfully: {file_id}")
            return file_data, storage_file
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            ERROR_COUNTER.labels(provider="multi_cloud", error_type="download").inc()
            raise
    
    async def delete_file(self, file_id: str, user_id: str = None) -> bool:
        """Delete file from all providers"""
        try:
            # Get file metadata
            storage_file = self.file_registry.get(file_id)
            if not storage_file:
                return False
            
            # Validate access
            if user_id and not self.security_manager.validate_file_access(user_id, file_id, "delete"):
                raise PermissionError("Access denied")
            
            # Delete from all providers
            deleted_from_providers = []
            for provider_type, provider in self.providers.items():
                try:
                    if await provider.delete_file(storage_file.key):
                        deleted_from_providers.append(provider_type)
                except Exception as e:
                    logger.error(f"Failed to delete from {provider_type}: {e}")
            
            # Remove from registry
            if deleted_from_providers:
                del self.file_registry[file_id]
                logger.info(f"File deleted successfully: {file_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            ERROR_COUNTER.labels(provider="multi_cloud", error_type="delete").inc()
            return False
    
    async def get_file_url(self, file_id: str, expires_in: int = 3600, user_id: str = None) -> str:
        """Get presigned URL for file access"""
        try:
            # Get file metadata
            storage_file = self.file_registry.get(file_id)
            if not storage_file:
                raise FileNotFoundError(f"File not found: {file_id}")
            
            # Validate access
            if user_id and not self.security_manager.validate_file_access(user_id, file_id, "read"):
                raise PermissionError("Access denied")
            
            # Get provider
            provider = self.providers.get(storage_file.provider)
            if not provider:
                raise ValueError(f"Provider not available: {storage_file.provider}")
            
            # Generate URL
            url = await provider.get_file_url(storage_file.key, expires_in)
            
            # Track access
            await self._track_file_access(file_id, user_id, "url_access")
            
            return url
            
        except Exception as e:
            logger.error(f"URL generation failed: {e}")
            raise
    
    def _determine_file_type(self, filename: str) -> FileType:
        """Determine file type from filename"""
        ext = Path(filename).suffix.lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        video_exts = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
        audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        doc_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz']
        
        if ext in image_exts:
            return FileType.IMAGE
        elif ext in video_exts:
            return FileType.VIDEO
        elif ext in audio_exts:
            return FileType.AUDIO
        elif ext in doc_exts:
            return FileType.DOCUMENT
        elif ext in archive_exts:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER
    
    def _select_provider(self, file_type: FileType, file_size: int, optimization: Dict) -> CloudStorageProvider:
        """Select optimal storage provider based on file characteristics"""
        # Use ML recommendations if available
        recommended_provider = optimization.get("recommended_provider")
        if recommended_provider and CloudProvider(recommended_provider) in self.providers:
            return self.providers[CloudProvider(recommended_provider)]
        
        # Fallback to rule-based selection
        if file_type in [FileType.IMAGE, FileType.VIDEO] and CloudProvider.CLOUDINARY in self.providers:
            return self.providers[CloudProvider.CLOUDINARY]
        elif CloudProvider.AWS_S3 in self.providers:
            return self.providers[CloudProvider.AWS_S3]
        elif CloudProvider.GOOGLE_CLOUD in self.providers:
            return self.providers[CloudProvider.GOOGLE_CLOUD]
        else:
            # Return first available provider
            return next(iter(self.providers.values()))
    
    async def _check_duplicate(self, checksum: str) -> Optional[StorageFile]:
        """Check if file already exists (deduplication)"""
        for file_id, storage_file in self.file_registry.items():
            if storage_file.checksum == checksum:
                return storage_file
        return None
    
    async def _backup_file(self, storage_file: StorageFile, file_data: bytes):
        """Backup file to secondary providers"""
        try:
            backup_providers = [p for p in self.providers.values() if p.provider != storage_file.provider]
            
            for provider in backup_providers[:2]:  # Limit to 2 backup providers
                try:
                    await provider.upload_file(
                        file_data,
                        storage_file.key,
                        storage_file.content_type,
                        storage_file.metadata
                    )
                    logger.info(f"File backed up to {provider.provider}: {storage_file.file_id}")
                except Exception as e:
                    logger.error(f"Backup failed to {provider.provider}: {e}")
        
        except Exception as e:
            logger.error(f"Backup process failed: {e}")
    
    async def _track_file_access(self, file_id: str, user_id: str, operation: str):
        """Track file access for ML optimization"""
        try:
            access_record = {
                "file_id": file_id,
                "user_id": user_id,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In real implementation, this would be stored in a database
            logger.debug(f"File access tracked: {access_record}")
        
        except Exception as e:
            logger.error(f"Access tracking failed: {e}")
    
    async def get_storage_analytics(self, creator_id: str = None) -> Dict[str, Any]:
        """Get comprehensive storage analytics"""
        try:
            analytics = {
                "total_files": len(self.file_registry),
                "total_size_bytes": 0,
                "provider_distribution": {},
                "file_type_distribution": {},
                "storage_cost_estimate": 0.0,
                "optimization_recommendations": []
            }
            
            # Calculate metrics
            for storage_file in self.file_registry.values():
                if creator_id and storage_file.metadata.get("creator_id") != creator_id:
                    continue
                
                analytics["total_size_bytes"] += storage_file.file_size
                
                provider = storage_file.provider.value
                analytics["provider_distribution"][provider] = analytics["provider_distribution"].get(provider, 0) + 1
                
                file_type = storage_file.file_type.value
                analytics["file_type_distribution"][file_type] = analytics["file_type_distribution"].get(file_type, 0) + 1
            
            # Calculate cost estimate
            analytics["storage_cost_estimate"] = (analytics["total_size_bytes"] / (1024**3)) * 0.023  # $0.023 per GB
            
            # Generate optimization recommendations
            if analytics["total_size_bytes"] > 100 * 1024**3:  # > 100GB
                analytics["optimization_recommendations"].append("Consider implementing archive policies for old files")
            
            if len(analytics["file_type_distribution"]) > 3:
                analytics["optimization_recommendations"].append("Optimize storage by file type - use specialized providers")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Storage analytics failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for multi-cloud storage"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "providers": {},
            "metrics": {
                "total_files": len(self.file_registry),
                "active_providers": len(self.providers),
                "system_memory_usage": psutil.virtual_memory().percent
            }
        }
        
        # Check each provider
        for provider_type, provider in self.providers.items():
            try:
                # Simple health check - attempt to list files
                await provider.list_files(limit=1)
                health_status["providers"][provider_type.value] = "healthy"
            except Exception as e:
                health_status["providers"][provider_type.value] = "unhealthy"
                logger.error(f"Provider {provider_type} health check failed: {e}")
        
        # Determine overall health
        unhealthy_providers = [p for p, status in health_status["providers"].items() if status == "unhealthy"]
        if len(unhealthy_providers) == len(self.providers):
            health_status["status"] = "unhealthy"
        elif unhealthy_providers:
            health_status["status"] = "degraded"
        
        return health_status

# Service factory and configuration
class CloudStorageService:
    """Main cloud storage service facade - DevOps + Integration role"""
    
    def __init__(self, config: Optional[CloudStorageConfig] = None):
        self.config = config or CloudStorageConfig(
            primary_provider=CloudProvider.AWS_S3,
            backup_providers=[CloudProvider.GOOGLE_CLOUD],
            enable_encryption=True,
            auto_backup=True,
            enable_cdn=True
        )
        self.manager = MultiCloudStorageManager(self.config)
    
    async def initialize(self) -> bool:
        """Initialize the cloud storage service"""
        logger.info("Initializing Cloud Storage Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Initialize storage manager
        success = await self.manager.initialize()
        
        if success:
            logger.info("Cloud Storage Service initialized successfully")
        else:
            logger.error("Cloud Storage Service initialization failed")
        
        return success
    
    async def _validate_configuration(self):
        """Validate service configuration"""
        if not self.config.aws_access_key_id and not self.config.gcp_project_id and not self.config.cloudinary_cloud_name:
            logger.warning("No cloud storage providers configured")
    
    async def upload_file(self, file_data: bytes, filename: str, creator_id: str,
                         file_type: FileType = None, metadata: Dict = None) -> StorageFile:
        """Upload file with full enterprise features"""
        return await self.manager.upload_file(file_data, filename, creator_id, file_type, metadata)
    
    async def download_file(self, file_id: str, user_id: str = None) -> Tuple[bytes, StorageFile]:
        """Download file"""
        return await self.manager.download_file(file_id, user_id)
    
    async def delete_file(self, file_id: str, user_id: str = None) -> bool:
        """Delete file"""
        return await self.manager.delete_file(file_id, user_id)
    
    async def get_file_url(self, file_id: str, expires_in: int = 3600, user_id: str = None) -> str:
        """Get file URL"""
        return await self.manager.get_file_url(file_id, expires_in, user_id)
    
    async def get_analytics(self, creator_id: str = None) -> Dict[str, Any]:
        """Get storage analytics"""
        return await self.manager.get_storage_analytics(creator_id)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.manager.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            "upload_operations": STORAGE_OPERATIONS.labels(operation="upload")._value.sum(),
            "download_operations": STORAGE_OPERATIONS.labels(operation="download")._value.sum(),
            "delete_operations": STORAGE_OPERATIONS.labels(operation="delete")._value.sum(),
            "error_count": ERROR_COUNTER._value.sum(),
            "total_storage_usage": STORAGE_USAGE._value.sum()
        }

# Export main classes and functions
__all__ = [
    'CloudStorageService',
    'CloudStorageConfig',
    'StorageFile',
    'StorageProvider',
    'CloudProvider',
    'StorageClass',
    'FileType',
    'MultiCloudStorageManager'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main():
        # Initialize service
        service = CloudStorageService()
        success = await service.initialize()
        
        if success:
            # Health check
            health = await service.get_health_status()
            print(f"Service Health: {health}")
            
            # Example file upload
            # with open("example.jpg", "rb") as f:
            #     file_data = f.read()
            # storage_file = await service.upload_file(file_data, "example.jpg", "creator123")
            # print(f"File uploaded: {storage_file}")
    
    # Run example
    # asyncio.run(main())