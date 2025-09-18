"""
🔗 INTEGRATION CONFIGURATION - AINFLUE ENTERPRISE PLATFORM

Ultra-advanced integration configuration for external services and APIs
Performance Target: < 10ms integration setup

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY SOFTWARE - COMMERCIAL USE PROHIBITED WITHOUT LICENSE
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import ssl
from urllib.parse import urljoin
import jwt

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Types of integrations supported"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"
    DATABASE = "database"
    FILE_STORAGE = "file_storage"
    STREAMING = "streaming"

class AuthenticationType(Enum):
    """Authentication types for integrations"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    CUSTOM = "custom"

@dataclass
class RetryPolicy:
    """Retry policy configuration for failed requests"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Optional[str] = None

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_second: int = 100
    requests_per_minute: int = 6000
    requests_per_hour: int = 360000
    burst_size: int = 50

@dataclass
class APIIntegrationConfig:
    """Configuration for API integrations"""
    name: str
    base_url: str
    integration_type: IntegrationType
    auth_type: AuthenticationType
    timeout: float = 30.0
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    headers: Dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    enabled: bool = True

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    enabled: bool = True
    mesh_type: str = "istio"  # istio, linkerd, consul_connect
    mtls_enabled: bool = True
    load_balancing: str = "round_robin"  # round_robin, least_conn, weighted
    health_check_enabled: bool = True
    health_check_interval: int = 30
    circuit_breaker_enabled: bool = True
    retry_enabled: bool = True
    timeout_enabled: bool = True

@dataclass
class MessageQueueConfig:
    """Message queue integration configuration"""
    broker_type: str = "rabbitmq"  # rabbitmq, kafka, redis, sqs
    connection_url: str = "amqp://localhost:5672"
    exchange: str = "ainflue_exchange"
    routing_key: str = "workflow"
    durable: bool = True
    auto_delete: bool = False
    prefetch_count: int = 10
    connection_pool_size: int = 10

class IntegrationConfig:
    """
    Enterprise integration configuration manager
    Performance target: < 10ms integration setup
    """
    
    def __init__(self):
        self.api_integrations: Dict[str, APIIntegrationConfig] = {}
        self.service_mesh = ServiceMeshConfig()
        self.message_queue = MessageQueueConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        self._integration_registry: Dict[str, Dict[str, Any]] = {}
        self._health_status: Dict[str, bool] = {}
        
        # Initialize default integrations
        self._setup_default_integrations()
    
    def _setup_default_integrations(self):
        """Setup default platform integrations"""
        
        # Social Media Platforms
        self.api_integrations["youtube"] = APIIntegrationConfig(
            name="YouTube Data API",
            base_url="https://www.googleapis.com/youtube/v3",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.API_KEY,
            timeout=15.0,
            rate_limit=RateLimitConfig(requests_per_second=10, requests_per_minute=600)
        )
        
        self.api_integrations["instagram"] = APIIntegrationConfig(
            name="Instagram Basic Display API",
            base_url="https://graph.instagram.com",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=10.0
        )
        
        self.api_integrations["tiktok"] = APIIntegrationConfig(
            name="TikTok Business API",
            base_url="https://business-api.tiktok.com",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=15.0
        )
        
        self.api_integrations["twitter"] = APIIntegrationConfig(
            name="Twitter API v2",
            base_url="https://api.twitter.com/2",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.BEARER_TOKEN,
            timeout=10.0
        )
        
        # Music Platforms
        self.api_integrations["spotify"] = APIIntegrationConfig(
            name="Spotify Web API",
            base_url="https://api.spotify.com/v1",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=10.0
        )
        
        self.api_integrations["soundcloud"] = APIIntegrationConfig(
            name="SoundCloud API",
            base_url="https://api.soundcloud.com",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=15.0
        )
        
        # Payment Processors
        self.api_integrations["stripe"] = APIIntegrationConfig(
            name="Stripe API",
            base_url="https://api.stripe.com/v1",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.BEARER_TOKEN,
            timeout=30.0,
            rate_limit=RateLimitConfig(requests_per_second=25, requests_per_minute=1500)
        )
        
        self.api_integrations["paypal"] = APIIntegrationConfig(
            name="PayPal API",
            base_url="https://api.paypal.com/v1",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=30.0
        )
        
        # Cloud Storage
        self.api_integrations["aws_s3"] = APIIntegrationConfig(
            name="AWS S3 API",
            base_url="https://s3.amazonaws.com",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.CUSTOM,
            timeout=60.0
        )
        
        self.api_integrations["google_cloud"] = APIIntegrationConfig(
            name="Google Cloud Storage API",
            base_url="https://storage.googleapis.com/storage/v1",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.OAUTH2,
            timeout=60.0
        )
        
        # AI/ML Services
        self.api_integrations["openai"] = APIIntegrationConfig(
            name="OpenAI API",
            base_url="https://api.openai.com/v1",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.BEARER_TOKEN,
            timeout=120.0,
            rate_limit=RateLimitConfig(requests_per_second=3, requests_per_minute=180)
        )
        
        self.api_integrations["huggingface"] = APIIntegrationConfig(
            name="Hugging Face Inference API",
            base_url="https://api-inference.huggingface.co",
            integration_type=IntegrationType.REST_API,
            auth_type=AuthenticationType.BEARER_TOKEN,
            timeout=60.0
        )
    
    async def configure_external_integrations(self) -> Dict[str, bool]:
        """Configure all external integrations"""
        start_time = time.time()
        results = {}
        
        try:
            for name, config in self.api_integrations.items():
                if config.enabled:
                    results[name] = await self._configure_single_integration(name, config)
                else:
                    results[name] = False
                    
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"External integrations configured in {elapsed:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"Failed to configure external integrations: {e}")
            raise
    
    async def _configure_single_integration(self, name: str, config: APIIntegrationConfig) -> bool:
        """Configure a single integration"""
        try:
            # Register integration
            self._integration_registry[name] = {
                "config": config,
                "status": "configuring",
                "last_health_check": None
            }
            
            # Setup connection session if needed
            if not self._session:
                self._session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                    headers=config.headers
                )
            
            # Perform health check
            health_ok = await self._perform_health_check(name, config)
            
            self._integration_registry[name]["status"] = "active" if health_ok else "unhealthy"
            self._health_status[name] = health_ok
            
            return health_ok
            
        except Exception as e:
            logger.error(f"Failed to configure integration {name}: {e}")
            self._integration_registry[name]["status"] = "error"
            return False
    
    async def _perform_health_check(self, name: str, config: APIIntegrationConfig) -> bool:
        """Perform health check for integration"""
        try:
            if not self._session:
                return False
                
            # Simple health check - attempt to connect
            health_endpoint = self._get_health_endpoint(name, config)
            
            async with self._session.get(
                health_endpoint,
                timeout=aiohttp.ClientTimeout(total=5.0)
            ) as response:
                return response.status < 400
                
        except Exception as e:
            logger.warning(f"Health check failed for {name}: {e}")
            return False
    
    def _get_health_endpoint(self, name: str, config: APIIntegrationConfig) -> str:
        """Get health check endpoint for integration"""
        # Return base URL for basic connectivity test
        return config.base_url
    
    async def manage_api_connections(self) -> Dict[str, Any]:
        """Manage API connections and connection pooling"""
        start_time = time.time()
        
        try:
            connection_status = {}
            
            for name, config in self.api_integrations.items():
                if config.enabled:
                    connection_status[name] = {
                        "status": self._health_status.get(name, False),
                        "last_check": self._integration_registry.get(name, {}).get("last_health_check"),
                        "rate_limit": {
                            "requests_per_second": config.rate_limit.requests_per_second,
                            "current_usage": 0  # Would track actual usage
                        }
                    }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"API connections managed in {elapsed:.2f}ms")
            return connection_status
            
        except Exception as e:
            logger.error(f"Failed to manage API connections: {e}")
            raise
    
    async def service_discovery_configuration(self) -> Dict[str, Any]:
        """Configure service discovery for microservices"""
        start_time = time.time()
        
        try:
            discovery_config = {
                "enabled": self.service_mesh.enabled,
                "services": {},
                "health_checks": {},
                "load_balancing": self.service_mesh.load_balancing
            }
            
            # Register internal services
            internal_services = [
                "workflow-engine",
                "content-processor", 
                "ai-analyzer",
                "monetization-service",
                "collaboration-service",
                "distribution-service"
            ]
            
            for service in internal_services:
                discovery_config["services"][service] = {
                    "instances": [f"{service}-{i}" for i in range(1, 4)],  # 3 instances each
                    "health_endpoint": f"/health",
                    "metrics_endpoint": f"/metrics"
                }
                
                discovery_config["health_checks"][service] = {
                    "interval": self.service_mesh.health_check_interval,
                    "timeout": 5,
                    "enabled": self.service_mesh.health_check_enabled
                }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Service discovery configured in {elapsed:.2f}ms")
            return discovery_config
            
        except Exception as e:
            logger.error(f"Failed to configure service discovery: {e}")
            raise
    
    async def integration_health_monitoring(self) -> Dict[str, Any]:
        """Monitor health of all integrations"""
        start_time = time.time()
        
        try:
            health_report = {
                "timestamp": time.time(),
                "overall_status": "healthy",
                "integrations": {},
                "metrics": {
                    "total_integrations": len(self.api_integrations),
                    "healthy_integrations": 0,
                    "unhealthy_integrations": 0,
                    "disabled_integrations": 0
                }
            }
            
            for name, config in self.api_integrations.items():
                if not config.enabled:
                    health_report["integrations"][name] = {
                        "status": "disabled",
                        "last_check": None
                    }
                    health_report["metrics"]["disabled_integrations"] += 1
                    continue
                
                # Perform fresh health check
                is_healthy = await self._perform_health_check(name, config)
                
                health_report["integrations"][name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_check": time.time(),
                    "response_time": None  # Would measure actual response time
                }
                
                if is_healthy:
                    health_report["metrics"]["healthy_integrations"] += 1
                else:
                    health_report["metrics"]["unhealthy_integrations"] += 1
            
            # Determine overall status
            if health_report["metrics"]["unhealthy_integrations"] > 0:
                health_report["overall_status"] = "degraded"
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Integration health monitoring completed in {elapsed:.2f}ms")
            return health_report
            
        except Exception as e:
            logger.error(f"Failed to monitor integration health: {e}")
            raise
    
    async def integration_security_validation(self) -> Dict[str, Any]:
        """Validate security configuration for integrations"""
        start_time = time.time()
        
        try:
            security_report = {
                "timestamp": time.time(),
                "overall_security_score": 0,
                "integrations": {},
                "security_issues": []
            }
            
            total_score = 0
            
            for name, config in self.api_integrations.items():
                security_score = 0
                issues = []
                
                # Check SSL verification
                if config.verify_ssl:
                    security_score += 20
                else:
                    issues.append("SSL verification disabled")
                
                # Check authentication type
                if config.auth_type in [AuthenticationType.OAUTH2, AuthenticationType.JWT]:
                    security_score += 30
                elif config.auth_type == AuthenticationType.BEARER_TOKEN:
                    security_score += 25
                elif config.auth_type == AuthenticationType.API_KEY:
                    security_score += 20
                elif config.auth_type == AuthenticationType.NONE:
                    issues.append("No authentication configured")
                
                # Check timeout configuration
                if config.timeout <= 60:
                    security_score += 15
                else:
                    issues.append("Timeout too high (potential DoS vulnerability)")
                
                # Check rate limiting
                if config.rate_limit.requests_per_second <= 100:
                    security_score += 15
                else:
                    issues.append("Rate limit too high")
                
                # Check circuit breaker
                if config.circuit_breaker.failure_threshold <= 10:
                    security_score += 10
                
                # Check retry policy
                if config.retry_policy.max_attempts <= 5:
                    security_score += 10
                
                security_report["integrations"][name] = {
                    "security_score": security_score,
                    "max_score": 100,
                    "issues": issues,
                    "status": "secure" if security_score >= 80 else "needs_review"
                }
                
                total_score += security_score
            
            security_report["overall_security_score"] = total_score / len(self.api_integrations) if self.api_integrations else 0
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Integration security validation completed in {elapsed:.2f}ms")
            return security_report
            
        except Exception as e:
            logger.error(f"Failed to validate integration security: {e}")
            raise
    
    async def integration_performance_optimization(self) -> Dict[str, Any]:
        """Optimize integration performance"""
        start_time = time.time()
        
        try:
            optimization_results = {
                "timestamp": time.time(),
                "optimizations_applied": [],
                "performance_improvements": {},
                "recommendations": []
            }
            
            for name, config in self.api_integrations.items():
                improvements = {}
                
                # Optimize timeout based on integration type
                if config.integration_type == IntegrationType.REST_API:
                    if config.timeout > 30:
                        config.timeout = 30
                        improvements["timeout_reduced"] = True
                        optimization_results["optimizations_applied"].append(f"Reduced timeout for {name}")
                
                # Optimize rate limits
                if config.rate_limit.requests_per_second > 50:
                    config.rate_limit.requests_per_second = 50
                    improvements["rate_limit_optimized"] = True
                    optimization_results["optimizations_applied"].append(f"Optimized rate limit for {name}")
                
                # Enable circuit breaker if not configured
                if config.circuit_breaker.failure_threshold > 5:
                    config.circuit_breaker.failure_threshold = 5
                    improvements["circuit_breaker_optimized"] = True
                    optimization_results["optimizations_applied"].append(f"Optimized circuit breaker for {name}")
                
                optimization_results["performance_improvements"][name] = improvements
            
            # General recommendations
            optimization_results["recommendations"] = [
                "Consider implementing connection pooling",
                "Enable HTTP/2 where supported",
                "Implement caching for frequently accessed data",
                "Use compression for large payloads",
                "Monitor and optimize based on actual usage patterns"
            ]
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Integration performance optimization completed in {elapsed:.2f}ms")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize integration performance: {e}")
            raise
    
    async def integration_failover_management(self) -> Dict[str, Any]:
        """Manage failover for integrations"""
        start_time = time.time()
        
        try:
            failover_config = {
                "timestamp": time.time(),
                "failover_strategies": {},
                "backup_endpoints": {},
                "recovery_procedures": {}
            }
            
            for name, config in self.api_integrations.items():
                # Define failover strategy based on integration type
                strategy = "circuit_breaker"
                if config.integration_type == IntegrationType.REST_API:
                    strategy = "retry_with_exponential_backoff"
                elif config.integration_type == IntegrationType.WEBSOCKET:
                    strategy = "automatic_reconnection"
                elif config.integration_type == IntegrationType.MESSAGE_QUEUE:
                    strategy = "queue_redirection"
                
                failover_config["failover_strategies"][name] = {
                    "primary_strategy": strategy,
                    "fallback_strategy": "graceful_degradation",
                    "max_failures_before_failover": config.circuit_breaker.failure_threshold,
                    "recovery_timeout": config.circuit_breaker.recovery_timeout
                }
                
                # Define backup endpoints (would be configurable)
                if name in ["stripe", "paypal"]:  # Critical payment services
                    failover_config["backup_endpoints"][name] = {
                        "backup_url": config.base_url.replace("api.", "api-backup."),
                        "enabled": True
                    }
                
                # Define recovery procedures
                failover_config["recovery_procedures"][name] = {
                    "health_check_interval": 30,
                    "recovery_validation": "send_test_request",
                    "gradual_traffic_restoration": True
                }
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Integration failover management configured in {elapsed:.2f}ms")
            return failover_config
            
        except Exception as e:
            logger.error(f"Failed to configure integration failover: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.close()
            self._session = None
    
    def get_integration_status(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get status of specific integration"""
        return self._integration_registry.get(integration_name)
    
    def enable_integration(self, integration_name: str) -> bool:
        """Enable specific integration"""
        if integration_name in self.api_integrations:
            self.api_integrations[integration_name].enabled = True
            return True
        return False
    
    def disable_integration(self, integration_name: str) -> bool:
        """Disable specific integration"""
        if integration_name in self.api_integrations:
            self.api_integrations[integration_name].enabled = False
            return True
        return False

# Global integration configuration instance
integration_config = IntegrationConfig()

__all__ = [
    'IntegrationConfig',
    'APIIntegrationConfig',
    'ServiceMeshConfig', 
    'MessageQueueConfig',
    'IntegrationType',
    'AuthenticationType',
    'RetryPolicy',
    'CircuitBreakerConfig',
    'RateLimitConfig',
    'integration_config'
]