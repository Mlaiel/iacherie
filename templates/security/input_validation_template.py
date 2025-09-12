"""{{validator_name}} Input Validation Template for Ainflue Platform
{{validator_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Security Expert Role: Enterprise input validation with comprehensive security protection
"""

import logging
import re
import html
import base64
import json
from typing import Any, Dict, List, Optional, Union, Callable, Type
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from urllib.parse import urlparse
import ipaddress

from pydantic import BaseModel, validator, ValidationError
from email_validator import validate_email, EmailNotValidError
import bleach
from markupsafe import Markup

logger = logging.getLogger(__name__)


class SecurityViolationError(ValueError):
    """Raised when input validation detects security violation"""
    pass


class ValidationContext:
    """Context for validation operations"""
    
    def __init__(
        self,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        strict_mode: bool = True
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.strict_mode = strict_mode
        self.violations = []


class InputSanitizer:
    """Comprehensive input sanitization utilities
    
    Provides enterprise-grade input sanitization with:
    - XSS protection
    - SQL injection prevention
    - Path traversal protection
    - Command injection prevention
    - HTML/XML sanitization
    - JSON sanitization
    - File upload validation
    - Regular expression injection protection
    """
    
    # Dangerous patterns for security scanning
    XSS_PATTERNS = [
        r'<\s*script[^>]*>.*?</\s*script\s*>',
        r'javascript\s*:',
        r'vbscript\s*:',
        r'on\w+\s*=',
        r'<\s*iframe[^>]*>',
        r'<\s*object[^>]*>',
        r'<\s*embed[^>]*>',
        r'<\s*link[^>]*>',
        r'<\s*meta[^>]*>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
        r'<\s*form[^>]*>',
        r'<\s*input[^>]*>',
        r'<\s*button[^>]*>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bSELECT\b.*\bFROM\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bALTER\b.*\bTABLE\b)',
        r'(\bCREATE\b.*\bTABLE\b)',
        r'(\bEXEC\b|\bEXECUTE\b)',
        r'(\bSP_\w+)',
        r'(\bXP_\w+)',
        r'(\b--\b)',
        r'(\b/\*.*\*/)',
        r'(\bOR\b.*=.*)',
        r'(\bAND\b.*=.*)',
        r"('.*OR.*'.*=.*')",
        r"(\".*OR.*\".*=.*\")",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./+',
        r'\.\.\\+',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
        r'%252e%252e%252f',
        r'%c0%ae%c0%ae%c0%af',
        r'%c1%1c',
        r'\.\.%c0%af',
        r'\.\.%255c',
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$\(\){}]',
        r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|wget|curl|nc|ncat|telnet|ssh|su|sudo|chmod|chown|rm|mv|cp|find|grep|awk|sed|sort|head|tail|cut|tr|wc|md5sum|sha1sum|base64)\b',
        r'[<>]',
        r'\$\{.*\}',
        r'\$\(.*\)',
        r'`.*`',
    ]
    
    # Allowed HTML tags and attributes for content sanitization
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 's', 'sub', 'sup',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'blockquote', 'pre', 'code',
        'a', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'div', 'span',
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'div': ['class'],
        'span': ['class'],
        'table': ['class'],
        'th': ['scope'],
        'td': ['colspan', 'rowspan'],
    }
    
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @classmethod
    def sanitize_string(
        cls,
        value: str,
        max_length: Optional[int] = None,
        allow_html: bool = False,
        strict: bool = True
    ) -> str:
        """Sanitize string input with comprehensive security checks"""
        if not isinstance(value, str):
            return str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Length check
        if max_length and len(value) > max_length:
            if strict:
                raise ValidationError(f"String too long (max {max_length} characters)")
            value = value[:max_length]
        
        # Check for null bytes
        if '\x00' in value:
            raise SecurityViolationError("Null bytes detected in input")
        
        # Check for control characters (except common ones)
        control_chars = [chr(i) for i in range(32) if i not in [9, 10, 13]]  # Exclude tab, LF, CR
        if any(char in value for char in control_chars):
            if strict:
                raise SecurityViolationError("Control characters detected in input")
            # Remove control characters
            value = ''.join(char for char in value if char not in control_chars)
        
        # Security pattern detection
        cls._check_security_patterns(value, strict)
        
        # HTML handling
        if allow_html:
            value = cls._sanitize_html(value)
        else:
            # Escape HTML entities
            value = html.escape(value, quote=True)
        
        return value
    
    @classmethod
    def sanitize_html(cls, value: str, strict: bool = True) -> str:
        """Sanitize HTML content"""
        if not isinstance(value, str):
            return str(value)
        
        # Check for dangerous patterns first
        cls._check_security_patterns(value, strict)
        
        # Clean HTML using bleach
        cleaned = bleach.clean(
            value,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            protocols=cls.ALLOWED_PROTOCOLS,
            strip=True,
            strip_comments=True
        )
        
        return cleaned
    
    @classmethod
    def sanitize_url(cls, value: str, allowed_schemes: Optional[List[str]] = None) -> str:
        """Sanitize and validate URL"""
        if not isinstance(value, str):
            raise ValidationError("URL must be a string")
        
        value = value.strip()
        
        # Parse URL
        try:
            parsed = urlparse(value)
        except Exception:
            raise ValidationError("Invalid URL format")
        
        # Check scheme
        allowed_schemes = allowed_schemes or ['http', 'https']
        if parsed.scheme.lower() not in allowed_schemes:
            raise ValidationError(f"URL scheme must be one of: {allowed_schemes}")
        
        # Check for dangerous patterns
        cls._check_security_patterns(value, strict=True)
        
        # Check for private/local addresses in hostname
        if parsed.hostname:
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    raise SecurityViolationError("Private/local IP addresses not allowed")
            except ipaddress.AddressValueError:
                # Not an IP address, check hostname
                if parsed.hostname.lower() in ['localhost', '127.0.0.1', '::1']:
                    raise SecurityViolationError("Localhost addresses not allowed")
        
        return value
    
    @classmethod
    def sanitize_email(cls, value: str) -> str:
        """Sanitize and validate email address"""
        if not isinstance(value, str):
            raise ValidationError("Email must be a string")
        
        value = value.strip().lower()
        
        # Basic email validation
        try:
            validated_email = validate_email(value)
            return validated_email.email
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {e}")
    
    @classmethod
    def sanitize_filename(cls, value: str, max_length: int = 255) -> str:
        """Sanitize filename for safe file operations"""
        if not isinstance(value, str):
            raise ValidationError("Filename must be a string")
        
        value = value.strip()
        
        # Check length
        if len(value) > max_length:
            raise ValidationError(f"Filename too long (max {max_length} characters)")
        
        # Check for path traversal
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityViolationError("Path traversal detected in filename")
        
        # Remove/replace dangerous characters
        # Keep only alphanumeric, dots, hyphens, underscores, and spaces
        sanitized = re.sub(r'[^\w\s.-]', '', value)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = sanitized.split('.')[0].upper()
        if name_without_ext in reserved_names:
            raise ValidationError(f"Reserved filename: {value}")
        
        if not sanitized:
            raise ValidationError("Filename cannot be empty after sanitization")
        
        return sanitized
    
    @classmethod
    def sanitize_json(cls, value: Union[str, dict, list], max_depth: int = 10) -> Union[dict, list]:
        """Sanitize JSON data"""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON format")
        
        # Check depth to prevent deeply nested objects
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise SecurityViolationError(f"JSON too deeply nested (max depth: {max_depth})")
            
            if isinstance(obj, dict):
                for key, val in obj.items():
                    # Sanitize keys
                    if not isinstance(key, str):
                        raise ValidationError("JSON keys must be strings")
                    cls._check_security_patterns(key, strict=True)
                    check_depth(val, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
            elif isinstance(obj, str):
                cls._check_security_patterns(obj, strict=True)
        
        check_depth(value)
        return value
    
    @classmethod
    def sanitize_sql_identifier(cls, value: str) -> str:
        """Sanitize SQL identifier (table/column names)"""
        if not isinstance(value, str):
            raise ValidationError("SQL identifier must be a string")
        
        value = value.strip()
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityViolationError("SQL injection detected in identifier")
        
        # Allow only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise ValidationError("Invalid SQL identifier format")
        
        # Check length
        if len(value) > 63:  # PostgreSQL limit
            raise ValidationError("SQL identifier too long (max 63 characters)")
        
        return value
    
    @classmethod
    def _check_security_patterns(cls, value: str, strict: bool = True):
        """Check for security violation patterns"""
        violations = []
        
        # XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                violations.append(f"XSS pattern detected: {pattern}")
        
        # SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                violations.append(f"SQL injection pattern detected: {pattern}")
        
        # Path traversal patterns
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                violations.append(f"Path traversal pattern detected: {pattern}")
        
        # Command injection patterns
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                violations.append(f"Command injection pattern detected: {pattern}")
        
        if violations:
            if strict:
                raise SecurityViolationError(f"Security violations detected: {'; '.join(violations)}")
            else:
                logger.warning(f"Security violations detected but not strict mode: {'; '.join(violations)}")
    
    @classmethod
    def _sanitize_html(cls, value: str) -> str:
        """Internal HTML sanitization"""
        return bleach.clean(
            value,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            protocols=cls.ALLOWED_PROTOCOLS,
            strip=True,
            strip_comments=True
        )


class DataValidator:
    """Comprehensive data validation utilities
    
    Provides enterprise-grade data validation with:
    - Type validation
    - Range validation
    - Format validation
    - Business rule validation
    - Cross-field validation
    - Custom validation rules
    """
    
    @staticmethod
    def validate_uuid(value: Union[str, UUID], required: bool = True) -> Optional[UUID]:
        """Validate UUID format"""
        if value is None:
            if required:
                raise ValidationError("UUID is required")
            return None
        
        if isinstance(value, UUID):
            return value
        
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError:
                raise ValidationError("Invalid UUID format")
        
        raise ValidationError("UUID must be string or UUID object")
    
    @staticmethod
    def validate_integer(
        value: Union[int, str],
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        required: bool = True
    ) -> Optional[int]:
        """Validate integer with range checks"""
        if value is None:
            if required:
                raise ValidationError("Integer is required")
            return None
        
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValidationError("Invalid integer format")
        
        if not isinstance(value, int):
            raise ValidationError("Value must be an integer")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return value
    
    @staticmethod
    def validate_float(
        value: Union[float, int, str],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        required: bool = True
    ) -> Optional[float]:
        """Validate float with range checks"""
        if value is None:
            if required:
                raise ValidationError("Float is required")
            return None
        
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                raise ValidationError("Invalid float format")
        
        if not isinstance(value, (int, float)):
            raise ValidationError("Value must be a number")
        
        value = float(value)
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return value
    
    @staticmethod
    def validate_decimal(
        value: Union[Decimal, float, int, str],
        max_digits: Optional[int] = None,
        decimal_places: Optional[int] = None,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        required: bool = True
    ) -> Optional[Decimal]:
        """Validate decimal with precision checks"""
        if value is None:
            if required:
                raise ValidationError("Decimal is required")
            return None
        
        if isinstance(value, str):
            try:
                value = Decimal(value)
            except Exception:
                raise ValidationError("Invalid decimal format")
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            raise ValidationError("Value must be a decimal")
        
        # Check precision
        if max_digits is not None:
            total_digits = len(str(value).replace('.', '').replace('-', ''))
            if total_digits > max_digits:
                raise ValidationError(f"Too many digits (max {max_digits})")
        
        # Check decimal places
        if decimal_places is not None:
            scale = value.as_tuple().exponent
            if scale < -decimal_places:
                raise ValidationError(f"Too many decimal places (max {decimal_places})")
        
        # Range checks
        if min_value is not None and value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return value
    
    @staticmethod
    def validate_datetime(
        value: Union[datetime, str],
        min_datetime: Optional[datetime] = None,
        max_datetime: Optional[datetime] = None,
        required: bool = True
    ) -> Optional[datetime]:
        """Validate datetime with range checks"""
        if value is None:
            if required:
                raise ValidationError("Datetime is required")
            return None
        
        if isinstance(value, str):
            # Try common datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%f%z',
                '%Y-%m-%dT%H:%M:%S%z', 
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValidationError("Invalid datetime format")
        
        if not isinstance(value, datetime):
            raise ValidationError("Value must be a datetime")
        
        # Range checks
        if min_datetime and value < min_datetime:
            raise ValidationError(f"Datetime must be after {min_datetime}")
        
        if max_datetime and value > max_datetime:
            raise ValidationError(f"Datetime must be before {max_datetime}")
        
        return value
    
    @staticmethod
    def validate_enum(
        value: Any,
        allowed_values: List[Any],
        required: bool = True
    ) -> Any:
        """Validate enumeration values"""
        if value is None:
            if required:
                raise ValidationError("Enum value is required")
            return None
        
        if value not in allowed_values:
            raise ValidationError(f"Value must be one of: {allowed_values}")
        
        return value
    
    @staticmethod
    def validate_list(
        value: Union[List, str],
        item_type: Type = str,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique: bool = False,
        required: bool = True
    ) -> Optional[List]:
        """Validate list with item type and size checks"""
        if value is None:
            if required:
                raise ValidationError("List is required")
            return None
        
        if isinstance(value, str):
            # Try to parse as JSON list
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # Split by comma as fallback
                value = [item.strip() for item in value.split(',') if item.strip()]
        
        if not isinstance(value, list):
            raise ValidationError("Value must be a list")
        
        # Size checks
        if min_items is not None and len(value) < min_items:
            raise ValidationError(f"List must have at least {min_items} items")
        
        if max_items is not None and len(value) > max_items:
            raise ValidationError(f"List must have at most {max_items} items")
        
        # Type validation for items
        validated_items = []
        for i, item in enumerate(value):
            try:
                if item_type == str:
                    validated_item = InputSanitizer.sanitize_string(str(item))
                elif item_type == int:
                    validated_item = DataValidator.validate_integer(item)
                elif item_type == float:
                    validated_item = DataValidator.validate_float(item)
                elif item_type == UUID:
                    validated_item = DataValidator.validate_uuid(item)
                else:
                    validated_item = item_type(item)
                
                validated_items.append(validated_item)
            except Exception as e:
                raise ValidationError(f"Invalid item at index {i}: {e}")
        
        # Uniqueness check
        if unique and len(validated_items) != len(set(validated_items)):
            raise ValidationError("List items must be unique")
        
        return validated_items


class {{validator_name}}Validator:
    """{{validator_description}}
    
    Specialized validator for {{model_name}} with business-specific rules
    """
    
    def __init__(self, context: Optional[ValidationContext] = None):
        self.context = context or ValidationContext()
        self.sanitizer = InputSanitizer()
        self.data_validator = DataValidator()
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data"""
        validated_data = {}
        
        try:
            # Validate each field based on business rules
            for field, value in data.items():
                validated_data[field] = self._validate_field(field, value)
            
            # Cross-field validation
            self._validate_cross_fields(validated_data)
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Validation failed for {self.__class__.__name__}: {e}")
            if self.context:
                self.context.violations.append(str(e))
            raise
    
    def _validate_field(self, field_name: str, value: Any) -> Any:
        """Validate individual field"""
        # Common field validations
        if field_name == 'id':
            return self.data_validator.validate_uuid(value, required=False)
        
        elif field_name == 'name':
            return self.sanitizer.sanitize_string(
                value, 
                max_length=255, 
                allow_html=False, 
                strict=self.context.strict_mode
            )
        
        elif field_name == 'description':
            return self.sanitizer.sanitize_string(
                value,
                max_length=2000,
                allow_html=True,
                strict=self.context.strict_mode
            )
        
        elif field_name == 'email':
            return self.sanitizer.sanitize_email(value)
        
        elif field_name == 'url':
            return self.sanitizer.sanitize_url(value)
        
        elif field_name == 'tags':
            return self.data_validator.validate_list(
                value,
                item_type=str,
                max_items=20,
                unique=True,
                required=False
            )
        
        elif field_name == 'metadata':
            if value is not None:
                return self.sanitizer.sanitize_json(value, max_depth=5)
            return None
        
        elif field_name == 'status':
            allowed_statuses = ['active', 'inactive', 'pending', 'deleted', 'archived']
            return self.data_validator.validate_enum(value, allowed_statuses)
        
        elif field_name == 'priority':
            return self.data_validator.validate_integer(value, min_value=0, max_value=10)
        
        elif field_name == 'score':
            return self.data_validator.validate_float(value, min_value=0.0, max_value=100.0, required=False)
        
        elif field_name in ['is_public', 'is_featured', 'is_locked', 'is_verified']:
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on']
            return bool(value)
        
        elif field_name in ['created_at', 'updated_at', 'deleted_at']:
            return self.data_validator.validate_datetime(value, required=False)
        
        elif field_name in ['owner_id', 'parent_id', 'tenant_id', 'workspace_id']:
            return self.data_validator.validate_uuid(value, required=False)
        
        # Default: sanitize as string
        elif isinstance(value, str):
            return self.sanitizer.sanitize_string(
                value,
                strict=self.context.strict_mode
            )
        
        return value
    
    def _validate_cross_fields(self, data: Dict[str, Any]):
        """Validate cross-field business rules"""
        # Business rule: Featured items must be public
        if data.get('is_featured') and not data.get('is_public'):
            raise ValidationError("Featured items must be public")
        
        # Business rule: Deleted items cannot be featured
        if data.get('status') == 'deleted' and data.get('is_featured'):
            raise ValidationError("Deleted items cannot be featured")
        
        # Business rule: Parent cannot be self
        if data.get('parent_id') and data.get('id'):
            if data['parent_id'] == data['id']:
                raise ValidationError("Item cannot be its own parent")
        
        # Add more business-specific validation rules here
    
    def validate_file_upload(
        self,
        filename: str,
        content_type: str,
        file_size: int,
        allowed_types: Optional[List[str]] = None,
        max_size: int = 10 * 1024 * 1024  # 10MB default
    ) -> Dict[str, str]:
        """Validate file upload"""
        # Sanitize filename
        safe_filename = self.sanitizer.sanitize_filename(filename)
        
        # Check file size
        if file_size > max_size:
            raise ValidationError(f"File too large (max {max_size} bytes)")
        
        # Check content type
        allowed_types = allowed_types or [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'application/json'
        ]
        
        if content_type not in allowed_types:
            raise ValidationError(f"File type not allowed: {content_type}")
        
        # Additional security checks
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
            '.jar', '.ps1', '.sh', '.php', '.asp', '.aspx', '.jsp'
        ]
        
        file_ext = '.' + safe_filename.split('.')[-1].lower() if '.' in safe_filename else ''
        if file_ext in dangerous_extensions:
            raise SecurityViolationError(f"Dangerous file extension: {file_ext}")
        
        return {
            'filename': safe_filename,
            'content_type': content_type,
            'size': file_size
        }


# Export validator classes
__all__ = [
    'SecurityViolationError',
    'ValidationContext',
    'InputSanitizer',
    'DataValidator',
    '{{validator_name}}Validator'
]