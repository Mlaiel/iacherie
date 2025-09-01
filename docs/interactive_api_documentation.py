"""Enhanced Interactive API Documentation Generator
Creates comprehensive OpenAPI/Swagger documentation with interactive features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import inspect
import ast
import importlib
from datetime import datetime

class APIMethod(Enum):
    """HTTP methods supported by the API."""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    HEAD = "head"

@dataclass
class APIParameter:
    """Enhanced API parameter definition with validation and examples."""
    name: str
    param_type: str  # "query", "path", "header", "body", "formData"
    data_type: str
    description: str
    required: bool = True
    example: Any = None
    enum_values: Optional[List[str]] = None
    format: Optional[str] = None  # "date", "date-time", "email", "uri", etc.
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    default: Any = None

@dataclass
class APIResponse:
    """Enhanced API response definition with detailed schemas."""
    status_code: int
    description: str
    schema: Dict[str, Any]
    examples: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Dict[str, Any]]] = None

@dataclass
class APIEndpoint:
    """Comprehensive API endpoint definition."""
    path: str
    method: APIMethod
    summary: str
    description: str
    tags: List[str]
    parameters: List[APIParameter]
    responses: List[APIResponse]
    security: Optional[List[str]] = None
    deprecated: bool = False
    operationId: Optional[str] = None
    consumes: Optional[List[str]] = None
    produces: Optional[List[str]] = None

class InteractiveAPIDocumentationGenerator:
    """Enhanced generator for interactive API documentation."""
    
    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self.components = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                },
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
                "OAuth2": {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": "https://api.ainflue.com/oauth/authorize",
                            "tokenUrl": "https://api.ainflue.com/oauth/token",
                            "scopes": {
                                "read": "Read access",
                                "write": "Write access",
                                "admin": "Admin access"
                            }
                        }
                    }
                }
            }
        }
        self.tags = []
        
    def add_endpoint(self, endpoint: APIEndpoint):
        """Add an endpoint to the documentation."""
        self.endpoints.append(endpoint)
        
        # Auto-add tags if not exists
        for tag in endpoint.tags:
            if not any(t["name"] == tag for t in self.tags):
                self.tags.append({
                    "name": tag,
                    "description": f"Operations related to {tag}"
                })
    
    def generate_interactive_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification with interactive features."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Ainflue AI Platform API",
                "description": self._get_api_description(),
                "version": "1.0.0",
                "termsOfService": "https://ainflue.com/terms",
                "contact": {
                    "name": "Fahed Mlaiel",
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
            "paths": self._generate_paths_with_examples(),
            "components": self.components,
            "security": [
                {"ApiKeyAuth": []},
                {"BearerAuth": []},
                {"OAuth2": ["read", "write"]}
            ],
            "tags": self.tags,
            "externalDocs": {
                "description": "Complete Documentation",
                "url": "https://docs.ainflue.com"
            }
        }
        
        return spec
    
    def _get_api_description(self) -> str:
        """Get comprehensive API description."""
        return """
# Ainflue AI Platform API

The Ainflue AI Platform provides a comprehensive suite of APIs for content protection, monetization, and AI-powered content analysis.

## Features

- **Content Protection**: Advanced fingerprinting and copyright protection
- **AI Agents**: Intelligent content processing and analysis
- **Monetization**: Revenue optimization and payment processing
- **Analytics**: Comprehensive performance and business insights
- **Multi-language Support**: 644+ languages supported
- **Real-time Processing**: Live content monitoring and analysis

## Authentication

The API supports multiple authentication methods:
- API Key authentication for simple access
- JWT Bearer tokens for user sessions
- OAuth2 for third-party integrations

## Rate Limiting

All endpoints are rate-limited to ensure fair usage:
- Free tier: 1000 requests/hour
- Pro tier: 10000 requests/hour
- Enterprise: Custom limits

## SDKs Available

- Python SDK
- JavaScript/Node.js SDK
- PHP SDK
- Java SDK

## Support

