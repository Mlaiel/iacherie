"""Validation Utilities for IA Influencer Agent Platform
Comprehensive data validation, schema validation, and business rule validation

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import re
import json
import uuid
from datetime import datetime, date, time
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List, Optional, Union, Callable, Type, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import validators
import phonenumbers
from phonenumbers import NumberParseException
import pycountry
from PIL import Image
import magic
import hashlib
import logging
from urllib.parse import urlparse
import ipaddress
from email_validator import validate_email, EmailNotValidError
import password_strength
from jsonschema import validate, ValidationError, Draft7Validator
from cerberus import Validator as CerberusValidator
import os
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ValidationSeverity(Enum):
    """Validation severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Validation result container"""    is_valid: bool
    severity: ValidationSeverity = ValidationSeverity.INFO
    field: Optional[str] = None
    message: str = ""
    code: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'is_valid': self.is_valid,
            'severity': self.severity.value,
            'field': self.field,
            'message': self.message,
            'code': self.code,
            'details': self.details
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report"""    is_valid: bool
    results: List[ValidationResult] = field(default_factory=list)
    errors_count: int = 0
    warnings_count: int = 0
    info_count: int = 0
    critical_count: int = 0
    
    def add_result(self, result: ValidationResult):
        """Add validation result"""        self.results.append(result)
        
        if result.severity == ValidationSeverity.ERROR:
            self.errors_count += 1
            self.is_valid = False
        elif result.severity == ValidationSeverity.WARNING:
            self.warnings_count += 1
        elif result.severity == ValidationSeverity.CRITICAL:
            self.critical_count += 1
            self.is_valid = False
        else:
            self.info_count += 1
    
    def get_errors(self) -> List[ValidationResult]:
        """Get all error results"""        return [r for r in self.results if r.severity == ValidationSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationResult]:
        """Get all warning results"""        return [r for r in self.results if r.severity == ValidationSeverity.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'is_valid': self.is_valid,
            'summary': {
                'total_checks': len(self.results),
                'errors': self.errors_count,
                'warnings': self.warnings_count,
                'info': self.info_count,
                'critical': self.critical_count
            },
            'results': [r.to_dict() for r in self.results]
        }


