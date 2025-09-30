"""
API Gateway Module - Enterprise API Management Hub
© 2025 Fahed Mlaiel. All rights reserved.

Central API management for Ainflue creator platform providing REST, GraphQL,
WebSocket APIs with rate limiting, authentication, and comprehensive middleware.
"""

from typing import Dict, List, Optional, Any

# API Gateway core components
try:
    from .api_gateway import APIGateway
except ImportError:
    APIGateway = None

try:
    from .rest_api import RESTAPIManager
except ImportError:
    RESTAPIManager = None

try:
    from .graphql_api import GraphQLAPIManager
except ImportError:
    GraphQLAPIManager = None

try:
    from .websocket_api import WebSocketAPIManager
except ImportError:
    WebSocketAPIManager = None

try:
    from .monitoring import EnterpriseMonitoringSystem
except ImportError:
    EnterpriseMonitoringSystem = None

try:
    from .authentication import AuthenticationGateway
except ImportError:
    AuthenticationGateway = None

try:
    from .authorization import AuthorizationEngine
except ImportError:
    AuthorizationEngine = None

try:
    from .security_middleware import SecurityMiddleware
except ImportError:
    SecurityMiddleware = None

try:
    from .rate_limiter import RateLimiter
except ImportError:
    RateLimiter = None

try:
    from .middleware import MiddlewareStack
except ImportError:
    MiddlewareStack = None

try:
    from .api_documentation import APIDocumentationGenerator
except ImportError:
    APIDocumentationGenerator = None

try:
    from .api_testing import APITestingFramework
except ImportError:
    APITestingFramework = None

try:
    from .api_versioning import APIVersionManager
except ImportError:
    APIVersionManager = None

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise API Gateway for Creator Platform"

# Exports
__all__ = [
    'APIGateway',
    'RESTAPIManager',
    'GraphQLAPIManager', 
    'WebSocketAPIManager',
    'RateLimiter',
    'EnterpriseMonitoringSystem',
    'AuthenticationGateway',
    'AuthorizationEngine',
    'SecurityMiddleware',
    'MiddlewareStack',
    'APIDocumentationGenerator',
    'APITestingFramework',
    'APIVersionManager'
]

# Configuration for Ainflue creator platform APIs
AINFLUE_API_CONFIG = {
    'creator_apis': {
        'content_upload_api': '/api/v1/creators/content',
        'profile_management_api': '/api/v1/creators/profile',
        'revenue_analytics_api': '/api/v1/creators/revenue',
        'collaboration_api': '/api/v1/creators/collaborate',
        'distribution_api': '/api/v1/creators/distribute'
    },
    'platform_apis': {
        'ai_processing_api': '/api/v1/ai/process',
        'analytics_api': '/api/v1/analytics',
        'platform_integration_api': '/api/v1/platforms',
        'monetization_api': '/api/v1/monetization',
        'compliance_api': '/api/v1/compliance'
    },
    'admin_apis': {
        'user_management_api': '/api/v1/admin/users',
        'platform_management_api': '/api/v1/admin/platform',
        'monitoring_api': '/api/v1/admin/monitoring',
        'compliance_reporting_api': '/api/v1/admin/compliance'
    },
    'supported_versions': ['v1', 'v2'],
    'rate_limits': {
        'creator_tier': 1000,  # requests per minute
        'premium_tier': 5000,
        'enterprise_tier': 10000,
        'platform_integration': 50000
    },
    'authentication': {
        'oauth2_enabled': True,
        'api_key_enabled': True,
        'jwt_enabled': True,
        'creator_auth_required': True
    }
}