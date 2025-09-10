"""Schema Metadata Validator - Consolidated Schema & Metadata Validation
========================================================================

Industrial-grade schema validation and metadata extraction system for the
IA Influencer Agent Platform, combining JSON/XML schema validation, enriched
AI-powered metadata extraction, and cross-platform metadata mapping.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Consolidated Validation Capabilities:
- JSON/XML schema validation with enterprise patterns
- AI-powered metadata extraction and enrichment
- SEO tags and descriptions validation
- Cross-platform metadata format mapping
- Automatic metadata optimization suggestions
- Schema compliance verification
- Metadata quality assessment and scoring
"""

import asyncio
import logging
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import re
import mimetypes
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Schema validation strictness levels."""
    STRICT = "strict"
    NORMAL = "normal"
    PERMISSIVE = "permissive"

class SchemaType(Enum):
    """Supported schema types."""
    JSON_SCHEMA = "json_schema"
    XML_SCHEMA = "xml_schema"
    CUSTOM_SCHEMA = "custom_schema"
    PLATFORM_SCHEMA = "platform_schema"
    CONTENT_SCHEMA = "content_schema"

class ValidationStatus(Enum):
    """Schema validation status."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    UNKNOWN = "unknown"

class MetadataFormat(Enum):
    """Metadata format types."""
    DUBLIN_CORE = "dublin_core"
    SCHEMA_ORG = "schema_org"
    OPEN_GRAPH = "open_graph"
    TWITTER_CARDS = "twitter_cards"
    JSON_LD = "json_ld"
    CUSTOM = "custom"

class MetadataQuality(Enum):
    """Metadata quality levels."""
    POOR = "poor"
    BASIC = "basic"
    GOOD = "good"
    EXCELLENT = "excellent"
    OPTIMAL = "optimal"

