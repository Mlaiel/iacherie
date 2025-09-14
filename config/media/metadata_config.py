"""
Metadata Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Metadata Configuration Module
import asyncio

=======================================

Enterprise-grade metadata configuration for the Ainflue platform.
Comprehensive metadata management, extraction, validation, and enrichment
for video, audio, image, and document content with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib

class MetadataType(str, Enum):
    """Metadata types"""
    TECHNICAL = "technical"       # Technical metadata (codec, bitrate, etc.)
    DESCRIPTIVE = "descriptive"   # Descriptive metadata (title, description, etc.)
    ADMINISTRATIVE = "administrative"  # Administrative metadata (rights, provenance)
    STRUCTURAL = "structural"     # Structural metadata (chapters, scenes)
    PRESERVATION = "preservation" # Preservation metadata (checksums, formats)
    RIGHTS = "rights"            # Rights and licensing metadata
    GEOSPATIAL = "geospatial"    # Location and geographic metadata
    TEMPORAL = "temporal"        # Time-based metadata
    BEHAVIORAL = "behavioral"    # User behavior and analytics metadata
    SEMANTIC = "semantic"        # AI-generated semantic metadata

class MediaType(str, Enum):
    """Media types for metadata"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"
    SUBTITLE = "subtitle"
    THUMBNAIL = "thumbnail"
    ANIMATION = "animation"

class MetadataFormat(str, Enum):
    """Metadata formats"""
    EXIF = "exif"                # Exchangeable Image File Format
    IPTC = "iptc"                # International Press Telecommunications Council
    XMP = "xmp"                  # Extensible Metadata Platform
    DUBLIN_CORE = "dublin_core"  # Dublin Core Metadata Element Set
    ID3 = "id3"                  # ID3 metadata for audio
    VORBIS_COMMENT = "vorbis_comment"  # Vorbis comment for audio
    QUICKTIME = "quicktime"      # QuickTime metadata
    BWF = "bwf"                  # Broadcast Wave Format
    JSON_LD = "json_ld"          # JSON-LD metadata
    SCHEMA_ORG = "schema_org"    # Schema.org structured data
    CUSTOM = "custom"            # Custom metadata format

class ValidationLevel(str, Enum):
    """Metadata validation levels"""
    BASIC = "basic"              # Basic format validation
    STANDARD = "standard"        # Standard compliance validation
    STRICT = "strict"            # Strict validation with all rules
    CUSTOM = "custom"            # Custom validation rules
    AI_ENHANCED = "ai_enhanced"  # AI-enhanced validation

class ExtractionMethod(str, Enum):
    """Metadata extraction methods"""
    AUTOMATIC = "automatic"      # Automatic extraction from file
    MANUAL = "manual"           # Manual entry
    AI_GENERATED = "ai_generated"  # AI-generated metadata
    API_RETRIEVED = "api_retrieved"  # Retrieved from external APIs
    INHERITED = "inherited"      # Inherited from source/template
    COMPUTED = "computed"        # Computed from other metadata

