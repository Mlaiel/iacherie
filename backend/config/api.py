"""API Configuration Module - Consolidated API Configs
====================================================

Consolidates all API-related configurations from:
- config/apis/ (18 files)
- config/microservices/ (22 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os

# ===== API ENDPOINTS CONFIGURATION =====

class HTTPMethod(str, Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class APIVersion(str, Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    BETA = "beta"
    ALPHA = "alpha"

@dataclass
class EndpointConfig:
    """Individual endpoint configuration"""
    path: str
    methods: List[HTTPMethod]
    version: APIVersion = APIVersion.V1
    auth_required: bool = True
    rate_limit_per_minute: int = 60
    cache_ttl: int = 300  # 5 minutes
    timeout_seconds: int = 30
    requires_premium: bool = False
    deprecated: bool = False
    documentation: str = ""

@dataclass
class APIEndpointsConfig:
    """API endpoints configuration"""
    base_url: str = "/api"
    default_version: APIVersion = APIVersion.V1
    versioning_strategy: str = "url_path"  # url_path, header, query_param
    endpoints: List[EndpointConfig] = field(default_factory=list)
    enable_swagger: bool = True
    enable_redoc: bool = True
    enable_openapi: bool = True
    cors_enabled: bool = True

# ===== MIDDLEWARE CONFIGURATION =====

@dataclass
class MiddlewareConfig:
    """API middleware configuration"""
    authentication_enabled: bool = True
    authorization_enabled: bool = True
    rate_limiting_enabled: bool = True
    request_logging_enabled: bool = True
    response_compression_enabled: bool = True
    cors_enabled: bool = True
    csrf_protection_enabled: bool = True
    request_validation_enabled: bool = True
    response_validation_enabled: bool = False
    error_handling_enabled: bool = True

# ===== MICROSERVICES CONFIGURATION =====

class ServiceType(str, Enum):
    """Microservice types"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization" 
    CONTENT_ANALYSIS = "content_analysis"
    FINGERPRINTING = "fingerprinting"
    MONETIZATION = "monetization"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    SEARCH = "search"
    RECOMMENDATION = "recommendation"

class CommunicationProtocol(str, Enum):
    """Service communication protocols"""
    HTTP = "http"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"

@dataclass
class ServiceEndpoint:
    """Microservice endpoint"""
    host: str
    port: int
    protocol: CommunicationProtocol = CommunicationProtocol.HTTP
    health_check_path: str = "/health"
    metrics_path: str = "/metrics"
    ssl_enabled: bool = False

@dataclass
class ServiceConfig:
    """Individual microservice configuration"""
    name: str
    service_type: ServiceType
    endpoint: ServiceEndpoint
    version: str = "1.0.0"
    timeout_seconds: int = 30
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True
    load_balancing_enabled: bool = True
    auto_scaling_enabled: bool = False
    min_instances: int = 1
    max_instances: int = 10

@dataclass
class MicroservicesConfig:
    """Microservices configuration"""
    enabled: bool = True
    service_discovery_enabled: bool = True
    service_mesh_enabled: bool = False
    services: List[ServiceConfig] = field(default_factory=list)
    default_protocol: CommunicationProtocol = CommunicationProtocol.HTTP
    load_balancer_type: str = "round_robin"  # round_robin, least_connections, weighted
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

# ===== AUTHENTICATION & AUTHORIZATION =====

@dataclass
class OAuthConfig:
    """OAuth configuration"""
    enabled: bool = True
    providers: Dict[str, Dict[str, str]] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=lambda: ["openid", "email", "profile"])
    redirect_uri: str = "/auth/callback"
    state_verification: bool = True
    pkce_enabled: bool = True

@dataclass
class JWTConfig:
    """JWT configuration"""
    enabled: bool = True
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "ia-influencer-agent"
    audience: str = "ia-influencer-users"
    verify_signature: bool = True
    verify_exp: bool = True
    verify_iat: bool = True

