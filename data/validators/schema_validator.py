"""Schema Validator - Advanced schema validation for IA Influencer Agent Platform
==============================================================================

Comprehensive schema validation system with Pydantic models and JSON Schema
support for data integrity and structure validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Type, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import jsonschema
from jsonschema import Draft7Validator, validators
from pydantic import BaseModel, ValidationError, Field, validator, root_validator
from pydantic.types import StrictStr, StrictInt, StrictFloat, StrictBool

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Schema validation levels."""    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class SchemaType(Enum):
    """Supported schema types."""    JSON_SCHEMA = "json_schema"
    PYDANTIC = "pydantic"
    OPENAPI = "openapi"
    AVRO = "avro"
    PROTOBUF = "protobuf"


class ValidationStatus(Enum):
    """Schema validation status."""    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class SchemaError:
    """Individual schema validation error."""    field_path: str
    error_type: str
    message: str
    expected_type: Optional[str] = None
    actual_value: Any = None
    constraint: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SchemaValidationResult:
    """Comprehensive schema validation result."""    is_valid: bool
    status: ValidationStatus
    validation_level: ValidationLevel
    
    # Validation details
    validation_time: float
    validator_version: str = "1.0.0"
    schema_type: Optional[SchemaType] = None
    
    # Errors and warnings
    errors: List[SchemaError] = field(default_factory=list)
    warnings: List[SchemaError] = field(default_factory=list)
    
    # Data analysis
    total_fields: int = 0
    validated_fields: int = 0
    missing_fields: List[str] = field(default_factory=list)
    extra_fields: List[str] = field(default_factory=list)
    
    # Schema information
    schema_name: Optional[str] = None
    schema_version: Optional[str] = None
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Additional data
    validated_data: Optional[Dict[str, Any]] = None
    schema_metadata: Dict[str, Any] = field(default_factory=dict)


# Base Pydantic models for content validation
class BaseContentModel(BaseModel):
    """Base model for content validation."""    
    class Config:
        extra = "forbid"
        validate_assignment = True
        use_enum_values = True
        
    @validator('*', pre=True)
    def validate_not_empty_string(cls, v):
        """Validate that string fields are not empty."""        if isinstance(v, str) and v.strip() == '':
            raise ValueError('Field cannot be empty string')
        return v


class ContentMetadataModel(BaseContentModel):
    """Pydantic model for content metadata."""    
    title: StrictStr = Field(..., min_length=1, max_length=200, description="Content title")
    description: Optional[StrictStr] = Field(None, max_length=2000, description="Content description")
    creator_id: StrictStr = Field(..., min_length=1, description="Creator identifier")
    content_type: StrictStr = Field(..., description="Type of content")
    
    # Technical metadata
    file_size: StrictInt = Field(..., gt=0, description="File size in bytes")
    duration: Optional[StrictFloat] = Field(None, gt=0, description="Duration in seconds")
    resolution: Optional[str] = Field(None, regex=r'^\d+x\d+$', description="Resolution (e.g., 1920x1080)")
    bitrate: Optional[StrictInt] = Field(None, gt=0, description="Bitrate in bps")
    
    # Quality metrics
    quality_score: Optional[StrictFloat] = Field(None, ge=0, le=100, description="Quality score (0-100)")
    
    # Timestamps
    created_at: StrictStr = Field(..., description="Creation timestamp")
    updated_at: Optional[StrictStr] = Field(None, description="Last update timestamp")
    
    # Tags and categories
    tags: List[StrictStr] = Field(default_factory=list, max_items=20, description="Content tags")
    categories: List[StrictStr] = Field(default_factory=list, max_items=5, description="Content categories")
    
    @validator('resolution')
    def validate_resolution(cls, v):
        """Validate resolution format."""        if v is not None:
            parts = v.split('x')
            if len(parts) != 2:
                raise ValueError('Resolution must be in format WIDTHxHEIGHT')
            try:
                width, height = int(parts[0]), int(parts[1])
                if width <= 0 or height <= 0:
                    raise ValueError('Resolution dimensions must be positive')
            except ValueError:
                raise ValueError('Resolution must contain valid integers')
        return v
    
    @validator('tags', 'categories')
    def validate_string_lists(cls, v):
        """Validate string lists."""        for item in v:
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValueError('List items must be non-empty strings')
        return v