@dataclass
class MetadataField:
    """Metadata field definition"""
    field_id: str
    name: str
    description: str
    data_type: str               # string, integer, float, boolean, date, array, object
    
    # Field properties
    required: bool = False
    repeatable: bool = False
    searchable: bool = True
    editable: bool = True
    
    # Validation
    validation_rules: List[str] = field(default_factory=list)
    allowed_values: List[str] = field(default_factory=list)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regex_pattern: Optional[str] = None
    
    # Format and display
    display_format: str = ""
    input_type: str = "text"     # text, textarea, select, date, number, etc.
    placeholder: str = ""
    help_text: str = ""
    
    # Categorization
    category: MetadataType = MetadataType.DESCRIPTIVE
    metadata_format: MetadataFormat = MetadataFormat.CUSTOM
    
    # Extraction
    extraction_method: ExtractionMethod = ExtractionMethod.MANUAL
    source_path: str = ""        # XPath or JSONPath for extraction
    ai_extraction_enabled: bool = False
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    priority: int = 5            # 1-10, higher = more important
    
    def validate_value(self, value: Any) -> Tuple[bool, str]:
        """Validate field value"""
        
        # Check required
        if self.required and (value is None or value == ""):
            return False, f"Field '{self.name}' is required"
        
        if value is None:
            return True, ""
        
        # Type validation
        if self.data_type == "string":
            if not isinstance(value, str):
                return False, f"Field '{self.name}' must be a string"
            
            # Length validation
            if self.min_length is not None and len(value) < self.min_length:
                return False, f"Field '{self.name}' must be at least {self.min_length} characters"
            
            if self.max_length is not None and len(value) > self.max_length:
                return False, f"Field '{self.name}' must be at most {self.max_length} characters"
            
            # Regex validation
            if self.regex_pattern:
                import re
                if not re.match(self.regex_pattern, value):
                    return False, f"Field '{self.name}' format is invalid"
        
        elif self.data_type == "integer":
            try:
                int_value = int(value)
                if self.min_value is not None and int_value < self.min_value:
                    return False, f"Field '{self.name}' must be at least {self.min_value}"
                if self.max_value is not None and int_value > self.max_value:
                    return False, f"Field '{self.name}' must be at most {self.max_value}"
            except (ValueError, TypeError):
                return False, f"Field '{self.name}' must be an integer"
        
        elif self.data_type == "float":
            try:
                float_value = float(value)
                if self.min_value is not None and float_value < self.min_value:
                    return False, f"Field '{self.name}' must be at least {self.min_value}"
                if self.max_value is not None and float_value > self.max_value:
                    return False, f"Field '{self.name}' must be at most {self.max_value}"
            except (ValueError, TypeError):
                return False, f"Field '{self.name}' must be a number"
        
        elif self.data_type == "boolean":
            if not isinstance(value, bool):
                return False, f"Field '{self.name}' must be true or false"
        
        elif self.data_type == "date":
            if isinstance(value, str):
                try:
                    datetime.fromisoformat(value)
                except ValueError:
                    return False, f"Field '{self.name}' must be a valid date"
        
        # Allowed values validation
        if self.allowed_values and str(value) not in self.allowed_values:
            return False, f"Field '{self.name}' must be one of: {', '.join(self.allowed_values)}"
        
        return True, ""
    
    def extract_from_source(self, source_data: Dict[str, Any]) -> Any:
        """Extract value from source data"""
        
        if not self.source_path:
            return None
        
        try:
            # Simple dot notation extraction
            keys = self.source_path.split('.')
            value = source_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
        except:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "required": self.required,
            "repeatable": self.repeatable,
            "searchable": self.searchable,
            "editable": self.editable,
            "validation_rules": self.validation_rules,
            "allowed_values": self.allowed_values,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "regex_pattern": self.regex_pattern,
            "display_format": self.display_format,
            "input_type": self.input_type,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "category": self.category.value,
            "metadata_format": self.metadata_format.value,
            "extraction_method": self.extraction_method.value,
            "source_path": self.source_path,
            "ai_extraction_enabled": self.ai_extraction_enabled,
            "created_date": self.created_date.isoformat(),
            "enabled": self.enabled,
            "priority": self.priority
        }