# ===== VALIDATION CONFIGURATION =====

class ValidationStrategy(str, Enum):
    """Validation strategies"""
    PYDANTIC = "pydantic"
    JSONSCHEMA = "jsonschema"
    MARSHMALLOW = "marshmallow"
    CERBERUS = "cerberus"

@dataclass
class ValidationConfig:
    """Request/response validation configuration"""
    enabled: bool = True
    strategy: ValidationStrategy = ValidationStrategy.PYDANTIC
    validate_requests: bool = True
    validate_responses: bool = False
    strict_mode: bool = True
    custom_validators: Dict[str, str] = field(default_factory=dict)
    error_format: str = "detailed"  # simple, detailed, minimal

# ===== SERIALIZATION CONFIGURATION =====

class SerializationFormat(str, Enum):
    """Serialization formats"""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    AVRO = "avro"

@dataclass
class SerializationConfig:
    """Data serialization configuration"""
    default_format: SerializationFormat = SerializationFormat.JSON
    supported_formats: List[SerializationFormat] = field(default_factory=lambda: [
        SerializationFormat.JSON,
        SerializationFormat.XML
    ])
    pretty_print: bool = False
    include_null_values: bool = False
    date_format: str = "iso"
    compression_enabled: bool = False

# ===== WEBSOCKETS CONFIGURATION =====

@dataclass
class WebSocketConfig:
    """WebSocket configuration"""
    enabled: bool = True
    path: str = "/ws"
    max_connections: int = 1000
    heartbeat_interval: int = 30
    message_size_limit: int = 1048576  # 1MB
    compression_enabled: bool = True
    auth_required: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

# ===== GRAPHQL CONFIGURATION =====

@dataclass
class GraphQLConfig:
    """GraphQL configuration"""
    enabled: bool = False
    path: str = "/graphql"
    playground_enabled: bool = True
    introspection_enabled: bool = True
    query_depth_limit: int = 10
    query_complexity_limit: int = 1000
    timeout_seconds: int = 30
    caching_enabled: bool = True
    subscriptions_enabled: bool = True

# ===== DOCUMENTATION CONFIGURATION =====

@dataclass
class APIDocumentationConfig:
    """API documentation configuration"""
    enabled: bool = True
    swagger_enabled: bool = True
    redoc_enabled: bool = True
    swagger_path: str = "/docs"
    redoc_path: str = "/redoc"
    openapi_path: str = "/openapi.json"
    title: str = "IA-Influencer Agent API"
    description: str = "AI-powered content protection and monetization platform"
    version: str = "1.0.0"
    contact_email: str = "mlaiel@live.de"
    license_name: str = "Proprietary"

# ===== VERSIONING CONFIGURATION =====

@dataclass
class APIVersioningConfig:
    """API versioning configuration"""
    enabled: bool = True
    strategy: str = "url_path"  # url_path, header, query_param, accept_header
    default_version: APIVersion = APIVersion.V1
    supported_versions: List[APIVersion] = field(default_factory=lambda: [
        APIVersion.V1,
        APIVersion.V2
    ])
    deprecation_warnings: bool = True
    sunset_dates: Dict[str, str] = field(default_factory=dict)

# ===== TESTING CONFIGURATION =====

@dataclass
class APITestingConfig:
    """API testing configuration"""
    enabled: bool = True
    test_data_generation: bool = True
    mock_external_services: bool = True
    load_testing_enabled: bool = False
    performance_monitoring: bool = True
    test_coverage_threshold: float = 80.0
    automated_testing: bool = True
    contract_testing: bool = True

# ===== MONITORING & METRICS =====

