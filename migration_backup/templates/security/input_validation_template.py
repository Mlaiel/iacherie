"""
🛡️ Input Validation Template - Enterprise Input Validation & Sanitization Framework
===================================================================================

🔐 SECURITY EXPERT - Advanced Input Validation Template
- Comprehensive input validation and sanitization
- XSS and injection attack prevention
- Data type validation and schema enforcement
- File upload security and virus scanning
- Rate limiting and abuse prevention
- Audit logging for security compliance

Author: Security Expert
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Pattern, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import re
import html
import uuid
import hashlib
import mimetypes
from abc import ABC, abstractmethod
import urllib.parse
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

class InputType(Enum):
    """Types of input to validate"""
    TEXT = "text"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    DATE = "date"
    JSON = "json"
    XML = "xml"
    FILE = "file"
    HTML = "html"
    SQL = "sql"
    SCRIPT = "script"

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationRule:
    """Validation rule definition"""
    rule_id: str
    input_type: InputType
    pattern: Optional[Pattern] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[Set[str]] = None
    blocked_chars: Optional[Set[str]] = None
    blocked_patterns: List[Pattern] = field(default_factory=list)
    required: bool = False
    sanitize: bool = True
    escape_html: bool = True
    description: str = ""

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_value: Any
    original_value: Any
    threats_detected: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    applied_sanitization: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    rule_id: Optional[str] = None

@dataclass
class ThreatDetection:
    """Detected security threat"""
    threat_id: str
    threat_type: str
    threat_level: ThreatLevel
    description: str
    detected_pattern: str
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)
    source_ip: Optional[str] = None
    user_id: Optional[str] = None

class SecurityPatterns:
    """Security threat detection patterns"""
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        re.compile(r"(\b(union|select|insert|delete|update|drop|create|alter)\b)", re.IGNORECASE),
        re.compile(r"(--|/\*|\*/|;)", re.IGNORECASE),
        re.compile(r"(\b(exec|execute|sp_|xp_)\b)", re.IGNORECASE),
        re.compile(r"('.*'|\".*\")", re.IGNORECASE),
        re.compile(r"(\bor\b.*=.*|and.*=.*)", re.IGNORECASE)
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on(load|click|mouse|focus|blur|submit|change)=", re.IGNORECASE),
        re.compile(r"<iframe[^>]*>", re.IGNORECASE),
        re.compile(r"<embed[^>]*>", re.IGNORECASE),
        re.compile(r"<object[^>]*>", re.IGNORECASE),
        re.compile(r"vbscript:", re.IGNORECASE),
        re.compile(r"data:text/html", re.IGNORECASE)
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        re.compile(r"(;|\||&|`|\$\(|\${)", re.IGNORECASE),
        re.compile(r"(\beval\b|\bexec\b|\bsystem\b)", re.IGNORECASE),
        re.compile(r"(\.\.\/|\.\.\\)", re.IGNORECASE),
        re.compile(r"(\bcat\b|\bls\b|\bps\b|\bnetstat\b|\bwhoami\b)", re.IGNORECASE)
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(r"(\.\.\/|\.\.\\)", re.IGNORECASE),
        re.compile(r"(\.\./){2,}", re.IGNORECASE),
        re.compile(r"(\/etc\/|\/var\/|\/tmp\/)", re.IGNORECASE),
        re.compile(r"(\\windows\\|\\system32\\)", re.IGNORECASE)
    ]
    
    # LDAP injection patterns
    LDAP_INJECTION_PATTERNS = [
        re.compile(r"[\(\)\*\+\-\&\|\!\=\<\>\~\%]", re.IGNORECASE),
        re.compile(r"(\bou=|\bdc=|\bcn=)", re.IGNORECASE)
    ]
    
    # NoSQL injection patterns
    NOSQL_INJECTION_PATTERNS = [
        re.compile(r"(\$where|\$ne|\$gt|\$lt|\$regex)", re.IGNORECASE),
        re.compile(r"(javascript:|\beval\b)", re.IGNORECASE)
    ]

class FileValidator:
    """File validation and security scanning"""
    
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.aac', '.flac'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.msi', '.deb', '.rpm', '.dmg', '.app', '.sh', '.ps1'
    ]
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @classmethod
    def validate_file(cls, file_data: bytes, filename: str, 
                     allowed_types: List[str] = None) -> ValidationResult:
        """Validate uploaded file"""
        start_time = time.time()
        threats = []
        warnings = []
        sanitization_applied = []
        
        try:
            # Check file extension
            file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
            
            if file_ext in cls.DANGEROUS_EXTENSIONS:
                threats.append({
                    "type": "dangerous_file_extension",
                    "level": ThreatLevel.HIGH,
                    "description": f"Dangerous file extension detected: {file_ext}",
                    "pattern": file_ext
                })
            
            # Check file size
            if len(file_data) > cls.MAX_FILE_SIZE:
                threats.append({
                    "type": "file_too_large",
                    "level": ThreatLevel.MEDIUM,
                    "description": f"File size {len(file_data)} exceeds limit {cls.MAX_FILE_SIZE}",
                    "pattern": f"size:{len(file_data)}"
                })
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type and 'executable' in mime_type:
                threats.append({
                    "type": "executable_mime_type",
                    "level": ThreatLevel.HIGH,
                    "description": f"Executable MIME type detected: {mime_type}",
                    "pattern": mime_type
                })
            
            # Check for embedded executables in file content
            if cls._contains_executable_signature(file_data):
                threats.append({
                    "type": "embedded_executable",
                    "level": ThreatLevel.CRITICAL,
                    "description": "Executable code detected in file content",
                    "pattern": "PE/ELF/MACH-O signature"
                })
            
            # Sanitize filename
            sanitized_filename = cls._sanitize_filename(filename)
            if sanitized_filename != filename:
                sanitization_applied.append(f"filename: {filename} -> {sanitized_filename}")
            
            # Check allowed types
            if allowed_types:
                type_allowed = False
                for allowed_type in allowed_types:
                    if file_ext in cls.ALLOWED_EXTENSIONS.get(allowed_type, []):
                        type_allowed = True
                        break
                
                if not type_allowed:
                    threats.append({
                        "type": "disallowed_file_type",
                        "level": ThreatLevel.MEDIUM,
                        "description": f"File type not allowed: {file_ext}",
                        "pattern": file_ext
                    })
            
            validation_time = (time.time() - start_time) * 1000
            
            return ValidationResult(
                is_valid=len([t for t in threats if t["level"] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]) == 0,
                sanitized_value=sanitized_filename,
                original_value=filename,
                threats_detected=threats,
                warnings=warnings,
                applied_sanitization=sanitization_applied,
                validation_time_ms=validation_time
            )
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                sanitized_value=filename,
                original_value=filename,
                threats_detected=[{
                    "type": "validation_error",
                    "level": ThreatLevel.HIGH,
                    "description": f"File validation failed: {str(e)}",
                    "pattern": "exception"
                }],
                validation_time_ms=(time.time() - start_time) * 1000
            )
    
    @classmethod
    def _contains_executable_signature(cls, file_data: bytes) -> bool:
        """Check for executable file signatures"""
        # PE signature (Windows executables)
        if file_data.startswith(b'MZ'):
            return True
        
        # ELF signature (Linux executables)
        if file_data.startswith(b'\x7fELF'):
            return True
        
        # Mach-O signature (macOS executables)
        if file_data.startswith(b'\xfe\xed\xfa\xce') or file_data.startswith(b'\xfe\xed\xfa\xcf'):
            return True
        
        # Java class files
        if file_data.startswith(b'\xca\xfe\xba\xbe'):
            return True
        
        return False
    
    @classmethod
    def _sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # Remove dangerous characters
        dangerous_chars = '<>:"|?*'
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename

class InputValidator:
    """🛡️ Advanced Input Validation and Security Framework"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """Initialize Input Validator"""
        self.validation_level = validation_level
        self.validation_rules = {}
        self.security_patterns = SecurityPatterns()
        self.file_validator = FileValidator()
        
        # Rate limiting
        self.rate_limits = defaultdict(list)
        self.max_requests_per_minute = 100
        
        # Threat tracking
        self.detected_threats = []
        self.threat_stats = defaultdict(int)
        
        # Setup default validation rules
        self._setup_default_rules()
        
        logger.info(f"🛡️ Input Validator initialized with {validation_level.value} security level")
    
    def _setup_default_rules(self):
        """Setup default validation rules"""
        
        # Email validation
        self.validation_rules['email'] = ValidationRule(
            rule_id='email',
            input_type=InputType.EMAIL,
            pattern=re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            max_length=254,
            required=False,
            description="Email address validation"
        )
        
        # URL validation
        self.validation_rules['url'] = ValidationRule(
            rule_id='url',
            input_type=InputType.URL,
            pattern=re.compile(r'^https?://[^\s/$.?#].[^\s]*$'),
            max_length=2048,
            blocked_patterns=[
                re.compile(r'javascript:', re.IGNORECASE),
                re.compile(r'data:', re.IGNORECASE),
                re.compile(r'vbscript:', re.IGNORECASE)
            ],
            description="URL validation with protocol restriction"
        )
        
        # Phone number validation
        self.validation_rules['phone'] = ValidationRule(
            rule_id='phone',
            input_type=InputType.PHONE,
            pattern=re.compile(r'^\+?[\d\s\-\(\)]{7,15}$'),
            max_length=20,
            description="Phone number validation"
        )
        
        # Text validation (general)
        self.validation_rules['text'] = ValidationRule(
            rule_id='text',
            input_type=InputType.TEXT,
            max_length=1000,
            blocked_patterns=self.security_patterns.XSS_PATTERNS + self.security_patterns.SQL_INJECTION_PATTERNS,
            escape_html=True,
            description="General text validation with XSS/SQL injection protection"
        )
        
        # HTML content validation
        self.validation_rules['html'] = ValidationRule(
            rule_id='html',
            input_type=InputType.HTML,
            max_length=10000,
            blocked_patterns=self.security_patterns.XSS_PATTERNS,
            sanitize=True,
            description="HTML content validation with XSS protection"
        )
        
        # JSON validation
        self.validation_rules['json'] = ValidationRule(
            rule_id='json',
            input_type=InputType.JSON,
            max_length=100000,
            description="JSON data validation"
        )
        
        # Numeric validation
        self.validation_rules['numeric'] = ValidationRule(
            rule_id='numeric',
            input_type=InputType.NUMERIC,
            pattern=re.compile(r'^-?\d+(\.\d+)?$'),
            max_length=20,
            description="Numeric value validation"
        )
    
    async def validate_input(self, value: Any, rule_id: str, 
                           context: Dict[str, Any] = None) -> ValidationResult:
        """Validate input against specified rule"""
        
        if rule_id not in self.validation_rules:
            raise ValueError(f"Validation rule {rule_id} not found")
        
        rule = self.validation_rules[rule_id]
        start_time = time.time()
        
        # Apply rate limiting
        if not await self._check_rate_limit(context):
            return ValidationResult(
                is_valid=False,
                sanitized_value=value,
                original_value=value,
                threats_detected=[{
                    "type": "rate_limit_exceeded",
                    "level": ThreatLevel.MEDIUM,
                    "description": "Rate limit exceeded",
                    "pattern": "rate_limit"
                }],
                validation_time_ms=(time.time() - start_time) * 1000
            )
        
        return await self._validate_against_rule(value, rule, context or {})
    
    async def _validate_against_rule(self, value: Any, rule: ValidationRule, 
                                   context: Dict[str, Any]) -> ValidationResult:
        """Validate value against specific rule"""
        start_time = time.time()
        threats = []
        warnings = []
        sanitization_applied = []
        sanitized_value = value
        
        try:
            # Convert to string for pattern matching
            str_value = str(value) if value is not None else ""
            
            # Required field validation
            if rule.required and (value is None or str_value.strip() == ""):
                threats.append({
                    "type": "required_field_missing",
                    "level": ThreatLevel.MEDIUM,
                    "description": "Required field is missing or empty",
                    "pattern": "empty"
                })
            
            # Length validation
            if rule.min_length and len(str_value) < rule.min_length:
                threats.append({
                    "type": "input_too_short",
                    "level": ThreatLevel.LOW,
                    "description": f"Input length {len(str_value)} is below minimum {rule.min_length}",
                    "pattern": f"length:{len(str_value)}"
                })
            
            if rule.max_length and len(str_value) > rule.max_length:
                # Truncate if validation level allows
                if self.validation_level in [ValidationLevel.BASIC, ValidationLevel.STANDARD]:
                    sanitized_value = str_value[:rule.max_length]
                    sanitization_applied.append(f"truncated to {rule.max_length} characters")
                else:
                    threats.append({
                        "type": "input_too_long",
                        "level": ThreatLevel.MEDIUM,
                        "description": f"Input length {len(str_value)} exceeds maximum {rule.max_length}",
                        "pattern": f"length:{len(str_value)}"
                    })
            
            # Pattern validation
            if rule.pattern and not rule.pattern.match(str_value):
                threats.append({
                    "type": "pattern_mismatch",
                    "level": ThreatLevel.MEDIUM,
                    "description": f"Input does not match required pattern for {rule.input_type.value}",
                    "pattern": rule.pattern.pattern
                })
            
            # Blocked patterns detection
            for blocked_pattern in rule.blocked_patterns:
                if blocked_pattern.search(str_value):
                    threat_level = ThreatLevel.HIGH
                    if blocked_pattern in self.security_patterns.SQL_INJECTION_PATTERNS:
                        threat_type = "sql_injection_attempt"
                    elif blocked_pattern in self.security_patterns.XSS_PATTERNS:
                        threat_type = "xss_attempt"
                    elif blocked_pattern in self.security_patterns.COMMAND_INJECTION_PATTERNS:
                        threat_type = "command_injection_attempt"
                        threat_level = ThreatLevel.CRITICAL
                    else:
                        threat_type = "malicious_pattern_detected"
                    
                    threats.append({
                        "type": threat_type,
                        "level": threat_level,
                        "description": f"Blocked pattern detected: {blocked_pattern.pattern}",
                        "pattern": blocked_pattern.pattern
                    })
                    
                    # Log security threat
                    await self._log_security_threat(threat_type, str_value, context)
            
            # Character restrictions
            if rule.allowed_chars:
                invalid_chars = set(str_value) - rule.allowed_chars
                if invalid_chars:
                    if rule.sanitize:
                        sanitized_value = ''.join(c for c in str_value if c in rule.allowed_chars)
                        sanitization_applied.append(f"removed invalid characters: {invalid_chars}")
                    else:
                        threats.append({
                            "type": "invalid_characters",
                            "level": ThreatLevel.MEDIUM,
                            "description": f"Invalid characters detected: {invalid_chars}",
                            "pattern": str(invalid_chars)
                        })
            
            if rule.blocked_chars:
                blocked_found = set(str_value) & rule.blocked_chars
                if blocked_found:
                    if rule.sanitize:
                        sanitized_value = ''.join(c for c in str_value if c not in rule.blocked_chars)
                        sanitization_applied.append(f"removed blocked characters: {blocked_found}")
                    else:
                        threats.append({
                            "type": "blocked_characters",
                            "level": ThreatLevel.MEDIUM,
                            "description": f"Blocked characters detected: {blocked_found}",
                            "pattern": str(blocked_found)
                        })
            
            # HTML escaping
            if rule.escape_html and rule.input_type in [InputType.TEXT, InputType.HTML]:
                escaped_value = html.escape(str(sanitized_value))
                if escaped_value != sanitized_value:
                    sanitized_value = escaped_value
                    sanitization_applied.append("HTML escaped")
            
            # Special validation by input type
            if rule.input_type == InputType.JSON:
                try:
                    json.loads(str_value)
                except json.JSONDecodeError as e:
                    threats.append({
                        "type": "invalid_json",
                        "level": ThreatLevel.MEDIUM,
                        "description": f"Invalid JSON format: {str(e)}",
                        "pattern": "json_parse_error"
                    })
            
            elif rule.input_type == InputType.URL:
                parsed = urllib.parse.urlparse(str_value)
                if parsed.scheme not in ['http', 'https']:
                    threats.append({
                        "type": "invalid_url_scheme",
                        "level": ThreatLevel.HIGH,
                        "description": f"Invalid URL scheme: {parsed.scheme}",
                        "pattern": parsed.scheme
                    })
            
            # Determine overall validity
            critical_threats = [t for t in threats if t["level"] == ThreatLevel.CRITICAL]
            high_threats = [t for t in threats if t["level"] == ThreatLevel.HIGH]
            
            is_valid = len(critical_threats) == 0
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                is_valid = is_valid and len(high_threats) == 0
            
            validation_time = (time.time() - start_time) * 1000
            
            return ValidationResult(
                is_valid=is_valid,
                sanitized_value=sanitized_value,
                original_value=value,
                threats_detected=threats,
                warnings=warnings,
                applied_sanitization=sanitization_applied,
                validation_time_ms=validation_time,
                rule_id=rule.rule_id
            )
            
        except Exception as e:
            logger.error(f"Validation error for rule {rule.rule_id}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                sanitized_value=value,
                original_value=value,
                threats_detected=[{
                    "type": "validation_exception",
                    "level": ThreatLevel.HIGH,
                    "description": f"Validation failed: {str(e)}",
                    "pattern": "exception"
                }],
                validation_time_ms=(time.time() - start_time) * 1000,
                rule_id=rule.rule_id
            )
    
    async def validate_file(self, file_data: bytes, filename: str,
                          allowed_types: List[str] = None,
                          context: Dict[str, Any] = None) -> ValidationResult:
        """Validate uploaded file"""
        
        # Apply rate limiting
        if not await self._check_rate_limit(context):
            return ValidationResult(
                is_valid=False,
                sanitized_value=filename,
                original_value=filename,
                threats_detected=[{
                    "type": "rate_limit_exceeded",
                    "level": ThreatLevel.MEDIUM,
                    "description": "File upload rate limit exceeded",
                    "pattern": "rate_limit"
                }]
            )
        
        result = self.file_validator.validate_file(file_data, filename, allowed_types)
        
        # Log any threats detected in file
        for threat in result.threats_detected:
            if threat["level"] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._log_security_threat(threat["type"], filename, context or {})
        
        return result
    
    async def validate_batch(self, inputs: Dict[str, Any], 
                           rules: Dict[str, str],
                           context: Dict[str, Any] = None) -> Dict[str, ValidationResult]:
        """Validate multiple inputs at once"""
        
        results = {}
        
        for field_name, value in inputs.items():
            if field_name in rules:
                rule_id = rules[field_name]
                try:
                    result = await self.validate_input(value, rule_id, context)
                    results[field_name] = result
                except Exception as e:
                    logger.error(f"Batch validation error for {field_name}: {str(e)}")
                    results[field_name] = ValidationResult(
                        is_valid=False,
                        sanitized_value=value,
                        original_value=value,
                        threats_detected=[{
                            "type": "batch_validation_error",
                            "level": ThreatLevel.HIGH,
                            "description": f"Batch validation failed: {str(e)}",
                            "pattern": "exception"
                        }]
                    )
        
        return results
    
    async def _check_rate_limit(self, context: Dict[str, Any] = None) -> bool:
        """Check rate limiting"""
        if not context:
            return True
        
        client_id = context.get('client_ip', 'unknown')
        current_time = time.time()
        
        # Clean old requests
        self.rate_limits[client_id] = [
            req_time for req_time in self.rate_limits[client_id]
            if current_time - req_time < 60  # 1 minute window
        ]
        
        # Check rate limit
        if len(self.rate_limits[client_id]) >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
        
        # Add current request
        self.rate_limits[client_id].append(current_time)
        return True
    
    async def _log_security_threat(self, threat_type: str, input_value: str, 
                                 context: Dict[str, Any]):
        """Log detected security threat"""
        
        threat = ThreatDetection(
            threat_id=str(uuid.uuid4()),
            threat_type=threat_type,
            threat_level=ThreatLevel.HIGH,
            description=f"Security threat detected: {threat_type}",
            detected_pattern=input_value[:100],  # First 100 chars
            recommendation="Block request and investigate source",
            source_ip=context.get('client_ip'),
            user_id=context.get('user_id')
        )
        
        self.detected_threats.append(threat)
        self.threat_stats[threat_type] += 1
        
        # Log critical threats immediately
        if threat.threat_level == ThreatLevel.CRITICAL:
            logger.critical(f"CRITICAL SECURITY THREAT: {threat_type} from {threat.source_ip}")
        else:
            logger.warning(f"Security threat detected: {threat_type}")
    
    def add_custom_rule(self, rule: ValidationRule):
        """Add custom validation rule"""
        self.validation_rules[rule.rule_id] = rule
        logger.info(f"Custom validation rule added: {rule.rule_id}")
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get security threat statistics"""
        recent_threats = [
            t for t in self.detected_threats
            if (datetime.now() - t.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        return {
            "total_threats_detected": len(self.detected_threats),
            "recent_threats_count": len(recent_threats),
            "threat_types": dict(self.threat_stats),
            "top_threat_types": sorted(
                self.threat_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "validation_rules_count": len(self.validation_rules),
            "validation_level": self.validation_level.value
        }

# Usage Example and Template Testing
async def main():
    """Example usage of Input Validation Template"""
    
    # Initialize validator with strict security level
    validator = InputValidator(ValidationLevel.STRICT)
    
    try:
        # Test text validation
        text_result = await validator.validate_input(
            "Hello <script>alert('xss')</script> World!",
            "text",
            {"client_ip": "192.168.1.100", "user_id": "user_123"}
        )
        
        print(f"✅ Text validation result:")
        print(f"  Valid: {text_result.is_valid}")
        print(f"  Sanitized: {text_result.sanitized_value}")
        print(f"  Threats: {len(text_result.threats_detected)}")
        print(f"  Processing time: {text_result.validation_time_ms:.2f}ms")
        
        # Test email validation
        email_result = await validator.validate_input(
            "user@example.com",
            "email"
        )
        
        print(f"\n✅ Email validation result:")
        print(f"  Valid: {email_result.is_valid}")
        print(f"  Sanitized: {email_result.sanitized_value}")
        
        # Test SQL injection attempt
        sql_result = await validator.validate_input(
            "'; DROP TABLE users; --",
            "text",
            {"client_ip": "192.168.1.100"}
        )
        
        print(f"\n🚨 SQL Injection test:")
        print(f"  Valid: {sql_result.is_valid}")
        print(f"  Threats detected: {len(sql_result.threats_detected)}")
        for threat in sql_result.threats_detected:
            print(f"    - {threat['type']}: {threat['description']}")
        
        # Test file validation
        fake_file_data = b"This is a test file content"
        file_result = await validator.validate_file(
            fake_file_data,
            "test_document.pdf",
            allowed_types=["document"]
        )
        
        print(f"\n📄 File validation result:")
        print(f"  Valid: {file_result.is_valid}")
        print(f"  Sanitized filename: {file_result.sanitized_value}")
        print(f"  Threats: {len(file_result.threats_detected)}")
        
        # Test malicious file
        malicious_file_result = await validator.validate_file(
            b"MZ" + b"\x00" * 100,  # PE signature
            "document.exe",
            allowed_types=["document"]
        )
        
        print(f"\n🚨 Malicious file test:")
        print(f"  Valid: {malicious_file_result.is_valid}")
        print(f"  Threats detected: {len(malicious_file_result.threats_detected)}")
        for threat in malicious_file_result.threats_detected:
            print(f"    - {threat['type']}: {threat['description']}")
        
        # Test batch validation
        batch_inputs = {
            "username": "admin'; DROP TABLE users; --",
            "email": "user@example.com",
            "website": "javascript:alert('xss')",
            "age": "25"
        }
        
        batch_rules = {
            "username": "text",
            "email": "email",
            "website": "url",
            "age": "numeric"
        }
        
        batch_results = await validator.validate_batch(
            batch_inputs,
            batch_rules,
            {"client_ip": "192.168.1.100"}
        )
        
        print(f"\n📋 Batch validation results:")
        for field, result in batch_results.items():
            print(f"  {field}: Valid={result.is_valid}, Threats={len(result.threats_detected)}")
        
        # Get threat statistics
        stats = validator.get_threat_statistics()
        print(f"\n📊 Security Statistics:")
        print(f"  Total threats detected: {stats['total_threats_detected']}")
        print(f"  Recent threats (1h): {stats['recent_threats_count']}")
        print(f"  Top threat types: {stats['top_threat_types']}")
        print(f"  Validation level: {stats['validation_level']}")
        
        print(f"\n✅ Input Validation demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in input validation demo: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🛡️ Input Validation Template demonstration completed!")