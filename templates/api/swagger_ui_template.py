"""Swagger UI Template for Ainflue Platform

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Version: 1.0.0
"""

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class SwaggerUICustomizer:
    """Enhanced Swagger UI with customization and security features"""
    
    def __init__(
        self,
        app: FastAPI,
        title: str = "Ainflue API Documentation",
        description: str = "Enterprise Creator Economy Platform APIs",
        version: str = "1.0.0",
        terms_of_service: str = "https://ainflue.com/terms",
        contact_info: Optional[Dict[str, str]] = None,
        license_info: Optional[Dict[str, str]] = None,
        servers: Optional[List[Dict[str, str]]] = None,
        security_schemes: Optional[Dict[str, Any]] = None,
        enable_authentication: bool = True,
        custom_css: Optional[str] = None,
        custom_js: Optional[str] = None,
        theme: str = "default",
        enable_try_it_out: bool = True,
        enable_download: bool = True,
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json"
    ):
        self.app = app
        self.title = title
        self.description = description
        self.version = version
        self.terms_of_service = terms_of_service
        self.contact_info = contact_info or {
            "name": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "url": "https://ainflue.com"
        }
        self.license_info = license_info or {
            "name": "Proprietary License",
            "url": "https://ainflue.com/license"
        }
        self.servers = servers or [
            {"url": "https://api.ainflue.com", "description": "Production server"},
            {"url": "https://staging-api.ainflue.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
        self.security_schemes = security_schemes or self._default_security_schemes()
        self.enable_authentication = enable_authentication
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.theme = theme
        self.enable_try_it_out = enable_try_it_out
        self.enable_download = enable_download
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        
        # Security
        self.security = HTTPBearer() if enable_authentication else None
        
        # Initialize Swagger UI
        self._setup_swagger_ui()
        
        logger.info(f"Swagger UI initialized for {title}")
    
    def _default_security_schemes(self) -> Dict[str, Any]:
        """Default security schemes"""
        return {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://auth.ainflue.com/oauth/authorize",
                        "tokenUrl": "https://auth.ainflue.com/oauth/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access",
                            "admin": "Admin access"
                        }
                    }
                }
            }
        }
    
    def _setup_swagger_ui(self):
        """Setup Swagger UI with customizations"""
        
        # Update OpenAPI schema
        self._update_openapi_schema()
        
        # Add custom Swagger UI endpoint
        @self.app.get(self.docs_url, response_class=HTMLResponse, include_in_schema=False)
        async def custom_swagger_ui_html(request: Request):
            return self._generate_swagger_html(request)
        
        # Add ReDoc endpoint
        @self.app.get(self.redoc_url, response_class=HTMLResponse, include_in_schema=False)
        async def custom_redoc_html(request: Request):
            return self._generate_redoc_html(request)
        
        # Add OpenAPI JSON endpoint with authentication
        @self.app.get(self.openapi_url, include_in_schema=False)
        async def get_openapi_schema(
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security) if self.enable_authentication else None
        ):
            if self.enable_authentication and not self._verify_documentation_access(credentials):
                raise HTTPException(status_code=401, detail="Documentation access denied")
            
            return self.app.openapi()
        
        # Add API specification downloads
        @self.app.get("/api/spec/yaml", include_in_schema=False)
        async def download_openapi_yaml(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security) if self.enable_authentication else None
        ):
            if self.enable_authentication and not self._verify_documentation_access(credentials):
                raise HTTPException(status_code=401, detail="Documentation access denied")
            
            openapi_schema = self.app.openapi()
            yaml_content = yaml.dump(openapi_schema, default_flow_style=False)
            
            return Response(
                content=yaml_content,
                media_type="application/x-yaml",
                headers={"Content-Disposition": f"attachment; filename={self.title.lower().replace(' ', '_')}_api_spec.yaml"}
            )
        
        @self.app.get("/api/spec/json", include_in_schema=False)
        async def download_openapi_json(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security) if self.enable_authentication else None
        ):
            if self.enable_authentication and not self._verify_documentation_access(credentials):
                raise HTTPException(status_code=401, detail="Documentation access denied")
            
            openapi_schema = self.app.openapi()
            
            return Response(
                content=json.dumps(openapi_schema, indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={self.title.lower().replace(' ', '_')}_api_spec.json"}
            )
    
    def _verify_documentation_access(self, credentials: Optional[HTTPAuthorizationCredentials]) -> bool:
        """Verify access to documentation"""
        if not credentials:
            return False
        
        # Add your authentication logic here
        # For example, verify JWT token or API key
        token = credentials.credentials
        
        # Mock verification - implement actual token validation
        if token == "demo-token" or len(token) > 10:
            return True
        
        return False
    
    def _update_openapi_schema(self):
        """Update OpenAPI schema with custom information"""
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema
            
            openapi_schema = self.app.openapi()
            
            # Update basic info
            openapi_schema["info"]["title"] = self.title
            openapi_schema["info"]["description"] = self._get_enhanced_description()
            openapi_schema["info"]["version"] = self.version
            openapi_schema["info"]["termsOfService"] = self.terms_of_service
            openapi_schema["info"]["contact"] = self.contact_info
            openapi_schema["info"]["license"] = self.license_info
            
            # Add servers
            openapi_schema["servers"] = self.servers
            
            # Add security schemes
            if "components" not in openapi_schema:
                openapi_schema["components"] = {}
            openapi_schema["components"]["securitySchemes"] = self.security_schemes
            
            # Add global security requirement
            openapi_schema["security"] = [{"BearerAuth": []}]
            
            # Add custom extensions
            openapi_schema["x-logo"] = {
                "url": "https://ainflue.com/logo.png",
                "altText": "Ainflue Logo"
            }
            
            # Add tags with descriptions
            openapi_schema["tags"] = self._get_api_tags()
            
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi
    
    def _get_enhanced_description(self) -> str:
        """Get enhanced API description with markdown"""
        return f"""
{self.description}

## 🚀 Creator Economy Platform

The Ainflue API provides comprehensive functionality for content creators, collaboration tools, and monetization systems.

### 🔑 Key Features

- **Creator Management**: Complete creator profile and content management
- **AI Processing**: Advanced content analysis and optimization
- **Collaboration Tools**: Real-time collaboration and communication
- **Monetization**: Multiple revenue streams and payment processing
- **Analytics**: Detailed performance metrics and insights
- **Security**: Enterprise-grade security and compliance

### 🔒 Authentication

This API uses JWT Bearer tokens for authentication. Include your token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### 📊 Rate Limiting

API calls are rate limited based on your subscription plan:
- **Free Plan**: 1,000 requests/hour
- **Pro Plan**: 10,000 requests/hour  
- **Enterprise Plan**: Unlimited

### 🆘 Support

For technical support and questions:
- **Email**: {self.contact_info['email']}
- **Documentation**: [API Docs](https://docs.ainflue.com)
- **Status Page**: [status.ainflue.com](https://status.ainflue.com)

### ⚠️ Legal Notice

© 2025 Fahed Mlaiel. All rights reserved. This API is proprietary software.
Commercial use requires explicit written authorization.
"""
    
    def _get_api_tags(self) -> List[Dict[str, str]]:
        """Get API tags with descriptions"""
        return [
            {
                "name": "Authentication",
                "description": "User authentication and authorization endpoints"
            },
            {
                "name": "Creators",
                "description": "Creator profile and management operations"
            },
            {
                "name": "Content",
                "description": "Content upload, processing, and management"
            },
            {
                "name": "Collaboration",
                "description": "Real-time collaboration and communication"
            },
            {
                "name": "Analytics",
                "description": "Performance metrics and analytics"
            },
            {
                "name": "Monetization",
                "description": "Revenue streams and payment processing"
            },
            {
                "name": "Admin",
                "description": "Administrative operations (requires admin access)"
            }
        ]
    
    def _generate_swagger_html(self, request: Request) -> str:
        """Generate custom Swagger UI HTML"""
        
        # Custom CSS
        custom_css = self.custom_css or self._get_default_css()
        
        # Custom JavaScript
        custom_js = self.custom_js or self._get_default_js()
        
        # Swagger UI configuration
        swagger_config = {
            "deepLinking": True,
            "displayOperationId": False,
            "defaultModelsExpandDepth": 1,
            "defaultModelExpandDepth": 1,
            "defaultModelRendering": "example",
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": self.enable_try_it_out,
            "validatorUrl": None,
            "supportedSubmitMethods": ["get", "post", "put", "delete", "patch", "head", "options"],
            "presets": [
                "SwaggerUIBundle.presets.apis",
                "SwaggerUIStandalonePreset"
            ],
            "plugins": [
                "SwaggerUIBundle.plugins.DownloadUrl"
            ],
            "layout": "StandaloneLayout"
        }
        
        html_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <link rel="icon" type="image/png" href="https://ainflue.com/favicon.png" sizes="32x32" />
    <style>
        {{ custom_css }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    
    <!-- Swagger UI Bundle -->
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '{{ openapi_url }}',
                dom_id: '#swagger-ui',
                ...{{ swagger_config | tojson }},
                requestInterceptor: function(request) {
                    // Add authentication header if available
                    const token = localStorage.getItem('swagger_auth_token');
                    if (token) {
                        request.headers['Authorization'] = 'Bearer ' + token;
                    }
                    return request;
                },
                onComplete: function() {
                    // Add custom functionality after UI loads
                    addAuthenticationUI();
                    addDownloadButtons();
                }
            });
            
            window.ui = ui;
        };
        
        function addAuthenticationUI() {
            // Add authentication input at the top
            const authHtml = `
                <div id="auth-container" style="margin: 20px 0; padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">
                    <h4>🔐 Authentication</h4>
                    <div style="margin: 10px 0;">
                        <label for="auth-token">JWT Token:</label>
                        <input type="password" id="auth-token" placeholder="Enter your JWT token" style="width: 300px; margin-left: 10px; padding: 5px;" />
                        <button onclick="setAuthToken()" style="margin-left: 10px; padding: 5px 15px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;">Set Token</button>
                        <button onclick="clearAuthToken()" style="margin-left: 5px; padding: 5px 15px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">Clear</button>
                    </div>
                    <div id="auth-status" style="margin-top: 10px; font-size: 14px;"></div>
                </div>
            `;
            
            const container = document.querySelector('.swagger-ui');
            if (container) {
                container.insertAdjacentHTML('afterbegin', authHtml);
            }
            
            // Load existing token
            const existingToken = localStorage.getItem('swagger_auth_token');
            if (existingToken) {
                document.getElementById('auth-token').value = existingToken;
                updateAuthStatus('Token loaded from storage', 'success');
            }
        }
        
        function setAuthToken() {
            const token = document.getElementById('auth-token').value;
            if (token) {
                localStorage.setItem('swagger_auth_token', token);
                updateAuthStatus('Authentication token set successfully', 'success');
                
                // Refresh the UI to apply authentication
                window.location.reload();
            } else {
                updateAuthStatus('Please enter a valid token', 'error');
            }
        }
        
        function clearAuthToken() {
            localStorage.removeItem('swagger_auth_token');
            document.getElementById('auth-token').value = '';
            updateAuthStatus('Authentication token cleared', 'info');
            window.location.reload();
        }
        
        function updateAuthStatus(message, type) {
            const statusEl = document.getElementById('auth-status');
            const colors = {
                success: '#28a745',
                error: '#dc3545',
                info: '#17a2b8'
            };
            statusEl.textContent = message;
            statusEl.style.color = colors[type] || '#333';
        }
        
        function addDownloadButtons() {
            if (!{{ enable_download }}) return;
            
            const downloadHtml = `
                <div id="download-container" style="margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px;">
                    <h4>📥 Download API Specification</h4>
                    <button onclick="downloadSpec('json')" style="margin: 5px; padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">Download JSON</button>
                    <button onclick="downloadSpec('yaml')" style="margin: 5px; padding: 8px 15px; background: #17a2b8; color: white; border: none; border-radius: 3px; cursor: pointer;">Download YAML</button>
                </div>
            `;
            
            const authContainer = document.getElementById('auth-container');
            if (authContainer) {
                authContainer.insertAdjacentHTML('afterend', downloadHtml);
            }
        }
        
        function downloadSpec(format) {
            const token = localStorage.getItem('swagger_auth_token');
            const headers = token ? { 'Authorization': 'Bearer ' + token } : {};
            
            fetch(`/api/spec/${format}`, { headers })
                .then(response => {
                    if (!response.ok) throw new Error('Download failed');
                    return response.blob();
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `{{ title.lower().replace(' ', '_') }}_api_spec.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                })
                .catch(error => {
                    alert('Download failed: ' + error.message);
                });
        }
        
        {{ custom_js }}
    </script>
</body>
</html>
        """)
        
        return html_template.render(
            title=self.title,
            openapi_url=self.openapi_url,
            custom_css=custom_css,
            custom_js=custom_js,
            swagger_config=swagger_config,
            enable_download=json.dumps(self.enable_download).lower()
        )
    
    def _generate_redoc_html(self, request: Request) -> str:
        """Generate custom ReDoc HTML"""
        
        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }} - API Documentation (ReDoc)</title>
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; }
        redoc { display: block; }
    </style>
</head>
<body>
    <redoc spec-url='{{ openapi_url }}'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>
        """)
        
        return html_template.render(
            title=self.title,
            openapi_url=self.openapi_url
        )
    
    def _get_default_css(self) -> str:
        """Get default custom CSS"""
        if self.theme == "dark":
            return """
                .swagger-ui {
                    filter: invert(1) hue-rotate(180deg);
                }
                .swagger-ui .scheme-container {
                    filter: invert(1) hue-rotate(180deg);
                }
            """
        
        return """
            .swagger-ui .topbar {
                background-color: #2d3748;
                border-bottom: 1px solid #4a5568;
            }
            .swagger-ui .topbar .download-url-wrapper .select-label {
                color: #e2e8f0;
            }
            .swagger-ui .info hgroup.main .title {
                color: #2d3748;
            }
            .swagger-ui .info .description p {
                color: #4a5568;
            }
            .swagger-ui .auth-wrapper {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            .swagger-ui .btn.authorize {
                background-color: #4299e1;
                border-color: #4299e1;
            }
            .swagger-ui .btn.authorize:hover {
                background-color: #3182ce;
                border-color: #3182ce;
            }
            .swagger-ui .opblock .opblock-summary-operation-id,
            .swagger-ui .opblock .opblock-summary-path,
            .swagger-ui .opblock .opblock-summary-description {
                font-family: 'Roboto', sans-serif;
            }
            .swagger-ui .parameter__name {
                font-weight: 600;
            }
            .swagger-ui .response-col_status {
                font-weight: bold;
            }
            .swagger-ui .response-col_description__inner p {
                margin: 0;
            }
            
            /* Custom branding */
            .swagger-ui .topbar .download-url-wrapper:after {
                content: "Powered by Ainflue";
                color: #e2e8f0;
                font-size: 12px;
                margin-left: 20px;
            }
            
            /* Authentication status indicator */
            .auth-indicator {
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                z-index: 1000;
            }
            .auth-indicator.authenticated {
                background-color: #28a745;
                color: white;
            }
            .auth-indicator.unauthenticated {
                background-color: #dc3545;
                color: white;
            }
        """
    
    def _get_default_js(self) -> str:
        """Get default custom JavaScript"""
        return """
            // Add authentication status indicator
            function addAuthIndicator() {
                const token = localStorage.getItem('swagger_auth_token');
                const indicator = document.createElement('div');
                indicator.className = 'auth-indicator ' + (token ? 'authenticated' : 'unauthenticated');
                indicator.textContent = token ? '🔒 Authenticated' : '🔓 Not Authenticated';
                document.body.appendChild(indicator);
            }
            
            // Initialize
            setTimeout(addAuthIndicator, 1000);
            
            // Analytics tracking
            if (typeof gtag === 'function') {
                gtag('event', 'page_view', {
                    page_title: 'API Documentation',
                    page_location: window.location.href
                });
            }
            
            // Custom keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl+/ to focus search
                if (e.ctrlKey && e.key === '/') {
                    e.preventDefault();
                    const searchInput = document.querySelector('.swagger-ui .filter input');
                    if (searchInput) searchInput.focus();
                }
            });
        """

# Example usage function
def setup_swagger_ui(
    app: FastAPI,
    title: str = "Ainflue Creator Economy API",
    description: str = "Enterprise-grade APIs for content creators and collaboration",
    version: str = "1.0.0",
    enable_authentication: bool = True,
    theme: str = "default"
) -> SwaggerUICustomizer:
    """Setup enhanced Swagger UI for FastAPI app"""
    
    return SwaggerUICustomizer(
        app=app,
        title=title,
        description=description,
        version=version,
        enable_authentication=enable_authentication,
        theme=theme,
        contact_info={
            "name": "Fahed Mlaiel - Technical Lead",
            "email": "mlaiel@live.de",
            "url": "https://ainflue.com"
        },
        license_info={
            "name": "Proprietary License",
            "url": "https://ainflue.com/license"
        }
    )

# Configuration template
SWAGGER_UI_CONFIG = {
    "title": "Ainflue Creator Economy API",
    "description": "Enterprise-grade APIs for content creators and collaboration",
    "version": "1.0.0",
    "theme": "default",  # "default" or "dark"
    "enable_authentication": True,
    "enable_try_it_out": True,
    "enable_download": True,
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
    "servers": [
        {"url": "https://api.ainflue.com", "description": "Production server"},
        {"url": "https://staging-api.ainflue.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"}
    ],
    "security_schemes": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
}

if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Setup Swagger UI
    swagger_ui = setup_swagger_ui(
        app,
        title="Ainflue API Documentation",
        description="Creator Economy Platform APIs",
        version="1.0.0"
    )
    
    # Add a sample endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "ainflue-api"}
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)