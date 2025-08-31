"""Professional validation utilities for IA Influencer Agent.
Enterprise-grade validators with comprehensive business rule enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import re
import validators
from email_validator import validate_email, EmailNotValidError


class ValidationType(Enum):
    """Types of validation for categorization."""    CONTENT = "content"
    USER = "user"
    BUSINESS = "business"
    SYSTEM = "system"
    SECURITY = "security"


@dataclass
class ValidationResult:
    """Result of validation with detailed feedback."""    is_valid: bool
    field_name: str
    value: Any
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class ValidationError(Exception):
    """Custom validation error with structured information."""    
    def __init__(self, results: List[ValidationResult]):
        self.results = results
        self.errors = [r for r in results if not r.is_valid]
        
        if self.errors:
            message = f"Validation failed for {len(self.errors)} field(s): " + \
                     ", ".join([f"{e.field_name}: {e.error_message}" for e in self.errors])
        else:
            message = "Validation completed successfully"
        
        super().__init__(message)


class ContentValidator:
    """Validators for content-related business rules."""    
    @staticmethod
    def validate_content_type(content_type: str) -> ValidationResult:
        """Validate content type against supported formats."""        allowed_types = {
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
            'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
            'text': ['txt', 'md', 'doc', 'docx', 'pdf', 'rtf']
        }
        
        # Extract main type and subtype
        if '/' not in content_type:
            return ValidationResult(
                is_valid=False,
                field_name="content_type",
                value=content_type,
                error_message="Content type must be in format 'type/subtype'",
                error_code="INVALID_FORMAT"
            )
        
        main_type, sub_type = content_type.split('/', 1)
        
        if main_type not in allowed_types:
            return ValidationResult(
                is_valid=False,
                field_name="content_type",
                value=content_type,
                error_message=f"Unsupported content type: {main_type}",
                error_code="UNSUPPORTED_TYPE",
                suggestions=list(allowed_types.keys())
            )
        
        # Check file extension for specific validation
        if sub_type not in allowed_types[main_type]:
            return ValidationResult(
                is_valid=False,
                field_name="content_type",
                value=content_type,
                error_message=f"Unsupported {main_type} format: {sub_type}",
                error_code="UNSUPPORTED_FORMAT",
                suggestions=allowed_types[main_type]
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="content_type",
            value=content_type
        )
    
    @staticmethod
    def validate_file_size(file_size: int, content_type: str) -> ValidationResult:
        """Validate file size against business limits."""        # Size limits in bytes by content type
        size_limits = {
            'audio': 100 * 1024 * 1024,  # 100MB
            'video': 500 * 1024 * 1024,  # 500MB
            'image': 20 * 1024 * 1024,   # 20MB
            'text': 10 * 1024 * 1024     # 10MB
        }
        
        main_type = content_type.split('/')[0] if '/' in content_type else content_type
        max_size = size_limits.get(main_type, 50 * 1024 * 1024)  # 50MB default
        
        if file_size <= 0:
            return ValidationResult(
                is_valid=False,
                field_name="file_size",
                value=file_size,
                error_message="File size must be greater than 0",
                error_code="INVALID_SIZE"
            )
        
        if file_size > max_size:
            return ValidationResult(
                is_valid=False,
                field_name="file_size",
                value=file_size,
                error_message=f"File size {file_size} bytes exceeds limit of {max_size} bytes",
                error_code="SIZE_EXCEEDED",
                suggestions=[f"Maximum allowed size: {max_size // (1024*1024)}MB"]
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="file_size",
            value=file_size
        )
    
    @staticmethod
    def validate_content_title(title: str) -> ValidationResult:
        """Validate content title for business requirements."""        if not title or not title.strip():
            return ValidationResult(
                is_valid=False,
                field_name="title",
                value=title,
                error_message="Title cannot be empty",
                error_code="REQUIRED_FIELD"
            )
        
        title = title.strip()
        
        if len(title) < 3:
            return ValidationResult(
                is_valid=False,
                field_name="title",
                value=title,
                error_message="Title must be at least 3 characters long",
                error_code="TOO_SHORT"
            )
        
        if len(title) > 200:
            return ValidationResult(
                is_valid=False,
                field_name="title",
                value=title,
                error_message="Title cannot exceed 200 characters",
                error_code="TOO_LONG"
            )
        
        # Check for prohibited characters
        prohibited_chars = ['<', '>', '&', '"', "'", '\x00']
        for char in prohibited_chars:
            if char in title:
                return ValidationResult(
                    is_valid=False,
                    field_name="title",
                    value=title,
                    error_message=f"Title contains prohibited character: {char}",
                    error_code="INVALID_CHARACTER"
                )
        
        return ValidationResult(
            is_valid=True,
            field_name="title",
            value=title
        )


class UserValidator:
    """Validators for user-related data."""    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email address with comprehensive checks."""        if not email:
            return ValidationResult(
                is_valid=False,
                field_name="email",
                value=email,
                error_message="Email address is required",
                error_code="REQUIRED_FIELD"
            )
        
        try:
            # Use email-validator library for comprehensive validation
            validated_email = validate_email(email)
            normalized_email = validated_email.email
            
            return ValidationResult(
                is_valid=True,
                field_name="email",
                value=normalized_email
            )
        
        except EmailNotValidError as e:
            return ValidationResult(
                is_valid=False,
                field_name="email",
                value=email,
                error_message=str(e),
                error_code="INVALID_EMAIL"
            )
    
    @staticmethod
    def validate_username(username: str) -> ValidationResult:
        """Validate username according to business rules."""        if not username:
            return ValidationResult(
                is_valid=False,
                field_name="username",
                value=username,
                error_message="Username is required",
                error_code="REQUIRED_FIELD"
            )
        
        # Length validation
        if len(username) < 3:
            return ValidationResult(
                is_valid=False,
                field_name="username",
                value=username,
                error_message="Username must be at least 3 characters long",
                error_code="TOO_SHORT"
            )
        
        if len(username) > 50:
            return ValidationResult(
                is_valid=False,
                field_name="username",
                value=username,
                error_message="Username cannot exceed 50 characters",
                error_code="TOO_LONG"
            )
        
        # Character validation
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return ValidationResult(
                is_valid=False,
                field_name="username",
                value=username,
                error_message="Username can only contain letters, numbers, dots, hyphens, and underscores",
                error_code="INVALID_CHARACTER"
            )
        
        # Reserved usernames
        reserved_usernames = {
            'admin', 'administrator', 'root', 'system', 'api', 'www',
            'mail', 'support', 'help', 'info', 'contact', 'service',
            'noreply', 'no-reply', 'postmaster', 'hostmaster'
        }
        
        if username.lower() in reserved_usernames:
            return ValidationResult(
                is_valid=False,
                field_name="username",
                value=username,
                error_message="This username is reserved and cannot be used",
                error_code="RESERVED_USERNAME"
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="username",
            value=username
        )
    
    @staticmethod
    def validate_password_strength(password: str) -> ValidationResult:
        """Validate password strength according to security policies."""        if not password:
            return ValidationResult(
                is_valid=False,
                field_name="password",
                value="[REDACTED]",
                error_message="Password is required",
                error_code="REQUIRED_FIELD"
            )
        
        # Length requirement
        if len(password) < 8:
            return ValidationResult(
                is_valid=False,
                field_name="password",
                value="[REDACTED]",
                error_message="Password must be at least 8 characters long",
                error_code="TOO_SHORT",
                suggestions=["Use at least 8 characters"]
            )
        
        if len(password) > 128:
            return ValidationResult(
                is_valid=False,
                field_name="password",
                value="[REDACTED]",
                error_message="Password cannot exceed 128 characters",
                error_code="TOO_LONG"
            )
        
        # Character complexity requirements
        has_lower = re.search(r'[a-z]', password) is not None
        has_upper = re.search(r'[A-Z]', password) is not None
        has_digit = re.search(r'\d', password) is not None
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None
        
        missing_requirements = []
        if not has_lower:
            missing_requirements.append("at least one lowercase letter")
        if not has_upper:
            missing_requirements.append("at least one uppercase letter")
        if not has_digit:
            missing_requirements.append("at least one number")
        if not has_special:
            missing_requirements.append("at least one special character")
        
        if missing_requirements:
            return ValidationResult(
                is_valid=False,
                field_name="password",
                value="[REDACTED]",
                error_message="Password does not meet complexity requirements",
                error_code="INSUFFICIENT_COMPLEXITY",
                suggestions=missing_requirements
            )
        
        # Common password checks
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        }
        
        if password.lower() in common_passwords:
            return ValidationResult(
                is_valid=False,
                field_name="password",
                value="[REDACTED]",
                error_message="Password is too common and easily guessable",
                error_code="COMMON_PASSWORD",
                suggestions=["Use a unique, hard-to-guess password"]
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="password",
            value="[REDACTED]"
        )


