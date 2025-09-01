"""Integration & Microservices Configuration Module

Advanced integration configuration for microservices architecture, API management,
external service connections, and enterprise-grade system integration.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected intellectual property. Unauthorized use is prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """
Types of microservices"""

    GATEWAY = "gateway"
    AUTH = "auth"
    USER_MANAGEMENT = "user_management"
    CONTENT_PROCESSING = "content_processing"
    AI_SERVICES = "ai_services"
    PROTECTION = "protection"
    SEO = "seo"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    STORAGE = "storage"
    CDN = "cdn"
    SEARCH = "search"
    COLLABORATION = "collaboration"
    STREAMING = "streaming"


class IntegrationType(Enum):
    """Types of external integrations"""

    PAYMENT_GATEWAY = "payment_gateway"
    SOCIAL_MEDIA = "social_media"
    CLOUD_STORAGE = "cloud_storage"
    CDN_PROVIDER = "cdn_provider"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    BLOCKCHAIN = "blockchain"
    AI_SERVICE = "ai_service"
    ANALYTICS_SERVICE = "analytics_service"
    MONITORING = "monitoring"
    LOGGING = "logging"
    BACKUP = "backup"


class CommunicationProtocol(Enum):
    """Communication protocols between services"""

    REST_API = "rest_api"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAMING = "event_streaming"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"


@dataclass
class ServiceEndpoint:
    """Configuration for service endpoints"""
    name: str
    url: str
    protocol: CommunicationProtocol
    authentication_required: bool = True
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    rate_limit_per_minute: int = 1000
    health_check_enabled: bool = True
    health_check_endpoint: str = "/health"
    health_check_interval_seconds: int = 60
    load_balancing_enabled: bool = False
    circuit_breaker_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300


@dataclass
class MicroserviceConfig:
    """Configuration for individual microservices"""
    service_name: str
    service_type: ServiceType
    version: str = "1.0.0"
    
    # Deployment settings
    replicas: int = 3
    min_replicas: int = 1
    max_replicas: int = 10
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    
    # Network settings
    port: int = 8080
    internal_port: int = 8080
    protocol: str = "HTTP"
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    required_services: List[str] = field(default_factory=list)
    
    # Configuration
    environment_variables: Dict[str, str] = field(default_factory=dict)
    config_files: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    
    # Monitoring
    health_check_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    logging_level: str = "INFO"
    
    # Scaling
    auto_scaling_enabled: bool = True
    cpu_threshold_percent: int = 70
    memory_threshold_percent: int = 80
    
    # Security
    security_enabled: bool = True
    tls_enabled: bool = True
    authentication_required: bool = True


@dataclass
class APIGatewayConfig:
    """Configuration for API Gateway"""
    enabled: bool = True
    
    # Gateway settings
    gateway_port: int = 80
    admin_port: int = 8001
    
    # Rate limiting
    global_rate_limit: int = 10000  # requests per minute
    per_user_rate_limit: int = 1000  # requests per minute
    
    # Authentication
    jwt_authentication: bool = True
    api_key_authentication: bool = True
    oauth2_enabled: bool = True
    
    # Load balancing
    load_balancer_algorithm: str = "round_robin"  # round_robin, least_connections, ip_hash
    health_checks_enabled: bool = True
    
    # Caching
    response_caching: bool = True
    cache_ttl_seconds: int = 300
    cache_size_mb: int = 512
    
    # Logging and monitoring
    access_logging: bool = True
    error_logging: bool = True
    metrics_collection: bool = True
    
    # CORS
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class MessageQueueConfig:
    """Configuration for message queuing system"""
    enabled: bool = True
    provider: str = "redis"  # redis, rabbitmq, kafka
    
    # Connection settings
    host: str = "localhost"
    port: int = 6379
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Queue settings
    default_queue: str = "ia_influencer_default"
    priority_queue: str = "ia_influencer_priority"
    dead_letter_queue: str = "ia_influencer_dlq"
    
    # Performance settings
    max_connections: int = 20
    connection_timeout: int = 10
    message_ttl_seconds: int = 3600
    max_retries: int = 3
    
    # Monitoring
    metrics_enabled: bool = True
    dead_letter_monitoring: bool = True


@dataclass
class DatabaseIntegrationConfig:
    """Configuration for database integrations"""
    
    # Primary database
    primary_db_type: str = "postgresql"
    primary_db_host: str = "localhost"
    primary_db_port: int = 5432
    primary_db_name: str = "ia_influencer"
    primary_db_pool_size: int = 20
    
    # Cache database
    cache_db_type: str = "redis"
    cache_db_host: str = "localhost"
    cache_db_port: int = 6379
    cache_db_ttl: int = 3600
    
    # Analytics database
    analytics_db_type: str = "clickhouse"
    analytics_db_host: str = "localhost"
    analytics_db_port: int = 8123
    
    # Search database
    search_db_type: str = "elasticsearch"
    search_db_host: str = "localhost"
    search_db_port: int = 9200
    search_db_index_prefix: str = "ia_influencer"
    
    # Connection pooling
    connection_pool_enabled: bool = True
    max_connections_per_service: int = 50
    connection_timeout_seconds: int = 30
    
    # Backup and replication
    backup_enabled: bool = True
    backup_interval_hours: int = 6
    replication_enabled: bool = True
    read_replicas: int = 2


@dataclass
class ExternalIntegrationConfig:
    """Configuration for external service integrations"""
    
    # Payment providers
    stripe_enabled: bool = True
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    paypal_enabled: bool = True
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    
    # Social media platforms
    youtube_api_key: Optional[str] = None
    instagram_api_key: Optional[str] = None
    tiktok_api_key: Optional[str] = None
    twitter_api_key: Optional[str] = None
    
    # Cloud storage
    aws_s3_enabled: bool = True
    aws_s3_bucket: str = "ia-influencer-content"
    aws_s3_region: str = "us-east-1"
    aws_s3_access_key: Optional[str] = None
    aws_s3_secret_key: Optional[str] = None
    
    # CDN
    cloudflare_enabled: bool = True
    cloudflare_zone_id: Optional[str] = None
    cloudflare_api_token: Optional[str] = None
    
    # AI services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    
    # Email service
    sendgrid_enabled: bool = True
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: str = "noreply@ia-influencer.com"
    
    # SMS service
    twilio_enabled: bool = True
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Monitoring services
    datadog_enabled: bool = True
    datadog_api_key: Optional[str] = None
    
    newrelic_enabled: bool = False
    newrelic_api_key: Optional[str] = None


@dataclass
class SecurityIntegrationConfig:
    """Configuration for security integrations"""
    
    # Certificate management
    ssl_enabled: bool = True
    ssl_provider: str = "letsencrypt"  # letsencrypt, custom, cloudflare
    auto_renewal: bool = True
    
    # Web Application Firewall
    waf_enabled: bool = True
    waf_provider: str = "cloudflare"  # cloudflare, aws_waf, custom
    
    # DDoS protection
    ddos_protection: bool = True
    ddos_provider: str = "cloudflare"
    
    # Security scanning
    vulnerability_scanning: bool = True
    dependency_scanning: bool = True
    code_scanning: bool = True
    
    # Compliance
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    soc2_compliance: bool = False
    iso27001_compliance: bool = False
    
    # Audit logging
    audit_logging_enabled: bool = True
    audit_log_retention_days: int = 365
    audit_log_encryption: bool = True


@dataclass
class MonitoringIntegrationConfig:
    """Configuration for monitoring and observability"""
    
    # Metrics collection
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    metrics_retention_days: int = 90
    
    # Log aggregation
    log_aggregation_enabled: bool = True
    log_aggregation_provider: str = "elasticsearch"  # elasticsearch, splunk, datadog
    log_retention_days: int = 30
    
    # Distributed tracing
    tracing_enabled: bool = True
    tracing_provider: str = "jaeger"  # jaeger, zipkin, datadog
    trace_sampling_rate: float = 0.1
    
    # Alerting
    alerting_enabled: bool = True
    alerting_provider: str = "prometheus"  # prometheus, datadog, pagerduty
    alert_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    
    # Health checks
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 10
    
    # Performance monitoring
    apm_enabled: bool = True
    apm_provider: str = "elastic_apm"  # elastic_apm, datadog, newrelic
    
    # Uptime monitoring
    uptime_monitoring: bool = True
    uptime_check_interval_minutes: int = 5
    uptime_check_locations: List[str] = field(default_factory=lambda: ["us-east", "eu-west", "asia-pacific"])


@dataclass
class IntegrationConfig:
    """Master integration configuration"""
    
    # Core settings
    enabled: bool = True
    environment: str = "production"  # development, staging, production
    
    # Service discovery
    service_discovery_enabled: bool = True
    service_registry: str = "consul"  # consul, etcd, kubernetes
    
    # Configuration management
    config_management: str = "kubernetes_configmap"  # kubernetes_configmap, consul_kv, etcd
    secret_management: str = "kubernetes_secrets"  # kubernetes_secrets, vault, aws_secrets
    
    # Components
    microservices: Dict[str, MicroserviceConfig] = field(default_factory=dict)
    api_gateway: APIGatewayConfig = field(default_factory=APIGatewayConfig)
    message_queue: MessageQueueConfig = field(default_factory=MessageQueueConfig)
    database_integration: DatabaseIntegrationConfig = field(default_factory=DatabaseIntegrationConfig)
    external_integration: ExternalIntegrationConfig = field(default_factory=ExternalIntegrationConfig)
    security_integration: SecurityIntegrationConfig = field(default_factory=SecurityIntegrationConfig)
    monitoring_integration: MonitoringIntegrationConfig = field(default_factory=MonitoringIntegrationConfig)
    
    def add_microservice(self, service_name: str, service_type: ServiceType, config: MicroserviceConfig):
        """Add microservice configuration"""
        self.microservices[service_name] = config
        logger.info(f"Added microservice: {service_name} of type {service_type.value}")
    
    def get_service_endpoints(self) -> Dict[str, ServiceEndpoint]:
        """Get all service endpoints"""
        endpoints = {}
        
        for service_name, config in self.microservices.items():
            endpoint = ServiceEndpoint(
                name=service_name,
                url=f"http://{service_name}:{config.port}",
                protocol=CommunicationProtocol.REST_API,
                timeout_seconds=30
            )
            endpoints[service_name] = endpoint
        
        return endpoints
    
    def validate_configuration(self) -> List[str]:
        """Validate integration configuration"""
        issues = []
        
        # Check required services
        required_services = [
            ServiceType.AUTH,
            ServiceType.USER_MANAGEMENT,
            ServiceType.CONTENT_PROCESSING,
            ServiceType.AI_SERVICES
        ]
        
        configured_types = {config.service_type for config in self.microservices.values()}
        
        for required_service in required_services:
            if required_service not in configured_types:
                issues.append(f"Required service {required_service.value} not configured")
        
        # Check external integrations
        if not self.external_integration.stripe_enabled and not self.external_integration.paypal_enabled:
            issues.append("No payment provider configured")
        
        if not self.external_integration.aws_s3_enabled:
            issues.append("No cloud storage configured")
        
        # Check monitoring
        if not self.monitoring_integration.metrics_collection:
            issues.append("Metrics collection not enabled")
        
        if not self.monitoring_integration.health_check_enabled:
            issues.append("Health checks not enabled")
        
        return issues
    
    def get_deployment_manifest(self) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifest"""
        manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "ia-influencer-agent",
                "labels": {
                    "creator": "fahed-mlaiel",
                    "environment": self.environment
                }
            }
        }
        
        # Add services to manifest
        services = []
        for service_name, config in self.microservices.items():
            service_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": service_name,
                    "namespace": "ia-influencer-agent"
                },
                "spec": {
                    "replicas": config.replicas,
                    "selector": {
                        "matchLabels": {
                            "app": service_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": service_name
                            }
                        },
                        "spec": {
                            "containers": [{
                                "name": service_name,
                                "image": f"ia-influencer/{service_name}:{config.version}",
                                "ports": [{
                                    "containerPort": config.internal_port
                                }],
                                "resources": {
                                    "limits": {
                                        "cpu": config.cpu_limit,
                                        "memory": config.memory_limit
                                    }
                                }
                            }]
                        }
                    }
                }
            }
            services.append(service_manifest)
        
        manifest["services"] = services
        return manifest