class BaseValidator:
    """Base validator class"""    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate value - base implementation"""        try:
            # Basic validation: check if value is not None
            if value is None:
                return self._create_result(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message="Value cannot be None",
                    field=field_name,
                    code="NULL_VALUE"
                )
            
            # Basic type validation for common types
            if isinstance(value, str):
                # String validation
                if not value.strip():
                    return self._create_result(
                        is_valid=not self.strict_mode,  # Allow empty strings in non-strict mode
                        severity=ValidationSeverity.WARNING if not self.strict_mode else ValidationSeverity.ERROR,
                        message="Empty string provided",
                        field=field_name,
                        code="EMPTY_STRING"
                    )
            
            # If we get here, basic validation passed
            return self._create_result(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                message="Basic validation passed",
                field=field_name,
                code="VALID",
                details={
                    "value_type": type(value).__name__,
                    "validation_type": "basic",
                    "strict_mode": self.strict_mode
                }
            )
            
        except Exception as e:
            return self._create_result(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Validation error: {str(e)}",
                field=field_name,
                code="VALIDATION_ERROR",
                details={"exception": str(e)}
            )
    
    def _create_result(self, is_valid: bool, 
                      severity: ValidationSeverity = ValidationSeverity.ERROR,
                      message: str = "", 
                      field: str = None,
                      code: str = None,
                      details: Dict[str, Any] = None) -> ValidationResult:
        """Helper to create validation result"""        return ValidationResult(
            is_valid=is_valid,
            severity=severity,
            field=field,
            message=message,
            code=code,
            details=details or {}
        )


class StringValidator(BaseValidator):
    """String validation with various constraints"""    
    def __init__(self, min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 pattern: Optional[str] = None,
                 allowed_chars: Optional[str] = None,
                 forbidden_chars: Optional[str] = None,
                 case_sensitive: bool = True,
                 strip_whitespace: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_chars = set(allowed_chars) if allowed_chars else None
        self.forbidden_chars = set(forbidden_chars) if forbidden_chars else None
        self.case_sensitive = case_sensitive
        self.strip_whitespace = strip_whitespace
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate string value"""        if value is None:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Value cannot be None", field_name, "NULL_VALUE"
            )
        
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"Cannot convert {type(value).__name__} to string", field_name, "TYPE_CONVERSION_ERROR"
                )
        
        # Strip whitespace if requested
        if self.strip_whitespace:
            value = value.strip()
        
        # Check length constraints
        if self.min_length is not None and len(value) < self.min_length:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"String too short (minimum {self.min_length} characters)", 
                field_name, "MIN_LENGTH_ERROR",
                {"actual_length": len(value), "min_length": self.min_length}
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"String too long (maximum {self.max_length} characters)", 
                field_name, "MAX_LENGTH_ERROR",
                {"actual_length": len(value), "max_length": self.max_length}
            )
        
        # Check pattern
        if self.pattern and not self.pattern.match(value):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "String does not match required pattern", 
                field_name, "PATTERN_MISMATCH"
            )
        
        # Check allowed characters
        if self.allowed_chars:
            value_chars = set(value.lower() if not self.case_sensitive else value)
            if not value_chars.issubset(self.allowed_chars):
                forbidden = value_chars - self.allowed_chars
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"String contains forbidden characters: {', '.join(forbidden)}", 
                    field_name, "FORBIDDEN_CHARS",
                    {"forbidden_chars": list(forbidden)}
                )
        
        # Check forbidden characters
        if self.forbidden_chars:
            value_chars = set(value.lower() if not self.case_sensitive else value)
            found_forbidden = value_chars.intersection(self.forbidden_chars)
            if found_forbidden:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"String contains forbidden characters: {', '.join(found_forbidden)}", 
                    field_name, "FORBIDDEN_CHARS",
                    {"forbidden_chars": list(found_forbidden)}
                )
        
        return self._create_result(True, ValidationSeverity.INFO, "Valid string", field_name)


class EmailValidator(BaseValidator):
    """Email address validation"""    
    def __init__(self, check_deliverability: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.check_deliverability = check_deliverability
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate email address"""        if not isinstance(value, str):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Email must be a string", field_name, "INVALID_TYPE"
            )
        
        try:
            # Use email-validator library for comprehensive validation
            validated_email = validate_email(
                value,
                check_deliverability=self.check_deliverability
            )
            
            return self._create_result(
                True, ValidationSeverity.INFO,
                "Valid email address", field_name, "VALID_EMAIL",
                {
                    "normalized": validated_email.email,
                    "local": validated_email.local,
                    "domain": validated_email.domain
                }
            )
            
        except EmailNotValidError as e:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Invalid email: {str(e)}", field_name, "INVALID_EMAIL"
            )


class PhoneValidator(BaseValidator):
    """Phone number validation"""    
    def __init__(self, default_country: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.default_country = default_country
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate phone number"""        if not isinstance(value, str):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Phone number must be a string", field_name, "INVALID_TYPE"
            )
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(value, self.default_country)
            
            # Check if valid
            if not phonenumbers.is_valid_number(parsed_number):
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Invalid phone number", field_name, "INVALID_PHONE"
                )
            
            # Get additional info
            country_code = phonenumbers.region_code_for_number(parsed_number)
            carrier = phonenumbers.carrier.name_for_number(parsed_number, 'en')
            timezone = phonenumbers.timezone.time_zones_for_number(parsed_number)
            
            return self._create_result(
                True, ValidationSeverity.INFO,
                "Valid phone number", field_name, "VALID_PHONE",
                {
                    "international_format": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    "national_format": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                    "country_code": country_code,
                    "carrier": carrier,
                    "timezones": list(timezone)
                }
            )
            
        except NumberParseException as e:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Phone parsing error: {str(e)}", field_name, "PHONE_PARSE_ERROR"
            )