@dataclass
class APIMonitoringConfig:
    """API monitoring configuration"""
    enabled: bool = True
    metrics_collection: bool = True
    distributed_tracing: bool = True
    error_tracking: bool = True
    performance_monitoring: bool = True
    uptime_monitoring: bool = True
    alerts_enabled: bool = True
    dashboard_enabled: bool = True
    log_requests: bool = True
    log_responses: bool = False

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_api_config() -> Dict[str, Any]:
    """Get development API configuration"""
    return {
        "endpoints": APIEndpointsConfig(
            enable_swagger=True,
            enable_redoc=True,
            cors_enabled=True
        ),
        "middleware": MiddlewareConfig(
            rate_limiting_enabled=False,
            csrf_protection_enabled=False
        ),
        "microservices": MicroservicesConfig(
            enabled=False,  # Monolithic in dev
            service_discovery_enabled=False
        ),
        "jwt": JWTConfig(
            secret_key="dev-secret-key",
            access_token_expire_minutes=60
        ),
        "validation": ValidationConfig(
            strict_mode=False
        ),
        "documentation": APIDocumentationConfig(
            playground_enabled=True,
            introspection_enabled=True
        ),
        "monitoring": APIMonitoringConfig(
            log_requests=True,
            log_responses=True
        )
    }

def get_production_api_config() -> Dict[str, Any]:
    """Get production API configuration"""
    return {
        "endpoints": APIEndpointsConfig(
            enable_swagger=False,  # Disable in production
            enable_redoc=False,
            cors_enabled=True
        ),
        "middleware": MiddlewareConfig(
            rate_limiting_enabled=True,
            csrf_protection_enabled=True
        ),
        "microservices": MicroservicesConfig(
            enabled=True,
            service_discovery_enabled=True,
            service_mesh_enabled=True
        ),
        "jwt": JWTConfig(
            secret_key=os.getenv("JWT_SECRET_KEY", "change-me"),
            access_token_expire_minutes=15
        ),
        "validation": ValidationConfig(
            strict_mode=True,
            validate_responses=True
        ),
        "documentation": APIDocumentationConfig(
            enabled=False  # No docs in production
        ),
        "monitoring": APIMonitoringConfig(
            log_requests=True,
            log_responses=False,
            alerts_enabled=True
        )
    }

def get_testing_api_config() -> Dict[str, Any]:
    """Get testing API configuration"""
    return {
        "endpoints": APIEndpointsConfig(
            enable_swagger=False,
            enable_redoc=False,
            cors_enabled=True
        ),
        "middleware": MiddlewareConfig(
            authentication_enabled=False,
            rate_limiting_enabled=False
        ),
        "microservices": MicroservicesConfig(
            enabled=False
        ),
        "jwt": JWTConfig(
            secret_key="test-secret-key",
            access_token_expire_minutes=120
        ),
        "validation": ValidationConfig(
            strict_mode=True
        ),
        "testing": APITestingConfig(
            mock_external_services=True,
            test_data_generation=True
        ),
        "monitoring": APIMonitoringConfig(
            enabled=False
        )
    }

# ===== API CONFIGURATION FACTORY =====

class APIConfigurationFactory:
    """Factory for creating API configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create API configuration for environment"""
        if environment.lower() == "production":
            return get_production_api_config()
        elif environment.lower() == "testing":
            return get_testing_api_config()
        else:
            return get_development_api_config()

# Export all API configurations
__all__ = [
    # Enums
    "HTTPMethod",
    "APIVersion",
    "ServiceType",
    "CommunicationProtocol",
    "ValidationStrategy",
    "SerializationFormat",
    
    # Configuration Classes
    "EndpointConfig",
    "APIEndpointsConfig",
    "MiddlewareConfig",
    "ServiceEndpoint",
    "ServiceConfig",
    "MicroservicesConfig",
    "OAuthConfig",
    "JWTConfig",
    "ValidationConfig",
    "SerializationConfig",
    "WebSocketConfig",
    "GraphQLConfig",
    "APIDocumentationConfig",
    "APIVersioningConfig",
    "APITestingConfig",
    "APIMonitoringConfig",
    
    # Factory and Functions
    "APIConfigurationFactory",
    "get_development_api_config",
    "get_production_api_config", 
    "get_testing_api_config"
]