class MetadataValidationType(Enum):
    """Types of metadata validation."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    SEO_OPTIMIZATION = "seo_optimization"
    PLATFORM_COMPLIANCE = "platform_compliance"
    ACCESSIBILITY = "accessibility"

@dataclass
class SchemaValidationError:
    """Schema validation error details."""
    error_type: str
    message: str
    path: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    severity: str = "error"
    suggestion: Optional[str] = None

@dataclass
class SchemaValidationResult:
    """Schema validation result."""
    is_valid: bool
    validation_status: ValidationStatus
    schema_type: SchemaType
    errors: List[SchemaValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_version: Optional[str] = None
    compliance_score: float = 0.0
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_duration_ms: int = 0

@dataclass
class MetadataField:
    """Metadata field definition."""
    name: str
    value: Any
    format_type: MetadataFormat
    is_required: bool = False
    quality_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)
    platform_specific: Optional[str] = None

@dataclass
class MetadataValidationIssue:
    """Metadata validation issue."""
    field_name: str
    issue_type: MetadataValidationType
    severity: str
    description: str
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None
    impact: str = "medium"

@dataclass
class MetadataValidationResult:
    """Metadata validation result."""
    is_valid: bool
    quality_level: MetadataQuality
    completeness_score: float
    seo_score: float
    platform_compliance_score: float
    fields: List[MetadataField] = field(default_factory=list)
    issues: List[MetadataValidationIssue] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    extracted_metadata: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CreatorProfile:
    """Creator profile metadata."""
    creator_id: str
    name: str
    platform_handles: Dict[str, str] = field(default_factory=dict)
    content_categories: List[str] = field(default_factory=list)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    verification_status: bool = False

@dataclass
class ContentMetadata:
    """Content metadata structure."""
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    duration: Optional[int] = None
    file_size: Optional[int] = None
    creation_date: Optional[datetime] = None
    creator_profile: Optional[CreatorProfile] = None
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    seo_metadata: Dict[str, Any] = field(default_factory=dict)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformConfiguration:
    """Platform-specific metadata configuration."""
    platform_name: str
    required_fields: List[str]
    optional_fields: List[str]
    field_limits: Dict[str, Dict[str, Any]]
    metadata_format: MetadataFormat
    validation_rules: Dict[str, Any]

class SchemaMetadataValidator:
    """Consolidated schema and metadata validation system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the schema metadata validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.schema_definitions = self._load_schema_definitions()
        self.metadata_standards = self._load_metadata_standards()
        self.platform_configs = self._load_platform_configurations()
        
        # Validation settings
        self.validation_level = ValidationLevel(self.config.get('validation_level', 'normal'))
        self.enable_ai_enhancement = self.config.get('enable_ai_enhancement', True)
        self.auto_fix_enabled = self.config.get('auto_fix_enabled', False)
        self.seo_optimization_enabled = self.config.get('seo_optimization_enabled', True)
        
        logger.info("SchemaMetadataValidator initialized")
    
    def _load_schema_definitions(self) -> Dict[SchemaType, Dict[str, Any]]:
        """Load schema definitions for validation.
        
        Returns:
            Dictionary of schema definitions by type
        """
        schemas = {
            SchemaType.CONTENT_SCHEMA: {
                "type": "object",
                "required": ["title", "description", "content_type"],
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 5000
                    },
                    "content_type": {
                        "type": "string",
                        "enum": ["video", "audio", "image", "text", "mixed"]
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 50
                    },
                    "category": {
                        "type": "string",
                        "minLength": 1
                    },
                    "language": {
                        "type": "string",
                        "pattern": "^[a-z]{2}(-[A-Z]{2})?$"
                    }
                }
            },
            SchemaType.PLATFORM_SCHEMA: {
                "youtube": {
                    "required": ["title", "description"],
                    "title": {"maxLength": 100},
                    "description": {"maxLength": 5000},
                    "tags": {"maxItems": 500}
                },
                "instagram": {
                    "required": ["caption"],
                    "caption": {"maxLength": 2200},
                    "hashtags": {"maxItems": 30}
                },
                "tiktok": {
                    "required": ["caption"],
                    "caption": {"maxLength": 4000},
                    "hashtags": {"maxItems": 100}
                }
            }
        }
        return schemas
    
    def _load_metadata_standards(self) -> Dict[MetadataFormat, Dict[str, Any]]:
        """Load metadata format standards.
        
        Returns:
            Dictionary of metadata standards by format
        """
        standards = {
            MetadataFormat.DUBLIN_CORE: {
                "core_elements": [
                    "title", "creator", "subject", "description",
                    "publisher", "contributor", "date", "type",
                    "format", "identifier", "source", "language",
                    "relation", "coverage", "rights"
                ],
                "namespace": "http://purl.org/dc/elements/1.1/"
            },
            MetadataFormat.SCHEMA_ORG: {
                "content_types": {
                    "VideoObject": ["name", "description", "thumbnailUrl", "uploadDate", "duration"],
                    "AudioObject": ["name", "description", "duration", "encodingFormat"],
                    "ImageObject": ["name", "description", "contentUrl", "width", "height"],
                    "Article": ["headline", "description", "author", "datePublished"]
                },
                "namespace": "https://schema.org/"
            },
            MetadataFormat.OPEN_GRAPH: {
                "required": ["og:title", "og:type", "og:image", "og:url"],
                "recommended": ["og:description", "og:site_name", "og:locale"],
                "namespace": "http://ogp.me/ns#"
            },
            MetadataFormat.TWITTER_CARDS: {
                "summary": ["twitter:card", "twitter:title", "twitter:description", "twitter:image"],
                "summary_large_image": ["twitter:card", "twitter:title", "twitter:description", "twitter:image"],
                "player": ["twitter:card", "twitter:title", "twitter:description", "twitter:player"]
            }
        }
        return standards
    
    def _load_platform_configurations(self) -> Dict[str, PlatformConfiguration]:
        """Load platform-specific metadata configurations.
        
        Returns:
            Dictionary of platform configurations
        """
        configs = {
            "youtube": PlatformConfiguration(
                platform_name="youtube",
                required_fields=["title", "description"],
                optional_fields=["tags", "category", "thumbnail", "privacy"],
                field_limits={
                    "title": {"max_length": 100, "min_length": 1},
                    "description": {"max_length": 5000, "min_length": 10},
                    "tags": {"max_items": 500, "max_length_per_tag": 100}
                },
                metadata_format=MetadataFormat.SCHEMA_ORG,
                validation_rules={
                    "title_keywords": True,
                    "description_seo": True,
                    "thumbnail_required": True
                }
            ),
            "instagram": PlatformConfiguration(
                platform_name="instagram",
                required_fields=["caption"],
                optional_fields=["hashtags", "location", "mentions"],
                field_limits={
                    "caption": {"max_length": 2200, "min_length": 1},
                    "hashtags": {"max_items": 30, "max_length_per_tag": 100}
                },
                metadata_format=MetadataFormat.OPEN_GRAPH,
                validation_rules={
                    "hashtag_relevance": True,
                    "engagement_optimization": True
                }
            ),
            "tiktok": PlatformConfiguration(
                platform_name="tiktok",
                required_fields=["caption"],
                optional_fields=["hashtags", "sounds", "effects"],
                field_limits={
                    "caption": {"max_length": 4000, "min_length": 1},
                    "hashtags": {"max_items": 100, "max_length_per_tag": 100}
                },
                metadata_format=MetadataFormat.JSON_LD,
                validation_rules={
                    "trending_hashtags": True,
                    "viral_optimization": True
                }
            ),
            "spotify": PlatformConfiguration(
                platform_name="spotify",
                required_fields=["title", "artist", "album"],
                optional_fields=["genre", "description", "release_date"],
                field_limits={
                    "title": {"max_length": 100, "min_length": 1},
                    "description": {"max_length": 4000, "min_length": 10},
                    "genre": {"allowed_values": ["Music", "Podcast", "Audiobook"]}
                },
                metadata_format=MetadataFormat.DUBLIN_CORE,
                validation_rules={
                    "audio_metadata": True,
                    "copyright_info": True
                }
            )
        }
        return configs
    
    async def validate_schema(self, data: Union[Dict[str, Any], str, Path],
                            schema_type: SchemaType = SchemaType.CONTENT_SCHEMA,
                            custom_schema: Optional[Dict[str, Any]] = None) -> SchemaValidationResult:
        """Validate data against specified schema.
        
        Args:
            data: Data to validate (dict, JSON string, or file path)
            schema_type: Type of schema to validate against
            custom_schema: Optional custom schema definition
            
        Returns:
            SchemaValidationResult with validation details
        """
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            # Parse input data
            if isinstance(data, Path):
                with open(data, 'r', encoding='utf-8') as f:
                    parsed_data = json.load(f)
            elif isinstance(data, str):
                parsed_data = json.loads(data)
            else:
                parsed_data = data
            
            # Get schema definition
            if custom_schema:
                schema = custom_schema
            else:
                schema = self.schema_definitions.get(schema_type, {})
            
            if not schema:
                return SchemaValidationResult(
                    is_valid=False,
                    validation_status=ValidationStatus.UNKNOWN,
                    schema_type=schema_type,
                    errors=[SchemaValidationError(
                        error_type="schema_not_found",
                        message=f"Schema definition not found for {schema_type.value}",
                        path="root"
                    )]
                )
            
            # Validate against schema
            validation_errors = await self._validate_against_schema(parsed_data, schema, "")
            errors.extend(validation_errors)
            
            # Additional validations based on validation level
            if self.validation_level == ValidationLevel.STRICT:
                strict_errors = await self._strict_schema_validation(parsed_data, schema)
                errors.extend(strict_errors)
            
            # Calculate compliance score
            total_checks = len(schema.get('required', [])) + len(schema.get('properties', {}))
            if total_checks > 0:
                compliance_score = max(0.0, 1.0 - (len(errors) / total_checks))
            else:
                compliance_score = 1.0 if not errors else 0.0
            
            # Determine validation status
            if errors:
                validation_status = ValidationStatus.INVALID
            elif warnings:
                validation_status = ValidationStatus.WARNING
            else:
                validation_status = ValidationStatus.VALID
            
            is_valid = validation_status in [ValidationStatus.VALID, ValidationStatus.WARNING]
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SchemaValidationResult(
                is_valid=is_valid,
                validation_status=validation_status,
                schema_type=schema_type,
                errors=errors,
                warnings=warnings,
                schema_version=schema.get('version', '1.0'),
                compliance_score=compliance_score,
                validated_at=start_time,
                validation_duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return SchemaValidationResult(
                is_valid=False,
                validation_status=ValidationStatus.INVALID,
                schema_type=schema_type,
                errors=[SchemaValidationError(
                    error_type="validation_error",
                    message=f"Schema validation error: {str(e)}",
                    path="root"
                )],
                validation_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def extract_metadata(self, content: Union[str, bytes, Path],
                             content_type: str = "auto",
                             ai_enhancement: bool = None) -> MetadataValidationResult:
        """Extract and validate metadata from content.
        
        Args:
            content: Content to extract metadata from
            content_type: Type of content (auto-detect if "auto")
            ai_enhancement: Enable AI-powered metadata enhancement
            
        Returns:
            MetadataValidationResult with extracted metadata
        """
        start_time = datetime.now()
        
        try:
            # Auto-detect content type if needed
            if content_type == "auto":
                content_type = await self._detect_content_type(content)
            
            # Extract basic metadata
            basic_metadata = await self._extract_basic_metadata(content, content_type)
            
            # Extract format-specific metadata
            format_metadata = await self._extract_format_specific_metadata(content, content_type)
            
            # Combine metadata
            extracted_metadata = {**basic_metadata, **format_metadata}
            
            # AI enhancement if enabled
            if ai_enhancement or (ai_enhancement is None and self.enable_ai_enhancement):
                ai_metadata = await self._ai_enhance_metadata(extracted_metadata, content_type)
                extracted_metadata.update(ai_metadata)
            
            # Create metadata fields
            fields = self._create_metadata_fields(extracted_metadata)
            
            # Validate metadata quality
            quality_result = await self._assess_metadata_quality(fields, content_type)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_metadata_optimizations(
                fields, quality_result, content_type
            )
            
            # Validate against metadata standards
            issues = await self._validate_metadata_standards(fields)
            
            return MetadataValidationResult(
                is_valid=quality_result['is_valid'],
                quality_level=quality_result['quality_level'],
                completeness_score=quality_result['completeness_score'],
                seo_score=quality_result['seo_score'],
                platform_compliance_score=quality_result['platform_compliance_score'],
                fields=fields,
                issues=issues,
                optimization_suggestions=optimization_suggestions,
                extracted_metadata=extracted_metadata,
                validated_at=start_time
            )
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return MetadataValidationResult(
                is_valid=False,
                quality_level=MetadataQuality.POOR,
                completeness_score=0.0,
                seo_score=0.0,
                platform_compliance_score=0.0,
                issues=[MetadataValidationIssue(
                    field_name="extraction_error",
                    issue_type=MetadataValidationType.COMPLETENESS,
                    severity="error",
                    description=f"Metadata extraction failed: {str(e)}"
                )],
                extracted_metadata={},
                validated_at=start_time
            )
    
    async def _validate_against_schema(self, data: Dict[str, Any], 
                                     schema: Dict[str, Any], 
                                     path: str) -> List[SchemaValidationError]:
        """Validate data against schema definition.
        
        Args:
            data: Data to validate
            schema: Schema definition
            path: Current validation path
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                errors.append(SchemaValidationError(
                    error_type="missing_required_field",
                    message=f"Required field '{field}' is missing",
                    path=f"{path}.{field}" if path else field,
                    suggestion=f"Add required field '{field}'"
                ))
        
        # Validate properties
        properties = schema.get('properties', {})
        for field_name, field_schema in properties.items():
            if field_name in data:
                field_errors = await self._validate_field(
                    data[field_name], field_schema, f"{path}.{field_name}" if path else field_name
                )
                errors.extend(field_errors)
        
        return errors
    
    async def _validate_field(self, value: Any, field_schema: Dict[str, Any], 
                            path: str) -> List[SchemaValidationError]:
        """Validate a single field against its schema.
        
        Args:
            value: Field value
            field_schema: Field schema definition
            path: Field path
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Type validation
        expected_type = field_schema.get('type')
        if expected_type:
            if not self._check_type(value, expected_type):
                errors.append(SchemaValidationError(
                    error_type="type_mismatch",
                    message=f"Expected type '{expected_type}', got '{type(value).__name__}'",
                    path=path,
                    expected=expected_type,
                    actual=type(value).__name__
                ))
        
        # String validations
        if isinstance(value, str):
            # Length validations
            min_length = field_schema.get('minLength')
            if min_length and len(value) < min_length:
                errors.append(SchemaValidationError(
                    error_type="min_length_violation",
                    message=f"String too short: {len(value)} < {min_length}",
                    path=path,
                    suggestion=f"Extend content to at least {min_length} characters"
                ))
            
            max_length = field_schema.get('maxLength')
            if max_length and len(value) > max_length:
                errors.append(SchemaValidationError(
                    error_type="max_length_violation",
                    message=f"String too long: {len(value)} > {max_length}",
                    path=path,
                    suggestion=f"Reduce content to at most {max_length} characters"
                ))
            
            # Pattern validation
            pattern = field_schema.get('pattern')
            if pattern and not re.match(pattern, value):
                errors.append(SchemaValidationError(
                    error_type="pattern_violation",
                    message=f"String does not match required pattern: {pattern}",
                    path=path,
                    suggestion=f"Ensure value matches pattern: {pattern}"
                ))
        
        # Array validations
        elif isinstance(value, list):
            max_items = field_schema.get('maxItems')
            if max_items and len(value) > max_items:
                errors.append(SchemaValidationError(
                    error_type="max_items_violation",
                    message=f"Too many items: {len(value)} > {max_items}",
                    path=path,
                    suggestion=f"Reduce to at most {max_items} items"
                ))
            
            min_items = field_schema.get('minItems')
            if min_items and len(value) < min_items:
                errors.append(SchemaValidationError(
                    error_type="min_items_violation",
                    message=f"Too few items: {len(value)} < {min_items}",
                    path=path,
                    suggestion=f"Add at least {min_items} items"
                ))
        
        # Enum validation
        enum_values = field_schema.get('enum')
        if enum_values and value not in enum_values:
            errors.append(SchemaValidationError(
                error_type="enum_violation",
                message=f"Value '{value}' not in allowed values: {enum_values}",
                path=path,
                suggestion=f"Use one of: {', '.join(map(str, enum_values))}"
            ))
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type.
        
        Args:
            value: Value to check
            expected_type: Expected type string
            
        Returns:
            True if type matches
        """
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, assume valid
    
    async def _strict_schema_validation(self, data: Dict[str, Any], 
                                      schema: Dict[str, Any]) -> List[SchemaValidationError]:
        """Perform strict validation checks.
        
        Args:
            data: Data to validate
            schema: Schema definition
            
        Returns:
            List of strict validation errors
        """
        errors = []
        
        # Check for unknown fields in strict mode
        properties = schema.get('properties', {})
        for field_name in data:
            if field_name not in properties:
                errors.append(SchemaValidationError(
                    error_type="unknown_field",
                    message=f"Unknown field '{field_name}' not allowed in strict mode",
                    path=field_name,
                    severity="warning",
                    suggestion=f"Remove field '{field_name}' or add to schema"
                ))
        
        return errors
    
    async def _detect_content_type(self, content: Union[str, bytes, Path]) -> str:
        """Auto-detect content type.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected content type
        """
        if isinstance(content, Path):
            # Use file extension and MIME type
            mime_type, _ = mimetypes.guess_type(str(content))
            if mime_type:
                if mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('text/'):
                    return 'text'
        
        elif isinstance(content, str):
            # Analyze string content
            if content.strip().startswith(('<', '{')):
                return 'structured'
            else:
                return 'text'
        
        elif isinstance(content, bytes):
            # Analyze binary content headers
            if content.startswith(b'\xff\xd8'):  # JPEG
                return 'image'
            elif content.startswith(b'PNG'):  # PNG
                return 'image'
            elif content.startswith(b'ID3') or content.startswith(b'\xff\xfb'):  # MP3
                return 'audio'
        
        return 'mixed'  # Default fallback
    
    async def _extract_basic_metadata(self, content: Union[str, bytes, Path], 
                                    content_type: str) -> Dict[str, Any]:
        """Extract basic metadata from content.
        
        Args:
            content: Content to extract from
            content_type: Type of content
            
        Returns:
            Basic metadata dictionary
        """
        metadata = {}
        
        if isinstance(content, Path):
            # File-based metadata
            stat = content.stat()
            metadata.update({
                'filename': content.name,
                'file_size': stat.st_size,
                'creation_date': datetime.fromtimestamp(stat.st_ctime, timezone.utc),
                'modification_date': datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                'file_extension': content.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(content))[0]
            })
        
        # Content-type specific extraction
        if content_type == 'text':
            if isinstance(content, str):
                metadata.update({
                    'character_count': len(content),
                    'word_count': len(content.split()),
                    'language': 'auto-detect',  # Placeholder for language detection
                    'readability_score': self._calculate_readability(content)
                })
        
        return metadata
    
    async def _extract_format_specific_metadata(self, content: Union[str, bytes, Path],
                                              content_type: str) -> Dict[str, Any]:
        """Extract format-specific metadata.
        
        Args:
            content: Content to extract from
            content_type: Type of content
            
        Returns:
            Format-specific metadata
        """
        metadata = {}
        
        try:
            if content_type == 'video' and isinstance(content, Path):
                # Video metadata extraction (simplified)
                metadata.update({
                    'video_format': content.suffix.lower(),
                    'estimated_duration': 'auto-detect',  # Would use ffprobe in production
                    'estimated_resolution': 'auto-detect',
                    'estimated_bitrate': 'auto-detect'
                })
            
            elif content_type == 'audio' and isinstance(content, Path):
                # Audio metadata extraction (simplified)
                metadata.update({
                    'audio_format': content.suffix.lower(),
                    'estimated_duration': 'auto-detect',  # Would use librosa in production
                    'estimated_bitrate': 'auto-detect',
                    'estimated_sample_rate': 'auto-detect'
                })
            
            elif content_type == 'image' and isinstance(content, Path):
                # Image metadata extraction (simplified)
                metadata.update({
                    'image_format': content.suffix.lower(),
                    'estimated_dimensions': 'auto-detect',  # Would use PIL in production
                    'estimated_color_depth': 'auto-detect',
                    'has_transparency': False
                })
            
        except Exception as e:
            logger.warning(f"Format-specific metadata extraction failed: {e}")
        
        return metadata
    
    async def _ai_enhance_metadata(self, metadata: Dict[str, Any], 
                                 content_type: str) -> Dict[str, Any]:
        """AI-powered metadata enhancement.
        
        Args:
            metadata: Current metadata
            content_type: Type of content
            
        Returns:
            Enhanced metadata
        """
        enhanced = {}
        
        # Simulated AI enhancement - in production, this would use actual AI models
        try:
            # Generate SEO-optimized title suggestions
            if 'title' in metadata:
                enhanced['seo_title_suggestions'] = [
                    f"Enhanced: {metadata['title']}",
                    f"Optimized {metadata['title']} for SEO",
                    f"{metadata['title']} - Premium Content"
                ]
            
            # Generate description suggestions
            if 'description' in metadata:
                enhanced['description_suggestions'] = [
                    f"Comprehensive guide: {metadata.get('title', 'Content')}",
                    f"Expert insights on {metadata.get('title', 'this topic')}",
                    f"Professional {content_type} content featuring {metadata.get('title', 'quality material')}"
                ]
            
            # Generate tag suggestions
            enhanced['ai_suggested_tags'] = [
                f"{content_type}_content",
                "professional_quality",
                "trending_topic",
                "educational_content",
                "entertainment"
            ]
            
            # Content quality assessment
            enhanced['ai_quality_assessment'] = {
                'technical_quality': 0.8,
                'content_relevance': 0.7,
                'engagement_potential': 0.75,
                'seo_optimization': 0.6
            }
            
            # Platform recommendations
            enhanced['platform_recommendations'] = self._recommend_platforms_for_content(
                metadata, content_type
            )
            
        except Exception as e:
            logger.warning(f"AI metadata enhancement failed: {e}")
        
        return enhanced
    
    def _create_metadata_fields(self, metadata: Dict[str, Any]) -> List[MetadataField]:
        """Create metadata field objects from extracted metadata.
        
        Args:
            metadata: Extracted metadata
            
        Returns:
            List of MetadataField objects
        """
        fields = []
        
        # Core fields
        core_mappings = {
            'title': (MetadataFormat.DUBLIN_CORE, True),
            'description': (MetadataFormat.DUBLIN_CORE, True),
            'tags': (MetadataFormat.SCHEMA_ORG, False),
            'category': (MetadataFormat.DUBLIN_CORE, False),
            'language': (MetadataFormat.DUBLIN_CORE, False),
            'creation_date': (MetadataFormat.DUBLIN_CORE, False),
            'creator': (MetadataFormat.DUBLIN_CORE, True)
        }
        
        for field_name, (format_type, is_required) in core_mappings.items():
            if field_name in metadata:
                quality_score = self._calculate_field_quality(field_name, metadata[field_name])
                optimization_suggestions = self._generate_field_optimizations(
                    field_name, metadata[field_name]
                )
                
                fields.append(MetadataField(
                    name=field_name,
                    value=metadata[field_name],
                    format_type=format_type,
                    is_required=is_required,
                    quality_score=quality_score,
                    optimization_suggestions=optimization_suggestions
                ))
        
        # Platform-specific fields
        for platform in ['youtube', 'instagram', 'tiktok', 'spotify']:
            platform_data = metadata.get(f'{platform}_metadata', {})
            for field_name, value in platform_data.items():
                fields.append(MetadataField(
                    name=f"{platform}_{field_name}",
                    value=value,
                    format_type=MetadataFormat.CUSTOM,
                    platform_specific=platform,
                    quality_score=self._calculate_field_quality(field_name, value)
                ))
        
        return fields
    
    async def _assess_metadata_quality(self, fields: List[MetadataField], 
                                     content_type: str) -> Dict[str, Any]:
        """Assess overall metadata quality.
        
        Args:
            fields: List of metadata fields
            content_type: Type of content
            
        Returns:
            Quality assessment result
        """
        # Calculate completeness score
        required_fields = [f for f in fields if f.is_required]
        optional_fields = [f for f in fields if not f.is_required]
        
        if required_fields:
            completeness_score = len(required_fields) / 5  # Assume 5 core required fields
        else:
            completeness_score = 0.0
        
        completeness_score = min(1.0, completeness_score + len(optional_fields) * 0.05)
        
        # Calculate SEO score
        seo_relevant_fields = [f for f in fields if f.name in ['title', 'description', 'tags']]
        if seo_relevant_fields:
            seo_score = sum(f.quality_score for f in seo_relevant_fields) / len(seo_relevant_fields)
        else:
            seo_score = 0.0
        
        # Calculate platform compliance score
        platform_fields = [f for f in fields if f.platform_specific]
        if platform_fields:
            platform_compliance_score = sum(f.quality_score for f in platform_fields) / len(platform_fields)
        else:
            platform_compliance_score = 0.5  # Neutral score if no platform-specific fields
        
        # Determine overall quality level
        overall_score = (completeness_score * 0.4 + seo_score * 0.4 + platform_compliance_score * 0.2)
        
        if overall_score >= 0.9:
            quality_level = MetadataQuality.OPTIMAL
        elif overall_score >= 0.8:
            quality_level = MetadataQuality.EXCELLENT
        elif overall_score >= 0.6:
            quality_level = MetadataQuality.GOOD
        elif overall_score >= 0.4:
            quality_level = MetadataQuality.BASIC
        else:
            quality_level = MetadataQuality.POOR
        
        is_valid = quality_level in [MetadataQuality.GOOD, MetadataQuality.EXCELLENT, MetadataQuality.OPTIMAL]
        
        return {
            'is_valid': is_valid,
            'quality_level': quality_level,
            'completeness_score': completeness_score,
            'seo_score': seo_score,
            'platform_compliance_score': platform_compliance_score
        }
    
    async def _generate_metadata_optimizations(self, fields: List[MetadataField],
                                             quality_result: Dict[str, Any],
                                             content_type: str) -> List[str]:
        """Generate metadata optimization suggestions.
        
        Args:
            fields: Metadata fields
            quality_result: Quality assessment result
            content_type: Type of content
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Completeness suggestions
        if quality_result['completeness_score'] < 0.8:
            suggestions.append("Add missing required metadata fields (title, description, creator)")
            
        required_field_names = {'title', 'description', 'tags', 'category'}
        existing_field_names = {f.name for f in fields}
        missing_fields = required_field_names - existing_field_names
        
        for missing_field in missing_fields:
            suggestions.append(f"Add {missing_field} field for better discoverability")
        
        # SEO suggestions
        if quality_result['seo_score'] < 0.7:
            suggestions.append("Optimize title and description for search engines")
            suggestions.append("Add relevant tags and keywords")
        
        # Field-specific suggestions
        for field in fields:
            if field.quality_score < 0.6:
                suggestions.extend(field.optimization_suggestions)
        
        # Content-type specific suggestions
        if content_type == 'video':
            suggestions.append("Add video thumbnail and chapter markers")
            suggestions.append("Include closed captions for accessibility")
        elif content_type == 'audio':
            suggestions.append("Add album art and episode descriptions")
            suggestions.append("Include transcript for better searchability")
        
        return suggestions[:8]  # Limit to top 8 suggestions
    
    async def _validate_metadata_standards(self, fields: List[MetadataField]) -> List[MetadataValidationIssue]:
        """Validate metadata against format standards.
        
        Args:
            fields: Metadata fields to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        for field in fields:
            # Format-specific validation
            if field.format_type == MetadataFormat.DUBLIN_CORE:
                dublin_core_issues = self._validate_dublin_core_field(field)
                issues.extend(dublin_core_issues)
            
            elif field.format_type == MetadataFormat.SCHEMA_ORG:
                schema_org_issues = self._validate_schema_org_field(field)
                issues.extend(schema_org_issues)
            
            # General quality issues
            if field.quality_score < 0.5:
                issues.append(MetadataValidationIssue(
                    field_name=field.name,
                    issue_type=MetadataValidationType.ACCURACY,
                    severity="warning",
                    description=f"Low quality score for {field.name}: {field.quality_score:.2f}",
                    current_value=str(field.value)[:100],  # Truncate for display
                    impact="medium"
                ))
        
        return issues
    
    def _validate_dublin_core_field(self, field: MetadataField) -> List[MetadataValidationIssue]:
        """Validate Dublin Core metadata field.
        
        Args:
            field: Metadata field to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Dublin Core specific validations
        dc_standards = self.metadata_standards[MetadataFormat.DUBLIN_CORE]
        core_elements = dc_standards['core_elements']
        
        if field.name in core_elements:
            # Validate core element requirements
            if not field.value or (isinstance(field.value, str) and not field.value.strip()):
                issues.append(MetadataValidationIssue(
                    field_name=field.name,
                    issue_type=MetadataValidationType.COMPLETENESS,
                    severity="error",
                    description=f"Dublin Core element '{field.name}' cannot be empty",
                    suggested_value="Provide meaningful content for this field"
                ))
        
        return issues
    
    def _validate_schema_org_field(self, field: MetadataField) -> List[MetadataValidationIssue]:
        """Validate Schema.org metadata field.
        
        Args:
            field: Metadata field to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Schema.org specific validations
        schema_org_standards = self.metadata_standards[MetadataFormat.SCHEMA_ORG]
        
        # Check if field follows Schema.org naming conventions
        if not re.match(r'^[a-z][a-zA-Z]*$', field.name):
            issues.append(MetadataValidationIssue(
                field_name=field.name,
                issue_type=MetadataValidationType.PLATFORM_COMPLIANCE,
                severity="warning",
                description=f"Field name '{field.name}' doesn't follow Schema.org camelCase convention",
                suggested_value=f"Use camelCase format for Schema.org compliance"
            ))
        
        return issues
    
    def _calculate_field_quality(self, field_name: str, value: Any) -> float:
        """Calculate quality score for a metadata field.
        
        Args:
            field_name: Name of the field
            value: Field value
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return 0.0
        
        score = 0.5  # Base score
        
        if isinstance(value, str):
            # Length-based scoring
            if field_name == 'title':
                if 10 <= len(value) <= 100:
                    score = 0.9
                elif 5 <= len(value) <= 150:
                    score = 0.7
                else:
                    score = 0.4
            
            elif field_name == 'description':
                if 50 <= len(value) <= 2000:
                    score = 0.9
                elif 20 <= len(value) <= 3000:
                    score = 0.7
                else:
                    score = 0.4
            
            # Keyword richness (simplified)
            if len(value.split()) > 1:
                score += 0.1
            
            # Special characters penalty
            if re.search(r'[^\w\s\-\.,!?]', value):
                score -= 0.1
        
        elif isinstance(value, list):
            # Array quality based on length and content
            if 3 <= len(value) <= 20:
                score = 0.8
            elif 1 <= len(value) <= 30:
                score = 0.6
            else:
                score = 0.3
        
        return max(0.0, min(1.0, score))
    
    def _generate_field_optimizations(self, field_name: str, value: Any) -> List[str]:
        """Generate optimization suggestions for a field.
        
        Args:
            field_name: Name of the field
            value: Field value
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if isinstance(value, str):
            if field_name == 'title':
                if len(value) < 10:
                    suggestions.append("Make title more descriptive (10+ characters)")
                elif len(value) > 100:
                    suggestions.append("Shorten title for better readability (<100 characters)")
                
                if not re.search(r'[A-Z]', value):
                    suggestions.append("Consider proper capitalization for title")
            
            elif field_name == 'description':
                if len(value) < 50:
                    suggestions.append("Expand description for better SEO (50+ characters)")
                elif len(value) > 2000:
                    suggestions.append("Consider shortening description for readability")
                
                if not re.search(r'\b(how|what|why|when|where)\b', value.lower()):
                    suggestions.append("Consider adding question-based keywords")
        
        elif isinstance(value, list):
            if field_name == 'tags' and len(value) < 3:
                suggestions.append("Add more relevant tags (3-20 recommended)")
        
        return suggestions
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score for text (simplified).
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability score (0.0 to 1.0)
        """
        if not text:
            return 0.0
        
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        if sentences == 0:
            sentences = 1
        
        avg_words_per_sentence = len(words) / sentences
        
        # Simple readability scoring
        if avg_words_per_sentence <= 15:
            return 0.9  # Easy to read
        elif avg_words_per_sentence <= 25:
            return 0.7  # Moderate
        else:
            return 0.4  # Difficult
    
    def _recommend_platforms_for_content(self, metadata: Dict[str, Any], 
                                       content_type: str) -> List[str]:
        """Recommend platforms based on content metadata.
        
        Args:
            metadata: Content metadata
            content_type: Type of content
            
        Returns:
            List of recommended platform names
        """
        recommendations = []
        
        if content_type == 'video':
            recommendations.extend(['youtube', 'tiktok', 'instagram'])
        elif content_type == 'audio':
            recommendations.extend(['spotify', 'youtube', 'podcast_platforms'])
        elif content_type == 'image':
            recommendations.extend(['instagram', 'pinterest', 'twitter'])
        elif content_type == 'text':
            recommendations.extend(['linkedin', 'twitter', 'blog_platforms'])
        
        # Filter based on content length/duration
        if metadata.get('duration', 0) < 60:  # Short content
            if 'tiktok' not in recommendations:
                recommendations.append('tiktok')
        
        return recommendations[:3]  # Limit to top 3

# Convenience functions for direct validation
async def validate_schema(data: Union[Dict[str, Any], str, Path],
                        schema_type: SchemaType = SchemaType.CONTENT_SCHEMA,
                        custom_schema: Optional[Dict[str, Any]] = None,
                        config: Optional[Dict[str, Any]] = None) -> SchemaValidationResult:
    """Validate schema (convenience function).
    
    Args:
        data: Data to validate
        schema_type: Type of schema
        custom_schema: Custom schema definition
        config: Optional validator configuration
        
    Returns:
        SchemaValidationResult
    """
    validator = SchemaMetadataValidator(config)
    return await validator.validate_schema(data, schema_type, custom_schema)

async def extract_metadata(content: Union[str, bytes, Path],
                         content_type: str = "auto",
                         ai_enhancement: bool = None,
                         config: Optional[Dict[str, Any]] = None) -> MetadataValidationResult:
    """Extract metadata (convenience function).
    
    Args:
        content: Content to extract from
        content_type: Type of content
        ai_enhancement: Enable AI enhancement
        config: Optional validator configuration
        
    Returns:
        MetadataValidationResult
    """
    validator = SchemaMetadataValidator(config)
    return await validator.extract_metadata(content, content_type, ai_enhancement)

# Export all classes and functions
__all__ = [
    'SchemaMetadataValidator',
    'ValidationLevel',
    'SchemaType',
    'ValidationStatus',
    'MetadataFormat',
    'MetadataQuality',
    'MetadataValidationType',
    'SchemaValidationError',
    'SchemaValidationResult',
    'MetadataField',
    'MetadataValidationIssue',
    'MetadataValidationResult',
    'CreatorProfile',
    'ContentMetadata',
    'PlatformConfiguration',
    'validate_schema',
    'extract_metadata'
]