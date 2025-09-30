"""
API Management Module - Ainflue Integrations
===========================================
Enterprise-grade API management providing comprehensive gateway functionality,
intelligent rate limiting, circuit breaker patterns, advanced retry logic,
and webhook orchestration across 65+ platform integrations.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all API management components
from .api_gateway import *
from .rate_limiter import *
from .retry_handler import *
from .circuit_breaker import *
from .webhook_manager import *

# Re-export for convenience
from . import (
    api_gateway,
    rate_limiter,
    retry_handler,
    circuit_breaker,
    webhook_manager
)

# Exports publics
__all__ = [
    'APIGateway',
    'RateLimiter',
    'RetryHandler',
    'CircuitBreaker',
    'WebhookManager',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise API management infrastructure for multi-platform content distribution"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'api_features': [
        'intelligent_routing',
        'adaptive_rate_limiting',
        'resilience_patterns',
        'webhook_orchestration',
        'performance_optimization'
    ]
}