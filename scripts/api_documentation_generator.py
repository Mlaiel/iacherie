#!/usr/bin/env python3
"""
API Documentation Generator - Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Backend Senior + DevOps Engineer + Lead Dev IA
Purpose: Enterprise API documentation generation and validation
"""

import asyncio
import ast
import inspect
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
import importlib.util
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIDocumentationGenerator:
    """Enterprise API documentation generator for FastAPI and Python services"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path("/home/runner/work/Ainfluencer/Ainfluencer")
        self.docs_output = self.project_root / "docs" / "api"
        self.docs_output.mkdir(parents=True, exist_ok=True)
        
        # API discovery patterns
        self.api_patterns = {
            "fastapi_routes": [
                "api/**/*.py",
                "backend/**/*.py", 
                "routers/**/*.py",
                "endpoints/**/*.py"
            ],
            "websocket_routes": [
                "ws/**/*.py",
                "websockets/**/*.py",
                "realtime/**/*.py"
            ],
            "ml_endpoints": [
                "ml/**/*.py",
                "ai_processing/**/*.py",
                "models/**/*.py"
            ]
        }
        
        self.discovered_apis = {
            "rest_endpoints": [],
            "websocket_endpoints": [],
            "ml_endpoints": [],
            "models": [],
            "schemas": []
        }
        
        self.stats = {
            "files_processed": 0,
            "endpoints_found": 0,
            "models_found": 0,
            "schemas_generated": 0
        }
    
    async def discover_api_files(self) -> List[Path]:
        """Discover all API-related Python files"""
        api_files = []
        
        for category, patterns in self.api_patterns.items():
            for pattern in patterns:
                matches = list(self.project_root.rglob(pattern))
                for match in matches:
                    if match.is_file() and match.suffix == '.py':
                        api_files.append(match)
        
        # Remove duplicates
        return list(set(api_files))
    
    def extract_fastapi_routes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract FastAPI route definitions from Python file"""
        routes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for FastAPI route decorators
                    for decorator in node.decorator_list:
                        route_info = self._parse_fastapi_decorator(decorator, node, content)
                        if route_info:
                            route_info["file_path"] = str(file_path)
                            route_info["function_name"] = node.name
                            route_info["docstring"] = ast.get_docstring(node)
                            route_info["parameters"] = self._extract_function_parameters(node)
                            routes.append(route_info)
                            self.stats["endpoints_found"] += 1
        
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return routes
    
    def _parse_fastapi_decorator(self, decorator: ast.expr, func_node: ast.FunctionDef, content: str) -> Optional[Dict[str, Any]]:
        """Parse FastAPI route decorator to extract route information"""
        route_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']
        
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                method_name = decorator.func.attr.lower()
                if method_name in route_methods:
                    route_info = {
                        "method": method_name.upper(),
                        "path": None,
                        "tags": [],
                        "summary": None,
                        "description": None,
                        "response_model": None,
                        "status_code": 200,
                        "dependencies": []
                    }
                    
                    # Extract path from first argument
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            route_info["path"] = decorator.args[0].value
                    
                    # Extract keyword arguments
                    for keyword in decorator.keywords:
                        if keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                            route_info["tags"] = [elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)]
                        elif keyword.arg == "summary" and isinstance(keyword.value, ast.Constant):
                            route_info["summary"] = keyword.value.value
                        elif keyword.arg == "description" and isinstance(keyword.value, ast.Constant):
                            route_info["description"] = keyword.value.value
                        elif keyword.arg == "status_code" and isinstance(keyword.value, ast.Constant):
                            route_info["status_code"] = keyword.value.value
                        elif keyword.arg == "response_model":
                            route_info["response_model"] = self._extract_type_annotation(keyword.value)
                    
                    return route_info
        
        return None
    
    def _extract_function_parameters(self, func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters with type annotations"""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": None,
                "default": None,
                "required": True
            }
            
            # Extract type annotation
            if arg.annotation:
                param_info["type"] = self._extract_type_annotation(arg.annotation)
            
            parameters.append(param_info)
        
        # Handle defaults
        defaults = func_node.args.defaults
        if defaults:
            # Map defaults to parameters (defaults are for the last n parameters)
            num_defaults = len(defaults)
            num_params = len(parameters)
            
            for i, default in enumerate(defaults):
                param_index = num_params - num_defaults + i
                if param_index < len(parameters):
                    parameters[param_index]["required"] = False
                    if isinstance(default, ast.Constant):
                        parameters[param_index]["default"] = default.value
        
        return parameters
    
    def _extract_type_annotation(self, annotation: ast.expr) -> str:
        """Extract type annotation as string"""
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
            elif isinstance(annotation, ast.Subscript):
                # Handle generic types like List[str], Dict[str, int]
                value = self._extract_type_annotation(annotation.value)
                if isinstance(annotation.slice, ast.Tuple):
                    slice_types = [self._extract_type_annotation(elt) for elt in annotation.slice.elts]
                    return f"{value}[{', '.join(slice_types)}]"
                else:
                    slice_type = self._extract_type_annotation(annotation.slice)
                    return f"{value}[{slice_type}]"
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            else:
                return "Any"
        except Exception:
            return "Any"
    
    def extract_pydantic_models(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Pydantic model definitions"""
        models = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from BaseModel
                    is_pydantic_model = any(
                        isinstance(base, ast.Name) and base.id == "BaseModel" or
                        isinstance(base, ast.Attribute) and base.attr == "BaseModel"
                        for base in node.bases
                    )
                    
                    if is_pydantic_model:
                        model_info = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "fields": [],
                            "file_path": str(file_path)
                        }
                        
                        # Extract fields
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                field_info = {
                                    "name": item.target.id,
                                    "type": self._extract_type_annotation(item.annotation),
                                    "required": True,
                                    "default": None
                                }
                                
                                # Check for default value
                                if item.value:
                                    if isinstance(item.value, ast.Constant):
                                        field_info["default"] = item.value.value
                                        field_info["required"] = False
                                    elif isinstance(item.value, ast.Call):
                                        # Handle Field() calls
                                        if isinstance(item.value.func, ast.Name) and item.value.func.id == "Field":
                                            field_info["required"] = False
                                
                                model_info["fields"].append(field_info)
                        
                        models.append(model_info)
                        self.stats["models_found"] += 1
        
        except Exception as e:
            logger.error(f"Error extracting models from {file_path}: {e}")
        
        return models
    
    def extract_websocket_routes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract WebSocket route definitions"""
        websocket_routes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for WebSocket decorators and route patterns
            websocket_patterns = [
                r'@app\.websocket\(["\']([^"\']+)["\']',
                r'@router\.websocket\(["\']([^"\']+)["\']',
                r'websocket\(["\']([^"\']+)["\']'
            ]
            
            for pattern in websocket_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    websocket_info = {
                        "path": match.group(1),
                        "file_path": str(file_path),
                        "type": "websocket"
                    }
                    websocket_routes.append(websocket_info)
        
        except Exception as e:
            logger.error(f"Error extracting WebSocket routes from {file_path}: {e}")
        
        return websocket_routes
    
    def generate_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 schema from discovered endpoints"""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Ainflue Platform API",
                "version": "1.0.0",
                "description": "Enterprise AI-powered content protection and monetization platform",
                "contact": {
                    "name": "Fahed Mlaiel",
                    "email": "mlaiel@live.de"
                },
                "license": {
                    "name": "Proprietary",
                    "url": "https://github.com/Mlaiel/Ainfluencer"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "Development server"
                },
                {
                    "url": "https://api.ainflue.com",
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
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
            },
            "security": [
                {"BearerAuth": []},
                {"ApiKeyAuth": []}
            ]
        }
        
        # Add paths from discovered REST endpoints
        for endpoint in self.discovered_apis["rest_endpoints"]:
            path = endpoint.get("path", "/")
            method = endpoint.get("method", "GET").lower()
            
            if path not in schema["paths"]:
                schema["paths"][path] = {}
            
            schema["paths"][path][method] = {
                "summary": endpoint.get("summary", f"{method.upper()} {path}"),
                "description": endpoint.get("description", endpoint.get("docstring", "")),
                "tags": endpoint.get("tags", ["default"]),
                "parameters": self._convert_parameters_to_openapi(endpoint.get("parameters", [])),
                "responses": {
                    str(endpoint.get("status_code", 200)): {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        
        # Add schemas from discovered models
        for model in self.discovered_apis["models"]:
            schema["components"]["schemas"][model["name"]] = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for field in model["fields"]:
                schema["components"]["schemas"][model["name"]]["properties"][field["name"]] = {
                    "type": self._convert_python_type_to_openapi(field["type"])
                }
                
                if field["required"]:
                    schema["components"]["schemas"][model["name"]]["required"].append(field["name"])
        
        return schema
    
    def _convert_parameters_to_openapi(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert function parameters to OpenAPI parameter format"""
        openapi_params = []
        
        for param in parameters:
            if param["name"] not in ["request", "response", "current_user", "db"]:  # Skip common injected params
                openapi_param = {
                    "name": param["name"],
                    "in": "query",  # Default to query parameter
                    "required": param["required"],
                    "schema": {
                        "type": self._convert_python_type_to_openapi(param["type"])
                    }
                }
                
                if param["default"] is not None:
                    openapi_param["schema"]["default"] = param["default"]
                
                openapi_params.append(openapi_param)
        
        return openapi_params
    
    def _convert_python_type_to_openapi(self, python_type: str) -> str:
        """Convert Python type annotation to OpenAPI type"""
        type_mapping = {
            "str": "string",
            "int": "integer", 
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "List": "array",
            "Dict": "object",
            "Optional": "string",
            "Union": "string",
            "Any": "object"
        }
        
        # Handle basic types
        for py_type, openapi_type in type_mapping.items():
            if py_type in python_type:
                return openapi_type
        
        return "string"  # Default fallback
    
    def generate_markdown_documentation(self) -> str:
        """Generate comprehensive Markdown documentation"""
        doc_content = f"""# Ainflue Platform API Documentation

Generated on: {datetime.now().isoformat()}

## Overview

The Ainflue Platform API provides comprehensive endpoints for AI-powered content protection and monetization. This documentation covers all available REST endpoints, WebSocket connections, and data models.

## Authentication

The API uses Bearer token authentication. Include your JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://api.ainflue.com`

## REST Endpoints

"""
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in self.discovered_apis["rest_endpoints"]:
            tags = endpoint.get("tags", ["default"])
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Document each group
        for tag, endpoints in endpoints_by_tag.items():
            doc_content += f"\n### {tag.title()}\n\n"
            
            for endpoint in endpoints:
                method = endpoint.get("method", "GET")
                path = endpoint.get("path", "/")
                summary = endpoint.get("summary", f"{method} {path}")
                
                doc_content += f"#### `{method} {path}`\n\n"
                doc_content += f"**Summary**: {summary}\n\n"
                
                if endpoint.get("description"):
                    doc_content += f"**Description**: {endpoint['description']}\n\n"
                
                # Parameters
                parameters = endpoint.get("parameters", [])
                if parameters:
                    doc_content += "**Parameters**:\n\n"
                    for param in parameters:
                        required = "✅" if param["required"] else "❌"
                        doc_content += f"- `{param['name']}` ({param['type']}) {required} - {param.get('description', 'No description')}\n"
                    doc_content += "\n"
                
                doc_content += "---\n\n"
        
        # WebSocket endpoints
        if self.discovered_apis["websocket_endpoints"]:
            doc_content += "## WebSocket Endpoints\n\n"
            
            for ws_endpoint in self.discovered_apis["websocket_endpoints"]:
                path = ws_endpoint.get("path", "/")
                doc_content += f"### `WS {path}`\n\n"
                doc_content += f"WebSocket connection for real-time communication.\n\n"
                doc_content += "---\n\n"
        
        # Data Models
        if self.discovered_apis["models"]:
            doc_content += "## Data Models\n\n"
            
            for model in self.discovered_apis["models"]:
                doc_content += f"### {model['name']}\n\n"
                
                if model.get("docstring"):
                    doc_content += f"{model['docstring']}\n\n"
                
                if model["fields"]:
                    doc_content += "**Fields**:\n\n"
                    for field in model["fields"]:
                        required = "✅" if field["required"] else "❌"
                        default = f" (default: {field['default']})" if field.get("default") is not None else ""
                        doc_content += f"- `{field['name']}`: {field['type']} {required}{default}\n"
                    doc_content += "\n"
                
                doc_content += "---\n\n"
        
        return doc_content
    
    async def comprehensive_documentation_generation(self) -> Dict[str, Any]:
        """Perform comprehensive API documentation generation"""
        print("📚 Starting comprehensive API documentation generation...")
        
        # Discover API files
        api_files = await self.discover_api_files()
        print(f"  📁 Found {len(api_files)} API files")
        
        # Process each file
        for api_file in api_files:
            print(f"  📄 Processing {api_file.name}...")
            self.stats["files_processed"] += 1
            
            # Extract REST endpoints
            rest_endpoints = self.extract_fastapi_routes(api_file)
            self.discovered_apis["rest_endpoints"].extend(rest_endpoints)
            
            # Extract WebSocket endpoints
            ws_endpoints = self.extract_websocket_routes(api_file)
            self.discovered_apis["websocket_endpoints"].extend(ws_endpoints)
            
            # Extract Pydantic models
            models = self.extract_pydantic_models(api_file)
            self.discovered_apis["models"].extend(models)
        
        # Generate documentation files
        results = {
            "files_processed": self.stats["files_processed"],
            "endpoints_discovered": len(self.discovered_apis["rest_endpoints"]),
            "websocket_endpoints": len(self.discovered_apis["websocket_endpoints"]),
            "models_discovered": len(self.discovered_apis["models"]),
            "generated_files": []
        }
        
        # Generate OpenAPI schema
        openapi_schema = self.generate_openapi_schema()
        openapi_file = self.docs_output / "openapi.json"
        with open(openapi_file, 'w') as f:
            json.dump(openapi_schema, f, indent=2)
        results["generated_files"].append(str(openapi_file))
        
        # Generate OpenAPI YAML
        openapi_yaml_file = self.docs_output / "openapi.yaml"
        with open(openapi_yaml_file, 'w') as f:
            yaml.dump(openapi_schema, f, default_flow_style=False)
        results["generated_files"].append(str(openapi_yaml_file))
        
        # Generate Markdown documentation
        markdown_content = self.generate_markdown_documentation()
        markdown_file = self.docs_output / "API_DOCUMENTATION.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_content)
        results["generated_files"].append(str(markdown_file))
        
        # Generate summary file
        summary = {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.stats,
            "discovered_apis": {
                "rest_endpoints_count": len(self.discovered_apis["rest_endpoints"]),
                "websocket_endpoints_count": len(self.discovered_apis["websocket_endpoints"]),
                "models_count": len(self.discovered_apis["models"])
            },
            "files": results["generated_files"]
        }
        
        summary_file = self.docs_output / "generation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        results["generated_files"].append(str(summary_file))
        
        return results

async def main():
    """Main API documentation generator execution"""
    generator = APIDocumentationGenerator()
    
    print("📚 API Documentation Generator - Ainflue Platform")
    print("=" * 50)
    
    # Generate comprehensive documentation
    results = await generator.comprehensive_documentation_generation()
    
    print(f"\n✅ Documentation generation completed!")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   REST endpoints: {results['endpoints_discovered']}")
    print(f"   WebSocket endpoints: {results['websocket_endpoints']}")
    print(f"   Data models: {results['models_discovered']}")
    
    print(f"\n📄 Generated files:")
    for file_path in results["generated_files"]:
        print(f"   📄 {file_path}")
    
    print(f"\n🌐 Documentation available at:")
    print(f"   📖 Markdown: {generator.docs_output}/API_DOCUMENTATION.md")
    print(f"   🔧 OpenAPI JSON: {generator.docs_output}/openapi.json")
    print(f"   📋 OpenAPI YAML: {generator.docs_output}/openapi.yaml")

if __name__ == "__main__":
    asyncio.run(main())