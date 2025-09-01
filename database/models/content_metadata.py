"""Content Metadata Database Model

Enterprise-grade SQLAlchemy model for comprehensive content metadata management,
including AI-extracted features, technical specifications, and enriched data.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, BYTEA
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class MetadataType(Enum):
    """
Metadata type enumeration"""

    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    STRUCTURAL = "structural"
    ADMINISTRATIVE = "administrative"
    PRESERVATION = "preservation"
    RIGHTS = "rights"
    AI_EXTRACTED = "ai_extracted"
    USER_GENERATED = "user_generated"
    PLATFORM_SPECIFIC = "platform_specific"
    QUALITY_METRICS = "quality_metrics"
    ANALYTICS = "analytics"
    BEHAVIORAL = "behavioral"
    CONTEXTUAL = "contextual"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"


class MetadataSchema(Enum):
    """Metadata schema standards"""

    DUBLIN_CORE = "dublin_core"
    MPEG7 = "mpeg7"
    EXIF = "exif"
    ID3 = "id3"
    VORBIS_COMMENT = "vorbis_comment"
    XMP = "xmp"
    IPTC = "iptc"
    BWF = "bwf"
    AES = "aes"
    PREMIS = "premis"
    MODS = "mods"
    MARC = "marc"
    SCHEMA_ORG = "schema_org"
    MUSIC_BRAINZ = "music_brainz"
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    CUSTOM = "custom"


class ExtractionMethod(Enum):
    """Metadata extraction methods"""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AI_POWERED = "ai_powered"
    USER_INPUT = "user_input"
    API_IMPORT = "api_import"
    FILE_PARSING = "file_parsing"
    EXTERNAL_SERVICE = "external_service"
    CROWD_SOURCED = "crowd_sourced"
    HYBRID = "hybrid"
    ML_INFERENCE = "ml_inference"
    RULE_BASED = "rule_based"
    PATTERN_MATCHING = "pattern_matching"
    OCR = "ocr"
    SPEECH_TO_TEXT = "speech_to_text"
    COMPUTER_VISION = "computer_vision"


class ConfidenceLevel(Enum):
    """Confidence levels for extracted metadata"""

    VERY_HIGH = "very_high"      # 95%+
    HIGH = "high"                # 85-94%
    MEDIUM = "medium"            # 70-84%
    LOW = "low"                  # 50-69%
    VERY_LOW = "very_low"        # <50%
    UNKNOWN = "unknown"


class ValidationStatus(Enum):
    """Metadata validation status"""

    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    PARTIAL = "partial"
    CONFLICTING = "conflicting"
    OUTDATED = "outdated"
    UNVERIFIED = "unverified"


class ContentMetadata(Base):
    """
    Enterprise Content Metadata Model
    
    Comprehensive metadata management system supporting multiple schemas,
    AI-extracted features, and advanced content analytics for all media types.
    """
    __tablename__ = "content_metadata"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_content_id = Column(UUID(as_uuid=True), ForeignKey('user_content.id'), nullable=False, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    
    # Metadata classification
    metadata_type = Column(SQLEnum(MetadataType), nullable=False, index=True)
    metadata_schema = Column(SQLEnum(MetadataSchema), nullable=False, index=True)
    schema_version = Column(String(20), nullable=True)
    namespace = Column(String(255), nullable=True)
    
    # Metadata identification
    field_name = Column(String(255), nullable=False, index=True)
    field_path = Column(String(500), nullable=True)  # XPath or JSON path
    field_description = Column(Text, nullable=True)
    field_category = Column(String(100), nullable=True)
    
    # Data values
    string_value = Column(Text, nullable=True)
    numeric_value = Column(Float, nullable=True)
    integer_value = Column(Integer, nullable=True)
    boolean_value = Column(Boolean, nullable=True)
    date_value = Column(DateTime(timezone=True), nullable=True)
    json_value = Column(JSON, nullable=True)
    binary_value = Column(BYTEA, nullable=True)
    array_value = Column(ARRAY(String), nullable=True)
    
    # Data type and format
    data_type = Column(String(50), nullable=False)  # string, number, boolean, date, json, binary, array
    data_format = Column(String(100), nullable=True)  # ISO format, MIME type, etc.
    data_unit = Column(String(50), nullable=True)  # seconds, pixels, Hz, dB, etc.
    encoding = Column(String(50), nullable=True)  # UTF-8, Base64, etc.
    
    # Extraction and provenance
    extraction_method = Column(SQLEnum(ExtractionMethod), nullable=False)
    extractor_name = Column(String(255), nullable=True)  # Tool/service name
    extractor_version = Column(String(50), nullable=True)
    extraction_config = Column(JSON, nullable=True)
    extraction_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Quality and confidence
    confidence_level = Column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.UNKNOWN)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    accuracy_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Validation and verification
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.UNVERIFIED)
    validation_rules = Column(JSON, nullable=True)
    validation_errors = Column(JSON, nullable=True)
    validation_warnings = Column(JSON, nullable=True)
    validated_by = Column(String(255), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Source and context
    source_system = Column(String(255), nullable=True)
    source_file = Column(String(500), nullable=True)
    source_location = Column(String(500), nullable=True)  # URL, file path, etc.
    source_metadata = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)
    
    # Language and localization
    language = Column(String(10), nullable=True)  # ISO language code
    country = Column(String(10), nullable=True)   # ISO country code
    locale = Column(String(20), nullable=True)    # Full locale
    character_set = Column(String(50), nullable=True)
    
    # Rights and permissions
    access_level = Column(String(50), default="public")
    edit_permissions = Column(JSON, nullable=True)
    view_permissions = Column(JSON, nullable=True)
    copyright_notice = Column(Text, nullable=True)
    license_info = Column(JSON, nullable=True)
    
    # Versioning and history
    version = Column(String(20), default="1.0")
    parent_metadata_id = Column(UUID(as_uuid=True), ForeignKey('content_metadata.id'), nullable=True)
    is_current_version = Column(Boolean, default=True)
    change_reason = Column(String(255), nullable=True)
    change_description = Column(Text, nullable=True)
    
    # Synchronization and distribution
    sync_status = Column(String(50), default="pending")
    sync_targets = Column(ARRAY(String), nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_errors = Column(JSON, nullable=True)
    distribution_status = Column(JSON, nullable=True)
    
    # AI and machine learning context
    ai_model_name = Column(String(255), nullable=True)
    ai_model_version = Column(String(50), nullable=True)
    ai_processing_time = Column(Float, nullable=True)
    ai_confidence_metrics = Column(JSON, nullable=True)
    feature_vector = Column(BYTEA, nullable=True)  # Encoded feature vector
    
    # Content-specific metadata (flexible structure)
    # Audio metadata
    audio_features = Column(JSON, nullable=True)
    spectral_features = Column(JSON, nullable=True)
    rhythm_features = Column(JSON, nullable=True)
    harmonic_features = Column(JSON, nullable=True)
    
    # Video metadata
    video_features = Column(JSON, nullable=True)
    visual_features = Column(JSON, nullable=True)
    motion_features = Column(JSON, nullable=True)
    scene_analysis = Column(JSON, nullable=True)
    
    # Image metadata
    image_features = Column(JSON, nullable=True)
    color_analysis = Column(JSON, nullable=True)
    composition_analysis = Column(JSON, nullable=True)
    object_detection = Column(JSON, nullable=True)
    
    # Text metadata
    text_features = Column(JSON, nullable=True)
    linguistic_features = Column(JSON, nullable=True)
    sentiment_analysis = Column(JSON, nullable=True)
    topic_modeling = Column(JSON, nullable=True)
    named_entities = Column(JSON, nullable=True)
    
    # Platform-specific metadata
    platform_metadata = Column(JSON, nullable=True)
    platform_constraints = Column(JSON, nullable=True)
    platform_optimizations = Column(JSON, nullable=True)
    platform_mappings = Column(JSON, nullable=True)
    
    # Performance and usage
    access_count = Column(Integer, default=0)
    modification_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    last_modified_at = Column(DateTime(timezone=True), nullable=True)
    usage_statistics = Column(JSON, nullable=True)
    
    # Preservation and archival
    preservation_level = Column(String(50), nullable=True)
    archival_status = Column(String(50), nullable=True)
    retention_period = Column(Integer, nullable=True)  # Days
    disposal_date = Column(DateTime(timezone=True), nullable=True)
    preservation_actions = Column(JSON, nullable=True)
    
    # Cross-references and relationships
    related_metadata_ids = Column(ARRAY(UUID), nullable=True)
    dependency_metadata_ids = Column(ARRAY(UUID), nullable=True)
    conflict_metadata_ids = Column(ARRAY(UUID), nullable=True)
    external_references = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_until = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    is_searchable = Column(Boolean, default=True)
    is_machine_readable = Column(Boolean, default=True)
    is_human_readable = Column(Boolean, default=True)
    is_editable = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Relationships
    user_content = relationship("UserContent", back_populates="metadata_records")
    content_fingerprint = relationship("ContentFingerprint", back_populates="metadata_records")
    parent_metadata = relationship("ContentMetadata", remote_side=[id], foreign_keys=[parent_metadata_id])
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_metadata_content_type', 'user_content_id', 'metadata_type'),
        Index('idx_metadata_schema_field', 'metadata_schema', 'field_name'),
        Index('idx_metadata_extraction_method', 'extraction_method', 'extraction_timestamp'),
        Index('idx_metadata_confidence_quality', 'confidence_level', 'quality_score'),
        Index('idx_metadata_validation_status', 'validation_status', 'validated_at'),
        Index('idx_metadata_language_locale', 'language', 'locale'),
        Index('idx_metadata_version_current', 'version', 'is_current_version'),
        Index('idx_metadata_sync_status', 'sync_status', 'last_sync_at'),
        Index('idx_metadata_ai_model', 'ai_model_name', 'ai_model_version'),
        Index('idx_metadata_access_level', 'access_level', 'is_published'),
        Index('idx_metadata_preservation', 'preservation_level', 'archival_status'),
        Index('idx_metadata_effective_period', 'effective_from', 'effective_until'),
        Index('idx_metadata_numeric_values', 'field_name', 'numeric_value'),
        Index('idx_metadata_string_values', 'field_name', 'string_value'),
        Index('idx_metadata_fingerprint', 'content_fingerprint_id', 'metadata_type'),
    )
    
    def __repr__(self):
        return f"<ContentMetadata(id={self.id}, field_name='{self.field_name}', type={self.metadata_type.value}, schema={self.metadata_schema.value})>"
    
    def to_dict(self, include_binary: bool = False, include_ai_features: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        base_dict = {
            "id": str(self.id),
            "user_content_id": str(self.user_content_id),
            "content_fingerprint_id": str(self.content_fingerprint_id) if self.content_fingerprint_id else None,
            "metadata_type": self.metadata_type.value if self.metadata_type else None,
            "metadata_schema": self.metadata_schema.value if self.metadata_schema else None,
            "schema_version": self.schema_version,
            "namespace": self.namespace,
            "field_name": self.field_name,
            "field_path": self.field_path,
            "field_description": self.field_description,
            "field_category": self.field_category,
            "string_value": self.string_value,
            "numeric_value": self.numeric_value,
            "integer_value": self.integer_value,
            "boolean_value": self.boolean_value,
            "date_value": self.date_value.isoformat() if self.date_value else None,
            "json_value": self.json_value,
            "array_value": self.array_value,
            "data_type": self.data_type,
            "data_format": self.data_format,
            "data_unit": self.data_unit,
            "encoding": self.encoding,
            "extraction_method": self.extraction_method.value if self.extraction_method else None,
            "extractor_name": self.extractor_name,
            "extractor_version": self.extractor_version,
            "extraction_timestamp": self.extraction_timestamp.isoformat() if self.extraction_timestamp else None,
            "confidence_level": self.confidence_level.value if self.confidence_level else None,
            "confidence_score": self.confidence_score,
            "quality_score": self.quality_score,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status.value if self.validation_status else None,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "source_system": self.source_system,
            "source_file": self.source_file,
            "source_location": self.source_location,
            "source_metadata": self.source_metadata,
            "context_data": self.context_data,
            "language": self.language,
            "country": self.country,
            "locale": self.locale,
            "character_set": self.character_set,
            "access_level": self.access_level,
            "edit_permissions": self.edit_permissions,
            "view_permissions": self.view_permissions,
            "version": self.version,
            "parent_metadata_id": str(self.parent_metadata_id) if self.parent_metadata_id else None,
            "is_current_version": self.is_current_version,
            "change_reason": self.change_reason,
            "change_description": self.change_description,
            "sync_status": self.sync_status,
            "sync_targets": self.sync_targets,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "sync_errors": self.sync_errors,
            "platform_metadata": self.platform_metadata,
            "platform_constraints": self.platform_constraints,
            "access_count": self.access_count,
            "modification_count": self.modification_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "last_modified_at": self.last_modified_at.isoformat() if self.last_modified_at else None,
            "preservation_level": self.preservation_level,
            "archival_status": self.archival_status,
            "retention_period": self.retention_period,
            "disposal_date": self.disposal_date.isoformat() if self.disposal_date else None,
            "related_metadata_ids": [str(id) for id in self.related_metadata_ids] if self.related_metadata_ids else [],
            "external_references": self.external_references,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "is_active": self.is_active,
            "is_published": self.is_published,
            "is_searchable": self.is_searchable,
            "is_machine_readable": self.is_machine_readable,
            "is_human_readable": self.is_human_readable,
            "is_editable": self.is_editable,
            "requires_approval": self.requires_approval
        }
        
        if include_binary and self.binary_value:
            # Convert binary data to base64 for JSON serialization
            import base64
            base_dict["binary_value"] = base64.b64encode(self.binary_value).decode('utf-8')
        
        if include_ai_features:
            base_dict.update({
                "ai_model_name": self.ai_model_name,
                "ai_model_version": self.ai_model_version,
                "ai_processing_time": self.ai_processing_time,
                "ai_confidence_metrics": self.ai_confidence_metrics,
                "audio_features": self.audio_features,
                "spectral_features": self.spectral_features,
                "video_features": self.video_features,
                "visual_features": self.visual_features,
                "image_features": self.image_features,
                "color_analysis": self.color_analysis,
                "text_features": self.text_features,
                "linguistic_features": self.linguistic_features,
                "sentiment_analysis": self.sentiment_analysis,
                "topic_modeling": self.topic_modeling,
                "named_entities": self.named_entities
            })
        
        return base_dict
    
    def get_typed_value(self) -> Any:
        """Get the value in its proper type"""
        if self.data_type == "string":
            return self.string_value
        elif self.data_type == "number":
            return self.numeric_value
        elif self.data_type == "integer":
            return self.integer_value
        elif self.data_type == "boolean":
            return self.boolean_value
        elif self.data_type == "date":
            return self.date_value
        elif self.data_type == "json":
            return self.json_value
        elif self.data_type == "binary":
            return self.binary_value
        elif self.data_type == "array":
            return self.array_value
        return None
    
    def is_valid(self) -> bool:
        """Check if metadata is valid"""
        return (
            self.validation_status == ValidationStatus.VALID and
            self.confidence_level not in [ConfidenceLevel.VERY_LOW, ConfidenceLevel.UNKNOWN] and
            self.is_active and
            (not self.effective_until or datetime.now(timezone.utc) <= self.effective_until)
        )
    
    def needs_validation(self) -> bool:
        """
