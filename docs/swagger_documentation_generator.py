"""Comprehensive API Documentation Generator
import logging

Creates complete Swagger/OpenAPI documentation for all API endpoints.

Author: AI Assistant
Purpose: Generate complete Swagger API documentation
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class APIMethod(Enum):
    """
HTTP methods"""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    HEAD = "head"


@dataclass
class APIParameter:
    """API parameter definition"""
    name: str
    param_type: str  # "query", "path", "header", "body"
    data_type: str
    description: str
    required: bool = True
    example: Any = None
    enum_values: Optional[List[str]] = None


@dataclass
class APIResponse:
    """API response definition"""
    status_code: int
    description: str
    schema: Dict[str, Any]
    examples: Optional[Dict[str, Any]] = None


@dataclass
class APIEndpoint:
    """
API endpoint definition"""
    path: str
    method: APIMethod
    summary: str
    description: str
    tags: List[str]
    parameters: List[APIParameter]
    responses: List[APIResponse]
    security: Optional[List[str]] = None
    deprecated: bool = False


class SwaggerDocumentationGenerator:
    """
Generates comprehensive Swagger/OpenAPI documentation"""
    
    def __init__(self, title -> None: str = "Ainflue AI Platform API", version -> None: str = "1.0.0") -> None:
        self.title = title
        self.version = version
        self.endpoints = []
        self.components = {
            "schemas": {},
            "securitySchemes": {},
            "responses": {},
            "parameters": {},
            "examples": {}
        }
    
    def add_endpoint(self, endpoint -> None: APIEndpoint) -> None:
        """Add an endpoint to the documentation"""
        self.endpoints.append(endpoint)
    
    def add_schema(self, name -> None: str, schema -> None: Dict[str, Any]) -> None:
        """
Add a schema definition"""
        self.components["schemas"][name] = schema
    
    def add_security_scheme(self, name -> None: str, scheme -> None: Dict[str, Any]) -> None:
        """Add a security scheme"""
        self.components["securitySchemes"][name] = scheme
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification"""
        
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": """# Ainflue AI Platform API

Complete API documentation for the Ainflue AI-powered content protection and monetization platform.

## Features

- **Content Protection**: Advanced AI-powered fingerprinting and rights management
- **Creator Management**: Comprehensive creator profiles and content management
- **Monetization**: Revenue tracking, licensing, and payment processing
- **Analytics**: Real-time analytics and performance metrics
- **Multi-platform Support**: Integration with major content platforms
- **Security**: Enterprise-grade security and compliance features

## Authentication

