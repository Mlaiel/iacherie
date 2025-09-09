"""Data Validation Utilities
Enterprise-grade data validation with comprehensive rules and error reporting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import json
import ipaddress
from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass
from datetime import datetime, date
from email.utils import parseaddr
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error"""
    field: str
    value: Any
    message: str
    code: str
    severity: str = "error"


@dataclass
class ValidationResult:
    """Represents validation result"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    cleaned_data: Dict[str, Any]


class DataValidator:
    """
    Enterprise-grade data validation system with built-in rules,
    custom validators, and comprehensive error reporting.
    """
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self.global_rules: List[Callable] = []
        
        # Register built-in validators
        self._register_builtin_validators()
        
        logger.info("DataValidator initialized with built-in validators")
    
    def _register_builtin_validators(self):
        """Register built-in validation functions"""
        self.validators.update({
            "required": self._validate_required,
            "email": self._validate_email,
            "url": self._validate_url,
            "phone": self._validate_phone,
            "ip_address": self._validate_ip_address,
            "uuid": self._validate_uuid,
            "json": self._validate_json,
            "date": self._validate_date,
            "datetime": self._validate_datetime,
            "numeric": self._validate_numeric,
            "string": self._validate_string,
            "list": self._validate_list,
            "dict": self._validate_dict,
            "boolean": self._validate_boolean,
            "regex": self._validate_regex,
            "range": self._validate_range,
            "length": self._validate_length,
            "choice": self._validate_choice,
            "unique": self._validate_unique,
            "credit_card": self._validate_credit_card,
            "password": self._validate_password,
            "alphanumeric": self._validate_alphanumeric,
            "slug": self._validate_slug,
            "hex_color": self._validate_hex_color,
            "base64": self._validate_base64,
            "jwt": self._validate_jwt
        })
    
    def register_validator(self, name: str, validator_func: Callable):
        """Register custom validator function"""
        self.validators[name] = validator_func
        logger.info(f"Registered custom validator: {name}")
    
    def add_global_rule(self, rule_func: Callable):
        """Add global validation rule applied to all data"""
        self.global_rules.append(rule_func)
        logger.info(f"Added global validation rule: {rule_func.__name__}")
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Validation schema with field rules
            
        Returns:
            ValidationResult with errors, warnings, and cleaned data
        """
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Apply global rules first
        for rule in self.global_rules:
            try:
                rule_errors = rule(data)
                if rule_errors:
                    errors.extend(rule_errors)
            except Exception as e:
                logger.error(f"Global rule error: {e}")
                errors.append(ValidationError(
                    field="__global__",
                    value=data,
                    message=f"Global rule failed: {str(e)}",
                    code="global_rule_error"
                ))
        
        # Validate each field according to schema
        for field_name, field_rules in schema.items():
            field_value = data.get(field_name)
            field_errors, field_warnings, cleaned_value = self._validate_field(
                field_name, field_value, field_rules
            )
            
            errors.extend(field_errors)
            warnings.extend(field_warnings)
            
            if not field_errors:
                cleaned_data[field_name] = cleaned_value
        
        # Check for unexpected fields
        unexpected_fields = set(data.keys()) - set(schema.keys())
        for field in unexpected_fields:
            warnings.append(ValidationError(
                field=field,
                value=data[field],
                message=f"Unexpected field '{field}'",
                code="unexpected_field",
                severity="warning"
            ))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def _validate_field(self, field_name: str, value: Any, rules: Union[str, List, Dict]) -> tuple:
        """Validate a single field"""
        errors = []
        warnings = []
        cleaned_value = value
        
        # Normalize rules to list format
        if isinstance(rules, str):
            rules = [rules]
        elif isinstance(rules, dict):
            rules = [rules]
        
        for rule in rules:
            if isinstance(rule, str):
                # Simple validator name
                validator_name = rule
                validator_args = {}
            elif isinstance(rule, dict):
                # Validator with arguments
                validator_name = rule.get("validator", rule.get("type"))
                validator_args = {k: v for k, v in rule.items() if k not in ["validator", "type"]}
            else:
                continue
            
            if validator_name not in self.validators:
                warnings.append(ValidationError(
                    field=field_name,
                    value=value,
                    message=f"Unknown validator '{validator_name}'",
                    code="unknown_validator",
                    severity="warning"
                ))
                continue
            
            try:
                validator_func = self.validators[validator_name]
                result = validator_func(value, **validator_args)
                
                if isinstance(result, tuple):
                    is_valid, error_message, new_value = result
                    if new_value is not None:
                        cleaned_value = new_value
                elif isinstance(result, bool):
                    is_valid = result
                    error_message = f"Validation failed for '{validator_name}'"
                    new_value = None
                else:
                    is_valid = bool(result)
                    error_message = str(result) if not is_valid else None
                    new_value = None
                
                if not is_valid:
                    errors.append(ValidationError(
                        field=field_name,
                        value=value,
                        message=error_message or f"Validation failed for '{validator_name}'",
                        code=validator_name
                    ))
                    
            except Exception as e:
                logger.error(f"Validator '{validator_name}' error: {e}")
                errors.append(ValidationError(
                    field=field_name,
                    value=value,
                    message=f"Validator error: {str(e)}",
                    code="validator_error"
                ))
        
        return errors, warnings, cleaned_value
    
    # Built-in validators
    
    def _validate_required(self, value: Any, **kwargs) -> tuple:
        """Validate required field"""
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return False, "This field is required", None
        return True, None, value
    
    def _validate_email(self, value: Any, **kwargs) -> tuple:
        """Validate email address"""
        if not isinstance(value, str):
            return False, "Email must be a string", None
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, "Invalid email format", None
        
        # Additional validation using email.utils
        try:
            parsed = parseaddr(value)
            if not parsed[1] or '@' not in parsed[1]:
                return False, "Invalid email format", None
        except:
            return False, "Invalid email format", None
        
        return True, None, value.lower()
    
    def _validate_url(self, value: Any, **kwargs) -> tuple:
        """Validate URL"""
        if not isinstance(value, str):
            return False, "URL must be a string", None
        
        url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if not re.match(url_pattern, value):
            return False, "Invalid URL format", None
        
        return True, None, value
    
    def _validate_phone(self, value: Any, **kwargs) -> tuple:
        """Validate phone number"""
        if not isinstance(value, str):
            return False, "Phone must be a string", None
        
        # Remove common separators
        phone = re.sub(r'[^\d+]', '', value)
        
        # Basic phone validation (10-15 digits, optional +)
        if not re.match(r'^\+?[\d]{10,15}$', phone):
            return False, "Invalid phone number format", None
        
        return True, None, phone
    
    def _validate_ip_address(self, value: Any, **kwargs) -> tuple:
        """Validate IP address (IPv4 or IPv6)"""
        if not isinstance(value, str):
            return False, "IP address must be a string", None
        
        try:
            ipaddress.ip_address(value)
            return True, None, value
        except ValueError:
            return False, "Invalid IP address format", None
    
    def _validate_uuid(self, value: Any, **kwargs) -> tuple:
        """Validate UUID"""
        if not isinstance(value, str):
            return False, "UUID must be a string", None
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, value.lower()):
            return False, "Invalid UUID format", None
        
        return True, None, value.lower()
    
    def _validate_json(self, value: Any, **kwargs) -> tuple:
        """Validate JSON string"""
        if not isinstance(value, str):
            return False, "JSON must be a string", None
        
        try:
            parsed = json.loads(value)
            return True, None, parsed
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}", None
    
    def _validate_date(self, value: Any, format: str = "%Y-%m-%d", **kwargs) -> tuple:
        """Validate date string"""
        if isinstance(value, date):
            return True, None, value
        
        if not isinstance(value, str):
            return False, "Date must be a string", None
        
        try:
            parsed_date = datetime.strptime(value, format).date()
            return True, None, parsed_date
        except ValueError:
            return False, f"Invalid date format (expected: {format})", None
    
    def _validate_datetime(self, value: Any, format: str = "%Y-%m-%d %H:%M:%S", **kwargs) -> tuple:
        """Validate datetime string"""
        if isinstance(value, datetime):
            return True, None, value
        
        if not isinstance(value, str):
            return False, "Datetime must be a string", None
        
        try:
            parsed_datetime = datetime.strptime(value, format)
            return True, None, parsed_datetime
        except ValueError:
            return False, f"Invalid datetime format (expected: {format})", None
    
    def _validate_numeric(self, value: Any, **kwargs) -> tuple:
        """Validate numeric value"""
        try:
            if isinstance(value, (int, float)):
                return True, None, value
            elif isinstance(value, str):
                # Try to convert string to number
                if '.' in value:
                    converted = float(value)
                else:
                    converted = int(value)
                return True, None, converted
            else:
                return False, "Value must be numeric", None
        except (ValueError, TypeError):
            return False, "Value must be numeric", None
    
    def _validate_string(self, value: Any, **kwargs) -> tuple:
        """Validate string value"""
        if not isinstance(value, str):
            return False, "Value must be a string", None
        return True, None, value
    
    def _validate_list(self, value: Any, **kwargs) -> tuple:
        """Validate list value"""
        if not isinstance(value, list):
            return False, "Value must be a list", None
        return True, None, value
    
    def _validate_dict(self, value: Any, **kwargs) -> tuple:
        """Validate dictionary value"""
        if not isinstance(value, dict):
            return False, "Value must be a dictionary", None
        return True, None, value
    
    def _validate_boolean(self, value: Any, **kwargs) -> tuple:
        """Validate boolean value"""
        if isinstance(value, bool):
            return True, None, value
        elif isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True, None, True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return True, None, False
            else:
                return False, "Invalid boolean value", None
        elif isinstance(value, (int, float)):
            return True, None, bool(value)
        else:
            return False, "Value must be boolean", None
    
    def _validate_regex(self, value: Any, pattern: str, **kwargs) -> tuple:
        """Validate against regex pattern"""
        if not isinstance(value, str):
            return False, "Value must be a string for regex validation", None
        
        try:
            if not re.match(pattern, value):
                return False, f"Value does not match pattern: {pattern}", None
            return True, None, value
        except re.error as e:
            return False, f"Invalid regex pattern: {e}", None
    
    def _validate_range(self, value: Any, min_val: float = None, max_val: float = None, **kwargs) -> tuple:
        """Validate numeric range"""
        try:
            num_value = float(value)
            
            if min_val is not None and num_value < min_val:
                return False, f"Value must be at least {min_val}", None
            
            if max_val is not None and num_value > max_val:
                return False, f"Value must be at most {max_val}", None
            
            return True, None, num_value
        except (ValueError, TypeError):
            return False, "Value must be numeric for range validation", None
    
    def _validate_length(self, value: Any, min_len: int = None, max_len: int = None, **kwargs) -> tuple:
        """Validate length of string, list, or dict"""
        try:
            length = len(value)
            
            if min_len is not None and length < min_len:
                return False, f"Length must be at least {min_len}", None
            
            if max_len is not None and length > max_len:
                return False, f"Length must be at most {max_len}", None
            
            return True, None, value
        except TypeError:
            return False, "Value must have length for length validation", None
    
    def _validate_choice(self, value: Any, choices: List[Any], **kwargs) -> tuple:
        """Validate value is in allowed choices"""
        if value not in choices:
            return False, f"Value must be one of: {choices}", None
        return True, None, value
    
    def _validate_unique(self, value: Any, existing_values: List[Any] = None, **kwargs) -> tuple:
        """Validate value is unique"""
        if existing_values and value in existing_values:
            return False, "Value must be unique", None
        return True, None, value
    
    def _validate_credit_card(self, value: Any, **kwargs) -> tuple:
        """Validate credit card number using Luhn algorithm"""
        if not isinstance(value, str):
            return False, "Credit card must be a string", None
        
        # Remove spaces and dashes
        card_number = re.sub(r'[^\d]', '', value)
        
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False, "Invalid credit card format", None
        
        # Luhn algorithm
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0
        
        if not luhn_check(card_number):
            return False, "Invalid credit card number", None
        
        return True, None, card_number
    
    def _validate_password(self, value: Any, min_length: int = 8, require_uppercase: bool = True,
                          require_lowercase: bool = True, require_digit: bool = True,
                          require_special: bool = True, **kwargs) -> tuple:
        """Validate password strength"""
        if not isinstance(value, str):
            return False, "Password must be a string", None
        
        errors = []
        
        if len(value) < min_length:
            errors.append(f"at least {min_length} characters")
        
        if require_uppercase and not re.search(r'[A-Z]', value):
            errors.append("at least one uppercase letter")
        
        if require_lowercase and not re.search(r'[a-z]', value):
            errors.append("at least one lowercase letter")
        
        if require_digit and not re.search(r'\d', value):
            errors.append("at least one digit")
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("at least one special character")
        
        if errors:
            return False, f"Password must contain {', '.join(errors)}", None
        
        return True, None, value
    
    def _validate_alphanumeric(self, value: Any, **kwargs) -> tuple:
        """Validate alphanumeric string"""
        if not isinstance(value, str):
            return False, "Value must be a string", None
        
        if not value.isalnum():
            return False, "Value must contain only letters and numbers", None
        
        return True, None, value
    
    def _validate_slug(self, value: Any, **kwargs) -> tuple:
        """Validate URL slug format"""
        if not isinstance(value, str):
            return False, "Slug must be a string", None
        
        slug_pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
        if not re.match(slug_pattern, value):
            return False, "Invalid slug format (use lowercase letters, numbers, and hyphens)", None
        
        return True, None, value
    
    def _validate_hex_color(self, value: Any, **kwargs) -> tuple:
        """Validate hex color code"""
        if not isinstance(value, str):
            return False, "Hex color must be a string", None
        
        hex_pattern = r'^#?[0-9a-fA-F]{6}$'
        if not re.match(hex_pattern, value):
            return False, "Invalid hex color format", None
        
        # Ensure it starts with #
        normalized = value if value.startswith('#') else f'#{value}'
        return True, None, normalized.upper()
    
    def _validate_base64(self, value: Any, **kwargs) -> tuple:
        """Validate base64 encoded string"""
        if not isinstance(value, str):
            return False, "Base64 must be a string", None
        
        try:
            import base64
            # Try to decode
            base64.b64decode(value, validate=True)
            return True, None, value
        except Exception:
            return False, "Invalid base64 encoding", None
    
    def _validate_jwt(self, value: Any, **kwargs) -> tuple:
        """Validate JWT token format"""
        if not isinstance(value, str):
            return False, "JWT must be a string", None
        
        parts = value.split('.')
        if len(parts) != 3:
            return False, "Invalid JWT format (must have 3 parts)", None
        
        # Basic validation of base64url encoding
        import base64
        try:
            for part in parts:
                # Add padding if needed
                padded = part + '=' * (4 - len(part) % 4)
                base64.urlsafe_b64decode(padded)
            return True, None, value
        except Exception:
            return False, "Invalid JWT encoding", None


# Global validator instance
_global_validator: Optional[DataValidator] = None


def get_global_validator() -> DataValidator:
    """Get global data validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = DataValidator()
    return _global_validator


def validate_data(data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    """Quick validation using global validator"""
    return get_global_validator().validate(data, schema)