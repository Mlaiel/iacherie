"""
API Gateway Configuration for IA-Influencer Agent Platform
==========================================================

Professional API gateway configuration for microservices architecture.

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
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import re


class AuthenticationType(str, Enum):
    """Authentication types supported by the gateway."""
    NONE = "none"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    MUTUAL_TLS = "mutual_tls"


class RateLimitType(str, Enum):
    """Rate limiting types."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class LoadBalancingMethod(str, Enum):
    """Load balancing methods."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    HEALTH_CHECK = "health_check"


class CacheStrategy(str, Enum):
    """Cache strategies."""
    NO_CACHE = "no_cache"
    CACHE_ALL = "cache_all"
    CACHE_GET_ONLY = "cache_get_only"
    SMART_CACHE = "smart_cache"


@dataclass
class RouteConfig:
    """Route configuration for API gateway."""
    path: str
    methods: List[str] = field(default_factory=lambda: ["GET"])
    upstream: str = ""
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    authentication: AuthenticationType = AuthenticationType.JWT
    rate_limit: Optional[Dict[str, Any]] = None
    cache: Optional[Dict[str, Any]] = None
    cors: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    middleware: List[str] = field(default_factory=list)
    enabled: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class UpstreamConfig:
    """Upstream service configuration."""
    name: str
    servers: List[Dict[str, Any]]
    load_balancing: LoadBalancingMethod = LoadBalancingMethod.ROUND_ROBIN
    health_check: Optional[Dict[str, Any]] = None
    circuit_breaker: Optional[Dict[str, Any]] = None
    ssl: Optional[Dict[str, Any]] = None
    keepalive: Optional[Dict[str, Any]] = None
    timeout: int = 30
    max_fails: int = 3
    fail_timeout: int = 10


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    type: RateLimitType = RateLimitType.SLIDING_WINDOW
    requests: int = 1000
    window: int = 60  # seconds
    burst: int = 100
    key: str = "ip"  # ip, user_id, api_key
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    enabled: bool = True


@dataclass
class CacheConfig:
    """Cache configuration."""
    strategy: CacheStrategy = CacheStrategy.SMART_CACHE
    ttl: int = 300  # seconds
    max_size: int = 10000
    key_pattern: str = "{method}:{path}:{query_hash}"
    vary_headers: List[str] = field(default_factory=list)
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    enabled: bool = True


@dataclass
class CORSConfig:
    """CORS configuration."""
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])
    exposed_headers: List[str] = field(default_factory=list)
    max_age: int = 86400
    credentials: bool = True
    enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    api_key_header: str = "X-API-Key"
    oauth2_token_url: Optional[str] = None
    oauth2_client_id: Optional[str] = None
    oauth2_client_secret: Optional[str] = None
    basic_auth_realm: str = "Protected Area"
    mtls_ca_cert: Optional[str] = None
    mtls_client_cert: Optional[str] = None
    mtls_client_key: Optional[str] = None
    enable_csrf_protection: bool = True
    enable_xss_protection: bool = True
    enable_content_type_validation: bool = True


class APIGatewayConfig(BaseSettings):
    """
    Centralized API gateway configuration for microservices architecture.
    Supports routing, load balancing, authentication, rate limiting, and more.
    """
    
    # Server settings
    host: str = Field("0.0.0.0", env="API_GATEWAY_HOST")
    port: int = Field(8000, env="API_GATEWAY_PORT")
    workers: int = Field(4, env="API_GATEWAY_WORKERS")
    
    # SSL/TLS settings
    ssl_enabled: bool = Field(False, env="API_GATEWAY_SSL_ENABLED")
    ssl_cert_path: Optional[str] = Field(None, env="API_GATEWAY_SSL_CERT_PATH")
    ssl_key_path: Optional[str] = Field(None, env="API_GATEWAY_SSL_KEY_PATH")
    ssl_ca_path: Optional[str] = Field(None, env="API_GATEWAY_SSL_CA_PATH")
    
    # Logging settings
    log_level: str = Field("INFO", env="API_GATEWAY_LOG_LEVEL")
    access_log_enabled: bool = Field(True, env="API_GATEWAY_ACCESS_LOG_ENABLED")
    access_log_format: str = Field("combined", env="API_GATEWAY_ACCESS_LOG_FORMAT")
    
    # Global timeouts
    connect_timeout: int = Field(10, env="API_GATEWAY_CONNECT_TIMEOUT")
    send_timeout: int = Field(60, env="API_GATEWAY_SEND_TIMEOUT")
    read_timeout: int = Field(60, env="API_GATEWAY_READ_TIMEOUT")
    keepalive_timeout: int = Field(75, env="API_GATEWAY_KEEPALIVE_TIMEOUT")
    
    # Buffer settings
    client_max_body_size: str = Field("100M", env="API_GATEWAY_CLIENT_MAX_BODY_SIZE")
    client_body_buffer_size: str = Field("128k", env="API_GATEWAY_CLIENT_BODY_BUFFER_SIZE")
    proxy_buffer_size: str = Field("4k", env="API_GATEWAY_PROXY_BUFFER_SIZE")
    proxy_buffers: str = Field("8 4k", env="API_GATEWAY_PROXY_BUFFERS")
    
    # Connection settings
    worker_connections: int = Field(1024, env="API_GATEWAY_WORKER_CONNECTIONS")
    keepalive_requests: int = Field(100, env="API_GATEWAY_KEEPALIVE_REQUESTS")
    
    # Health check settings
    health_check_enabled: bool = Field(True, env="API_GATEWAY_HEALTH_CHECK_ENABLED")
    health_check_path: str = Field("/health", env="API_GATEWAY_HEALTH_CHECK_PATH")
    health_check_interval: int = Field(30, env="API_GATEWAY_HEALTH_CHECK_INTERVAL")
    
    # Metrics settings
    metrics_enabled: bool = Field(True, env="API_GATEWAY_METRICS_ENABLED")
    metrics_path: str = Field("/metrics", env="API_GATEWAY_METRICS_PATH")
    
    # Rate limiting (global defaults)
    rate_limit_enabled: bool = Field(True, env="API_GATEWAY_RATE_LIMIT_ENABLED")
    default_rate_limit_requests: int = Field(1000, env="API_GATEWAY_DEFAULT_RATE_LIMIT_REQUESTS")
    default_rate_limit_window: int = Field(60, env="API_GATEWAY_DEFAULT_RATE_LIMIT_WINDOW")
    
    # Cache settings (global defaults)
    cache_enabled: bool = Field(True, env="API_GATEWAY_CACHE_ENABLED")
    default_cache_ttl: int = Field(300, env="API_GATEWAY_DEFAULT_CACHE_TTL")
    cache_redis_host: str = Field("localhost", env="API_GATEWAY_CACHE_REDIS_HOST")
    cache_redis_port: int = Field(6379, env="API_GATEWAY_CACHE_REDIS_PORT")
    
    # CORS settings (global defaults)
    cors_enabled: bool = Field(True, env="API_GATEWAY_CORS_ENABLED")
    cors_allowed_origins: List[str] = Field(["*"], env="API_GATEWAY_CORS_ALLOWED_ORIGINS")
    cors_allowed_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
        env="API_GATEWAY_CORS_ALLOWED_METHODS"
    )
    
    # Security settings
    jwt_secret_key: str = Field("your-secret-key", env="API_GATEWAY_JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="API_GATEWAY_JWT_ALGORITHM")
    jwt_expiration: int = Field(3600, env="API_GATEWAY_JWT_EXPIRATION")
    
    # Service discovery
    service_discovery_enabled: bool = Field(True, env="API_GATEWAY_SERVICE_DISCOVERY_ENABLED")
    service_discovery_host: str = Field("localhost", env="API_GATEWAY_SERVICE_DISCOVERY_HOST")
    service_discovery_port: int = Field(8500, env="API_GATEWAY_SERVICE_DISCOVERY_PORT")
    
    # Load balancing
    default_load_balancing: LoadBalancingMethod = Field(
        LoadBalancingMethod.ROUND_ROBIN, 
        env="API_GATEWAY_DEFAULT_LOAD_BALANCING"
    )
    
    # Circuit breaker (global defaults)
    circuit_breaker_enabled: bool = Field(True, env="API_GATEWAY_CIRCUIT_BREAKER_ENABLED")
    circuit_breaker_failure_threshold: int = Field(5, env="API_GATEWAY_CB_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: int = Field(60, env="API_GATEWAY_CB_RECOVERY_TIMEOUT")
    
    class Config:
        env_prefix = "API_GATEWAY_"
        case_sensitive = False
        
    def get_global_rate_limit_config(self) -> RateLimitConfig:
        """Get global rate limiting configuration."""
        return RateLimitConfig(
            requests=self.default_rate_limit_requests,
            window=self.default_rate_limit_window,
            redis_host=self.cache_redis_host,
            redis_port=self.cache_redis_port,
            enabled=self.rate_limit_enabled
        )
    
    def get_global_cache_config(self) -> CacheConfig:
        """Get global cache configuration."""
        return CacheConfig(
            ttl=self.default_cache_ttl,
            redis_host=self.cache_redis_host,
            redis_port=self.cache_redis_port,
            enabled=self.cache_enabled
        )
    
    def get_global_cors_config(self) -> CORSConfig:
        """Get global CORS configuration."""
        return CORSConfig(
            allowed_origins=self.cors_allowed_origins,
            allowed_methods=self.cors_allowed_methods,
            enabled=self.cors_enabled
        )
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            jwt_secret=self.jwt_secret_key,
            jwt_algorithm=self.jwt_algorithm,
            jwt_expiration=self.jwt_expiration
        )


# Pre-configured routes for IA-Influencer Agent microservices
MICROSERVICE_ROUTES = {
    # Authentication routes
    "auth_login": RouteConfig(
        path="/api/v1/auth/login",
        methods=["POST"],
        upstream="auth-service",
        timeout=10,
        authentication=AuthenticationType.NONE,
        rate_limit={"requests": 10, "window": 60, "key": "ip"},
        description="User login endpoint",
        tags=["auth", "public"]
    ),
    "auth_refresh": RouteConfig(
        path="/api/v1/auth/refresh",
        methods=["POST"],
        upstream="auth-service",
        timeout=10,
        authentication=AuthenticationType.JWT,
        description="Token refresh endpoint",
        tags=["auth", "protected"]
    ),
    
    # Spotify Agent routes
    "spotify_profile": RouteConfig(
        path="/api/v1/spotify/profile",
        methods=["GET"],
        upstream="spotify-agent",
        timeout=30,
        cache={"ttl": 300, "vary_headers": ["Authorization"]},
        description="Get Spotify user profile",
        tags=["spotify", "profile"]
    ),
    "spotify_analytics": RouteConfig(
        path="/api/v1/spotify/analytics",
        methods=["GET"],
        upstream="spotify-agent",
        timeout=60,
        cache={"ttl": 600, "vary_headers": ["Authorization"]},
        description="Get Spotify analytics data",
        tags=["spotify", "analytics"]
    ),
    "spotify_recommendations": RouteConfig(
        path="/api/v1/spotify/recommendations",
        methods=["GET", "POST"],
        upstream="spotify-agent",
        timeout=45,
        cache={"ttl": 1800, "vary_headers": ["Authorization"]},
        description="Get AI-powered recommendations",
        tags=["spotify", "ai", "recommendations"]
    ),
    
    # Content Protection routes
    "protection_upload": RouteConfig(
        path="/api/v1/protection/upload",
        methods=["POST"],
        upstream="content-protection",
        timeout=300,  # Long timeout for file uploads
        authentication=AuthenticationType.JWT,
        rate_limit={"requests": 10, "window": 3600, "key": "user_id"},
        description="Upload content for protection",
        tags=["protection", "upload"]
    ),
    "protection_scan": RouteConfig(
        path="/api/v1/protection/scan",
        methods=["POST"],
        upstream="content-protection",
        timeout=120,
        rate_limit={"requests": 50, "window": 3600, "key": "user_id"},
        description="Scan content for violations",
        tags=["protection", "scan"]
    ),
    "protection_violations": RouteConfig(
        path="/api/v1/protection/violations",
        methods=["GET"],
        upstream="content-protection",
        timeout=30,
        cache={"ttl": 300, "vary_headers": ["Authorization"]},
        description="Get detected violations",
        tags=["protection", "violations"]
    ),
    
    # Fingerprinting routes
    "fingerprint_audio": RouteConfig(
        path="/api/v1/fingerprint/audio",
        methods=["POST"],
        upstream="fingerprinting-engine",
        timeout=180,
        rate_limit={"requests": 20, "window": 3600, "key": "user_id"},
        description="Generate audio fingerprint",
        tags=["fingerprint", "audio"]
    ),
    "fingerprint_video": RouteConfig(
        path="/api/v1/fingerprint/video",
        methods=["POST"],
        upstream="fingerprinting-engine",
        timeout=300,
        rate_limit={"requests": 10, "window": 3600, "key": "user_id"},
        description="Generate video fingerprint",
        tags=["fingerprint", "video"]
    ),
    "fingerprint_image": RouteConfig(
        path="/api/v1/fingerprint/image",
        methods=["POST"],
        upstream="fingerprinting-engine",
        timeout=60,
        rate_limit={"requests": 100, "window": 3600, "key": "user_id"},
        description="Generate image fingerprint",
        tags=["fingerprint", "image"]
    ),
    "fingerprint_text": RouteConfig(
        path="/api/v1/fingerprint/text",
        methods=["POST"],
        upstream="fingerprinting-engine",
        timeout=30,
        rate_limit={"requests": 200, "window": 3600, "key": "user_id"},
        description="Generate text fingerprint",
        tags=["fingerprint", "text"]
    ),
    
    # Web Crawler routes
    "crawler_start": RouteConfig(
        path="/api/v1/crawler/start",
        methods=["POST"],
        upstream="web-crawler",
        timeout=10,
        rate_limit={"requests": 5, "window": 3600, "key": "user_id"},
        description="Start web crawling for content",
        tags=["crawler", "monitoring"]
    ),
    "crawler_status": RouteConfig(
        path="/api/v1/crawler/status/{job_id}",
        methods=["GET"],
        upstream="web-crawler",
        timeout=15,
        cache={"ttl": 30, "vary_headers": ["Authorization"]},
        description="Get crawling job status",
        tags=["crawler", "status"]
    ),
    "crawler_results": RouteConfig(
        path="/api/v1/crawler/results/{job_id}",
        methods=["GET"],
        upstream="web-crawler",
        timeout=30,
        cache={"ttl": 300, "vary_headers": ["Authorization"]},
        description="Get crawling results",
        tags=["crawler", "results"]
    ),
    
    # Monetization routes
    "monetization_revenue": RouteConfig(
        path="/api/v1/monetization/revenue",
        methods=["GET"],
        upstream="monetization-engine",
        timeout=45,
        cache={"ttl": 900, "vary_headers": ["Authorization"]},
        description="Get revenue analytics",
        tags=["monetization", "revenue"]
    ),
    "monetization_payouts": RouteConfig(
        path="/api/v1/monetization/payouts",
        methods=["GET", "POST"],
        upstream="monetization-engine",
        timeout=30,
        rate_limit={"requests": 20, "window": 3600, "key": "user_id"},
        description="Manage payouts",
        tags=["monetization", "payouts"]
    ),
    "monetization_licensing": RouteConfig(
        path="/api/v1/monetization/licensing",
        methods=["GET", "POST"],
        upstream="monetization-engine",
        timeout=60,
        rate_limit={"requests": 10, "window": 3600, "key": "user_id"},
        description="Manage content licensing",
        tags=["monetization", "licensing"]
    ),
    
    # Notification routes
    "notifications_list": RouteConfig(
        path="/api/v1/notifications",
        methods=["GET"],
        upstream="notification-service",
        timeout=15,
        cache={"ttl": 60, "vary_headers": ["Authorization"]},
        description="Get user notifications",
        tags=["notifications", "list"]
    ),
    "notifications_mark_read": RouteConfig(
        path="/api/v1/notifications/{notification_id}/read",
        methods=["PUT"],
        upstream="notification-service",
        timeout=10,
        description="Mark notification as read",
        tags=["notifications", "update"]
    ),
    "notifications_websocket": RouteConfig(
        path="/api/v1/notifications/ws",
        methods=["GET"],
        upstream="notification-service",
        timeout=0,  # No timeout for WebSocket
        authentication=AuthenticationType.JWT,
        description="WebSocket notifications",
        tags=["notifications", "websocket"]
    ),
    
    # Analytics routes
    "analytics_dashboard": RouteConfig(
        path="/api/v1/analytics/dashboard",
        methods=["GET"],
        upstream="analytics-engine",
        timeout=60,
        cache={"ttl": 300, "vary_headers": ["Authorization"]},
        description="Get analytics dashboard data",
        tags=["analytics", "dashboard"]
    ),
    "analytics_reports": RouteConfig(
        path="/api/v1/analytics/reports",
        methods=["GET", "POST"],
        upstream="analytics-engine",
        timeout=120,
        rate_limit={"requests": 20, "window": 3600, "key": "user_id"},
        description="Generate analytics reports",
        tags=["analytics", "reports"]
    ),
    "analytics_metrics": RouteConfig(
        path="/api/v1/analytics/metrics",
        methods=["GET"],
        upstream="analytics-engine",
        timeout=45,
        cache={"ttl": 180, "vary_headers": ["Authorization"]},
        description="Get metrics data",
        tags=["analytics", "metrics"]
    ),
    
    # Admin routes
    "admin_health": RouteConfig(
        path="/api/v1/admin/health",
        methods=["GET"],
        upstream="api-gateway",
        timeout=10,
        authentication=AuthenticationType.API_KEY,
        description="System health check",
        tags=["admin", "health"]
    ),
    "admin_metrics": RouteConfig(
        path="/api/v1/admin/metrics",
        methods=["GET"],
        upstream="api-gateway",
        timeout=15,
        authentication=AuthenticationType.API_KEY,
        cache={"ttl": 60},
        description="System metrics",
        tags=["admin", "metrics"]
    )
}

# Pre-configured upstreams for IA-Influencer Agent microservices
MICROSERVICE_UPSTREAMS = {
    "auth-service": UpstreamConfig(
        name="auth-service",
        servers=[
            {"host": "localhost", "port": 8000, "weight": 100},
            {"host": "localhost", "port": 8080, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.ROUND_ROBIN,
        health_check={
            "path": "/health",
            "interval": 30,
            "timeout": 5,
            "healthy_threshold": 2,
            "unhealthy_threshold": 3
        },
        circuit_breaker={
            "failure_threshold": 5,
            "recovery_timeout": 30,
            "success_threshold": 3
        }
    ),
    "spotify-agent": UpstreamConfig(
        name="spotify-agent",
        servers=[
            {"host": "localhost", "port": 8001, "weight": 100},
            {"host": "localhost", "port": 8081, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.LEAST_CONNECTIONS,
        health_check={
            "path": "/health",
            "interval": 30,
            "timeout": 10,
            "healthy_threshold": 2,
            "unhealthy_threshold": 3
        }
    ),
    "content-protection": UpstreamConfig(
        name="content-protection",
        servers=[
            {"host": "localhost", "port": 8002, "weight": 150},
            {"host": "localhost", "port": 8082, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.WEIGHTED_ROUND_ROBIN,
        timeout=120
    ),
    "fingerprinting-engine": UpstreamConfig(
        name="fingerprinting-engine",
        servers=[
            {"host": "localhost", "port": 8003, "weight": 200},
            {"host": "localhost", "port": 8083, "weight": 150},
            {"host": "localhost", "port": 8084, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.HEALTH_CHECK,
        timeout=300
    ),
    "web-crawler": UpstreamConfig(
        name="web-crawler",
        servers=[
            {"host": "localhost", "port": 8004, "weight": 100},
            {"host": "localhost", "port": 8085, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.IP_HASH
    ),
    "monetization-engine": UpstreamConfig(
        name="monetization-engine",
        servers=[
            {"host": "localhost", "port": 8005, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.ROUND_ROBIN
    ),
    "notification-service": UpstreamConfig(
        name="notification-service",
        servers=[
            {"host": "localhost", "port": 8006, "weight": 100},
            {"host": "localhost", "port": 8086, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.ROUND_ROBIN
    ),
    "analytics-engine": UpstreamConfig(
        name="analytics-engine",
        servers=[
            {"host": "localhost", "port": 8007, "weight": 100},
            {"host": "localhost", "port": 8087, "weight": 100}
        ],
        load_balancing=LoadBalancingMethod.ROUND_ROBIN
    )
}


# Export configuration instance
api_gateway_config = APIGatewayConfig()
