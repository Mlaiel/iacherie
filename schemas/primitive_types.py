"""IA Influencer Agent Platform - Enhanced Primitive Types Module
Enhanced primitive type definitions for business-specific validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides enhanced primitive types with business logic validation:
- Enhanced string types (URLs, emails, phone numbers, etc.)
- Numeric types with business constraints
- Date/time types with timezone support
- File and media type definitions
- Geographic and currency types
"""

from typing import Optional, Union, List, Dict, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime, date, time
import re
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import constr, conint, confloat
from pydantic import EmailStr
from .base import BaseSchema


# =================== STRING TYPES ===================

class URLType(str):
    """Enhanced URL type with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('URL must be a string')
        
        # Basic URL pattern validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        
        return cls(v)


class PhoneNumberType(str):
    """Enhanced phone number type with international format support."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Phone number must be a string')
        
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+\.]', '', v)
        
        # Check if it's a valid international format
        if not re.match(r'^\d{7,15}$', cleaned):
            raise ValueError('Invalid phone number format')
        
        return cls(v)


class ColorHexType(str):
    """Hexadecimal color code type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Color must be a string')
        
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Invalid hex color format (must be #RRGGBB)')
        
        return cls(v)


class SlugType(str):
    """URL-friendly slug type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Slug must be a string')
        
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Invalid slug format (lowercase letters, numbers, hyphens only)')
        
        return cls(v)


class HashType(str):
    """Hash string type for various hash formats."""
    
    def __init__(self, hash_type: str = "sha256"):
        self.hash_type = hash_type
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Hash must be a string')
        
        # Validate common hash formats
        hash_patterns = {
            "md5": r'^[a-f0-9]{32}$',
            "sha1": r'^[a-f0-9]{40}$',
            "sha256": r'^[a-f0-9]{64}$',
            "sha512": r'^[a-f0-9]{128}$'
        }
        
        # Check against any valid hash format
        for pattern in hash_patterns.values():
            if re.match(pattern, v, re.IGNORECASE):
                return cls(v)
        
        raise ValueError('Invalid hash format')


# =================== NUMERIC TYPES ===================

class PercentageType(float):
    """Percentage type (0-100)."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, (int, float)):
            raise TypeError('Percentage must be a number')
        
        if not 0 <= v <= 100:
            raise ValueError('Percentage must be between 0 and 100')
        
        return cls(v)


class CurrencyAmountType(Decimal):
    """Currency amount with precision control."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            v = Decimal(v)
        elif isinstance(v, (int, float)):
            v = Decimal(str(v))
        elif not isinstance(v, Decimal):
            raise TypeError('Currency amount must be a number or decimal string')
        
        # Ensure 2 decimal places for currency
        return cls(v.quantize(Decimal('0.01')))


class RatingType(float):
    """Rating type (1-5 stars)."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, (int, float)):
            raise TypeError('Rating must be a number')
        
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        
        return cls(v)


class ScoreType(float):
    """Generic score type (0-1)."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, (int, float)):
            raise TypeError('Score must be a number')
        
        if not 0 <= v <= 1:
            raise ValueError('Score must be between 0 and 1')
        
        return cls(v)


# =================== GEOGRAPHIC TYPES ===================

class CountryCodeType(str):
    """ISO 3166-1 alpha-2 country code."""
    
    # Common country codes
    VALID_CODES = {
        'US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH',
        'AT', 'SE', 'NO', 'DK', 'FI', 'IE', 'PT', 'GR', 'PL', 'CZ',
        'HU', 'RO', 'BG', 'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'LU',
        'MT', 'CY', 'JP', 'KR', 'CN', 'IN', 'AU', 'NZ', 'BR', 'MX',
        'AR', 'CL', 'CO', 'PE', 'VE', 'ZA', 'EG', 'NG', 'KE', 'MA'
    }
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Country code must be a string')
        
        v = v.upper()
        if v not in cls.VALID_CODES:
            raise ValueError(f'Invalid country code: {v}')
        
        return cls(v)


class LanguageCodeType(str):
    """ISO 639-1 language code."""
    
    # Common language codes
    VALID_CODES = {
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
        'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'cs',
        'hu', 'ro', 'bg', 'hr', 'sk', 'sl', 'et', 'lv', 'lt', 'mt',
        'el', 'he', 'th', 'vi', 'id', 'ms', 'tl', 'sw', 'am', 'zu'
    }
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Language code must be a string')
        
        v = v.lower()
        if v not in cls.VALID_CODES:
            raise ValueError(f'Invalid language code: {v}')
        
        return cls(v)


class TimezoneType(str):
    """Timezone identifier type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Timezone must be a string')
        
        # Basic timezone format validation
        if not re.match(r'^[A-Za-z_]+\/[A-Za-z_]+$', v):
            raise ValueError('Invalid timezone format (expected: Continent/City)')
        
        return cls(v)


# =================== FILE AND MEDIA TYPES ===================

class FileExtensionType(str):
    """File extension type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('File extension must be a string')
        
        v = v.lower()
        if not v.startswith('.'):
            v = '.' + v
        
        if not re.match(r'^\.[a-z0-9]+$', v):
            raise ValueError('Invalid file extension format')
        
        return cls(v)


