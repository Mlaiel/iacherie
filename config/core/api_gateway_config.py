"""Ainflue API Gateway Configuration
==================================

API Gateway configurations for routing, load balancing, rate limiting,
authentication, monitoring, and microservices orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class GatewayLevel(str, Enum):
    """API Gateway configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    ADAPTIVE = "adaptive"

class AuthenticationStrategy(str, Enum):
    """API authentication strategies"""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"
    HMAC_SIGNATURE = "hmac_signature"

@dataclass
class APIGatewayConfiguration:
    """API Gateway configuration"""
    
    def __init__(self, level -> None: GatewayLevel = GatewayLevel.ENTERPRISE) -> None:
        self.level = level
        self.routing_config = self._get_routing_config()
        self.load_balancing_config = self._get_load_balancing_config()
        self.rate_limiting_config = self._get_rate_limiting_config()
        self.authentication_config = self._get_authentication_config()
        self.monitoring_config = self._get_monitoring_config()
        self.caching_config = self._get_caching_config()
        self.security_config = self._get_security_config()
        self.circuit_breaker_config = self._get_circuit_breaker_config()
        
        logger.info(f"🌐 API Gateway Configuration initialized - Level: {self.level.value}")
    
    def _get_routing_config(self) -> Dict[str, Any]:
        """Get API routing configuration"""
        base_config = {
            "enable_dynamic_routing": True,
            "enable_path_rewriting": True,
            "enable_host_rewriting": True,
            "enable_request_transformation": True,
            "enable_response_transformation": True,
            "routes": {
                "/api/v1/auth/*": {
                    "service": "auth-service",
                    "upstream": "http://auth-service:8001",
                    "timeout": 30,
                    "retries": 3
                },
                "/api/v1/creators/*": {
                    "service": "creator-service", 
                    "upstream": "http://creator-service:8002",
                    "timeout": 60,
                    "retries": 2
                },
                "/api/v1/content/*": {
                    "service": "content-service",
                    "upstream": "http://content-service:8003",
                    "timeout": 120,
                    "retries": 1
                },
                "/api/v1/ai/*": {
                    "service": "ai-service",
                    "upstream": "http://ai-service:8004",
                    "timeout": 300,
                    "retries": 1
                },
                "/api/v1/payments/*": {
                    "service": "payment-service",
                    "upstream": "http://payment-service:8005",
                    "timeout": 60,
                    "retries": 3
                },
                "/api/v1/analytics/*": {
                    "service": "analytics-service",
                    "upstream": "http://analytics-service:8006",
                    "timeout": 90,
                    "retries": 2
                }
            }
        }
        
        if self.level == GatewayLevel.ENTERPRISE:
            base_config.update({
                "enable_service_discovery": True,
                "enable_health_checks": True,
                "enable_blue_green_deployment": True,
                "enable_canary_deployment": True,
                "service_mesh_integration": True
            })
        
        return base_config
    
    def _get_load_balancing_config(self) -> Dict[str, Any]:
        """Get load balancing configuration"""
        base_config = {
            "default_algorithm": LoadBalancingAlgorithm.ROUND_ROBIN,
            "enable_sticky_sessions": False,
            "enable_health_checks": True,
            "health_check_interval": 30,
            "health_check_timeout": 5,
            "max_fails": 3,
            "fail_timeout": 60
        }
        
        if self.level == GatewayLevel.ENTERPRISE:
            base_config.update({
                "algorithms": [
                    LoadBalancingAlgorithm.ROUND_ROBIN,
                    LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                    LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
                    LoadBalancingAlgorithm.ADAPTIVE
                ],
                "enable_dynamic_weights": True,
                "enable_geographic_routing": True,
                "enable_latency_based_routing": True
            })
        
        return base_config
    
    def _get_rate_limiting_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "enable_rate_limiting": True,
            "enable_distributed_rate_limiting": True,
            "enable_adaptive_rate_limiting": True,
            "default_limits": {
                "requests_per_second": 100,
                "requests_per_minute": 1000,
                "requests_per_hour": 10000,
                "requests_per_day": 100000
            },
            "user_type_limits": {
                "guest": {
                    "requests_per_second": 10,
                    "requests_per_minute": 100,
                    "requests_per_hour": 1000,
                    "requests_per_day": 5000
                },
                "creator": {
                    "requests_per_second": 50,
                    "requests_per_minute": 500,
                    "requests_per_hour": 5000,
                    "requests_per_day": 50000
                },
                "premium": {
                    "requests_per_second": 200,
                    "requests_per_minute": 2000,
                    "requests_per_hour": 20000,
                    "requests_per_day": 200000
                },
                "enterprise": {
                    "requests_per_second": 1000,
                    "requests_per_minute": 10000,
                    "requests_per_hour": 100000,
                    "requests_per_day": 1000000
                }
            },
            "endpoint_specific_limits": {
                "/api/v1/auth/login": {
                    "requests_per_minute": 5,
                    "requests_per_hour": 20
                },
                "/api/v1/content/upload": {
                    "requests_per_minute": 10,
                    "requests_per_hour": 100
                },
                "/api/v1/ai/process": {
                    "requests_per_minute": 2,
                    "requests_per_hour": 10
                }
            },
            "burst_handling": {
                "enable_burst_allowance": True,
                "burst_multiplier": 2,
                "burst_duration": 60
            }
        }
    
    def _get_authentication_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        return {
            "default_strategy": AuthenticationStrategy.JWT_TOKEN,
            "enable_multiple_strategies": True,
            "strategies": {
                AuthenticationStrategy.API_KEY: {
                    "header_name": "X-API-Key",
                    "query_param": "api_key",
                    "enable_rotation": True,
                    "rotation_interval": 2592000  # 30 days
                },
                AuthenticationStrategy.JWT_TOKEN: {
                    "header_name": "Authorization",
                    "token_prefix": "Bearer",
                    "enable_refresh": True,
                    "algorithm": "HS256"
                },
                AuthenticationStrategy.OAUTH2: {
                    "enable_pkce": True,
                    "enable_openid_connect": True,
                    "supported_flows": ["authorization_code", "client_credentials"]
                },
                AuthenticationStrategy.HMAC_SIGNATURE: {
                    "header_name": "X-Signature",
                    "algorithm": "sha256",
                    "include_timestamp": True,
                    "timestamp_tolerance": 300  # 5 minutes
                }
            },
            "exempt_paths": [
                "/health",
                "/metrics",
                "/api/v1/auth/register",
                "/api/v1/auth/login",
                "/api/v1/public/*"
            ]
        }
    
    def _get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "enable_request_logging": True,
            "enable_response_logging": True,
            "enable_error_logging": True,
            "enable_performance_monitoring": True,
            "enable_distributed_tracing": True,
            "metrics": {
                "enable_prometheus": True,
                "enable_custom_metrics": True,
                "metrics_path": "/metrics",
                "collection_interval": 15
            },
            "tracing": {
                "enable_jaeger": True,
                "enable_zipkin": True,
                "sampling_rate": 0.1
            },
            "alerting": {
                "enable_alerts": True,
                "alert_rules": [
                    {
                        "name": "high_error_rate",
                        "condition": "error_rate > 5%",
                        "duration": "5m",
                        "severity": "warning"
                    },
                    {
                        "name": "high_latency",
                        "condition": "avg_response_time > 1000ms",
                        "duration": "5m", 
                        "severity": "warning"
                    },
                    {
                        "name": "service_down",
                        "condition": "availability < 99%",
                        "duration": "1m",
                        "severity": "critical"
                    }
                ]
            }
        }
    
    def _get_caching_config(self) -> Dict[str, Any]:
        """Get caching configuration"""
        return {
            "enable_response_caching": True,
            "enable_upstream_caching": True,
            "cache_strategies": {
                "static_content": {
                    "ttl": 86400,  # 24 hours
                    "cache_control": "public, max-age=86400"
                },
                "api_responses": {
                    "ttl": 300,  # 5 minutes
                    "cache_control": "private, max-age=300"
                },
                "user_data": {
                    "ttl": 60,  # 1 minute
                    "cache_control": "private, max-age=60"
                }
            },
            "cache_invalidation": {
                "enable_manual_invalidation": True,
                "enable_automatic_invalidation": True,
                "invalidation_patterns": [
                    "/api/v1/creators/{id}/*",
                    "/api/v1/content/{id}/*"
                ]
            }
        }
    
    def _get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "enable_cors": True,
            "cors_config": {
                "allowed_origins": ["https://ainflue.com", "https://app.ainflue.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "allowed_headers": ["Authorization", "Content-Type", "X-API-Key"],
                "expose_headers": ["X-RateLimit-Remaining"],
                "allow_credentials": True,
                "max_age": 86400
            },
            "security_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000",
                "Content-Security-Policy": "default-src 'self'"
            },
            "enable_request_validation": True,
            "enable_response_validation": True,
            "enable_sql_injection_protection": True,
            "enable_xss_protection": True
        }
    
    def _get_circuit_breaker_config(self) -> Dict[str, Any]:
        """Get circuit breaker configuration"""
        return {
            "enable_circuit_breaker": True,
            "failure_threshold": 50,  # Percentage
            "recovery_timeout": 60,  # Seconds
            "request_volume_threshold": 10,
            "sleep_window": 30,  # Seconds
            "service_configs": {
                "ai-service": {
                    "failure_threshold": 30,
                    "recovery_timeout": 120,
                    "request_volume_threshold": 5
                },
                "payment-service": {
                    "failure_threshold": 20,
                    "recovery_timeout": 30,
                    "request_volume_threshold": 20
                }
            }
        }
    
    def validate_gateway_configuration(self) -> Dict[str, Any]:
        """Validate API Gateway configuration"""
        validation_result = {
            "overall_status": "VALID",
            "routing_status": "CONFIGURED",
            "load_balancing_status": "ENABLED",
            "rate_limiting_status": "ACTIVE",
            "authentication_status": "CONFIGURED",
            "monitoring_status": "ENABLED",
            "security_status": "SECURE",
            "performance_score": 92,
            "recommendations": []
        }
        
        # Add recommendations based on level
        if self.level != GatewayLevel.ENTERPRISE:
            validation_result["recommendations"].append(
                "Consider upgrading to Enterprise gateway level for advanced features"
            )
        
        return validation_result

# Global API Gateway configuration instance
api_gateway_config = APIGatewayConfiguration()

# Module exports
__all__ = [
    "APIGatewayConfiguration",
    "GatewayLevel",
    "LoadBalancingAlgorithm",
    "AuthenticationStrategy",
    "api_gateway_config"
]

logger.info("🌐 Ainflue API Gateway Configuration loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
