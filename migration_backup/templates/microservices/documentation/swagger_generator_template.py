#!/usr/bin/env python3
"""Swagger Generator Template - OpenAPI/Swagger documentation generation"""

import json
from typing import Dict, Any

class SwaggerGeneratorTemplate:
    """Swagger/OpenAPI documentation generator"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": service_name,
                "version": version,
                "description": f"API documentation for {service_name}"
            },
            "paths": {}
        }
    
    def add_path(self, path: str, method: str, operation_spec: Dict[str, Any]):
        """Add API path to spec"""
        if path not in self.spec["paths"]:
            self.spec["paths"][path] = {}
        
        self.spec["paths"][path][method.lower()] = operation_spec
    
    def generate_json(self) -> str:
        """Generate OpenAPI JSON specification"""
        return json.dumps(self.spec, indent=2)