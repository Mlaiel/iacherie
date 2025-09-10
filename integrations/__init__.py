"""Integrations Module
===================

Complete integration system for external services and platforms.
Supports AI services, cloud providers, payment gateways, social media platforms, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import core infrastructure
from .integration_manager import IntegrationManager, get_integration_manager
from .oauth_manager import OAuthManager
from .rate_limiter import RateLimiter, get_rate_limiter
from .webhook_manager import WebhookManager, get_webhook_manager
from .error_handler import IntegrationErrorHandler, get_error_handler
from .circuit_breaker import CircuitBreaker, get_circuit_breaker
from .cache_manager import IntegrationCacheManager, get_cache_manager

# Import submodules to make them accessible
from . import ai_services
from . import cloud_providers  
from . import payment_gateways
from . import platforms
from . import social_media
from . import spotify
from . import third_party

__all__ = [
    # Core infrastructure
    "IntegrationManager",
    "get_integration_manager",
    "OAuthManager", 
    "RateLimiter",
    "get_rate_limiter",
    "WebhookManager",
    "get_webhook_manager", 
    "IntegrationErrorHandler",
    "get_error_handler",
    "CircuitBreaker",
    "get_circuit_breaker",
    "IntegrationCacheManager",
    "get_cache_manager",
    
    # Service modules
    "ai_services",
    "cloud_providers", 
    "payment_gateways",
    "platforms",
    "social_media", 
    "spotify",
    "third_party"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