class URLValidator(BaseValidator):
    """URL validation"""    
    def __init__(self, allowed_schemes: Optional[List[str]] = None,
                 require_tld: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        self.require_tld = require_tld
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate URL"""        if not isinstance(value, str):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "URL must be a string", field_name, "INVALID_TYPE"
            )
        
        try:
            # Use validators library
            if not validators.url(value):
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Invalid URL format", field_name, "INVALID_URL"
                )
            
            # Parse URL for additional validation
            parsed = urlparse(value)
            
            # Check scheme
            if self.allowed_schemes and parsed.scheme not in self.allowed_schemes:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"URL scheme '{parsed.scheme}' not allowed. Allowed: {', '.join(self.allowed_schemes)}", 
                    field_name, "INVALID_SCHEME",
                    {"scheme": parsed.scheme, "allowed_schemes": self.allowed_schemes}
                )
            
            # Check for TLD if required
            if self.require_tld and '.' not in parsed.netloc:
                return self._create_result(
                    False, ValidationSeverity.WARNING,
                    "URL appears to lack top-level domain", field_name, "NO_TLD"
                )
            
            return self._create_result(
                True, ValidationSeverity.INFO,
                "Valid URL", field_name, "VALID_URL",
                {
                    "scheme": parsed.scheme,
                    "netloc": parsed.netloc,
                    "path": parsed.path,
                    "params": parsed.params,
                    "query": parsed.query,
                    "fragment": parsed.fragment
                }
            )
            
        except Exception as e:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"URL validation error: {str(e)}", field_name, "URL_VALIDATION_ERROR"
            )


class IPAddressValidator(BaseValidator):
    """IP address validation"""    
    def __init__(self, allow_ipv4: bool = True, allow_ipv6: bool = True,
                 allow_private: bool = True, allow_loopback: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.allow_ipv4 = allow_ipv4
        self.allow_ipv6 = allow_ipv6
        self.allow_private = allow_private
        self.allow_loopback = allow_loopback
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate IP address"""        if not isinstance(value, str):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "IP address must be a string", field_name, "INVALID_TYPE"
            )
        
        try:
            ip = ipaddress.ip_address(value)
            
            # Check IP version
            if isinstance(ip, ipaddress.IPv4Address) and not self.allow_ipv4:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "IPv4 addresses not allowed", field_name, "IPV4_NOT_ALLOWED"
                )
            
            if isinstance(ip, ipaddress.IPv6Address) and not self.allow_ipv6:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "IPv6 addresses not allowed", field_name, "IPV6_NOT_ALLOWED"
                )
            
            # Check for private addresses
            if ip.is_private and not self.allow_private:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Private IP addresses not allowed", field_name, "PRIVATE_IP_NOT_ALLOWED"
                )
            
            # Check for loopback addresses
            if ip.is_loopback and not self.allow_loopback:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Loopback IP addresses not allowed", field_name, "LOOPBACK_IP_NOT_ALLOWED"
                )
            
            return self._create_result(
                True, ValidationSeverity.INFO,
                "Valid IP address", field_name, "VALID_IP",
                {
                    "version": ip.version,
                    "is_private": ip.is_private,
                    "is_global": ip.is_global,
                    "is_loopback": ip.is_loopback,
                    "is_multicast": ip.is_multicast,
                    "compressed": ip.compressed if hasattr(ip, 'compressed') else str(ip)
                }
            )
            
        except ValueError as e:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Invalid IP address: {str(e)}", field_name, "INVALID_IP"
            )


