"""🔧 API Breaking Changes Detector - Ainflue Platform
================================================================
Expert: API_ARCHITECT + QUALITY_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Automatic detection of breaking changes in API contracts, schemas,
and interfaces to ensure backward compatibility.
================================================================
"""

import ast
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of API changes"""
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"
    DEPRECATED = "deprecated"
    ENHANCEMENT = "enhancement"

class BreakingSeverity(Enum):
    """Severity of breaking changes"""
    CRITICAL = "critical"  # Will break existing clients
    MAJOR = "major"       # Significant impact
    MINOR = "minor"       # Limited impact
    PATCH = "patch"       # Minimal impact

@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: str
    function_name: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    status_codes: List[int]
    documentation: Optional[str]
    decorators: List[str]
    file_path: str
    line_number: int
    signature_hash: str

@dataclass
class APIChange:
    """API change detected"""
    change_type: ChangeType
    severity: BreakingSeverity
    endpoint_path: str
    method: str
    description: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    impact_description: str
    remediation: Optional[str]
    file_path: str
    line_number: Optional[int]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class APIContract:
    """Complete API contract representation"""
    endpoints: List[APIEndpoint]
    schemas: Dict[str, Dict[str, Any]]
    version: str
    timestamp: datetime
    contract_hash: str

class APIBreakingChangesDetector:
    """
    Detector for API breaking changes and contract violations
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize API breaking changes detector"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.api_patterns = [
            r"@app\.(get|post|put|delete|patch)",
            r"@router\.(get|post|put|delete|patch)",
            r"@api\.(route|get|post|put|delete|patch)"
        ]
        self.current_contract: Optional[APIContract] = None
        self.previous_contract: Optional[APIContract] = None

    async def detect_breaking_changes(
        self, 
        baseline_contract_path: Optional[str] = None
    ) -> List[APIChange]:
        """Detect breaking changes in API"""
        self.logger.info("Starting API breaking changes detection")
        
        # Extract current API contract
        self.current_contract = await self._extract_api_contract()
        
        # Load baseline contract if provided
        if baseline_contract_path:
            self.previous_contract = self._load_baseline_contract(baseline_contract_path)
        
        # Compare contracts and detect changes
        changes = []
        if self.previous_contract:
            changes = await self._compare_contracts(
                self.previous_contract, 
                self.current_contract
            )
        else:
            self.logger.warning("No baseline contract found, cannot detect breaking changes")
        
        # Save current contract as baseline for future comparisons
        await self._save_contract(self.current_contract)
        
        self.logger.info(f"Breaking changes detection completed. Found {len(changes)} changes")
        return changes

    async def _extract_api_contract(self) -> APIContract:
        """Extract API contract from codebase"""
        endpoints = []
        schemas = {}
        
        # Find API files
        api_files = []
        for pattern in ["**/api/**/*.py", "**/routes/**/*.py", "**/endpoints/**/*.py"]:
            api_files.extend(self.project_root.glob(pattern))
        
        # Also check main application files
        for file_path in self.project_root.rglob("*.py"):
            if self._contains_api_definitions(file_path):
                api_files.append(file_path)
        
        # Extract endpoints from API files
        for file_path in api_files:
            try:
                file_endpoints = await self._extract_endpoints_from_file(file_path)
                endpoints.extend(file_endpoints)
            except Exception as e:
                self.logger.warning(f"Error extracting endpoints from {file_path}: {e}")
        
        # Extract schemas
        schemas = await self._extract_schemas()
        
        # Generate contract hash
        contract_content = json.dumps({
            "endpoints": [endpoint.__dict__ for endpoint in endpoints],
            "schemas": schemas
        }, sort_keys=True)
        contract_hash = hashlib.sha256(contract_content.encode()).hexdigest()
        
        return APIContract(
            endpoints=endpoints,
            schemas=schemas,
            version=self._get_api_version(),
            timestamp=datetime.utcnow(),
            contract_hash=contract_hash
        )

    def _contains_api_definitions(self, file_path: Path) -> bool:
        """Check if file contains API definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in self.api_patterns:
                    if re.search(pattern, content):
                        return True
        except:
            pass
        return False

    async def _extract_endpoints_from_file(self, file_path: Path) -> List[APIEndpoint]:
        """Extract API endpoints from a file"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            class APIVisitor(ast.NodeVisitor):
                def __init__(self, file_path):
                    self.file_path = str(file_path)
                    self.endpoints = []
                
                def visit_FunctionDef(self, node):
                    # Check for API decorators
                    api_info = self._extract_api_info(node)
                    if api_info:
                        endpoint = self._create_endpoint(node, api_info)
                        self.endpoints.append(endpoint)
                    
                    self.generic_visit(node)
                
                def _extract_api_info(self, node):
                    """Extract API information from decorators"""
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            decorator_name = self._get_decorator_name(decorator)
                            if any(pattern.replace('\\', '').replace('(', '').replace(')', '') 
                                   in decorator_name for pattern in [
                                       "app.get", "app.post", "app.put", "app.delete", "app.patch",
                                       "router.get", "router.post", "router.put", "router.delete", "router.patch"
                                   ]):
                                return self._parse_decorator(decorator, decorator_name)
                    return None
                
                def _get_decorator_name(self, decorator):
                    """Get decorator name from AST node"""
                    if isinstance(decorator.func, ast.Attribute):
                        return f"{decorator.func.value.id}.{decorator.func.attr}"
                    elif isinstance(decorator.func, ast.Name):
                        return decorator.func.id
                    return ""
                
                def _parse_decorator(self, decorator, decorator_name):
                    """Parse API decorator to extract route info"""
                    method = decorator_name.split('.')[-1].upper()
                    path = "/"
                    
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value
                    
                    return {"method": method, "path": path}
                
                def _create_endpoint(self, node, api_info):
                    """Create APIEndpoint from function node"""
                    # Extract parameters
                    parameters = []
                    for arg in node.args.args:
                        param_info = {
                            "name": arg.arg,
                            "type": self._get_type_annotation(arg),
                            "required": True  # Simplified, would need more analysis
                        }
                        parameters.append(param_info)
                    
                    # Extract return type
                    return_type = None
                    if node.returns:
                        return_type = ast.unparse(node.returns)
                    
                    # Get function signature for hashing
                    signature = f"{api_info['method']}:{api_info['path']}:{node.name}"
                    for param in parameters:
                        signature += f":{param['name']}:{param['type']}"
                    
                    signature_hash = hashlib.md5(signature.encode()).hexdigest()
                    
                    return APIEndpoint(
                        path=api_info["path"],
                        method=api_info["method"],
                        function_name=node.name,
                        parameters=parameters,
                        return_type=return_type,
                        status_codes=[200],  # Default, would need more analysis
                        documentation=ast.get_docstring(node),
                        decorators=[decorator_name],
                        file_path=self.file_path,
                        line_number=node.lineno,
                        signature_hash=signature_hash
                    )
                
                def _get_type_annotation(self, arg):
                    """Get type annotation for argument"""
                    if arg.annotation:
                        return ast.unparse(arg.annotation)
                    return "Any"
            
            visitor = APIVisitor(file_path)
            visitor.visit(tree)
            endpoints.extend(visitor.endpoints)
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
        
        return endpoints

    async def _extract_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Extract data schemas from codebase"""
        schemas = {}
        
        # Look for Pydantic models and schema definitions
        schema_files = []
        for pattern in ["**/schemas/**/*.py", "**/models/**/*.py", "**/dto/**/*.py"]:
            schema_files.extend(self.project_root.glob(pattern))
        
        for file_path in schema_files:
            try:
                file_schemas = await self._extract_schemas_from_file(file_path)
                schemas.update(file_schemas)
            except Exception as e:
                self.logger.warning(f"Error extracting schemas from {file_path}: {e}")
        
        return schemas

    async def _extract_schemas_from_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Extract schemas from a single file"""
        schemas = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            class SchemaVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.schemas = {}
                
                def visit_ClassDef(self, node):
                    # Check if it's a Pydantic model or similar schema
                    if self._is_schema_class(node):
                        schema_info = self._extract_schema_info(node)
                        self.schemas[node.name] = schema_info
                    
                    self.generic_visit(node)
                
                def _is_schema_class(self, node):
                    """Check if class is a schema definition"""
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            if base.id in ["BaseModel", "Schema", "Model"]:
                                return True
                        elif isinstance(base, ast.Attribute):
                            if base.attr in ["BaseModel", "Schema", "Model"]:
                                return True
                    return False
                
                def _extract_schema_info(self, node):
                    """Extract schema information from class"""
                    fields = {}
                    
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            field_type = ast.unparse(item.annotation) if item.annotation else "Any"
                            fields[field_name] = {"type": field_type, "required": True}
                    
                    return {
                        "fields": fields,
                        "docstring": ast.get_docstring(node)
                    }
            
            visitor = SchemaVisitor()
            visitor.visit(tree)
            schemas.update(visitor.schemas)
            
        except Exception as e:
            self.logger.error(f"Error parsing schemas from {file_path}: {e}")
        
        return schemas

    async def _compare_contracts(
        self, 
        old_contract: APIContract, 
        new_contract: APIContract
    ) -> List[APIChange]:
        """Compare two API contracts and detect changes"""
        changes = []
        
        # Create lookup maps
        old_endpoints = {f"{ep.method}:{ep.path}": ep for ep in old_contract.endpoints}
        new_endpoints = {f"{ep.method}:{ep.path}": ep for ep in new_contract.endpoints}
        
        # Check for removed endpoints (breaking)
        for key, old_ep in old_endpoints.items():
            if key not in new_endpoints:
                changes.append(APIChange(
                    change_type=ChangeType.BREAKING,
                    severity=BreakingSeverity.CRITICAL,
                    endpoint_path=old_ep.path,
                    method=old_ep.method,
                    description=f"Endpoint {old_ep.method} {old_ep.path} was removed",
                    old_value=key,
                    new_value=None,
                    impact_description="Existing clients will receive 404 errors",
                    remediation="Add deprecated endpoint or provide migration path",
                    file_path=old_ep.file_path,
                    line_number=old_ep.line_number
                ))
        
        # Check for added endpoints (non-breaking)
        for key, new_ep in new_endpoints.items():
            if key not in old_endpoints:
                changes.append(APIChange(
                    change_type=ChangeType.ENHANCEMENT,
                    severity=BreakingSeverity.PATCH,
                    endpoint_path=new_ep.path,
                    method=new_ep.method,
                    description=f"New endpoint {new_ep.method} {new_ep.path} was added",
                    old_value=None,
                    new_value=key,
                    impact_description="No impact on existing clients",
                    remediation=None,
                    file_path=new_ep.file_path,
                    line_number=new_ep.line_number
                ))
        
        # Check for modified endpoints
        for key in old_endpoints.keys() & new_endpoints.keys():
            old_ep = old_endpoints[key]
            new_ep = new_endpoints[key]
            
            endpoint_changes = await self._compare_endpoints(old_ep, new_ep)
            changes.extend(endpoint_changes)
        
        # Check schema changes
        schema_changes = await self._compare_schemas(old_contract.schemas, new_contract.schemas)
        changes.extend(schema_changes)
        
        return changes

    async def _compare_endpoints(self, old_ep: APIEndpoint, new_ep: APIEndpoint) -> List[APIChange]:
        """Compare two endpoints for changes"""
        changes = []
        
        # Check signature changes
        if old_ep.signature_hash != new_ep.signature_hash:
            # Check parameter changes
            old_params = {p["name"]: p for p in old_ep.parameters}
            new_params = {p["name"]: p for p in new_ep.parameters}
            
            # Removed parameters (breaking)
            for param_name in old_params.keys() - new_params.keys():
                changes.append(APIChange(
                    change_type=ChangeType.BREAKING,
                    severity=BreakingSeverity.MAJOR,
                    endpoint_path=old_ep.path,
                    method=old_ep.method,
                    description=f"Parameter '{param_name}' was removed",
                    old_value=old_params[param_name],
                    new_value=None,
                    impact_description="Clients passing this parameter will receive errors",
                    remediation="Make parameter optional or add backward compatibility",
                    file_path=new_ep.file_path,
                    line_number=new_ep.line_number
                ))
            
            # Added required parameters (breaking)
            for param_name in new_params.keys() - old_params.keys():
                param = new_params[param_name]
                if param.get("required", True):
                    changes.append(APIChange(
                        change_type=ChangeType.BREAKING,
                        severity=BreakingSeverity.MAJOR,
                        endpoint_path=old_ep.path,
                        method=old_ep.method,
                        description=f"Required parameter '{param_name}' was added",
                        old_value=None,
                        new_value=param,
                        impact_description="Existing clients will receive validation errors",
                        remediation="Make parameter optional with default value",
                        file_path=new_ep.file_path,
                        line_number=new_ep.line_number
                    ))
            
            # Changed parameter types (breaking)
            for param_name in old_params.keys() & new_params.keys():
                old_param = old_params[param_name]
                new_param = new_params[param_name]
                
                if old_param.get("type") != new_param.get("type"):
                    changes.append(APIChange(
                        change_type=ChangeType.BREAKING,
                        severity=BreakingSeverity.MAJOR,
                        endpoint_path=old_ep.path,
                        method=old_ep.method,
                        description=f"Parameter '{param_name}' type changed from {old_param.get('type')} to {new_param.get('type')}",
                        old_value=old_param.get("type"),
                        new_value=new_param.get("type"),
                        impact_description="Clients may send incompatible data types",
                        remediation="Accept both types or provide clear migration",
                        file_path=new_ep.file_path,
                        line_number=new_ep.line_number
                    ))
        
        # Check return type changes
        if old_ep.return_type != new_ep.return_type:
            changes.append(APIChange(
                change_type=ChangeType.BREAKING,
                severity=BreakingSeverity.MINOR,
                endpoint_path=old_ep.path,
                method=old_ep.method,
                description=f"Return type changed from {old_ep.return_type} to {new_ep.return_type}",
                old_value=old_ep.return_type,
                new_value=new_ep.return_type,
                impact_description="Clients expecting specific response format may break",
                remediation="Ensure backward compatibility in response format",
                file_path=new_ep.file_path,
                line_number=new_ep.line_number
            ))
        
        return changes

    async def _compare_schemas(
        self, 
        old_schemas: Dict[str, Dict[str, Any]], 
        new_schemas: Dict[str, Dict[str, Any]]
    ) -> List[APIChange]:
        """Compare schemas for breaking changes"""
        changes = []
        
        # Check for removed schemas
        for schema_name in old_schemas.keys() - new_schemas.keys():
            changes.append(APIChange(
                change_type=ChangeType.BREAKING,
                severity=BreakingSeverity.MAJOR,
                endpoint_path="N/A",
                method="SCHEMA",
                description=f"Schema '{schema_name}' was removed",
                old_value=schema_name,
                new_value=None,
                impact_description="APIs using this schema will break",
                remediation="Deprecate schema gradually or provide migration",
                file_path="schemas",
                line_number=None
            ))
        
        # Check for schema field changes
        for schema_name in old_schemas.keys() & new_schemas.keys():
            old_schema = old_schemas[schema_name]
            new_schema = new_schemas[schema_name]
            
            old_fields = old_schema.get("fields", {})
            new_fields = new_schema.get("fields", {})
            
            # Removed fields (breaking)
            for field_name in old_fields.keys() - new_fields.keys():
                changes.append(APIChange(
                    change_type=ChangeType.BREAKING,
                    severity=BreakingSeverity.MINOR,
                    endpoint_path="N/A",
                    method="SCHEMA",
                    description=f"Field '{field_name}' removed from schema '{schema_name}'",
                    old_value=field_name,
                    new_value=None,
                    impact_description="Clients expecting this field will break",
                    remediation="Keep field for backward compatibility",
                    file_path="schemas",
                    line_number=None
                ))
        
        return changes

    def _load_baseline_contract(self, contract_path: str) -> Optional[APIContract]:
        """Load baseline contract from file"""
        try:
            with open(contract_path, 'r') as f:
                data = json.load(f)
            
            endpoints = [
                APIEndpoint(**ep_data) for ep_data in data["endpoints"]
            ]
            
            return APIContract(
                endpoints=endpoints,
                schemas=data["schemas"],
                version=data["version"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                contract_hash=data["contract_hash"]
            )
        except Exception as e:
            self.logger.error(f"Error loading baseline contract: {e}")
            return None

    async def _save_contract(self, contract: APIContract, output_path: str = "api_contract.json"):
        """Save API contract to file"""
        try:
            data = {
                "endpoints": [
                    {
                        "path": ep.path,
                        "method": ep.method,
                        "function_name": ep.function_name,
                        "parameters": ep.parameters,
                        "return_type": ep.return_type,
                        "status_codes": ep.status_codes,
                        "documentation": ep.documentation,
                        "decorators": ep.decorators,
                        "file_path": ep.file_path,
                        "line_number": ep.line_number,
                        "signature_hash": ep.signature_hash
                    }
                    for ep in contract.endpoints
                ],
                "schemas": contract.schemas,
                "version": contract.version,
                "timestamp": contract.timestamp.isoformat(),
                "contract_hash": contract.contract_hash
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"API contract saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving contract: {e}")

    def _get_api_version(self) -> str:
        """Get API version from codebase"""
        # Try to find version in common locations
        version_files = ["version.py", "__init__.py", "setup.py", "pyproject.toml"]
        
        for version_file in version_files:
            file_path = self.project_root / version_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                        if version_match:
                            return version_match.group(1)
                except:
                    continue
        
        return "1.0.0"

    def generate_breaking_changes_report(self, changes: List[APIChange]) -> str:
        """Generate breaking changes report"""
        if not changes:
            return "No breaking changes detected."
        
        breaking_changes = [c for c in changes if c.change_type == ChangeType.BREAKING]
        non_breaking_changes = [c for c in changes if c.change_type != ChangeType.BREAKING]
        
        report = f"# API Breaking Changes Report\n\n"
        report += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if breaking_changes:
            report += f"## ⚠️ Breaking Changes ({len(breaking_changes)})\n\n"
            for change in breaking_changes:
                report += f"### {change.severity.value.title()}: {change.description}\n"
                report += f"- **Endpoint:** {change.method} {change.endpoint_path}\n"
                report += f"- **Impact:** {change.impact_description}\n"
                if change.remediation:
                    report += f"- **Remediation:** {change.remediation}\n"
                report += f"- **File:** {change.file_path}:{change.line_number}\n\n"
        
        if non_breaking_changes:
            report += f"## ✅ Non-Breaking Changes ({len(non_breaking_changes)})\n\n"
            for change in non_breaking_changes:
                report += f"- {change.description}\n"
        
        return report

# Global API breaking changes detector instance
api_breaking_detector = APIBreakingChangesDetector()

__all__ = [
    "APIBreakingChangesDetector",
    "APIEndpoint",
    "APIChange", 
    "APIContract",
    "ChangeType",
    "BreakingSeverity",
    "api_breaking_detector"
]