All API endpoints require authentication using API keys or JWT tokens.
                """,
                "termsOfService": "https://ainflue.com/terms",
                "contact": {
                    "name": "Ainflue API Support",
                    "email": "mlaiel@live.de",
                    "url": "https://ainflue.com/support"
                },
                "license": {
                    "name": "Proprietary",
                    "url": "https://ainflue.com/license"
                }
            },
            "servers": [
                {
                    "url": "https://api.ainflue.com/v1",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.ainflue.com/v1",
                    "description": "Staging server"
                },
                {
                    "url": "http://localhost:8000/api/v1",
                    "description": "Development server"
                }
            ],
            "paths": self._generate_paths(),
            "components": self.components,
            "security": [
                {"ApiKeyAuth": []},
                {"BearerAuth": []}
            ],
            "tags": self._generate_tags()
        }
        
        return spec
    
    def _generate_paths(self) -> Dict[str, Any]:
        """Generate paths section from endpoints"""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            operation = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": self._convert_parameters(endpoint.parameters),
                "responses": self._convert_responses(endpoint.responses)
            }
            
            if endpoint.security:
                operation["security"] = [{scheme: []} for scheme in endpoint.security]
            
            if endpoint.deprecated:
                operation["deprecated"] = True
            
            # Add request body for POST/PUT operations
            if endpoint.method in [APIMethod.POST, APIMethod.PUT, APIMethod.PATCH]:
                body_params = [p for p in endpoint.parameters if p.param_type == "body"]
                if body_params:
                    operation["requestBody"] = self._generate_request_body(body_params[0])
            
            paths[endpoint.path][endpoint.method.value] = operation
        
        return paths
    
    def _convert_parameters(self, parameters: List[APIParameter]) -> List[Dict[str, Any]]:
        """Convert parameter objects to OpenAPI format"""
        result = []
        
        for param in parameters:
            if param.param_type != "body":  # Body parameters handled separately
                param_spec = {
                    "name": param.name,
                    "in": param.param_type,
                    "description": param.description,
                    "required": param.required,
                    "schema": {
                        "type": param.data_type
                    }
                }
                
                if param.example is not None:
                    param_spec["example"] = param.example
                
                if param.enum_values:
                    param_spec["schema"]["enum"] = param.enum_values
                
                result.append(param_spec)
        
        return result
    
    def _convert_responses(self, responses: List[APIResponse]) -> Dict[str, Any]:
        """Convert response objects to OpenAPI format"""
        result = {}
        
        for response in responses:
            response_spec = {
                "description": response.description,
                "content": {
                    "application/json": {
                        "schema": response.schema
                    }
                }
            }
            
            if response.examples:
                response_spec["content"]["application/json"]["examples"] = response.examples
            
            result[str(response.status_code)] = response_spec
        
        return result
    
    def _generate_request_body(self, body_param: APIParameter) -> Dict[str, Any]:
        """Generate request body specification"""
        return {
            "description": body_param.description,
            "required": body_param.required,
            "content": {
                "application/json": {
                    "schema": {
                        "type": body_param.data_type,
                        "example": body_param.example
                    }
                }
            }
        }
    
    def _generate_tags(self) -> List[Dict[str, Any]]:
        """Generate tag definitions"""
        return [
            {
                "name": "Health",
                "description": "API health check and system status endpoints"
            },
            {
                "name": "Creators",
                "description": "Creator management and profile operations"
            },
            {
                "name": "Content",
                "description": "Content upload, management, and analysis"
            },
            {
                "name": "Protection",
                "description": "Content protection and rights management"
            },
            {
                "name": "Monetization",
                "description": "Revenue tracking and payment processing"
            },
            {
                "name": "Analytics",
                "description": "Analytics and reporting endpoints"
            },
            {
                "name": "Security",
                "description": "Security and audit endpoints"
            },
            {
                "name": "Admin",
                "description": "Administrative operations (admin only)"
            }
        ]


def create_comprehensive_api_documentation() -> SwaggerDocumentationGenerator:
    """Create comprehensive API documentation for Ainflue platform"""
    
    doc_generator = SwaggerDocumentationGenerator()
    
    # Add security schemes
    doc_generator.add_security_scheme("ApiKeyAuth", {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key for authentication"
    })
    
    doc_generator.add_security_scheme("BearerAuth", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token for authentication"
    })
    
    # Add common schemas
    _add_common_schemas(doc_generator)
    
    # Add all endpoint definitions
    _add_health_endpoints(doc_generator)
    _add_creator_endpoints(doc_generator)
    _add_content_endpoints(doc_generator)
    _add_protection_endpoints(doc_generator)
    _add_monetization_endpoints(doc_generator)
    _add_analytics_endpoints(doc_generator)
    _add_security_endpoints(doc_generator)
    _add_admin_endpoints(doc_generator)
    
    return doc_generator


def _add_common_schemas(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add common schema definitions"""
    
    # Error response schema
    doc_generator.add_schema("ErrorResponse", {
        "type": "object",
        "properties": {
            "error": {
                "type": "string",
                "description": "Error message"
            },
            "error_code": {
                "type": "string",
                "description": "Machine-readable error code"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Error timestamp"
            },
            "request_id": {
                "type": "string",
                "description": "Request ID for tracking"
            }
        },
        "required": ["error"]
    })
    
    # Creator schema
    doc_generator.add_schema("Creator", {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique creator identifier"
            },
            "name": {
                "type": "string",
                "description": "Creator's full name"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "Creator's email address"
            },
            "type": {
                "type": "string",
                "enum": ["musician", "blogger", "photographer", "influencer", "comedian", "podcaster", "writer", "artist", "videographer"],
                "description": "Type of creator"
            },
            "country": {
                "type": "string",
                "description": "Creator's country code"
            },
            "language": {
                "type": "string",
                "description": "Creator's primary language"
            },
            "verification_status": {
                "type": "string",
                "enum": ["pending", "verified", "rejected"],
                "description": "Creator verification status"
            },
            "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "Account creation timestamp"
            },
            "updated_at": {
                "type": "string",
                "format": "date-time",
                "description": "Last update timestamp"
            }
        },
        "required": ["id", "name", "email", "type"]
    })
    
    # Content schema
    doc_generator.add_schema("Content", {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique content identifier"
            },
            "creator_id": {
                "type": "string",
                "description": "ID of the content creator"
            },
            "title": {
                "type": "string",
                "description": "Content title"
            },
            "description": {
                "type": "string",
                "description": "Content description"
            },
            "content_type": {
                "type": "string",
                "enum": ["audio", "video", "image", "text", "mixed"],
                "description": "Type of content"
            },
            "file_size": {
                "type": "integer",
                "description": "File size in bytes"
            },
            "duration": {
                "type": "number",
                "description": "Content duration in seconds (for audio/video)"
            },
            "status": {
                "type": "string",
                "enum": ["uploaded", "processing", "processed", "failed", "deleted"],
                "description": "Content processing status"
            },
            "protection_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Content protection level"
            },
            "metadata": {
                "type": "object",
                "description": "Additional content metadata"
            },
            "created_at": {
                "type": "string",
                "format": "date-time",
                "description": "Upload timestamp"
            }
        },
        "required": ["id", "creator_id", "content_type", "status"]
    })
    
    # Analytics data schema
    doc_generator.add_schema("AnalyticsData", {
        "type": "object",
        "properties": {
            "total_creators": {
                "type": "integer",
                "description": "Total number of creators"
            },
            "total_content": {
                "type": "integer", 
                "description": "Total content items"
            },
            "active_workflows": {
                "type": "integer",
                "description": "Number of active workflows"
            },
            "revenue_today": {
                "type": "number",
                "description": "Today's revenue"
            },
            "revenue_this_month": {
                "type": "number",
                "description": "This month's revenue"
            },
            "protected_content": {
                "type": "integer",
                "description": "Number of protected content items"
            },
            "last_updated": {
                "type": "string",
                "format": "date-time",
                "description": "Last update timestamp"
            }
        },
        "required": ["total_creators", "total_content", "last_updated"]
    })


