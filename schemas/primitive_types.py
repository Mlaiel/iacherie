"""
🔧 Enhanced Primitive Type Definitions
Enterprise-grade primitive data types with advanced validation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

🎯 Backend Senior + DBA Expert Role: Advanced type system and validation
"""

from datetime import datetime, date, time, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union, Pattern, Type
from uuid import UUID
from enum import Enum
import re
from pydantic import BaseModel, Field, validator, root_validator, EmailStr
from pydantic.types import StrictStr, StrictInt, StrictFloat, StrictBool
import phonenumbers
from phonenumbers import NumberParseException
import ipaddress


class StringFormat(str, Enum):
    """Enhanced string format types"""
    EMAIL = "email"
    URI = "uri"
    URL = "url"
    UUID = "uuid"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    PASSWORD = "password"
    PHONE = "phone"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    SLUG = "slug"
    USERNAME = "username"
    CURRENCY = "currency"
    COUNTRY_CODE = "country_code"
    LANGUAGE_CODE = "language_code"
    TIMEZONE = "timezone"
    HEX_COLOR = "hex_color"
    BASE64 = "base64"
    JWT = "jwt"
    SEMVER = "semver"


class NumericFormat(str, Enum):
    """Numeric format types"""
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    CURRENCY_AMOUNT = "currency_amount"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    RATING = "rating"
    COUNT = "count"
    BYTES = "bytes"


