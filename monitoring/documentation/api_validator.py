"""
API Documentation Coverage Validation System
Ensures 100% API documentation coverage requirement
"""

import asyncio
import logging
import ast
import inspect
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class APIEndpoint:
    """API endpoint information"""
    path: str
    method: str
    function_name: str
    file_path: str
    line_number: int
    has_docstring: bool
    docstring_content: Optional[str]
    parameters: List[str]
    has_openapi_schema: bool
    is_documented: bool

@dataclass
class DocumentationReport:
    """API documentation coverage report"""
    total_endpoints: int
    documented_endpoints: int
    undocumented_endpoints: int
    coverage_percentage: float
    compliance_status: str  # "COMPLIANT" or "NON_COMPLIANT"
    endpoints: List[APIEndpoint]
    scan_date: datetime
    issues: List[str]

class APIDocumentationValidator:
    """
    Validates API documentation coverage
    Ensures 100% documentation coverage requirement
    """
    
    def __init__(self, project_root: str = "/home/runner/work/Ainflue/Ainflue"):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(project_root)
        self.api_directories = [
            "api",
            "endpoints", 
            "routes",
            "handlers"
        ]
        
        # API frameworks and decorators to look for
        self.api_decorators = [
            "app.get",
            "app.post", 
            "app.put",
            "app.delete",
            "app.patch",
            "router.get",
            "router.post",
            "router.put", 
            "router.delete",
            "router.patch",
            "@app.route",
            "@router.route",
            "@api_route"
        ]
        
        self.documentation_requirements = {
            'docstring_required': True,
            'openapi_schema_required': True,
            'parameter_documentation_required': True,
            'response_documentation_required': True,
            'example_required': False  # Optional but recommended
        }
        
    async def scan_api_documentation(self) -> DocumentationReport:
        """Scan all API endpoints and validate documentation coverage"""
        scan_start = datetime.now()
        self.logger.info("Starting API documentation coverage scan")
        
        # Find all API endpoints
        endpoints = await self._discover_api_endpoints()
        
        # Validate documentation for each endpoint
        for endpoint in endpoints:
            await self._validate_endpoint_documentation(endpoint)
        
        # Calculate coverage metrics
        total_endpoints = len(endpoints)
        documented_endpoints = len([e for e in endpoints if e.is_documented])
        undocumented_endpoints = total_endpoints - documented_endpoints
        
        coverage_percentage = (documented_endpoints / total_endpoints * 100) if total_endpoints > 0 else 100.0
        compliance_status = "COMPLIANT" if coverage_percentage >= 100.0 else "NON_COMPLIANT"
        
        # Collect issues
        issues = []
        for endpoint in endpoints:
            if not endpoint.is_documented:
                issues.append(f"Undocumented endpoint: {endpoint.method} {endpoint.path} ({endpoint.function_name})")
            if not endpoint.has_docstring:
                issues.append(f"Missing docstring: {endpoint.method} {endpoint.path}")
            if not endpoint.has_openapi_schema:
                issues.append(f"Missing OpenAPI schema: {endpoint.method} {endpoint.path}")
        
        report = DocumentationReport(
            total_endpoints=total_endpoints,
            documented_endpoints=documented_endpoints,
            undocumented_endpoints=undocumented_endpoints,
            coverage_percentage=coverage_percentage,
            compliance_status=compliance_status,
            endpoints=endpoints,
            scan_date=scan_start,
            issues=issues
        )
        
        # Log results
        self.logger.info(
            f"API documentation scan completed: {documented_endpoints}/{total_endpoints} endpoints documented "
            f"({coverage_percentage:.1f}%) - Status: {compliance_status}"
        )
        
        if compliance_status == "NON_COMPLIANT":
            self.logger.warning(f"Documentation compliance violation: {len(issues)} issues found")
            for issue in issues[:10]:  # Log first 10 issues
                self.logger.warning(f"  - {issue}")
        
        return report
        
    async def _discover_api_endpoints(self) -> List[APIEndpoint]:
        """Discover all API endpoints in the project"""
        endpoints = []
        
        # Search for Python files containing API endpoints
        for api_dir in self.api_directories:
            api_path = self.project_root / api_dir
            if api_path.exists():
                endpoints.extend(await self._scan_directory_for_endpoints(api_path))
        
        # Also scan root level files that might contain APIs
        root_files = ["main.py", "app.py", "server.py"]
        for file_name in root_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                endpoints.extend(await self._scan_file_for_endpoints(file_path))
        
        return endpoints
        
    async def _scan_directory_for_endpoints(self, directory: Path) -> List[APIEndpoint]:
        """Scan directory recursively for API endpoints"""
        endpoints = []
        
        for file_path in directory.rglob("*.py"):
            if file_path.name.startswith("test_"):
                continue  # Skip test files
                
            try:
                file_endpoints = await self._scan_file_for_endpoints(file_path)
                endpoints.extend(file_endpoints)
            except Exception as e:
                self.logger.error(f"Error scanning file {file_path}: {e}")
        
        return endpoints
        
    async def _scan_file_for_endpoints(self, file_path: Path) -> List[APIEndpoint]:
        """Scan individual file for API endpoints"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to find API endpoints
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    endpoint = await self._check_function_for_api_endpoint(node, file_path, content)
                    if endpoint:
                        endpoints.append(endpoint)
                        
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
        
        return endpoints
        
    async def _check_function_for_api_endpoint(self, func_node: ast.FunctionDef, 
                                              file_path: Path, file_content: str) -> Optional[APIEndpoint]:
        """Check if function is an API endpoint"""
        
        # Look for API decorators
        api_decorator_found = False
        method = "GET"  # Default
        path = ""
        
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Handle @app.get("/path") style decorators
                if isinstance(decorator.func, ast.Attribute):
                    decorator_name = f"{decorator.func.value.id}.{decorator.func.attr}"
                    if any(dec in decorator_name for dec in self.api_decorators):
                        api_decorator_found = True
                        method = decorator.func.attr.upper()
                        
                        # Extract path from first argument
                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
            
            elif isinstance(decorator, ast.Name):
                # Handle simple decorators like @api_route
                if decorator.id in self.api_decorators:
                    api_decorator_found = True
        
        if not api_decorator_found:
            return None
        
        # Extract function information
        has_docstring = bool(ast.get_docstring(func_node))
        docstring_content = ast.get_docstring(func_node)
        
        # Get function parameters
        parameters = [arg.arg for arg in func_node.args.args if arg.arg != 'self']
        
        # Check for OpenAPI schema (simplified check)
        has_openapi_schema = self._has_openapi_schema(file_content, func_node.name)
        
        endpoint = APIEndpoint(
            path=path or f"/{func_node.name}",
            method=method,
            function_name=func_node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=func_node.lineno,
            has_docstring=has_docstring,
            docstring_content=docstring_content,
            parameters=parameters,
            has_openapi_schema=has_openapi_schema,
            is_documented=False  # Will be set by validation
        )
        
        return endpoint
        
    def _has_openapi_schema(self, file_content: str, function_name: str) -> bool:
        """Check if function has OpenAPI schema documentation"""
        # Look for common OpenAPI patterns
        openapi_patterns = [
            f"@{function_name}.responses",
            f"response_model=",
            f"response_description=",
            f"tags=",
            f"summary=",
            f"description=",
            "Response(",
            "HTTPException(",
            "status_code="
        ]
        
        # Check if any OpenAPI patterns are found near the function
        lines = file_content.split('\n')
        for i, line in enumerate(lines):
            if function_name in line and any(pattern in line for pattern in openapi_patterns):
                return True
        
        return False
        
    async def _validate_endpoint_documentation(self, endpoint: APIEndpoint):
        """Validate documentation completeness for an endpoint"""
        is_documented = True
        
        # Check docstring requirement
        if self.documentation_requirements['docstring_required'] and not endpoint.has_docstring:
            is_documented = False
        
        # Check OpenAPI schema requirement
        if self.documentation_requirements['openapi_schema_required'] and not endpoint.has_openapi_schema:
            is_documented = False
        
        # Check parameter documentation
        if (self.documentation_requirements['parameter_documentation_required'] and 
            endpoint.parameters and endpoint.docstring_content):
            # Simple check: see if parameters are mentioned in docstring
            if endpoint.docstring_content:
                for param in endpoint.parameters:
                    if param not in endpoint.docstring_content.lower():
                        is_documented = False
                        break
        
        # Check response documentation
        if (self.documentation_requirements['response_documentation_required'] and 
            endpoint.docstring_content):
            # Simple check: look for response documentation keywords
            response_keywords = ['return', 'response', 'status', 'error']
            if endpoint.docstring_content and not any(
                keyword in endpoint.docstring_content.lower() for keyword in response_keywords
            ):
                is_documented = False
        
        endpoint.is_documented = is_documented
        
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get current API documentation compliance status"""
        report = await self.scan_api_documentation()
        
        return {
            'status': report.compliance_status,
            'coverage_percentage': report.coverage_percentage,
            'target_coverage': 100.0,
            'documented_endpoints': report.documented_endpoints,
            'total_endpoints': report.total_endpoints,
            'undocumented_count': report.undocumented_endpoints,
            'compliant': report.compliance_status == 'COMPLIANT',
            'last_scan': report.scan_date.isoformat()
        }

# Global API documentation validator instance
api_doc_validator = APIDocumentationValidator()