"""📋 API Contract Validator - Ainflue Platform
================================================================
Expert: API_ARCHITECT + QUALITY_ENGINEER + BACKEND_SENIOR + TESTING_LEAD
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Advanced API contract validation system that ensures API consistency,
backward compatibility, and adherence to OpenAPI specifications.
================================================================
"""

import asyncio
import json
import logging
import time
import hashlib
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml
import jsonschema
import requests
import aiohttp
from urllib.parse import urljoin
import re

# OpenAPI/Swagger libraries
try:
    import openapi3
    from openapi3 import OpenAPI
    from openapi_spec_validator import validate_spec
    from openapi_spec_validator.exceptions import OpenAPIValidationError
    HAS_OPENAPI_LIBS = True
except ImportError:
    HAS_OPENAPI_LIBS = False

logger = logging.getLogger(__name__)

class ContractValidationType(Enum):
    """Types of contract validation"""
    SCHEMA_VALIDATION = "schema_validation"
    BACKWARD_COMPATIBILITY = "backward_compatibility"
    FORWARD_COMPATIBILITY = "forward_compatibility"
    ENDPOINT_CONSISTENCY = "endpoint_consistency"
    RESPONSE_FORMAT = "response_format"
    ERROR_HANDLING = "error_handling"
    SECURITY_SCHEMES = "security_schemes"
    DOCUMENTATION_COMPLETENESS = "documentation_completeness"

class ViolationSeverity(Enum):
    """Severity levels for contract violations"""
    CRITICAL = "critical"      # Breaking changes
    HIGH = "high"             # Major issues
    MEDIUM = "medium"         # Minor issues
    LOW = "low"              # Warnings
    INFO = "info"            # Informational

class ContractChangeType(Enum):
    """Types of API contract changes"""
    BREAKING_CHANGE = "breaking_change"
    NON_BREAKING_CHANGE = "non_breaking_change"
    ADDITION = "addition"
    DEPRECATION = "deprecation"
    MODIFICATION = "modification"
    REMOVAL = "removal"

@dataclass
class ContractViolation:
    """Individual contract violation"""
    violation_type: ContractValidationType
    severity: ViolationSeverity
    message: str
    endpoint: str
    method: str
    field_path: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None
    documentation_url: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class ContractChange:
    """API contract change detection"""
    change_type: ContractChangeType
    severity: ViolationSeverity
    endpoint: str
    method: str
    change_description: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    impact_assessment: str = ""
    migration_guide: Optional[str] = None

@dataclass
class EndpointValidation:
    """Validation result for a single endpoint"""
    endpoint: str
    method: str
    is_valid: bool
    violations: List[ContractViolation] = field(default_factory=list)
    schema_valid: bool = True
    response_examples_valid: bool = True
    security_properly_defined: bool = True
    documentation_complete: bool = True
    performance_considerations: List[str] = field(default_factory=list)

@dataclass
class APIContractReport:
    """Comprehensive API contract validation report"""
    api_name: str
    api_version: str
    spec_version: str
    validation_timestamp: datetime
    overall_valid: bool
    total_endpoints: int
    valid_endpoints: int
    total_violations: int
    critical_violations: int
    high_violations: int
    endpoint_validations: List[EndpointValidation]
    contract_changes: List[ContractChange]
    compatibility_score: float
    documentation_score: float
    security_score: float
    recommendations: List[str]
    validation_time: float