class AudioContentModel(ContentMetadataModel):
    """Pydantic model for audio content."""    
    content_type: StrictStr = Field("audio", const=True)
    sample_rate: Optional[StrictInt] = Field(None, gt=0, description="Sample rate in Hz")
    channels: Optional[StrictInt] = Field(None, gt=0, le=8, description="Number of audio channels")
    codec: Optional[StrictStr] = Field(None, description="Audio codec")
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        """Validate sample rate."""        if v is not None and v not in [8000, 11025, 16000, 22050, 44100, 48000, 96000, 192000]:
            raise ValueError('Invalid sample rate')
        return v


class VideoContentModel(ContentMetadataModel):
    """Pydantic model for video content."""    
    content_type: StrictStr = Field("video", const=True)
    frame_rate: Optional[StrictFloat] = Field(None, gt=0, le=120, description="Frame rate in fps")
    video_codec: Optional[StrictStr] = Field(None, description="Video codec")
    audio_codec: Optional[StrictStr] = Field(None, description="Audio codec")
    
    @validator('frame_rate')
    def validate_frame_rate(cls, v):
        """Validate frame rate."""        if v is not None:
            common_rates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60, 120]
            if not any(abs(v - rate) < 0.1 for rate in common_rates):
                raise ValueError('Uncommon frame rate detected')
        return v


class ImageContentModel(ContentMetadataModel):
    """Pydantic model for image content."""    
    content_type: StrictStr = Field("image", const=True)
    color_space: Optional[StrictStr] = Field(None, description="Color space")
    has_transparency: Optional[StrictBool] = Field(None, description="Has transparency")
    compression_quality: Optional[StrictInt] = Field(None, ge=1, le=100, description="Compression quality")