class BusinessValidator:
    """Validators for business logic rules."""    
    @staticmethod
    def validate_revenue_amount(amount: float, currency: str = "EUR") -> ValidationResult:
        """Validate revenue amount for business processing."""        if amount is None:
            return ValidationResult(
                is_valid=False,
                field_name="amount",
                value=amount,
                error_message="Revenue amount is required",
                error_code="REQUIRED_FIELD"
            )
        
        if amount < 0:
            return ValidationResult(
                is_valid=False,
                field_name="amount",
                value=amount,
                error_message="Revenue amount cannot be negative",
                error_code="NEGATIVE_VALUE"
            )
        
        # Maximum reasonable amount (anti-fraud)
        max_amount = 1000000.00  # 1 million in any currency
        if amount > max_amount:
            return ValidationResult(
                is_valid=False,
                field_name="amount",
                value=amount,
                error_message=f"Revenue amount {amount} exceeds maximum allowed {max_amount}",
                error_code="AMOUNT_EXCEEDED",
                suggestions=["Contact support for large transactions"]
            )
        
        # Precision validation (2 decimal places for most currencies)
        if round(amount, 2) != amount:
            return ValidationResult(
                is_valid=False,
                field_name="amount",
                value=amount,
                error_message="Revenue amount cannot have more than 2 decimal places",
                error_code="INVALID_PRECISION"
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="amount",
            value=amount
        )
    
    @staticmethod
    def validate_platform_name(platform: str) -> ValidationResult:
        """Validate platform name against supported platforms."""        supported_platforms = {
            'youtube', 'instagram', 'tiktok', 'facebook', 'twitter',
            'spotify', 'soundcloud', 'bandcamp', 'linkedin', 'pinterest'
        }
        
        if not platform:
            return ValidationResult(
                is_valid=False,
                field_name="platform",
                value=platform,
                error_message="Platform name is required",
                error_code="REQUIRED_FIELD"
            )
        
        platform_lower = platform.lower()
        
        if platform_lower not in supported_platforms:
            return ValidationResult(
                is_valid=False,
                field_name="platform",
                value=platform,
                error_message=f"Unsupported platform: {platform}",
                error_code="UNSUPPORTED_PLATFORM",
                suggestions=list(supported_platforms)
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="platform",
            value=platform_lower
        )


