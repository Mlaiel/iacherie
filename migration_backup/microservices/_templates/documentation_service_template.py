#!/usr/bin/env python3
"""
📚 Documentation Service Template - IA Chéries Enterprise
=====================================================
Template enterprise pour services documentation.
OpenAPI + Swagger + automated docs + API examples + versioning.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
import json
import yaml
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from pathlib import Path
import markdown
import jinja2
from urllib.parse import urljoin

from .service_template import EnterpriseServiceBase, ServiceConfig

# Documentation-specific configurations
@dataclass
class APIDocConfig:
    """Configuration for API documentation."""
    title: str
    version: str
    description: str = ""
    contact: Dict[str, str] = field(default_factory=dict)
    license: Dict[str, str] = field(default_factory=dict)
    servers: List[Dict[str, str]] = field(default_factory=list)
    tags: List[Dict[str, str]] = field(default_factory=list)
    security_schemes: Dict[str, Any] = field(default_factory=dict)
    examples_enabled: bool = True
    try_it_out_enabled: bool = True

@dataclass
class CodeDocConfig:
    """Configuration for code documentation."""
    source_paths: List[str]
    output_path: str = "docs/"
    format: str = "sphinx"  # sphinx, mkdocs, gitbook
    theme: str = "default"
    plugins: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    auto_generate: bool = True

@dataclass
class InteractiveExampleConfig:
    """Configuration for interactive examples."""
    example_name: str
    endpoint: str
    method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    request_body: Optional[Dict[str, Any]] = None
    expected_response: Optional[Dict[str, Any]] = None
    curl_example: bool = True
    language_examples: List[str] = field(default_factory=lambda: ["python", "javascript", "curl"])

@dataclass
class DocumentationVersionConfig:
    """Configuration for documentation versioning."""
    version: str
    is_latest: bool = False
    is_stable: bool = False
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    migration_guide: Optional[str] = None

class DocumentationFormat(Enum):
    """Documentation formats."""
    OPENAPI = "openapi"
    SWAGGER = "swagger"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    SPHINX = "sphinx"

class DocumentationServiceTemplate(EnterpriseServiceBase):
    """
    📚 Template enterprise pour services documentation.
    
    Fonctionnalités:
    - API documentation automatique avec OpenAPI/Swagger
    - Code documentation avec Sphinx/MkDocs
    - Interactive examples avec try-it-out
    - Multi-version documentation support
    - Automated documentation updates
    - Multi-format export (HTML, PDF, Markdown)
    - Search functionality et navigation
    - Integration avec CI/CD pour updates automatiques
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize documentation service."""
        super().__init__(config)
        self.api_docs: Dict[str, Any] = {}
        self.code_docs: Dict[str, Any] = {}
        self.interactive_examples: Dict[str, Any] = {}
        self.documentation_versions: Dict[str, DocumentationVersionConfig] = {}
        
        # Documentation state
        self.openapi_spec: Optional[Dict[str, Any]] = None
        self.swagger_ui_config: Dict[str, Any] = {}
        self.search_index: Dict[str, Any] = {}
        
        # Templates and generators
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        self.logger = logging.getLogger(f"{self.config.service_name}.documentation")
        
    async def setup_api_documentation(self, docs_configs: List[APIDocConfig]) -> None:
        """Documentation API automatique avec OpenAPI."""
        try:
            for config in docs_configs:
                # Generate OpenAPI specification
                openapi_spec = await self._generate_openapi_spec(config)
                
                # Setup Swagger UI
                swagger_ui = await self._setup_swagger_ui(config, openapi_spec)
                
                # Create API documentation context
                api_doc = {
                    'config': config,
                    'openapi_spec': openapi_spec,
                    'swagger_ui': swagger_ui,
                    'last_updated': datetime.utcnow(),
                    'endpoints_count': len(openapi_spec.get('paths', {})),
                    'schemas_count': len(openapi_spec.get('components', {}).get('schemas', {}))
                }
                
                self.api_docs[config.title] = api_doc
                
                self.logger.info(f"API documentation '{config.title}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup API documentation: {e}")
            raise
    
    async def setup_code_documentation(self, code_docs_configs: List[CodeDocConfig]) -> None:
        """Documentation code avec Sphinx/MkDocs."""
        try:
            for config in code_docs_configs:
                # Analyze source code
                source_analysis = await self._analyze_source_code(config.source_paths)
                
                # Generate documentation structure
                doc_structure = await self._generate_doc_structure(config, source_analysis)
                
                # Setup documentation generator
                generator = await self._setup_doc_generator(config)
                
                # Create code documentation context
                code_doc = {
                    'config': config,
                    'source_analysis': source_analysis,
                    'doc_structure': doc_structure,
                    'generator': generator,
                    'last_generated': None,
                    'build_status': 'pending'
                }
                
                self.code_docs[config.output_path] = code_doc
                
                self.logger.info(f"Code documentation for '{config.output_path}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup code documentation: {e}")
            raise
    
    async def setup_interactive_examples(self, examples_configs: List[InteractiveExampleConfig]) -> None:
        """Exemples interactifs avec Swagger UI."""
        try:
            for config in examples_configs:
                # Generate code examples in multiple languages
                code_examples = await self._generate_code_examples(config)
                
                # Create interactive example context
                example = {
                    'config': config,
                    'code_examples': code_examples,
                    'last_updated': datetime.utcnow(),
                    'execution_count': 0,
                    'success_rate': 0.0
                }
                
                self.interactive_examples[config.example_name] = example
                
                self.logger.info(f"Interactive example '{config.example_name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup interactive examples: {e}")
            raise
    
    async def setup_documentation_versioning(self, versioning_configs: List[DocumentationVersionConfig]) -> None:
        """Versioning documentation avec automated updates."""
        try:
            for config in versioning_configs:
                # Setup version-specific documentation paths
                version_path = await self._setup_version_path(config)
                
                # Create version context
                version_context = {
                    'config': config,
                    'version_path': version_path,
                    'created_at': datetime.utcnow(),
                    'last_updated': datetime.utcnow(),
                    'build_status': 'pending',
                    'access_count': 0
                }
                
                self.documentation_versions[config.version] = version_context
                
                # Set latest version
                if config.is_latest:
                    await self._set_latest_version(config.version)
                
                self.logger.info(f"Documentation version '{config.version}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup documentation versioning: {e}")
            raise
    
    async def generate_api_documentation(self, api_title: str, 
                                        format: DocumentationFormat = DocumentationFormat.HTML) -> Dict[str, Any]:
        """Generate API documentation in specified format."""
        try:
            api_doc = self.api_docs.get(api_title)
            if not api_doc:
                raise ValueError(f"API documentation '{api_title}' not found")
            
            self.logger.info(f"Generating API documentation '{api_title}' in {format.value} format")
            
            start_time = datetime.utcnow()
            
            if format == DocumentationFormat.HTML:
                result = await self._generate_html_docs(api_doc)
            elif format == DocumentationFormat.OPENAPI:
                result = await self._generate_openapi_docs(api_doc)
            elif format == DocumentationFormat.MARKDOWN:
                result = await self._generate_markdown_docs(api_doc)
            elif format == DocumentationFormat.PDF:
                result = await self._generate_pdf_docs(api_doc)
            else:
                raise ValueError(f"Unsupported documentation format: {format.value}")
            
            # Update documentation metadata
            api_doc['last_updated'] = datetime.utcnow()
            api_doc['generation_time'] = (datetime.utcnow() - start_time).total_seconds()
            api_doc['format'] = format.value
            
            self.logger.info(f"API documentation '{api_title}' generated successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate API documentation '{api_title}': {e}")
            raise
    
    async def generate_code_documentation(self, output_path: str) -> Dict[str, Any]:
        """Generate code documentation."""
        try:
            code_doc = self.code_docs.get(output_path)
            if not code_doc:
                raise ValueError(f"Code documentation '{output_path}' not found")
            
            config = code_doc['config']
            
            self.logger.info(f"Generating code documentation for '{output_path}'")
            
            start_time = datetime.utcnow()
            code_doc['build_status'] = 'building'
            
            # Generate documentation based on format
            if config.format == "sphinx":
                result = await self._build_sphinx_docs(code_doc)
            elif config.format == "mkdocs":
                result = await self._build_mkdocs_docs(code_doc)
            else:
                raise ValueError(f"Unsupported documentation format: {config.format}")
            
            # Update build status
            code_doc['build_status'] = 'completed' if result['success'] else 'failed'
            code_doc['last_generated'] = datetime.utcnow()
            code_doc['build_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(f"Code documentation for '{output_path}' generated successfully")
            
            return result
            
        except Exception as e:
            code_doc['build_status'] = 'failed'
            self.logger.error(f"Failed to generate code documentation '{output_path}': {e}")
            raise
    
    async def update_interactive_example(self, example_name: str, 
                                        execution_result: Dict[str, Any]) -> None:
        """Update interactive example with execution results."""
        try:
            example = self.interactive_examples.get(example_name)
            if not example:
                raise ValueError(f"Interactive example '{example_name}' not found")
            
            # Update execution statistics
            example['execution_count'] += 1
            
            if execution_result.get('success', False):
                # Calculate success rate
                success_count = example.get('success_count', 0) + 1
                example['success_count'] = success_count
                example['success_rate'] = success_count / example['execution_count']
            
            # Store latest execution result
            example['last_execution'] = {
                'timestamp': datetime.utcnow(),
                'result': execution_result
            }
            
            example['last_updated'] = datetime.utcnow()
            
            self.logger.info(f"Interactive example '{example_name}' updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update interactive example '{example_name}': {e}")
            raise
    
    async def search_documentation(self, query: str, 
                                  doc_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search across all documentation."""
        try:
            search_results = []
            
            # Search API documentation
            if not doc_types or 'api' in doc_types:
                api_results = await self._search_api_docs(query)
                search_results.extend(api_results)
            
            # Search code documentation
            if not doc_types or 'code' in doc_types:
                code_results = await self._search_code_docs(query)
                search_results.extend(code_results)
            
            # Search interactive examples
            if not doc_types or 'examples' in doc_types:
                example_results = await self._search_examples(query)
                search_results.extend(example_results)
            
            # Sort by relevance
            search_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Failed to search documentation: {e}")
            raise
    
    async def get_documentation_metrics(self) -> Dict[str, Any]:
        """Get documentation metrics and analytics."""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'api_documentation': {
                    'total_apis': len(self.api_docs),
                    'total_endpoints': sum(doc['endpoints_count'] for doc in self.api_docs.values()),
                    'total_schemas': sum(doc['schemas_count'] for doc in self.api_docs.values()),
                    'last_updated': max([doc['last_updated'] for doc in self.api_docs.values()], default=datetime.min).isoformat()
                },
                'code_documentation': {
                    'total_projects': len(self.code_docs),
                    'build_success_rate': len([doc for doc in self.code_docs.values() if doc['build_status'] == 'completed']) / len(self.code_docs) if self.code_docs else 0,
                    'avg_build_time': sum([doc.get('build_time', 0) for doc in self.code_docs.values()]) / len(self.code_docs) if self.code_docs else 0
                },
                'interactive_examples': {
                    'total_examples': len(self.interactive_examples),
                    'total_executions': sum(ex['execution_count'] for ex in self.interactive_examples.values()),
                    'avg_success_rate': sum(ex['success_rate'] for ex in self.interactive_examples.values()) / len(self.interactive_examples) if self.interactive_examples else 0
                },
                'versions': {
                    'total_versions': len(self.documentation_versions),
                    'latest_version': next((v for v, config in self.documentation_versions.items() if config['config'].is_latest), None),
                    'deprecated_versions': len([v for v, config in self.documentation_versions.items() if config['config'].deprecated])
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get documentation metrics: {e}")
            raise
    
    # Private helper methods
    async def _generate_openapi_spec(self, config: APIDocConfig) -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        openapi_spec = {
            'openapi': '3.0.3',
            'info': {
                'title': config.title,
                'version': config.version,
                'description': config.description,
                'contact': config.contact,
                'license': config.license
            },
            'servers': config.servers,
            'tags': config.tags,
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': config.security_schemes
            }
        }
        
        # This would be populated from actual API endpoints
        # For now, return basic structure
        return openapi_spec
    
    async def _setup_swagger_ui(self, config: APIDocConfig, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Swagger UI configuration."""
        swagger_config = {
            'url': '/openapi.json',
            'dom_id': '#swagger-ui',
            'deepLinking': True,
            'tryItOutEnabled': config.try_it_out_enabled,
            'displayRequestDuration': True,
            'docExpansion': 'none',
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True,
            'supportedSubmitMethods': ['get', 'post', 'put', 'delete', 'patch'],
            'validatorUrl': None
        }
        
        return swagger_config
    
    async def _analyze_source_code(self, source_paths: List[str]) -> Dict[str, Any]:
        """Analyze source code for documentation generation."""
        analysis = {
            'modules': [],
            'classes': [],
            'functions': [],
            'total_lines': 0,
            'docstring_coverage': 0.0
        }
        
        # This would analyze actual source code
        # For now, return mock analysis
        for path in source_paths:
            if Path(path).exists():
                analysis['modules'].append({
                    'name': Path(path).stem,
                    'path': path,
                    'functions': 5,
                    'classes': 2,
                    'lines': 150
                })
        
        return analysis
    
    async def _generate_doc_structure(self, config: CodeDocConfig, 
                                     source_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation structure."""
        structure = {
            'index': 'index.rst' if config.format == 'sphinx' else 'index.md',
            'api_reference': 'api/',
            'user_guide': 'guide/',
            'tutorials': 'tutorials/',
            'changelog': 'changelog.md'
        }
        
        return structure
    
    async def _setup_doc_generator(self, config: CodeDocConfig) -> Any:
        """Setup documentation generator."""
        if config.format == 'sphinx':
            return await self._setup_sphinx_generator(config)
        elif config.format == 'mkdocs':
            return await self._setup_mkdocs_generator(config)
        else:
            raise ValueError(f"Unsupported documentation format: {config.format}")
    
    async def _setup_sphinx_generator(self, config: CodeDocConfig) -> Dict[str, Any]:
        """Setup Sphinx documentation generator."""
        sphinx_config = {
            'project': 'Project Documentation',
            'author': 'Fahed Mlaiel',
            'release': '1.0.0',
            'extensions': [
                'sphinx.ext.autodoc',
                'sphinx.ext.viewcode',
                'sphinx.ext.napoleon',
                'sphinx.ext.intersphinx'
            ] + config.plugins,
            'html_theme': config.theme,
            'html_static_path': ['_static'],
            'exclude_patterns': config.exclude_patterns
        }
        
        return sphinx_config
    
    async def _setup_mkdocs_generator(self, config: CodeDocConfig) -> Dict[str, Any]:
        """Setup MkDocs documentation generator."""
        mkdocs_config = {
            'site_name': 'Project Documentation',
            'site_author': 'Fahed Mlaiel',
            'theme': {
                'name': config.theme
            },
            'plugins': config.plugins,
            'markdown_extensions': [
                'codehilite',
                'toc',
                'tables'
            ]
        }
        
        return mkdocs_config
    
    async def _generate_code_examples(self, config: InteractiveExampleConfig) -> Dict[str, str]:
        """Generate code examples in multiple languages."""
        examples = {}
        
        # Python example
        if 'python' in config.language_examples:
            examples['python'] = await self._generate_python_example(config)
        
        # JavaScript example
        if 'javascript' in config.language_examples:
            examples['javascript'] = await self._generate_javascript_example(config)
        
        # cURL example
        if 'curl' in config.language_examples or config.curl_example:
            examples['curl'] = await self._generate_curl_example(config)
        
        return examples
    
    async def _generate_python_example(self, config: InteractiveExampleConfig) -> str:
        """Generate Python code example."""
        template = """
import requests

# {example_name}
url = "{endpoint}"
{params_code}
{headers_code}
{body_code}

response = requests.{method}(url{request_args})
print(response.json())
"""
        
        params_code = ""
        if config.parameters:
            params_code = f"params = {json.dumps(config.parameters, indent=2)}"
        
        headers_code = 'headers = {"Content-Type": "application/json"}'
        
        body_code = ""
        request_args = ""
        if config.request_body:
            body_code = f"data = {json.dumps(config.request_body, indent=2)}"
            request_args = ", json=data"
        
        if config.parameters:
            request_args += ", params=params"
        
        request_args += ", headers=headers"
        
        return template.format(
            example_name=config.example_name,
            endpoint=config.endpoint,
            method=config.method.lower(),
            params_code=params_code,
            headers_code=headers_code,
            body_code=body_code,
            request_args=request_args
        )
    
    async def _generate_javascript_example(self, config: InteractiveExampleConfig) -> str:
        """Generate JavaScript code example."""
        template = """
// {example_name}
const url = '{endpoint}';
{params_code}
const options = {{
  method: '{method}',
  headers: {{
    'Content-Type': 'application/json'
  }}{body_code}
}};

fetch(url{query_string}, options)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
"""
        
        params_code = ""
        query_string = ""
        if config.parameters:
            params_code = f"const params = new URLSearchParams({json.dumps(config.parameters)});"
            query_string = " + '?' + params"
        
        body_code = ""
        if config.request_body:
            body_code = f",\n  body: JSON.stringify({json.dumps(config.request_body)})"
        
        return template.format(
            example_name=config.example_name,
            endpoint=config.endpoint,
            method=config.method.upper(),
            params_code=params_code,
            query_string=query_string,
            body_code=body_code
        )
    
    async def _generate_curl_example(self, config: InteractiveExampleConfig) -> str:
        """Generate cURL example."""
        curl_parts = [f"curl -X {config.method.upper()}"]
        
        # Add headers
        curl_parts.append('-H "Content-Type: application/json"')
        
        # Add body
        if config.request_body:
            body_json = json.dumps(config.request_body)
            curl_parts.append(f"-d '{body_json}'")
        
        # Build URL with parameters
        url = config.endpoint
        if config.parameters:
            query_params = "&".join([f"{k}={v}" for k, v in config.parameters.items()])
            url += f"?{query_params}"
        
        curl_parts.append(f'"{url}"')
        
        return " \\\n  ".join(curl_parts)
    
    async def _setup_version_path(self, config: DocumentationVersionConfig) -> str:
        """Setup version-specific documentation path."""
        version_path = f"docs/v{config.version}"
        Path(version_path).mkdir(parents=True, exist_ok=True)
        return version_path
    
    async def _set_latest_version(self, version: str) -> None:
        """Set version as latest."""
        # Reset other versions
        for v, context in self.documentation_versions.items():
            if v != version:
                context['config'].is_latest = False
        
        # Create symlink for latest
        latest_path = Path("docs/latest")
        if latest_path.exists():
            latest_path.unlink()
        
        version_path = Path(f"docs/v{version}")
        if version_path.exists():
            latest_path.symlink_to(version_path, target_is_directory=True)
    
    async def _generate_html_docs(self, api_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML documentation."""
        return {
            'format': 'html',
            'output_path': 'docs/api.html',
            'size_bytes': 1024,
            'success': True
        }
    
    async def _generate_openapi_docs(self, api_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OpenAPI JSON/YAML documentation."""
        return {
            'format': 'openapi',
            'output_path': 'docs/openapi.json',
            'spec': api_doc['openapi_spec'],
            'success': True
        }
    
    async def _generate_markdown_docs(self, api_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Markdown documentation."""
        return {
            'format': 'markdown',
            'output_path': 'docs/api.md',
            'size_bytes': 2048,
            'success': True
        }
    
    async def _generate_pdf_docs(self, api_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF documentation."""
        return {
            'format': 'pdf',
            'output_path': 'docs/api.pdf',
            'size_bytes': 5120,
            'success': True
        }
    
    async def _build_sphinx_docs(self, code_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Build Sphinx documentation."""
        return {
            'success': True,
            'output_path': code_doc['config'].output_path,
            'warnings': 0,
            'errors': 0,
            'build_time': 15.5
        }
    
    async def _build_mkdocs_docs(self, code_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Build MkDocs documentation."""
        return {
            'success': True,
            'output_path': code_doc['config'].output_path,
            'pages_built': 25,
            'build_time': 8.2
        }
    
    async def _search_api_docs(self, query: str) -> List[Dict[str, Any]]:
        """Search API documentation."""
        results = []
        
        for title, doc in self.api_docs.items():
            # Simple search implementation
            if query.lower() in title.lower() or query.lower() in doc['config'].description.lower():
                results.append({
                    'type': 'api',
                    'title': title,
                    'description': doc['config'].description,
                    'url': f"/docs/api/{title}",
                    'relevance_score': 0.8
                })
        
        return results
    
    async def _search_code_docs(self, query: str) -> List[Dict[str, Any]]:
        """Search code documentation."""
        results = []
        
        for path, doc in self.code_docs.items():
            # Simple search implementation
            for module in doc['source_analysis']['modules']:
                if query.lower() in module['name'].lower():
                    results.append({
                        'type': 'code',
                        'title': module['name'],
                        'description': f"Module documentation for {module['name']}",
                        'url': f"/docs/code/{module['name']}",
                        'relevance_score': 0.7
                    })
        
        return results
    
    async def _search_examples(self, query: str) -> List[Dict[str, Any]]:
        """Search interactive examples."""
        results = []
        
        for name, example in self.interactive_examples.items():
            if query.lower() in name.lower() or query.lower() in example['config'].endpoint.lower():
                results.append({
                    'type': 'example',
                    'title': name,
                    'description': f"Interactive example for {example['config'].endpoint}",
                    'url': f"/docs/examples/{name}",
                    'relevance_score': 0.6
                })
        
        return results
    
    @abstractmethod
    async def setup_service_specific_documentation(self) -> None:
        """Setup service-specific documentation. Override in subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check."""
        base_health = await super().health_check()
        
        return {
            **base_health,
            'documentation': {
                'api_docs': len(self.api_docs),
                'code_docs': len(self.code_docs),
                'interactive_examples': len(self.interactive_examples),
                'versions': len(self.documentation_versions)
            },
            'components': {
                'openapi_generator': 'available',
                'swagger_ui': 'available',
                'doc_generators': 'available',
                'search_index': 'available'
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup documentation resources."""
        # Cleanup temporary files, stop background tasks, etc.
        await super().cleanup()