class PasswordValidator(BaseValidator):
    """Password strength validation"""    
    def __init__(self, min_length: int = 8, max_length: int = 128,
                 require_uppercase: bool = True, require_lowercase: bool = True,
                 require_digits: bool = True, require_symbols: bool = True,
                 min_strength_score: float = 0.6, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_symbols = require_symbols
        self.min_strength_score = min_strength_score
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate password strength"""        if not isinstance(value, str):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Password must be a string", field_name, "INVALID_TYPE"
            )
        
        issues = []
        
        # Check length
        if len(value) < self.min_length:
            issues.append(f"Password too short (minimum {self.min_length} characters)")
        
        if len(value) > self.max_length:
            issues.append(f"Password too long (maximum {self.max_length} characters)")
        
        # Check character requirements
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            issues.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            issues.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', value):
            issues.append("Password must contain at least one digit")
        
        if self.require_symbols and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            issues.append("Password must contain at least one special character")
        
        # Calculate strength score
        try:
            strength = password_strength.PasswordStats(value)
            strength_score = min(1.0, strength.strength())
        except Exception:
            strength_score = 0.0
        
        if strength_score < self.min_strength_score:
            issues.append(f"Password strength too low (score: {strength_score:.2f}, minimum: {self.min_strength_score})")
        
        if issues:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "; ".join(issues), field_name, "WEAK_PASSWORD",
                {"strength_score": strength_score, "issues": issues}
            )
        
        return self._create_result(
            True, ValidationSeverity.INFO,
            "Strong password", field_name, "STRONG_PASSWORD",
            {"strength_score": strength_score}
        )


class NumericValidator(BaseValidator):
    """Numeric value validation"""    
    def __init__(self, min_value: Optional[Union[int, float]] = None,
                 max_value: Optional[Union[int, float]] = None,
                 allow_float: bool = True,
                 precision: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float
        self.precision = precision
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate numeric value"""        # Try to convert to number
        if isinstance(value, str):
            try:
                if '.' in value and self.allow_float:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Cannot convert to number", field_name, "INVALID_NUMBER"
                )
        
        if not isinstance(value, (int, float, Decimal)):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Value must be numeric", field_name, "NOT_NUMERIC"
            )
        
        # Check if float is allowed
        if isinstance(value, float) and not self.allow_float:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Float values not allowed", field_name, "FLOAT_NOT_ALLOWED"
            )
        
        # Check range
        if self.min_value is not None and value < self.min_value:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Value too small (minimum {self.min_value})", field_name, "VALUE_TOO_SMALL",
                {"value": value, "min_value": self.min_value}
            )
        
        if self.max_value is not None and value > self.max_value:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Value too large (maximum {self.max_value})", field_name, "VALUE_TOO_LARGE",
                {"value": value, "max_value": self.max_value}
            )
        
        # Check precision
        if self.precision is not None and isinstance(value, float):
            decimal_places = len(str(value).split('.')[-1]) if '.' in str(value) else 0
            if decimal_places > self.precision:
                return self._create_result(
                    False, ValidationSeverity.WARNING,
                    f"Value has too many decimal places (maximum {self.precision})", 
                    field_name, "PRECISION_EXCEEDED",
                    {"decimal_places": decimal_places, "max_precision": self.precision}
                )
        
        return self._create_result(
            True, ValidationSeverity.INFO,
            "Valid numeric value", field_name, "VALID_NUMBER",
            {"value": value, "type": type(value).__name__}
        )


