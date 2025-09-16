"""
API Management Module - Ainflue Integrations
===========================================
Enterprise API management module providing comprehensive API gateway,
authentication, load balancing, versioning, metrics, security, rate limiting,
circuit breaker, retry logic, and webhook management.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 2.0 Enterprise Production
"""

# API Gateway Core Components
from .api_gateway import APIGateway
from .rate_limiter import RateLimiter
from .retry_handler import RetryHandler
from .circuit_breaker import CircuitBreaker
from .webhook_manager import WebhookManager

# Enterprise Phase 1 Components (CRITICAL)
from .authentication_manager import EnterpriseAuthenticationManager
from .load_balancer import IntelligentLoadBalancer
from .api_versioning_manager import EnterpriseAPIVersioningManager
from .metrics_collector import EnterpriseMetricsCollector
from .security_manager import EnterpriseSecurityManager

# Public exports
__all__ = [
    # Core Components
    'APIGateway',
    'RateLimiter',
    'RetryHandler',
    'CircuitBreaker',
    'WebhookManager',
    
    # Enterprise Phase 1 Components
    'EnterpriseAuthenticationManager',
    'IntelligentLoadBalancer',
    'EnterpriseAPIVersioningManager',
    'EnterpriseMetricsCollector',
    'EnterpriseSecurityManager',
]

# Metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise API management and gateway for Ainflue platform with multi-expert architecture"

# Configuration logique métier Ainflue
AINFLUE_API_MANAGEMENT = {
    'platforms': 65,
    'gateway_features': [
        'authentication', 'load_balancing', 'versioning', 'metrics_collection',
        'security_management', 'rate_limiting', 'circuit_breaker', 'retry_logic',
        'webhook_management'
    ],
    'workflow': 'connect→auth→validate→route→process→monitor→secure→distribute',
    'expert_implementation': [
        'Lead_Dev_IA', 'Backend_Senior', 'ML_Engineer', 'DBA', 'Security',
        'Microservices', 'Audio', 'DevOps', 'IA_Prompt_Engineer'
    ],
    'creator_economy_features': [
        'creator_authentication', 'platform_integration', 'content_security',
        'ai_processing', 'monetization_apis', 'collaboration_tools'
    ]
}