class SecurityValidator:
    """Validators for security-related requirements."""    
    @staticmethod
    def validate_api_key(api_key: str) -> ValidationResult:
        """Validate API key format and structure."""        if not api_key:
            return ValidationResult(
                is_valid=False,
                field_name="api_key",
                value="[REDACTED]",
                error_message="API key is required",
                error_code="REQUIRED_FIELD"
            )
        
        # Expected format: prefix + 32 hex characters
        if not re.match(r'^[a-zA-Z0-9_-]{8,64}$', api_key):
            return ValidationResult(
                is_valid=False,
                field_name="api_key",
                value="[REDACTED]",
                error_message="API key format is invalid",
                error_code="INVALID_FORMAT"
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="api_key",
            value="[REDACTED]"
        )
    
    @staticmethod
    def validate_url_safety(url: str) -> ValidationResult:
        """Validate URL for security and format compliance."""        if not url:
            return ValidationResult(
                is_valid=False,
                field_name="url",
                value=url,
                error_message="URL is required",
                error_code="REQUIRED_FIELD"
            )
        
        # Basic URL format validation
        if not validators.url(url):
            return ValidationResult(
                is_valid=False,
                field_name="url",
                value=url,
                error_message="URL format is invalid",
                error_code="INVALID_FORMAT"
            )
        
        # Security checks
        url_lower = url.lower()
        
        # Block dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'file:', 'ftp:']
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return ValidationResult(
                    is_valid=False,
                    field_name="url",
                    value=url,
                    error_message=f"Unsafe protocol detected: {protocol}",
                    error_code="UNSAFE_PROTOCOL"
                )
        
        # Block localhost and internal IPs (basic check)
        if any(term in url_lower for term in ['localhost', '127.0.0.1', '0.0.0.0']):
            return ValidationResult(
                is_valid=False,
                field_name="url",
                value=url,
                error_message="Internal/localhost URLs are not allowed",
                error_code="INTERNAL_URL"
            )
        
        return ValidationResult(
            is_valid=True,
            field_name="url",
            value=url
        )


class CompoundValidator:
    """Validator that combines multiple validation rules."""    
    def __init__(self):
        self.content_validator = ContentValidator()
        self.user_validator = UserValidator()
        self.business_validator = BusinessValidator()
        self.security_validator = SecurityValidator()
    
    def validate_content_upload(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate complete content upload data."""        results = []
        
        # Validate required fields
        if 'title' in data:
            results.append(self.content_validator.validate_content_title(data['title']))
        
        if 'content_type' in data:
            results.append(self.content_validator.validate_content_type(data['content_type']))
        
        if 'file_size' in data and 'content_type' in data:
            results.append(self.content_validator.validate_file_size(
                data['file_size'], 
                data['content_type']
            ))
        
        return results
    
    def validate_user_registration(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate user registration data."""        results = []
        
        if 'email' in data:
            results.append(self.user_validator.validate_email(data['email']))
        
        if 'username' in data:
            results.append(self.user_validator.validate_username(data['username']))
        
        if 'password' in data:
            results.append(self.user_validator.validate_password_strength(data['password']))
        
        return results
    
    def validate_and_raise(self, validation_func: Callable, *args, **kwargs):
        """Validate and raise ValidationError if any validation fails."""        results = validation_func(*args, **kwargs)
        
        if not isinstance(results, list):
            results = [results]
        
        failed_validations = [r for r in results if not r.is_valid]
        
        if failed_validations:
            raise ValidationError(results)
        
        return results


# Global validator instance
_validator = CompoundValidator()


def get_validator() -> CompoundValidator:
    """Get global validator instance."""    return _validator


def validate_content_upload(data: Dict[str, Any]) -> List[ValidationResult]:
    """Validate content upload data using global validator."""    return _validator.validate_content_upload(data)


def validate_user_registration(data: Dict[str, Any]) -> List[ValidationResult]:
    """Validate user registration data using global validator."""    return _validator.validate_user_registration(data)
