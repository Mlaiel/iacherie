"""External Services Configuration Module for IA-Influencer Agent Platform
=======================================================================

Professional configuration for external service integrations including cloud storage,
vector databases, content protection APIs, and third-party service providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseSettings, Field, validator, HttpUrl
from enum import Enum
from dataclasses import dataclass


class ServiceCategory(str, Enum):
    """External service categories."""    CLOUD_STORAGE = "cloud_storage"
    VECTOR_DATABASE = "vector_database"
    SEARCH_ENGINE = "search_engine"
    CONTENT_PROTECTION = "content_protection"
    PAYMENT_PROCESSING = "payment_processing"
    NOTIFICATION_SERVICE = "notification_service"
    MONITORING = "monitoring"
    SECURITY = "security"
    MACHINE_LEARNING = "machine_learning"
    CONTENT_DELIVERY = "content_delivery"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"


class ServiceProvider(str, Enum):
    """External service providers."""    # Cloud Storage
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD_STORAGE = "google_cloud_storage"
    AZURE_BLOB = "azure_blob"
    MINIO = "minio"
    
    # Vector Databases
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    FAISS = "faiss"
    CHROMA = "chroma"
    
    # Search Engines
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    ALGOLIA = "algolia"
    
    # Content Protection
    SHAZAM = "shazam"
    AUDIBLE_MAGIC = "audible_magic"
    CONTENT_ID = "content_id"
    COPYRIGHT_ENGINE = "copyright_engine"
    
    # Payment Processing
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    SQUARE = "square"
    
    # Notification Services
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    TWILIO = "twilio"
    SLACK = "slack"
    DISCORD = "discord"
    
    # Monitoring
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"
    SENTRY = "sentry"
    
    # Machine Learning
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging_face"
    GOOGLE_AI = "google_ai"
    
    # Content Delivery
    CLOUDFLARE = "cloudflare"
    FASTLY = "fastly"
    AWS_CLOUDFRONT = "aws_cloudfront"


@dataclass
class ServiceHealthConfig:
    """Service health check configuration."""    enabled: bool = True
    check_interval: int = 60  # seconds
    timeout: float = 10.0
    retry_attempts: int = 3
    failure_threshold: int = 3
    recovery_threshold: int = 2


@dataclass
class ServiceLimits:
    """Service usage limits configuration."""    max_requests_per_second: float = 10.0
    max_requests_per_hour: int = 3600
    max_payload_size: int = 10485760  # 10MB
    max_concurrent_connections: int = 100


class ExternalServicesConfig(BaseSettings):
    """External services configuration for third-party integrations."""    
    # === CLOUD STORAGE SERVICES ===
    
    # AWS S3
    aws_s3_enabled: bool = Field(default=True, env="AWS_S3_ENABLED")
    aws_s3_bucket_name: str = Field(..., env="AWS_S3_BUCKET_NAME")
    aws_s3_region: str = Field(..., env="AWS_S3_REGION")
    aws_s3_access_key_id: str = Field(..., env="AWS_S3_ACCESS_KEY_ID")
    aws_s3_secret_access_key: str = Field(..., env="AWS_S3_SECRET_ACCESS_KEY")
    aws_s3_endpoint_url: Optional[str] = Field(default=None, env="AWS_S3_ENDPOINT_URL")
    aws_s3_use_ssl: bool = Field(default=True, env="AWS_S3_USE_SSL")
    
    # Google Cloud Storage
    gcs_enabled: bool = Field(default=False, env="GCS_ENABLED")
    gcs_bucket_name: str = Field(..., env="GCS_BUCKET_NAME")
    gcs_project_id: str = Field(..., env="GCS_PROJECT_ID")
    gcs_credentials_path: str = Field(..., env="GCS_CREDENTIALS_PATH")
    
    # Azure Blob Storage
    azure_blob_enabled: bool = Field(default=False, env="AZURE_BLOB_ENABLED")
    azure_storage_account: str = Field(..., env="AZURE_STORAGE_ACCOUNT")
    azure_storage_key: str = Field(..., env="AZURE_STORAGE_KEY")
    azure_container_name: str = Field(..., env="AZURE_CONTAINER_NAME")
    
    # MinIO (Self-hosted S3 compatible)
    minio_enabled: bool = Field(default=False, env="MINIO_ENABLED")
    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(..., env="MINIO_BUCKET_NAME")
    minio_use_ssl: bool = Field(default=False, env="MINIO_USE_SSL")
    
    # === VECTOR DATABASES ===
    
    # Pinecone
    pinecone_enabled: bool = Field(default=True, env="PINECONE_ENABLED")
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(..., env="PINECONE_INDEX_NAME")
    pinecone_dimension: int = Field(default=512, env="PINECONE_DIMENSION")
    
    # Weaviate
    weaviate_enabled: bool = Field(default=False, env="WEAVIATE_ENABLED")
    weaviate_url: str = Field(..., env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    weaviate_class_name: str = Field(default="ContentFingerprint", env="WEAVIATE_CLASS_NAME")
    
    # Qdrant
    qdrant_enabled: bool = Field(default=False, env="QDRANT_ENABLED")
    qdrant_url: str = Field(..., env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="content_vectors", env="QDRANT_COLLECTION_NAME")
    
    # === SEARCH ENGINES ===
    
    # Elasticsearch
    elasticsearch_enabled: bool = Field(default=True, env="ELASTICSEARCH_ENABLED")
    elasticsearch_hosts: List[str] = Field(..., env="ELASTICSEARCH_HOSTS")
    elasticsearch_username: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    elasticsearch_use_ssl: bool = Field(default=True, env="ELASTICSEARCH_USE_SSL")
    elasticsearch_verify_certs: bool = Field(default=True, env="ELASTICSEARCH_VERIFY_CERTS")
    
    # Algolia
    algolia_enabled: bool = Field(default=False, env="ALGOLIA_ENABLED")
    algolia_app_id: str = Field(..., env="ALGOLIA_APP_ID")
    algolia_admin_api_key: str = Field(..., env="ALGOLIA_ADMIN_API_KEY")
    algolia_search_api_key: str = Field(..., env="ALGOLIA_SEARCH_API_KEY")
    algolia_index_name: str = Field(default="content_search", env="ALGOLIA_INDEX_NAME")
    
    # === CONTENT PROTECTION SERVICES ===
    
    # Shazam API
    shazam_enabled: bool = Field(default=True, env="SHAZAM_ENABLED")
    shazam_api_key: str = Field(..., env="SHAZAM_API_KEY")
    shazam_base_url: str = Field(
        default="https://shazam-core.p.rapidapi.com", 
        env="SHAZAM_BASE_URL"
    )
    shazam_rate_limit: int = Field(default=500, env="SHAZAM_RATE_LIMIT")
    
    # Audible Magic
    audible_magic_enabled: bool = Field(default=False, env="AUDIBLE_MAGIC_ENABLED")
    audible_magic_api_key: str = Field(..., env="AUDIBLE_MAGIC_API_KEY")
    audible_magic_base_url: str = Field(..., env="AUDIBLE_MAGIC_BASE_URL")
    
    # Content ID System
    content_id_enabled: bool = Field(default=True, env="CONTENT_ID_ENABLED")
    content_id_api_key: str = Field(..., env="CONTENT_ID_API_KEY")
    content_id_base_url: str = Field(..., env="CONTENT_ID_BASE_URL")
    
    # === PAYMENT PROCESSING ===
    
    # Stripe
    stripe_enabled: bool = Field(default=True, env="STRIPE_ENABLED")
    stripe_publishable_key: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    stripe_base_url: str = Field(default="https://api.stripe.com/v1", env="STRIPE_BASE_URL")
    
    # PayPal
    paypal_enabled: bool = Field(default=True, env="PAYPAL_ENABLED")
    paypal_client_id: str = Field(..., env="PAYPAL_CLIENT_ID")
    paypal_client_secret: str = Field(..., env="PAYPAL_CLIENT_SECRET")
    paypal_base_url: str = Field(..., env="PAYPAL_BASE_URL")  # sandbox or live
    paypal_webhook_id: str = Field(..., env="PAYPAL_WEBHOOK_ID")
    
    # Wise (formerly TransferWise)
    wise_enabled: bool = Field(default=False, env="WISE_ENABLED")
    wise_api_token: str = Field(..., env="WISE_API_TOKEN")
    wise_base_url: str = Field(default="https://api.transferwise.com", env="WISE_BASE_URL")
    
    # === NOTIFICATION SERVICES ===
    
    # SendGrid (Email)
    sendgrid_enabled: bool = Field(default=True, env="SENDGRID_ENABLED")
    sendgrid_api_key: str = Field(..., env="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field(..., env="SENDGRID_FROM_EMAIL")
    sendgrid_from_name: str = Field(default="IA-Influencer Agent", env="SENDGRID_FROM_NAME")
    
    # Mailgun (Email)
    mailgun_enabled: bool = Field(default=False, env="MAILGUN_ENABLED")
    mailgun_api_key: str = Field(..., env="MAILGUN_API_KEY")
    mailgun_domain: str = Field(..., env="MAILGUN_DOMAIN")
    mailgun_base_url: str = Field(default="https://api.mailgun.net/v3", env="MAILGUN_BASE_URL")
    
    # Twilio (SMS)
    twilio_enabled: bool = Field(default=False, env="TWILIO_ENABLED")
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., env="TWILIO_PHONE_NUMBER")
    
    # Slack
    slack_enabled: bool = Field(default=False, env="SLACK_ENABLED")
    slack_webhook_url: str = Field(..., env="SLACK_WEBHOOK_URL")
    slack_channel: str = Field(default="#alerts", env="SLACK_CHANNEL")
    
    # === MONITORING SERVICES ===
    
    # Sentry (Error Tracking)
    sentry_enabled: bool = Field(default=True, env="SENTRY_ENABLED")
    sentry_dsn: str = Field(..., env="SENTRY_DSN")
    sentry_environment: str = Field(default="production", env="SENTRY_ENVIRONMENT")
    sentry_release: Optional[str] = Field(default=None, env="SENTRY_RELEASE")
    sentry_traces_sample_rate: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    
    # Datadog
    datadog_enabled: bool = Field(default=False, env="DATADOG_ENABLED")
    datadog_api_key: str = Field(..., env="DATADOG_API_KEY")
    datadog_app_key: str = Field(..., env="DATADOG_APP_KEY")
    
    # === MACHINE LEARNING SERVICES ===
    
    # OpenAI
    openai_enabled: bool = Field(default=True, env="OPENAI_ENABLED")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    
    # Hugging Face
    huggingface_enabled: bool = Field(default=True, env="HUGGINGFACE_ENABLED")
    huggingface_api_token: str = Field(..., env="HUGGINGFACE_API_TOKEN")
    huggingface_base_url: str = Field(
        default="https://api-inference.huggingface.co", 
        env="HUGGINGFACE_BASE_URL"
    )
    
    # === CDN SERVICES ===
    
    # Cloudflare
    cloudflare_enabled: bool = Field(default=False, env="CLOUDFLARE_ENABLED")
    cloudflare_api_token: str = Field(..., env="CLOUDFLARE_API_TOKEN")
    cloudflare_zone_id: str = Field(..., env="CLOUDFLARE_ZONE_ID")
    
    # === GENERAL SETTINGS ===
    
    # Health checks
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(default=300, env="HEALTH_CHECK_INTERVAL")  # 5 minutes
    
    # Service discovery
    enable_service_discovery: bool = Field(default=True, env="ENABLE_SERVICE_DISCOVERY")
    service_registry_url: Optional[str] = Field(default=None, env="SERVICE_REGISTRY_URL")
    
    # Circuit breaker
    enable_circuit_breaker: bool = Field(default=True, env="ENABLE_CIRCUIT_BREAKER")
    circuit_breaker_failure_threshold: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    
    # Caching
    enable_service_caching: bool = Field(default=True, env="ENABLE_SERVICE_CACHING")
    service_cache_ttl: int = Field(default=3600, env="SERVICE_CACHE_TTL")  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ExternalServiceManager:
    """Manager for external service integrations with health monitoring."""    
    def __init__(self, config: ExternalServicesConfig):
        self.config = config
        self.service_status: Dict[str, bool] = {}
        self.service_configs: Dict[ServiceProvider, Dict[str, Any]] = {}
        self._initialize_service_configs()
    
    def _initialize_service_configs(self):
        """Initialize service configurations."""        # Cloud Storage Services
        if self.config.aws_s3_enabled:
            self.service_configs[ServiceProvider.AWS_S3] = {
                "bucket_name": self.config.aws_s3_bucket_name,
                "region": self.config.aws_s3_region,
                "access_key_id": self.config.aws_s3_access_key_id,
                "secret_access_key": self.config.aws_s3_secret_access_key,
                "endpoint_url": self.config.aws_s3_endpoint_url,
                "use_ssl": self.config.aws_s3_use_ssl
            }
        
        # Vector Databases
        if self.config.pinecone_enabled:
            self.service_configs[ServiceProvider.PINECONE] = {
                "api_key": self.config.pinecone_api_key,
                "environment": self.config.pinecone_environment,
                "index_name": self.config.pinecone_index_name,
                "dimension": self.config.pinecone_dimension
            }
        
        # Search Engines
        if self.config.elasticsearch_enabled:
            self.service_configs[ServiceProvider.ELASTICSEARCH] = {
                "hosts": self.config.elasticsearch_hosts,
                "username": self.config.elasticsearch_username,
                "password": self.config.elasticsearch_password,
                "use_ssl": self.config.elasticsearch_use_ssl,
                "verify_certs": self.config.elasticsearch_verify_certs
            }
        
        # Content Protection
        if self.config.shazam_enabled:
            self.service_configs[ServiceProvider.SHAZAM] = {
                "api_key": self.config.shazam_api_key,
                "base_url": self.config.shazam_base_url,
                "rate_limit": self.config.shazam_rate_limit
            }
        
        # Payment Processing
        if self.config.stripe_enabled:
            self.service_configs[ServiceProvider.STRIPE] = {
                "publishable_key": self.config.stripe_publishable_key,
                "secret_key": self.config.stripe_secret_key,
                "webhook_secret": self.config.stripe_webhook_secret,
                "base_url": self.config.stripe_base_url
            }
        
        # Notification Services
        if self.config.sendgrid_enabled:
            self.service_configs[ServiceProvider.SENDGRID] = {
                "api_key": self.config.sendgrid_api_key,
                "from_email": self.config.sendgrid_from_email,
                "from_name": self.config.sendgrid_from_name
            }
        
        # Machine Learning Services
        if self.config.openai_enabled:
            self.service_configs[ServiceProvider.OPENAI] = {
                "api_key": self.config.openai_api_key,
                "organization": self.config.openai_organization,
                "base_url": self.config.openai_base_url
            }
    
    def get_service_config(self, provider: ServiceProvider) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific service provider."""        return self.service_configs.get(provider)
    
    def is_service_enabled(self, provider: ServiceProvider) -> bool:
        """Check if a service provider is enabled."""        return provider in self.service_configs
    
    def get_enabled_services(self, category: Optional[ServiceCategory] = None) -> List[ServiceProvider]:
        """Get list of enabled services, optionally filtered by category."""        enabled_services = list(self.service_configs.keys())
        
        if category is None:
            return enabled_services
        
        # Filter by category (simplified mapping)
        category_mapping = {
            ServiceCategory.CLOUD_STORAGE: [
                ServiceProvider.AWS_S3, ServiceProvider.GOOGLE_CLOUD_STORAGE,
                ServiceProvider.AZURE_BLOB, ServiceProvider.MINIO
            ],
            ServiceCategory.VECTOR_DATABASE: [
                ServiceProvider.PINECONE, ServiceProvider.WEAVIATE,
                ServiceProvider.QDRANT, ServiceProvider.FAISS
            ],
            ServiceCategory.SEARCH_ENGINE: [
                ServiceProvider.ELASTICSEARCH, ServiceProvider.OPENSEARCH,
                ServiceProvider.ALGOLIA
            ],
            ServiceCategory.CONTENT_PROTECTION: [
                ServiceProvider.SHAZAM, ServiceProvider.AUDIBLE_MAGIC,
                ServiceProvider.CONTENT_ID
            ],
            ServiceCategory.PAYMENT_PROCESSING: [
                ServiceProvider.STRIPE, ServiceProvider.PAYPAL, ServiceProvider.WISE
            ]
        }
        
        category_services = category_mapping.get(category, [])
        return [service for service in enabled_services if service in category_services]
    
    async def check_service_health(self, provider: ServiceProvider) -> bool:
        """Check health status of a specific service."""        # Implementation would include actual health checks
        # This is a placeholder that returns True for configured services
        return provider in self.service_configs
    
    def get_service_limits(self, provider: ServiceProvider) -> ServiceLimits:
        """Get service limits for a specific provider."""        # Default limits - could be customized per provider
        return ServiceLimits()
    
    def get_health_config(self, provider: ServiceProvider) -> ServiceHealthConfig:
        """Get health check configuration for a specific provider."""        return ServiceHealthConfig()


# Global external services configuration instance
external_services_config = ExternalServicesConfig()
external_service_manager = ExternalServiceManager(external_services_config)
