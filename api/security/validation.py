"""Advanced Input Validation and Security Protection System
Enterprise-grade validation against common web vulnerabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Security Expert + Web Security Specialist + Backend Senior
"""import re
import html
import json
import time
import hashlib
import secrets
import ipaddress
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from collections import defaultdict, deque
import asyncio
import aioredis
from urllib.parse import urlparse, parse_qs
import bleach
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation exception"""    pass


class SecurityThreat(Enum):
    """Security threat types"""    XSS = "xss"
    SQL_INJECTION = "sql_injection"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    XML_INJECTION = "xml_injection"
    XXE = "xxe"
    SSRF = "ssrf"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MALICIOUS_FILE = "malicious_file"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


class ValidationSeverity(Enum):
    """Validation error severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Validation result data structure"""    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_value: Any = None
    threat_type: Optional[SecurityThreat] = None
    severity: ValidationSeverity = ValidationSeverity.LOW
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""    max_requests: int
    time_window: int  # seconds
    block_duration: int = 300  # 5 minutes default
    identifier_func: Callable[[Dict], str] = lambda x: x.get('ip_address', 'unknown')


class BaseValidator(ABC):
    """Base validator interface"""    
    @abstractmethod
    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate input value"""        pass
    
    @abstractmethod
    def sanitize(self, value: Any, context: Dict[str, Any] = None) -> Any:
        """Sanitize input value"""        pass