@dataclass
class MetadataSchema:
    """Metadata schema definition"""
    schema_id: str
    name: str
    description: str
    media_type: MediaType
    
    # Schema fields
    fields: List[MetadataField] = field(default_factory=list)
    
    # Schema properties
    version: str = "1.0"
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    auto_extraction: bool = True
    ai_enrichment: bool = False
    
    # Inheritance
    parent_schema_id: Optional[str] = None
    inherit_fields: bool = True
    
    # Export formats
    supported_formats: List[MetadataFormat] = field(default_factory=list)
    default_export_format: MetadataFormat = MetadataFormat.JSON_LD
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    enabled: bool = True
    
    def get_field_by_id(self, field_id: str) -> Optional[MetadataField]:
        """Get field by ID"""
        for field in self.fields:
            if field.field_id == field_id:
                return field
        return None
    
    def get_fields_by_category(self, category: MetadataType) -> List[MetadataField]:
        """Get fields by category"""
        return [field for field in self.fields if field.category == category and field.enabled]
    
    def get_required_fields(self) -> List[MetadataField]:
        """Get required fields"""
        return [field for field in self.fields if field.required and field.enabled]
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate metadata against schema"""
        
        errors = []
        
        for field in self.fields:
            if not field.enabled:
                continue
            
            value = metadata.get(field.field_id)
            
            # Handle repeatable fields
            if field.repeatable and isinstance(value, list):
                for i, item_value in enumerate(value):
                    is_valid, error_msg = field.validate_value(item_value)
                    if not is_valid:
                        errors.append(f"{error_msg} (item {i})")
            else:
                is_valid, error_msg = field.validate_value(value)
                if not is_valid:
                    errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def extract_metadata(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from source data"""
        
        extracted_metadata = {}
        
        for field in self.fields:
            if not field.enabled or field.extraction_method == ExtractionMethod.MANUAL:
                continue
            
            # Extract value
            extracted_value = field.extract_from_source(source_data)
            
            if extracted_value is not None:
                extracted_metadata[field.field_id] = extracted_value
        
        return extracted_metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "schema_id": self.schema_id,
            "name": self.name,
            "description": self.description,
            "media_type": self.media_type.value,
            "fields": [field.to_dict() for field in self.fields],
            "version": self.version,
            "validation_level": self.validation_level.value,
            "auto_extraction": self.auto_extraction,
            "ai_enrichment": self.ai_enrichment,
            "parent_schema_id": self.parent_schema_id,
            "inherit_fields": self.inherit_fields,
            "supported_formats": [f.value for f in self.supported_formats],
            "default_export_format": self.default_export_format.value,
            "total_fields": len(self.fields),
            "required_fields": len(self.get_required_fields()),
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "created_by": self.created_by,
            "enabled": self.enabled
        }

