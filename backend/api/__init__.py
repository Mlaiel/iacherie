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

# Core API routers for backward compatibility
from .core_api import core_router
from .business_api import business_router
from .public import public_router

# Consolidated modules - importing from existing files only
from .middleware import (
    setup_middleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    authentication_middleware
)
from .authentication import (
    AuthenticationService,
    JWTManager,
    OAuth2Manager,
    SessionManager,
    MFAManager,
    BiometricAuthManager,
    get_auth_service
)
from .validation import (
    ValidationService,
    FileValidationService,
    InputSanitizer,
    UserValidation,
    ContentMetadataValidation,
    FileUploadValidation
)
from .serialization import (
    SerializationService,
    ResponseBuilder,
    APIResponse,
    PaginatedResponse,
    ContentMetadataSerializer
)
from .websockets import (
    WebSocketHandler,
    WebSocketManager,
    get_websocket_handler,
    ChannelNames
)
from .graphql import (
    schema as graphql_schema,
    Query,
    Mutation,
    Subscription
)
from .versioning import (
    VersioningService,
    APIVersionManager,
    get_api_version,
    get_compatibility_info
)
from .monitoring import (
    MonitoringService,
    HealthCheckManager,
    MetricsCollector,
    AlertManager
)

__all__ = [
    # Core routers (backward compatibility)
    "core_router", 
    "business_router",
    "public_router",
    
    # Middleware
    "setup_middleware",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware", 
    "SecurityHeadersMiddleware",
    "authentication_middleware",
    
    # Authentication
    "AuthenticationService",
    "JWTManager",
    "OAuth2Manager", 
    "SessionManager",
    "MFAManager",
    "BiometricAuthManager",
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
    "Query",
    "Mutation",
    "Subscription",
    
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