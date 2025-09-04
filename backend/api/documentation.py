"""Documentation - OpenAPI, Swagger Generation
Consolidated API documentation functionality.

This module consolidates documentation from:
- OpenAPI 3.0 schema generation
- Swagger UI configuration and customization
- API documentation automation
- Example generation and validation
- Interactive API explorer
- Documentation versioning and publishing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import json

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# ========================================
# DOCUMENTATION CONFIGURATION
# ========================================

class DocumentationConfig:
    """Configuration for API documentation"""
    
    def __init__(self):
        self.title = "IA Influencer Agent API"
        self.description = self._get_api_description()
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
        self.servers = [
            {"url": "https://api.ainflue.com/v2", "description": "Production server"},
            {"url": "https://staging-api.ainflue.com/v2", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
        self.tags_metadata = self._get_tags_metadata()
    
    def _get_api_description(self) -> str:
        """Get comprehensive API description"""
        return """
# 🚀 IA Influencer Agent API - Enterprise Multi-Format Content Protection & Monetization Platform

## Overview
The IA Influencer Agent API is a comprehensive platform designed for content creators, musicians, bloggers, photographers, influencers, and comedians to protect, monetize, and collaborate on their digital content.

## Key Features

### 🛡️ **Advanced Content Protection**
- **AI Fingerprinting Engine**: Multi-format content identification (audio, video, image, text)
- **Real-time Monitoring**: Automated content surveillance across platforms
- **DMCA Protection**: Automated takedown requests and legal compliance
- **Blockchain Verification**: Immutable proof of ownership and timestamps

### 💰 **Monetization & Revenue**
- **Dynamic Pricing**: AI-powered pricing optimization
- **Revenue Tracking**: Real-time earnings analytics
- **Licensing Automation**: Smart contracts for content licensing
- **Multi-Platform Distribution**: Automated content distribution across social platforms

### 🤝 **Collaboration Platform**
- **Creator Matching**: AI-powered collaboration recommendations
- **Project Management**: Built-in tools for managing creative projects
- **Revenue Sharing**: Transparent and automated revenue distribution
- **Communication Tools**: Integrated messaging and file sharing

### 📊 **Analytics & Intelligence**
- **Performance Metrics**: Comprehensive content performance analytics
- **Market Intelligence**: Competitive analysis and trend identification
- **Predictive Analytics**: Machine learning-based performance predictions
- **Real-time Dashboard**: Live updates on content performance and earnings

### 🔐 **Enterprise Security**
- **OAuth2 Authentication**: Integration with major social platforms
- **JWT Token Management**: Secure API access with refresh tokens
- **Multi-Factor Authentication**: TOTP, SMS, email, and biometric options
- **Rate Limiting**: Advanced rate limiting with tiered access levels

## Authentication
All API endpoints require authentication using JWT tokens. Obtain tokens through the `/auth/login` endpoint or OAuth2 providers.

## Rate Limits
- **Free Tier**: 1,000 requests per hour
- **Basic Tier**: 10,000 requests per hour  
- **Premium Tier**: 100,000 requests per hour
- **Enterprise Tier**: Unlimited requests

## Error Handling
All errors follow RFC 7807 Problem Details format with detailed error codes and descriptions.

## Support
For technical support, integration assistance, or licensing inquiries, contact: mlaiel@live.de