@dataclass
class MetadataRecord:
    """Metadata record for a media file"""
    record_id: str
    file_path: str
    media_type: MediaType
    schema_id: str
    
    # Metadata content
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Technical metadata
    file_size_bytes: int = 0
    file_hash: str = ""
    mime_type: str = ""
    
    # Processing information
    extraction_method: ExtractionMethod = ExtractionMethod.AUTOMATIC
    last_extracted: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    validation_errors: List[str] = field(default_factory=list)
    
    # AI enrichment
    ai_enriched: bool = False
    ai_confidence_scores: Dict[str, float] = field(default_factory=dict)
    ai_generated_tags: List[str] = field(default_factory=list)
    
    # Versioning
    version: int = 1
    change_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    updated_by: str = ""
    
    def get_metadata_value(self, field_id: str, default: Any = None) -> Any:
        """Get metadata value by field ID"""
        return self.metadata.get(field_id, default)
    
    def set_metadata_value(self, field_id: str, value: Any, user_id: str = "") -> None:
        """Set metadata value"""
        old_value = self.metadata.get(field_id)
        self.metadata[field_id] = value
        
        # Record change
        change_record = {
            "field_id": field_id,
            "old_value": old_value,
            "new_value": value,
            "changed_by": user_id,
            "changed_date": datetime.now().isoformat(),
            "version": self.version
        }
        
        self.change_history.append(change_record)
        self.updated_date = datetime.now()
        self.updated_by = user_id
        self.version += 1
    
    def calculate_completeness(self, schema: MetadataSchema) -> float:
        """Calculate metadata completeness percentage"""
        
        total_fields = len([f for f in schema.fields if f.enabled])
        if total_fields == 0:
            return 100.0
        
        filled_fields = 0
        for field in schema.fields:
            if not field.enabled:
                continue
            
            value = self.metadata.get(field.field_id)
            if value is not None and value != "":
                filled_fields += 1
        
        return (filled_fields / total_fields) * 100.0
    
    def calculate_quality_score(self, schema: MetadataSchema) -> float:
        """Calculate metadata quality score"""
        
        score = 0.0
        total_weight = 0.0
        
        for field in schema.fields:
            if not field.enabled:
                continue
            
            field_weight = field.priority / 10.0  # Normalize priority to 0-1
            total_weight += field_weight
            
            value = self.metadata.get(field.field_id)
            
            # Check if field has value
            if value is not None and value != "":
                field_score = 1.0
                
                # Additional scoring based on field type and content
                if field.data_type == "string" and isinstance(value, str):
                    # Score based on content length and quality
                    if len(value) >= 10:  # Reasonable content length
                        field_score = 1.0
                    elif len(value) >= 5:
                        field_score = 0.8
                    else:
                        field_score = 0.5
                
                # AI confidence bonus
                if field.field_id in self.ai_confidence_scores:
                    confidence = self.ai_confidence_scores[field.field_id]
                    field_score *= confidence
                
                score += field_score * field_weight
            # Penalty for missing required fields
            elif field.required:
                score -= field_weight * 0.5
        
        if total_weight > 0:
            return min(max(score / total_weight, 0.0), 1.0) * 100
        else:
            return 0.0
    
    def export_metadata(self, format: MetadataFormat, schema: MetadataSchema) -> Dict[str, Any]:
        """Export metadata in specified format"""
        
        if format == MetadataFormat.JSON_LD:
            return self._export_json_ld(schema)
        elif format == MetadataFormat.DUBLIN_CORE:
            return self._export_dublin_core(schema)
        elif format == MetadataFormat.SCHEMA_ORG:
            return self._export_schema_org(schema)
        else:
            # Default: return raw metadata
            return self.metadata.copy()
    
    def _export_json_ld(self, schema: MetadataSchema) -> Dict[str, Any]:
        """Export as JSON-LD"""
        
        json_ld = {
            "@context": "https://schema.org/",
            "@type": "MediaObject",
            "@id": self.record_id,
            "name": self.metadata.get("title", ""),
            "description": self.metadata.get("description", ""),
            "contentUrl": self.file_path,
            "encodingFormat": self.mime_type,
            "contentSize": self.file_size_bytes,
            "dateCreated": self.created_date.isoformat(),
            "dateModified": self.updated_date.isoformat()
        }
        
        # Add additional metadata
        for field_id, value in self.metadata.items():
            if field_id not in ["title", "description"]:
                json_ld[field_id] = value
        
        return json_ld
    
    def _export_dublin_core(self, schema: MetadataSchema) -> Dict[str, Any]:
        """Export as Dublin Core"""
        
        dublin_core = {
            "dc:title": self.metadata.get("title", ""),
            "dc:description": self.metadata.get("description", ""),
            "dc:creator": self.metadata.get("creator", ""),
            "dc:subject": self.metadata.get("tags", []),
            "dc:date": self.created_date.isoformat(),
            "dc:type": self.media_type.value,
            "dc:format": self.mime_type,
            "dc:identifier": self.record_id
        }
        
        return {k: v for k, v in dublin_core.items() if v}
    
    def _export_schema_org(self, schema: MetadataSchema) -> Dict[str, Any]:
        """Export as Schema.org structured data"""
        
        schema_org = {
            "@context": "https://schema.org/",
            "@type": self._get_schema_org_type(),
            "name": self.metadata.get("title", ""),
            "description": self.metadata.get("description", ""),
            "contentUrl": self.file_path,
            "encodingFormat": self.mime_type,
            "contentSize": f"{self.file_size_bytes} bytes",
            "uploadDate": self.created_date.isoformat()
        }
        
        return schema_org
    
    def _get_schema_org_type(self) -> str:
        """Get Schema.org type based on media type"""
        
        type_mapping = {
            MediaType.VIDEO: "VideoObject",
            MediaType.AUDIO: "AudioObject",
            MediaType.IMAGE: "ImageObject",
            MediaType.DOCUMENT: "DigitalDocument",
            MediaType.LIVE_STREAM: "BroadcastEvent"
        }
        
        return type_mapping.get(self.media_type, "MediaObject")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "file_path": self.file_path,
            "media_type": self.media_type.value,
            "schema_id": self.schema_id,
            "metadata": self.metadata,
            "file_size_bytes": self.file_size_bytes,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "extraction_method": self.extraction_method.value,
            "last_extracted": self.last_extracted.isoformat() if self.last_extracted else None,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "validation_errors": self.validation_errors,
            "ai_enriched": self.ai_enriched,
            "ai_confidence_scores": self.ai_confidence_scores,
            "ai_generated_tags": self.ai_generated_tags,
            "version": self.version,
            "change_history": self.change_history,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }

