"""API Documentation Generator
Enterprise-grade automatic API documentation generation system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import ast
import inspect
import re

logger = logging.getLogger(__name__)

class APIMethod(Enum):
    """Supported HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"

class APIDocumentationFormat(Enum):
    """Supported documentation formats"""
    OPENAPI_3_0 = "openapi_3_0"
    SWAGGER_2_0 = "swagger_2_0"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    POSTMAN = "postman"

@dataclass
class APIParameter:
    """API parameter definition"""
    name: str
    type: str
    location: str  # query, path, header, body
    required: bool
    description: str
    example: Any = None
    schema: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None

@dataclass
class APIResponse:
    """API response definition"""
    status_code: int
    description: str
    content_type: str
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None

@dataclass
class APIEndpointDoc:
    """Complete API endpoint documentation"""
    path: str
    method: APIMethod
    summary: str
    description: str
    tags: List[str]
    parameters: List[APIParameter]
    responses: List[APIResponse]
    security: Optional[List[Dict[str, Any]]] = None
    deprecated: bool = False
    creator_specific: bool = False
    creator_types: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    rate_limits: Optional[Dict[str, Any]] = None

@dataclass
class APIDocumentationPackage:
    """Complete API documentation package"""
    title: str
    version: str
    description: str
    base_url: str
    endpoints: List[APIEndpointDoc]
    security_schemes: Dict[str, Any]
    tags: List[Dict[str, str]]
    generated_at: datetime
    formats: List[APIDocumentationFormat]
    creator_economy_endpoints: List[APIEndpointDoc]