def _add_health_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add health check endpoints"""
    
    # Health check endpoint
    doc_generator.add_endpoint(APIEndpoint(
        path="/health",
        method=APIMethod.GET,
        summary="System health check",
        description="Check the overall health and status of the API system",
        tags=["Health"],
        parameters=[],
        responses=[
            APIResponse(
                status_code=200,
                description="System is healthy",
                schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "healthy"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "version": {"type": "string", "example": "1.0.0"},
                        "uptime": {"type": "number", "description": "Uptime in seconds"}
                    }
                },
                examples={
                    "healthy": {
                        "summary": "Healthy system response",
                        "value": {
                            "status": "healthy",
                            "timestamp": "2025-01-07T10:00:00Z",
                            "version": "1.0.0",
                            "uptime": 3600
                        }
                    }
                }
            ),
            APIResponse(
                status_code=503,
                description="System is unhealthy",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ]
    ))
    
    # Detailed health check
    doc_generator.add_endpoint(APIEndpoint(
        path="/health/detailed",
        method=APIMethod.GET,
        summary="Detailed system health check",
        description="Get detailed health information about all system components",
        tags=["Health"],
        parameters=[],
        responses=[
            APIResponse(
                status_code=200,
                description="Detailed health information",
                schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "components": {
                            "type": "object",
                            "properties": {
                                "database": {"type": "string"},
                                "redis": {"type": "string"},
                                "ai_engine": {"type": "string"},
                                "storage": {"type": "string"}
                            }
                        },
                        "metrics": {
                            "type": "object",
                            "properties": {
                                "cpu_usage": {"type": "number"},
                                "memory_usage": {"type": "number"},
                                "disk_usage": {"type": "number"}
                            }
                        }
                    }
                }
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_creator_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add creator management endpoints"""
    
    # List creators
    doc_generator.add_endpoint(APIEndpoint(
        path="/creators",
        method=APIMethod.GET,
        summary="List creators",
        description="Get a paginated list of creators with optional filtering",
        tags=["Creators"],
        parameters=[
            APIParameter("page", "query", "integer", "Page number (1-based)", False, 1),
            APIParameter("per_page", "query", "integer", "Items per page", False, 10),
            APIParameter("type", "query", "string", "Filter by creator type", False, None, 
                       ["musician", "blogger", "photographer", "influencer"]),
            APIParameter("status", "query", "string", "Filter by verification status", False, None,
                       ["pending", "verified", "rejected"]),
            APIParameter("search", "query", "string", "Search by name or email", False)
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="List of creators",
                schema={
                    "type": "object",
                    "properties": {
                        "creators": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Creator"}
                        },
                        "total": {"type": "integer"},
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"},
                        "total_pages": {"type": "integer"}
                    }
                }
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))
    
    # Get creator by ID
    doc_generator.add_endpoint(APIEndpoint(
        path="/creators/{creator_id}",
        method=APIMethod.GET,
        summary="Get creator by ID",
        description="Retrieve detailed information about a specific creator",
        tags=["Creators"],
        parameters=[
            APIParameter("creator_id", "path", "string", "Creator identifier", True, "creator_123")
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Creator details",
                schema={"$ref": "#/components/schemas/Creator"}
            ),
            APIResponse(
                status_code=404,
                description="Creator not found",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))
    
    # Create creator
    doc_generator.add_endpoint(APIEndpoint(
        path="/creators",
        method=APIMethod.POST,
        summary="Create new creator",
        description="Create a new creator account with the provided information",
        tags=["Creators"],
        parameters=[
            APIParameter("creator_data", "body", "object", "Creator information", True, {
                "name": "John Doe",
                "email": "john@example.com",
                "type": "musician",
                "country": "US",
                "language": "en"
            })
        ],
        responses=[
            APIResponse(
                status_code=201,
                description="Creator created successfully",
                schema={"$ref": "#/components/schemas/Creator"}
            ),
            APIResponse(
                status_code=400,
                description="Invalid input data",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            ),
            APIResponse(
                status_code=409,
                description="Creator with email already exists",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_content_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add content management endpoints"""
    
    # Upload content
    doc_generator.add_endpoint(APIEndpoint(
        path="/content/upload",
        method=APIMethod.POST,
        summary="Upload content",
        description="Upload new content for protection and management",
        tags=["Content"],
        parameters=[
            APIParameter("upload_data", "body", "object", "Content upload data", True, {
                "creator_id": "creator_123",
                "title": "My New Song",
                "description": "A beautiful acoustic piece",
                "content_type": "audio",
                "file_data": "base64_encoded_file_data"
            })
        ],
        responses=[
            APIResponse(
                status_code=201,
                description="Content uploaded successfully",
                schema={
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string"},
                        "status": {"type": "string"},
                        "upload_time": {"type": "string", "format": "date-time"},
                        "processing_eta": {"type": "integer", "description": "ETA in seconds"}
                    }
                }
            ),
            APIResponse(
                status_code=400,
                description="Invalid upload data",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            ),
            APIResponse(
                status_code=413,
                description="File too large",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))
    
    # Get content details
    doc_generator.add_endpoint(APIEndpoint(
        path="/content/{content_id}",
        method=APIMethod.GET,
        summary="Get content details",
        description="Retrieve detailed information about specific content",
        tags=["Content"],
        parameters=[
            APIParameter("content_id", "path", "string", "Content identifier", True, "content_123")
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Content details",
                schema={"$ref": "#/components/schemas/Content"}
            ),
            APIResponse(
                status_code=404,
                description="Content not found",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))
    
    # Analyze content
    doc_generator.add_endpoint(APIEndpoint(
        path="/content/{content_id}/analyze",
        method=APIMethod.POST,
        summary="Analyze content",
        description="Run AI analysis on uploaded content for protection and classification",
        tags=["Content", "Protection"],
        parameters=[
            APIParameter("content_id", "path", "string", "Content identifier", True, "content_123")
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Analysis completed",
                schema={
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string"},
                        "analysis_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "protection_level": {"type": "string", "enum": ["low", "medium", "high"]},
                        "metadata": {"type": "object"},
                        "fingerprint": {"type": "string", "description": "Content fingerprint"},
                        "analyzed_at": {"type": "string", "format": "date-time"}
                    }
                }
            ),
            APIResponse(
                status_code=404,
                description="Content not found",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            ),
            APIResponse(
                status_code=409,
                description="Content already analyzed",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_protection_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add content protection endpoints"""
    
    # Check for infringement
    doc_generator.add_endpoint(APIEndpoint(
        path="/protection/check",
        method=APIMethod.POST,
        summary="Check for content infringement",
        description="Check if content matches any protected content in the system",
        tags=["Protection"],
        parameters=[
            APIParameter("check_data", "body", "object", "Content to check", True, {
                "content_data": "base64_encoded_content",
                "content_type": "audio",
                "threshold": 0.85
            })
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Infringement check results",
                schema={
                    "type": "object",
                    "properties": {
                        "matches_found": {"type": "boolean"},
                        "matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "content_id": {"type": "string"},
                                    "similarity_score": {"type": "number"},
                                    "creator_id": {"type": "string"},
                                    "match_segments": {"type": "array"}
                                }
                            }
                        },
                        "check_timestamp": {"type": "string", "format": "date-time"}
                    }
                }
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_monetization_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add monetization endpoints"""
    
    # Get revenue reports
    doc_generator.add_endpoint(APIEndpoint(
        path="/monetization/revenue",
        method=APIMethod.GET,
        summary="Get revenue reports",
        description="Retrieve revenue reports for creators and content",
        tags=["Monetization"],
        parameters=[
            APIParameter("creator_id", "query", "string", "Filter by creator", False),
            APIParameter("start_date", "query", "string", "Start date (ISO 8601)", False),
            APIParameter("end_date", "query", "string", "End date (ISO 8601)", False),
            APIParameter("group_by", "query", "string", "Group results by", False, None, 
                       ["day", "week", "month"])
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Revenue report data",
                schema={
                    "type": "object",
                    "properties": {
                        "total_revenue": {"type": "number"},
                        "period_start": {"type": "string", "format": "date-time"},
                        "period_end": {"type": "string", "format": "date-time"},
                        "breakdown": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "period": {"type": "string"},
                                    "revenue": {"type": "number"},
                                    "transactions": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_analytics_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add analytics endpoints"""
    
    # Dashboard analytics
    doc_generator.add_endpoint(APIEndpoint(
        path="/analytics/dashboard",
        method=APIMethod.GET,
        summary="Get dashboard analytics",
        description="Retrieve key metrics for the analytics dashboard",
        tags=["Analytics"],
        parameters=[],
        responses=[
            APIResponse(
                status_code=200,
                description="Dashboard analytics data",
                schema={"$ref": "#/components/schemas/AnalyticsData"}
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_security_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add security and audit endpoints"""
    
    # Security audit
    doc_generator.add_endpoint(APIEndpoint(
        path="/security/audit",
        method=APIMethod.GET,
        summary="Get security audit report",
        description="Retrieve security audit information and compliance status",
        tags=["Security"],
        parameters=[
            APIParameter("audit_type", "query", "string", "Type of audit", False, None,
                       ["access", "data", "infrastructure", "compliance"]),
            APIParameter("start_date", "query", "string", "Audit period start", False),
            APIParameter("end_date", "query", "string", "Audit period end", False)
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Security audit report",
                schema={
                    "type": "object",
                    "properties": {
                        "audit_id": {"type": "string"},
                        "audit_type": {"type": "string"},
                        "status": {"type": "string", "enum": ["passed", "failed", "warning"]},
                        "score": {"type": "number", "minimum": 0, "maximum": 100},
                        "findings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "severity": {"type": "string"},
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "recommendation": {"type": "string"}
                                }
                            }
                        },
                        "generated_at": {"type": "string", "format": "date-time"}
                    }
                }
            )
        ],
        security=["ApiKeyAuth", "BearerAuth"]
    ))


def _add_admin_endpoints(doc_generator -> None: SwaggerDocumentationGenerator) -> None:
    """Add admin endpoints"""
    
    # System configuration
    doc_generator.add_endpoint(APIEndpoint(
        path="/admin/config",
        method=APIMethod.GET,
        summary="Get system configuration",
        description="Retrieve current system configuration (admin only)",
        tags=["Admin"],
        parameters=[],
        responses=[
            APIResponse(
                status_code=200,
                description="System configuration",
                schema={
                    "type": "object",
                    "properties": {
                        "version": {"type": "string"},
                        "environment": {"type": "string"},
                        "features": {"type": "object"},
                        "limits": {"type": "object"},
                        "security_settings": {"type": "object"}
                    }
                }
            ),
            APIResponse(
                status_code=403,
                description="Insufficient permissions",
                schema={"$ref": "#/components/schemas/ErrorResponse"}
            )
        ],
        security=["BearerAuth"]
    ))


def generate_swagger_json_file(output_path -> None: str = "swagger.json") -> None:
    """Generate and save Swagger JSON documentation to file"""
    doc_generator = create_comprehensive_api_documentation()
    swagger_spec = doc_generator.generate_openapi_spec()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(swagger_spec, f, indent=2, ensure_ascii=False)
    
    return swagger_spec


def generate_swagger_yaml_file(output_path -> None: str = "swagger.yaml") -> None:
    """Generate and save Swagger YAML documentation to file"""
    try:
        import yaml
        
        doc_generator = create_comprehensive_api_documentation()
        swagger_spec = doc_generator.generate_openapi_spec()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(swagger_spec, f, default_flow_style=False, allow_unicode=True)
        
        return swagger_spec
    except ImportError:
        print("PyYAML not installed. Install with: pip install PyYAML")
        return None


if __name__ == "__main__":
    # Generate documentation files
    print("Generating comprehensive API documentation...")
    
    # Generate JSON format
    swagger_spec = generate_swagger_json_file("/home/runner/work/Ainflue/Ainflue/docs/swagger.json")
    print(f"Generated Swagger JSON documentation with {len(swagger_spec['paths'])} endpoints")
    
    # Try to generate YAML format
    yaml_spec = generate_swagger_yaml_file("/home/runner/work/Ainflue/Ainflue/docs/swagger.yaml")
    if yaml_spec:
        print("Generated Swagger YAML documentation")
    
    # Print summary
    print(f"\nDocumentation Summary:")
    print(f"- API Title: {swagger_spec['info']['title']}")
    print(f"- Version: {swagger_spec['info']['version']}")
    print(f"- Total Endpoints: {len(swagger_spec['paths'])}")
    print(f"- Security Schemes: {len(swagger_spec['components']['securitySchemes'])}")
    print(f"- Schema Definitions: {len(swagger_spec['components']['schemas'])}")
    print(f"- Tags: {len(swagger_spec['tags'])}")