class DateTimeValidator(BaseValidator):
    """Date and time validation"""    
    def __init__(self, min_date: Optional[datetime] = None,
                 max_date: Optional[datetime] = None,
                 date_format: Optional[str] = None,
                 allow_future: bool = True,
                 allow_past: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.min_date = min_date
        self.max_date = max_date
        self.date_format = date_format
        self.allow_future = allow_future
        self.allow_past = allow_past
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate date/time value"""        # Convert string to datetime if needed
        if isinstance(value, str):
            try:
                if self.date_format:
                    value = datetime.strptime(value, self.date_format)
                else:
                    # Try common formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            value = datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        return self._create_result(
                            False, ValidationSeverity.ERROR,
                            "Cannot parse date string", field_name, "INVALID_DATE_FORMAT"
                        )
            except ValueError:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Invalid date format", field_name, "INVALID_DATE_FORMAT"
                )
        
        if not isinstance(value, (datetime, date)):
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Value must be a date/datetime", field_name, "INVALID_TYPE"
            )
        
        # Convert date to datetime for comparison
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, time.min)
        
        now = datetime.now()
        
        # Check future/past restrictions
        if value > now and not self.allow_future:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Future dates not allowed", field_name, "FUTURE_DATE_NOT_ALLOWED"
            )
        
        if value < now and not self.allow_past:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Past dates not allowed", field_name, "PAST_DATE_NOT_ALLOWED"
            )
        
        # Check date range
        if self.min_date and value < self.min_date:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Date too early (minimum {self.min_date})", field_name, "DATE_TOO_EARLY",
                {"value": value.isoformat(), "min_date": self.min_date.isoformat()}
            )
        
        if self.max_date and value > self.max_date:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"Date too late (maximum {self.max_date})", field_name, "DATE_TOO_LATE",
                {"value": value.isoformat(), "max_date": self.max_date.isoformat()}
            )
        
        return self._create_result(
            True, ValidationSeverity.INFO,
            "Valid date/time", field_name, "VALID_DATETIME",
            {"value": value.isoformat()}
        )


class FileValidator(BaseValidator):
    """File validation"""    
    def __init__(self, allowed_extensions: Optional[List[str]] = None,
                 allowed_mime_types: Optional[List[str]] = None,
                 max_file_size: Optional[int] = None,
                 min_file_size: Optional[int] = None,
                 check_content: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions] if allowed_extensions else None
        self.allowed_mime_types = allowed_mime_types
        self.max_file_size = max_file_size
        self.min_file_size = min_file_size
        self.check_content = check_content
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate file"""        if isinstance(value, str):
            # Assume it's a file path
            file_path = Path(value)
            if not file_path.exists():
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "File does not exist", field_name, "FILE_NOT_FOUND"
                )
            
            file_size = file_path.stat().st_size
            file_name = file_path.name
            
        elif hasattr(value, 'read'):
            # Assume it's a file-like object
            try:
                current_pos = value.tell()
                value.seek(0, 2)  # Go to end
                file_size = value.tell()
                value.seek(current_pos)  # Return to original position
                file_name = getattr(value, 'name', 'unknown')
            except Exception:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    "Cannot determine file size", field_name, "SIZE_UNKNOWN"
                )
        else:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                "Invalid file type", field_name, "INVALID_FILE_TYPE"
            )
        
        # Check file size
        if self.min_file_size and file_size < self.min_file_size:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"File too small (minimum {self.min_file_size} bytes)", 
                field_name, "FILE_TOO_SMALL",
                {"file_size": file_size, "min_size": self.min_file_size}
            )
        
        if self.max_file_size and file_size > self.max_file_size:
            return self._create_result(
                False, ValidationSeverity.ERROR,
                f"File too large (maximum {self.max_file_size} bytes)", 
                field_name, "FILE_TOO_LARGE",
                {"file_size": file_size, "max_size": self.max_file_size}
            )
        
        # Check extension
        if self.allowed_extensions:
            file_ext = Path(file_name).suffix.lower()
            if file_ext not in self.allowed_extensions:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"File extension '{file_ext}' not allowed. Allowed: {', '.join(self.allowed_extensions)}", 
                    field_name, "INVALID_EXTENSION",
                    {"extension": file_ext, "allowed_extensions": self.allowed_extensions}
                )
        
        # Check MIME type
        if self.allowed_mime_types and self.check_content:
            try:
                if isinstance(value, str):
                    mime_type = magic.from_file(value, mime=True)
                else:
                    # Read a small chunk to determine MIME type
                    current_pos = value.tell()
                    chunk = value.read(1024)
                    value.seek(current_pos)
                    mime_type = magic.from_buffer(chunk, mime=True)
                
                if mime_type not in self.allowed_mime_types:
                    return self._create_result(
                        False, ValidationSeverity.ERROR,
                        f"MIME type '{mime_type}' not allowed. Allowed: {', '.join(self.allowed_mime_types)}", 
                        field_name, "INVALID_MIME_TYPE",
                        {"mime_type": mime_type, "allowed_mime_types": self.allowed_mime_types}
                    )
                    
            except Exception as e:
                return self._create_result(
                    False, ValidationSeverity.WARNING,
                    f"Could not determine MIME type: {str(e)}", field_name, "MIME_TYPE_UNKNOWN"
                )
        
        return self._create_result(
            True, ValidationSeverity.INFO,
            "Valid file", field_name, "VALID_FILE",
            {
                "file_name": file_name,
                "file_size": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2)
            }
        )