class MimeTypeType(str):
    """MIME type validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('MIME type must be a string')
        
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_]*\/[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_.]*$', v):
            raise ValueError('Invalid MIME type format')
        
        return cls(v)


class FileSizeType(int):
    """File size in bytes with human-readable formatting."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, int):
            raise TypeError('File size must be an integer')
        
        if v < 0:
            raise ValueError('File size cannot be negative')
        
        return cls(v)
    
    def __str__(self):
        """Human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self < 1024.0:
                return f"{self:.1f} {unit}"
            self /= 1024.0
        return f"{self:.1f} PB"


# =================== BUSINESS TYPES ===================

class UsernameType(str):
    """Username type with validation rules."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Username must be a string')
        
        if not 3 <= len(v) <= 30:
            raise ValueError('Username must be between 3 and 30 characters')
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        
        if v.startswith(('-', '_')) or v.endswith(('-', '_')):
            raise ValueError('Username cannot start or end with hyphens or underscores')
        
        return cls(v)


class HandleType(str):
    """Social media handle type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Handle must be a string')
        
        # Remove @ prefix if present
        if v.startswith('@'):
            v = v[1:]
        
        if not 1 <= len(v) <= 50:
            raise ValueError('Handle must be between 1 and 50 characters')
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Handle can only contain letters, numbers, underscores, dots, and hyphens')
        
        return cls(v)


class TagType(str):
    """Content tag type."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Tag must be a string')
        
        v = v.strip().lower()
        
        if not 1 <= len(v) <= 50:
            raise ValueError('Tag must be between 1 and 50 characters')
        
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', v):
            raise ValueError('Tag can only contain letters, numbers, spaces, underscores, and hyphens')
        
        return cls(v)


# =================== SCHEMA DEFINITIONS ===================

class EnhancedStringType(BaseSchema):
    """Enhanced string type with business validation."""
    
    value: str = Field(..., description="String value")
    type_name: str = Field(..., description="String type name")
    validation_rules: List[str] = Field(default=[], description="Applied validation rules")
    normalized_value: Optional[str] = Field(None, description="Normalized string value")


class NumericConstraints(BaseSchema):
    """Numeric type constraints."""
    
    minimum: Optional[Union[int, float]] = Field(None, description="Minimum value")
    maximum: Optional[Union[int, float]] = Field(None, description="Maximum value")
    multiple_of: Optional[Union[int, float]] = Field(None, description="Must be multiple of")
    exclusive_minimum: bool = Field(False, description="Exclusive minimum")
    exclusive_maximum: bool = Field(False, description="Exclusive maximum")
    decimal_places: Optional[int] = Field(None, ge=0, le=10, description="Number of decimal places")


class EnhancedNumericType(BaseSchema):
    """Enhanced numeric type with constraints."""
    
    value: Union[int, float, Decimal] = Field(..., description="Numeric value")
    type_name: str = Field(..., description="Numeric type name")
    constraints: Optional[NumericConstraints] = Field(None, description="Value constraints")
    formatted_value: Optional[str] = Field(None, description="Formatted display value")
    currency: Optional[str] = Field(None, description="Currency code for monetary values")


class DateTimeConstraints(BaseSchema):
    """Date/time constraints."""
    
    earliest: Optional[datetime] = Field(None, description="Earliest allowed date/time")
    latest: Optional[datetime] = Field(None, description="Latest allowed date/time")
    timezone_required: bool = Field(False, description="Timezone information required")
    business_hours_only: bool = Field(False, description="Must be within business hours")
    weekdays_only: bool = Field(False, description="Must be on weekdays")


class EnhancedDateTimeType(BaseSchema):
    """Enhanced date/time type with constraints."""
    
    value: datetime = Field(..., description="Date/time value")
    type_name: str = Field(..., description="Date/time type name")
    constraints: Optional[DateTimeConstraints] = Field(None, description="Date/time constraints")
    timezone: Optional[str] = Field(None, description="Timezone identifier")
    formatted_value: Optional[str] = Field(None, description="Formatted display value")


class PrimitiveTypeRegistry(BaseSchema):
    """Registry of all enhanced primitive types."""
    
    string_types: Dict[str, Any] = Field(
        default={
            "url": URLType,
            "phone": PhoneNumberType,
            "color_hex": ColorHexType,
            "slug": SlugType,
            "hash": HashType,
            "username": UsernameType,
            "handle": HandleType,
            "tag": TagType
        },
        description="Available string types"
    )
    
    numeric_types: Dict[str, Any] = Field(
        default={
            "percentage": PercentageType,
            "currency": CurrencyAmountType,
            "rating": RatingType,
            "score": ScoreType
        },
        description="Available numeric types"
    )
    
    geographic_types: Dict[str, Any] = Field(
        default={
            "country_code": CountryCodeType,
            "language_code": LanguageCodeType,
            "timezone": TimezoneType
        },
        description="Available geographic types"
    )
    
    file_types: Dict[str, Any] = Field(
        default={
            "file_extension": FileExtensionType,
            "mime_type": MimeTypeType,
            "file_size": FileSizeType
        },
        description="Available file types"
    )


class TypeValidationResult(BaseSchema):
    """Result of primitive type validation."""
    
    is_valid: bool = Field(..., description="Validation result")
    type_name: str = Field(..., description="Type being validated")
    original_value: Any = Field(..., description="Original input value")
    validated_value: Optional[Any] = Field(None, description="Validated/normalized value")
    errors: List[str] = Field(default=[], description="Validation errors")
    warnings: List[str] = Field(default=[], description="Validation warnings")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")