class SecurityLevel(str, Enum):
    """Security classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


class EnhancedString(BaseModel):
    """Enhanced string type with format validation and metadata"""
    value: str = Field(description="String value")
    format: Optional[StringFormat] = Field(None, description="String format constraint")
    min_length: Optional[int] = Field(None, ge=0, description="Minimum length")
    max_length: Optional[int] = Field(None, ge=0, description="Maximum length")
    pattern: Optional[str] = Field(None, description="Regex pattern")
    encoding: str = Field(default="utf-8", description="Character encoding")
    case_sensitive: bool = Field(default=True, description="Case sensitivity")
    trim_whitespace: bool = Field(default=True, description="Auto-trim whitespace")
    allow_empty: bool = Field(default=False, description="Allow empty strings")
    security_level: SecurityLevel = Field(default=SecurityLevel.PUBLIC, description="Security classification")
    
    @validator('value')
    def validate_string_value(cls, v, values):
        """Validate string according to constraints"""
        format_type = values.get('format')
        min_length = values.get('min_length')
        max_length = values.get('max_length')
        pattern = values.get('pattern')
        allow_empty = values.get('allow_empty', False)
        trim_whitespace = values.get('trim_whitespace', True)
        
        # Trim whitespace if enabled
        if trim_whitespace and isinstance(v, str):
            v = v.strip()
        
        # Check empty string
        if not v and not allow_empty:
            raise ValueError('Empty strings not allowed')
        
        # Length validation
        if min_length is not None and len(v) < min_length:
            raise ValueError(f'String length {len(v)} is less than minimum {min_length}')
        
        if max_length is not None and len(v) > max_length:
            raise ValueError(f'String length {len(v)} exceeds maximum {max_length}')
        
        # Pattern validation
        if pattern and not re.match(pattern, v):
            raise ValueError(f'String does not match required pattern: {pattern}')
        
        # Format-specific validation
        if format_type:
            cls._validate_string_format(v, format_type)
        
        return v
    
    @staticmethod
    def _validate_string_format(value: str, format_type: StringFormat):
        """Validate string against specific format"""
        format_validators = {
            StringFormat.EMAIL: lambda v: EmailStr.validate(v),
            StringFormat.UUID: lambda v: UUID(v),
            StringFormat.URL: lambda v: cls._validate_url(v),
            StringFormat.PHONE: lambda v: cls._validate_phone(v),
            StringFormat.IPV4: lambda v: ipaddress.IPv4Address(v),
            StringFormat.IPV6: lambda v: ipaddress.IPv6Address(v),
            StringFormat.SLUG: lambda v: cls._validate_slug(v),
            StringFormat.USERNAME: lambda v: cls._validate_username(v),
            StringFormat.HEX_COLOR: lambda v: cls._validate_hex_color(v),
            StringFormat.SEMVER: lambda v: cls._validate_semver(v),
        }
        
        validator_func = format_validators.get(format_type)
        if validator_func:
            try:
                validator_func(value)
            except Exception as e:
                raise ValueError(f'Invalid {format_type.value} format: {str(e)}')
    
    @staticmethod
    def _validate_url(value: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(value):
            raise ValueError('Invalid URL format')
        return True
    
    @staticmethod
    def _validate_phone(value: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
        except NumberParseException as e:
            raise ValueError(f'Invalid phone number: {str(e)}')
        return True
    
    @staticmethod
    def _validate_slug(value: str) -> bool:
        """Validate slug format"""
        slug_pattern = re.compile(r'^[a-z0-9-]+$')
        if not slug_pattern.match(value):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return True
    
    @staticmethod
    def _validate_username(value: str) -> bool:
        """Validate username format"""
        username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
        if not username_pattern.match(value):
            raise ValueError('Username must be 3-30 characters, alphanumeric and underscores only')
        return True
    
    @staticmethod
    def _validate_hex_color(value: str) -> bool:
        """Validate hex color format"""
        hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        if not hex_pattern.match(value):
            raise ValueError('Invalid hex color format')
        return True
    
    @staticmethod
    def _validate_semver(value: str) -> bool:
        """Validate semantic version format"""
        semver_pattern = re.compile(
            r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
            r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
            r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
            r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        )
        if not semver_pattern.match(value):
            raise ValueError('Invalid semantic version format')
        return True


class EnhancedInteger(BaseModel):
    """Enhanced integer type with advanced constraints"""
    value: int = Field(description="Integer value")
    minimum: Optional[int] = Field(None, description="Minimum value (inclusive)")
    maximum: Optional[int] = Field(None, description="Maximum value (inclusive)")
    exclusive_minimum: Optional[int] = Field(None, description="Exclusive minimum")
    exclusive_maximum: Optional[int] = Field(None, description="Exclusive maximum")
    multiple_of: Optional[int] = Field(None, gt=0, description="Must be multiple of this value")
    format: Optional[NumericFormat] = Field(None, description="Numeric format")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    precision: Optional[int] = Field(None, ge=0, description="Number of significant digits")
    
    @validator('value')
    def validate_integer_constraints(cls, v, values):
        """Validate integer against constraints"""
        minimum = values.get('minimum')
        maximum = values.get('maximum')
        exclusive_minimum = values.get('exclusive_minimum')
        exclusive_maximum = values.get('exclusive_maximum')
        multiple_of = values.get('multiple_of')
        
        # Range validation
        if minimum is not None and v < minimum:
            raise ValueError(f'Value {v} is less than minimum {minimum}')
        
        if maximum is not None and v > maximum:
            raise ValueError(f'Value {v} exceeds maximum {maximum}')
        
        if exclusive_minimum is not None and v <= exclusive_minimum:
            raise ValueError(f'Value {v} must be greater than {exclusive_minimum}')
        
        if exclusive_maximum is not None and v >= exclusive_maximum:
            raise ValueError(f'Value {v} must be less than {exclusive_maximum}')
        
        # Multiple validation
        if multiple_of is not None and v % multiple_of != 0:
            raise ValueError(f'Value {v} is not a multiple of {multiple_of}')
        
        return v


class EnhancedFloat(BaseModel):
    """Enhanced float type with precision and range constraints"""
    value: float = Field(description="Float value")
    minimum: Optional[float] = Field(None, description="Minimum value (inclusive)")
    maximum: Optional[float] = Field(None, description="Maximum value (inclusive)")
    exclusive_minimum: Optional[float] = Field(None, description="Exclusive minimum")
    exclusive_maximum: Optional[float] = Field(None, description="Exclusive maximum")
    precision: Optional[int] = Field(None, ge=0, le=15, description="Decimal precision")
    format: Optional[NumericFormat] = Field(None, description="Numeric format")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    allow_infinity: bool = Field(default=False, description="Allow infinite values")
    allow_nan: bool = Field(default=False, description="Allow NaN values")
    
    @validator('value')
    def validate_float_constraints(cls, v, values):
        """Validate float against constraints"""
        import math
        
        minimum = values.get('minimum')
        maximum = values.get('maximum')
        exclusive_minimum = values.get('exclusive_minimum')
        exclusive_maximum = values.get('exclusive_maximum')
        precision = values.get('precision')
        allow_infinity = values.get('allow_infinity', False)
        allow_nan = values.get('allow_nan', False)
        
        # Check for special values
        if math.isnan(v) and not allow_nan:
            raise ValueError('NaN values not allowed')
        
        if math.isinf(v) and not allow_infinity:
            raise ValueError('Infinite values not allowed')
        
        # Skip other validations for special values
        if math.isnan(v) or math.isinf(v):
            return v
        
        # Range validation
        if minimum is not None and v < minimum:
            raise ValueError(f'Value {v} is less than minimum {minimum}')
        
        if maximum is not None and v > maximum:
            raise ValueError(f'Value {v} exceeds maximum {maximum}')
        
        if exclusive_minimum is not None and v <= exclusive_minimum:
            raise ValueError(f'Value {v} must be greater than {exclusive_minimum}')
        
        if exclusive_maximum is not None and v >= exclusive_maximum:
            raise ValueError(f'Value {v} must be less than {exclusive_maximum}')
        
        # Precision validation
        if precision is not None:
            rounded_value = round(v, precision)
            if abs(v - rounded_value) > 1e-10:  # Allow for floating point precision errors
                raise ValueError(f'Value {v} exceeds precision of {precision} decimal places')
        
        return v


class EnhancedDecimal(BaseModel):
    """Enhanced decimal type for financial and precise calculations"""
    value: Decimal = Field(description="Decimal value")
    minimum: Optional[Decimal] = Field(None, description="Minimum value (inclusive)")
    maximum: Optional[Decimal] = Field(None, description="Maximum value (inclusive)")
    precision: Optional[int] = Field(None, ge=1, le=28, description="Total digits")
    scale: Optional[int] = Field(None, ge=0, description="Decimal places")
    currency: Optional[str] = Field(None, description="Currency code (ISO 4217)")
    
    @validator('value', pre=True)
    def convert_to_decimal(cls, v):
        """Convert input to Decimal"""
        if isinstance(v, (int, float, str)):
            try:
                return Decimal(str(v))
            except InvalidOperation:
                raise ValueError(f'Cannot convert {v} to Decimal')
        return v
    
    @validator('value')
    def validate_decimal_constraints(cls, v, values):
        """Validate decimal against constraints"""
        minimum = values.get('minimum')
        maximum = values.get('maximum')
        precision = values.get('precision')
        scale = values.get('scale')
        
        # Range validation
        if minimum is not None and v < minimum:
            raise ValueError(f'Value {v} is less than minimum {minimum}')
        
        if maximum is not None and v > maximum:
            raise ValueError(f'Value {v} exceeds maximum {maximum}')
        
        # Precision and scale validation
        if precision is not None or scale is not None:
            sign, digits, exponent = v.as_tuple()
            
            if precision is not None and len(digits) > precision:
                raise ValueError(f'Value {v} exceeds precision of {precision} digits')
            
            if scale is not None and -exponent > scale:
                raise ValueError(f'Value {v} exceeds scale of {scale} decimal places')
        
        return v


class EnhancedDateTime(BaseModel):
    """Enhanced datetime type with timezone and range support"""
    value: datetime = Field(description="Datetime value")
    timezone_aware: bool = Field(default=True, description="Require timezone awareness")
    minimum: Optional[datetime] = Field(None, description="Minimum datetime")
    maximum: Optional[datetime] = Field(None, description="Maximum datetime")
    format: Optional[str] = Field(None, description="Expected datetime format")
    
    @validator('value')
    def validate_datetime_constraints(cls, v, values):
        """Validate datetime against constraints"""
        timezone_aware = values.get('timezone_aware', True)
        minimum = values.get('minimum')
        maximum = values.get('maximum')
        
        # Timezone validation
        if timezone_aware and v.tzinfo is None:
            raise ValueError('Timezone-aware datetime required')
        
        if not timezone_aware and v.tzinfo is not None:
            raise ValueError('Timezone-naive datetime required')
        
        # Range validation
        if minimum is not None and v < minimum:
            raise ValueError(f'Datetime {v} is before minimum {minimum}')
        
        if maximum is not None and v > maximum:
            raise ValueError(f'Datetime {v} is after maximum {maximum}')
        
        return v


class EnhancedBoolean(BaseModel):
    """Enhanced boolean type with string conversion support"""
    value: bool = Field(description="Boolean value")
    strict: bool = Field(default=True, description="Strict boolean validation")
    truthy_values: List[str] = Field(
        default_factory=lambda: ["true", "yes", "1", "on", "enable", "enabled"],
        description="Values considered true"
    )
    falsy_values: List[str] = Field(
        default_factory=lambda: ["false", "no", "0", "off", "disable", "disabled"],
        description="Values considered false"
    )
    
    @validator('value', pre=True)
    def convert_to_boolean(cls, v, values):
        """Convert various types to boolean"""
        strict = values.get('strict', True)
        truthy_values = values.get('truthy_values', [])
        falsy_values = values.get('falsy_values', [])
        
        if isinstance(v, bool):
            return v
        
        if strict:
            raise ValueError('Strict boolean mode: only bool values allowed')
        
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in truthy_values:
                return True
            elif v_lower in falsy_values:
                return False
            else:
                raise ValueError(f'Cannot convert "{v}" to boolean')
        
        if isinstance(v, (int, float)):
            return bool(v)
        
        raise ValueError(f'Cannot convert {type(v)} to boolean')


class EnhancedArray(BaseModel):
    """Enhanced array type with size and uniqueness constraints"""
    value: List[Any] = Field(description="Array value")
    min_items: Optional[int] = Field(None, ge=0, description="Minimum number of items")
    max_items: Optional[int] = Field(None, ge=0, description="Maximum number of items")
    unique_items: bool = Field(default=False, description="Require unique items")
    item_type: Optional[Type] = Field(None, description="Type constraint for items")
    allow_empty: bool = Field(default=True, description="Allow empty arrays")
    
    @validator('value')
    def validate_array_constraints(cls, v, values):
        """Validate array against constraints"""
        min_items = values.get('min_items')
        max_items = values.get('max_items')
        unique_items = values.get('unique_items', False)
        item_type = values.get('item_type')
        allow_empty = values.get('allow_empty', True)
        
        # Empty array check
        if not v and not allow_empty:
            raise ValueError('Empty arrays not allowed')
        
        # Size validation
        if min_items is not None and len(v) < min_items:
            raise ValueError(f'Array has {len(v)} items, minimum is {min_items}')
        
        if max_items is not None and len(v) > max_items:
            raise ValueError(f'Array has {len(v)} items, maximum is {max_items}')
        
        # Uniqueness validation
        if unique_items and len(v) != len(set(str(item) for item in v)):
            raise ValueError('Array items must be unique')
        
        # Item type validation
        if item_type is not None:
            for i, item in enumerate(v):
                if not isinstance(item, item_type):
                    raise ValueError(f'Item at index {i} is not of type {item_type.__name__}')
        
        return v


class EnhancedObject(BaseModel):
    """Enhanced object type with property constraints"""
    value: Dict[str, Any] = Field(description="Object value")
    min_properties: Optional[int] = Field(None, ge=0, description="Minimum number of properties")
    max_properties: Optional[int] = Field(None, ge=0, description="Maximum number of properties")
    required_properties: List[str] = Field(default_factory=list, description="Required property names")
    allowed_properties: Optional[List[str]] = Field(None, description="Allowed property names")
    property_pattern: Optional[str] = Field(None, description="Pattern for property names")
    
    @validator('value')
    def validate_object_constraints(cls, v, values):
        """Validate object against constraints"""
        min_properties = values.get('min_properties')
        max_properties = values.get('max_properties')
        required_properties = values.get('required_properties', [])
        allowed_properties = values.get('allowed_properties')
        property_pattern = values.get('property_pattern')
        
        # Size validation
        if min_properties is not None and len(v) < min_properties:
            raise ValueError(f'Object has {len(v)} properties, minimum is {min_properties}')
        
        if max_properties is not None and len(v) > max_properties:
            raise ValueError(f'Object has {len(v)} properties, maximum is {max_properties}')
        
        # Required properties validation
        missing_props = set(required_properties) - set(v.keys())
        if missing_props:
            raise ValueError(f'Missing required properties: {missing_props}')
        
        # Allowed properties validation
        if allowed_properties is not None:
            extra_props = set(v.keys()) - set(allowed_properties)
            if extra_props:
                raise ValueError(f'Extra properties not allowed: {extra_props}')
        
        # Property name pattern validation
        if property_pattern is not None:
            pattern = re.compile(property_pattern)
            invalid_props = [prop for prop in v.keys() if not pattern.match(prop)]
            if invalid_props:
                raise ValueError(f'Property names do not match pattern: {invalid_props}')
        
        return v


# Type aliases for convenience
AinflueString = EnhancedString
AinflueInteger = EnhancedInteger
AinflueFloat = EnhancedFloat
AinflueDecimal = EnhancedDecimal
AinflueDateTime = EnhancedDateTime
AinflueBoolean = EnhancedBoolean
AinflueArray = EnhancedArray
AinflueObject = EnhancedObject

# Export all types
__all__ = [
    'StringFormat',
    'NumericFormat',
    'SecurityLevel',
    'EnhancedString',
    'EnhancedInteger',
    'EnhancedFloat',
    'EnhancedDecimal',
    'EnhancedDateTime',
    'EnhancedBoolean',
    'EnhancedArray',
    'EnhancedObject',
    'AinflueString',
    'AinflueInteger',
    'AinflueFloat',
    'AinflueDecimal',
    'AinflueDateTime',
    'AinflueBoolean',
    'AinflueArray',
    'AinflueObject'
]