class JSONValidator(BaseValidator):
    """JSON validation with schema support"""    
    def __init__(self, schema: Optional[Dict[str, Any]] = None,
                 max_depth: Optional[int] = None,
                 max_size: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
        self.max_depth = max_depth
        self.max_size = max_size
    
    def validate(self, value: Any, field_name: str = None) -> ValidationResult:
        """Validate JSON data"""        json_data = value
        
        # Parse JSON string if needed
        if isinstance(value, str):
            if self.max_size and len(value) > self.max_size:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"JSON string too large (maximum {self.max_size} characters)", 
                    field_name, "JSON_TOO_LARGE"
                )
            
            try:
                json_data = json.loads(value)
            except json.JSONDecodeError as e:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"Invalid JSON: {str(e)}", field_name, "INVALID_JSON"
                )
        
        # Check depth
        if self.max_depth:
            depth = self._calculate_depth(json_data)
            if depth > self.max_depth:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"JSON depth too high (maximum {self.max_depth})", 
                    field_name, "JSON_TOO_DEEP",
                    {"depth": depth, "max_depth": self.max_depth}
                )
        
        # Validate against schema
        if self.schema:
            try:
                validate(instance=json_data, schema=self.schema, cls=Draft7Validator)
            except ValidationError as e:
                return self._create_result(
                    False, ValidationSeverity.ERROR,
                    f"Schema validation failed: {e.message}", field_name, "SCHEMA_VALIDATION_ERROR",
                    {"schema_path": list(e.absolute_path), "failed_value": e.instance}
                )
        
        return self._create_result(
            True, ValidationSeverity.INFO,
            "Valid JSON", field_name, "VALID_JSON",
            {"type": type(json_data).__name__}
        )
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate JSON depth"""        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


class CompositeValidator:
    """Composite validator that combines multiple validators"""    
    def __init__(self, validators: List[BaseValidator], 
                 mode: str = 'all'):  # 'all', 'any', 'first_valid'
        self.validators = validators
        self.mode = mode
    
    def validate(self, value: Any, field_name: str = None) -> ValidationReport:
        """Validate using multiple validators"""        report = ValidationReport(is_valid=True)
        
        if self.mode == 'all':
            # All validators must pass
            for validator in self.validators:
                result = validator.validate(value, field_name)
                report.add_result(result)
                
        elif self.mode == 'any':
            # At least one validator must pass
            all_failed = True
            for validator in self.validators:
                result = validator.validate(value, field_name)
                report.add_result(result)
                if result.is_valid:
                    all_failed = False
            
            if all_failed:
                report.is_valid = False
                
        elif self.mode == 'first_valid':
            # Use first validator that passes
            for validator in self.validators:
                result = validator.validate(value, field_name)
                report.add_result(result)
                if result.is_valid:
                    break
        
        return report


class DataValidator:
    """Main data validation coordinator"""    
    def __init__(self):
        self.validators = {}
        self.schemas = {}
    
    def register_validator(self, name: str, validator: BaseValidator):
        """Register a named validator"""        self.validators[name] = validator
    
    def register_schema(self, name: str, schema: Dict[str, Any]):
        """Register a validation schema"""        self.schemas[name] = schema
    
    def validate_field(self, value: Any, validator_name: str, 
                      field_name: str = None) -> ValidationResult:
        """Validate a single field"""        if validator_name not in self.validators:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field=field_name,
                message=f"Validator '{validator_name}' not found",
                code="VALIDATOR_NOT_FOUND"
            )
        
        return self.validators[validator_name].validate(value, field_name)
    
    def validate_data(self, data: Dict[str, Any], 
                     schema_name: str) -> ValidationReport:
        """Validate data against a registered schema"""        if schema_name not in self.schemas:
            report = ValidationReport(is_valid=False)
            report.add_result(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Schema '{schema_name}' not found",
                code="SCHEMA_NOT_FOUND"
            ))
            return report
        
        return self.validate_data_with_schema(data, self.schemas[schema_name])
    
    def validate_data_with_schema(self, data: Dict[str, Any], 
                                 schema: Dict[str, Any]) -> ValidationReport:
        """Validate data with provided schema"""        report = ValidationReport(is_valid=True)
        
        # Use Cerberus for comprehensive validation
        validator = CerberusValidator(schema)
        
        if validator.validate(data):
            report.add_result(ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                message="Data validation successful"
            ))
        else:
            report.is_valid = False
            for field, errors in validator.errors.items():
                for error in errors:
                    report.add_result(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        field=field,
                        message=error,
                        code="SCHEMA_VALIDATION_ERROR"
                    ))
        
        return report
    
    def create_user_schema(self) -> Dict[str, Any]:
        """Create a comprehensive user validation schema"""        return {
            'username': {
                'type': 'string',
                'required': True,
                'minlength': 3,
                'maxlength': 30,
                'regex': '^[a-zA-Z0-9_]+$'
            },
            'email': {
                'type': 'string',
                'required': True,
                'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            },
            'password': {
                'type': 'string',
                'required': True,
                'minlength': 8,
                'maxlength': 128
            },
            'age': {
                'type': 'integer',
                'min': 13,
                'max': 120,
                'required': False
            },
            'phone': {
                'type': 'string',
                'required': False,
                'regex': r'^\+?1?\d{9,15}$'
            },
            'country': {
                'type': 'string',
                'required': False,
                'allowed': [country.alpha_2 for country in pycountry.countries]
            },
            'bio': {
                'type': 'string',
                'maxlength': 500,
                'required': False
            },
            'profile_image_url': {
                'type': 'string',
                'regex': r'^https?://.*\.(jpg|jpeg|png|gif)$',
                'required': False
            }
        }
    
    def create_content_schema(self) -> Dict[str, Any]:
        """Create a content validation schema"""        return {
            'title': {
                'type': 'string',
                'required': True,
                'minlength': 1,
                'maxlength': 200
            },
            'description': {
                'type': 'string',
                'required': False,
                'maxlength': 2000
            },
            'content_type': {
                'type': 'string',
                'required': True,
                'allowed': ['audio', 'video', 'image', 'text']
            },
            'tags': {
                'type': 'list',
                'schema': {'type': 'string', 'maxlength': 50},
                'maxlength': 20,
                'required': False
            },
            'visibility': {
                'type': 'string',
                'allowed': ['public', 'private', 'unlisted'],
                'default': 'public'
            },
            'monetization_enabled': {
                'type': 'boolean',
                'default': False
            }
        }


class BusinessRuleValidator:
    """Business logic validation"""    
    def __init__(self):
        self.rules = {}
    
    def register_rule(self, name: str, rule_func: Callable[[Any], bool], 
                     error_message: str):
        """Register a business rule"""        self.rules[name] = {
            'function': rule_func,
            'message': error_message
        }
    
    def validate_business_rules(self, data: Dict[str, Any], 
                               rule_names: List[str]) -> ValidationReport:
        """Validate against business rules"""        report = ValidationReport(is_valid=True)
        
        for rule_name in rule_names:
            if rule_name not in self.rules:
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Business rule '{rule_name}' not found",
                    code="RULE_NOT_FOUND"
                ))
                continue
            
            rule = self.rules[rule_name]
            
            try:
                if not rule['function'](data):
                    report.add_result(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        message=rule['message'],
                        code=f"BUSINESS_RULE_{rule_name.upper()}"
                    ))
            except Exception as e:
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Business rule validation error: {str(e)}",
                    code="BUSINESS_RULE_ERROR"
                ))
        
        return report


class ValidationUtils:
    """Utility functions for validation"""    
    @staticmethod
    def is_valid_uuid(value: str) -> bool:
        """Check if string is a valid UUID"""        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_hex_color(value: str) -> bool:
        """Check if string is a valid hex color"""        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', value))
    
    @staticmethod
    def is_valid_credit_card(value: str) -> bool:
        """Check if string is a valid credit card number (Luhn algorithm)"""        value = re.sub(r'\D', '', value)  # Remove non-digits
        
        if len(value) < 13 or len(value) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = value[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""        # Remove or replace unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def generate_validation_hash(data: Dict[str, Any]) -> str:
        """Generate hash for validation data"""        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()


class ValidationError(Exception):
    """Custom validation exception"""    
    def __init__(self, message: str, field: str = None, 
                 code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.field = field
        self.code = code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'message': str(self),
            'field': self.field,
            'code': self.code,
            'details': self.details
        }