# Initialize default microservices
def create_default_microservices() -> Dict[str, MicroserviceConfig]:
    """Create default microservice configurations"""
    services = {}
    
    # API Gateway
    services["api-gateway"] = MicroserviceConfig(
        service_name="api-gateway",
        service_type=ServiceType.GATEWAY,
        port=80,
        replicas=3,
        dependencies=["auth-service", "user-management"]
    )
    
    # Auth Service
    services["auth-service"] = MicroserviceConfig(
        service_name="auth-service",
        service_type=ServiceType.AUTH,
        port=8001,
        replicas=3
    )
    
    # User Management
    services["user-management"] = MicroserviceConfig(
        service_name="user-management",
        service_type=ServiceType.USER_MANAGEMENT,
        port=8002,
        dependencies=["auth-service"]
    )
    
    # Content Processing
    services["content-processing"] = MicroserviceConfig(
        service_name="content-processing",
        service_type=ServiceType.CONTENT_PROCESSING,
        port=8003,
        cpu_limit="1000m",
        memory_limit="2Gi",
        dependencies=["ai-services", "storage-service"]
    )
    
    # AI Services
    services["ai-services"] = MicroserviceConfig(
        service_name="ai-services",
        service_type=ServiceType.AI_SERVICES,
        port=8004,
        cpu_limit="2000m",
        memory_limit="4Gi",
        replicas=5
    )
    
    # Protection Service
    services["protection-service"] = MicroserviceConfig(
        service_name="protection-service",
        service_type=ServiceType.PROTECTION,
        port=8005,
        dependencies=["ai-services", "content-processing"]
    )
    
    # SEO Service
    services["seo-service"] = MicroserviceConfig(
        service_name="seo-service",
        service_type=ServiceType.SEO,
        port=8006,
        dependencies=["ai-services", "content-processing"]
    )
    
    # Monetization Service
    services["monetization-service"] = MicroserviceConfig(
        service_name="monetization-service",
        service_type=ServiceType.MONETIZATION,
        port=8007,
        dependencies=["user-management", "analytics-service"]
    )
    
    # Analytics Service
    services["analytics-service"] = MicroserviceConfig(
        service_name="analytics-service",
        service_type=ServiceType.ANALYTICS,
        port=8008,
        memory_limit="4Gi"
    )
    
    # Notification Service
    services["notification-service"] = MicroserviceConfig(
        service_name="notification-service",
        service_type=ServiceType.NOTIFICATION,
        port=8009,
        dependencies=["user-management"]
    )
    
    # Storage Service
    services["storage-service"] = MicroserviceConfig(
        service_name="storage-service",
        service_type=ServiceType.STORAGE,
        port=8010,
        memory_limit="1Gi"
    )
    
    return services


# Create global integration configuration
integration_config = IntegrationConfig(
    microservices=create_default_microservices()
)

# Export all components
__all__ = [
    'ServiceType',
    'IntegrationType',
    'CommunicationProtocol',
    'ServiceEndpoint',
    'MicroserviceConfig',
    'APIGatewayConfig',
    'MessageQueueConfig',
    'DatabaseIntegrationConfig',
    'ExternalIntegrationConfig',
    'SecurityIntegrationConfig',
    'MonitoringIntegrationConfig',
    'IntegrationConfig',
    'integration_config'
]