Check if metadata needs validation"""
        return (
            self.validation_status in [ValidationStatus.PENDING, ValidationStatus.UNVERIFIED] or
            self.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW] or
            (self.validated_at and 
             (datetime.now(timezone.utc) - self.validated_at).days > 30)
        )
    
    def is_ai_generated(self) -> bool:
        """
Check if metadata was generated by AI"""
        return self.extraction_method in [
            ExtractionMethod.AI_POWERED,
            ExtractionMethod.ML_INFERENCE,
            ExtractionMethod.COMPUTER_VISION,
            ExtractionMethod.SPEECH_TO_TEXT,
            ExtractionMethod.OCR
        ]
    
    @classmethod
    def create_metadata(cls, metadata_data: Dict[str, Any], user_content_id: str) -> 'ContentMetadata':
        """
Create ContentMetadata from metadata extraction data"""
        return cls(
            user_content_id=user_content_id,
            content_fingerprint_id=metadata_data.get('content_fingerprint_id'),
            metadata_type=MetadataType(metadata_data.get('metadata_type', 'technical')),
            metadata_schema=MetadataSchema(metadata_data.get('metadata_schema', 'custom')),
            field_name=metadata_data.get('field_name'),
            field_description=metadata_data.get('field_description'),
            string_value=metadata_data.get('string_value'),
            numeric_value=metadata_data.get('numeric_value'),
            integer_value=metadata_data.get('integer_value'),
            boolean_value=metadata_data.get('boolean_value'),
            date_value=metadata_data.get('date_value'),
            json_value=metadata_data.get('json_value'),
            array_value=metadata_data.get('array_value'),
            data_type=metadata_data.get('data_type', 'string'),
            data_format=metadata_data.get('data_format'),
            data_unit=metadata_data.get('data_unit'),
            extraction_method=ExtractionMethod(metadata_data.get('extraction_method', 'automatic')),
            extractor_name=metadata_data.get('extractor_name'),
            extractor_version=metadata_data.get('extractor_version'),
            extraction_timestamp=metadata_data.get('extraction_timestamp', datetime.now(timezone.utc)),
            confidence_level=ConfidenceLevel(metadata_data.get('confidence_level', 'unknown')),
            confidence_score=metadata_data.get('confidence_score'),
            quality_score=metadata_data.get('quality_score'),
            source_system=metadata_data.get('source_system'),
            source_metadata=metadata_data.get('source_metadata', {}),
            language=metadata_data.get('language'),
            locale=metadata_data.get('locale'),
            ai_model_name=metadata_data.get('ai_model_name'),
            ai_model_version=metadata_data.get('ai_model_version'),
            ai_processing_time=metadata_data.get('ai_processing_time')
        )