class APIDocumentationGenerator:
    """
    Enterprise API documentation generator
    
    Automatically generates comprehensive API documentation
    with Creator Economy specific enhancements and multi-format output.
    """
    
    def __init__(self, project_root: str = "/home/runner/work/Ainflue/Ainflue"):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(f"{__name__}.APIDocumentationGenerator")
        
        # API discovery configuration
        self.api_directories = [
            "api", "endpoints", "routes", "handlers", 
            "services", "controllers", "views"
        ]
        
        # Creator Economy specific endpoints
        self.creator_economy_patterns = [
            r"/creators?/",
            r"/content/",
            r"/monetization/",
            r"/collaboration/",
            r"/analytics/",
            r"/protection/",
            r"/seo/",
            r"/distribution/"
        ]
        
        # Documentation templates
        self.documentation_templates = {}
        
        # Statistics tracking
        self.stats = {
            'endpoints_documented': 0,
            'creator_specific_endpoints': 0,
            'documentation_formats_generated': 0,
            'average_generation_time': 0.0
        }
        
        self.logger.info("API Documentation Generator initialized")
    
    async def generate_complete_api_documentation(
        self,
        formats: Optional[List[APIDocumentationFormat]] = None,
        include_creator_specific: bool = True,
        language: str = 'en'
    ) -> APIDocumentationPackage:
        """
        Generate complete API documentation in multiple formats
        
        Args:
            formats: List of output formats to generate
            include_creator_specific: Include Creator Economy specific endpoints
            language: Documentation language
        
        Returns:
            Complete API documentation package
        """
        start_time = datetime.now()
        
        try:
            if formats is None:
                formats = [
                    APIDocumentationFormat.OPENAPI_3_0,
                    APIDocumentationFormat.MARKDOWN,
                    APIDocumentationFormat.HTML
                ]
            
            self.logger.info("Starting complete API documentation generation")
            
            # Discover all API endpoints
            all_endpoints = await self._discover_api_endpoints()
            
            # Separate Creator Economy endpoints
            creator_endpoints = [
                endpoint for endpoint in all_endpoints
                if self._is_creator_economy_endpoint(endpoint)
            ]
            
            # Generate detailed documentation for each endpoint
            documented_endpoints = []
            for endpoint in all_endpoints:
                doc = await self._generate_endpoint_documentation(endpoint, language)
                if doc:
                    documented_endpoints.append(doc)
            
            # Generate security schemes
            security_schemes = await self._generate_security_schemes()
            
            # Generate tags
            tags = await self._generate_api_tags(documented_endpoints)
            
            # Create documentation package
            package = APIDocumentationPackage(
                title="Ainflue Creator Economy API",
                version="4.0.0",
                description="Enterprise API for Creator Economy platform with advanced content processing, monetization, and collaboration features",
                base_url="https://api.ainflue.com/v4",
                endpoints=documented_endpoints,
                security_schemes=security_schemes,
                tags=tags,
                generated_at=datetime.now(),
                formats=formats,
                creator_economy_endpoints=creator_endpoints if include_creator_specific else []
            )
            
            # Update statistics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.stats['endpoints_documented'] = len(documented_endpoints)
            self.stats['creator_specific_endpoints'] = len(creator_endpoints)
            self.stats['documentation_formats_generated'] = len(formats)
            self.stats['average_generation_time'] = generation_time
            
            self.logger.info(
                f"Generated API documentation: {len(documented_endpoints)} endpoints, "
                f"{len(creator_endpoints)} Creator Economy specific, "
                f"in {generation_time:.2f}s"
            )
            
            return package
            
        except Exception as e:
            self.logger.error(f"Failed to generate API documentation: {e}")
            raise
    
    async def generate_creator_api_documentation(
        self,
        creator_type: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Generate API documentation specific to a creator type
        
        Args:
            creator_type: Type of creator (musician, blogger, etc.)
            language: Documentation language
        
        Returns:
            Creator-specific API documentation
        """
        try:
            # Get all endpoints
            all_endpoints = await self._discover_api_endpoints()
            
            # Filter creator-specific endpoints
            creator_endpoints = []
            for endpoint in all_endpoints:
                if self._is_relevant_for_creator_type(endpoint, creator_type):
                    doc = await self._generate_endpoint_documentation(endpoint, language)
                    if doc:
                        doc.creator_specific = True
                        doc.creator_types = [creator_type]
                        creator_endpoints.append(doc)
            
            # Generate creator-specific documentation
            creator_doc = {
                'creator_type': creator_type,
                'language': language,
                'title': f'Ainflue API for {creator_type.replace("_", " ").title()} Creators',
                'description': f'Specialized API endpoints and features for {creator_type.replace("_", " ")} creators',
                'endpoints': [asdict(endpoint) for endpoint in creator_endpoints],
                'endpoint_count': len(creator_endpoints),
                'generated_at': datetime.now().isoformat()
            }
            
            # Add creator-specific guides
            creator_doc['quick_start_guide'] = await self._generate_creator_quick_start(creator_type, language)
            creator_doc['common_workflows'] = await self._generate_creator_workflows(creator_type, language)
            creator_doc['examples'] = await self._generate_creator_examples(creator_type, language)
            
            return creator_doc
            
        except Exception as e:
            self.logger.error(f"Failed to generate creator API documentation: {e}")
            raise
    
    async def export_documentation(
        self,
        package: APIDocumentationPackage,
        output_directory: Optional[Path] = None,
        formats: Optional[List[APIDocumentationFormat]] = None
    ) -> Dict[str, str]:
        """
        Export documentation in specified formats
        
        Args:
            package: API documentation package
            output_directory: Directory to save files
            formats: Formats to export
        
        Returns:
            Dictionary of generated file paths
        """
        try:
            if output_directory is None:
                output_directory = self.project_root / "docs" / "api"
            
            if formats is None:
                formats = package.formats
            
            output_directory.mkdir(parents=True, exist_ok=True)
            
            generated_files = {}
            
            for format_type in formats:
                if format_type == APIDocumentationFormat.OPENAPI_3_0:
                    file_path = await self._export_openapi_3_0(package, output_directory)
                    generated_files['openapi'] = str(file_path)
                
                elif format_type == APIDocumentationFormat.MARKDOWN:
                    file_path = await self._export_markdown(package, output_directory)
                    generated_files['markdown'] = str(file_path)
                
                elif format_type == APIDocumentationFormat.HTML:
                    file_path = await self._export_html(package, output_directory)
                    generated_files['html'] = str(file_path)
                
                elif format_type == APIDocumentationFormat.JSON:
                    file_path = await self._export_json(package, output_directory)
                    generated_files['json'] = str(file_path)
                
                elif format_type == APIDocumentationFormat.POSTMAN:
                    file_path = await self._export_postman(package, output_directory)
                    generated_files['postman'] = str(file_path)
            
            self.logger.info(f"Exported API documentation in {len(generated_files)} formats")
            return generated_files
            
        except Exception as e:
            self.logger.error(f"Failed to export documentation: {e}")
            raise
    
    async def _discover_api_endpoints(self) -> List[Dict[str, Any]]:
        """Discover all API endpoints in the project"""
        endpoints = []
        
        # Search in API directories
        for api_dir in self.api_directories:
            api_path = self.project_root / api_dir
            if api_path.exists():
                endpoints.extend(await self._scan_directory_for_endpoints(api_path))
        
        # Search in root files
        root_files = ["main.py", "app.py", "server.py", "index.py"]
        for file_name in root_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                endpoints.extend(await self._scan_file_for_endpoints(file_path))
        
        return endpoints
    
    async def _scan_directory_for_endpoints(self, directory: Path) -> List[Dict[str, Any]]:
        """Scan directory for API endpoints"""
        endpoints = []
        
        for file_path in directory.rglob("*.py"):
            if file_path.name.startswith("test_"):
                continue
            
            try:
                file_endpoints = await self._scan_file_for_endpoints(file_path)
                endpoints.extend(file_endpoints)
            except Exception as e:
                self.logger.warning(f"Error scanning file {file_path}: {e}")
        
        return endpoints
    
    async def _scan_file_for_endpoints(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan individual file for API endpoints"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    endpoint = await self._extract_endpoint_info(node, file_path, content)
                    if endpoint:
                        endpoints.append(endpoint)
        
        except Exception as e:
            self.logger.warning(f"Error parsing file {file_path}: {e}")
        
        return endpoints
    
    async def _extract_endpoint_info(
        self, 
        func_node: ast.FunctionDef, 
        file_path: Path, 
        file_content: str
    ) -> Optional[Dict[str, Any]]:
        """Extract endpoint information from function node"""
        
        # Look for API decorators
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                method_name = decorator.func.attr.upper()
                if method_name in [method.value for method in APIMethod]:
                    # Extract path from decorator arguments
                    path = "/"
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value
                    
                    return {
                        'path': path,
                        'method': method_name,
                        'function_name': func_node.name,
                        'file_path': str(file_path.relative_to(self.project_root)),
                        'line_number': func_node.lineno,
                        'docstring': ast.get_docstring(func_node),
                        'parameters': self._extract_parameters(func_node),
                        'source_code': self._extract_function_source(file_content, func_node)
                    }
        
        return None
    
    def _extract_parameters(self, func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters"""
        parameters = []
        
        for arg in func_node.args.args:
            if arg.arg not in ['self', 'cls']:
                param = {
                    'name': arg.arg,
                    'type': 'any',  # Default type
                    'required': True
                }
                
                # Try to extract type annotation
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        param['type'] = arg.annotation.id
                    elif isinstance(arg.annotation, ast.Constant):
                        param['type'] = str(arg.annotation.value)
                
                parameters.append(param)
        
        return parameters
    
    def _extract_function_source(self, file_content: str, func_node: ast.FunctionDef) -> str:
        """Extract function source code"""
        lines = file_content.split('\n')
        start_line = func_node.lineno - 1
        
        # Find end of function (simplified)
        end_line = start_line + 10  # Default to 10 lines
        for i in range(start_line + 1, min(len(lines), start_line + 50)):
            if lines[i] and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                end_line = i
                break
        
        return '\n'.join(lines[start_line:end_line])
    
    async def _generate_endpoint_documentation(
        self, 
        endpoint: Dict[str, Any], 
        language: str
    ) -> Optional[APIEndpointDoc]:
        """Generate detailed documentation for an endpoint"""
        
        try:
            # Parse docstring for additional information
            summary, description, params, responses = await self._parse_docstring(
                endpoint.get('docstring', '')
            )
            
            # Generate parameters
            parameters = []
            for param in endpoint.get('parameters', []):
                api_param = APIParameter(
                    name=param['name'],
                    type=param.get('type', 'string'),
                    location='query',  # Default location
                    required=param.get('required', False),
                    description=f"Parameter {param['name']}",
                    example=self._generate_parameter_example(param['type'])
                )
                parameters.append(api_param)
            
            # Generate responses
            api_responses = []
            if responses:
                for status_code, resp_info in responses.items():
                    api_response = APIResponse(
                        status_code=int(status_code),
                        description=resp_info.get('description', 'Success'),
                        content_type='application/json',
                        schema=resp_info.get('schema'),
                        example=resp_info.get('example')
                    )
                    api_responses.append(api_response)
            else:
                # Default success response
                api_responses.append(
                    APIResponse(
                        status_code=200,
                        description='Successful operation',
                        content_type='application/json'
                    )
                )
            
            # Generate tags
            tags = await self._generate_endpoint_tags(endpoint)
            
            return APIEndpointDoc(
                path=endpoint['path'],
                method=APIMethod(endpoint['method']),
                summary=summary or f"{endpoint['method']} {endpoint['path']}",
                description=description or f"API endpoint for {endpoint['function_name']}",
                tags=tags,
                parameters=parameters,
                responses=api_responses,
                creator_specific=self._is_creator_economy_endpoint(endpoint),
                examples=await self._generate_endpoint_examples(endpoint)
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to generate documentation for endpoint {endpoint.get('path', 'unknown')}: {e}")
            return None
    
    async def _parse_docstring(self, docstring: str) -> Tuple[Optional[str], Optional[str], Dict[str, Any], Dict[str, Any]]:
        """Parse function docstring for API documentation"""
        if not docstring:
            return None, None, {}, {}
        
        lines = docstring.strip().split('\n')
        summary = lines[0] if lines else None
        
        description = ""
        parameters = {}
        responses = {}
        
        current_section = None
        
        for line in lines[1:]:
            line = line.strip()
            
            if line.lower().startswith('args:') or line.lower().startswith('parameters:'):
                current_section = 'parameters'
                continue
            elif line.lower().startswith('returns:') or line.lower().startswith('response:'):
                current_section = 'responses'
                continue
            elif line.lower().startswith('raises:') or line.lower().startswith('errors:'):
                current_section = 'errors'
                continue
            
            if current_section == 'parameters':
                # Parse parameter documentation
                param_match = re.match(r'\s*(\w+):\s*(.+)', line)
                if param_match:
                    param_name, param_desc = param_match.groups()
                    parameters[param_name] = {'description': param_desc}
            
            elif current_section == 'responses':
                # Parse response documentation
                if '200' not in responses:
                    responses['200'] = {'description': line}
            
            elif current_section is None and line:
                description += line + " "
        
        return summary, description.strip(), parameters, responses
    
    def _generate_parameter_example(self, param_type: str) -> Any:
        """Generate example value for parameter type"""
        examples = {
            'string': 'example_string',
            'int': 123,
            'integer': 123,
            'float': 12.34,
            'bool': True,
            'boolean': True,
            'list': ['item1', 'item2'],
            'dict': {'key': 'value'},
            'object': {'key': 'value'}
        }
        
        return examples.get(param_type.lower(), 'example_value')
    
    async def _generate_endpoint_tags(self, endpoint: Dict[str, Any]) -> List[str]:
        """Generate tags for an endpoint"""
        tags = []
        
        # Add tags based on path
        path = endpoint.get('path', '')
        if '/creators' in path:
            tags.append('Creators')
        if '/content' in path:
            tags.append('Content')
        if '/monetization' in path:
            tags.append('Monetization')
        if '/collaboration' in path:
            tags.append('Collaboration')
        if '/analytics' in path:
            tags.append('Analytics')
        
        # Add default tag if none found
        if not tags:
            tags.append('General')
        
        return tags
    
    async def _generate_endpoint_examples(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate examples for an endpoint"""
        examples = []
        
        method = endpoint.get('method', 'GET')
        path = endpoint.get('path', '/')
        
        if method == 'GET':
            examples.append({
                'title': 'Basic GET request',
                'description': f'Retrieve data from {path}',
                'request': {
                    'method': method,
                    'url': f'https://api.ainflue.com/v4{path}',
                    'headers': {
                        'Authorization': 'Bearer YOUR_API_TOKEN',
                        'Content-Type': 'application/json'
                    }
                },
                'response': {
                    'status': 200,
                    'body': {
                        'success': True,
                        'data': {}
                    }
                }
            })
        
        elif method == 'POST':
            examples.append({
                'title': 'Create resource',
                'description': f'Create new resource at {path}',
                'request': {
                    'method': method,
                    'url': f'https://api.ainflue.com/v4{path}',
                    'headers': {
                        'Authorization': 'Bearer YOUR_API_TOKEN',
                        'Content-Type': 'application/json'
                    },
                    'body': {
                        'name': 'Example Resource',
                        'description': 'Resource description'
                    }
                },
                'response': {
                    'status': 201,
                    'body': {
                        'success': True,
                        'data': {
                            'id': '12345',
                            'name': 'Example Resource',
                            'created_at': '2025-01-17T10:00:00Z'
                        }
                    }
                }
            })
        
        return examples
    
    def _is_creator_economy_endpoint(self, endpoint: Dict[str, Any]) -> bool:
        """Check if endpoint is Creator Economy specific"""
        path = endpoint.get('path', '')
        return any(re.search(pattern, path) for pattern in self.creator_economy_patterns)
    
    def _is_relevant_for_creator_type(self, endpoint: Dict[str, Any], creator_type: str) -> bool:
        """Check if endpoint is relevant for specific creator type"""
        path = endpoint.get('path', '').lower()
        function_name = endpoint.get('function_name', '').lower()
        
        # Creator type specific patterns
        creator_patterns = {
            'musician': [r'music', r'audio', r'song', r'track', r'album', r'streaming'],
            'blogger': [r'blog', r'post', r'article', r'content', r'seo'],
            'photographer': [r'photo', r'image', r'gallery', r'portfolio'],
            'influencer': [r'influence', r'brand', r'partnership', r'social'],
            'comedian': [r'comedy', r'joke', r'entertainment', r'humor']
        }
        
        patterns = creator_patterns.get(creator_type, [])
        return (self._is_creator_economy_endpoint(endpoint) or 
                any(re.search(pattern, path) or re.search(pattern, function_name) 
                    for pattern in patterns))
    
    async def _generate_security_schemes(self) -> Dict[str, Any]:
        """Generate security schemes for API documentation"""
        return {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'JWT Bearer token authentication'
            },
            'ApiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key',
                'description': 'API key authentication'
            },
            'OAuth2': {
                'type': 'oauth2',
                'flows': {
                    'authorizationCode': {
                        'authorizationUrl': 'https://auth.ainflue.com/oauth/authorize',
                        'tokenUrl': 'https://auth.ainflue.com/oauth/token',
                        'scopes': {
                            'read': 'Read access to resources',
                            'write': 'Write access to resources',
                            'admin': 'Administrative access'
                        }
                    }
                }
            }
        }
    
    async def _generate_api_tags(self, endpoints: List[APIEndpointDoc]) -> List[Dict[str, str]]:
        """Generate tags for API documentation"""
        tag_descriptions = {
            'Creators': 'Creator management and profiles',
            'Content': 'Content creation and management',
            'Monetization': 'Monetization and revenue features',
            'Collaboration': 'Creator collaboration tools',
            'Analytics': 'Analytics and reporting',
            'Protection': 'Content protection and IP rights',
            'SEO': 'Search engine optimization',
            'Distribution': 'Multi-platform distribution',
            'General': 'General API endpoints'
        }
        
        # Extract unique tags from endpoints
        unique_tags = set()
        for endpoint in endpoints:
            unique_tags.update(endpoint.tags)
        
        return [
            {'name': tag, 'description': tag_descriptions.get(tag, f'{tag} related endpoints')}
            for tag in sorted(unique_tags)
        ]
    
    # Export methods for different formats
    async def _export_openapi_3_0(self, package: APIDocumentationPackage, output_dir: Path) -> Path:
        """Export OpenAPI 3.0 specification"""
        openapi_spec = {
            'openapi': '3.0.3',
            'info': {
                'title': package.title,
                'version': package.version,
                'description': package.description,
                'contact': {
                    'name': 'Fahed Mlaiel',
                    'email': 'mlaiel@live.de'
                },
                'license': {
                    'name': 'Proprietary',
                    'url': 'https://ainflue.com/license'
                }
            },
            'servers': [
                {
                    'url': package.base_url,
                    'description': 'Production server'
                }
            ],
            'paths': {},
            'components': {
                'securitySchemes': package.security_schemes
            },
            'tags': package.tags
        }
        
        # Add paths
        for endpoint in package.endpoints:
            if endpoint.path not in openapi_spec['paths']:
                openapi_spec['paths'][endpoint.path] = {}
            
            openapi_spec['paths'][endpoint.path][endpoint.method.value.lower()] = {
                'summary': endpoint.summary,
                'description': endpoint.description,
                'tags': endpoint.tags,
                'parameters': [
                    {
                        'name': param.name,
                        'in': param.location,
                        'required': param.required,
                        'description': param.description,
                        'schema': {'type': param.type},
                        'example': param.example
                    }
                    for param in endpoint.parameters
                ],
                'responses': {
                    str(response.status_code): {
                        'description': response.description,
                        'content': {
                            response.content_type: {
                                'schema': response.schema or {'type': 'object'},
                                'example': response.example
                            }
                        } if response.content_type else {}
                    }
                    for response in endpoint.responses
                }
            }
        
        # Write to file
        output_file = output_dir / 'openapi.yaml'
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        return output_file
    
    async def _export_markdown(self, package: APIDocumentationPackage, output_dir: Path) -> Path:
        """Export Markdown documentation"""
        markdown_content = f"""# {package.title}

{package.description}

**Version:** {package.version}  
**Base URL:** {package.base_url}  
**Generated:** {package.generated_at.strftime('%Y-%m-%d %H:%M:%S')}

## Authentication

This API uses Bearer token authentication. Include your API token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

"""
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in package.endpoints:
            for tag in endpoint.tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Generate documentation for each tag
        for tag, endpoints in endpoints_by_tag.items():
            markdown_content += f"### {tag}\n\n"
            
            for endpoint in endpoints:
                markdown_content += f"#### {endpoint.method.value} {endpoint.path}\n\n"
                markdown_content += f"{endpoint.description}\n\n"
                
                if endpoint.parameters:
                    markdown_content += "**Parameters:**\n\n"
                    for param in endpoint.parameters:
                        markdown_content += f"- `{param.name}` ({param.type}) - {param.description}\n"
                    markdown_content += "\n"
                
                markdown_content += "**Responses:**\n\n"
                for response in endpoint.responses:
                    markdown_content += f"- `{response.status_code}` - {response.description}\n"
                markdown_content += "\n"
        
        # Write to file
        output_file = output_dir / 'api_documentation.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_file
    
    async def _export_html(self, package: APIDocumentationPackage, output_dir: Path) -> Path:
        """Export HTML documentation"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{package.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin: -20px -20px 20px -20px; }}
        .endpoint {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .method {{ display: inline-block; padding: 5px 10px; color: white; border-radius: 3px; font-weight: bold; }}
        .get {{ background: #28a745; }}
        .post {{ background: #007bff; }}
        .put {{ background: #ffc107; color: black; }}
        .delete {{ background: #dc3545; }}
        .patch {{ background: #6c757d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{package.title}</h1>
        <p>{package.description}</p>
        <p><strong>Version:</strong> {package.version} | <strong>Base URL:</strong> {package.base_url}</p>
    </div>
"""
        
        for endpoint in package.endpoints:
            method_class = endpoint.method.value.lower()
            html_content += f"""
    <div class="endpoint">
        <h3><span class="method {method_class}">{endpoint.method.value}</span> {endpoint.path}</h3>
        <p>{endpoint.description}</p>
        
        <h4>Parameters:</h4>
        <ul>
"""
            for param in endpoint.parameters:
                html_content += f"<li><strong>{param.name}</strong> ({param.type}) - {param.description}</li>"
            
            html_content += """
        </ul>
        
        <h4>Responses:</h4>
        <ul>
"""
            for response in endpoint.responses:
                html_content += f"<li><strong>{response.status_code}</strong> - {response.description}</li>"
            
            html_content += """
        </ul>
    </div>
"""
        
        html_content += """
</body>
</html>"""
        
        # Write to file
        output_file = output_dir / 'api_documentation.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    async def _export_json(self, package: APIDocumentationPackage, output_dir: Path) -> Path:
        """Export JSON documentation"""
        json_data = {
            'title': package.title,
            'version': package.version,
            'description': package.description,
            'base_url': package.base_url,
            'generated_at': package.generated_at.isoformat(),
            'endpoints': [asdict(endpoint) for endpoint in package.endpoints],
            'security_schemes': package.security_schemes,
            'tags': package.tags
        }
        
        # Convert enums to strings for JSON serialization
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value
            return obj
        
        json_data = convert_enums(json_data)
        
        # Write to file
        output_file = output_dir / 'api_documentation.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    async def _export_postman(self, package: APIDocumentationPackage, output_dir: Path) -> Path:
        """Export Postman collection"""
        postman_collection = {
            'info': {
                'name': package.title,
                'description': package.description,
                'version': package.version,
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': []
        }
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in package.endpoints:
            for tag in endpoint.tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Create Postman folders and requests
        for tag, endpoints in endpoints_by_tag.items():
            folder = {
                'name': tag,
                'item': []
            }
            
            for endpoint in endpoints:
                request = {
                    'name': f"{endpoint.method.value} {endpoint.path}",
                    'request': {
                        'method': endpoint.method.value,
                        'header': [
                            {
                                'key': 'Authorization',
                                'value': 'Bearer {{api_token}}',
                                'type': 'text'
                            },
                            {
                                'key': 'Content-Type',
                                'value': 'application/json',
                                'type': 'text'
                            }
                        ],
                        'url': {
                            'raw': f"{package.base_url}{endpoint.path}",
                            'host': [package.base_url.replace('https://', '').replace('http://', '')],
                            'path': endpoint.path.strip('/').split('/')
                        },
                        'description': endpoint.description
                    }
                }
                
                folder['item'].append(request)
            
            postman_collection['item'].append(folder)
        
        # Write to file
        output_file = output_dir / 'postman_collection.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(postman_collection, f, indent=2)
        
        return output_file
    
    async def _generate_creator_quick_start(self, creator_type: str, language: str) -> Dict[str, Any]:
        """Generate quick start guide for creator type"""
        return {
            'title': f'Quick Start Guide for {creator_type.replace("_", " ").title()} Creators',
            'steps': [
                {
                    'step': 1,
                    'title': 'Authentication',
                    'description': 'Get your API token from the creator dashboard',
                    'example': 'Authorization: Bearer YOUR_API_TOKEN'
                },
                {
                    'step': 2,
                    'title': 'Create Creator Profile',
                    'description': 'Set up your creator profile with basic information',
                    'endpoint': 'POST /creators/profile'
                },
                {
                    'step': 3,
                    'title': 'Upload Content',
                    'description': 'Upload your first piece of content',
                    'endpoint': 'POST /content/upload'
                },
                {
                    'step': 4,
                    'title': 'Configure Monetization',
                    'description': 'Set up your monetization preferences',
                    'endpoint': 'POST /monetization/settings'
                }
            ]
        }
    
    async def _generate_creator_workflows(self, creator_type: str, language: str) -> List[Dict[str, Any]]:
        """Generate common workflows for creator type"""
        return [
            {
                'name': 'Content Upload and Publishing',
                'description': 'Complete workflow for uploading and publishing content',
                'steps': [
                    'POST /content/upload - Upload content file',
                    'PUT /content/{id}/metadata - Add metadata and tags',
                    'POST /content/{id}/process - Process with AI enhancement',
                    'PUT /content/{id}/publish - Publish to platforms'
                ]
            },
            {
                'name': 'Collaboration Setup',
                'description': 'Set up collaboration with other creators',
                'steps': [
                    'GET /creators/search - Find potential collaborators',
                    'POST /collaboration/invite - Send collaboration invite',
                    'PUT /collaboration/{id}/accept - Accept collaboration',
                    'POST /collaboration/{id}/content - Share collaborative content'
                ]
            }
        ]
    
    async def _generate_creator_examples(self, creator_type: str, language: str) -> List[Dict[str, Any]]:
        """Generate API examples for creator type"""
        return [
            {
                'title': 'Upload Content',
                'description': f'Example of uploading {creator_type} content',
                'request': {
                    'method': 'POST',
                    'endpoint': '/content/upload',
                    'headers': {
                        'Authorization': 'Bearer YOUR_API_TOKEN',
                        'Content-Type': 'multipart/form-data'
                    },
                    'body': {
                        'file': 'content_file',
                        'title': f'My {creator_type} Content',
                        'description': 'Content description',
                        'tags': [creator_type, 'original'],
                        'creator_type': creator_type
                    }
                },
                'response': {
                    'status': 201,
                    'body': {
                        'success': True,
                        'data': {
                            'content_id': '12345',
                            'status': 'uploaded',
                            'processing_status': 'queued'
                        }
                    }
                }
            }
        ]

__all__ = [
    'APIDocumentationGenerator',
    'APIMethod',
    'APIDocumentationFormat',
    'APIParameter',
    'APIResponse', 
    'APIEndpointDoc',
    'APIDocumentationPackage'
]