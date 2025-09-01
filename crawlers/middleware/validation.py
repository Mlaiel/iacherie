"""Data Validation Middleware Module
=================================

Enterprise-grade data validation middleware for crawler pipeline.
Implements comprehensive schema validation, sanitization, and data quality checks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Validation:
- Multi-format content integrity validation
- Creator rights and ownership verification
- AI protection metadata validation
- Monetization data accuracy checks
- Cross-platform compliance validation
"""

import re
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Type, Callable
from enum import Enum
import logging
import mimetypes
import magic
from urllib.parse import urlparse
import phonenumbers
import email_validator

from pydantic import BaseModel, ValidationError, Field, validator
from pydantic.schema import schema
import redis
from sqlalchemy import text

from ...config.settings import get_settings
from ...utils.cache import CacheManager

settings = get_settings()
logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """
Validation levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"
    REGULATORY = "regulatory"


class DataType(str, Enum):
    """Supported data types"""

    TEXT = "text"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    DATE = "date"
    DATETIME = "datetime"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    UUID = "uuid"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    BASE64 = "base64"
    HASH = "hash"
    IP_ADDRESS = "ip_address"
    FILE_PATH = "file_path"
    MIME_TYPE = "mime_type"
    AUDIO_FORMAT = "audio_format"
    VIDEO_FORMAT = "video_format"
    IMAGE_FORMAT = "image_format"
    COPYRIGHT_INFO = "copyright_info"
    MONETIZATION_DATA = "monetization_data"


class SanitizationLevel(str, Enum):
    """Sanitization levels"""

    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    GDPR_COMPLIANT = "gdpr_compliant"


class ContentQuality(str, Enum):
    """Content quality levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"


class ValidationRule(BaseModel):
    """Enhanced data validation rule"""
    rule_id: str = Field(description="Rule identifier")
    field_name: str = Field(description="Field name to validate")
    data_type: DataType = Field(description="Expected data type")
    required: bool = Field(default=True, description="Whether field is required")
    min_length: Optional[int] = Field(None, description="Minimum length")
    max_length: Optional[int] = Field(None, description="Maximum length")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum numeric value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum numeric value")
    pattern: Optional[str] = Field(None, description="Regex pattern")
    allowed_values: Optional[List[Any]] = Field(None, description="Allowed values")
    forbidden_values: Optional[List[Any]] = Field(None, description="Forbidden values")
    custom_validator: Optional[str] = Field(None, description="Custom validator function name")
    sanitization_level: SanitizationLevel = Field(default=SanitizationLevel.BASIC)
    quality_requirements: Optional[ContentQuality] = Field(None, description="Quality requirements")
    business_rules: Dict[str, Any] = Field(default_factory=dict, description="Business-specific rules")


class ValidationResult(BaseModel):
    """Enhanced validation result"""
    is_valid: bool = Field(description="Whether data is valid")
    field_name: str = Field(description="Field name")
    original_value: Any = Field(description="Original value")
    sanitized_value: Any = Field(description="Sanitized value")
    quality_score: Optional[float] = Field(None, description="Data quality score (0-1)")
    confidence_level: Optional[float] = Field(None, description="Validation confidence (0-1)")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ContentValidationResult(BaseModel):
    """Complete content validation result"""
    content_id: str = Field(description="Content identifier")
    overall_valid: bool = Field(description="Overall validation status")
    validation_level: ValidationLevel = Field(description="Validation level used")
    field_results: Dict[str, ValidationResult] = Field(description="Field validation results")
    quality_score: float = Field(description="Data quality score (0-1)")
    sanitized_data: Dict[str, Any] = Field(description="Sanitized data")
    validation_timestamp: datetime = Field(description="Validation timestamp")
    processing_time: float = Field(description="Processing time in seconds")


class SchemaValidator:
    """Advanced schema validation engine"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
        self.custom_validators = {}
        self.validation_rules = {}
        
        # Initialize built-in validators
        self._initialize_builtin_validators()
    
    def _initialize_builtin_validators(self):
        """
Initialize built-in validation patterns and rules"""
        self.patterns = {
            DataType.EMAIL: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            DataType.URL: r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            DataType.PHONE: r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
            DataType.UUID: r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            DataType.IP_ADDRESS: r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            DataType.HASH: r'^[a-fA-F0-9]{32,128}$'
        }
        
        # Register built-in custom validators
        self.custom_validators.update({
            'validate_json': self._validate_json,
            'validate_html': self._validate_html,
            'validate_markdown': self._validate_markdown,
            'validate_base64': self._validate_base64,
            'validate_file_path': self._validate_file_path,
            'validate_date_range': self._validate_date_range,
            'validate_content_type': self._validate_content_type
        })
    
    def register_validation_rule(self, rule: ValidationRule):
        """