class MetadataConfiguration:
    """Main metadata configuration manager"""
    
    def __init__(self) -> None:
        """Initialize metadata configuration"""
        # Data storage
        self.schemas: Dict[str, MetadataSchema] = {}
        self.records: Dict[str, MetadataRecord] = {}
        
        # Global settings
        self.metadata_enabled = True
        self.auto_extraction = True
        self.ai_enrichment = True
        self.validation_enabled = True
        
        # Extraction settings
        self.extraction_settings = {
            "auto_extract_on_upload": True,
            "extract_technical_metadata": True,
            "extract_descriptive_metadata": True,
            "use_ai_for_extraction": True,
            "ai_confidence_threshold": 0.7,
            "parallel_extraction": True,
            "cache_extractions": True,
            "extraction_timeout_seconds": 300
        }
        
        # Validation settings
        self.validation_settings = {
            "validate_on_save": True,
            "validate_on_export": True,
            "strict_validation": False,
            "custom_validation_rules": True,
            "ai_assisted_validation": True,
            "validation_reports": True,
            "auto_fix_errors": False
        }
        
        # Export settings
        self.export_settings = {
            "default_format": "json_ld",
            "include_technical_metadata": True,
            "include_ai_metadata": True,
            "include_change_history": False,
            "compress_exports": True,
            "embed_in_files": True,
            "external_sidecar_files": False
        }
        
        # AI settings
        self.ai_settings = {
            "content_analysis": True,
            "object_detection": True,
            "scene_recognition": True,
            "text_extraction": True,
            "speech_to_text": True,
            "sentiment_analysis": True,
            "topic_modeling": True,
            "auto_tagging": True,
            "content_classification": True,
            "quality_assessment": True
        }
        
        # Performance settings
        self.performance_settings = {
            "max_concurrent_extractions": 10,
            "cache_size_mb": 1024,
            "background_processing": True,
            "batch_size": 50,
            "indexing_enabled": True,
            "search_optimization": True,
            "metadata_compression": True
        }
        
        # Initialize default schemas
        self._initialize_default_schemas()
    
    def _initialize_default_schemas(self) -> None:
        """Initialize default metadata schemas"""
        
        # Video metadata schema
        video_schema = MetadataSchema(
            schema_id="video_standard",
            name="Standard Video Metadata",
            description="Standard metadata schema for video content",
            media_type=MediaType.VIDEO,
            supported_formats=[MetadataFormat.JSON_LD, MetadataFormat.XMP, MetadataFormat.QUICKTIME],
            fields=[
                # Descriptive metadata
                MetadataField(
                    field_id="title",
                    name="Title",
                    description="Video title",
                    data_type="string",
                    required=True,
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    max_length=200,
                    priority=10
                ),
                MetadataField(
                    field_id="description",
                    name="Description",
                    description="Video description",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    input_type="textarea",
                    max_length=2000,
                    priority=8
                ),
                MetadataField(
                    field_id="tags",
                    name="Tags",
                    description="Video tags",
                    data_type="array",
                    repeatable=True,
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    ai_extraction_enabled=True,
                    priority=7
                ),
                MetadataField(
                    field_id="creator",
                    name="Creator",
                    description="Content creator",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    priority=9
                ),
                MetadataField(
                    field_id="duration",
                    name="Duration",
                    description="Video duration in seconds",
                    data_type="float",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="technical.duration",
                    priority=8
                ),
                
                # Technical metadata
                MetadataField(
                    field_id="resolution",
                    name="Resolution",
                    description="Video resolution",
                    data_type="string",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="technical.resolution",
                    priority=7
                ),
                MetadataField(
                    field_id="bitrate",
                    name="Bitrate",
                    description="Video bitrate in kbps",
                    data_type="integer",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="technical.bitrate",
                    priority=6
                ),
                MetadataField(
                    field_id="codec",
                    name="Codec",
                    description="Video codec",
                    data_type="string",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="technical.codec",
                    priority=6
                ),
                MetadataField(
                    field_id="framerate",
                    name="Frame Rate",
                    description="Video frame rate",
                    data_type="float",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="technical.framerate",
                    priority=5
                ),
                
                # Rights metadata
                MetadataField(
                    field_id="license",
                    name="License",
                    description="Content license",
                    data_type="string",
                    category=MetadataType.RIGHTS,
                    allowed_values=["CC0", "CC BY", "CC BY-SA", "CC BY-NC", "All Rights Reserved"],
                    priority=7
                ),
                MetadataField(
                    field_id="copyright",
                    name="Copyright",
                    description="Copyright information",
                    data_type="string",
                    category=MetadataType.RIGHTS,
                    priority=6
                ),
                
                # Geospatial metadata
                MetadataField(
                    field_id="location",
                    name="Location",
                    description="Recording location",
                    data_type="string",
                    category=MetadataType.GEOSPATIAL,
                    searchable=True,
                    ai_extraction_enabled=True,
                    priority=5
                ),
                MetadataField(
                    field_id="latitude",
                    name="Latitude",
                    description="GPS latitude",
                    data_type="float",
                    category=MetadataType.GEOSPATIAL,
                    min_value=-90.0,
                    max_value=90.0,
                    priority=4
                ),
                MetadataField(
                    field_id="longitude",
                    name="Longitude",
                    description="GPS longitude",
                    data_type="float",
                    category=MetadataType.GEOSPATIAL,
                    min_value=-180.0,
                    max_value=180.0,
                    priority=4
                )
            ]
        )
        
        self.schemas[video_schema.schema_id] = video_schema
        
        # Audio metadata schema
        audio_schema = MetadataSchema(
            schema_id="audio_standard",
            name="Standard Audio Metadata",
            description="Standard metadata schema for audio content",
            media_type=MediaType.AUDIO,
            supported_formats=[MetadataFormat.ID3, MetadataFormat.VORBIS_COMMENT, MetadataFormat.JSON_LD],
            fields=[
                # Basic audio metadata
                MetadataField(
                    field_id="title",
                    name="Title",
                    description="Audio title",
                    data_type="string",
                    required=True,
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    priority=10
                ),
                MetadataField(
                    field_id="artist",
                    name="Artist",
                    description="Audio artist",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    priority=9
                ),
                MetadataField(
                    field_id="album",
                    name="Album",
                    description="Album name",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    priority=8
                ),
                MetadataField(
                    field_id="genre",
                    name="Genre",
                    description="Music genre",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    ai_extraction_enabled=True,
                    priority=7
                ),
                MetadataField(
                    field_id="duration",
                    name="Duration",
                    description="Audio duration in seconds",
                    data_type="float",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    priority=8
                ),
                MetadataField(
                    field_id="bitrate",
                    name="Bitrate",
                    description="Audio bitrate in kbps",
                    data_type="integer",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    priority=6
                ),
                MetadataField(
                    field_id="sample_rate",
                    name="Sample Rate",
                    description="Audio sample rate in Hz",
                    data_type="integer",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    priority=5
                )
            ]
        )
        
        self.schemas[audio_schema.schema_id] = audio_schema
        
        # Image metadata schema
        image_schema = MetadataSchema(
            schema_id="image_standard",
            name="Standard Image Metadata",
            description="Standard metadata schema for image content",
            media_type=MediaType.IMAGE,
            supported_formats=[MetadataFormat.EXIF, MetadataFormat.IPTC, MetadataFormat.XMP],
            fields=[
                # Basic image metadata
                MetadataField(
                    field_id="title",
                    name="Title",
                    description="Image title",
                    data_type="string",
                    required=True,
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    priority=10
                ),
                MetadataField(
                    field_id="caption",
                    name="Caption",
                    description="Image caption",
                    data_type="string",
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    ai_extraction_enabled=True,
                    priority=8
                ),
                MetadataField(
                    field_id="keywords",
                    name="Keywords",
                    description="Image keywords",
                    data_type="array",
                    repeatable=True,
                    searchable=True,
                    category=MetadataType.DESCRIPTIVE,
                    ai_extraction_enabled=True,
                    priority=7
                ),
                MetadataField(
                    field_id="width",
                    name="Width",
                    description="Image width in pixels",
                    data_type="integer",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    priority=7
                ),
                MetadataField(
                    field_id="height",
                    name="Height",
                    description="Image height in pixels",
                    data_type="integer",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    priority=7
                ),
                MetadataField(
                    field_id="camera_make",
                    name="Camera Make",
                    description="Camera manufacturer",
                    data_type="string",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="exif.make",
                    priority=5
                ),
                MetadataField(
                    field_id="camera_model",
                    name="Camera Model",
                    description="Camera model",
                    data_type="string",
                    category=MetadataType.TECHNICAL,
                    extraction_method=ExtractionMethod.AUTOMATIC,
                    source_path="exif.model",
                    priority=5
                )
            ]
        )
        
        self.schemas[image_schema.schema_id] = image_schema
    
    def create_metadata_record(self, record_data: Dict[str, Any]) -> MetadataRecord:
        """Create metadata record"""
        
        record = MetadataRecord(
            record_id=record_data.get("record_id", f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            file_path=record_data["file_path"],
            media_type=MediaType(record_data["media_type"]),
            schema_id=record_data["schema_id"],
            metadata=record_data.get("metadata", {}),
            file_size_bytes=record_data.get("file_size_bytes", 0),
            file_hash=record_data.get("file_hash", ""),
            mime_type=record_data.get("mime_type", ""),
            extraction_method=ExtractionMethod(record_data.get("extraction_method", "automatic")),
            created_by=record_data.get("created_by", ""),
            updated_by=record_data.get("updated_by", "")
        )
        
        self.records[record.record_id] = record
        return record
    
    async def extract_metadata(self, file_path: str, media_type: MediaType, 
                              schema_id: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        
        result = {
            "success": False,
            "metadata": {},
            "technical_metadata": {},
            "ai_metadata": {},
            "error": None
        }
        
        try:
            if schema_id not in self.schemas:
                result["error"] = f"Schema {schema_id} not found"
                return result
            
            schema = self.schemas[schema_id]
            
            # Extract technical metadata
            technical_metadata = await self._extract_technical_metadata(file_path, media_type)
            result["technical_metadata"] = technical_metadata
            
            # Extract metadata using schema
            extracted_metadata = schema.extract_metadata(technical_metadata)
            
            # AI-enhanced extraction if enabled
            if self.ai_settings["content_analysis"]:
                ai_metadata = await self._extract_ai_metadata(file_path, media_type, schema)
                result["ai_metadata"] = ai_metadata
                extracted_metadata.update(ai_metadata)
            
            result["metadata"] = extracted_metadata
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def validate_metadata(self, record_id: str) -> Dict[str, Any]:
        """Validate metadata record"""
        
        result = {
            "success": False,
            "valid": False,
            "errors": [],
            "warnings": [],
            "completeness": 0.0,
            "quality_score": 0.0
        }
        
        try:
            if record_id not in self.records:
                result["errors"].append(f"Record {record_id} not found")
                return result
            
            record = self.records[record_id]
            
            if record.schema_id not in self.schemas:
                result["errors"].append(f"Schema {record.schema_id} not found")
                return result
            
            schema = self.schemas[record.schema_id]
            
            # Validate metadata
            is_valid, validation_errors = schema.validate_metadata(record.metadata)
            
            # Calculate metrics
            completeness = record.calculate_completeness(schema)
            quality_score = record.calculate_quality_score(schema)
            
            # Update record
            record.last_validated = datetime.now()
            record.validation_errors = validation_errors
            
            result.update({
                "success": True,
                "valid": is_valid,
                "errors": validation_errors,
                "completeness": completeness,
                "quality_score": quality_score
            })
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def search_records(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search metadata records"""
        
        matching_records = []
        
        for record in self.records.values():
            if self._matches_record_criteria(record, search_criteria):
                matching_records.append(record.to_dict())
        
        # Sort by updated date (descending)
        matching_records.sort(key=lambda x: x["updated_date"], reverse=True)
        
        return matching_records
    
    def get_metadata_statistics(self) -> Dict[str, Any]:
        """Get metadata statistics"""
        
        stats = {
            "total_records": len(self.records),
            "total_schemas": len(self.schemas),
            "records_by_media_type": {},
            "records_by_schema": {},
            "average_completeness": 0.0,
            "average_quality_score": 0.0,
            "ai_enriched_count": 0,
            "validation_error_count": 0
        }
        
        # Calculate statistics
        total_completeness = 0.0
        total_quality = 0.0
        ai_enriched_count = 0
        validation_error_count = 0
        
        for record in self.records.values():
            # Count by media type
            media_type = record.media_type.value
            stats["records_by_media_type"][media_type] = stats["records_by_media_type"].get(media_type, 0) + 1
            
            # Count by schema
            schema_id = record.schema_id
            stats["records_by_schema"][schema_id] = stats["records_by_schema"].get(schema_id, 0) + 1
            
            # Calculate averages
            if record.schema_id in self.schemas:
                schema = self.schemas[record.schema_id]
                total_completeness += record.calculate_completeness(schema)
                total_quality += record.calculate_quality_score(schema)
            
            # Count AI enriched
            if record.ai_enriched:
                ai_enriched_count += 1
            
            # Count validation errors
            if record.validation_errors:
                validation_error_count += 1
        
        # Calculate averages
        if self.records:
            stats["average_completeness"] = total_completeness / len(self.records)
            stats["average_quality_score"] = total_quality / len(self.records)
        
        stats["ai_enriched_count"] = ai_enriched_count
        stats["validation_error_count"] = validation_error_count
        
        return stats
    
    # Helper methods
    async def _extract_technical_metadata(self, file_path: str, media_type: MediaType) -> Dict[str, Any]:
        """Extract technical metadata from file"""
        
        # Simulate technical metadata extraction
        technical_metadata = {
            "file_size": 1024000,
            "mime_type": "video/mp4",
            "technical": {
                "duration": 120.5,
                "resolution": "1920x1080",
                "bitrate": 2500,
                "codec": "h264",
                "framerate": 30.0
            }
        }
        
        return technical_metadata
    
    async def _extract_ai_metadata(self, file_path: str, media_type: MediaType, 
                                  schema: MetadataSchema) -> Dict[str, Any]:
        """Extract AI-enhanced metadata"""
        
        # Simulate AI metadata extraction
        ai_metadata = {
            "tags": ["nature", "landscape", "mountain"],
            "description": "A beautiful mountain landscape at sunset",
            "objects_detected": ["mountain", "sky", "clouds"],
            "sentiment": "positive",
            "quality_score": 0.85
        }
        
        return ai_metadata
    
    def _matches_record_criteria(self, record: MetadataRecord, criteria: Dict[str, Any]) -> bool:
        """Check if record matches search criteria"""
        
        # Check media type
        if "media_type" in criteria and criteria["media_type"] != record.media_type.value:
            return False
        
        # Check schema
        if "schema_id" in criteria and criteria["schema_id"] != record.schema_id:
            return False
        
        # Check metadata search
        if "search_term" in criteria:
            search_term = criteria["search_term"].lower()
            
            # Search in metadata values
            for value in record.metadata.values():
                if isinstance(value, str) and search_term in value.lower():
                    return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and search_term in item.lower():
                            return True
            
            return False
        
        # Check date range
        if "start_date" in criteria:
            start_date = datetime.fromisoformat(criteria["start_date"])
            if record.created_date < start_date:
                return False
        
        if "end_date" in criteria:
            end_date = datetime.fromisoformat(criteria["end_date"])
            if record.created_date > end_date:
                return False
        
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete metadata configuration"""
        return {
            "metadata_statistics": self.get_metadata_statistics(),
            "schemas_count": len(self.schemas),
            "records_count": len(self.records),
            "global_settings": {
                "metadata_enabled": self.metadata_enabled,
                "auto_extraction": self.auto_extraction,
                "ai_enrichment": self.ai_enrichment,
                "validation_enabled": self.validation_enabled
            },
            "extraction_settings": self.extraction_settings,
            "validation_settings": self.validation_settings,
            "export_settings": self.export_settings,
            "ai_settings": self.ai_settings,
            "performance_settings": self.performance_settings
        }

# Global metadata configuration instance
metadata_config = MetadataConfiguration()

# Export main classes
__all__ = [
    "MetadataConfiguration",
    "MetadataType",
    "MediaType",
    "MetadataFormat",
    "ValidationLevel",
    "ExtractionMethod",
    "MetadataField",
    "MetadataSchema",
    "MetadataRecord",
    "metadata_config"
]