For technical support, contact mlaiel@live.de or visit https://ainflue.com/support
        """
    
    def _generate_paths_with_examples(self) -> Dict[str, Any]:
        """Generate paths section with comprehensive examples."""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            operation = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "operationId": endpoint.operationId or f"{endpoint.method.value}_{endpoint.path.replace('/', '_').replace('{', '').replace('}', '')}",
                "tags": endpoint.tags,
                "parameters": self._convert_parameters_with_examples(endpoint.parameters),
                "responses": self._convert_responses_with_examples(endpoint.responses)
            }
            
            if endpoint.security:
                operation["security"] = [{scheme: []} for scheme in endpoint.security]
            
            if endpoint.deprecated:
                operation["deprecated"] = True
                
            if endpoint.consumes:
                operation["consumes"] = endpoint.consumes
                
            if endpoint.produces:
                operation["produces"] = endpoint.produces
            
            # Add request body for POST/PUT operations
            if endpoint.method in [APIMethod.POST, APIMethod.PUT, APIMethod.PATCH]:
                body_params = [p for p in endpoint.parameters if p.param_type == "body"]
                if body_params:
                    operation["requestBody"] = self._generate_request_body_with_examples(body_params[0])
            
            paths[endpoint.path][endpoint.method.value] = operation
        
        return paths
    
    def _convert_parameters_with_examples(self, parameters: List[APIParameter]) -> List[Dict[str, Any]]:
        """Convert parameters with comprehensive examples and validation."""
        converted = []
        
        for param in parameters:
            if param.param_type == "body":
                continue  # Body parameters handled separately
                
            param_spec = {
                "name": param.name,
                "in": param.param_type,
                "description": param.description,
                "required": param.required,
                "schema": {
                    "type": param.data_type
                }
            }
            
            if param.format:
                param_spec["schema"]["format"] = param.format
                
            if param.enum_values:
                param_spec["schema"]["enum"] = param.enum_values
                
            if param.minimum is not None:
                param_spec["schema"]["minimum"] = param.minimum
                
            if param.maximum is not None:
                param_spec["schema"]["maximum"] = param.maximum
                
            if param.pattern:
                param_spec["schema"]["pattern"] = param.pattern
                
            if param.default is not None:
                param_spec["schema"]["default"] = param.default
            
            if param.example is not None:
                param_spec["example"] = param.example
            
            converted.append(param_spec)
        
        return converted
    
    def _convert_responses_with_examples(self, responses: List[APIResponse]) -> Dict[str, Any]:
        """Convert responses with detailed examples."""
        converted = {}
        
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
                
            if response.headers:
                response_spec["headers"] = response.headers
            
            converted[str(response.status_code)] = response_spec
        
        return converted
    
    def _generate_request_body_with_examples(self, body_param: APIParameter) -> Dict[str, Any]:
        """Generate request body with examples."""
        return {
            "description": body_param.description,
            "required": body_param.required,
            "content": {
                "application/json": {
                    "schema": {
                        "type": body_param.data_type
                    },
                    "example": body_param.example
                }
            }
        }
    
    def load_endpoints_from_fastapi_app(self, app_module_path: str = "api.asgi"):
        """Automatically load endpoints from FastAPI application."""
        try:
            # This would introspect the FastAPI app and generate documentation
            # Implementation would analyze route decorators and docstrings
            pass
        except Exception as e:
            print(f"Could not auto-load endpoints: {e}")
    
    def add_common_endpoints(self):
        """Add common platform endpoints with examples."""
        # Health check endpoint
        self.add_endpoint(APIEndpoint(
            path="/health",
            method=APIMethod.GET,
            summary="Health Check",
            description="Check the health status of the API",
            tags=["Health"],
            parameters=[],
            responses=[
                APIResponse(
                    status_code=200,
                    description="API is healthy",
                    schema={
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "healthy"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "version": {"type": "string", "example": "1.0.0"},
                            "uptime": {"type": "number", "example": 3600}
                        }
                    },
                    examples={
                        "healthy": {
                            "summary": "Healthy response",
                            "value": {
                                "status": "healthy",
                                "timestamp": "2025-01-01T12:00:00Z",
                                "version": "1.0.0",
                                "uptime": 3600
                            }
                        }
                    }
                )
            ]
        ))
        
        # Authentication endpoint
        self.add_endpoint(APIEndpoint(
            path="/auth/login",
            method=APIMethod.POST,
            summary="User Login",
            description="Authenticate user and return JWT token",
            tags=["Authentication"],
            parameters=[
                APIParameter(
                    name="credentials",
                    param_type="body",
                    data_type="object",
                    description="User login credentials",
                    example={
                        "email": "user@example.com",
                        "password": "secure_password"
                    }
                )
            ],
            responses=[
                APIResponse(
                    status_code=200,
                    description="Login successful",
                    schema={
                        "type": "object",
                        "properties": {
                            "access_token": {"type": "string"},
                            "token_type": {"type": "string", "example": "bearer"},
                            "expires_in": {"type": "integer", "example": 3600},
                            "user": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "email": {"type": "string"},
                                    "name": {"type": "string"}
                                }
                            }
                        }
                    }
                ),
                APIResponse(
                    status_code=401,
                    description="Invalid credentials",
                    schema={
                        "type": "object",
                        "properties": {
                            "error": {"type": "string", "example": "Invalid credentials"},
                            "code": {"type": "string", "example": "AUTH_FAILED"}
                        }
                    }
                )
            ]
        ))
    
    def generate_html_documentation(self) -> str:
        """Generate standalone HTML documentation with Swagger UI."""
        spec_json = json.dumps(self.generate_interactive_spec(), indent=2)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Ainflue AI Platform API Documentation" />
    <title>Ainflue API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        .swagger-ui .topbar {{ display: none }}
        .swagger-ui .info .title {{ color: #1f2937 }}
        .swagger-ui .scheme-container {{ background: #f9fafb; padding: 1rem; border-radius: 0.5rem; }}
        .custom-header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            margin-bottom: 2rem;
        }}
        .custom-header h1 {{ margin: 0; font-size: 2.5rem; }}
        .custom-header p {{ margin: 0.5rem 0 0 0; opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="custom-header">
        <h1>🚀 Ainflue AI Platform API</h1>
        <p>Comprehensive API Documentation with Interactive Examples</p>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {{
            window.ui = SwaggerUIBundle({{
                url: null,
                spec: {spec_json},
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone,
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                docExpansion: "list",
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                tryItOutEnabled: true,
                requestInterceptor: (request) => {{
                    // Add custom headers or modify requests
                    request.headers['X-API-Version'] = '1.0';
                    return request;
                }},
                responseInterceptor: (response) => {{
                    // Handle responses
                    return response;
                }}
            }});
        }};
    </script>
</body>
</html>
        """
        
        return html
    
    def save_documentation(self, output_dir: str = "docs/api"):
        """Save all documentation formats."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate spec
        spec = self.generate_interactive_spec()
        
        # Save OpenAPI JSON
        with open(output_path / "openapi.json", "w") as f:
            json.dump(spec, f, indent=2)
        
        # Save OpenAPI YAML
        with open(output_path / "openapi.yaml", "w") as f:
            yaml.dump(spec, f, default_flow_style=False)
        
        # Save HTML documentation
        html_doc = self.generate_html_documentation()
        with open(output_path / "index.html", "w") as f:
            f.write(html_doc)
        
        print(f"✅ API documentation saved to {output_path}")
        print(f"📖 View at: file://{output_path.absolute()}/index.html")

def main():
    """Generate complete API documentation."""
    generator = InteractiveAPIDocumentationGenerator()
    
    # Add common endpoints
    generator.add_common_endpoints()
    
    # Try to auto-load from FastAPI app
    generator.load_endpoints_from_fastapi_app()
    
    # Save documentation
    generator.save_documentation()

if __name__ == "__main__":
    main()