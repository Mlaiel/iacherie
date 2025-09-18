#!/usr/bin/env python3
"""OpenAPI Spec Template - Complete OpenAPI 3.0 specification generator"""

class OpenAPISpecTemplate:
    """OpenAPI 3.0 specification template"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.spec_template = {
            "openapi": "3.0.0",
            "info": {
                "title": service_name,
                "version": "1.0.0"
            },
            "servers": [
                {"url": "http://localhost:8080", "description": "Development server"}
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }