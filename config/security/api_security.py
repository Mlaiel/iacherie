"""API Security Configuration Module
=================================

Advanced API security configuration for IA Influencer Agent platform.
Provides comprehensive API protection, security headers, input validation,
and API gateway security configurations.

Business Logic Integration:
- Creator API security for content operations
- Platform integration API protection  
- Revenue API security for financial operations
- Content protection API security measures

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class SecurityHeaderType(Enum):
    """Types of security headers."""    CONTENT_SECURITY_POLICY = "content_security_policy"
    STRICT_TRANSPORT_SECURITY = "strict_transport_security"
    X_CONTENT_TYPE_OPTIONS = "x_content_type_options"
    X_FRAME_OPTIONS = "x_frame_options"
    X_XSS_PROTECTION = "x_xss_protection"
    REFERRER_POLICY = "referrer_policy"
    PERMISSIONS_POLICY = "permissions_policy"
    CROSS_ORIGIN_EMBEDDER_POLICY = "cross_origin_embedder_policy"
    CROSS_ORIGIN_OPENER_POLICY = "cross_origin_opener_policy"
    CROSS_ORIGIN_RESOURCE_POLICY = "cross_origin_resource_policy"


class InputValidationType(Enum):
    """Types of input validation."""    SCHEMA_VALIDATION = "schema_validation"
    TYPE_VALIDATION = "type_validation"
    RANGE_VALIDATION = "range_validation"
    FORMAT_VALIDATION = "format_validation"
    SANITIZATION = "sanitization"
    ENCODING_VALIDATION = "encoding_validation"
    SIZE_VALIDATION = "size_validation"
    PATTERN_VALIDATION = "pattern_validation"


class ApiEndpointSecurity(Enum):
    """API endpoint security levels."""    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ELEVATED = "elevated"
    RESTRICTED = "restricted"


@dataclass
class SecurityHeaders:
    """Security headers configuration."""    
    # Content Security Policy
    content_security_policy: Dict[str, List[str]] = field(default_factory=lambda: {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "connect-src": ["'self'", "https://api.ia-influencer.com"],
        "media-src": ["'self'", "https://cdn.ia-influencer.com"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],
        "upgrade-insecure-requests": []
    })
    
    # HTTP Strict Transport Security
    strict_transport_security: Dict[str, Any] = field(default_factory=lambda: {
        "max_age": 31536000,  # 1 year
        "include_subdomains": True,
        "preload": True
    })
    
    # X-Content-Type-Options
    x_content_type_options: str = "nosniff"
    
    # X-Frame-Options
    x_frame_options: str = "DENY"
    
    # X-XSS-Protection
    x_xss_protection: str = "1; mode=block"
    
    # Referrer Policy
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    permissions_policy: Dict[str, List[str]] = field(default_factory=lambda: {
        "geolocation": ["'none'"],
        "microphone": ["'none'"],
        "camera": ["'none'"],
        "payment": ["'self'"],
        "usb": ["'none'"],
        "magnetometer": ["'none'"],
        "gyroscope": ["'none'"],
        "speaker": ["'self'"]
    })
    
    # Cross-Origin headers
    cross_origin_embedder_policy: str = "require-corp"
    cross_origin_opener_policy: str = "same-origin"
    cross_origin_resource_policy: str = "same-origin"
    
    # Custom security headers
    custom_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-API-Version": "v1",
        "X-Security-Contact": "security@ia-influencer.com",
        "X-Content-Duration": "86400"
    })


@dataclass
class CorsConfiguration:
    """Cross-Origin Resource Sharing (CORS) configuration."""    
    # Allowed origins
    allowed_origins: List[str] = field(default_factory=lambda: [
        "https://app.ia-influencer.com",
        "https://dashboard.ia-influencer.com",
        "https://creator.ia-influencer.com"
    ])
    
    # Allowed methods
    allowed_methods: List[str] = field(default_factory=lambda: [
        "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
    ])
    
    # Allowed headers
    allowed_headers: List[str] = field(default_factory=lambda: [
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "X-API-Key",
        "X-Creator-ID",
        "X-Platform-Token",
        "X-Request-ID"
    ])
    
    # Exposed headers
    exposed_headers: List[str] = field(default_factory=lambda: [
        "X-Total-Count",
        "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset",
        "X-Request-ID"
    ])
    
    # CORS settings
    allow_credentials: bool = True
    max_age: int = 86400  # 24 hours
    
    # Development settings
    allow_all_origins: bool = False  # Only for development
    preflight_cache_duration: int = 3600


@dataclass
class InputValidationRules:
    """Input validation rules configuration."""    
    # String validation
    string_validation: Dict[str, Any] = field(default_factory=lambda: {
        "max_length": 10000,
        "min_length": 1,
        "allowed_characters": r"^[a-zA-Z0-9\s\-_.,!?@#$%&*()+=\[\]{}|\\:;\"'<>/~`]+$",
        "sanitize_html": True,
        "strip_whitespace": True,
        "normalize_unicode": True
    })
    
    # Numeric validation
    numeric_validation: Dict[str, Any] = field(default_factory=lambda: {
        "integer_range": {"min": -2147483648, "max": 2147483647},
        "float_precision": 10,
        "allow_negative": True,
        "allow_zero": True
    })
    
    # File validation
    file_validation: Dict[str, Any] = field(default_factory=lambda: {
        "max_size_mb": 100,
        "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif", ".mp3", ".mp4", ".wav", ".txt"],
        "mime_type_validation": True,
        "malware_scanning": True,
        "metadata_extraction": True
    })
    
    # URL validation
    url_validation: Dict[str, Any] = field(default_factory=lambda: {
        "allowed_schemes": ["http", "https"],
        "allow_localhost": False,
        "max_length": 2048,
        "domain_whitelist": [],
        "domain_blacklist": ["localhost", "127.0.0.1", "10.0.0.0/8"]
    })
    
    # Email validation
    email_validation: Dict[str, Any] = field(default_factory=lambda: {
        "regex_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "max_length": 254,
        "domain_validation": True,
        "disposable_email_check": True
    })
    
    # JSON validation
    json_validation: Dict[str, Any] = field(default_factory=lambda: {
        "max_depth": 10,
        "max_keys": 1000,
        "max_array_length": 10000,
        "schema_validation": True,
        "additional_properties": False
    })


@dataclass
class ApiAuthenticationSecurity:
    """API authentication security configuration."""    
    # JWT security
    jwt_security: Dict[str, Any] = field(default_factory=lambda: {
        "algorithm": "RS256",
        "issuer_validation": True,
        "audience_validation": True,
        "expiration_validation": True,
        "not_before_validation": True,
        "signature_validation": True,
        "claim_validation": True,
        "leeway_seconds": 10
    })
    
    # API key security
    api_key_security: Dict[str, Any] = field(default_factory=lambda: {
        "key_length": 64,
        "key_entropy_bits": 256,
        "key_rotation_days": 90,
        "usage_tracking": True,
        "rate_limiting": True,
        "ip_whitelisting": False,
        "scope_limitations": True
    })
    
    # OAuth2 security
    oauth2_security: Dict[str, Any] = field(default_factory=lambda: {
        "token_introspection": True,
        "scope_validation": True,
        "client_validation": True,
        "pkce_required": True,
        "state_validation": True,
        "redirect_uri_validation": True
    })
    
    # Session security
    session_security: Dict[str, Any] = field(default_factory=lambda: {
        "secure_cookies": True,
        "httponly_cookies": True,
        "samesite_cookies": "Strict",
        "session_timeout": 3600,  # 1 hour
        "idle_timeout": 1800,     # 30 minutes
        "concurrent_session_limit": 5
    })
    
    # Multi-factor authentication
    mfa_security: Dict[str, Any] = field(default_factory=lambda: {
        "required_for_sensitive_operations": True,
        "totp_window": 30,
        "backup_codes": True,
        "rate_limiting": True,
        "max_attempts": 3
    })


@dataclass
class ApiEndpointProtection:
    """API endpoint protection configuration."""    
    # Endpoint security levels
    endpoint_security_levels: Dict[str, ApiEndpointSecurity] = field(default_factory=lambda: {
        "/api/v1/auth/login": ApiEndpointSecurity.PUBLIC,
        "/api/v1/auth/register": ApiEndpointSecurity.PUBLIC,
        "/api/v1/content/upload": ApiEndpointSecurity.AUTHENTICATED,
        "/api/v1/fingerprint/*": ApiEndpointSecurity.AUTHORIZED,
        "/api/v1/revenue/*": ApiEndpointSecurity.ELEVATED,
        "/api/v1/admin/*": ApiEndpointSecurity.RESTRICTED,
        "/api/v1/platform/connect": ApiEndpointSecurity.AUTHENTICATED
    })
    
    # Request size limits
    request_size_limits: Dict[str, int] = field(default_factory=lambda: {
        "/api/v1/content/upload": 100 * 1024 * 1024,  # 100MB
        "/api/v1/auth/*": 1024,                        # 1KB
        "/api/v1/revenue/*": 10 * 1024,               # 10KB
        "default": 1 * 1024 * 1024                     # 1MB
    })
    
    # Rate limiting by endpoint
    endpoint_rate_limits: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "/api/v1/auth/login": {
            "requests_per_minute": 5,
            "requests_per_hour": 20,
            "burst_limit": 10
        },
        "/api/v1/content/upload": {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "size_limit_mb": 100
        },
        "/api/v1/platform/*": {
            "requests_per_minute": 30,
            "requests_per_hour": 500
        }
    })
    
    # Input validation by endpoint
    endpoint_validation: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "/api/v1/content/upload": {
            "file_validation": True,
            "metadata_validation": True,
            "content_scanning": True,
            "virus_scanning": True
        },
        "/api/v1/revenue/*": {
            "financial_data_validation": True,
            "amount_validation": True,
            "currency_validation": True,
            "encryption_required": True
        },
        "/api/v1/platform/*": {
            "token_validation": True,
            "scope_validation": True,
            "platform_specific_validation": True
        }
    })
    
    # Response security
    response_security: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "/api/v1/revenue/*": {
            "sensitive_data_masking": True,
            "encryption": True,
            "audit_logging": True
        },
        "/api/v1/admin/*": {
            "access_logging": True,
            "response_filtering": True,
            "data_classification": True
        }
    })


@dataclass
class ApiGatewaySecurity:
    """API Gateway security configuration."""    
    # Request filtering
    request_filtering: Dict[str, Any] = field(default_factory=lambda: {
        "sql_injection_protection": True,
        "xss_protection": True,
        "command_injection_protection": True,
        "path_traversal_protection": True,
        "remote_file_inclusion_protection": True,
        "ldap_injection_protection": True,
        "xml_external_entity_protection": True
    })
    
    # DDoS protection
    ddos_protection: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "connection_limit": 1000,
        "request_rate_limit": 100,  # per second
        "geographic_filtering": True,
        "bot_detection": True,
        "captcha_challenge": True
    })
    
    # IP filtering
    ip_filtering: Dict[str, Any] = field(default_factory=lambda: {
        "whitelist_enabled": False,
        "blacklist_enabled": True,
        "geoblocking_enabled": True,
        "tor_blocking": True,
        "vpn_detection": True,
        "proxy_detection": True
    })
    
    # Load balancing security
    load_balancer_security: Dict[str, Any] = field(default_factory=lambda: {
        "health_check_authentication": True,
        "ssl_termination": True,
        "backend_encryption": True,
        "session_affinity": True,
        "failover_protection": True
    })
    
    # Web Application Firewall (WAF)
    waf_configuration: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "rule_engine": "modsecurity",
        "owasp_core_rules": True,
        "custom_rules": True,
        "anomaly_scoring": True,
        "blocking_mode": True,
        "logging_enabled": True
    })


@dataclass
class ApiMonitoringSecurity:
    """API monitoring and security analytics configuration."""    
    # Request monitoring
    request_monitoring: Dict[str, Any] = field(default_factory=lambda: {
        "all_requests_logged": True,
        "response_time_tracking": True,
        "error_rate_tracking": True,
        "success_rate_tracking": True,
        "user_agent_analysis": True,
        "ip_reputation_checking": True
    })
    
    # Security event detection
    security_event_detection: Dict[str, Any] = field(default_factory=lambda: {
        "brute_force_detection": True,
        "privilege_escalation_detection": True,
        "data_exfiltration_detection": True,
        "anomalous_behavior_detection": True,
        "attack_pattern_recognition": True,
        "bot_behavior_detection": True
    })
    
    # Alerting configuration
    alerting_config: Dict[str, Any] = field(default_factory=lambda: {
        "real_time_alerts": True,
        "alert_channels": ["email", "slack", "webhook"],
        "alert_thresholds": {
            "error_rate_percent": 5,
            "response_time_ms": 5000,
            "failed_auth_per_minute": 10,
            "suspicious_requests_per_minute": 50
        },
        "escalation_rules": True
    })
    
    # Metrics collection
    metrics_collection: Dict[str, Any] = field(default_factory=lambda: {
        "prometheus_metrics": True,
        "custom_metrics": True,
        "business_metrics": True,
        "security_metrics": True,
        "performance_metrics": True,
        "retention_days": 90
    })


@dataclass
class ApiDocumentationSecurity:
    """API documentation and disclosure security."""    
    # Documentation access
    documentation_access: Dict[str, Any] = field(default_factory=lambda: {
        "public_documentation": True,
        "authenticated_documentation": True,
        "sensitive_endpoint_redaction": True,
        "example_data_sanitization": True,
        "security_information_filtering": True
    })
    
    # OpenAPI security
    openapi_security: Dict[str, Any] = field(default_factory=lambda: {
        "security_schemes": True,
        "scope_documentation": True,
        "authentication_examples": True,
        "error_response_documentation": True,
        "rate_limiting_documentation": True
    })
    
    # Information disclosure prevention
    disclosure_prevention: Dict[str, Any] = field(default_factory=lambda: {
        "server_information_hiding": True,
        "error_message_sanitization": True,
        "debug_information_filtering": True,
        "stack_trace_removal": True,
        "internal_url_hiding": True
    })


@dataclass
class ApiSecurityConfig:
    """Main API security configuration container."""    
    # Core security configurations
    security_headers: SecurityHeaders = field(default_factory=SecurityHeaders)
    cors: CorsConfiguration = field(default_factory=CorsConfiguration)
    input_validation: InputValidationRules = field(default_factory=InputValidationRules)
    authentication: ApiAuthenticationSecurity = field(default_factory=ApiAuthenticationSecurity)
    endpoint_protection: ApiEndpointProtection = field(default_factory=ApiEndpointProtection)
    gateway_security: ApiGatewaySecurity = field(default_factory=ApiGatewaySecurity)
    monitoring: ApiMonitoringSecurity = field(default_factory=ApiMonitoringSecurity)
    documentation: ApiDocumentationSecurity = field(default_factory=ApiDocumentationSecurity)
    
    # Global API security settings
    api_security_enabled: bool = True
    strict_mode: bool = True
    debug_mode: bool = False  # Never enable in production
    
    # API versioning security
    versioning_security: Dict[str, Any] = field(default_factory=lambda: {
        "version_enforcement": True,
        "deprecated_version_warnings": True,
        "sunset_date_headers": True,
        "version_specific_security": True
    })
    
    # Content type security
    content_type_security: Dict[str, Any] = field(default_factory=lambda: {
        "strict_content_type_checking": True,
        "allowed_content_types": [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain"
        ],
        "charset_enforcement": "UTF-8",
        "content_length_validation": True
    })
    
    # Error handling security
    error_handling: Dict[str, Any] = field(default_factory=lambda: {
        "generic_error_messages": True,
        "error_code_mapping": True,
        "stack_trace_suppression": True,
        "security_event_logging": True,
        "error_rate_limiting": True
    })
    
    # Cache security
    cache_security: Dict[str, Any] = field(default_factory=lambda: {
        "no_cache_sensitive_data": True,
        "cache_control_headers": True,
        "etag_validation": True,
        "private_caching_only": True
    })


# Default configuration instance
api_security_config = ApiSecurityConfig()


def get_api_security_config() -> ApiSecurityConfig:
    """Get the API security configuration instance."""    return api_security_config


def get_endpoint_security_level(endpoint: str) -> ApiEndpointSecurity:
    """Get security level for a specific endpoint."""    config = get_api_security_config()
    
    # Check exact match first
    if endpoint in config.endpoint_protection.endpoint_security_levels:
        return config.endpoint_protection.endpoint_security_levels[endpoint]
    
    # Check wildcard matches
    for pattern, level in config.endpoint_protection.endpoint_security_levels.items():
        if pattern.endswith("*") and endpoint.startswith(pattern[:-1]):
            return level
    
    # Default to authenticated
    return ApiEndpointSecurity.AUTHENTICATED


def get_endpoint_rate_limit(endpoint: str) -> Dict[str, Any]:
    """Get rate limit configuration for a specific endpoint."""    config = get_api_security_config()
    
    # Check exact match first
    if endpoint in config.endpoint_protection.endpoint_rate_limits:
        return config.endpoint_protection.endpoint_rate_limits[endpoint]
    
    # Check wildcard matches
    for pattern, limits in config.endpoint_protection.endpoint_rate_limits.items():
        if pattern.endswith("*") and endpoint.startswith(pattern[:-1]):
            return limits
    
    # Return default rate limits
    return {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "burst_limit": 10
    }


def generate_csp_header(csp_config: Dict[str, List[str]]) -> str:
    """Generate Content Security Policy header string."""    directives = []
    for directive, sources in csp_config.items():
        if sources:
            directives.append(f"{directive} {' '.join(sources)}")
        else:
            directives.append(directive)
    return "; ".join(directives)


def validate_api_security_config(config: ApiSecurityConfig) -> bool:
    """Validate API security configuration settings."""    # Validate CORS origins
    for origin in config.cors.allowed_origins:
        if not origin.startswith(("http://", "https://")):
            raise ValueError(f"Invalid CORS origin: {origin}")
    
    # Validate input validation ranges
    string_val = config.input_validation.string_validation
    if string_val["min_length"] > string_val["max_length"]:
        raise ValueError("String min_length cannot be greater than max_length")
    
    # Validate file size limits
    if config.input_validation.file_validation["max_size_mb"] <= 0:
        raise ValueError("File max size must be positive")
    
    # Validate security headers
    if config.security_headers.strict_transport_security["max_age"] <= 0:
        raise ValueError("HSTS max-age must be positive")
    
    return True
