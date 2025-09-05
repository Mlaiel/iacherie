"""Backend API Module - Consolidated API Framework
All API functionality consolidated into 12 modules for the Ainflue platform.

This module consolidates 285+ API files into 12 focused modules:
- endpoints.py: All REST endpoints consolidated
- middleware.py: Auth, CORS, rate limiting middleware  
- authentication.py: OAuth, JWT, session management
- validation.py: Request/response validation
- serialization.py: Data serializers and formatters
- websockets.py: WebSocket handlers and events
- graphql.py: GraphQL schema and resolvers
- documentation.py: OpenAPI, Swagger generation
- testing.py: API testing utilities
- versioning.py: API versioning and compatibility
- monitoring.py: API metrics, logging, health

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Legacy routers for backward compatibility
from .core_api import core_router
from .business_api import business_router
from .public import public_router

# Import available modules with error handling
try:
    from .core_api import *
    CORE_API_AVAILABLE = True
except ImportError as e:
    CORE_API_AVAILABLE = False
    logger.warning(f"Core API not available: {e}")

try:
    from .business_api import *
    BUSINESS_API_AVAILABLE = True
except ImportError as e:
    BUSINESS_API_AVAILABLE = False
    logger.warning(f"Business API not available: {e}")

try:
    from .public import *
    PUBLIC_API_AVAILABLE = True
except ImportError as e:
    PUBLIC_API_AVAILABLE = False
    logger.warning(f"Public API not available: {e}")

# New consolidated modules
try:
    from .middleware import (
        authentication_middleware,
        setup_middleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware,
        SecurityHeadersMiddleware
    )
    MIDDLEWARE_AVAILABLE = True
except ImportError as e:
    MIDDLEWARE_AVAILABLE = False
    logger.warning(f"Middleware not available: {e}")
try:
    from .authentication import (
        AuthenticationService,
        JWTManager,
        OAuth2Manager,
        SessionManager,
        MFAManager,
        get_auth_service
    )
    AUTH_AVAILABLE = True
except ImportError as e:
    AUTH_AVAILABLE = False
    logger.warning(f"Authentication not available: {e}")

try:
    from .validation import (
        ValidationService,
        FileValidationService,
        InputSanitizer,
        UserValidation,
        ContentMetadataValidation,
        FileUploadValidation
    )
    VALIDATION_AVAILABLE = True
except ImportError as e:
    VALIDATION_AVAILABLE = False
    logger.warning(f"Validation not available: {e}")

try:
    from .serialization import (
        SerializationService,
        ResponseBuilder,
        APIResponse,
        PaginatedResponse,
        ContentMetadataSerializer
    )
    SERIALIZATION_AVAILABLE = True
except ImportError as e:
    SERIALIZATION_AVAILABLE = False
    logger.warning(f"Serialization not available: {e}")

try:
    from .websockets import (
        WebSocketHandler,
        WebSocketManager,
        get_websocket_handler,
        ChannelNames
    )
    WEBSOCKETS_AVAILABLE = True
except ImportError as e:
    WEBSOCKETS_AVAILABLE = False
    logger.warning(f"WebSockets not available: {e}")

try:
    from .graphql import schema as graphql_schema
    GRAPHQL_AVAILABLE = True
except ImportError as e:
    GRAPHQL_AVAILABLE = False
    logger.warning(f"GraphQL not available: {e}")
except Exception as e:
    GRAPHQL_AVAILABLE = False
    logger.warning(f"GraphQL module error: {e}")
try:
    from .documentation import (
        DocumentationService,
        DocumentationConfig,
        OpenAPIGenerator
    )
    DOCUMENTATION_AVAILABLE = True
except ImportError as e:
    DOCUMENTATION_AVAILABLE = False
    logger.warning(f"Documentation not available: {e}")

try:
    from .testing import (
        APITestClient,
        TestDataGenerator,
        APITestSuite,
        PerformanceTestRunner
    )
    TESTING_AVAILABLE = True
except ImportError as e:
    TESTING_AVAILABLE = False
    logger.warning(f"Testing not available: {e}")
try:
    from .versioning import (
        VersioningService,
        APIVersionManager,
        get_api_version,
        get_compatibility_info
    )
    VERSIONING_AVAILABLE = True
except ImportError as e:
    VERSIONING_AVAILABLE = False
    logger.warning(f"Versioning not available: {e}")

try:
    from .monitoring import (
        MonitoringService,
        HealthCheckManager,
        MetricsCollector,
        AlertManager
    )
    MONITORING_AVAILABLE = True
except ImportError as e:
    MONITORING_AVAILABLE = False
    logger.warning(f"Monitoring not available: {e}")

__all__ = [
    # Legacy routers (backward compatibility)
    "core_router", 
    "business_router",
    "public_router",
    
    # Consolidated endpoints
    "endpoints_router",
    
    # Middleware
    "authentication_middleware",
    "setup_middleware",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware", 
    "SecurityHeadersMiddleware",
    
    # Authentication
    "AuthenticationService",
    "JWTManager",
    "OAuth2Manager", 
    "SessionManager",
    "MFAManager",
    "get_auth_service",
    
    # Validation
    "ValidationService",
    "FileValidationService",
    "InputSanitizer",
    "UserValidation",
    "ContentMetadataValidation",
    "FileUploadValidation",
    
    # Serialization
    "SerializationService",
    "ResponseBuilder",
    "APIResponse",
    "PaginatedResponse",
    "ContentMetadataSerializer",
    
    # WebSockets
    "WebSocketHandler",
    "WebSocketManager",
    "get_websocket_handler",
    "ChannelNames",
    
    # GraphQL
    "graphql_schema",
    
    # Documentation
    "DocumentationService",
    "DocumentationConfig", 
    "OpenAPIGenerator",
    
    # Testing
    "APITestClient",
    "TestDataGenerator",
    "APITestSuite",
    "PerformanceTestRunner",
    
    # Versioning
    "VersioningService",
    "APIVersionManager",
    "get_api_version",
    "get_compatibility_info",
    
    # Monitoring
    "MonitoringService",
    "HealthCheckManager",
    "MetricsCollector",
    "AlertManager"
]