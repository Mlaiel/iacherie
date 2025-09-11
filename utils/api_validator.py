"""
API Validator - Microservices Expert Implementation
=================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise API validation and testing utilities for microservices architecture.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """API validation result"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    timestamp: datetime


class APIValidator:
    """
    Enterprise API validation system implementing:
    - Request/response validation
    - Schema validation
    - Performance testing
    - Security validation
    - Microservices communication validation
    """
    
    def __init__(self):
        """Initialize API validator"""
        # Validation rules
        self.validation_rules = {
            'max_request_size': 10 * 1024 * 1024,  # 10MB
            'max_response_time': 5000,  # 5 seconds
            'required_headers': ['Content-Type', 'User-Agent'],
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
            'max_query_params': 50,
            'max_header_size': 8192  # 8KB
        }
        
        # Schema definitions
        self.schemas = {}
        
        # Performance metrics
        self.performance_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'average_validation_time': 0.0
        }
        
        logger.info("APIValidator initialized with enterprise validation rules")
    
    def validate_request(self, request_data: Dict[str, Any], 
                        schema_name: str = None) -> ValidationResult:
        """Validate API request"""
        try:
            start_time = time.time()
            errors = []
            warnings = []
            
            # Basic structure validation
            if not isinstance(request_data, dict):
                errors.append({
                    'field': 'request',
                    'message': 'Request must be a dictionary',
                    'severity': ValidationSeverity.CRITICAL.value
                })
                return self._create_result(False, errors, warnings, start_time)
            
            # Validate HTTP method
            method = request_data.get('method', '').upper()
            if method not in self.validation_rules['allowed_methods']:
                errors.append({
                    'field': 'method',
                    'message': f'Invalid HTTP method: {method}',
                    'severity': ValidationSeverity.HIGH.value
                })
            
            # Validate headers
            headers = request_data.get('headers', {})
            self._validate_headers(headers, errors, warnings)
            
            # Validate URL and query parameters
            url = request_data.get('url', '')
            self._validate_url(url, errors, warnings)
            
            # Validate request body
            body = request_data.get('body')
            if body:
                self._validate_request_body(body, errors, warnings)
            
            # Schema validation if provided
            if schema_name and schema_name in self.schemas:
                schema_errors = self._validate_schema(request_data, self.schemas[schema_name])
                errors.extend(schema_errors)
            
            # Security validation
            security_issues = self._validate_security(request_data)
            errors.extend(security_issues)
            
            # Update statistics
            self._update_stats(len(errors) == 0, start_time)
            
            is_valid = len(errors) == 0
            return self._create_result(is_valid, errors, warnings, start_time)
            
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[{'field': 'validation', 'message': str(e), 'severity': 'critical'}],
                warnings=[],
                performance_metrics={},
                timestamp=datetime.now()
            )
    
    def validate_response(self, response_data: Dict[str, Any],
                         expected_schema: str = None) -> ValidationResult:
        """Validate API response"""
        try:
            start_time = time.time()
            errors = []
            warnings = []
            
            # Validate status code
            status_code = response_data.get('status_code')
            if not isinstance(status_code, int) or not (100 <= status_code <= 599):
                errors.append({
                    'field': 'status_code',
                    'message': 'Invalid HTTP status code',
                    'severity': ValidationSeverity.HIGH.value
                })
            
            # Validate response headers
            headers = response_data.get('headers', {})
            self._validate_response_headers(headers, errors, warnings)
            
            # Validate response body
            body = response_data.get('body')
            if body:
                self._validate_response_body(body, errors, warnings)
            
            # Validate response time
            response_time = response_data.get('response_time_ms', 0)
            if response_time > self.validation_rules['max_response_time']:
                warnings.append({
                    'field': 'response_time',
                    'message': f'Slow response time: {response_time}ms',
                    'severity': ValidationSeverity.MEDIUM.value
                })
            
            # Schema validation if provided
            if expected_schema and expected_schema in self.schemas:
                schema_errors = self._validate_response_schema(body, self.schemas[expected_schema])
                errors.extend(schema_errors)
            
            # Update statistics
            self._update_stats(len(errors) == 0, start_time)
            
            is_valid = len(errors) == 0
            return self._create_result(is_valid, errors, warnings, start_time)
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[{'field': 'validation', 'message': str(e), 'severity': 'critical'}],
                warnings=[],
                performance_metrics={},
                timestamp=datetime.now()
            )
    
    def _validate_headers(self, headers: Dict[str, str], errors: List, warnings: List):
        """Validate request headers"""
        # Check required headers
        for required_header in self.validation_rules['required_headers']:
            if required_header not in headers:
                warnings.append({
                    'field': 'headers',
                    'message': f'Missing recommended header: {required_header}',
                    'severity': ValidationSeverity.LOW.value
                })
        
        # Check header size
        total_header_size = sum(len(k) + len(str(v)) for k, v in headers.items())
        if total_header_size > self.validation_rules['max_header_size']:
            errors.append({
                'field': 'headers',
                'message': f'Headers too large: {total_header_size} bytes',
                'severity': ValidationSeverity.MEDIUM.value
            })
        
        # Validate specific headers
        content_type = headers.get('Content-Type', '')
        if content_type and not self._is_valid_content_type(content_type):
            warnings.append({
                'field': 'Content-Type',
                'message': 'Unusual content type',
                'severity': ValidationSeverity.LOW.value
            })
    
    def _validate_response_headers(self, headers: Dict[str, str], errors: List, warnings: List):
        """Validate response headers"""
        # Check for security headers
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']
        for security_header in security_headers:
            if security_header not in headers:
                warnings.append({
                    'field': 'headers',
                    'message': f'Missing security header: {security_header}',
                    'severity': ValidationSeverity.MEDIUM.value
                })
        
        # Check CORS headers if present
        if 'Access-Control-Allow-Origin' in headers:
            origin = headers['Access-Control-Allow-Origin']
            if origin == '*':
                warnings.append({
                    'field': 'CORS',
                    'message': 'Overly permissive CORS policy',
                    'severity': ValidationSeverity.MEDIUM.value
                })
    
    def _validate_url(self, url: str, errors: List, warnings: List):
        """Validate URL format and parameters"""
        if not url:
            errors.append({
                'field': 'url',
                'message': 'URL is required',
                'severity': ValidationSeverity.HIGH.value
            })
            return
        
        # Basic URL format validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            errors.append({
                'field': 'url',
                'message': 'Invalid URL format',
                'severity': ValidationSeverity.HIGH.value
            })
        
        # Check for HTTPS
        if url.startswith('http://') and not url.startswith('http://localhost'):
            warnings.append({
                'field': 'url',
                'message': 'Consider using HTTPS for security',
                'severity': ValidationSeverity.MEDIUM.value
            })
        
        # Check query parameter count
        if '?' in url:
            query_part = url.split('?')[1]
            param_count = len(query_part.split('&'))
            if param_count > self.validation_rules['max_query_params']:
                warnings.append({
                    'field': 'url',
                    'message': f'Many query parameters: {param_count}',
                    'severity': ValidationSeverity.LOW.value
                })
    
    def _validate_request_body(self, body: Any, errors: List, warnings: List):
        """Validate request body"""
        # Check body size
        if isinstance(body, (str, bytes)):
            body_size = len(body)
        else:
            body_size = len(json.dumps(body))
        
        if body_size > self.validation_rules['max_request_size']:
            errors.append({
                'field': 'body',
                'message': f'Request body too large: {body_size} bytes',
                'severity': ValidationSeverity.HIGH.value
            })
        
        # Validate JSON structure if applicable
        if isinstance(body, str):
            try:
                json.loads(body)
            except json.JSONDecodeError:
                errors.append({
                    'field': 'body',
                    'message': 'Invalid JSON format',
                    'severity': ValidationSeverity.HIGH.value
                })
    
    def _validate_response_body(self, body: Any, errors: List, warnings: List):
        """Validate response body"""
        if body is None:
            return
        
        # Check if response body is valid JSON when expected
        if isinstance(body, str):
            try:
                json.loads(body)
            except json.JSONDecodeError:
                warnings.append({
                    'field': 'body',
                    'message': 'Response body is not valid JSON',
                    'severity': ValidationSeverity.LOW.value
                })
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data against schema"""
        errors = []
        
        # Simple schema validation (in production, use jsonschema library)
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})
        
        for field in required_fields:
            if field not in data:
                errors.append({
                    'field': field,
                    'message': f'Required field missing: {field}',
                    'severity': ValidationSeverity.HIGH.value
                })
        
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                field_type = field_schema.get('type')
                
                if field_type and not self._check_type(value, field_type):
                    errors.append({
                        'field': field,
                        'message': f'Invalid type for {field}: expected {field_type}',
                        'severity': ValidationSeverity.MEDIUM.value
                    })
        
        return errors
    
    def _validate_response_schema(self, body: Any, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate response body against schema"""
        errors = []
        
        if not body:
            return errors
        
        # Parse JSON if string
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                errors.append({
                    'field': 'body',
                    'message': 'Response body is not valid JSON',
                    'severity': ValidationSeverity.HIGH.value
                })
                return errors
        
        # Validate against schema
        schema_errors = self._validate_schema(body, schema)
        return schema_errors
    
    def _validate_security(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate security aspects of the request"""
        errors = []
        
        # Check for potential injection attacks
        body = request_data.get('body', '')
        if isinstance(body, str):
            # SQL injection patterns
            sql_patterns = ['union select', 'drop table', '--', 'or 1=1']
            for pattern in sql_patterns:
                if pattern.lower() in body.lower():
                    errors.append({
                        'field': 'security',
                        'message': f'Potential SQL injection pattern detected: {pattern}',
                        'severity': ValidationSeverity.CRITICAL.value
                    })
            
            # XSS patterns
            xss_patterns = ['<script>', 'javascript:', 'onload=', 'onerror=']
            for pattern in xss_patterns:
                if pattern.lower() in body.lower():
                    errors.append({
                        'field': 'security',
                        'message': f'Potential XSS pattern detected: {pattern}',
                        'severity': ValidationSeverity.HIGH.value
                    })
        
        # Check for suspicious headers
        headers = request_data.get('headers', {})
        for header_name, header_value in headers.items():
            if isinstance(header_value, str) and len(header_value) > 1000:
                errors.append({
                    'field': 'security',
                    'message': f'Suspiciously long header value: {header_name}',
                    'severity': ValidationSeverity.MEDIUM.value
                })
        
        return errors
    
    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid"""
        valid_types = [
            'application/json', 'application/xml', 'text/plain', 'text/html',
            'application/x-www-form-urlencoded', 'multipart/form-data',
            'application/octet-stream', 'image/', 'video/', 'audio/'
        ]
        
        return any(content_type.startswith(vt) for vt in valid_types)
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, assume valid
    
    def _create_result(self, is_valid: bool, errors: List, warnings: List, 
                      start_time: float) -> ValidationResult:
        """Create validation result"""
        validation_time = (time.time() - start_time) * 1000  # milliseconds
        
        performance_metrics = {
            'validation_time_ms': validation_time,
            'errors_count': len(errors),
            'warnings_count': len(warnings)
        }
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            performance_metrics=performance_metrics,
            timestamp=datetime.now()
        )
    
    def _update_stats(self, is_valid: bool, start_time: float):
        """Update performance statistics"""
        validation_time = time.time() - start_time
        
        self.performance_stats['total_validations'] += 1
        if is_valid:
            self.performance_stats['passed_validations'] += 1
        else:
            self.performance_stats['failed_validations'] += 1
        
        # Update average validation time
        total_validations = self.performance_stats['total_validations']
        current_avg = self.performance_stats['average_validation_time']
        new_avg = (current_avg * (total_validations - 1) + validation_time) / total_validations
        self.performance_stats['average_validation_time'] = new_avg
    
    def register_schema(self, name: str, schema: Dict[str, Any]):
        """Register a validation schema"""
        self.schemas[name] = schema
        logger.info(f"Schema registered: {name}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get validation performance statistics"""
        stats = self.performance_stats.copy()
        
        if stats['total_validations'] > 0:
            stats['success_rate'] = (stats['passed_validations'] / stats['total_validations']) * 100
        else:
            stats['success_rate'] = 0.0
        
        stats['registered_schemas'] = len(self.schemas)
        
        return stats


# Global instance
api_validator = APIValidator()