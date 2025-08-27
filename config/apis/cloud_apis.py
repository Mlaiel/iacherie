"""
Cloud APIs Configuration - Cloud Storage, CDN & Infrastructure Services
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures cloud service APIs including storage (AWS S3, MinIO),
CDN (CloudFlare, AWS CloudFront), and other infrastructure services.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class CloudServiceType(Enum):
    """Cloud service types"""
    OBJECT_STORAGE = "object_storage"
    CDN = "cdn"
    DATABASE = "database"
    SEARCH_ENGINE = "search_engine"
    MESSAGE_QUEUE = "message_queue"
    COMPUTE = "compute"
    MONITORING = "monitoring"

class StorageClass(Enum):
    """Storage class types"""
    STANDARD = "standard"
    INFREQUENT_ACCESS = "infrequent_access"
    ARCHIVE = "archive"
    COLD_STORAGE = "cold_storage"

@dataclass
class CloudAPIConfig:
    """Configuration class for cloud service APIs"""
    service_name: str
    service_type: CloudServiceType
    provider: str  # AWS, Google Cloud, Azure, etc.
    base_url: str
    region: str
    
    # Credentials (from environment)
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    service_account_key: Optional[str] = None
    api_key: Optional[str] = None
    
    # Storage configuration
    default_bucket: Optional[str] = None
    default_storage_class: StorageClass = StorageClass.STANDARD
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 100
    chunk_size_mb: int = 8
    multipart_threshold_mb: int = 64
    timeout_seconds: int = 300
    
    # Cost optimization
    lifecycle_rules_enabled: bool = True
    auto_tiering_enabled: bool = False
    cost_per_gb_month: float = 0.023  # USD per GB per month
    
    # Security settings
    public_access_blocked: bool = True
    access_logging_enabled: bool = True
    ssl_required: bool = True
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""
        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# AWS S3 Configuration
AWS_S3_CONFIG = CloudAPIConfig(
    service_name="aws_s3",
    service_type=CloudServiceType.OBJECT_STORAGE,
    provider="aws",
    base_url="https://s3.amazonaws.com",
    region=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"),
    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    default_bucket=os.getenv("AWS_S3_BUCKET", "ia-influencer-storage"),
    default_storage_class=StorageClass.STANDARD,
    encryption_enabled=True,
    versioning_enabled=True,
    max_concurrent_requests=100,
    multipart_threshold_mb=64,
    lifecycle_rules_enabled=True,
    cost_per_gb_month=0.023,  # S3 Standard pricing
    environments={
        "development": {
            "default_bucket": "ia-influencer-dev-storage",
            "cost_per_gb_month": 0.023
        },
        "staging": {
            "default_bucket": "ia-influencer-staging-storage",
            "cost_per_gb_month": 0.023
        }
    }
)

# MinIO (Self-hosted S3-compatible) Configuration
MINIO_CONFIG = CloudAPIConfig(
    service_name="minio",
    service_type=CloudServiceType.OBJECT_STORAGE,
    provider="minio",
    base_url=os.getenv("MINIO_ENDPOINT", "https://minio.ia-influencer.com"),
    region="us-east-1",  # MinIO default
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    default_bucket=os.getenv("MINIO_BUCKET", "ia-influencer-content"),
    encryption_enabled=True,
    versioning_enabled=True,
    max_concurrent_requests=50,
    cost_per_gb_month=0.01,  # Much cheaper self-hosted
    environments={
        "development": {
            "base_url": "http://localhost:9000",
            "default_bucket": "dev-content"
        },
        "staging": {
            "base_url": "https://staging-minio.ia-influencer.com",
            "default_bucket": "staging-content"
        }
    }
)

# Google Cloud Storage Configuration
GCS_CONFIG = CloudAPIConfig(
    service_name="google_cloud_storage",
    service_type=CloudServiceType.OBJECT_STORAGE,
    provider="google_cloud",
    base_url="https://storage.googleapis.com",
    region=os.getenv("GCS_DEFAULT_REGION", "europe-west1"),
    service_account_key=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    default_bucket=os.getenv("GCS_BUCKET", "ia-influencer-gcs-storage"),
    encryption_enabled=True,
    versioning_enabled=True,
    auto_tiering_enabled=True,  # Google Cloud auto-class
    cost_per_gb_month=0.020,  # GCS Standard pricing
    environments={
        "development": {
            "default_bucket": "ia-influencer-dev-gcs",
            "region": "europe-west1"
        },
        "staging": {
            "default_bucket": "ia-influencer-staging-gcs",
            "region": "europe-west1"
        }
    }
)

# CloudFlare R2 Storage Configuration
CLOUDFLARE_R2_CONFIG = CloudAPIConfig(
    service_name="cloudflare_r2",
    service_type=CloudServiceType.OBJECT_STORAGE,
    provider="cloudflare",
    base_url=os.getenv("CLOUDFLARE_R2_ENDPOINT"),
    region="auto",  # CloudFlare global
    access_key=os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
    secret_key=os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
    default_bucket=os.getenv("CLOUDFLARE_R2_BUCKET", "ia-influencer-r2"),
    cost_per_gb_month=0.015,  # R2 pricing advantage
    environments={
        "development": {
            "default_bucket": "ia-influencer-dev-r2"
        },
        "staging": {
            "default_bucket": "ia-influencer-staging-r2"
        }
    }
)

# CloudFlare CDN Configuration
CLOUDFLARE_CDN_CONFIG = CloudAPIConfig(
    service_name="cloudflare_cdn",
    service_type=CloudServiceType.CDN,
    provider="cloudflare",
    base_url="https://api.cloudflare.com/client/v4",
    region="global",
    api_key=os.getenv("CLOUDFLARE_API_KEY"),
    access_key=os.getenv("CLOUDFLARE_EMAIL"),  # Email for API access
    timeout_seconds=30,
    cost_per_gb_month=0.0,  # Free tier available
    environments={
        "development": {
            "base_url": "https://api.cloudflare.com/client/v4"
        }
    }
)

# AWS CloudFront CDN Configuration
AWS_CLOUDFRONT_CONFIG = CloudAPIConfig(
    service_name="aws_cloudfront",
    service_type=CloudServiceType.CDN,
    provider="aws",
    base_url="https://cloudfront.amazonaws.com",
    region="global",
    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    ssl_required=True,
    cost_per_gb_month=0.085,  # CloudFront pricing
    environments={
        "development": {
            "cost_per_gb_month": 0.085
        }
    }
)

# Elasticsearch Configuration
ELASTICSEARCH_CONFIG = CloudAPIConfig(
    service_name="elasticsearch",
    service_type=CloudServiceType.SEARCH_ENGINE,
    provider="elastic",
    base_url=os.getenv("ELASTICSEARCH_URL", "https://elasticsearch.ia-influencer.com"),
    region="eu-central-1",
    api_key=os.getenv("ELASTICSEARCH_API_KEY"),
    access_key=os.getenv("ELASTICSEARCH_USERNAME"),
    secret_key=os.getenv("ELASTICSEARCH_PASSWORD"),
    timeout_seconds=30,
    environments={
        "development": {
            "base_url": "http://localhost:9200",
            "api_key": None,
            "access_key": "elastic",
            "secret_key": "password"
        },
        "staging": {
            "base_url": "https://staging-elasticsearch.ia-influencer.com"
        }
    }
)

# Redis Configuration (for caching and queues)
REDIS_CONFIG = CloudAPIConfig(
    service_name="redis",
    service_type=CloudServiceType.MESSAGE_QUEUE,
    provider="redis",
    base_url=os.getenv("REDIS_URL", "redis://redis.ia-influencer.com:6379"),
    region="eu-central-1",
    secret_key=os.getenv("REDIS_PASSWORD"),
    timeout_seconds=5,
    max_concurrent_requests=1000,
    environments={
        "development": {
            "base_url": "redis://localhost:6379",
            "secret_key": None
        },
        "staging": {
            "base_url": "redis://staging-redis.ia-influencer.com:6379"
        }
    }
)

# MongoDB Atlas Configuration
MONGODB_ATLAS_CONFIG = CloudAPIConfig(
    service_name="mongodb_atlas",
    service_type=CloudServiceType.DATABASE,
    provider="mongodb",
    base_url=os.getenv("MONGODB_ATLAS_URL"),
    region=os.getenv("MONGODB_ATLAS_REGION", "EU_CENTRAL_1"),
    api_key=os.getenv("MONGODB_ATLAS_API_KEY"),
    access_key=os.getenv("MONGODB_ATLAS_USERNAME"),
    secret_key=os.getenv("MONGODB_ATLAS_PASSWORD"),
    encryption_enabled=True,
    environments={
        "development": {
            "base_url": "mongodb://localhost:27017/ia_influencer_dev"
        },
        "staging": {
            "base_url": os.getenv("MONGODB_STAGING_URL")
        }
    }
)

# Prometheus Monitoring Configuration
PROMETHEUS_CONFIG = CloudAPIConfig(
    service_name="prometheus",
    service_type=CloudServiceType.MONITORING,
    provider="prometheus",
    base_url=os.getenv("PROMETHEUS_URL", "https://prometheus.ia-influencer.com"),
    region="eu-central-1",
    api_key=os.getenv("PROMETHEUS_API_KEY"),
    timeout_seconds=30,
    environments={
        "development": {
            "base_url": "http://localhost:9090"
        },
        "staging": {
            "base_url": "https://staging-prometheus.ia-influencer.com"
        }
    }
)

# Grafana Monitoring Configuration
GRAFANA_CONFIG = CloudAPIConfig(
    service_name="grafana",
    service_type=CloudServiceType.MONITORING,
    provider="grafana",
    base_url=os.getenv("GRAFANA_URL", "https://grafana.ia-influencer.com"),
    region="eu-central-1",
    api_key=os.getenv("GRAFANA_API_KEY"),
    access_key=os.getenv("GRAFANA_USERNAME"),
    secret_key=os.getenv("GRAFANA_PASSWORD"),
    environments={
        "development": {
            "base_url": "http://localhost:3000",
            "access_key": "admin",
            "secret_key": "admin"
        },
        "staging": {
            "base_url": "https://staging-grafana.ia-influencer.com"
        }
    }
)

# FAISS Vector Database Configuration
FAISS_CONFIG = CloudAPIConfig(
    service_name="faiss",
    service_type=CloudServiceType.SEARCH_ENGINE,
    provider="faiss",
    base_url=os.getenv("FAISS_SERVER_URL", "http://faiss.ia-influencer.com:8000"),
    region="eu-central-1",
    api_key=os.getenv("FAISS_API_KEY"),
    max_concurrent_requests=200,
    timeout_seconds=60,
    environments={
        "development": {
            "base_url": "http://localhost:8001"
        },
        "staging": {
            "base_url": "http://staging-faiss.ia-influencer.com:8000"
        }
    }
)

# Cloud configurations registry
CLOUD_CONFIGS: Dict[str, CloudAPIConfig] = {
    "aws_s3": AWS_S3_CONFIG,
    "minio": MINIO_CONFIG,
    "google_cloud_storage": GCS_CONFIG,
    "cloudflare_r2": CLOUDFLARE_R2_CONFIG,
    "cloudflare_cdn": CLOUDFLARE_CDN_CONFIG,
    "aws_cloudfront": AWS_CLOUDFRONT_CONFIG,
    "elasticsearch": ELASTICSEARCH_CONFIG,
    "redis": REDIS_CONFIG,
    "mongodb_atlas": MONGODB_ATLAS_CONFIG,
    "prometheus": PROMETHEUS_CONFIG,
    "grafana": GRAFANA_CONFIG,
    "faiss": FAISS_CONFIG
}

def get_cloud_config(service: str) -> Optional[CloudAPIConfig]:
    """Get cloud service configuration by name"""
    return CLOUD_CONFIGS.get(service.lower())

def get_services_by_type(service_type: CloudServiceType) -> List[CloudAPIConfig]:
    """Get all cloud services of specific type"""
    return [config for config in CLOUD_CONFIGS.values() 
            if config.service_type == service_type]

def get_services_by_provider(provider: str) -> List[CloudAPIConfig]:
    """Get all services from specific cloud provider"""
    return [config for config in CLOUD_CONFIGS.values() 
            if config.provider.lower() == provider.lower()]

def get_storage_services() -> List[CloudAPIConfig]:
    """Get all object storage services"""
    return get_services_by_type(CloudServiceType.OBJECT_STORAGE)

def get_cdn_services() -> List[CloudAPIConfig]:
    """Get all CDN services"""
    return get_services_by_type(CloudServiceType.CDN)

def get_monitoring_services() -> List[CloudAPIConfig]:
    """Get all monitoring services"""
    return get_services_by_type(CloudServiceType.MONITORING)