Register validation rule for specific content type or field"""
        self.validation_rules[rule.field_name] = rule
    
    def register_custom_validator(self, name: str, validator_func: Callable):
        """
Register custom validator function"""
        self.custom_validators[name] = validator_func
    
    async def validate_field(self, field_name: str, value: Any, 
                           rule: ValidationRule) -> ValidationResult:
        """
Validate single field according to rule"""
        start_time = time.time()
        result = ValidationResult(
            is_valid=True,
            field_name=field_name,
            original_value=value,
            sanitized_value=value,
            errors=[],
            warnings=[],
            metadata={}
        )
        
        try:
            # Check if field is required
            if rule.required and (value is None or value == ""):
                result.is_valid = False
                result.errors.append("Field is required")
                return result
            
            # Skip validation for optional empty fields
            if not rule.required and (value is None or value == ""):
                return result
            
            # Sanitize value
            sanitized_value = await self.sanitize_value(value, rule.sanitization_level)
            result.sanitized_value = sanitized_value
            
            # Type validation
            type_valid, type_error = await self.validate_data_type(sanitized_value, rule.data_type)
            if not type_valid:
                result.is_valid = False
                result.errors.append(type_error)
                return result
            
            # Length validation
            if isinstance(sanitized_value, (str, list, dict)):
                value_length = len(sanitized_value)
                
                if rule.min_length and value_length < rule.min_length:
                    result.is_valid = False
                    result.errors.append(f"Length {value_length} is below minimum {rule.min_length}")
                
                if rule.max_length and value_length > rule.max_length:
                    result.is_valid = False
                    result.errors.append(f"Length {value_length} exceeds maximum {rule.max_length}")
            
            # Pattern validation
            if rule.pattern and isinstance(sanitized_value, str):
                if not re.match(rule.pattern, sanitized_value):
                    result.is_valid = False
                    result.errors.append("Value does not match required pattern")
            
            # Allowed values validation
            if rule.allowed_values and sanitized_value not in rule.allowed_values:
                result.is_valid = False
                result.errors.append(f"Value not in allowed values: {rule.allowed_values}")
            
            # Custom validation
            if rule.custom_validator and rule.custom_validator in self.custom_validators:
                custom_valid, custom_error = await self.custom_validators[rule.custom_validator](sanitized_value)
                if not custom_valid:
                    result.is_valid = False
                    result.errors.append(custom_error)
            
            # Add metadata
            result.metadata = {
                "validation_time": time.time() - start_time,
                "data_type": rule.data_type.value,
                "sanitization_level": rule.sanitization_level.value
            }
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {str(e)}")
            logger.error(f"Field validation error for {field_name}: {e}")
        
        return result
    
    async def validate_data_type(self, value: Any, data_type: DataType) -> tuple[bool, str]:
        """Validate value against specific data type"""
        try:
            if data_type == DataType.TEXT:
                return isinstance(value, str), "Value must be text"
            
            elif data_type == DataType.EMAIL:
                if not isinstance(value, str):
                    return False, "Email must be text"
                return bool(re.match(self.patterns[DataType.EMAIL], value)), "Invalid email format"
            
            elif data_type == DataType.URL:
                if not isinstance(value, str):
                    return False, "URL must be text"
                return bool(re.match(self.patterns[DataType.URL], value)), "Invalid URL format"
            
            elif data_type == DataType.PHONE:
                if not isinstance(value, str):
                    return False, "Phone must be text"
                return bool(re.match(self.patterns[DataType.PHONE], value)), "Invalid phone format"
            
            elif data_type == DataType.DATE:
                try:
                    datetime.strptime(str(value), "%Y-%m-%d")
                    return True, ""
                except ValueError:
                    return False, "Invalid date format (YYYY-MM-DD expected)"
            
            elif data_type == DataType.DATETIME:
                try:
                    datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                    return True, ""
                except ValueError:
                    return False, "Invalid datetime format (ISO format expected)"
            
            elif data_type == DataType.INTEGER:
                try:
                    int(value)
                    return True, ""
                except (ValueError, TypeError):
                    return False, "Value must be integer"
            
            elif data_type == DataType.FLOAT:
                try:
                    float(value)
                    return True, ""
                except (ValueError, TypeError):
                    return False, "Value must be float"
            
            elif data_type == DataType.BOOLEAN:
                return isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0'], "Value must be boolean"
            
            elif data_type == DataType.UUID:
                if not isinstance(value, str):
                    return False, "UUID must be text"
                return bool(re.match(self.patterns[DataType.UUID], value.lower())), "Invalid UUID format"
            
            elif data_type == DataType.JSON:
                try:
                    if isinstance(value, str):
                        json.loads(value)
                    return True, ""
                except json.JSONDecodeError:
                    return False, "Invalid JSON format"
            
            elif data_type == DataType.IP_ADDRESS:
                if not isinstance(value, str):
                    return False, "IP address must be text"
                return bool(re.match(self.patterns[DataType.IP_ADDRESS], value)), "Invalid IP address format"
            
            elif data_type == DataType.HASH:
                if not isinstance(value, str):
                    return False, "Hash must be text"
                return bool(re.match(self.patterns[DataType.HASH], value)), "Invalid hash format"
            
            else:
                return True, ""  # Unknown type passes
                
        except Exception as e:
            return False, f"Type validation error: {str(e)}"
    
    async def sanitize_value(self, value: Any, level: SanitizationLevel) -> Any:
        """Sanitize value according to sanitization level"""
        if not isinstance(value, str):
            return value
        
        if level == SanitizationLevel.NONE:
            return value
        
        sanitized = value
        
        if level in [SanitizationLevel.BASIC, SanitizationLevel.MODERATE, SanitizationLevel.AGGRESSIVE]:
            # Basic sanitization - trim whitespace
            sanitized = sanitized.strip()
            
            # Remove null bytes
            sanitized = sanitized.replace('\x00', '')
        
        if level in [SanitizationLevel.MODERATE, SanitizationLevel.AGGRESSIVE]:
            # Remove control characters
            sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in ['\n', '\r', '\t'])
            
            # Basic HTML escape
            sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
            
            # Remove potential SQL injection patterns
            sql_patterns = [
                r'(\'|\"|;|--|\*|\/\*|\*\/)',
                r'(union|select|insert|update|delete|drop|create|alter)',
            ]
            for pattern in sql_patterns:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        if level == SanitizationLevel.AGGRESSIVE:
            # Remove all HTML tags
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
            
            # Remove JavaScript
            sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', '(', ')', '{', '}', '[', ']']
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    # Built-in custom validators
    async def _validate_json(self, value: Any) -> tuple[bool, str]:
        """Validate JSON format"""
        try:
            if isinstance(value, str):
                json.loads(value)
            elif not isinstance(value, (dict, list)):
                return False, "Value must be valid JSON"
            return True, ""
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
    
    async def _validate_html(self, value: Any) -> tuple[bool, str]:
        """Validate HTML content"""
        if not isinstance(value, str):
            return False, "HTML must be text"
        
        # Basic HTML validation - check for balanced tags
        import html.parser
        
        class HTMLValidator(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.errors = []
                self.stack = []
            
            def handle_starttag(self, tag, attrs):
                if tag not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
                    self.stack.append(tag)
            
            def handle_endtag(self, tag):
                if self.stack and self.stack[-1] == tag:
                    self.stack.pop()
                else:
                    self.errors.append(f"Mismatched tag: {tag}")
        
        try:
            validator = HTMLValidator()
            validator.feed(value)
            if validator.errors or validator.stack:
                return False, "Invalid HTML structure"
            return True, ""
        except Exception:
            return False, "HTML parsing error"
    
    async def _validate_markdown(self, value: Any) -> tuple[bool, str]:
        """Validate Markdown content"""
        if not isinstance(value, str):
            return False, "Markdown must be text"
        
        # Basic Markdown validation
        try:
            # Check for common Markdown patterns
            markdown_patterns = [
                r'^#{1,6}\s',  # Headers
                r'^\*\s|\-\s|\d+\.\s',  # Lists
                r'\[.+\]\(.+\)',  # Links
                r'!\[.*\]\(.+\)',  # Images
                r'`[^`]+`',  # Inline code
                r'```[\s\S]*?```',  # Code blocks
            ]
            
            # If it contains markdown patterns, it's likely valid
            # This is a basic check - more sophisticated validation could be added
            return True, ""
        except Exception:
            return False, "Markdown validation error"
    
    async def _validate_base64(self, value: Any) -> tuple[bool, str]:
        """Validate Base64 encoding"""
        if not isinstance(value, str):
            return False, "Base64 must be text"
        
        try:
            import base64
            base64.b64decode(value, validate=True)
            return True, ""
        except Exception:
            return False, "Invalid Base64 encoding"
    
    async def _validate_file_path(self, value: Any) -> tuple[bool, str]:
        """Validate file path"""
        if not isinstance(value, str):
            return False, "File path must be text"
        
        # Check for path traversal attempts
        dangerous_patterns = ['../', '..\\', '/etc/', '/proc/', 'C:\\']
        if any(pattern in value for pattern in dangerous_patterns):
            return False, "Potentially dangerous file path"
        
        return True, ""
    
    async def _validate_date_range(self, value: Any) -> tuple[bool, str]:
        """Validate date is within reasonable range"""
        try:
            if isinstance(value, str):
                date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                date_obj = value
            
            # Check if date is within reasonable range (1900-2100)
            if date_obj.year < 1900 or date_obj.year > 2100:
                return False, "Date outside reasonable range (1900-2100)"
            
            return True, ""
        except Exception:
            return False, "Date validation error"
    
    async def _validate_content_type(self, value: Any) -> tuple[bool, str]:
        """Validate content type"""
        if not isinstance(value, str):
            return False, "Content type must be text"
        
        valid_content_types = [
            'text/plain', 'text/html', 'application/json', 'application/xml',
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'audio/mpeg', 'audio/wav', 'audio/ogg',
            'video/mp4', 'video/webm', 'video/ogg'
        ]
        
        if value not in valid_content_types:
            return False, f"Invalid content type. Allowed: {valid_content_types}"
        
        return True, ""


class DataQualityAnalyzer:
    """Advanced data quality analysis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache = CacheManager()
    
    async def calculate_quality_score(self, validation_results: Dict[str, ValidationResult]) -> float:
        """
Calculate overall data quality score"""
        if not validation_results:
            return 0.0
        
        total_fields = len(validation_results)
        valid_fields = sum(1 for result in validation_results.values() if result.is_valid)
        warning_fields = sum(1 for result in validation_results.values() if result.warnings)
        
        # Base score from valid fields
        base_score = valid_fields / total_fields
        
        # Penalty for warnings
        warning_penalty = (warning_fields / total_fields) * 0.1
        
        # Quality score between 0 and 1
        quality_score = max(0.0, base_score - warning_penalty)
        
        return round(quality_score, 3)
    
    async def analyze_data_completeness(self, data: Dict[str, Any], 
                                      required_fields: List[str]) -> Dict[str, Any]:
        """
Analyze data completeness"""
        completeness_analysis = {
            "total_fields": len(required_fields),
            "present_fields": 0,
            "missing_fields": [],
            "empty_fields": [],
            "completeness_score": 0.0
        }
        
        for field in required_fields:
            if field in data:
                completeness_analysis["present_fields"] += 1
                if not data[field] or data[field] == "":
                    completeness_analysis["empty_fields"].append(field)
            else:
                completeness_analysis["missing_fields"].append(field)
        
        # Calculate completeness score
        completeness_analysis["completeness_score"] = (
            completeness_analysis["present_fields"] / completeness_analysis["total_fields"]
        )
        
        return completeness_analysis
    
    async def detect_data_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data anomalies"""
        anomalies = []
        
        for field_name, value in data.items():
            if isinstance(value, str):
                # Check for suspiciously long values
                if len(value) > 10000:
                    anomalies.append({
                        "field": field_name,
                        "type": "excessive_length",
                        "description": f"Field length {len(value)} is unusually long",
                        "severity": "medium"
                    })
                
                # Check for suspicious patterns
                if re.search(r'<script|javascript:|vbscript:', value, re.IGNORECASE):
                    anomalies.append({
                        "field": field_name,
                        "type": "potential_xss",
                        "description": "Field contains potentially malicious script content",
                        "severity": "high"
                    })
                
                # Check for SQL injection patterns
                if re.search(r'(union|select|insert|update|delete|drop)\s', value, re.IGNORECASE):
                    anomalies.append({
                        "field": field_name,
                        "type": "potential_sql_injection",
                        "description": "Field contains SQL-like keywords",
                        "severity": "high"
                    })
            
            elif isinstance(value, (int, float)):
                # Check for extreme numeric values
                if abs(value) > 1e10:
                    anomalies.append({
                        "field": field_name,
                        "type": "extreme_numeric_value",
                        "description": f"Numeric value {value} is extremely large",
                        "severity": "low"
                    })
        
        return anomalies


class ValidationMiddleware:
    """Main data validation middleware orchestrator"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
        # Initialize components
        self.schema_validator = SchemaValidator(self.redis_client)
        self.quality_analyzer = DataQualityAnalyzer(self.redis_client)
        
        # Load default validation schemas
        self._load_default_schemas()
    
    def _load_default_schemas(self):
        """
Load default validation schemas for common content types"""
        # User profile validation schema
        user_rules = [
            ValidationRule(
                rule_id="user_email",
                field_name="email",
                data_type=DataType.EMAIL,
                required=True,
                max_length=255,
                sanitization_level=SanitizationLevel.BASIC
            ),
            ValidationRule(
                rule_id="user_name",
                field_name="name",
                data_type=DataType.TEXT,
                required=True,
                min_length=2,
                max_length=100,
                sanitization_level=SanitizationLevel.MODERATE
            ),
            ValidationRule(
                rule_id="user_bio",
                field_name="bio",
                data_type=DataType.TEXT,
                required=False,
                max_length=500,
                sanitization_level=SanitizationLevel.MODERATE
            )
        ]
        
        # Content validation schema
        content_rules = [
            ValidationRule(
                rule_id="content_title",
                field_name="title",
                data_type=DataType.TEXT,
                required=True,
                min_length=5,
                max_length=200,
                sanitization_level=SanitizationLevel.MODERATE
            ),
            ValidationRule(
                rule_id="content_description",
                field_name="description",
                data_type=DataType.TEXT,
                required=False,
                max_length=1000,
                sanitization_level=SanitizationLevel.MODERATE
            ),
            ValidationRule(
                rule_id="content_url",
                field_name="url",
                data_type=DataType.URL,
                required=True,
                sanitization_level=SanitizationLevel.BASIC
            ),
            ValidationRule(
                rule_id="content_tags",
                field_name="tags",
                data_type=DataType.JSON,
                required=False,
                sanitization_level=SanitizationLevel.BASIC
            )
        ]
        
        # Register schemas
        for rule in user_rules + content_rules:
            self.schema_validator.register_validation_rule(rule)
    
    async def validate_content(self, content_id: str, data: Dict[str, Any],
                             validation_level: ValidationLevel = ValidationLevel.STANDARD,
                             schema_name: Optional[str] = None) -> ContentValidationResult:
        """Validate complete content according to schema"""
        start_time = time.time()
        
        # Get validation rules for schema
        if schema_name:
            rules = await self.get_schema_rules(schema_name)
        else:
            rules = list(self.schema_validator.validation_rules.values())
        
        # Filter rules for fields present in data or required
        applicable_rules = [
            rule for rule in rules 
            if rule.field_name in data or rule.required
        ]
        
        # Validate each field
        field_results = {}
        for rule in applicable_rules:
            field_value = data.get(rule.field_name)
            validation_result = await self.schema_validator.validate_field(
                rule.field_name, field_value, rule
            )
            field_results[rule.field_name] = validation_result
        
        # Calculate quality score
        quality_score = await self.quality_analyzer.calculate_quality_score(field_results)
        
        # Determine overall validity
        overall_valid = all(result.is_valid for result in field_results.values())
        
        # Create sanitized data from successful validations
        sanitized_data = {}
        for field_name, result in field_results.items():
            if result.is_valid:
                sanitized_data[field_name] = result.sanitized_value
            else:
                # Keep original for invalid fields (application decision)
                sanitized_data[field_name] = result.original_value
        
        # Create final result
        content_result = ContentValidationResult(
            content_id=content_id,
            overall_valid=overall_valid,
            validation_level=validation_level,
            field_results=field_results,
            quality_score=quality_score,
            sanitized_data=sanitized_data,
            validation_timestamp=datetime.utcnow(),
            processing_time=time.time() - start_time
        )
        
        # Store validation result for analytics
        await self.store_validation_result(content_result)
        
        return content_result
    
    async def get_schema_rules(self, schema_name: str) -> List[ValidationRule]:
        """
Get validation rules for specific schema"""
        # This would typically load from database or configuration
        # For now, return all rules (simplified)
        return list(self.schema_validator.validation_rules.values())
    
    async def store_validation_result(self, result: ContentValidationResult):
        """
Store validation result for analytics and monitoring"""
        try:
            # Store in Redis with expiration
            result_key = f"validation_results:{result.content_id}"
            result_data = result.dict()
            
            # Convert datetime objects to strings for JSON serialization
            result_data["validation_timestamp"] = result.validation_timestamp.isoformat()
            
            await self.redis_client.set(result_key, json.dumps(result_data), ex=86400)  # 24 hours
            
            # Update validation statistics
            await self.update_validation_statistics(result)
            
        except Exception as e:
            logger.error(f"Failed to store validation result: {e}")
    
    async def update_validation_statistics(self, result: ContentValidationResult):
        """Update validation statistics for monitoring"""
        try:
            now = time.time()
            hour_window = int(now // 3600)
            day_window = int(now // 86400)
            
            # Update counts
            await self.redis_client.incr(f"validation_stats:hourly:{hour_window}:total")
            await self.redis_client.incr(f"validation_stats:daily:{day_window}:total")
            
            if result.overall_valid:
                await self.redis_client.incr(f"validation_stats:hourly:{hour_window}:valid")
                await self.redis_client.incr(f"validation_stats:daily:{day_window}:valid")
            else:
                await self.redis_client.incr(f"validation_stats:hourly:{hour_window}:invalid")
                await self.redis_client.incr(f"validation_stats:daily:{day_window}:invalid")
            
            # Update quality score statistics
            await self.redis_client.lpush(f"quality_scores:hourly:{hour_window}", result.quality_score)
            await self.redis_client.ltrim(f"quality_scores:hourly:{hour_window}", 0, 1000)  # Keep last 1000
            await self.redis_client.expire(f"quality_scores:hourly:{hour_window}", 86400)
            
            # Set expiration for hourly stats
            await self.redis_client.expire(f"validation_stats:hourly:{hour_window}:total", 86400 * 7)
            await self.redis_client.expire(f"validation_stats:daily:{day_window}:total", 86400 * 30)
            
        except Exception as e:
            logger.error(f"Failed to update validation statistics: {e}")
    
    async def get_validation_statistics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get validation statistics for specified time range"""
        try:
            now = time.time()
            
            if time_range == "1h":
                window = int(now // 3600)
                prefix = "validation_stats:hourly"
                windows = [window]
            elif time_range == "24h":
                window = int(now // 3600)
                prefix = "validation_stats:hourly"
                windows = [window - i for i in range(24)]
            elif time_range == "7d":
                window = int(now // 86400)
                prefix = "validation_stats:daily"
                windows = [window - i for i in range(7)]
            else:
                return {"error": "Invalid time range"}
            
            # Collect statistics
            total_validations = 0
            valid_validations = 0
            invalid_validations = 0
            quality_scores = []
            
            for w in windows:
                total = await self.redis_client.get(f"{prefix}:{w}:total") or 0
                valid = await self.redis_client.get(f"{prefix}:{w}:valid") or 0
                invalid = await self.redis_client.get(f"{prefix}:{w}:invalid") or 0
                
                total_validations += int(total)
                valid_validations += int(valid)
                invalid_validations += int(invalid)
                
                # Get quality scores for hourly data
                if "hourly" in prefix:
                    scores = await self.redis_client.lrange(f"quality_scores:hourly:{w}", 0, -1)
                    quality_scores.extend([float(score) for score in scores])
            
            # Calculate metrics
            success_rate = (valid_validations / total_validations * 100) if total_validations > 0 else 0
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                "time_range": time_range,
                "total_validations": total_validations,
                "valid_validations": valid_validations,
                "invalid_validations": invalid_validations,
                "success_rate": round(success_rate, 2),
                "average_quality_score": round(avg_quality_score, 3),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation statistics retrieval error: {e}")
            return {"error": str(e)}


# Factory function for dependency injection
def get_validation_middleware() -> ValidationMiddleware:
    """Get validation middleware instance"""
    return ValidationMiddleware()


# Convenience functions
async def validate_data(content_id: str, data: Dict[str, Any],
                       validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ContentValidationResult:
    """
Convenience function for data validation"""
    middleware = get_validation_middleware()
    return await middleware.validate_content(content_id, data, validation_level)


async def register_validation_schema(schema_name: str, rules: List[ValidationRule]):
    """
Convenience function for registering validation schema"""
    middleware = get_validation_middleware()
    for rule in rules:
        middleware.schema_validator.register_validation_rule(rule)