---
**Copyright © 2025 Fahed Mlaiel. All rights reserved.**
        """
    
    def _get_tags_metadata(self) -> List[Dict[str, Any]]:
        """Get API tags metadata for organization"""
        return [
            {
                "name": "Authentication",
                "description": "User authentication, registration, and OAuth2 integration"
            },
            {
                "name": "Content Management", 
                "description": "Upload, manage, and organize creative content"
            },
            {
                "name": "Content Protection",
                "description": "AI fingerprinting, monitoring, and DMCA protection"
            },
            {
                "name": "Monetization",
                "description": "Pricing, licensing, and revenue management"
            },
            {
                "name": "Collaboration",
                "description": "Creator matching, project management, and communication"
            },
            {
                "name": "Analytics",
                "description": "Performance metrics, market intelligence, and insights"
            },
            {
                "name": "Payments",
                "description": "Payment processing, billing, and financial operations"
            },
            {
                "name": "Webhooks",
                "description": "Real-time event notifications and integrations"
            },
            {
                "name": "System",
                "description": "System health, monitoring, and administrative functions"
            }
        ]

# ========================================
# OPENAPI SCHEMA CUSTOMIZATION
# ========================================

class OpenAPIGenerator:
    """Custom OpenAPI schema generator"""
    
    def __init__(self, app: FastAPI, config: DocumentationConfig):
        self.app = app
        self.config = config
    
    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate custom OpenAPI schema"""
        if self.app.openapi_schema:
            return self.app.openapi_schema
        
        openapi_schema = get_openapi(
            title=self.config.title,
            version=self.config.version,
            description=self.config.description,
            routes=self.app.routes,
            tags=self.config.tags_metadata,
            servers=self.config.servers
        )
        
        # Add custom extensions
        openapi_schema["info"]["contact"] = self.config.contact
        openapi_schema["info"]["license"] = self.config.license_info
        openapi_schema["info"]["termsOfService"] = self.config.terms_of_service
        
        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from login endpoint"
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for programmatic access"
            },
            "oauth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://api.ainflue.com/v2/auth/oauth2/authorize",
                        "tokenUrl": "https://api.ainflue.com/v2/auth/oauth2/token",
                        "refreshUrl": "https://api.ainflue.com/v2/auth/oauth2/refresh",
                        "scopes": {
                            "read": "Read access to user data",
                            "write": "Write access to user data",
                            "admin": "Administrative access"
                        }
                    }
                }
            }
        }
        
        # Add global security requirement
        openapi_schema["security"] = [
            {"bearerAuth": []},
            {"apiKeyAuth": []},
            {"oauth2": ["read", "write"]}
        ]
        
        # Add custom extensions
        openapi_schema["x-logo"] = {
            "url": "https://ainflue.com/logo.png",
            "altText": "IA Influencer Agent Logo"
        }
        
        # Add rate limiting info
        openapi_schema["x-rate-limits"] = {
            "free": {"requests": 1000, "period": "hour"},
            "basic": {"requests": 10000, "period": "hour"},
            "premium": {"requests": 100000, "period": "hour"},
            "enterprise": {"requests": "unlimited", "period": "hour"}
        }
        
        # Add examples for common operations
        self._add_operation_examples(openapi_schema)
        
        self.app.openapi_schema = openapi_schema
        return openapi_schema
    
    def _add_operation_examples(self, schema: Dict[str, Any]):
        """Add examples to operations"""
        examples = {
            "/auth/login": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "examples": {
                                    "musician_login": {
                                        "summary": "Musician login",
                                        "value": {
                                            "email": "musician@example.com",
                                            "password": "SecurePassword123!"
                                        }
                                    },
                                    "influencer_login": {
                                        "summary": "Influencer login",
                                        "value": {
                                            "email": "influencer@example.com", 
                                            "password": "MyPassword456@"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Merge examples into schema paths
        if "paths" in schema:
            for path, path_examples in examples.items():
                if path in schema["paths"]:
                    for method, method_examples in path_examples.items():
                        if method in schema["paths"][path]:
                            schema["paths"][path][method].update(method_examples)

# ========================================
# SWAGGER UI CUSTOMIZATION
# ========================================

class SwaggerUICustomizer:
    """Custom Swagger UI configuration"""
    
    def __init__(self, config: DocumentationConfig):
        self.config = config
    
    def get_swagger_ui_html(self, openapi_url: str, title: str) -> HTMLResponse:
        """Get customized Swagger UI HTML"""
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{title} - API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayOperationId": False,
                "defaultModelsExpandDepth": 1,
                "defaultModelExpandDepth": 1,
                "displayRequestDuration": True,
                "docExpansion": "list",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True,
                "validatorUrl": None,
                "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
                "persistAuthorization": True,
                "layout": "StandaloneLayout"
            }
        )
    
    def get_redoc_html(self, openapi_url: str, title: str) -> HTMLResponse:
        """Get customized ReDoc HTML"""
        return get_redoc_html(
            openapi_url=openapi_url,
            title=f"{title} - API Documentation",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.0/bundles/redoc.standalone.js",
        )

# ========================================
# DOCUMENTATION MODELS
# ========================================

class APIExample(BaseModel):
    """API example model"""
    summary: str = Field(..., description="Example summary")
    description: Optional[str] = Field(None, description="Example description")
    value: Dict[str, Any] = Field(..., description="Example value")

class APIError(BaseModel):
    """API error documentation model"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

class RateLimitInfo(BaseModel):
    """Rate limit information model"""
    tier: str = Field(..., description="Subscription tier")
    requests_per_hour: Union[int, str] = Field(..., description="Requests per hour limit")
    burst_limit: Optional[int] = Field(None, description="Burst request limit")

# ========================================
# DOCUMENTATION ENDPOINTS
# ========================================

class DocumentationEndpoints:
    """Documentation-specific endpoints"""
    
    def __init__(self, app: FastAPI, config: DocumentationConfig):
        self.app = app
        self.config = config
        self.openapi_generator = OpenAPIGenerator(app, config)
        self.swagger_customizer = SwaggerUICustomizer(config)
    
    def add_documentation_routes(self):
        """Add documentation routes to the app"""
        
        @self.app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            """Custom Swagger UI"""
            return self.swagger_customizer.get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=self.config.title
            )
        
        @self.app.get("/redoc", include_in_schema=False)
        async def custom_redoc_html():
            """Custom ReDoc documentation"""
            return self.swagger_customizer.get_redoc_html(
                openapi_url="/openapi.json",
                title=self.config.title
            )
        
        @self.app.get("/openapi.json", include_in_schema=False)
        async def custom_openapi():
            """Custom OpenAPI schema"""
            return JSONResponse(self.openapi_generator.generate_openapi_schema())
        
        @self.app.get("/api/v1/docs/examples", tags=["Documentation"])
        async def get_api_examples() -> Dict[str, List[APIExample]]:
            """Get API usage examples"""
            return {
                "authentication": [
                    APIExample(
                        summary="Login with email/password",
                        description="Standard email and password authentication",
                        value={
                            "email": "user@example.com",
                            "password": "SecurePassword123!"
                        }
                    ),
                    APIExample(
                        summary="OAuth2 login",
                        description="Login using OAuth2 provider",
                        value={
                            "provider": "google",
                            "redirect_uri": "https://yourapp.com/callback"
                        }
                    )
                ],
                "content_upload": [
                    APIExample(
                        summary="Upload audio file",
                        description="Upload music track with metadata",
                        value={
                            "title": "My New Song",
                            "description": "Latest musical creation",
                            "tags": ["music", "electronic", "original"],
                            "is_public": True,
                            "content_type": "audio"
                        }
                    )
                ],
                "collaboration": [
                    APIExample(
                        summary="Create collaboration request",
                        description="Request collaboration with another creator",
                        value={
                            "title": "Music Video Collaboration",
                            "description": "Looking for videographer for my new track",
                            "budget": 500.00,
                            "deadline": "2025-02-01T00:00:00Z",
                            "requirements": ["Professional camera", "Video editing skills"]
                        }
                    )
                ]
            }
        
        @self.app.get("/api/v1/docs/errors", tags=["Documentation"])
        async def get_error_codes() -> Dict[str, List[APIError]]:
            """Get API error codes and descriptions"""
            return {
                "authentication_errors": [
                    APIError(
                        code="AUTH_001",
                        message="Invalid credentials",
                        details={"description": "Email or password is incorrect"}
                    ),
                    APIError(
                        code="AUTH_002", 
                        message="Token expired",
                        details={"description": "JWT token has expired, refresh required"}
                    )
                ],
                "validation_errors": [
                    APIError(
                        code="VAL_001",
                        message="Invalid file format",
                        details={"description": "File format not supported for content type"}
                    ),
                    APIError(
                        code="VAL_002",
                        message="File too large",
                        details={"description": "File exceeds maximum size limit"}
                    )
                ],
                "rate_limit_errors": [
                    APIError(
                        code="RATE_001",
                        message="Rate limit exceeded",
                        details={"description": "Too many requests, please try again later"}
                    )
                ]
            }
        
        @self.app.get("/api/v1/docs/rate-limits", tags=["Documentation"])
        async def get_rate_limits() -> List[RateLimitInfo]:
            """Get rate limit information for different tiers"""
            return [
                RateLimitInfo(tier="free", requests_per_hour=1000, burst_limit=50),
                RateLimitInfo(tier="basic", requests_per_hour=10000, burst_limit=500),
                RateLimitInfo(tier="premium", requests_per_hour=100000, burst_limit=5000),
                RateLimitInfo(tier="enterprise", requests_per_hour="unlimited")
            ]

# ========================================
# DOCUMENTATION SERVICE
# ========================================

class DocumentationService:
    """Main documentation service"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.config = DocumentationConfig()
        self.endpoints = DocumentationEndpoints(app, self.config)
    
    def setup_documentation(self):
        """Setup complete documentation system"""
        # Set app metadata
        self.app.title = self.config.title
        self.app.description = self.config.description
        self.app.version = self.config.version
        self.app.terms_of_service = self.config.terms_of_service
        self.app.contact = self.config.contact
        self.app.license_info = self.config.license_info
        self.app.servers = self.config.servers
        
        # Add documentation routes
        self.endpoints.add_documentation_routes()
        
        # Override OpenAPI schema generation
        self.app.openapi = self.endpoints.openapi_generator.generate_openapi_schema
    
    def generate_sdk_documentation(self, language: str = "python") -> str:
        """Generate SDK documentation for specific language"""
        if language == "python":
            return self._generate_python_sdk_docs()
        elif language == "javascript":
            return self._generate_javascript_sdk_docs()
        else:
            return "SDK documentation not available for this language"
    
    def _generate_python_sdk_docs(self) -> str:
        """Generate Python SDK documentation"""
        return """
# Python SDK Documentation

## Installation
```bash
pip install ainflue-sdk
```

## Quick Start
```python
from ainflue import AIInfluenceClient

# Initialize client
client = AIInfluenceClient(api_key="your_api_key")

# Upload content
content = client.content.upload(
    file_path="my_song.mp3",
    title="My New Song",
    tags=["music", "electronic"]
)

# Get analytics
analytics = client.analytics.get_content_performance(content.id)
print(f"Views: {analytics.views}, Engagement: {analytics.engagement_rate}%")
```
        """
    
    def _generate_javascript_sdk_docs(self) -> str:
        """Generate JavaScript SDK documentation"""
        return """
# JavaScript SDK Documentation

## Installation
```bash
npm install @ainflue/sdk
```

## Quick Start
```javascript
import { AIInfluenceClient } from '@ainflue/sdk';

// Initialize client
const client = new AIInfluenceClient({ apiKey: 'your_api_key' });

// Upload content
const content = await client.content.upload({
  file: fileBlob,
  title: 'My New Song',
  tags: ['music', 'electronic']
});

// Get analytics
const analytics = await client.analytics.getContentPerformance(content.id);
console.log(`Views: ${analytics.views}, Engagement: ${analytics.engagementRate}%`);
```
        """

# ========================================
# EXPORTS
# ========================================

__all__ = [
    "DocumentationConfig",
    "OpenAPIGenerator",
    "SwaggerUICustomizer", 
    "DocumentationEndpoints",
    "DocumentationService",
    "APIExample",
    "APIError",
    "RateLimitInfo"
]