class APIContractValidator:
    """
    Comprehensive API contract validator for OpenAPI specifications
    """
    
    def __init__(self, project_root -> None: Optional[str] = None) -> None:
        """Initialize API contract validator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.spec_cache: Dict[str, Any] = {}
        self.validation_rules = self._load_validation_rules()
        self.compatibility_matrix = self._load_compatibility_matrix()
        
        # API specifications directory
        self.specs_dir = self.project_root / "api" / "specs"
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        
        # Historical versions for compatibility checking
        self.versions_dir = self.project_root / "api" / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration"""
        return {
            "required_fields": {
                "info": ["title", "version", "description"],
                "paths": {
                    "required_methods": ["get", "post", "put", "delete"],
                    "required_responses": ["200", "400", "401", "403", "404", "500"]
                },
                "components": {
                    "required_schemas": True,
                    "required_security_schemes": True
                }
            },
            "naming_conventions": {
                "endpoints": r"^/api/v\d+/[a-z0-9\-/{}]+$",
                "parameters": r"^[a-zA-Z][a-zA-Z0-9_]*$",
                "schemas": r"^[A-Z][a-zA-Z0-9]*$"
            },
            "security_requirements": {
                "authentication_required": True,
                "https_only": True,
                "rate_limiting": True
            },
            "documentation_requirements": {
                "endpoint_descriptions": True,
                "parameter_descriptions": True,
                "response_descriptions": True,
                "example_requests": True,
                "example_responses": True
            }
        }

    def _load_compatibility_matrix(self) -> Dict[str, List[str]]:
        """Load backward compatibility rules"""
        return {
            "breaking_changes": [
                "removing_endpoint",
                "removing_parameter",
                "changing_parameter_type",
                "removing_response_field",
                "changing_response_type",
                "adding_required_parameter",
                "changing_endpoint_url",
                "removing_http_method"
            ],
            "non_breaking_changes": [
                "adding_endpoint",
                "adding_optional_parameter",
                "adding_response_field",
                "adding_http_method",
                "improving_documentation",
                "adding_examples"
            ],
            "deprecation_rules": [
                "mark_deprecated_before_removal",
                "provide_migration_path",
                "minimum_deprecation_period"
            ]
        }

    async def validate_api_contract(self, spec_file: Union[str, Path],
                                  previous_version: Optional[Union[str, Path]] = None,
                                  validate_examples: bool = True) -> APIContractReport:
        """Validate API contract against OpenAPI specification"""
        start_time = time.time()
        self.logger.info(f"Starting API contract validation for {spec_file}")
        
        try:
            # Load and parse specification
            spec_data = await self._load_spec_file(spec_file)
            api_name = spec_data.get("info", {}).get("title", "Unknown API")
            api_version = spec_data.get("info", {}).get("version", "unknown")
            spec_version = spec_data.get("openapi", spec_data.get("swagger", "unknown"))
            
            # Validate OpenAPI specification format
            spec_validation_result = await self._validate_openapi_spec(spec_data)
            
            # Validate individual endpoints
            endpoint_validations = await self._validate_endpoints(spec_data, validate_examples)
            
            # Check backward compatibility if previous version provided
            contract_changes = []
            if previous_version:
                contract_changes = await self._check_backward_compatibility(spec_data, previous_version)
            
            # Calculate scores
            compatibility_score = self._calculate_compatibility_score(contract_changes)
            documentation_score = self._calculate_documentation_score(endpoint_validations)
            security_score = self._calculate_security_score(spec_data, endpoint_validations)
            
            # Aggregate results
            total_violations = sum(len(ev.violations) for ev in endpoint_validations)
            critical_violations = sum(
                len([v for v in ev.violations if v.severity == ViolationSeverity.CRITICAL])
                for ev in endpoint_validations
            )
            high_violations = sum(
                len([v for v in ev.violations if v.severity == ViolationSeverity.HIGH])
                for ev in endpoint_validations
            )
            
            overall_valid = (
                spec_validation_result and
                critical_violations == 0 and
                all(ev.is_valid for ev in endpoint_validations)
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                endpoint_validations, contract_changes, compatibility_score,
                documentation_score, security_score
            )
            
            report = APIContractReport(
                api_name=api_name,
                api_version=api_version,
                spec_version=spec_version,
                validation_timestamp=datetime.utcnow(),
                overall_valid=overall_valid,
                total_endpoints=len(endpoint_validations),
                valid_endpoints=len([ev for ev in endpoint_validations if ev.is_valid]),
                total_violations=total_violations,
                critical_violations=critical_violations,
                high_violations=high_violations,
                endpoint_validations=endpoint_validations,
                contract_changes=contract_changes,
                compatibility_score=compatibility_score,
                documentation_score=documentation_score,
                security_score=security_score,
                recommendations=recommendations,
                validation_time=time.time() - start_time
            )
            
            self.logger.info(
                f"API contract validation completed. "
                f"Valid: {overall_valid}, Violations: {total_violations}, "
                f"Score: {(compatibility_score + documentation_score + security_score) / 3:.1f}%"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"API contract validation failed: {e}")
            raise

    async def _load_spec_file(self, spec_file: Union[str, Path]) -> Dict[str, Any]:
        """Load OpenAPI specification file"""
        file_path = Path(spec_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Specification file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    # Try to detect format
                    content = f.read()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return yaml.safe_load(content)
                        
        except Exception as e:
            raise ValueError(f"Error parsing specification file {file_path}: {e}")

    async def _validate_openapi_spec(self, spec_data: Dict[str, Any]) -> bool:
        """Validate OpenAPI specification format"""
        if not HAS_OPENAPI_LIBS:
            self.logger.warning("OpenAPI validation libraries not available")
            return True
        
        try:
            # Validate using openapi-spec-validator
            validate_spec(spec_data)
            return True
            
        except OpenAPIValidationError as e:
            self.logger.error(f"OpenAPI specification validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error validating OpenAPI spec: {e}")
            return False

    async def _validate_endpoints(self, spec_data: Dict[str, Any],
                                validate_examples: bool = True) -> List[EndpointValidation]:
        """Validate individual API endpoints"""
        validations = []
        paths = spec_data.get("paths", {})
        
        for endpoint_path, methods in paths.items():
            for method, endpoint_spec in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                    validation = await self._validate_single_endpoint(
                        endpoint_path, method.upper(), endpoint_spec, spec_data, validate_examples
                    )
                    validations.append(validation)
        
        return validations

    async def _validate_single_endpoint(self, endpoint: str, method: str,
                                      endpoint_spec: Dict[str, Any],
                                      full_spec: Dict[str, Any],
                                      validate_examples: bool) -> EndpointValidation:
        """Validate a single API endpoint"""
        violations = []
        
        # Check required fields
        violations.extend(self._check_required_endpoint_fields(endpoint, method, endpoint_spec))
        
        # Check naming conventions
        violations.extend(self._check_naming_conventions(endpoint, method, endpoint_spec))
        
        # Check parameter definitions
        violations.extend(self._check_parameter_definitions(endpoint, method, endpoint_spec))
        
        # Check response definitions
        violations.extend(self._check_response_definitions(endpoint, method, endpoint_spec))
        
        # Check security definitions
        violations.extend(self._check_security_definitions(endpoint, method, endpoint_spec, full_spec))
        
        # Check documentation completeness
        violations.extend(self._check_documentation_completeness(endpoint, method, endpoint_spec))
        
        # Validate examples if requested
        if validate_examples:
            violations.extend(await self._validate_examples(endpoint, method, endpoint_spec))
        
        # Check performance considerations
        performance_considerations = self._check_performance_considerations(endpoint, method, endpoint_spec)
        
        # Determine overall validity
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        is_valid = len(critical_violations) == 0
        
        return EndpointValidation(
            endpoint=endpoint,
            method=method,
            is_valid=is_valid,
            violations=violations,
            schema_valid=len([v for v in violations if v.violation_type == ContractValidationType.SCHEMA_VALIDATION]) == 0,
            response_examples_valid=len([v for v in violations if v.violation_type == ContractValidationType.RESPONSE_FORMAT]) == 0,
            security_properly_defined=len([v for v in violations if v.violation_type == ContractValidationType.SECURITY_SCHEMES]) == 0,
            documentation_complete=len([v for v in violations if v.violation_type == ContractValidationType.DOCUMENTATION_COMPLETENESS]) == 0,
            performance_considerations=performance_considerations
        )

    def _check_required_endpoint_fields(self, endpoint: str, method: str,
                                      endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check if endpoint has required fields"""
        violations = []
        
        # Check for description
        if not endpoint_spec.get("description") and not endpoint_spec.get("summary"):
            violations.append(ContractViolation(
                violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                severity=ViolationSeverity.MEDIUM,
                message="Endpoint missing description or summary",
                endpoint=endpoint,
                method=method,
                suggestion="Add a description or summary to explain the endpoint's purpose"
            ))
        
        # Check for responses
        if "responses" not in endpoint_spec:
            violations.append(ContractViolation(
                violation_type=ContractValidationType.SCHEMA_VALIDATION,
                severity=ViolationSeverity.CRITICAL,
                message="Endpoint missing responses definition",
                endpoint=endpoint,
                method=method,
                suggestion="Define at least success and error responses"
            ))
        
        # Check for required response codes
        responses = endpoint_spec.get("responses", {})
        required_responses = self.validation_rules["required_fields"]["paths"]["required_responses"]
        
        # At least one success response (2xx)
        success_responses = [code for code in responses.keys() if code.startswith('2')]
        if not success_responses:
            violations.append(ContractViolation(
                violation_type=ContractValidationType.RESPONSE_FORMAT,
                severity=ViolationSeverity.HIGH,
                message="Endpoint missing success response (2xx)",
                endpoint=endpoint,
                method=method,
                suggestion="Define at least one success response (e.g., 200, 201)"
            ))
        
        return violations

    def _check_naming_conventions(self, endpoint: str, method: str,
                                endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check naming conventions"""
        violations = []
        
        # Check endpoint naming convention
        endpoint_pattern = self.validation_rules["naming_conventions"]["endpoints"]
        if not re.match(endpoint_pattern, endpoint):
            violations.append(ContractViolation(
                violation_type=ContractValidationType.ENDPOINT_CONSISTENCY,
                severity=ViolationSeverity.MEDIUM,
                message=f"Endpoint does not follow naming convention: {endpoint_pattern}",
                endpoint=endpoint,
                method=method,
                actual=endpoint,
                suggestion="Use lowercase, hyphens for separators, and version prefix (e.g., /api/v1/users)"
            ))
        
        # Check parameter naming
        parameters = endpoint_spec.get("parameters", [])
        param_pattern = self.validation_rules["naming_conventions"]["parameters"]
        
        for param in parameters:
            param_name = param.get("name", "")
            if not re.match(param_pattern, param_name):
                violations.append(ContractViolation(
                    violation_type=ContractValidationType.ENDPOINT_CONSISTENCY,
                    severity=ViolationSeverity.LOW,
                    message=f"Parameter name does not follow convention: {param_name}",
                    endpoint=endpoint,
                    method=method,
                    field_path=f"parameters.{param_name}",
                    actual=param_name,
                    suggestion="Use camelCase or snake_case consistently"
                ))
        
        return violations

    def _check_parameter_definitions(self, endpoint: str, method: str,
                                   endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check parameter definitions"""
        violations = []
        
        parameters = endpoint_spec.get("parameters", [])
        
        for param in parameters:
            param_name = param.get("name", "unknown")
            
            # Check required fields
            if "type" not in param and "schema" not in param:
                violations.append(ContractViolation(
                    violation_type=ContractValidationType.SCHEMA_VALIDATION,
                    severity=ViolationSeverity.HIGH,
                    message=f"Parameter '{param_name}' missing type definition",
                    endpoint=endpoint,
                    method=method,
                    field_path=f"parameters.{param_name}.type",
                    suggestion="Define parameter type (string, integer, boolean, etc.)"
                ))
            
            # Check description
            if not param.get("description"):
                violations.append(ContractViolation(
                    violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                    severity=ViolationSeverity.LOW,
                    message=f"Parameter '{param_name}' missing description",
                    endpoint=endpoint,
                    method=method,
                    field_path=f"parameters.{param_name}.description",
                    suggestion="Add description explaining the parameter's purpose and usage"
                ))
            
            # Check required vs optional
            if param.get("required") and param.get("in") == "query":
                violations.append(ContractViolation(
                    violation_type=ContractValidationType.ENDPOINT_CONSISTENCY,
                    severity=ViolationSeverity.MEDIUM,
                    message=f"Query parameter '{param_name}' should generally be optional",
                    endpoint=endpoint,
                    method=method,
                    field_path=f"parameters.{param_name}.required",
                    suggestion="Consider making query parameters optional with sensible defaults"
                ))
        
        return violations

    def _check_response_definitions(self, endpoint: str, method: str,
                                  endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check response definitions"""
        violations = []
        
        responses = endpoint_spec.get("responses", {})
        
        for status_code, response_spec in responses.items():
            # Check description
            if not response_spec.get("description"):
                violations.append(ContractViolation(
                    violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                    severity=ViolationSeverity.MEDIUM,
                    message=f"Response {status_code} missing description",
                    endpoint=endpoint,
                    method=method,
                    field_path=f"responses.{status_code}.description",
                    suggestion="Add description explaining when this response is returned"
                ))
            
            # Check schema for success responses
            if status_code.startswith('2') and "content" in response_spec:
                content = response_spec["content"]
                if "application/json" in content:
                    json_content = content["application/json"]
                    if "schema" not in json_content:
                        violations.append(ContractViolation(
                            violation_type=ContractValidationType.SCHEMA_VALIDATION,
                            severity=ViolationSeverity.HIGH,
                            message=f"Response {status_code} missing schema definition",
                            endpoint=endpoint,
                            method=method,
                            field_path=f"responses.{status_code}.content.application/json.schema",
                            suggestion="Define response schema to document the expected structure"
                        ))
        
        # Check for error responses
        error_responses = [code for code in responses.keys() if code.startswith('4') or code.startswith('5')]
        if not error_responses:
            violations.append(ContractViolation(
                violation_type=ContractValidationType.ERROR_HANDLING,
                severity=ViolationSeverity.MEDIUM,
                message="Endpoint missing error response definitions",
                endpoint=endpoint,
                method=method,
                suggestion="Define common error responses (400, 401, 403, 404, 500)"
            ))
        
        return violations

    def _check_security_definitions(self, endpoint: str, method: str,
                                  endpoint_spec: Dict[str, Any],
                                  full_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check security definitions"""
        violations = []
        
        # Check if security is defined
        security = endpoint_spec.get("security", full_spec.get("security", []))
        
        if not security and method.upper() not in ["GET", "HEAD", "OPTIONS"]:
            violations.append(ContractViolation(
                violation_type=ContractValidationType.SECURITY_SCHEMES,
                severity=ViolationSeverity.HIGH,
                message="Endpoint missing security requirements",
                endpoint=endpoint,
                method=method,
                suggestion="Define security requirements (authentication, authorization)"
            ))
        
        # Check if security schemes are properly defined
        security_schemes = full_spec.get("components", {}).get("securitySchemes", {})
        
        for security_requirement in security:
            for scheme_name in security_requirement.keys():
                if scheme_name not in security_schemes:
                    violations.append(ContractViolation(
                        violation_type=ContractValidationType.SECURITY_SCHEMES,
                        severity=ViolationSeverity.CRITICAL,
                        message=f"Security scheme '{scheme_name}' not defined in components",
                        endpoint=endpoint,
                        method=method,
                        field_path=f"security.{scheme_name}",
                        suggestion="Define the security scheme in components.securitySchemes"
                    ))
        
        return violations

    def _check_documentation_completeness(self, endpoint: str, method: str,
                                        endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Check documentation completeness"""
        violations = []
        
        # Check operation ID
        if not endpoint_spec.get("operationId"):
            violations.append(ContractViolation(
                violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                severity=ViolationSeverity.LOW,
                message="Endpoint missing operationId",
                endpoint=endpoint,
                method=method,
                suggestion="Add unique operationId for code generation and testing"
            ))
        
        # Check tags
        if not endpoint_spec.get("tags"):
            violations.append(ContractViolation(
                violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                severity=ViolationSeverity.LOW,
                message="Endpoint missing tags",
                endpoint=endpoint,
                method=method,
                suggestion="Add tags to group related endpoints in documentation"
            ))
        
        # Check examples in request body
        request_body = endpoint_spec.get("requestBody", {})
        if request_body and "content" in request_body:
            for media_type, content in request_body["content"].items():
                if "example" not in content and "examples" not in content:
                    violations.append(ContractViolation(
                        violation_type=ContractValidationType.DOCUMENTATION_COMPLETENESS,
                        severity=ViolationSeverity.LOW,
                        message=f"Request body missing example for {media_type}",
                        endpoint=endpoint,
                        method=method,
                        field_path=f"requestBody.content.{media_type}.example",
                        suggestion="Add example to help API consumers understand the expected format"
                    ))
        
        return violations

    async def _validate_examples(self, endpoint: str, method: str,
                               endpoint_spec: Dict[str, Any]) -> List[ContractViolation]:
        """Validate examples against schemas"""
        violations = []
        
        # This would validate examples against their schemas
        # For now, return empty list as it requires complex schema validation
        
        return violations

    def _check_performance_considerations(self, endpoint: str, method: str,
                                        endpoint_spec: Dict[str, Any]) -> List[str]:
        """Check for performance considerations"""
        considerations = []
        
        # Check for pagination in list endpoints
        if "get" in method.lower() and any(word in endpoint.lower() for word in ["list", "search", "all"]):
            parameters = endpoint_spec.get("parameters", [])
            has_pagination = any(
                param.get("name", "").lower() in ["limit", "offset", "page", "size"]
                for param in parameters
            )
            if not has_pagination:
                considerations.append("Consider adding pagination parameters for list endpoints")
        
        # Check for caching headers
        responses = endpoint_spec.get("responses", {})
        for status_code, response in responses.items():
            if status_code.startswith('2'):
                headers = response.get("headers", {})
                cache_headers = ["Cache-Control", "ETag", "Last-Modified"]
                if not any(header in headers for header in cache_headers):
                    considerations.append("Consider adding caching headers for better performance")
                break
        
        return considerations

    async def _check_backward_compatibility(self, current_spec: Dict[str, Any],
                                          previous_version: Union[str, Path]) -> List[ContractChange]:
        """Check backward compatibility with previous version"""
        changes = []
        
        try:
            # Load previous specification
            previous_spec = await self._load_spec_file(previous_version)
            
            # Compare endpoints
            changes.extend(self._compare_endpoints(previous_spec, current_spec))
            
            # Compare schemas
            changes.extend(self._compare_schemas(previous_spec, current_spec))
            
            # Compare security schemes
            changes.extend(self._compare_security_schemes(previous_spec, current_spec))
            
        except Exception as e:
            self.logger.error(f"Error checking backward compatibility: {e}")
        
        return changes

    def _compare_endpoints(self, old_spec: Dict[str, Any],
                         new_spec: Dict[str, Any]) -> List[ContractChange]:
        """Compare endpoints between versions"""
        changes = []
        
        old_paths = old_spec.get("paths", {})
        new_paths = new_spec.get("paths", {})
        
        # Check for removed endpoints
        for endpoint in old_paths:
            if endpoint not in new_paths:
                changes.append(ContractChange(
                    change_type=ContractChangeType.REMOVAL,
                    severity=ViolationSeverity.CRITICAL,
                    endpoint=endpoint,
                    method="ALL",
                    change_description=f"Endpoint {endpoint} has been removed",
                    impact_assessment="Breaking change - existing clients will fail",
                    migration_guide="Update client code to use alternative endpoint"
                ))
            else:
                # Compare methods within endpoint
                old_methods = old_paths[endpoint]
                new_methods = new_paths[endpoint]
                
                for method in old_methods:
                    if method not in new_methods:
                        changes.append(ContractChange(
                            change_type=ContractChangeType.REMOVAL,
                            severity=ViolationSeverity.CRITICAL,
                            endpoint=endpoint,
                            method=method.upper(),
                            change_description=f"Method {method} removed from {endpoint}",
                            impact_assessment="Breaking change for clients using this method"
                        ))
        
        # Check for new endpoints (non-breaking)
        for endpoint in new_paths:
            if endpoint not in old_paths:
                changes.append(ContractChange(
                    change_type=ContractChangeType.ADDITION,
                    severity=ViolationSeverity.INFO,
                    endpoint=endpoint,
                    method="ALL",
                    change_description=f"New endpoint {endpoint} added",
                    impact_assessment="Non-breaking change - adds new functionality"
                ))
        
        return changes

    def _compare_schemas(self, old_spec: Dict[str, Any],
                       new_spec: Dict[str, Any]) -> List[ContractChange]:
        """Compare schemas between versions"""
        changes = []
        
        old_schemas = old_spec.get("components", {}).get("schemas", {})
        new_schemas = new_spec.get("components", {}).get("schemas", {})
        
        # Check for removed schemas
        for schema_name in old_schemas:
            if schema_name not in new_schemas:
                changes.append(ContractChange(
                    change_type=ContractChangeType.REMOVAL,
                    severity=ViolationSeverity.HIGH,
                    endpoint="N/A",
                    method="N/A",
                    change_description=f"Schema {schema_name} has been removed",
                    impact_assessment="Potentially breaking change if schema was referenced"
                ))
        
        # Check for schema modifications
        for schema_name in old_schemas:
            if schema_name in new_schemas:
                # This would require deep comparison of schema structures
                # For now, just flag as potential change
                pass
        
        return changes

    def _compare_security_schemes(self, old_spec: Dict[str, Any],
                                new_spec: Dict[str, Any]) -> List[ContractChange]:
        """Compare security schemes between versions"""
        changes = []
        
        old_security = old_spec.get("components", {}).get("securitySchemes", {})
        new_security = new_spec.get("components", {}).get("securitySchemes", {})
        
        # Check for removed security schemes
        for scheme_name in old_security:
            if scheme_name not in new_security:
                changes.append(ContractChange(
                    change_type=ContractChangeType.REMOVAL,
                    severity=ViolationSeverity.CRITICAL,
                    endpoint="N/A",
                    method="N/A",
                    change_description=f"Security scheme {scheme_name} has been removed",
                    impact_assessment="Breaking change - authentication will fail"
                ))
        
        return changes

    def _calculate_compatibility_score(self, changes: List[ContractChange]) -> float:
        """Calculate backward compatibility score"""
        if not changes:
            return 100.0
        
        # Weight penalties by severity
        penalty_weights = {
            ViolationSeverity.CRITICAL: 20,
            ViolationSeverity.HIGH: 10,
            ViolationSeverity.MEDIUM: 5,
            ViolationSeverity.LOW: 2,
            ViolationSeverity.INFO: 0
        }
        
        total_penalty = sum(penalty_weights.get(change.severity, 0) for change in changes)
        
        # Cap at 0% minimum
        score = max(0, 100 - total_penalty)
        return score

    def _calculate_documentation_score(self, validations: List[EndpointValidation]) -> float:
        """Calculate documentation completeness score"""
        if not validations:
            return 100.0
        
        doc_violations = []
        for validation in validations:
            doc_violations.extend([
                v for v in validation.violations
                if v.violation_type == ContractValidationType.DOCUMENTATION_COMPLETENESS
            ])
        
        total_endpoints = len(validations)
        doc_penalty = len(doc_violations) * 2  # 2% penalty per missing doc item
        
        score = max(0, 100 - doc_penalty)
        return score

    def _calculate_security_score(self, spec_data: Dict[str, Any],
                                validations: List[EndpointValidation]) -> float:
        """Calculate security implementation score"""
        if not validations:
            return 100.0
        
        security_violations = []
        for validation in validations:
            security_violations.extend([
                v for v in validation.violations
                if v.violation_type == ContractValidationType.SECURITY_SCHEMES
            ])
        
        # Check global security configuration
        security_schemes = spec_data.get("components", {}).get("securitySchemes", {})
        has_auth = len(security_schemes) > 0
        
        # Calculate score
        violation_penalty = len(security_violations) * 5  # 5% penalty per security issue
        no_auth_penalty = 0 if has_auth else 30  # 30% penalty for no authentication
        
        score = max(0, 100 - violation_penalty - no_auth_penalty)
        return score

    def _generate_recommendations(self, validations: List[EndpointValidation],
                                changes: List[ContractChange],
                                compatibility_score: float,
                                documentation_score: float,
                                security_score: float) -> List[str]:
        """Generate recommendations for API improvement"""
        recommendations = []
        
        # Critical violations
        critical_violations = []
        for validation in validations:
            critical_violations.extend([
                v for v in validation.violations
                if v.severity == ViolationSeverity.CRITICAL
            ])
        
        if critical_violations:
            recommendations.append(f"Fix {len(critical_violations)} critical API contract violations immediately")
        
        # Compatibility issues
        breaking_changes = [c for c in changes if c.change_type == ContractChangeType.BREAKING_CHANGE]
        if breaking_changes:
            recommendations.append(f"Address {len(breaking_changes)} breaking changes to maintain compatibility")
        
        # Score-based recommendations
        if documentation_score < 80:
            recommendations.append("Improve API documentation - add descriptions, examples, and better parameter documentation")
        
        if security_score < 70:
            recommendations.append("Strengthen API security - implement proper authentication and authorization schemes")
        
        if compatibility_score < 90:
            recommendations.append("Review API changes for backward compatibility and provide migration guides")
        
        # Specific improvement suggestions
        missing_examples = sum(1 for v in validations if not v.response_examples_valid)
        if missing_examples > len(validations) * 0.3:
            recommendations.append("Add examples to API responses to improve developer experience")
        
        return recommendations

    def generate_report(self, report: APIContractReport, format: str = "markdown") -> str:
        """Generate API contract validation report"""
        if format == "json":
            return self._generate_json_report(report)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        elif format == "html":
            return self._generate_html_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self, report: APIContractReport) -> str:
        """Generate JSON report"""
        # Convert to serializable format
        data = {
            "api_name": report.api_name,
            "api_version": report.api_version,
            "validation_timestamp": report.validation_timestamp.isoformat(),
            "overall_valid": report.overall_valid,
            "summary": {
                "total_endpoints": report.total_endpoints,
                "valid_endpoints": report.valid_endpoints,
                "total_violations": report.total_violations,
                "critical_violations": report.critical_violations,
                "high_violations": report.high_violations
            },
            "scores": {
                "compatibility_score": report.compatibility_score,
                "documentation_score": report.documentation_score,
                "security_score": report.security_score
            },
            "contract_changes": [
                {
                    "type": change.change_type.value,
                    "severity": change.severity.value,
                    "endpoint": change.endpoint,
                    "method": change.method,
                    "description": change.change_description
                }
                for change in report.contract_changes[:10]
            ],
            "critical_violations": [
                {
                    "endpoint": v.endpoint,
                    "method": v.method,
                    "message": v.message,
                    "type": v.violation_type.value
                }
                for validation in report.endpoint_validations
                for v in validation.violations
                if v.severity == ViolationSeverity.CRITICAL
            ][:10],
            "recommendations": report.recommendations
        }
        
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, report: APIContractReport) -> str:
        """Generate Markdown report"""
        status_emoji = "✅" if report.overall_valid else "❌"
        
        md = f"""# API Contract Validation Report {status_emoji}

**API:** {report.api_name} v{report.api_version}  
**Generated:** {report.validation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Validation Time:** {report.validation_time:.2f}s

## Summary

| Metric | Value |
|--------|-------|
| Overall Valid | {'✅ Yes' if report.overall_valid else '❌ No'} |
| Total Endpoints | {report.total_endpoints} |
| Valid Endpoints | {report.valid_endpoints} |
| Total Violations | {report.total_violations} |
| Critical Violations | {report.critical_violations} |
| High Violations | {report.high_violations} |

## Quality Scores

| Score Type | Value | Status |
|------------|-------|--------|
| Compatibility | {report.compatibility_score:.1f}% | {'✅' if report.compatibility_score >= 90 else '⚠️' if report.compatibility_score >= 70 else '❌'} |
| Documentation | {report.documentation_score:.1f}% | {'✅' if report.documentation_score >= 80 else '⚠️' if report.documentation_score >= 60 else '❌'} |
| Security | {report.security_score:.1f}% | {'✅' if report.security_score >= 80 else '⚠️' if report.security_score >= 60 else '❌'} |

"""
        
        # Critical violations
        critical_violations = []
        for validation in report.endpoint_validations:
            critical_violations.extend([
                v for v in validation.violations
                if v.severity == ViolationSeverity.CRITICAL
            ])
        
        if critical_violations:
            md += "\n## 🔴 Critical Violations\n\n"
            for violation in critical_violations[:10]:
                md += f"- **{violation.endpoint} {violation.method}**: {violation.message}\n"
        
        # Contract changes
        if report.contract_changes:
            md += "\n## 📋 Contract Changes\n\n"
            for change in report.contract_changes[:10]:
                emoji = "🔴" if change.severity == ViolationSeverity.CRITICAL else "⚠️"
                md += f"- {emoji} **{change.endpoint} {change.method}**: {change.change_description}\n"
        
        # Recommendations
        if report.recommendations:
            md += "\n## 📝 Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

    def _generate_html_report(self, report: APIContractReport) -> str:
        """Generate HTML report"""
        status_color = "green" if report.overall_valid else "red"
        
        return f"""
        <html>
        <head><title>API Contract Report - {report.api_name}</title></head>
        <body>
        <h1 style="color: {status_color}">API Contract Report - {report.api_name}</h1>
        <p><strong>Version:</strong> {report.api_version}</p>
        <p><strong>Status:</strong> {'Valid' if report.overall_valid else 'Invalid'}</p>
        <p><strong>Critical Violations:</strong> {report.critical_violations}</p>
        </body>
        </html>
        """

# Global API contract validator instance
api_contract_validator = APIContractValidator()

__all__ = [
    "APIContractValidator",
    "ContractViolation",
    "ContractChange",
    "EndpointValidation",
    "APIContractReport",
    "ContractValidationType",
    "ViolationSeverity",
    "ContractChangeType",
    "api_contract_validator"
]