class TextContentModel(ContentMetadataModel):
    """Pydantic model for text content."""    
    content_type: StrictStr = Field("text", const=True)
    word_count: Optional[StrictInt] = Field(None, ge=0, description="Word count")
    language: Optional[StrictStr] = Field(None, min_length=2, max_length=5, description="Language code")
    encoding: Optional[StrictStr] = Field("utf-8", description="Text encoding")
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language code."""        if v is not None:
            # Basic language code validation (ISO 639-1 or extended)
            if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
                raise ValueError('Invalid language code format')
        return v


class PlatformRequirementsModel(BaseContentModel):
    """Pydantic model for platform requirements."""    
    platform_name: StrictStr = Field(..., description="Platform name")
    max_file_size: StrictInt = Field(..., gt=0, description="Maximum file size")
    max_duration: Optional[StrictFloat] = Field(None, gt=0, description="Maximum duration")
    supported_formats: List[StrictStr] = Field(..., min_items=1, description="Supported formats")
    min_resolution: Optional[str] = Field(None, description="Minimum resolution")
    max_resolution: Optional[str] = Field(None, description="Maximum resolution")
    aspect_ratios: Optional[List[StrictStr]] = Field(None, description="Supported aspect ratios")
    
    @root_validator
    def validate_resolution_constraints(cls, values):
        """Validate resolution constraints."""        min_res = values.get('min_resolution')
        max_res = values.get('max_resolution')
        
        if min_res and max_res:
            try:
                min_w, min_h = map(int, min_res.split('x'))
                max_w, max_h = map(int, max_res.split('x'))
                
                if min_w > max_w or min_h > max_h:
                    raise ValueError('Minimum resolution cannot exceed maximum resolution')
            except ValueError:
                raise ValueError('Invalid resolution format')
        
        return values


class SchemaValidator:
    """    Advanced schema validator for the IA Influencer Agent Platform.
    
    Provides comprehensive schema validation with Pydantic models,
    JSON Schema validation, and custom validation rules.
    """    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enable_strict_mode: bool = False
    ):
        """        Initialize schema validator.
        
        Args:
            config: Validator configuration
            enable_strict_mode: Enable strict validation mode
        """        self.config = config or {}
        self.enable_strict_mode = enable_strict_mode
        
        # Pydantic models registry
        self.pydantic_models = self._init_pydantic_models()
        
        # JSON schemas registry
        self.json_schemas = self._init_json_schemas()
        
        # Custom validators
        self.custom_validators = self._init_custom_validators()
        
        # Validation rules
        self.validation_rules = self._init_validation_rules()
        
        logger.info("SchemaValidator initialized with strict_mode=%s", enable_strict_mode)
    
    async def validate_data(
        self,
        data: Dict[str, Any],
        schema_name: str,
        schema_type: SchemaType = SchemaType.PYDANTIC,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> SchemaValidationResult:
        """        Validate data against schema.
        
        Args:
            data: Data to validate
            schema_name: Name of schema to use
            schema_type: Type of schema validation
            validation_level: Validation strictness level
            
        Returns:
            Schema validation result
        """        start_time = time.time()
        
        try:
            result = SchemaValidationResult(
                is_valid=True,
                status=ValidationStatus.VALID,
                validation_level=validation_level,
                validation_time=0.0,
                schema_type=schema_type,
                schema_name=schema_name
            )
            
            # Count total fields
            result.total_fields = self._count_fields_recursive(data)
            
            # Validate based on schema type
            if schema_type == SchemaType.PYDANTIC:
                await self._validate_with_pydantic(data, schema_name, result)
            elif schema_type == SchemaType.JSON_SCHEMA:
                await self._validate_with_json_schema(data, schema_name, result)
            else:
                result.errors.append(SchemaError(
                    field_path="",
                    error_type="unsupported_schema",
                    message=f"Schema type {schema_type.value} not supported"
                ))
            
            # Apply validation level rules
            await self._apply_validation_level_rules(data, result, validation_level)
            
            # Custom validation rules
            await self._apply_custom_validation(data, schema_name, result)
            
            # Generate recommendations
            await self._generate_schema_recommendations(result)
            
            # Finalize result
            result.validation_time = time.time() - start_time
            result.is_valid = len(result.errors) == 0
            
            if result.errors:
                result.status = ValidationStatus.INVALID
            elif result.warnings:
                result.status = ValidationStatus.WARNING
            
            result.validated_fields = result.total_fields - len(result.errors)
            
            logger.info(f"Schema validation completed: {result.is_valid} ({result.validated_fields}/{result.total_fields} fields)")
            return result
            
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return self._create_error_result(str(e), validation_level)
    
    async def validate_batch(
        self,
        data_items: List[Dict[str, Any]],
        schema_mappings: Dict[int, str],
        schema_type: SchemaType = SchemaType.PYDANTIC,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        max_workers: int = 4
    ) -> List[SchemaValidationResult]:
        """        Validate multiple data items in batch.
        
        Args:
            data_items: List of data items to validate
            schema_mappings: Mapping of item index to schema name
            schema_type: Schema type
            validation_level: Validation level
            max_workers: Maximum concurrent workers
            
        Returns:
            List of validation results
        """        try:
            semaphore = asyncio.Semaphore(max_workers)
            
            async def validate_item(index, data):
                async with semaphore:
                    schema_name = schema_mappings.get(index, "base_content")
                    return await self.validate_data(
                        data=data,
                        schema_name=schema_name,
                        schema_type=schema_type,
                        validation_level=validation_level
                    )
            
            tasks = [validate_item(i, data) for i, data in enumerate(data_items)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(
                        self._create_error_result(str(result), validation_level)
                    )
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Batch schema validation failed: {str(e)}")
            return [self._create_error_result(str(e), validation_level) for _ in data_items]
    
    async def validate_schema_definition(
        self,
        schema_definition: Dict[str, Any],
        schema_type: SchemaType = SchemaType.JSON_SCHEMA
    ) -> SchemaValidationResult:
        """        Validate schema definition itself.
        
        Args:
            schema_definition: Schema definition to validate
            schema_type: Type of schema
            
        Returns:
            Validation result for schema definition
        """        try:
            result = SchemaValidationResult(
                is_valid=True,
                status=ValidationStatus.VALID,
                validation_level=ValidationLevel.STANDARD,
                validation_time=0.0,
                schema_type=schema_type
            )
            
            if schema_type == SchemaType.JSON_SCHEMA:
                # Validate JSON Schema syntax
                try:
                    Draft7Validator.check_schema(schema_definition)
                except jsonschema.SchemaError as e:
                    result.errors.append(SchemaError(
                        field_path=str(e.absolute_path),
                        error_type="schema_error",
                        message=str(e.message),
                        suggestion="Fix schema definition syntax"
                    ))
            
            result.is_valid = len(result.errors) == 0
            if result.errors:
                result.status = ValidationStatus.INVALID
            
            return result
            
        except Exception as e:
            logger.error(f"Schema definition validation failed: {str(e)}")
            return self._create_error_result(str(e), ValidationLevel.STANDARD)
    
    async def convert_pydantic_to_json_schema(
        self,
        model_name: str
    ) -> Optional[Dict[str, Any]]:
        """        Convert Pydantic model to JSON Schema.
        
        Args:
            model_name: Name of Pydantic model
            
        Returns:
            JSON Schema definition or None if model not found
        """        try:
            if model_name not in self.pydantic_models:
                return None
            
            model_class = self.pydantic_models[model_name]
            return model_class.schema()
            
        except Exception as e:
            logger.error(f"Pydantic to JSON Schema conversion failed: {str(e)}")
            return None
    
    async def generate_sample_data(
        self,
        schema_name: str,
        schema_type: SchemaType = SchemaType.PYDANTIC
    ) -> Optional[Dict[str, Any]]:
        """        Generate sample data for schema.
        
        Args:
            schema_name: Schema name
            schema_type: Schema type
            
        Returns:
            Sample data or None if generation failed
        """        try:
            if schema_type == SchemaType.PYDANTIC and schema_name in self.pydantic_models:
                model_class = self.pydantic_models[schema_name]
                schema = model_class.schema()
                return self._generate_sample_from_json_schema(schema)
            
            elif schema_type == SchemaType.JSON_SCHEMA and schema_name in self.json_schemas:
                schema = self.json_schemas[schema_name]
                return self._generate_sample_from_json_schema(schema)
            
            return None
            
        except Exception as e:
            logger.error(f"Sample data generation failed: {str(e)}")
            return None
    
    async def _validate_with_pydantic(
        self,
        data: Dict[str, Any],
        schema_name: str,
        result: SchemaValidationResult
    ):
        """Validate data with Pydantic model."""        try:
            if schema_name not in self.pydantic_models:
                result.errors.append(SchemaError(
                    field_path="",
                    error_type="schema_not_found",
                    message=f"Pydantic model '{schema_name}' not found",
                    suggestion="Check available schema names"
                ))
                return
            
            model_class = self.pydantic_models[schema_name]
            
            try:
                # Validate data
                validated_model = model_class(**data)
                result.validated_data = validated_model.dict()
                
            except ValidationError as e:
                # Convert Pydantic errors to our format
                for error in e.errors():
                    field_path = ".".join(str(loc) for loc in error["loc"])
                    
                    result.errors.append(SchemaError(
                        field_path=field_path,
                        error_type=error["type"],
                        message=error["msg"],
                        actual_value=error.get("input"),
                        suggestion=self._get_pydantic_error_suggestion(error)
                    ))
            
        except Exception as e:
            logger.error(f"Pydantic validation failed: {str(e)}")
            result.errors.append(SchemaError(
                field_path="",
                error_type="validation_error",
                message=f"Pydantic validation error: {str(e)}"
            ))
    
    async def _validate_with_json_schema(
        self,
        data: Dict[str, Any],
        schema_name: str,
        result: SchemaValidationResult
    ):
        """Validate data with JSON Schema."""        try:
            if schema_name not in self.json_schemas:
                result.errors.append(SchemaError(
                    field_path="",
                    error_type="schema_not_found",
                    message=f"JSON Schema '{schema_name}' not found",
                    suggestion="Check available schema names"
                ))
                return
            
            schema = self.json_schemas[schema_name]
            validator = Draft7Validator(schema)
            
            # Validate data
            errors = list(validator.iter_errors(data))
            
            for error in errors:
                field_path = ".".join(str(item) for item in error.absolute_path)
                
                result.errors.append(SchemaError(
                    field_path=field_path,
                    error_type="validation_error",
                    message=error.message,
                    actual_value=error.instance,
                    constraint=str(error.validator_value) if error.validator_value else None,
                    suggestion=self._get_json_schema_error_suggestion(error)
                ))
            
            if not errors:
                result.validated_data = data
            
        except Exception as e:
            logger.error(f"JSON Schema validation failed: {str(e)}")
            result.errors.append(SchemaError(
                field_path="",
                error_type="validation_error",
                message=f"JSON Schema validation error: {str(e)}"
            ))
    
    async def _apply_validation_level_rules(
        self,
        data: Dict[str, Any],
        result: SchemaValidationResult,
        level: ValidationLevel
    ):
        """Apply validation rules based on level."""        try:
            if level == ValidationLevel.BASIC:
                # Basic validation - only check required fields
                pass
            
            elif level == ValidationLevel.STANDARD:
                # Standard validation - check types and basic constraints
                await self._check_data_types(data, result)
            
            elif level == ValidationLevel.STRICT:
                # Strict validation - comprehensive checks
                await self._check_data_types(data, result)
                await self._check_business_rules(data, result)
                await self._check_data_consistency(data, result)
            
            elif level == ValidationLevel.ENTERPRISE:
                # Enterprise validation - all checks plus security
                await self._check_data_types(data, result)
                await self._check_business_rules(data, result)
                await self._check_data_consistency(data, result)
                await self._check_security_constraints(data, result)
            
        except Exception as e:
            logger.error(f"Validation level rules failed: {str(e)}")
    
    async def _apply_custom_validation(
        self,
        data: Dict[str, Any],
        schema_name: str,
        result: SchemaValidationResult
    ):
        """Apply custom validation rules."""        try:
            if schema_name in self.custom_validators:
                validators = self.custom_validators[schema_name]
                
                for validator_func in validators:
                    try:
                        validator_result = await validator_func(data)
                        if not validator_result.get("valid", True):
                            result.errors.append(SchemaError(
                                field_path=validator_result.get("field", ""),
                                error_type="custom_validation",
                                message=validator_result.get("message", "Custom validation failed"),
                                suggestion=validator_result.get("suggestion")
                            ))
                    except Exception as e:
                        logger.error(f"Custom validator failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Custom validation failed: {str(e)}")
    
    async def _check_data_types(self, data: Dict[str, Any], result: SchemaValidationResult):
        """Check data types consistency."""        try:
            for key, value in data.items():
                if isinstance(value, str) and value.strip() == "":
                    result.warnings.append(SchemaError(
                        field_path=key,
                        error_type="empty_string",
                        message=f"Field '{key}' contains empty string",
                        suggestion="Provide meaningful value or use null"
                    ))
                
                elif isinstance(value, (int, float)) and value < 0:
                    if key.endswith(('_size', '_count', '_duration', '_score')):
                        result.warnings.append(SchemaError(
                            field_path=key,
                            error_type="negative_value",
                            message=f"Field '{key}' has negative value: {value}",
                            suggestion="Use positive value for size/count/duration fields"
                        ))
            
        except Exception as e:
            logger.error(f"Data type check failed: {str(e)}")
    
    async def _check_business_rules(self, data: Dict[str, Any], result: SchemaValidationResult):
        """Check business logic rules."""        try:
            # Content-specific business rules
            if "content_type" in data:
                content_type = data["content_type"]
                
                # Audio-specific rules
                if content_type == "audio":
                    if "duration" in data and data["duration"] > 3600:  # 1 hour
                        result.warnings.append(SchemaError(
                            field_path="duration",
                            error_type="business_rule",
                            message="Audio duration exceeds 1 hour",
                            suggestion="Consider splitting into shorter segments"
                        ))
                
                # Video-specific rules
                elif content_type == "video":
                    if "file_size" in data and data["file_size"] > 4 * 1024 * 1024 * 1024:  # 4GB
                        result.warnings.append(SchemaError(
                            field_path="file_size",
                            error_type="business_rule",
                            message="Video file size exceeds 4GB",
                            suggestion="Compress video or reduce quality"
                        ))
            
            # Quality score rules
            if "quality_score" in data and data["quality_score"] < 60:
                result.warnings.append(SchemaError(
                    field_path="quality_score",
                    error_type="business_rule",
                    message="Quality score below recommended threshold",
                    suggestion="Improve content quality"
                ))
            
        except Exception as e:
            logger.error(f"Business rules check failed: {str(e)}")
    
    async def _check_data_consistency(self, data: Dict[str, Any], result: SchemaValidationResult):
        """Check data consistency across fields."""        try:
            # Check timestamp consistency
            if "created_at" in data and "updated_at" in data:
                # In a real implementation, would parse timestamps and compare
                pass
            
            # Check resolution vs file size consistency
            if all(key in data for key in ["resolution", "file_size", "content_type"]):
                if data["content_type"] in ["image", "video"]:
                    # Basic consistency check - could be more sophisticated
                    resolution = data["resolution"]
                    file_size = data["file_size"]
                    
                    if "x" in resolution:
                        try:
                            width, height = map(int, resolution.split("x"))
                            expected_min_size = (width * height) / 1000  # Very rough estimate
                            
                            if file_size < expected_min_size:
                                result.warnings.append(SchemaError(
                                    field_path="file_size",
                                    error_type="consistency",
                                    message="File size seems small for given resolution",
                                    suggestion="Verify file integrity"
                                ))
                        except ValueError:
                            pass
            
        except Exception as e:
            logger.error(f"Data consistency check failed: {str(e)}")
    
    async def _check_security_constraints(self, data: Dict[str, Any], result: SchemaValidationResult):
        """Check security-related constraints."""        try:
            # Check for potentially dangerous values
            for key, value in data.items():
                if isinstance(value, str):
                    # Check for script injection patterns
                    if any(pattern in value.lower() for pattern in ['<script', 'javascript:', 'eval(']):
                        result.errors.append(SchemaError(
                            field_path=key,
                            error_type="security",
                            message=f"Potentially dangerous content in field '{key}'",
                            suggestion="Remove script content"
                        ))
                    
                    # Check for SQL injection patterns
                    if any(pattern in value.lower() for pattern in ['drop table', 'delete from', 'union select']):
                        result.errors.append(SchemaError(
                            field_path=key,
                            error_type="security",
                            message=f"Potentially dangerous SQL content in field '{key}'",
                            suggestion="Sanitize input"
                        ))
            
        except Exception as e:
            logger.error(f"Security constraints check failed: {str(e)}")
    
    async def _generate_schema_recommendations(self, result: SchemaValidationResult):
        """Generate schema validation recommendations."""        try:
            recommendations = []
            
            # Error-based recommendations
            error_types = set(error.error_type for error in result.errors)
            
            if "required" in error_types:
                recommendations.append("Add missing required fields")
            
            if "type" in error_types:
                recommendations.append("Fix data type mismatches")
            
            if "format" in error_types:
                recommendations.append("Correct field format issues")
            
            # Warning-based recommendations
            if result.warnings:
                warning_types = set(warning.error_type for warning in result.warnings)
                
                if "business_rule" in warning_types:
                    recommendations.append("Review business rule violations")
                
                if "consistency" in warning_types:
                    recommendations.append("Check data consistency across fields")
            
            # Validation level recommendations
            if result.validation_level == ValidationLevel.BASIC and result.is_valid:
                recommendations.append("Consider using higher validation level for production")
            
            result.recommendations = recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
    
    def _count_fields_recursive(self, data: Any, path: str = "") -> int:
        """Count fields recursively in data structure."""        try:
            if isinstance(data, dict):
                count = 0
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    count += 1  # Count the field itself
                    if isinstance(value, (dict, list)):
                        count += self._count_fields_recursive(value, current_path)
                return count
            
            elif isinstance(data, list):
                count = 0
                for i, item in enumerate(data):
                    current_path = f"{path}[{i}]"
                    if isinstance(item, (dict, list)):
                        count += self._count_fields_recursive(item, current_path)
                    else:
                        count += 1
                return count
            
            else:
                return 1
            
        except Exception:
            return 0
    
    def _get_pydantic_error_suggestion(self, error: Dict[str, Any]) -> Optional[str]:
        """Get suggestion for Pydantic validation error."""        error_type = error.get("type", "")
        
        suggestions = {
            "missing": "Provide the required field",
            "type_error": "Use the correct data type",
            "value_error": "Provide a valid value",
            "length": "Adjust the length to meet requirements",
            "regex": "Match the required pattern",
            "const": "Use the exact required value",
            "enum": "Use one of the allowed values"
        }
        
        return suggestions.get(error_type)
    
    def _get_json_schema_error_suggestion(self, error) -> Optional[str]:
        """Get suggestion for JSON Schema validation error."""        validator = error.validator
        
        suggestions = {
            "required": "Add the missing required property",
            "type": "Use the correct data type",
            "format": "Use the correct format",
            "pattern": "Match the required pattern",
            "minimum": "Use a larger value",
            "maximum": "Use a smaller value",
            "minLength": "Use a longer string",
            "maxLength": "Use a shorter string",
            "enum": "Use one of the allowed values",
            "const": "Use the exact required value"
        }
        
        return suggestions.get(validator)
    
    def _generate_sample_from_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample data from JSON Schema."""        try:
            def generate_value(prop_schema):
                prop_type = prop_schema.get("type", "string")
                
                if prop_type == "string":
                    if "enum" in prop_schema:
                        return prop_schema["enum"][0]
                    return "sample_string"
                
                elif prop_type == "integer":
                    return 42
                
                elif prop_type == "number":
                    return 3.14
                
                elif prop_type == "boolean":
                    return True
                
                elif prop_type == "array":
                    items_schema = prop_schema.get("items", {"type": "string"})
                    return [generate_value(items_schema)]
                
                elif prop_type == "object":
                    obj_properties = prop_schema.get("properties", {})
                    return {key: generate_value(value) for key, value in obj_properties.items()}
                
                else:
                    return None
            
            properties = schema.get("properties", {})
            sample_data = {}
            
            for key, prop_schema in properties.items():
                sample_data[key] = generate_value(prop_schema)
            
            return sample_data
            
        except Exception as e:
            logger.error(f"Sample data generation failed: {str(e)}")
            return {}
    
    def _create_error_result(self, error_message: str, validation_level: ValidationLevel) -> SchemaValidationResult:
        """Create error validation result."""        return SchemaValidationResult(
            is_valid=False,
            status=ValidationStatus.ERROR,
            validation_level=validation_level,
            validation_time=0.0,
            errors=[SchemaError(
                field_path="",
                error_type="system_error",
                message=error_message
            )]
        )
    
    def _init_pydantic_models(self) -> Dict[str, Type[BaseModel]]:
        """Initialize Pydantic models registry."""        return {
            "base_content": BaseContentModel,
            "content_metadata": ContentMetadataModel,
            "audio_content": AudioContentModel,
            "video_content": VideoContentModel,
            "image_content": ImageContentModel,
            "text_content": TextContentModel,
            "platform_requirements": PlatformRequirementsModel
        }
    
    def _init_json_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize JSON schemas registry."""        return {
            "basic_content": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 1},
                    "content_type": {"type": "string", "enum": ["audio", "video", "image", "text"]},
                    "creator_id": {"type": "string", "minLength": 1}
                },
                "required": ["title", "content_type", "creator_id"],
                "additionalProperties": False
            },
            "platform_config": {
                "type": "object",
                "properties": {
                    "platform_name": {"type": "string"},
                    "max_file_size": {"type": "integer", "minimum": 1},
                    "supported_formats": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                },
                "required": ["platform_name", "max_file_size", "supported_formats"]
            }
        }
    
    def _init_custom_validators(self) -> Dict[str, List[Callable]]:
        """Initialize custom validators."""        async def validate_content_title(data):
            """Custom validator for content titles."""            title = data.get("title", "")
            if len(title) < 5:
                return {
                    "valid": False,
                    "field": "title",
                    "message": "Title too short for SEO optimization",
                    "suggestion": "Use at least 5 characters for better discoverability"
                }
            return {"valid": True}
        
        async def validate_quality_metrics(data):
            """Custom validator for quality metrics."""            quality_score = data.get("quality_score")
            file_size = data.get("file_size")
            
            if quality_score and file_size:
                if quality_score > 90 and file_size < 1024 * 1024:  # < 1MB
                    return {
                        "valid": False,
                        "field": "quality_score",
                        "message": "High quality score with small file size is unusual",
                        "suggestion": "Verify quality assessment accuracy"
                    }
            
            return {"valid": True}
        
        return {
            "content_metadata": [validate_content_title, validate_quality_metrics],
            "audio_content": [validate_content_title, validate_quality_metrics],
            "video_content": [validate_content_title, validate_quality_metrics],
            "image_content": [validate_content_title, validate_quality_metrics]
        }
    
    def _init_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules configuration."""        return {
            "strict_types": self.enable_strict_mode,
            "allow_extra_fields": not self.enable_strict_mode,
            "validate_formats": True,
            "check_business_rules": True,
            "security_validation": True
        }
