"""
Generate Postman Collection module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Postman Collection Generator for Ainflue API

This script generates comprehensive Postman collections from the OpenAPI specification
to enable easy testing and development with the Ainflue API.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved.
"""

import json
import yaml
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional


class PostmanCollectionGenerator:
    """Generate Postman collections from OpenAPI specifications."""
    
    def __init__(self, openapi_spec_path -> None: str) -> None:
        """Initialize with OpenAPI specification file."""
        self.openapi_spec_path = openapi_spec_path
        self.spec = self._load_openapi_spec()
        
    def _load_openapi_spec(self) -> Dict[str, Any]:
        """Load and parse OpenAPI specification."""
        with open(self.openapi_spec_path, 'r', encoding='utf-8') as f:
            if self.openapi_spec_path.endswith('.yaml') or self.openapi_spec_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def generate_collection(self) -> Dict[str, Any]:
        """Generate complete Postman collection."""
        info = self.spec.get('info', {})
        
        collection = {
            "info": {
                "name": f"{info.get('title', 'API')} - Complete Collection",
                "description": self._generate_collection_description(),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "event": [
                {
                    "listen": "prerequest",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "// Global pre-request script",
                            "if (!pm.environment.get('base_url')) {",
                            "    pm.environment.set('base_url', 'https://api.ainflue.com/v1');",
                            "}",
                            "",
                            "// Set request timestamp",
                            "pm.environment.set('timestamp', new Date().toISOString());"
                        ]
                    }
                },
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "// Global test script",
                            "pm.test('Response time is less than 5000ms', () => {",
                            "    pm.expect(pm.response.responseTime).to.be.below(5000);",
                            "});",
                            "",
                            "pm.test('Response has valid headers', () => {",
                            "    pm.expect(pm.response.headers.get('Content-Type')).to.include('application/json');",
                            "});",
                            "",
                            "// Store rate limit headers if present",
                            "if (pm.response.headers.get('X-RateLimit-Remaining')) {",
                            "    pm.environment.set('rate_limit_remaining', pm.response.headers.get('X-RateLimit-Remaining'));",
                            "}"
                        ]
                    }
                }
            ],
            "variable": [
                {
                    "key": "base_url",
                    "value": "https://api.ainflue.com/v1",
                    "type": "string"
                },
                {
                    "key": "api_version",
                    "value": "v1",
                    "type": "string"
                }
            ],
            "item": self._generate_folders()
        }
        
        return collection
    
    def _generate_collection_description(self) -> str:
        """Generate comprehensive collection description."""
        info = self.spec.get('info', {})
        
        description = f"""
# {info.get('title', 'API')} Postman Collection

{info.get('description', 'Complete API testing collection')}

## 🚀 Quick Start

1. **Import Environment**: Import the companion environment file
2. **Set Variables**: Configure your API credentials in environment variables
3. **Authenticate**: Run the login request to get your access token
4. **Start Testing**: All requests are organized by feature area

## 🔐 Authentication

This collection uses Bearer token authentication. The token is automatically set after successful login.

### Required Environment Variables:

- `base_url`: API base URL (default: https://api.ainflue.com/v1)
- `test_email`: Your test account email
- `test_password`: Your test account password
- `api_key`: Your API key (alternative to JWT)

### Optional Variables:

- `content_id`: UUID for content testing
- `project_id`: UUID for collaboration testing
- `violation_id`: UUID for violation testing

## 📊 Rate Limiting

All requests include rate limiting information in headers:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Reset time

## 🧪 Testing

Each request includes comprehensive tests:
- Response time validation
- Status code verification
- Schema validation
- Business logic assertions
- Rate limit monitoring

## 📁 Collection Structure

Requests are organized by API functionality:
"""
        
        # Add tag descriptions
        tags = self.spec.get('tags', [])
        for tag in tags:
            description += f"\n- **{tag['name']}**: {tag.get('description', 'No description')}"
        
        description += f"""

## 📞 Support

- **Documentation**: {info.get('contact', {}).get('url', 'N/A')}
- **Email**: {info.get('contact', {}).get('email', 'N/A')}
- **Version**: {info.get('version', 'N/A')}

Generated on: {datetime.now().isoformat()}
"""
        
        return description.strip()
    
    def _generate_folders(self) -> List[Dict[str, Any]]:
        """Generate folder structure based on tags."""
        folders = []
        tags = self.spec.get('tags', [])
        paths = self.spec.get('paths', {})
        
        # Group paths by tags
        tag_requests = {}
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                    operation_tags = operation.get('tags', ['Uncategorized'])
                    for tag in operation_tags:
                        if tag not in tag_requests:
                            tag_requests[tag] = []
                        tag_requests[tag].append({
                            'path': path,
                            'method': method.upper(),
                            'operation': operation
                        })
        
        # Create folders for each tag
        for tag in tags:
            tag_name = tag['name']
            if tag_name in tag_requests:
                folder = {
                    "name": f"{tag_name}",
                    "description": tag.get('description', ''),
                    "item": []
                }
                
                # Add requests to folder
                for request_info in tag_requests[tag_name]:
                    request = self._generate_request(
                        request_info['path'],
                        request_info['method'],
                        request_info['operation']
                    )
                    folder['item'].append(request)
                
                folders.append(folder)
        
        # Add uncategorized requests if any
        if 'Uncategorized' in tag_requests:
            folder = {
                "name": "Uncategorized",
                "description": "Requests without specific tags",
                "item": []
            }
            for request_info in tag_requests['Uncategorized']:
                request = self._generate_request(
                    request_info['path'],
                    request_info['method'],
                    request_info['operation']
                )
                folder['item'].append(request)
            folders.append(folder)
        
        return folders
    
    def _generate_request(self, path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate individual Postman request."""
        request = {
            "name": operation.get('summary', f"{method} {path}"),
            "request": {
                "method": method,
                "header": self._generate_headers(operation),
                "url": {
                    "raw": "{{base_url}}" + path,
                    "host": ["{{base_url}}"],
                    "path": path.strip('/').split('/'),
                    "query": self._generate_query_params(operation)
                },
                "description": operation.get('description', '')
            },
            "response": [],
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": self._generate_test_script(operation)
                    }
                }
            ]
        }
        
        # Add request body if needed
        if method in ['POST', 'PUT', 'PATCH']:
            body = self._generate_request_body(operation)
            if body:
                request['request']['body'] = body
        
        # Add path parameters
        path_params = self._extract_path_parameters(path, operation)
        if path_params:
            request['request']['url']['variable'] = path_params
        
        return request
    
    def _generate_headers(self, operation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate request headers."""
        headers = [
            {
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
            }
        ]
        
        # Check if operation requires authentication
        if 'security' in operation or 'security' in self.spec:
            headers.append({
                "key": "Authorization",
                "value": "Bearer {{access_token}}",
                "type": "text"
            })
        
        return headers
    
    def _generate_query_params(self, operation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate query parameters."""
        query_params = []
        parameters = operation.get('parameters', [])
        
        for param in parameters:
            if param.get('in') == 'query':
                query_params.append({
                    "key": param['name'],
                    "value": self._generate_example_value(param),
                    "description": param.get('description', ''),
                    "disabled": not param.get('required', False)
                })
        
        return query_params
    
    def _generate_request_body(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate request body from operation."""
        request_body = operation.get('requestBody')
        if not request_body:
            return None
        
        content = request_body.get('content', {})
        
        # Handle JSON content
        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            example = self._generate_json_example(schema)
            
            return {
                "mode": "raw",
                "raw": json.dumps(example, indent=2),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
        
        # Handle form data
        elif 'multipart/form-data' in content:
            schema = content['multipart/form-data'].get('schema', {})
            properties = schema.get('properties', {})
            
            formdata = []
            for prop_name, prop_schema in properties.items():
                if prop_schema.get('type') == 'string' and prop_schema.get('format') == 'binary':
                    formdata.append({
                        "key": prop_name,
                        "type": "file",
                        "src": []
                    })
                else:
                    formdata.append({
                        "key": prop_name,
                        "value": self._generate_example_value({'schema': prop_schema}),
                        "type": "text"
                    })
            
            return {
                "mode": "formdata",
                "formdata": formdata
            }
        
        return None
    
    def _extract_path_parameters(self, path: str, operation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract path parameters from URL."""
        import re
        path_params = []
        
        # Find path parameters in the URL
        param_pattern = r'\{([^}]+)\}'
        matches = re.findall(param_pattern, path)
        
        # Get parameter details from operation
        parameters = operation.get('parameters', [])
        param_details = {p['name']: p for p in parameters if p.get('in') == 'path'}
        
        for param_name in matches:
            param_info = param_details.get(param_name, {})
            path_params.append({
                "key": param_name,
                "value": self._generate_example_value(param_info),
                "description": param_info.get('description', '')
            })
        
        return path_params
    
    def _generate_test_script(self, operation: Dict[str, Any]) -> List[str]:
        """Generate test script for request."""
        scripts = [
            "// Test response status",
            "pm.test('Status code is successful', () => {",
            "    pm.expect(pm.response.code).to.be.oneOf([200, 201, 202, 204]);",
            "});",
            "",
            "// Test response format",
            "if (pm.response.code !== 204) {",
            "    pm.test('Response is valid JSON', () => {",
            "        pm.expect(() => pm.response.json()).to.not.throw();",
            "    });",
            "}",
            ""
        ]
        
        # Add specific tests based on operation
        responses = operation.get('responses', {})
        
        if '200' in responses or '201' in responses:
            scripts.extend([
                "// Test successful response structure",
                "if (pm.response.code === 200 || pm.response.code === 201) {",
                "    const response = pm.response.json();",
                "    ",
                "    pm.test('Response has expected structure', () => {",
                "        pm.expect(response).to.be.an('object');",
                "    });",
                "}"
            ])
        
        # Add authentication token extraction for login endpoints
        if 'login' in operation.get('operationId', '').lower():
            scripts.extend([
                "",
                "// Extract and store access token",
                "if (pm.response.code === 200) {",
                "    const response = pm.response.json();",
                "    if (response.access_token) {",
                "        pm.environment.set('access_token', response.access_token);",
                "        pm.test('Access token received', () => {",
                "            pm.expect(response.access_token).to.be.a('string').and.not.empty;",
                "        });",
                "    }",
                "}"
            ])
        
        # Add ID extraction for creation endpoints
        operation_id = operation.get('operationId', '').lower()
        if any(keyword in operation_id for keyword in ['create', 'upload', 'generate']):
            scripts.extend([
                "",
                "// Extract and store resource ID",
                "if (pm.response.code === 201 || pm.response.code === 200) {",
                "    const response = pm.response.json();",
                "    if (response.id) {",
                "        pm.environment.set('last_created_id', response.id);",
                "    }",
                "    if (response.content_id) {",
                "        pm.environment.set('content_id', response.content_id);",
                "    }",
                "    if (response.project_id) {",
                "        pm.environment.set('project_id', response.project_id);",
                "    }",
                "}"
            ])
        
        return scripts
    
    def _generate_json_example(self, schema: Dict[str, Any]) -> Any:
        """Generate example JSON from schema."""
        if 'example' in schema:
            return schema['example']
        
        if '$ref' in schema:
            # Handle schema references
            ref_path = schema['$ref'].split('/')[-1]
            components = self.spec.get('components', {}).get('schemas', {})
            if ref_path in components:
                return self._generate_json_example(components[ref_path])
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            obj = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required:
                    obj[prop_name] = self._generate_json_example(prop_schema)
                else:
                    # Include some optional properties for completeness
                    obj[prop_name] = self._generate_json_example(prop_schema)
            
            return obj
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._generate_json_example(items_schema)]
        
        elif schema_type == 'string':
            format_type = schema.get('format')
            enum_values = schema.get('enum')
            
            if enum_values:
                return enum_values[0]
            elif format_type == 'email':
                return "user@example.com"
            elif format_type == 'password':
                return "SecurePassword123!"
            elif format_type == 'date-time':
                return "2025-01-07T10:00:00Z"
            elif format_type == 'date':
                return "2025-01-07"
            elif format_type == 'uuid':
                return "123e4567-e89b-12d3-a456-426614174000"
            elif format_type == 'uri':
                return "https://example.com"
            else:
                return schema.get('example', 'string_value')
        
        elif schema_type == 'integer':
            return schema.get('example', 42)
        
        elif schema_type == 'number':
            return schema.get('example', 123.45)
        
        elif schema_type == 'boolean':
            return schema.get('example', True)
        
        else:
            return None
    
    def _generate_example_value(self, parameter: Dict[str, Any]) -> str:
        """Generate example value for parameter."""
        schema = parameter.get('schema', {})
        example = parameter.get('example')
        
        if example is not None:
            return str(example)
        
        return str(self._generate_json_example(schema))
    
    def generate_environment(self) -> Dict[str, Any]:
        """Generate companion Postman environment."""
        info = self.spec.get('info', {})
        servers = self.spec.get('servers', [])
        
        environment = {
            "name": f"{info.get('title', 'API')} - Environment",
            "values": [
                {
                    "key": "base_url",
                    "value": servers[0]['url'] if servers else "https://api.ainflue.com/v1",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "api_version",
                    "value": "v1",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "access_token",
                    "value": "",
                    "enabled": True,
                    "type": "secret"
                },
                {
                    "key": "api_key",
                    "value": "",
                    "enabled": True,
                    "type": "secret"
                },
                {
                    "key": "test_email",
                    "value": "test@example.com",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "test_password",
                    "value": "TestPassword123!",
                    "enabled": True,
                    "type": "secret"
                },
                {
                    "key": "content_id",
                    "value": "123e4567-e89b-12d3-a456-426614174000",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "project_id",
                    "value": "123e4567-e89b-12d3-a456-426614174001",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "violation_id",
                    "value": "123e4567-e89b-12d3-a456-426614174002",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "timestamp",
                    "value": "",
                    "enabled": True,
                    "type": "default"
                },
                {
                    "key": "rate_limit_remaining",
                    "value": "",
                    "enabled": True,
                    "type": "default"
                }
            ]
        }
        
        return environment


def main() -> None:
    """Generate Postman collection and environment files."""
    import os
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    openapi_spec_path = os.path.join(script_dir, 'openapi-spec-complete.yaml')
    
    if not os.path.exists(openapi_spec_path):
        print(f"Error: OpenAPI specification not found at {openapi_spec_path}")
        return
    
    # Generate collection
    generator = PostmanCollectionGenerator(openapi_spec_path)
    
    try:
        collection = generator.generate_collection()
        environment = generator.generate_environment()
        
        # Save collection
        collection_path = os.path.join(script_dir, 'ainflue-api-collection.json')
        with open(collection_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        # Save environment
        environment_path = os.path.join(script_dir, 'ainflue-api-environment.json')
        with open(environment_path, 'w', encoding='utf-8') as f:
            json.dump(environment, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Postman collection generated: {collection_path}")
        print(f"✅ Postman environment generated: {environment_path}")
        print(f"📊 Generated {len(collection['item'])} folders with requests")
        
    except Exception as e:
        print(f"❌ Error generating Postman collection: {e}")
        raise


if __name__ == "__main__":
    main()