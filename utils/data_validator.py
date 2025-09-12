"""
Data Validation Utilities - Enterprise Grade
===========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: Lead Dev IA + Backend Senior + Security Expert
Provides comprehensive data validation for enterprise applications.
"""

import re
import json
import uuid
import logging
from typing import Any, Dict, List, Optional, Union, Callable, Type
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, ValidationError
import phonenumbers
from phonenumbers import carrier, geocoder, timezone


class ValidationResult:
    """Validation result container with detailed feedback."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now()
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'timestamp': self.timestamp.isoformat()
        }


class DataValidator:
    """
    Enterprise-grade data validation utility.
    
    Features:
    - Input validation and sanitization
    - Format validation (email, phone, URLs)
    - Schema validation with Pydantic
    - Custom validation rules
    - Security-focused validation
    - Multi-language support
    """
    
    def __init__(self, strict_mode: bool = True, custom_rules: Dict[str, Callable] = None):
        self.strict_mode = strict_mode
        self.custom_rules = custom_rules or {}
        self.logger = logging.getLogger(__name__)
        
        # Common regex patterns
        self.patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'phone': re.compile(r'^\+?1?-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'),
            'url': re.compile(r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
            'ipv4': re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
            'credit_card': re.compile(r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$'),
            'username': re.compile(r'^[a-zA-Z0-9_]{3,30}$'),
            'password_strong': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        }
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address with comprehensive checks."""
        result = ValidationResult(True)
        
        if not email or not isinstance(email, str):
            result.add_error("Email is required and must be a string")
            return result
        
        # Basic format validation
        if not self.patterns['email'].match(email):
            result.add_error("Invalid email format")
            return result
        
        # Advanced validation using email-validator
        try:
            validation = validate_email(email)
            email = validation.email
        except EmailNotValidError as e:
            result.add_error(f"Email validation failed: {str(e)}")
            return result
        
        # Additional security checks
        if len(email) > 254:
            result.add_error("Email address too long")
        
        # Check for suspicious patterns
        suspicious_patterns = ['+', 'test', 'temp', 'fake', 'example']
        for pattern in suspicious_patterns:
            if pattern in email.lower():
                result.add_warning(f"Email contains suspicious pattern: {pattern}")
        
        return result
    
    def validate_phone(self, phone: str, region: str = "US") -> ValidationResult:
        """Validate phone number with international support."""
        result = ValidationResult(True)
        
        if not phone or not isinstance(phone, str):
            result.add_error("Phone number is required and must be a string")
            return result
        
        try:
            parsed_number = phonenumbers.parse(phone, region)
            
            if not phonenumbers.is_valid_number(parsed_number):
                result.add_error("Invalid phone number")
                return result
            
            # Additional info
            carrier_name = carrier.name_for_number(parsed_number, "en")
            location = geocoder.description_for_number(parsed_number, "en")
            timezones = timezone.time_zones_for_number(parsed_number)
            
            if carrier_name:
                result.add_warning(f"Carrier: {carrier_name}")
            if location:
                result.add_warning(f"Location: {location}")
                
        except phonenumbers.NumberParseException as e:
            result.add_error(f"Phone parsing failed: {str(e)}")
        
        return result
    
    def validate_url(self, url: str, allow_http: bool = False) -> ValidationResult:
        """Validate URL with security considerations."""
        result = ValidationResult(True)
        
        if not url or not isinstance(url, str):
            result.add_error("URL is required and must be a string")
            return result
        
        if not self.patterns['url'].match(url):
            result.add_error("Invalid URL format")
            return result
        
        # Security checks
        if not allow_http and url.startswith('http://'):
            result.add_error("HTTP URLs not allowed, use HTTPS")
        
        # Check for suspicious domains
        suspicious_domains = ['bit.ly', 'tinyurl.com', 'goo.gl']
        for domain in suspicious_domains:
            if domain in url.lower():
                result.add_warning(f"URL contains suspicious domain: {domain}")
        
        # Check URL length
        if len(url) > 2048:
            result.add_error("URL too long")
        
        return result
    
    def validate_password(self, password: str, min_length: int = 8) -> ValidationResult:
        """Validate password strength with security requirements."""
        result = ValidationResult(True)
        
        if not password or not isinstance(password, str):
            result.add_error("Password is required and must be a string")
            return result
        
        # Length check
        if len(password) < min_length:
            result.add_error(f"Password must be at least {min_length} characters")
        
        # Complexity checks
        if not re.search(r'[a-z]', password):
            result.add_error("Password must contain lowercase letters")
        
        if not re.search(r'[A-Z]', password):
            result.add_error("Password must contain uppercase letters")
        
        if not re.search(r'\d', password):
            result.add_error("Password must contain numbers")
        
        if not re.search(r'[@$!%*?&]', password):
            result.add_error("Password must contain special characters")
        
        # Common password checks
        common_passwords = ['password', '123456', 'admin', 'user']
        if password.lower() in common_passwords:
            result.add_error("Password is too common")
        
        # Entropy check
        unique_chars = len(set(password))
        if unique_chars < len(password) * 0.6:
            result.add_warning("Password has low character diversity")
        
        return result
    
    def validate_json(self, json_str: str, schema: Dict[str, Any] = None) -> ValidationResult:
        """Validate JSON string and optional schema."""
        result = ValidationResult(True)
        
        if not json_str or not isinstance(json_str, str):
            result.add_error("JSON is required and must be a string")
            return result
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {str(e)}")
            return result
        
        # Schema validation if provided
        if schema:
            try:
                # Simple schema validation (can be extended with jsonschema)
                self._validate_schema(data, schema, result)
            except Exception as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    def validate_model(self, data: Dict[str, Any], model_class: Type[BaseModel]) -> ValidationResult:
        """Validate data against Pydantic model."""
        result = ValidationResult(True)
        
        if not isinstance(data, dict):
            result.add_error("Data must be a dictionary")
            return result
        
        try:
            model_class(**data)
        except ValidationError as e:
            for error in e.errors():
                field = ' -> '.join(str(loc) for loc in error['loc'])
                result.add_error(f"Field '{field}': {error['msg']}")
        except Exception as e:
            result.add_error(f"Model validation failed: {str(e)}")
        
        return result
    
    def validate_file_upload(self, file_data: Dict[str, Any], max_size: int = 10 * 1024 * 1024) -> ValidationResult:
        """Validate file upload data."""
        result = ValidationResult(True)
        
        required_fields = ['filename', 'content_type', 'size']
        for field in required_fields:
            if field not in file_data:
                result.add_error(f"Missing required field: {field}")
        
        if result.errors:
            return result
        
        # Size validation
        if file_data['size'] > max_size:
            result.add_error(f"File size exceeds limit of {max_size} bytes")
        
        # Content type validation
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'audio/mpeg', 'audio/wav', 'audio/ogg',
            'video/mp4', 'video/avi', 'video/mov',
            'application/pdf', 'text/plain'
        ]
        
        if file_data['content_type'] not in allowed_types:
            result.add_error(f"File type not allowed: {file_data['content_type']}")
        
        # Filename validation
        filename = file_data['filename']
        if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
            result.add_error("Filename contains invalid characters")
        
        if len(filename) > 255:
            result.add_error("Filename too long")
        
        return result
    
    def validate_custom(self, data: Any, rule_name: str) -> ValidationResult:
        """Validate using custom rule."""
        result = ValidationResult(True)
        
        if rule_name not in self.custom_rules:
            result.add_error(f"Custom rule '{rule_name}' not found")
            return result
        
        try:
            rule_result = self.custom_rules[rule_name](data)
            if isinstance(rule_result, ValidationResult):
                return rule_result
            elif isinstance(rule_result, bool):
                if not rule_result:
                    result.add_error(f"Custom validation '{rule_name}' failed")
            else:
                result.add_error(f"Invalid custom rule return type")
        except Exception as e:
            result.add_error(f"Custom rule execution failed: {str(e)}")
        
        return result
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any], result: ValidationResult):
        """Simple schema validation helper."""
        if 'type' in schema:
            expected_type = schema['type']
            if expected_type == 'string' and not isinstance(data, str):
                result.add_error(f"Expected string, got {type(data).__name__}")
            elif expected_type == 'number' and not isinstance(data, (int, float)):
                result.add_error(f"Expected number, got {type(data).__name__}")
            elif expected_type == 'boolean' and not isinstance(data, bool):
                result.add_error(f"Expected boolean, got {type(data).__name__}")
            elif expected_type == 'array' and not isinstance(data, list):
                result.add_error(f"Expected array, got {type(data).__name__}")
            elif expected_type == 'object' and not isinstance(data, dict):
                result.add_error(f"Expected object, got {type(data).__name__}")
        
        if 'required' in schema and isinstance(data, dict):
            for field in schema['required']:
                if field not in data:
                    result.add_error(f"Required field missing: {field}")
    
    def bulk_validate(self, data_list: List[Dict[str, Any]], validation_rules: Dict[str, str]) -> Dict[str, ValidationResult]:
        """Validate multiple data items."""
        results = {}
        
        for i, data in enumerate(data_list):
            item_result = ValidationResult(True)
            
            for field, rule_type in validation_rules.items():
                if field not in data:
                    item_result.add_error(f"Missing field: {field}")
                    continue
                
                field_value = data[field]
                
                if rule_type == 'email':
                    field_result = self.validate_email(field_value)
                elif rule_type == 'phone':
                    field_result = self.validate_phone(field_value)
                elif rule_type == 'url':
                    field_result = self.validate_url(field_value)
                elif rule_type == 'password':
                    field_result = self.validate_password(field_value)
                else:
                    field_result = ValidationResult(True)
                    field_result.add_warning(f"Unknown validation rule: {rule_type}")
                
                if not field_result.is_valid:
                    item_result.errors.extend([f"{field}: {error}" for error in field_result.errors])
                
                item_result.warnings.extend([f"{field}: {warning}" for warning in field_result.warnings])
            
            results[f"item_{i}"] = item_result
        
        return results