class InputValidator:
    """Comprehensive input validation system"""    
    def __init__(self):
        self.validation_patterns = self._initialize_patterns()
        self.allowed_file_extensions = {
            'images': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'},
            'audio': {'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'},
            'video': {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'},
            'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'},
            'archives': {'zip', 'tar', 'gz', 'rar', '7z'}
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB default
        
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize validation regex patterns"""        return {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'phone': re.compile(r'^\+?[\d\s\-\(\)]{7,15}$'),
            'url': re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?$'),
            'username': re.compile(r'^[a-zA-Z0-9_]{3,30}$'),
            'password_strong': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'),
            'ip_address': re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I),
            'hex_color': re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'),
            'base64': re.compile(r'^[A-Za-z0-9+/]*={0,2}$'),
            'jwt_token': re.compile(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'),
        }
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000,
                       pattern: str = None, required: bool = True) -> ValidationResult:
        """Validate string input"""        
        if not value and required:
            return ValidationResult(
                is_valid=False,
                errors=['Value is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if not value and not required:
            return ValidationResult(is_valid=True, sanitized_value='')
        
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                errors=['Value must be a string'],
                severity=ValidationSeverity.MEDIUM
            )
        
        errors = []
        warnings = []
        
        # Length validation
        if len(value) < min_length:
            errors.append(f'Value must be at least {min_length} characters long')
        
        if len(value) > max_length:
            errors.append(f'Value must be at most {max_length} characters long')
        
        # Pattern validation
        if pattern and pattern in self.validation_patterns:
            if not self.validation_patterns[pattern].match(value):
                errors.append(f'Value does not match required pattern: {pattern}')
        
        # Sanitize for basic security
        sanitized_value = self._sanitize_string(value)
        
        if sanitized_value != value:
            warnings.append('Value was sanitized for security')
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_value=sanitized_value,
            severity=ValidationSeverity.MEDIUM if errors else ValidationSeverity.LOW
        )
    
    def validate_integer(self, value: Union[str, int], min_value: int = None,
                        max_value: int = None, required: bool = True) -> ValidationResult:
        """Validate integer input"""        
        if value is None and required:
            return ValidationResult(
                is_valid=False,
                errors=['Value is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if value is None and not required:
            return ValidationResult(is_valid=True, sanitized_value=None)
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                errors=['Value must be a valid integer'],
                severity=ValidationSeverity.MEDIUM
            )
        
        errors = []
        
        if min_value is not None and int_value < min_value:
            errors.append(f'Value must be at least {min_value}')
        
        if max_value is not None and int_value > max_value:
            errors.append(f'Value must be at most {max_value}')
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_value=int_value,
            severity=ValidationSeverity.MEDIUM if errors else ValidationSeverity.LOW
        )
    
    def validate_float(self, value: Union[str, float], min_value: float = None,
                      max_value: float = None, required: bool = True) -> ValidationResult:
        """Validate float input"""        
        if value is None and required:
            return ValidationResult(
                is_valid=False,
                errors=['Value is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if value is None and not required:
            return ValidationResult(is_valid=True, sanitized_value=None)
        
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                errors=['Value must be a valid number'],
                severity=ValidationSeverity.MEDIUM
            )
        
        errors = []
        
        if min_value is not None and float_value < min_value:
            errors.append(f'Value must be at least {min_value}')
        
        if max_value is not None and float_value > max_value:
            errors.append(f'Value must be at most {max_value}')
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            sanitized_value=float_value,
            severity=ValidationSeverity.MEDIUM if errors else ValidationSeverity.LOW
        )
    
    def validate_email(self, email: str, required: bool = True) -> ValidationResult:
        """Validate email address"""        
        if not email and required:
            return ValidationResult(
                is_valid=False,
                errors=['Email is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if not email and not required:
            return ValidationResult(is_valid=True, sanitized_value='')
        
        try:
            # Use email-validator library for comprehensive validation
            valid_email = validate_email(email)
            sanitized_email = valid_email.email
            
            return ValidationResult(
                is_valid=True,
                sanitized_value=sanitized_email,
                metadata={'normalized_email': sanitized_email}
            )
            
        except EmailNotValidError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f'Invalid email address: {str(e)}'],
                severity=ValidationSeverity.MEDIUM
            )
    
    def validate_password(self, password: str, min_length: int = 12,
                         require_complexity: bool = True) -> ValidationResult:
        """Validate password strength"""        
        if not password:
            return ValidationResult(
                is_valid=False,
                errors=['Password is required'],
                severity=ValidationSeverity.HIGH
            )
        
        errors = []
        warnings = []
        
        # Length check
        if len(password) < min_length:
            errors.append(f'Password must be at least {min_length} characters long')
        
        if require_complexity:
            complexity_checks = [
                (r'[a-z]', 'lowercase letter'),
                (r'[A-Z]', 'uppercase letter'),
                (r'\d', 'digit'),
                (r'[@$!%*?&]', 'special character')
            ]
            
            for pattern, description in complexity_checks:
                if not re.search(pattern, password):
                    errors.append(f'Password must contain at least one {description}')
        
        # Check for common weak patterns
        weak_patterns = [
            (r'(.)\1{2,}', 'contains repeated characters'),
            (r'123|abc|qwe', 'contains sequential characters'),
            (r'password|123456|qwerty', 'is too common')
        ]
        
        for pattern, description in weak_patterns:
            if re.search(pattern, password.lower()):
                warnings.append(f'Password {description}')
        
        # Calculate password strength score
        strength_score = self._calculate_password_strength(password)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_value=password,
            severity=ValidationSeverity.HIGH if errors else ValidationSeverity.LOW,
            metadata={'strength_score': strength_score}
        )
    
    def validate_url(self, url: str, allowed_schemes: List[str] = None,
                    required: bool = True) -> ValidationResult:
        """Validate URL"""        
        if not url and required:
            return ValidationResult(
                is_valid=False,
                errors=['URL is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if not url and not required:
            return ValidationResult(is_valid=True, sanitized_value='')
        
        if not allowed_schemes:
            allowed_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            
            errors = []
            
            if not parsed.scheme:
                errors.append('URL must include a scheme (http:// or https://)')
            elif parsed.scheme not in allowed_schemes:
                errors.append(f'URL scheme must be one of: {", ".join(allowed_schemes)}')
            
            if not parsed.netloc:
                errors.append('URL must include a domain name')
            
            # Check for suspicious patterns
            if self._contains_suspicious_url_patterns(url):
                return ValidationResult(
                    is_valid=False,
                    errors=['URL contains suspicious patterns'],
                    threat_type=SecurityThreat.SSRF,
                    severity=ValidationSeverity.HIGH
                )
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                sanitized_value=url,
                metadata={'parsed_url': parsed._asdict()}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f'Invalid URL format: {str(e)}'],
                severity=ValidationSeverity.MEDIUM
            )
    
    def validate_file_upload(self, filename: str, file_content: bytes,
                           allowed_types: List[str] = None) -> ValidationResult:
        """Validate file upload"""        
        if not filename:
            return ValidationResult(
                is_valid=False,
                errors=['Filename is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if not file_content:
            return ValidationResult(
                is_valid=False,
                errors=['File content is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        errors = []
        warnings = []
        
        # File size check
        if len(file_content) > self.max_file_size:
            errors.append(f'File size exceeds maximum allowed size of {self.max_file_size} bytes')
        
        # File extension check
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if allowed_types:
            allowed_extensions = set()
            for file_type in allowed_types:
                allowed_extensions.update(self.allowed_file_extensions.get(file_type, set()))
            
            if file_ext not in allowed_extensions:
                errors.append(f'File extension "{file_ext}" not allowed. Allowed types: {", ".join(allowed_extensions)}')
        
        # Magic number validation
        magic_number_result = self._validate_file_magic_number(file_content, file_ext)
        if not magic_number_result['is_valid']:
            errors.append(magic_number_result['error'])
        
        # Malware scan (simplified)
        malware_result = self._scan_for_malware(file_content, filename)
        if malware_result['is_suspicious']:
            return ValidationResult(
                is_valid=False,
                errors=['File appears to contain malicious content'],
                threat_type=SecurityThreat.MALICIOUS_FILE,
                severity=ValidationSeverity.CRITICAL
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_value={'filename': filename, 'size': len(file_content)},
            metadata={
                'file_extension': file_ext,
                'file_size': len(file_content),
                'magic_number': magic_number_result.get('magic_number')
            }
        )
    
    def validate_json(self, json_string: str, max_depth: int = 10,
                     max_size: int = 10000) -> ValidationResult:
        """Validate JSON input"""        
        if not json_string:
            return ValidationResult(
                is_valid=False,
                errors=['JSON string is required'],
                severity=ValidationSeverity.MEDIUM
            )
        
        if len(json_string) > max_size:
            return ValidationResult(
                is_valid=False,
                errors=[f'JSON string exceeds maximum size of {max_size} characters'],
                severity=ValidationSeverity.MEDIUM
            )
        
        try:
            parsed_json = json.loads(json_string)
            
            # Check JSON depth to prevent deeply nested attacks
            current_depth = self._calculate_json_depth(parsed_json)
            if current_depth > max_depth:
                return ValidationResult(
                    is_valid=False,
                    errors=[f'JSON depth exceeds maximum allowed depth of {max_depth}'],
                    severity=ValidationSeverity.HIGH
                )
            
            return ValidationResult(
                is_valid=True,
                sanitized_value=parsed_json,
                metadata={'json_depth': current_depth}
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f'Invalid JSON format: {str(e)}'],
                severity=ValidationSeverity.MEDIUM
            )
    
    def _sanitize_string(self, value: str) -> str:
        """Basic string sanitization"""        # HTML escape
        sanitized = html.escape(value)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        return sanitized.strip()
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""        score = 0
        
        # Length bonus
        score += min(len(password) * 2, 50)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(r'[@$!%*?&]', password):
            score += 10
        
        # Uniqueness bonus
        unique_chars = len(set(password))
        score += min(unique_chars, 25)
        
        # Penalties
        if re.search(r'(.)\1{2,}', password):
            score -= 10  # Repeated characters
        if re.search(r'123|abc|qwe', password.lower()):
            score -= 15  # Sequential patterns
        
        return max(0, min(score, 100))
    
    def _contains_suspicious_url_patterns(self, url: str) -> bool:
        """Check for suspicious URL patterns"""        suspicious_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'169\.254\.',  # Link-local
            r'10\.',        # Private network
            r'172\.1[6-9]\.',  # Private network
            r'172\.2[0-9]\.',  # Private network  
            r'172\.3[0-1]\.',  # Private network
            r'192\.168\.',  # Private network
            r'file://',
            r'ftp://',
            r'data:',
            r'javascript:',
        ]
        
        url_lower = url.lower()
        return any(re.search(pattern, url_lower) for pattern in suspicious_patterns)
    
    def _validate_file_magic_number(self, file_content: bytes, expected_ext: str) -> Dict[str, Any]:
        """Validate file magic number matches extension"""        
        if len(file_content) < 4:
            return {'is_valid': False, 'error': 'File too small to validate'}
        
        # Common magic numbers
        magic_numbers = {
            'jpg': [b'\xFF\xD8\xFF', b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1'],
            'png': [b'\x89\x50\x4E\x47'],
            'gif': [b'\x47\x49\x46\x38'],
            'pdf': [b'\x25\x50\x44\x46'],
            'zip': [b'\x50\x4B\x03\x04', b'\x50\x4B\x05\x06', b'\x50\x4B\x07\x08'],
            'mp3': [b'\xFF\xFB', b'\xFF\xF3', b'\xFF\xF2', b'\x49\x44\x33'],
            'wav': [b'\x52\x49\x46\x46'],
        }
        
        if expected_ext not in magic_numbers:
            return {'is_valid': True, 'warning': 'Unable to validate magic number for this file type'}
        
        file_start = file_content[:12]  # Check first 12 bytes
        expected_magic = magic_numbers[expected_ext]
        
        for magic in expected_magic:
            if file_start.startswith(magic):
                return {'is_valid': True, 'magic_number': magic.hex()}
        
        return {
            'is_valid': False, 
            'error': f'File content does not match extension "{expected_ext}"'
        }
    
    def _scan_for_malware(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Basic malware detection (simplified implementation)"""        
        # Check for suspicious file patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onerror=',
            b'eval(',
            b'document.write',
            b'exec(',
            b'system(',
        ]
        
        content_lower = file_content.lower()
        
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return {
                    'is_suspicious': True,
                    'reason': f'Suspicious pattern found: {pattern.decode("utf-8", errors="ignore")}'
                }
        
        # Check filename for suspicious extensions
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar']
        filename_lower = filename.lower()
        
        for ext in suspicious_extensions:
            if filename_lower.endswith(ext):
                return {
                    'is_suspicious': True,
                    'reason': f'Potentially dangerous file extension: {ext}'
                }
        
        return {'is_suspicious': False}
    
    def _calculate_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of JSON object"""        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(value, current_depth + 1) 
                      for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_json_depth(item, current_depth + 1) 
                      for item in obj)
        else:
            return current_depth


class XSSProtection:
    """Cross-Site Scripting (XSS) protection"""    
    def __init__(self):
        self.xss_patterns = self._initialize_xss_patterns()
        self.allowed_tags = {
            'basic': ['p', 'br', 'strong', 'em', 'u', 'b', 'i'],
            'extended': ['p', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                        'ul', 'ol', 'li', 'blockquote', 'pre', 'code'],
            'rich': ['p', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'a', 'img', 'table', 'tr', 'td', 'th']
        }
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
            'table': ['class', 'id'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan']
        }
    
    def _initialize_xss_patterns(self) -> List[re.Pattern]:
        """Initialize XSS detection patterns"""        patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'onfocus\s*=',
            r'onblur\s*=',
            r'onchange\s*=',
            r'eval\s*\(',
            r'expression\s*\(',
            r'url\s*\(',
            r'document\.write',
            r'document\.cookie',
            r'window\.location',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<applet[^>]*>',
            r'<meta[^>]*>',
            r'<link[^>]*>',
            r'<style[^>]*>.*?</style>',
            r'data:text/html',
            r'data:image/svg\+xml',
        ]
        
        return [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in patterns]
    
    def detect_xss(self, content: str) -> ValidationResult:
        """Detect XSS attacks in content"""        
        if not content:
            return ValidationResult(is_valid=True)
        
        detected_threats = []
        
        for pattern in self.xss_patterns:
            matches = pattern.findall(content)
            if matches:
                detected_threats.extend(matches)
        
        if detected_threats:
            return ValidationResult(
                is_valid=False,
                errors=[f'XSS threat detected: {threat[:50]}...' for threat in detected_threats[:3]],
                threat_type=SecurityThreat.XSS,
                severity=ValidationSeverity.HIGH,
                metadata={'detected_patterns': detected_threats}
            )
        
        return ValidationResult(is_valid=True)
    
    def sanitize_html(self, content: str, level: str = 'basic') -> str:
        """Sanitize HTML content"""        
        if not content:
            return ''
        
        # Use bleach for HTML sanitization
        allowed_tags = self.allowed_tags.get(level, self.allowed_tags['basic'])
        
        sanitized = bleach.clean(
            content,
            tags=allowed_tags,
            attributes=self.allowed_attributes,
            strip=True,
            strip_comments=True
        )
        
        return sanitized
    
    def escape_html_entities(self, content: str) -> str:
        """Escape HTML entities"""        return html.escape(content, quote=True)


class SQLInjectionProtection:
    """SQL Injection protection"""    
    def __init__(self):
        self.sql_patterns = self._initialize_sql_patterns()
    
    def _initialize_sql_patterns(self) -> List[re.Pattern]:
        """Initialize SQL injection detection patterns"""        patterns = [
            r"('|\"|;).*(-{2}|#|\/\*)",  # Comments after quotes
            r"union\s+select",
            r"select\s+.*\s+from",
            r"insert\s+into",
            r"update\s+.*\s+set",
            r"delete\s+from",
            r"drop\s+(table|database|schema)",
            r"alter\s+table",
            r"create\s+(table|database|schema)",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_\w+",
            r"xp_\w+",
            r";\s*(exec|execute|select|insert|update|delete|drop|alter|create)",
            r"'\s*;\s*",
            r'"\s*;\s*',
            r"or\s+1\s*=\s*1",
            r"and\s+1\s*=\s*1",
            r"'\s*or\s+'1'\s*=\s*'1",
            r'"\s*or\s+"1"\s*=\s*"1',
            r"'\s*or\s+'x'\s*=\s*'x",
            r'"\s*or\s+"x"\s*=\s*"x',
            r"'\s*(and|or)\s+'",
            r'"\s*(and|or)\s+"',
            r"(group\s+by|order\s+by).*having",
            r"(un|)ion.*(select|all|distinct)",
        ]
        
        return [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in patterns]
    
    def detect_sql_injection(self, content: str) -> ValidationResult:
        """Detect SQL injection attempts"""        
        if not content:
            return ValidationResult(is_valid=True)
        
        # Decode URL encoded characters
        content_decoded = content.replace('%20', ' ').replace('%27', "'").replace('%22', '"')
        
        detected_patterns = []
        
        for pattern in self.sql_patterns:
            matches = pattern.findall(content_decoded)
            if matches:
                detected_patterns.extend(matches)
        
        if detected_patterns:
            return ValidationResult(
                is_valid=False,
                errors=['SQL injection attempt detected'],
                threat_type=SecurityThreat.SQL_INJECTION,
                severity=ValidationSeverity.CRITICAL,
                metadata={'detected_patterns': detected_patterns[:5]}
            )
        
        return ValidationResult(is_valid=True)
    
    def sanitize_sql_input(self, content: str) -> str:
        """Sanitize input for SQL queries (basic sanitization)"""        
        if not content:
            return ''
        
        # Remove dangerous characters and patterns
        sanitized = content.replace("'", "''")  # Escape single quotes
        sanitized = re.sub(r'[;\-\/\*]', '', sanitized)  # Remove comment characters
        sanitized = re.sub(r'\s+(and|or|union|select|insert|update|delete|drop|alter|create)\s+', ' ', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()


class CSRFProtection:
    """Cross-Site Request Forgery (CSRF) protection"""    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.token_expiry = 3600  # 1 hour
        self.tokens: Dict[str, Dict[str, Any]] = {}  # In-memory fallback
    
    async def generate_token(self, session_id: str, user_id: str = None) -> str:
        """Generate CSRF token"""        token = secrets.token_urlsafe(32)
        token_data = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(seconds=self.token_expiry)).isoformat()
        }
        
        try:
            redis_client = await aioredis.from_url(self.redis_url)
            await redis_client.setex(
                f"csrf_token:{token}",
                self.token_expiry,
                json.dumps(token_data)
            )
            await redis_client.close()
        except Exception:
            # Fallback to in-memory storage
            self.tokens[token] = token_data
        
        return token
    
    async def validate_token(self, token: str, session_id: str, user_id: str = None) -> ValidationResult:
        """Validate CSRF token"""        
        if not token:
            return ValidationResult(
                is_valid=False,
                errors=['CSRF token is required'],
                threat_type=SecurityThreat.CSRF,
                severity=ValidationSeverity.HIGH
            )
        
        try:
            # Try Redis first
            redis_client = await aioredis.from_url(self.redis_url)
            token_data_json = await redis_client.get(f"csrf_token:{token}")
            await redis_client.close()
            
            if token_data_json:
                token_data = json.loads(token_data_json)
            else:
                # Fallback to in-memory
                token_data = self.tokens.get(token)
            
        except Exception:
            # Fallback to in-memory
            token_data = self.tokens.get(token)
        
        if not token_data:
            return ValidationResult(
                is_valid=False,
                errors=['Invalid or expired CSRF token'],
                threat_type=SecurityThreat.CSRF,
                severity=ValidationSeverity.HIGH
            )
        
        # Check expiration
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now(timezone.utc) > expires_at:
            return ValidationResult(
                is_valid=False,
                errors=['CSRF token has expired'],
                threat_type=SecurityThreat.CSRF,
                severity=ValidationSeverity.HIGH
            )
        
        # Check session match
        if token_data['session_id'] != session_id:
            return ValidationResult(
                is_valid=False,
                errors=['CSRF token session mismatch'],
                threat_type=SecurityThreat.CSRF,
                severity=ValidationSeverity.HIGH
            )
        
        # Check user match if provided
        if user_id and token_data.get('user_id') != user_id:
            return ValidationResult(
                is_valid=False,
                errors=['CSRF token user mismatch'],
                threat_type=SecurityThreat.CSRF,
                severity=ValidationSeverity.HIGH
            )
        
        return ValidationResult(is_valid=True)
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke CSRF token"""        try:
            redis_client = await aioredis.from_url(self.redis_url)
            result = await redis_client.delete(f"csrf_token:{token}")
            await redis_client.close()
            
            # Also remove from memory
            self.tokens.pop(token, None)
            
            return result > 0
        except Exception:
            # Fallback to in-memory
            return self.tokens.pop(token, None) is not None


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.rules: Dict[str, RateLimitRule] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Default rate limit rules
        self.add_rule('default', RateLimitRule(100, 60))  # 100 requests per minute
        self.add_rule('auth', RateLimitRule(5, 300))      # 5 auth attempts per 5 minutes
        self.add_rule('api', RateLimitRule(1000, 3600))   # 1000 API calls per hour
        self.add_rule('upload', RateLimitRule(10, 300))   # 10 uploads per 5 minutes
    
    def add_rule(self, name: str, rule: RateLimitRule):
        """Add rate limiting rule"""        self.rules[name] = rule
    
    async def check_rate_limit(self, identifier: str, rule_name: str = 'default',
                              context: Dict[str, Any] = None) -> ValidationResult:
        """Check if request is within rate limits"""        
        rule = self.rules.get(rule_name)
        if not rule:
            return ValidationResult(is_valid=True)
        
        # Check if IP is currently blocked
        if identifier in self.blocked_ips:
            if datetime.now(timezone.utc) < self.blocked_ips[identifier]:
                return ValidationResult(
                    is_valid=False,
                    errors=['IP address is temporarily blocked'],
                    threat_type=SecurityThreat.RATE_LIMIT_EXCEEDED,
                    severity=ValidationSeverity.HIGH,
                    metadata={'blocked_until': self.blocked_ips[identifier].isoformat()}
                )
            else:
                # Block period expired
                del self.blocked_ips[identifier]
        
        try:
            redis_client = await aioredis.from_url(self.redis_url)
            
            # Use sliding window algorithm
            now = int(time.time())
            window_start = now - rule.time_window
            
            # Get request count in current window
            request_count = await redis_client.zcount(
                f"rate_limit:{rule_name}:{identifier}",
                window_start,
                now
            )
            
            if request_count >= rule.max_requests:
                # Block the identifier
                block_until = datetime.now(timezone.utc) + timedelta(seconds=rule.block_duration)
                self.blocked_ips[identifier] = block_until
                
                await redis_client.close()
                return ValidationResult(
                    is_valid=False,
                    errors=[f'Rate limit exceeded. Maximum {rule.max_requests} requests per {rule.time_window} seconds'],
                    threat_type=SecurityThreat.RATE_LIMIT_EXCEEDED,
                    severity=ValidationSeverity.HIGH,
                    metadata={
                        'current_requests': request_count,
                        'max_requests': rule.max_requests,
                        'window_seconds': rule.time_window,
                        'blocked_until': block_until.isoformat()
                    }
                )
            
            # Record this request
            await redis_client.zadd(
                f"rate_limit:{rule_name}:{identifier}",
                {str(now): now}
            )
            
            # Set expiry on the key
            await redis_client.expire(
                f"rate_limit:{rule_name}:{identifier}",
                rule.time_window + rule.block_duration
            )
            
            # Clean old entries
            await redis_client.zremrangebyscore(
                f"rate_limit:{rule_name}:{identifier}",
                0,
                window_start
            )
            
            await redis_client.close()
            
            return ValidationResult(
                is_valid=True,
                metadata={
                    'current_requests': request_count + 1,
                    'max_requests': rule.max_requests,
                    'window_seconds': rule.time_window
                }
            )
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fallback to in-memory rate limiting
            return self._check_memory_rate_limit(identifier, rule)
    
    def _check_memory_rate_limit(self, identifier: str, rule: RateLimitRule) -> ValidationResult:
        """Fallback in-memory rate limiting"""        now = time.time()
        window_start = now - rule.time_window
        
        # Get request history for identifier
        requests = self.request_history[identifier]
        
        # Remove old requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        if len(requests) >= rule.max_requests:
            return ValidationResult(
                is_valid=False,
                errors=[f'Rate limit exceeded. Maximum {rule.max_requests} requests per {rule.time_window} seconds'],
                threat_type=SecurityThreat.RATE_LIMIT_EXCEEDED,
                severity=ValidationSeverity.HIGH
            )
        
        # Record this request
        requests.append(now)
        
        return ValidationResult(is_valid=True)


