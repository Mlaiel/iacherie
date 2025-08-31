"""API Gateway Agent Configuration

Enterprise-level configuration management for API Gateway with environment-specific
settings, security parameters, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""import os
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, validator
from enum import Enum


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies for service distribution"""    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    HEALTH_BASED = "health_based"


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies for API protection"""    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class APIGatewayConfig(BaseSettings):
    """Comprehensive API Gateway configuration"""    
    # Core Settings
    service_name: str = "api-gateway-agent"
    version: str = "1.0.0"
    environment: str = "production"
    debug: bool = False
    
    # Network Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    max_connections: int = 10000
    keep_alive: int = 75
    
    # Security Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    api_key_header: str = "X-API-Key"
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Rate Limiting Configuration
    rate_limit_strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    default_rate_limit: int = 1000  # requests per minute
    burst_limit: int = 100  # burst allowance
    rate_limit_window: int = 60  # seconds
    
    # Circuit Breaker Configuration
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60
    circuit_breaker_expected_exception: str = "requests.RequestException"
    
    # Load Balancing Configuration
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5    # seconds
    health_check_retries: int = 3
    
    # Service Discovery Configuration
    service_registry_url: str = "http://consul:8500"
    service_discovery_enabled: bool = True
    service_health_check_endpoint: str = "/health"
    
    # Cache Configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300  # 5 minutes
    cache_prefix: str = "api_gateway"
    
    # Monitoring Configuration
    metrics_enabled: bool = True
    metrics_port: int = 9090
    prometheus_endpoint: str = "/metrics"
    jaeger_endpoint: str = "http://jaeger:14268/api/traces"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    access_log_enabled: bool = True
    error_log_enabled: bool = True
    
    # Request/Response Configuration
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_response_size: int = 50 * 1024 * 1024  # 50MB
    request_timeout: int = 30  # seconds
    response_timeout: int = 60  # seconds
    
    # Retry Configuration
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    retry_status_codes: List[int] = [500, 502, 503, 504]
    
    # Service Routes Configuration
    service_routes: Dict[str, Dict[str, Any]] = {
        "audio_agent": {
            "path_prefix": "/api/v1/audio",
            "upstream": "http://audio-service:8001",
            "weight": 10,
            "health_check": True,
            "timeout": 30,
            "retries": 3
        },
        "music_agent": {
            "path_prefix": "/api/v1/music",
            "upstream": "http://music-service:8002",
            "weight": 10,
            "health_check": True,
            "timeout": 30,
            "retries": 3
        },
        "content_agent": {
            "path_prefix": "/api/v1/content",
            "upstream": "http://content-service:8003",
            "weight": 10,
            "health_check": True,
            "timeout": 30,
            "retries": 3
        },
        "protection_agent": {
            "path_prefix": "/api/v1/protection",
            "upstream": "http://protection-service:8004",
            "weight": 15,
            "health_check": True,
            "timeout": 45,
            "retries": 5
        },
        "monetization_agent": {
            "path_prefix": "/api/v1/monetization",
            "upstream": "http://monetization-service:8005",
            "weight": 12,
            "health_check": True,
            "timeout": 60,
            "retries": 3
        },
        "collaboration_agent": {
            "path_prefix": "/api/v1/collaboration",
            "upstream": "http://collaboration-service:8006",
            "weight": 8,
            "health_check": True,
            "timeout": 30,
            "retries": 3
        },
        "analytics_agent": {
            "path_prefix": "/api/v1/analytics",
            "upstream": "http://analytics-service:8007",
            "weight": 10,
            "health_check": True,
            "timeout": 45,
            "retries": 3
        },
        "seo_agent": {
            "path_prefix": "/api/v1/seo",
            "upstream": "http://seo-service:8008",
            "weight": 8,
            "health_check": True,
            "timeout": 30,
            "retries": 3
        }
    }
    
    # Authentication Bypass Paths
    auth_bypass_paths: List[str] = [
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh"
    ]
    
    # Request Transformation Rules
    request_transformations: Dict[str, Dict[str, Any]] = {
        "add_headers": {
            "X-Gateway-Version": version,
            "X-Request-ID": "auto-generate",
            "X-Forwarded-Proto": "https"
        },
        "remove_headers": [
            "Server",
            "X-Powered-By"
        ]
    }
    
    # Response Transformation Rules
    response_transformations: Dict[str, Dict[str, Any]] = {
        "add_headers": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        },
        "remove_headers": [
            "Server",
            "X-Powered-By"
        ]
    }
    
    # WebSocket Configuration
    websocket_enabled: bool = True
    websocket_path: str = "/ws"
    websocket_max_connections: int = 1000
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # SSL Configuration
    ssl_enabled: bool = False
    ssl_cert_path: str = "/etc/ssl/certs/api_gateway.crt"
    ssl_key_path: str = "/etc/ssl/private/api_gateway.key"
    ssl_verify_mode: str = "CERT_REQUIRED"
    
    @validator('service_routes')
    def validate_service_routes(cls, v):
        """Validate service routes configuration"""        required_fields = ['path_prefix', 'upstream', 'weight']
        for service_name, config in v.items():
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Service '{service_name}' missing required field: {field}")
            
            # Validate weight
            if not isinstance(config['weight'], int) or config['weight'] < 1:
                raise ValueError(f"Service '{service_name}' weight must be positive integer")
            
            # Validate upstream URL format
            upstream = config['upstream']
            if not upstream.startswith(('http://', 'https://')):
                raise ValueError(f"Service '{service_name}' upstream must be valid URL")
        
        return v
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        """Validate CORS origins"""        if isinstance(v, str):
            return [v]
        return v
    
    class Config:
        env_prefix = "API_GATEWAY_"
        env_file = ".env"
        case_sensitive = False
