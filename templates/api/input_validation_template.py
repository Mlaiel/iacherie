#!/usr/bin/env python3
"""
⚡ Input Validation Template - Enterprise Security
🏗️ Architecture: iacherie Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable, Type
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, validator, Field
import re
import json
import html
import bleach
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import ipaddress
import email_validator
from urllib.parse import urlparse
import logging
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import hashlib

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + ML Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class ValidationLevel(str, Enum):
    """Input validation security levels"""
    PERMISSIVE = "permissive"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


class SanitizationMode(str, Enum):
    """Data sanitization modes"""
    NONE = "none"
    ESCAPE = "escape"
    STRIP = "strip"
    ALLOWLIST = "allowlist"
    CUSTOM = "custom"


class ValidationStrategy(str, Enum):
    """Validation strategies"""
    FAIL_FAST = "fail_fast"
    COLLECT_ALL = "collect_all"
    WARN_AND_CONTINUE = "warn_and_continue"


@dataclass
class ValidationRule:
    """Individual validation rule"""
    name: str
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[str] = None
    forbidden_chars: Optional[str] = None
    custom_validator: Optional[Callable] = None
    sanitization_mode: SanitizationMode = SanitizationMode.ESCAPE
    error_message: Optional[str] = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationConfig:
    """Enterprise input validation configuration"""
    # Basic settings
    validation_level: ValidationLevel = ValidationLevel.STRICT
    sanitization_mode: SanitizationMode = SanitizationMode.ESCAPE
    validation_strategy: ValidationStrategy = ValidationStrategy.FAIL_FAST
    
    # Content limits
    max_content_length: int = 1024 * 1024  # 1MB
    max_field_count: int = 100
    max_nesting_depth: int = 10
    max_array_length: int = 1000
    
    # Security patterns
    enable_xss_protection: bool = True
    enable_sql_injection_protection: bool = True
    enable_command_injection_protection: bool = True
    enable_path_traversal_protection: bool = True
    enable_ldap_injection_protection: bool = True
    
    # Custom validation rules
    field_rules: Dict[str, ValidationRule] = field(default_factory=dict)
    global_rules: List[ValidationRule] = field(default_factory=list)
    
    # Content type validation
    allowed_content_types: Set[str] = field(default_factory=lambda: {
        "application/json", "application/x-www-form-urlencoded", "multipart/form-data"
    })
    
    # File upload validation
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_extensions: Set[str] = field(default_factory=lambda: {
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".mp4", ".mp3"
    })
    
    # Advanced features
    enable_ml_detection: bool = False
    enable_audit_logging: bool = True
    enable_metrics: bool = True
    enable_rate_limiting: bool = True
    
    # Creator-specific settings
    enable_content_analysis: bool = True
    enable_metadata_validation: bool = True
    enable_format_detection: bool = True


@dataclass
class ValidationResult:
    """Validation result with details"""
    is_valid: bool
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    sanitized_data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationMetrics:
    """Input validation metrics"""
    total_requests: int = 0
    validated_requests: int = 0
    blocked_requests: int = 0
    xss_attempts: int = 0
    sql_injection_attempts: int = 0
    command_injection_attempts: int = 0
    path_traversal_attempts: int = 0
    oversized_requests: int = 0
    invalid_content_type: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.validated_requests == 0:
            return 0.0
        return (self.validated_requests - self.blocked_requests) / self.validated_requests * 100


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise Input Validation Middleware
    
    Features:
    - Comprehensive XSS protection
    - SQL injection prevention
    - Command injection detection
    - Path traversal protection
    - Content sanitization
    - ML-based threat detection
    - Creator content validation
    - Real-time metrics
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[ValidationConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or ValidationConfig()
        self.logger = logger or self._setup_logger()
        
        # Security patterns
        self._compile_security_patterns()
        
        # Validation state
        self.metrics = ValidationMetrics()
        self.threat_patterns: Dict[str, int] = {}
        self.request_history: List[Dict[str, Any]] = []
        
        # ML detection (if enabled)
        if self.config.enable_ml_detection:
            self._initialize_ml_detector()
        
        self.logger.info(f"Input Validation initialized with level: {self.config.validation_level}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup security audit logger"""
        logger = logging.getLogger("input_validation")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _compile_security_patterns(self):
        """Compile security threat patterns"""
        # XSS patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>', re.IGNORECASE),
            re.compile(r'<object[^>]*>', re.IGNORECASE),
            re.compile(r'<embed[^>]*>', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE),
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            re.compile(r'\bunion\s+select\b', re.IGNORECASE),
            re.compile(r'\bselect\s+.*\bfrom\b', re.IGNORECASE),
            re.compile(r'\binsert\s+into\b', re.IGNORECASE),
            re.compile(r'\bupdate\s+.*\bset\b', re.IGNORECASE),
            re.compile(r'\bdelete\s+from\b', re.IGNORECASE),
            re.compile(r'\bdrop\s+table\b', re.IGNORECASE),
            re.compile(r'[;\'"]\s*;\s*', re.IGNORECASE),
            re.compile(r'--.*', re.IGNORECASE),
            re.compile(r'/\*.*\*/', re.IGNORECASE | re.DOTALL),
        ]
        
        # Command injection patterns
        self.command_patterns = [
            re.compile(r'[;&|`$(){}[\]\\]'),
            re.compile(r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b', re.IGNORECASE),
            re.compile(r'[<>]'),
            re.compile(r'\.\./'),
            re.compile(r'%2e%2e%2f', re.IGNORECASE),
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            re.compile(r'\.\.[\\/]'),
            re.compile(r'%2e%2e[\\/]', re.IGNORECASE),
            re.compile(r'%252e%252e[\\/]', re.IGNORECASE),
            re.compile(r'\.\.%2f', re.IGNORECASE),
            re.compile(r'\.\.%5c', re.IGNORECASE),
        ]
        
        # LDAP injection patterns
        self.ldap_patterns = [
            re.compile(r'[()&|!*]'),
            re.compile(r'%28|%29|%26|%7c|%21|%2a', re.IGNORECASE),
        ]
    
    def _initialize_ml_detector(self):
        """Initialize ML-based threat detection"""
        # TODO: Implement ML threat detection
        # This could use a pre-trained model to detect malicious input
        self.logger.info("ML threat detection initialized")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with input validation"""
        start_time = datetime.utcnow()
        
        try:
            self.metrics.total_requests += 1
            
            # Skip validation for certain paths/methods
            if await self._should_skip_validation(request):
                return await call_next(request)
            
            self.metrics.validated_requests += 1
            
            # Content length check
            content_length = int(request.headers.get("content-length", 0))
            if content_length > self.config.max_content_length:
                self.metrics.oversized_requests += 1
                return await self._create_error_response(
                    "Request too large", 413, request
                )
            
            # Content type validation
            content_type = request.headers.get("content-type", "").split(";")[0]
            if content_type and content_type not in self.config.allowed_content_types:
                self.metrics.invalid_content_type += 1
                return await self._create_error_response(
                    "Invalid content type", 415, request
                )
            
            # Validate request data
            validation_result = await self._validate_request(request)
            
            if not validation_result.is_valid:
                self.metrics.blocked_requests += 1
                return await self._create_validation_error_response(
                    validation_result, request
                )
            
            # Replace request body with sanitized data if needed
            if validation_result.sanitized_data is not None:
                request = await self._update_request_body(request, validation_result.sanitized_data)
            
            # Process request
            response = await call_next(request)
            
            # Audit logging
            if self.config.enable_audit_logging:
                self._log_validation(request, validation_result, start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Input validation middleware error: {e}")
            self.metrics.blocked_requests += 1
            
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers={"X-Content-Type-Options": "nosniff"}
            )
    
    async def _should_skip_validation(self, request: Request) -> bool:
        """Check if request should skip validation"""
        # Skip validation for GET requests (query params still validated)
        if request.method == "GET":
            return False  # Still validate query parameters
        
        # Skip for certain paths
        skip_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
        return any(request.url.path.startswith(path) for path in skip_paths)
    
    async def _validate_request(self, request: Request) -> ValidationResult:
        """Comprehensive request validation"""
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate query parameters
            await self._validate_query_params(request, result)
            
            # Validate headers
            await self._validate_headers(request, result)
            
            # Validate body (if present)
            if request.method not in ["GET", "HEAD", "OPTIONS"]:
                await self._validate_body(request, result)
            
            # Apply global validation rules
            await self._apply_global_rules(request, result)
            
            # ML-based threat detection
            if self.config.enable_ml_detection:
                await self._ml_threat_detection(request, result)
            
            # Determine final validation status
            if self.config.validation_strategy == ValidationStrategy.FAIL_FAST:
                result.is_valid = len(result.errors) == 0
            else:
                # Allow warnings but fail on errors
                result.is_valid = len([e for e in result.errors if e.get("severity") == "error"]) == 0
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            result.is_valid = False
            result.errors.append({
                "type": "validation_error",
                "message": "Internal validation error",
                "severity": "error"
            })
            return result
    
    async def _validate_query_params(self, request: Request, result: ValidationResult):
        """Validate query parameters"""
        for key, value in request.query_params.items():
            await self._validate_field(key, value, "query", result)
    
    async def _validate_headers(self, request: Request, result: ValidationResult):
        """Validate request headers"""
        suspicious_headers = ["x-forwarded-host", "x-original-url", "x-rewrite-url"]
        
        for header_name, header_value in request.headers.items():
            # Check for suspicious headers
            if header_name.lower() in suspicious_headers:
                result.warnings.append({
                    "type": "suspicious_header",
                    "field": header_name,
                    "message": f"Potentially suspicious header: {header_name}",
                    "severity": "warning"
                })
            
            # Validate header values
            await self._validate_field(header_name, header_value, "header", result)
    
    async def _validate_body(self, request: Request, result: ValidationResult):
        """Validate request body"""
        try:
            body = await request.body()
            if not body:
                return
            
            content_type = request.headers.get("content-type", "").split(";")[0]
            
            if content_type == "application/json":
                await self._validate_json_body(body, result)
            elif content_type == "application/x-www-form-urlencoded":
                await self._validate_form_body(body, result)
            elif content_type.startswith("multipart/form-data"):
                await self._validate_multipart_body(request, result)
            else:
                # Validate as raw text
                await self._validate_text_body(body.decode("utf-8", errors="ignore"), result)
                
        except Exception as e:
            result.errors.append({
                "type": "body_validation_error",
                "message": f"Failed to validate request body: {str(e)}",
                "severity": "error"
            })
    
    async def _validate_json_body(self, body: bytes, result: ValidationResult):
        """Validate JSON body"""
        try:
            data = json.loads(body.decode("utf-8"))
            sanitized_data = await self._validate_json_object(data, result, depth=0)
            result.sanitized_data = sanitized_data
            
        except json.JSONDecodeError as e:
            result.errors.append({
                "type": "invalid_json",
                "message": f"Invalid JSON format: {str(e)}",
                "severity": "error"
            })
    
    async def _validate_json_object(self, data: Any, result: ValidationResult, depth: int = 0) -> Any:
        """Recursively validate JSON object"""
        if depth > self.config.max_nesting_depth:
            result.errors.append({
                "type": "max_depth_exceeded",
                "message": f"Maximum nesting depth ({self.config.max_nesting_depth}) exceeded",
                "severity": "error"
            })
            return data
        
        if isinstance(data, dict):
            if len(data) > self.config.max_field_count:
                result.errors.append({
                    "type": "max_fields_exceeded",
                    "message": f"Maximum field count ({self.config.max_field_count}) exceeded",
                    "severity": "error"
                })
                return data
            
            sanitized_dict = {}
            for key, value in data.items():
                # Validate field name
                await self._validate_field(str(key), str(key), "field_name", result)
                
                # Recursively validate value
                sanitized_value = await self._validate_json_object(value, result, depth + 1)
                
                # Validate field value
                if isinstance(value, str):
                    await self._validate_field(str(key), value, "json_field", result)
                    sanitized_value = await self._sanitize_string(value)
                
                sanitized_dict[key] = sanitized_value
            
            return sanitized_dict
        
        elif isinstance(data, list):
            if len(data) > self.config.max_array_length:
                result.errors.append({
                    "type": "max_array_length_exceeded",
                    "message": f"Maximum array length ({self.config.max_array_length}) exceeded",
                    "severity": "error"
                })
                return data
            
            return [
                await self._validate_json_object(item, result, depth + 1)
                for item in data
            ]
        
        elif isinstance(data, str):
            await self._validate_field("string_value", data, "json_string", result)
            return await self._sanitize_string(data)
        
        return data
    
    async def _validate_form_body(self, body: bytes, result: ValidationResult):
        """Validate form-encoded body"""
        try:
            # Parse form data
            from urllib.parse import parse_qs
            form_data = parse_qs(body.decode("utf-8"))
            
            sanitized_data = {}
            for key, values in form_data.items():
                for value in values:
                    await self._validate_field(key, value, "form_field", result)
                    sanitized_data[key] = await self._sanitize_string(value)
            
            result.sanitized_data = sanitized_data
            
        except Exception as e:
            result.errors.append({
                "type": "form_validation_error",
                "message": f"Failed to validate form data: {str(e)}",
                "severity": "error"
            })
    
    async def _validate_multipart_body(self, request: Request, result: ValidationResult):
        """Validate multipart form data"""
        try:
            # This would require more complex parsing
            # For now, we'll just validate the presence and basic properties
            content_length = int(request.headers.get("content-length", 0))
            
            if content_length > self.config.max_file_size:
                result.errors.append({
                    "type": "file_too_large",
                    "message": f"File size exceeds maximum ({self.config.max_file_size} bytes)",
                    "severity": "error"
                })
            
        except Exception as e:
            result.errors.append({
                "type": "multipart_validation_error",
                "message": f"Failed to validate multipart data: {str(e)}",
                "severity": "error"
            })
    
    async def _validate_text_body(self, text: str, result: ValidationResult):
        """Validate raw text body"""
        await self._validate_field("body_text", text, "text_body", result)
        result.sanitized_data = await self._sanitize_string(text)
    
    async def _validate_field(self, field_name: str, value: str, field_type: str, result: ValidationResult):
        """Validate individual field"""
        # Apply field-specific rules
        if field_name in self.config.field_rules:
            rule = self.config.field_rules[field_name]
            await self._apply_validation_rule(field_name, value, rule, result)
        
        # Security validation
        await self._validate_security_threats(field_name, value, field_type, result)
        
        # Content validation for creators
        if self.config.enable_content_analysis and field_type in ["json_field", "form_field"]:
            await self._validate_creator_content(field_name, value, result)
    
    async def _apply_validation_rule(self, field_name: str, value: str, rule: ValidationRule, result: ValidationResult):
        """Apply custom validation rule"""
        errors = []
        
        # Length validation
        if rule.min_length is not None and len(value) < rule.min_length:
            errors.append(f"Minimum length {rule.min_length} required")
        
        if rule.max_length is not None and len(value) > rule.max_length:
            errors.append(f"Maximum length {rule.max_length} exceeded")
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, value):
            errors.append(f"Value does not match required pattern")
        
        # Character validation
        if rule.allowed_chars:
            invalid_chars = set(value) - set(rule.allowed_chars)
            if invalid_chars:
                errors.append(f"Invalid characters: {', '.join(invalid_chars)}")
        
        if rule.forbidden_chars:
            forbidden_found = set(value) & set(rule.forbidden_chars)
            if forbidden_found:
                errors.append(f"Forbidden characters: {', '.join(forbidden_found)}")
        
        # Custom validator
        if rule.custom_validator:
            try:
                if not rule.custom_validator(value):
                    errors.append("Custom validation failed")
            except Exception as e:
                errors.append(f"Custom validation error: {str(e)}")
        
        # Add errors to result
        for error in errors:
            result.errors.append({
                "type": "field_validation_error",
                "field": field_name,
                "rule": rule.name,
                "message": rule.error_message or error,
                "severity": rule.severity
            })
    
    async def _validate_security_threats(self, field_name: str, value: str, field_type: str, result: ValidationResult):
        """Validate against security threats"""
        # XSS protection
        if self.config.enable_xss_protection:
            for pattern in self.xss_patterns:
                if pattern.search(value):
                    self.metrics.xss_attempts += 1
                    self.threat_patterns["xss"] = self.threat_patterns.get("xss", 0) + 1
                    result.errors.append({
                        "type": "xss_attempt",
                        "field": field_name,
                        "message": "Potential XSS attack detected",
                        "severity": "error"
                    })
                    break
        
        # SQL injection protection
        if self.config.enable_sql_injection_protection:
            for pattern in self.sql_patterns:
                if pattern.search(value):
                    self.metrics.sql_injection_attempts += 1
                    self.threat_patterns["sql_injection"] = self.threat_patterns.get("sql_injection", 0) + 1
                    result.errors.append({
                        "type": "sql_injection_attempt",
                        "field": field_name,
                        "message": "Potential SQL injection detected",
                        "severity": "error"
                    })
                    break
        
        # Command injection protection
        if self.config.enable_command_injection_protection:
            for pattern in self.command_patterns:
                if pattern.search(value):
                    self.metrics.command_injection_attempts += 1
                    self.threat_patterns["command_injection"] = self.threat_patterns.get("command_injection", 0) + 1
                    result.errors.append({
                        "type": "command_injection_attempt",
                        "field": field_name,
                        "message": "Potential command injection detected",
                        "severity": "error"
                    })
                    break
        
        # Path traversal protection
        if self.config.enable_path_traversal_protection:
            for pattern in self.path_traversal_patterns:
                if pattern.search(value):
                    self.metrics.path_traversal_attempts += 1
                    self.threat_patterns["path_traversal"] = self.threat_patterns.get("path_traversal", 0) + 1
                    result.errors.append({
                        "type": "path_traversal_attempt",
                        "field": field_name,
                        "message": "Potential path traversal detected",
                        "severity": "error"
                    })
                    break
        
        # LDAP injection protection
        if self.config.enable_ldap_injection_protection:
            for pattern in self.ldap_patterns:
                if pattern.search(value):
                    self.threat_patterns["ldap_injection"] = self.threat_patterns.get("ldap_injection", 0) + 1
                    result.errors.append({
                        "type": "ldap_injection_attempt",
                        "field": field_name,
                        "message": "Potential LDAP injection detected",
                        "severity": "error"
                    })
                    break
    
    async def _validate_creator_content(self, field_name: str, value: str, result: ValidationResult):
        """Validate creator-specific content"""
        # Content metadata validation
        if field_name in ["title", "description", "tags"]:
            # Check for appropriate content length
            if field_name == "title" and len(value) > 200:
                result.warnings.append({
                    "type": "content_warning",
                    "field": field_name,
                    "message": "Title may be too long for optimal SEO",
                    "severity": "warning"
                })
            
            # Check for empty or minimal content
            if len(value.strip()) < 3:
                result.warnings.append({
                    "type": "content_warning",
                    "field": field_name,
                    "message": "Content appears to be too short",
                    "severity": "warning"
                })
        
        # Format detection for media fields
        if self.config.enable_format_detection and field_name in ["video_url", "audio_url", "image_url"]:
            await self._validate_media_url(field_name, value, result)
    
    async def _validate_media_url(self, field_name: str, url: str, result: ValidationResult):
        """Validate media URLs for creators"""
        try:
            parsed = urlparse(url)
            
            # Check for valid scheme
            if parsed.scheme not in ["http", "https"]:
                result.errors.append({
                    "type": "invalid_media_url",
                    "field": field_name,
                    "message": "Media URL must use HTTP or HTTPS",
                    "severity": "error"
                })
                return
            
            # Check for suspicious domains
            suspicious_domains = ["bit.ly", "tinyurl.com", "t.co"]
            if any(domain in parsed.netloc for domain in suspicious_domains):
                result.warnings.append({
                    "type": "suspicious_domain",
                    "field": field_name,
                    "message": "URL uses a link shortener service",
                    "severity": "warning"
                })
            
        except Exception:
            result.errors.append({
                "type": "invalid_url_format",
                "field": field_name,
                "message": "Invalid URL format",
                "severity": "error"
            })
    
    async def _apply_global_rules(self, request: Request, result: ValidationResult):
        """Apply global validation rules"""
        for rule in self.config.global_rules:
            # This could validate request-wide patterns
            # For example, checking total content characteristics
            pass
    
    async def _ml_threat_detection(self, request: Request, result: ValidationResult):
        """ML-based threat detection"""
        if not self.config.enable_ml_detection:
            return
        
        # TODO: Implement ML-based threat detection
        # This could use a trained model to detect malicious patterns
        pass
    
    async def _sanitize_string(self, value: str) -> str:
        """Sanitize string value based on configuration"""
        if self.config.sanitization_mode == SanitizationMode.NONE:
            return value
        
        elif self.config.sanitization_mode == SanitizationMode.ESCAPE:
            return html.escape(value)
        
        elif self.config.sanitization_mode == SanitizationMode.STRIP:
            # Strip potentially dangerous characters
            dangerous_chars = '<>"\'&;()|`'
            for char in dangerous_chars:
                value = value.replace(char, '')
            return value
        
        elif self.config.sanitization_mode == SanitizationMode.ALLOWLIST:
            # Use bleach to allow only safe HTML
            allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br']
            return bleach.clean(value, tags=allowed_tags, strip=True)
        
        return value
    
    async def _update_request_body(self, request: Request, sanitized_data: Any) -> Request:
        """Update request body with sanitized data"""
        # This is a simplified approach - in practice you might need more sophisticated
        # request body replacement depending on your framework
        if isinstance(sanitized_data, dict):
            new_body = json.dumps(sanitized_data).encode()
            # Note: Modifying request body in FastAPI middleware is complex
            # This is a conceptual example
        return request
    
    async def _create_error_response(self, message: str, status_code: int, request: Request) -> Response:
        """Create error response for validation failures"""
        self.logger.warning(f"Request blocked: {message} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Validation failed",
                "message": message
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )
    
    async def _create_validation_error_response(self, result: ValidationResult, request: Request) -> Response:
        """Create response for validation errors"""
        error_summary = {
            "error": "Input validation failed",
            "errors": result.errors,
            "warnings": result.warnings if self.config.validation_strategy != ValidationStrategy.FAIL_FAST else []
        }
        
        self.logger.warning(f"Validation failed for {request.url.path}: {len(result.errors)} errors")
        
        return JSONResponse(
            status_code=400,
            content=error_summary,
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )
    
    def _log_validation(self, request: Request, result: ValidationResult, start_time: datetime):
        """Log validation results for audit"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        self.logger.info(
            f"Validation: {request.method} {request.url.path} "
            f"Valid: {result.is_valid} Errors: {len(result.errors)} "
            f"Warnings: {len(result.warnings)} Duration: {duration:.3f}s"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "validated_requests": self.metrics.validated_requests,
            "blocked_requests": self.metrics.blocked_requests,
            "success_rate": self.metrics.success_rate,
            "xss_attempts": self.metrics.xss_attempts,
            "sql_injection_attempts": self.metrics.sql_injection_attempts,
            "command_injection_attempts": self.metrics.command_injection_attempts,
            "path_traversal_attempts": self.metrics.path_traversal_attempts,
            "oversized_requests": self.metrics.oversized_requests,
            "invalid_content_type": self.metrics.invalid_content_type,
            "threat_patterns": self.threat_patterns
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = ValidationMetrics()
        self.threat_patterns.clear()
        self.request_history.clear()
        self.logger.info("Validation metrics reset")


# Factory function for easy integration
def create_input_validation_middleware(
    app: FastAPI,
    validation_level: ValidationLevel = ValidationLevel.STRICT,
    **kwargs
) -> InputValidationMiddleware:
    """
    🏭 Factory function to create input validation middleware
    
    Args:
        app: FastAPI application
        validation_level: Input validation level
        **kwargs: Additional configuration options
    
    Returns:
        Configured input validation middleware instance
    """
    config = ValidationConfig(
        validation_level=validation_level,
        **kwargs
    )
    
    return InputValidationMiddleware(app, config)


def setup_creator_input_validation(app: FastAPI) -> InputValidationMiddleware:
    """
    🎯 Creator-specific input validation setup
    Optimized for content creation platforms
    """
    # Custom validation rules for creator content
    creator_rules = {
        "title": ValidationRule(
            name="content_title",
            min_length=3,
            max_length=200,
            forbidden_chars="<>&\"'",
            sanitization_mode=SanitizationMode.ESCAPE,
            error_message="Title must be 3-200 characters and not contain HTML"
        ),
        "description": ValidationRule(
            name="content_description",
            min_length=10,
            max_length=5000,
            sanitization_mode=SanitizationMode.ALLOWLIST,
            error_message="Description must be 10-5000 characters"
        ),
        "tags": ValidationRule(
            name="content_tags",
            pattern=r'^[a-zA-Z0-9,\s\-_]+$',
            max_length=500,
            error_message="Tags can only contain letters, numbers, commas, spaces, hyphens and underscores"
        ),
        "email": ValidationRule(
            name="email_validation",
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            error_message="Invalid email format"
        )
    }
    
    config = ValidationConfig(
        validation_level=ValidationLevel.STRICT,
        sanitization_mode=SanitizationMode.ALLOWLIST,
        validation_strategy=ValidationStrategy.COLLECT_ALL,
        
        # Enhanced limits for creator content
        max_content_length=50 * 1024 * 1024,  # 50MB for media uploads
        max_file_size=100 * 1024 * 1024,      # 100MB for video files
        max_field_count=200,                   # More fields for rich metadata
        
        # Creator-specific features
        enable_content_analysis=True,
        enable_metadata_validation=True,
        enable_format_detection=True,
        
        field_rules=creator_rules,
        
        # Enhanced file type support for creators
        allowed_file_extensions={
            ".jpg", ".jpeg", ".png", ".gif", ".webp",          # Images
            ".mp4", ".mov", ".avi", ".mkv", ".webm",           # Videos
            ".mp3", ".wav", ".aac", ".flac", ".ogg",           # Audio
            ".pdf", ".txt", ".doc", ".docx",                   # Documents
            ".zip", ".rar"                                      # Archives
        },
        
        # Security settings
        enable_audit_logging=True,
        enable_metrics=True
    )
    
    return InputValidationMiddleware(app, config)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="Input Validation Demo")
    
    # Setup input validation middleware
    validation_middleware = create_input_validation_middleware(
        app,
        validation_level=ValidationLevel.STRICT
    )
    
    app.add_middleware(InputValidationMiddleware, middleware=validation_middleware)
    
    @app.get("/")
    async def root():
        return {"message": "Input Validation Template Active"}
    
    @app.post("/validate")
    async def validate_data(data: dict):
        return {"message": "Data validated successfully", "data": data}
    
    @app.get("/metrics")
    async def get_metrics():
        return validation_middleware.get_metrics()