class SecurityValidator:
    """Comprehensive security validator combining all protection mechanisms"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.input_validator = InputValidator()
        self.xss_protection = XSSProtection()
        self.sql_protection = SQLInjectionProtection()
        self.csrf_protection = CSRFProtection(
            redis_url=self.config.get('redis_url', 'redis://localhost:6379')
        )
        self.rate_limiter = RateLimiter(
            redis_url=self.config.get('redis_url', 'redis://localhost:6379')
        )
        
        # Security metrics
        self.threat_counter = defaultdict(int)
        self.blocked_ips = set()
    
    async def validate_request(self, request_data: Dict[str, Any],
                              context: Dict[str, Any] = None) -> ValidationResult:
        """Comprehensive request validation"""        
        context = context or {}
        errors = []
        warnings = []
        threats = []
        
        # Rate limiting check
        client_ip = context.get('client_ip', 'unknown')
        rate_limit_result = await self.rate_limiter.check_rate_limit(
            client_ip, context.get('rate_limit_rule', 'default'), context
        )
        
        if not rate_limit_result.is_valid:
            return rate_limit_result
        
        # CSRF token validation for state-changing requests
        if context.get('requires_csrf', False):
            csrf_token = request_data.get('csrf_token') or context.get('csrf_token')
            session_id = context.get('session_id')
            user_id = context.get('user_id')
            
            csrf_result = await self.csrf_protection.validate_token(csrf_token, session_id, user_id)
            if not csrf_result.is_valid:
                return csrf_result
        
        # Validate all string fields for XSS and SQL injection
        for field_name, field_value in request_data.items():
            if isinstance(field_value, str):
                # XSS detection
                xss_result = self.xss_protection.detect_xss(field_value)
                if not xss_result.is_valid:
                    errors.extend(xss_result.errors)
                    threats.append(SecurityThreat.XSS)
                
                # SQL injection detection
                sql_result = self.sql_protection.detect_sql_injection(field_value)
                if not sql_result.is_valid:
                    errors.extend(sql_result.errors)
                    threats.append(SecurityThreat.SQL_INJECTION)
        
        # Additional security checks based on request type
        request_type = context.get('request_type', 'unknown')
        
        if request_type == 'file_upload':
            file_result = self.input_validator.validate_file_upload(
                request_data.get('filename', ''),
                request_data.get('file_content', b''),
                context.get('allowed_file_types', ['images'])
            )
            if not file_result.is_valid:
                errors.extend(file_result.errors)
        
        if request_type == 'json_api':
            json_data = request_data.get('json_payload')
            if json_data:
                json_result = self.input_validator.validate_json(
                    json.dumps(json_data) if isinstance(json_data, dict) else json_data
                )
                if not json_result.is_valid:
                    errors.extend(json_result.errors)
        
        # Update threat metrics
        for threat in threats:
            self.threat_counter[threat] += 1
        
        # Determine overall severity
        if SecurityThreat.SQL_INJECTION in threats or SecurityThreat.XSS in threats:
            severity = ValidationSeverity.CRITICAL
        elif len(threats) > 0:
            severity = ValidationSeverity.HIGH
        elif len(warnings) > 0:
            severity = ValidationSeverity.MEDIUM
        else:
            severity = ValidationSeverity.LOW
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            threat_type=threats[0] if threats else None,
            severity=severity,
            metadata={
                'detected_threats': [t.value for t in threats],
                'client_ip': client_ip,
                'request_type': request_type
            }
        )
    
    def validate_authentication(self, user_context: Dict[str, Any]) -> bool:
        """Validate authentication context"""        required_fields = ['user_id', 'session_id', 'authenticated_at']
        
        for field in required_fields:
            if not user_context.get(field):
                return False
        
        # Check session age
        authenticated_at = user_context.get('authenticated_at')
        if isinstance(authenticated_at, str):
            authenticated_at = datetime.fromisoformat(authenticated_at)
        
        max_session_age = timedelta(hours=24)  # 24 hours
        if datetime.now(timezone.utc) - authenticated_at > max_session_age:
            return False
        
        return True
    
    def validate_authorization(self, user_context: Dict[str, Any], 
                             request_data: Dict[str, Any]) -> bool:
        """Validate authorization context"""        # Basic authorization validation
        user_roles = user_context.get('roles', [])
        required_role = request_data.get('required_role')
        
        if required_role and required_role not in user_roles:
            return False
        
        return True
    
    def validate_input(self, request_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""        # Check for required fields, data types, etc.
        # This is a simplified implementation
        return isinstance(request_data, dict)
    
    def validate_csrf_token(self, request_data: Dict[str, Any]) -> bool:
        """Check if CSRF token is present when required"""        # This would be called from validate_request
        return True  # Placeholder
    
    def check_rate_limits(self, user_context: Dict[str, Any]) -> bool:
        """Check if user is within rate limits"""        # This would be called from validate_request
        return True  # Placeholder
    
    def scan_for_threats(self, request_data: Dict[str, Any]) -> bool:
        """Scan for security threats"""        # This would be called from validate_request
        return True  # Placeholder
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security validation metrics"""        return {
            'threat_counts': dict(self.threat_counter),
            'blocked_ips_count': len(self.blocked_ips),
            'total_threats_detected': sum(self.threat_counter.values())
        }


__all__ = [
    'InputValidator',
    'SecurityValidator',
    'XSSProtection',
    'SQLInjectionProtection',
    'CSRFProtection',
    'RateLimiter',
    'ValidationResult',
    'ValidationError',
    'SecurityThreat',
    'ValidationSeverity',
    'RateLimitRule'
]
