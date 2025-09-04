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

# New consolidated modules
from .public import endpoints_router
from .middleware import (
    authentication_middleware,
    setup_middleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware
)
from .authentication import (
    AuthenticationService,
    JWTManager,
    OAuth2Manager,
    SessionManager,
    MFAManager,
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
from .graphql import schema as graphql_schema
from .testing import (
    APITestClient,
    TestDataGenerator,
    APITestSuite,
    PerformanceTestRunner
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


# ========================================
# INTEGRATED DOCUMENTATION (from documentation.py)
# ========================================

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import json

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

class DocumentationConfig:
    """Configuration for API documentation"""
    
    def __init__(self):
        self.title = "IA Influencer Agent API"
        self.description = """
        # IA Influencer Agent API

        The most advanced AI-powered influencer management platform with:
        - **Content Protection**: Advanced fingerprinting and DMCA protection
        - **AI-Powered Analytics**: Market intelligence and performance insights
        - **Multi-Platform Distribution**: Automated content publishing
        - **Collaboration Tools**: Smart matching and collaboration management
        - **Monetization**: Revenue optimization and payment processing
        - **Real-time Monitoring**: Performance tracking and alerts
        """
        self.version = "2.0.0"
        self.terms_of_service = "https://ainflue.com/terms"
        self.contact = {
            "name": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "url": "https://ainflue.com"
        }
        self.license_info = {
            "name": "Proprietary License",
            "url": "https://ainflue.com/license"
        }

class OpenAPIGenerator:
    """Generate OpenAPI 3.0 documentation"""
    
    def __init__(self, config: DocumentationConfig):
        self.config = config
    
    def generate_schema(self, app: FastAPI) -> Dict[str, Any]:
        """Generate OpenAPI schema"""
        return get_openapi(
            title=self.config.title,
            version=self.config.version,
            description=self.config.description,
            routes=app.routes,
        )