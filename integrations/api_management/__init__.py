"""
API Management Module - Ainflue Integrations
===========================================
Enterprise API management module providing comprehensive API gateway,
rate limiting, circuit breaker, retry logic, and webhook management.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# API Gateway Core Components
from .api_gateway import APIGateway
from .rate_limiter import RateLimiter
from .retry_handler import RetryHandler
from .circuit_breaker import CircuitBreaker
from .webhook_manager import WebhookManager

# Public exports
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
__description__ = "Enterprise API management and gateway for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_API_MANAGEMENT = {
    'platforms': 65,
    'gateway_features': ['rate_limiting', 'circuit_breaker', 'retry_logic', 'webhook_management'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}