# Convenience functions for common validations
def validate_email(email: str) -> bool:
    """Quick email validation."""
    validator = DataValidator()
    return validator.validate_email(email).is_valid


def validate_phone(phone: str, region: str = "US") -> bool:
    """Quick phone validation."""
    validator = DataValidator()
    return validator.validate_phone(phone, region).is_valid


def validate_password_strength(password: str) -> bool:
    """Quick password strength validation."""
    validator = DataValidator()
    return validator.validate_password(password).is_valid


def validate_url_safe(url: str) -> bool:
    """Quick URL safety validation."""
    validator = DataValidator()
    return validator.validate_url(url).is_valid


def validate_json_format(json_str: str) -> bool:
    """Quick JSON format validation."""
    validator = DataValidator()
    return validator.validate_json(json_str).is_valid


# Example usage and test cases
if __name__ == "__main__":
    validator = DataValidator()
    
    # Test email validation
    email_result = validator.validate_email("test@example.com")
    print(f"Email validation: {email_result.to_dict()}")
    
    # Test phone validation
    phone_result = validator.validate_phone("+1-555-123-4567")
    print(f"Phone validation: {phone_result.to_dict()}")
    
    # Test password validation
    password_result = validator.validate_password("SecurePass123!")
    print(f"Password validation: {password_result.to_dict()}")
    
    # Test URL validation
    url_result = validator.validate_url("https://example.com/api/endpoint")
    print(f"URL validation: {url_result.to_dict()}")
    
    # Test bulk validation
    test_data = [
        {"email": "user1@test.com", "phone": "+1-555-111-2222"},
        {"email": "invalid-email", "phone": "555-333-4444"}
    ]
    
    bulk_results = validator.bulk_validate(test_data, {"email": "email", "phone": "phone"})
    for key, result in bulk_results.items():
        print(f"{key}: {result.to_dict()}")