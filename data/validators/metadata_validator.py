"""Metadata Validator - Industrial metadata validation and enrichment for IA Influencer Agent Platform
===================================================================================================

Advanced metadata validation system with AI-powered extraction, validation, enrichment,
and standardization capabilities for creator content workflows. Supports multi-format
metadata standards and automated optimization for platform distribution.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Features:
- Multi-format metadata extraction (ID3, EXIF, XMP, IPTC, etc.)
- AI-powered metadata enhancement and auto-completion
- Platform-specific metadata optimization
- Metadata standardization and normalization
- Creator workflow integration
- Copyright and licensing metadata management
- Multilingual metadata support
- Real-time metadata validation and enrichment
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import re
from datetime import datetime, timedelta, timezone
import hashlib
import tempfile
import io
import base64

# Advanced metadata processing dependencies
try:
    # Audio metadata
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    
    # Image metadata
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    import exifread
    
    # Video metadata
    import ffmpeg
    
    # Text processing
    import spacy
    from langdetect import detect, LangDetectError
    
    METADATA_FEATURES = True
except ImportError as e:
    logger.warning(f"Advanced metadata features unavailable: {e}")
    METADATA_FEATURES = False

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata for comprehensive management."""

    TECHNICAL = "technical"          # Technical specifications
    DESCRIPTIVE = "descriptive"      # Title, description, keywords
    ADMINISTRATIVE = "administrative" # Creation date, file info
    STRUCTURAL = "structural"        # File structure, relationships
    PRESERVATION = "preservation"    # Long-term preservation info
    RIGHTS = "rights"               # Copyright, licensing
    PROVENANCE = "provenance"       # Creation history, workflow
    SEMANTIC = "semantic"           # AI-generated tags, categories
    CREATOR = "creator"             # Creator-specific metadata
    PLATFORM = "platform"          # Platform-specific requirements
    MONETIZATION = "monetization"   # Revenue and monetization data
    COLLABORATION = "collaboration" # Collaboration information


class MetadataStandard(Enum):
    """Metadata standards and formats."""

    DUBLIN_CORE = "dublin_core"
    EXIF = "exif"
    IPTC = "iptc"
    XMP = "xmp"
    ID3V1 = "id3v1"
    ID3V2 = "id3v2"
    VORBIS_COMMENT = "vorbis_comment"
    MP4_METADATA = "mp4_metadata"
    FLAC_METADATA = "flac_metadata"
    FFMPEG_METADATA = "ffmpeg_metadata"
    CUSTOM = "custom"
    PLATFORM_SPECIFIC = "platform_specific"


class ValidationSeverity(Enum):
    """Metadata validation issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetadataField(Enum):
    """Standard metadata fields for creator content."""
    # Basic identification
    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"
    DESCRIPTION = "description"
    
    # Content classification
    GENRE = "genre"
    CATEGORY = "category"
    TAGS = "tags"
    KEYWORDS = "keywords"
    LANGUAGE = "language"
    
    # Technical information
    DURATION = "duration"
    BITRATE = "bitrate"
    SAMPLE_RATE = "sample_rate"
    RESOLUTION = "resolution"
    CODEC = "codec"
    FILE_FORMAT = "file_format"
    
    # Rights and licensing
    COPYRIGHT = "copyright"
    LICENSE = "license"
    RIGHTS_HOLDER = "rights_holder"
    USAGE_RIGHTS = "usage_rights"
    
    # Creator information
    CREATOR_NAME = "creator_name"
    CREATOR_EMAIL = "creator_email"
    LABEL = "label"
    PUBLISHER = "publisher"
    
    # Publication information
    RELEASE_DATE = "release_date"
    CREATION_DATE = "creation_date"
    MODIFICATION_DATE = "modification_date"
    PUBLISH_DATE = "publish_date"
    
    # Commercial information
    ISRC = "isrc"
    UPC = "upc"
    CATALOG_NUMBER = "catalog_number"
    PRICE = "price"
    
    # Collaboration information
    FEATURED_ARTISTS = "featured_artists"
    COLLABORATORS = "collaborators"
    PRODUCERS = "producers"
    SONGWRITERS = "songwriters"
    
    # Platform-specific
    YOUTUBE_TITLE = "youtube_title"
    YOUTUBE_DESCRIPTION = "youtube_description"
    INSTAGRAM_CAPTION = "instagram_caption"
    SPOTIFY_DESCRIPTION = "spotify_description"
    
    # AI-generated
    AUTO_TAGS = "auto_tags"
    SENTIMENT_SCORE = "sentiment_score"
    QUALITY_SCORE = "quality_score"
    CONTENT_FINGERPRINT = "content_fingerprint"


class PlatformRequirement(Enum):
    """Platform-specific metadata requirements."""

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    FORBIDDEN = "forbidden"


@dataclass
class MetadataValidationIssue:
    """Metadata validation issue."""
    field: str
    issue_type: str
    severity: ValidationSeverity
    message: str
    current_value: Optional[Any] = None
    suggested_value: Optional[Any] = None
    platform_specific: Optional[str] = None
    auto_fixable: bool = False
    standard: Optional[MetadataStandard] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return {
            "field": self.field,
            "issue_type": self.issue_type,
            "severity": self.severity.value,
            "message": self.message,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "platform_specific": self.platform_specific,
            "auto_fixable": self.auto_fixable,
            "standard": self.standard.value if self.standard else None
        }


@dataclass
class ExtractedMetadata:
    """Extracted metadata from content."""
    file_path: Optional[str] = None
    file_size: int = 0
    mime_type: str = ""
    
    # Technical metadata
    technical: Dict[str, Any] = field(default_factory=dict)
    
    # Standard metadata fields
    descriptive: Dict[str, Any] = field(default_factory=dict)
    administrative: Dict[str, Any] = field(default_factory=dict)
    rights: Dict[str, Any] = field(default_factory=dict)
    
    # Format-specific metadata
    id3_metadata: Dict[str, Any] = field(default_factory=dict)
    exif_metadata: Dict[str, Any] = field(default_factory=dict)
    xmp_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # AI-enhanced metadata
    ai_generated: Dict[str, Any] = field(default_factory=dict)
    
    # Platform-optimized metadata
    platform_optimized: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Extraction metadata
    extraction_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    extraction_method: str = "automated"
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    def get_field_value(self, field: MetadataField) -> Optional[Any]:
        """Get value for a specific metadata field."""
        field_name = field.value
        
        # Check descriptive metadata first
        if field_name in self.descriptive:
            return self.descriptive[field_name]
        
        # Check technical metadata
        if field_name in self.technical:
            return self.technical[field_name]
        
        # Check administrative metadata
        if field_name in self.administrative:
            return self.administrative[field_name]
        
        # Check rights metadata
        if field_name in self.rights:
            return self.rights[field_name]
        
        # Check AI-generated metadata
        if field_name in self.ai_generated:
            return self.ai_generated[field_name]
        
        return None
    
    def set_field_value(self, field: MetadataField, value: Any, category: str = "descriptive") -> None:
        """Set value for a specific metadata field."""
        field_name = field.value
        
        if category == "technical":
            self.technical[field_name] = value
        elif category == "administrative":
            self.administrative[field_name] = value
        elif category == "rights":
            self.rights[field_name] = value
        elif category == "ai_generated":
            self.ai_generated[field_name] = value
        else:
            self.descriptive[field_name] = value


@dataclass
class MetadataValidationResult:
    """Metadata validation result."""
    is_valid: bool
    extracted_metadata: ExtractedMetadata
    
    # Validation details
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_duration: float = 0.0
    validator_version: str = "2.0.0"
    
    # Issues and recommendations
    issues: List[MetadataValidationIssue] = field(default_factory=list)
    warnings: List[MetadataValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Enhancement results
    enhanced_metadata: Optional[ExtractedMetadata] = None
    enhancement_applied: bool = False
    
    # Platform compatibility
    platform_compatibility: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Quality metrics
    completeness_score: float = 0.0
    quality_score: float = 0.0
    standardization_score: float = 0.0
    
    # Statistics
    total_fields_extracted: int = 0
    total_fields_enhanced: int = 0
    total_fields_validated: int = 0
    
    def get_critical_issues(self) -> List[MetadataValidationIssue]:
        """Get critical validation issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]
    
    def get_auto_fixable_issues(self) -> List[MetadataValidationIssue]:
        """
Get issues that can be automatically fixed."""
        return [issue for issue in self.issues if issue.auto_fixable]
    
    def calculate_completeness_score(self) -> float:
        """
Calculate metadata completeness score."""
        essential_fields = [
            MetadataField.TITLE, MetadataField.ARTIST, MetadataField.DESCRIPTION,
            MetadataField.CREATION_DATE, MetadataField.COPYRIGHT
        ]
        
        completed_fields = 0
        for field in essential_fields:
            if self.extracted_metadata.get_field_value(field):
                completed_fields += 1
        
        self.completeness_score = (completed_fields / len(essential_fields)) * 100
        return self.completeness_score
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "validation_timestamp": self.validation_timestamp.isoformat(),
            "validation_duration": self.validation_duration,
            "validator_version": self.validator_version,
            "completeness_score": self.completeness_score,
            "quality_score": self.quality_score,
            "standardization_score": self.standardization_score,
            "total_fields_extracted": self.total_fields_extracted,
            "total_fields_enhanced": self.total_fields_enhanced,
            "enhancement_applied": self.enhancement_applied,
            "issues_count": len(self.issues),
            "warnings_count": len(self.warnings),
            "critical_issues_count": len(self.get_critical_issues()),
            "auto_fixable_issues_count": len(self.get_auto_fixable_issues()),
            "platform_compatibility": self.platform_compatibility
        }


class MetadataValidator:
    """
    Industrial-grade metadata validator for the IA Influencer Agent Platform.
    
    Provides comprehensive metadata validation, extraction, enhancement,
    and standardization for creator content workflows.
    
    Features:
    - Multi-format metadata extraction and validation
    - AI-powered metadata enhancement and auto-completion
    - Platform-specific metadata optimization
    - Metadata standardization and normalization
    - Creator workflow integration
    - Real-time metadata processing
    """

    
    VERSION = "2.0.0"
    
    # Platform-specific metadata requirements
    PLATFORM_REQUIREMENTS = {
        "spotify": {
            MetadataField.TITLE: PlatformRequirement.REQUIRED,
            MetadataField.ARTIST: PlatformRequirement.REQUIRED,
            MetadataField.ALBUM: PlatformRequirement.REQUIRED,
            MetadataField.GENRE: PlatformRequirement.RECOMMENDED,
            MetadataField.RELEASE_DATE: PlatformRequirement.RECOMMENDED,
            MetadataField.ISRC: PlatformRequirement.RECOMMENDED,
        },
        "youtube": {
            MetadataField.TITLE: PlatformRequirement.REQUIRED,
            MetadataField.DESCRIPTION: PlatformRequirement.REQUIRED,
            MetadataField.TAGS: PlatformRequirement.RECOMMENDED,
            MetadataField.CATEGORY: PlatformRequirement.RECOMMENDED,
            MetadataField.LANGUAGE: PlatformRequirement.RECOMMENDED,
        },
        "instagram": {
            MetadataField.TITLE: PlatformRequirement.OPTIONAL,
            MetadataField.DESCRIPTION: PlatformRequirement.RECOMMENDED,
            MetadataField.TAGS: PlatformRequirement.RECOMMENDED,
            MetadataField.COPYRIGHT: PlatformRequirement.RECOMMENDED,
        },
        "tiktok": {
            MetadataField.TITLE: PlatformRequirement.OPTIONAL,
            MetadataField.DESCRIPTION: PlatformRequirement.RECOMMENDED,
            MetadataField.TAGS: PlatformRequirement.REQUIRED,
            MetadataField.LANGUAGE: PlatformRequirement.RECOMMENDED,
        }
    }
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enable_ai_enhancement: bool = True,
        enable_auto_fix: bool = True
    ):
        """
        Initialize metadata validator.
        
        Args:
            config: Validator configuration
            enable_ai_enhancement: Enable AI-powered metadata enhancement
            enable_auto_fix: Enable automatic metadata fixes
        """
        self.config = config or {}
        self.enable_ai_enhancement = enable_ai_enhancement and METADATA_FEATURES
        self.enable_auto_fix = enable_auto_fix
        
        # Validation rules
        self._validation_rules: Dict[MetadataField, List[Callable]] = {}
        self._enhancement_rules: Dict[MetadataField, Callable] = {}
        
        # AI models for enhancement
        self._ai_models = {}
        self._ai_initialized = False
        
        # Statistics
        self._stats = {
            "total_validations": 0,
            "successful_extractions": 0,
            "enhancements_applied": 0,
            "auto_fixes_applied": 0,
            "avg_processing_time": 0.0
        }
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
        # Initialize AI models if enabled
        if self.enable_ai_enhancement:
            asyncio.create_task(self._initialize_ai_models())
        
        logger.info(f"MetadataValidator {self.VERSION} initialized")
        logger.info(f"AI Enhancement: {'Enabled' if self.enable_ai_enhancement else 'Disabled'}")
        logger.info(f"Auto Fix: {'Enabled' if self.enable_auto_fix else 'Disabled'}")
    
    async def _initialize_ai_models(self) -> None:
        """Initialize AI models for metadata enhancement."""
        try:
            if not METADATA_FEATURES:
                logger.warning("Advanced features not available, skipping AI model initialization")
                return
            
            logger.info("Initializing AI models for metadata enhancement...")
            
            # Initialize NLP model for text processing
            try:
                self._ai_models["nlp"] = spacy.load("en_core_web_sm")
                logger.debug("NLP model loaded for metadata enhancement")
            except Exception as e:
                logger.warning(f"Failed to load NLP model: {e}")
            
            self._ai_initialized = True
            logger.info("AI models for metadata enhancement initialized")
            
        except Exception as e:
            logger.error(f"AI models initialization failed: {e}")
            self._ai_initialized = False
    
    def _initialize_validation_rules(self) -> None:
        """Initialize metadata validation rules."""
        # Title validation rules
        self._validation_rules[MetadataField.TITLE] = [
            self._validate_title_length,
            self._validate_title_content,
            self._validate_title_encoding
        ]
        
        # Artist validation rules
        self._validation_rules[MetadataField.ARTIST] = [
            self._validate_artist_format,
            self._validate_artist_length,
            self._validate_artist_characters
        ]
        
        # Duration validation rules
        self._validation_rules[MetadataField.DURATION] = [
            self._validate_duration_format,
            self._validate_duration_range
        ]
        
        # Date validation rules
        self._validation_rules[MetadataField.CREATION_DATE] = [
            self._validate_date_format,
            self._validate_date_validity
        ]
        
        # Copyright validation rules
        self._validation_rules[MetadataField.COPYRIGHT] = [
            self._validate_copyright_format,
            self._validate_copyright_completeness
        ]
        
        # Initialize enhancement rules
        self._enhancement_rules[MetadataField.TAGS] = self._enhance_tags
        self._enhancement_rules[MetadataField.DESCRIPTION] = self._enhance_description
        self._enhancement_rules[MetadataField.GENRE] = self._enhance_genre
        self._enhancement_rules[MetadataField.LANGUAGE] = self._enhance_language
    
    async def validate_metadata_comprehensive(
        self,
        content_data: Union[str, bytes, Path],
        content_type: str = "auto",
        target_platforms: Optional[List[str]] = None,
        enhancement_level: str = "standard"
    ) -> MetadataValidationResult:
        """
        Comprehensive metadata validation with extraction and enhancement.
        
        Args:
            content_data: Content to validate metadata for
            content_type: Type of content (audio, video, image, auto)
            target_platforms: Target platforms for optimization
            enhancement_level: Level of AI enhancement (basic, standard, advanced)
        
        Returns:
            Comprehensive metadata validation result
        """
        start_time = time.time()
        self._stats["total_validations"] += 1
        
        try:
            logger.info(f"Starting comprehensive metadata validation for {content_type} content")
            
            # Extract metadata from content
            extracted_metadata = await self._extract_metadata_comprehensive(
                content_data, content_type
            )
            
            # Validate extracted metadata
            validation_result = MetadataValidationResult(
                is_valid=True,
                extracted_metadata=extracted_metadata
            )
            
            # Run validation rules
            await self._run_validation_rules(validation_result)
            
            # Validate platform compatibility
            if target_platforms:
                await self._validate_platform_compatibility(
                    validation_result, target_platforms
                )
            
            # Apply AI enhancement if enabled
            if self.enable_ai_enhancement and enhancement_level != "basic":
                await self._apply_metadata_enhancement(
                    validation_result, enhancement_level
                )
            
            # Apply automatic fixes if enabled
            if self.enable_auto_fix:
                await self._apply_automatic_fixes(validation_result)
            
            # Calculate quality scores
            self._calculate_quality_scores(validation_result)
            
            # Update statistics
            validation_result.validation_duration = time.time() - start_time
            self._update_statistics(validation_result)
            
            logger.info(f"Metadata validation completed in {validation_result.validation_duration:.2f}s")
            logger.info(f"Completeness score: {validation_result.completeness_score:.1f}%")
            logger.info(f"Quality score: {validation_result.quality_score:.1f}%")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Metadata validation failed: {e}")
            return MetadataValidationResult(
                is_valid=False,
                extracted_metadata=ExtractedMetadata(),
                validation_duration=time.time() - start_time
            )
    
    async def _extract_metadata_comprehensive(
        self,
        content_data: Union[str, bytes, Path],
        content_type: str
    ) -> ExtractedMetadata:
        """Extract comprehensive metadata from content."""
        try:
            metadata = ExtractedMetadata()
            
            # Determine content type if auto
            if content_type == "auto":
                content_type = await self._detect_content_type(content_data)
            
            # Extract based on content type
            if content_type == "audio":
                await self._extract_audio_metadata(content_data, metadata)
            elif content_type == "video":
                await self._extract_video_metadata(content_data, metadata)
            elif content_type == "image":
                await self._extract_image_metadata(content_data, metadata)
            elif content_type == "text":
                await self._extract_text_metadata(content_data, metadata)
            
            # Extract universal metadata
            await self._extract_universal_metadata(content_data, metadata)
            
            self._stats["successful_extractions"] += 1
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return ExtractedMetadata()
    
    async def _detect_content_type(self, content_data: Union[str, bytes, Path]) -> str:
        """Detect content type from data."""
        try:
            # Simple MIME type detection based on file extension or magic bytes
            if isinstance(content_data, (str, Path)):
                file_path = Path(content_data)
                suffix = file_path.suffix.lower()
                
                if suffix in ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']:
                    return "audio"
                elif suffix in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                    return "video"
                elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                    return "image"
                elif suffix in ['.txt', '.md', '.doc', '.docx', '.pdf']:
                    return "text"
            
            elif isinstance(content_data, bytes):
                # Check magic bytes
                if content_data.startswith(b'\xff\xfb') or content_data.startswith(b'ID3'):
                    return "audio"
                elif content_data.startswith(b'\x89PNG') or content_data.startswith(b'\xff\xd8\xff'):
                    return "image"
                elif content_data.startswith(b'ftyp'):
                    return "video"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Content type detection failed: {e}")
            return "unknown"
    
    async def _extract_audio_metadata(self, content_data: Union[str, bytes, Path], metadata: ExtractedMetadata) -> None:
        """Extract metadata from audio files."""
        try:
            if not METADATA_FEATURES:
                logger.warning("Audio metadata extraction requires additional dependencies")
                return
            
            # Handle different input types
            file_path = None
            if isinstance(content_data, Path):
                file_path = str(content_data)
            elif isinstance(content_data, str) and Path(content_data).exists():
                file_path = content_data
            elif isinstance(content_data, bytes):
                # Create temporary file for bytes data
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                    tmp_file.write(content_data)
                    file_path = tmp_file.name
            
            if not file_path:
                return
            
            # Extract with Mutagen
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                logger.warning(f"Could not read audio metadata from {file_path}")
                return
            
            # Extract basic metadata
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata.technical.update({
                    "duration": getattr(info, 'length', 0),
                    "bitrate": getattr(info, 'bitrate', 0),
                    "sample_rate": getattr(info, 'sample_rate', 0),
                    "channels": getattr(info, 'channels', 0),
                    "codec": getattr(info, 'codec', "unknown")
                })
            
            # Extract ID3 tags (MP3)
            if isinstance(audio_file, MP3):
                await self._extract_id3_metadata(audio_file, metadata)
            
            # Extract FLAC metadata
            elif isinstance(audio_file, FLAC):
                await self._extract_flac_metadata(audio_file, metadata)
            
            # Extract MP4 metadata
            elif isinstance(audio_file, MP4):
                await self._extract_mp4_metadata(audio_file, metadata)
            
            # Clean up temporary file if created
            if isinstance(content_data, bytes) and file_path:
                try:
                    Path(file_path).unlink()
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {e}")
    
    async def _extract_id3_metadata(self, audio_file: MP3, metadata: ExtractedMetadata) -> None:
        """Extract ID3 metadata from MP3 files."""
        try:
            tags = audio_file.tags
            if not tags:
                return
            
            # Map ID3 tags to our metadata structure
            id3_mapping = {
                "TIT2": MetadataField.TITLE,
                "TPE1": MetadataField.ARTIST,
                "TALB": MetadataField.ALBUM,
                "TCON": MetadataField.GENRE,
                "TDRC": MetadataField.RELEASE_DATE,
                "TCOP": MetadataField.COPYRIGHT,
                "TPE2": MetadataField.FEATURED_ARTISTS,
                "TLAN": MetadataField.LANGUAGE,
            }
            
            for tag_id, metadata_field in id3_mapping.items():
                if tag_id in tags:
                    value = str(tags[tag_id].text[0]) if tags[tag_id].text else ""
                    metadata.set_field_value(metadata_field, value, "descriptive")
                    metadata.id3_metadata[tag_id] = value
            
            # Extract additional ID3 tags
            if "COMM::eng" in tags:  # Comments
                comment = str(tags["COMM::eng"].text[0])
                metadata.set_field_value(MetadataField.DESCRIPTION, comment, "descriptive")
            
            if "TSRC" in tags:  # ISRC
                isrc = str(tags["TSRC"].text[0])
                metadata.set_field_value(MetadataField.ISRC, isrc, "administrative")
            
        except Exception as e:
            logger.error(f"ID3 metadata extraction failed: {e}")
    
    async def _extract_flac_metadata(self, audio_file: FLAC, metadata: ExtractedMetadata) -> None:
        """Extract metadata from FLAC files."""
        try:
            tags = audio_file.tags
            if not tags:
                return
            
            # Map FLAC Vorbis comments to our metadata structure
            flac_mapping = {
                "TITLE": MetadataField.TITLE,
                "ARTIST": MetadataField.ARTIST,
                "ALBUM": MetadataField.ALBUM,
                "GENRE": MetadataField.GENRE,
                "DATE": MetadataField.RELEASE_DATE,
                "COPYRIGHT": MetadataField.COPYRIGHT,
                "ALBUMARTIST": MetadataField.FEATURED_ARTISTS,
                "LANGUAGE": MetadataField.LANGUAGE,
                "DESCRIPTION": MetadataField.DESCRIPTION,
            }
            
            for tag_name, metadata_field in flac_mapping.items():
                if tag_name in tags:
                    value = tags[tag_name][0] if tags[tag_name] else ""
                    metadata.set_field_value(metadata_field, value, "descriptive")
            
        except Exception as e:
            logger.error(f"FLAC metadata extraction failed: {e}")
    
    async def _extract_mp4_metadata(self, audio_file: MP4, metadata: ExtractedMetadata) -> None:
        """Extract metadata from MP4/M4A files."""
        try:
            tags = audio_file.tags
            if not tags:
                return
            
            # Map MP4 tags to our metadata structure
            mp4_mapping = {
                "\xa9nam": MetadataField.TITLE,
                "\xa9ART": MetadataField.ARTIST,
                "\xa9alb": MetadataField.ALBUM,
                "\xa9gen": MetadataField.GENRE,
                "\xa9day": MetadataField.RELEASE_DATE,
                "cprt": MetadataField.COPYRIGHT,
                "aART": MetadataField.FEATURED_ARTISTS,
            }
            
            for tag_name, metadata_field in mp4_mapping.items():
                if tag_name in tags:
                    value = str(tags[tag_name][0]) if tags[tag_name] else ""
                    metadata.set_field_value(metadata_field, value, "descriptive")
            
        except Exception as e:
            logger.error(f"MP4 metadata extraction failed: {e}")
    
    async def _extract_image_metadata(self, content_data: Union[str, bytes, Path], metadata: ExtractedMetadata) -> None:
        """Extract metadata from image files."""
        try:
            if not METADATA_FEATURES:
                logger.warning("Image metadata extraction requires additional dependencies")
                return
            
            # Handle different input types
            image = None
            if isinstance(content_data, (str, Path)):
                image = Image.open(content_data)
            elif isinstance(content_data, bytes):
                image = Image.open(io.BytesIO(content_data))
            
            if not image:
                return
            
            # Extract basic image information
            metadata.technical.update({
                "width": image.width,
                "height": image.height,
                "resolution": f"{image.width}x{image.height}",
                "format": image.format,
                "mode": image.mode,
                "file_size": len(content_data) if isinstance(content_data, bytes) else 0
            })
            
            # Extract EXIF data
            exif_data = image.getexif()
            if exif_data:
                await self._extract_exif_metadata(exif_data, metadata)
            
            # Extract additional metadata
            info = image.info
            if info:
                metadata.descriptive.update({
                    "dpi": info.get("dpi", (0, 0)),
                    "compression": info.get("compression"),
                    "photometric": info.get("photometric")
                })
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
    
    async def _extract_exif_metadata(self, exif_data: dict, metadata: ExtractedMetadata) -> None:
        """Extract EXIF metadata from image files."""
        try:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                # Map important EXIF tags
                if tag_name == "DateTime":
                    metadata.set_field_value(MetadataField.CREATION_DATE, str(value), "administrative")
                elif tag_name == "Artist":
                    metadata.set_field_value(MetadataField.ARTIST, str(value), "descriptive")
                elif tag_name == "Copyright":
                    metadata.set_field_value(MetadataField.COPYRIGHT, str(value), "rights")
                elif tag_name == "ImageDescription":
                    metadata.set_field_value(MetadataField.DESCRIPTION, str(value), "descriptive")
                
                # Store in EXIF metadata
                metadata.exif_metadata[tag_name] = str(value)
            
        except Exception as e:
            logger.error(f"EXIF metadata extraction failed: {e}")
    
    async def _extract_video_metadata(self, content_data: Union[str, bytes, Path], metadata: ExtractedMetadata) -> None:
        """Extract metadata from video files."""
        try:
            if not METADATA_FEATURES:
                logger.warning("Video metadata extraction requires ffmpeg")
                return
            
            # Handle file path
            file_path = None
            if isinstance(content_data, Path):
                file_path = str(content_data)
            elif isinstance(content_data, str) and Path(content_data).exists():
                file_path = content_data
            elif isinstance(content_data, bytes):
                # Create temporary file for bytes data
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                    tmp_file.write(content_data)
                    file_path = tmp_file.name
            
            if not file_path:
                return
            
            # Probe video file with ffmpeg
            probe = ffmpeg.probe(file_path)
            
            # Extract format information
            format_info = probe.get("format", {})
            metadata.technical.update({
                "duration": float(format_info.get("duration", 0)),
                "size": int(format_info.get("size", 0)),
                "bit_rate": int(format_info.get("bit_rate", 0)),
                "format_name": format_info.get("format_name", ""),
                "format_long_name": format_info.get("format_long_name", "")
            })
            
            # Extract video stream information
            video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
            if video_streams:
                video_stream = video_streams[0]
                metadata.technical.update({
                    "width": video_stream.get("width", 0),
                    "height": video_stream.get("height", 0),
                    "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                    "codec": video_stream.get("codec_name", ""),
                    "frame_rate": video_stream.get("r_frame_rate", ""),
                    "pixel_format": video_stream.get("pix_fmt", "")
                })
            
            # Extract audio stream information
            audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
            if audio_streams:
                audio_stream = audio_streams[0]
                metadata.technical.update({
                    "audio_codec": audio_stream.get("codec_name", ""),
                    "sample_rate": int(audio_stream.get("sample_rate", 0)),
                    "channels": audio_stream.get("channels", 0),
                    "channel_layout": audio_stream.get("channel_layout", "")
                })
            
            # Extract metadata tags
            tags = format_info.get("tags", {})
            if tags:
                # Map common video metadata tags
                if "title" in tags:
                    metadata.set_field_value(MetadataField.TITLE, tags["title"], "descriptive")
                if "artist" in tags:
                    metadata.set_field_value(MetadataField.ARTIST, tags["artist"], "descriptive")
                if "album" in tags:
                    metadata.set_field_value(MetadataField.ALBUM, tags["album"], "descriptive")
                if "date" in tags:
                    metadata.set_field_value(MetadataField.CREATION_DATE, tags["date"], "administrative")
                if "comment" in tags:
                    metadata.set_field_value(MetadataField.DESCRIPTION, tags["comment"], "descriptive")
            
            # Clean up temporary file if created
            if isinstance(content_data, bytes) and file_path:
                try:
                    Path(file_path).unlink()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
    
    async def _extract_text_metadata(self, content_data: Union[str, bytes, Path], metadata: ExtractedMetadata) -> None:
        """Extract metadata from text content."""
        try:
            # Read text content
            text_content = ""
            if isinstance(content_data, str):
                if Path(content_data).exists():
                    text_content = Path(content_data).read_text(encoding='utf-8')
                else:
                    text_content = content_data
            elif isinstance(content_data, bytes):
                text_content = content_data.decode('utf-8', errors='ignore')
            elif isinstance(content_data, Path):
                text_content = content_data.read_text(encoding='utf-8')
            
            if not text_content:
                return
            
            # Extract basic text statistics
            metadata.technical.update({
                "character_count": len(text_content),
                "word_count": len(text_content.split()),
                "line_count": len(text_content.splitlines()),
                "encoding": "utf-8"
            })
            
            # Detect language
            try:
                language = detect(text_content[:1000])  # Use first 1000 chars for detection
                metadata.set_field_value(MetadataField.LANGUAGE, language, "descriptive")
            except LangDetectError:
                pass
            
            # Extract title from first line or heading
            lines = text_content.splitlines()
            if lines:
                first_line = lines[0].strip()
                if first_line and len(first_line) < 200:
                    # Check if it looks like a title (no punctuation at end, reasonable length)
                    if not first_line.endswith('.') and len(first_line.split()) > 1:
                        metadata.set_field_value(MetadataField.TITLE, first_line, "descriptive")
            
            # Extract description from first paragraph
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
            if paragraphs and len(paragraphs) > 1:
                description = paragraphs[1][:500]  # First 500 chars of second paragraph
                metadata.set_field_value(MetadataField.DESCRIPTION, description, "descriptive")
            
        except Exception as e:
            logger.error(f"Text metadata extraction failed: {e}")
    
    async def _extract_universal_metadata(self, content_data: Union[str, bytes, Path], metadata: ExtractedMetadata) -> None:
        """Extract universal metadata applicable to all content types."""
        try:
            # Set extraction timestamp
            metadata.extraction_timestamp = datetime.now(timezone.utc)
            metadata.extraction_method = "automated"
            
            # Calculate file information if possible
            if isinstance(content_data, (str, Path)):
                file_path = Path(content_data)
                if file_path.exists():
                    stat = file_path.stat()
                    metadata.file_path = str(file_path)
                    metadata.file_size = stat.st_size
                    metadata.administrative.update({
                        "file_name": file_path.name,
                        "file_extension": file_path.suffix,
                        "creation_time": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                        "modification_time": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        "file_size_mb": round(stat.st_size / (1024 * 1024), 2)
                    })
            
            elif isinstance(content_data, bytes):
                metadata.file_size = len(content_data)
                metadata.administrative["file_size_mb"] = round(len(content_data) / (1024 * 1024), 2)
            
            # Generate content fingerprint
            if isinstance(content_data, bytes):
                fingerprint = hashlib.sha256(content_data).hexdigest()[:16]
            elif isinstance(content_data, (str, Path)):
                file_path = Path(content_data)
                if file_path.exists():
                    fingerprint = hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
                else:
                    fingerprint = hashlib.sha256(str(content_data).encode()).hexdigest()[:16]
            else:
                fingerprint = hashlib.sha256(str(content_data).encode()).hexdigest()[:16]
            
            metadata.set_field_value(MetadataField.CONTENT_FINGERPRINT, fingerprint, "technical")
            
        except Exception as e:
            logger.error(f"Universal metadata extraction failed: {e}")
    
    async def _apply_automatic_fixes(self, validation_result: MetadataValidationResult) -> None:
        """Apply automatic fixes to metadata issues."""
        try:
            if not self.enable_auto_fix:
                return
            
            logger.debug("Applying automatic metadata fixes")
            
            auto_fixable_issues = validation_result.get_auto_fixable_issues()
            fixes_applied = 0
            
            for issue in auto_fixable_issues:
                try:
                    if issue.suggested_value is not None:
                        # Find the metadata field and apply the fix
                        for field in MetadataField:
                            if field.value == issue.field:
                                validation_result.extracted_metadata.set_field_value(
                                    field, issue.suggested_value
                                )
                                fixes_applied += 1
                                break
                                
                except Exception as e:
                    logger.error(f"Failed to apply fix for {issue.field}: {e}")
            
            if fixes_applied > 0:
                logger.info(f"Applied {fixes_applied} automatic metadata fixes")
                self._stats["auto_fixes_applied"] += fixes_applied
            
        except Exception as e:
            logger.error(f"Automatic fixes application failed: {e}")
    
    def _calculate_quality_scores(self, validation_result: MetadataValidationResult) -> None:
        """Calculate metadata quality scores."""
        try:
            # Calculate completeness score
            validation_result.calculate_completeness_score()
            
            # Calculate quality score based on various factors
            quality_factors = {
                "completeness": validation_result.completeness_score * 0.4,
                "accuracy": self._calculate_accuracy_score(validation_result) * 0.3,
                "consistency": self._calculate_consistency_score(validation_result) * 0.2,
                "richness": self._calculate_richness_score(validation_result) * 0.1
            }
            
            validation_result.quality_score = sum(quality_factors.values())
            
            # Calculate standardization score
            validation_result.standardization_score = self._calculate_standardization_score(validation_result)
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
    
    def _calculate_accuracy_score(self, validation_result: MetadataValidationResult) -> float:
        """Calculate metadata accuracy score."""
        try:
            total_issues = len(validation_result.issues) + len(validation_result.warnings)
            total_fields = len([f for f in MetadataField if validation_result.extracted_metadata.get_field_value(f)])
            
            if total_fields == 0:
                return 0.0
            
            # Penalize based on issue severity
            error_penalty = len([i for i in validation_result.issues if i.severity == ValidationSeverity.ERROR]) * 10
            warning_penalty = len([i for i in validation_result.warnings if i.severity == ValidationSeverity.WARNING]) * 5
            
            total_penalty = error_penalty + warning_penalty
            max_penalty = total_fields * 10
            
            accuracy = max(0, 100 - (total_penalty / max_penalty * 100)) if max_penalty > 0 else 100
            return accuracy
            
        except Exception as e:
            logger.error(f"Accuracy score calculation failed: {e}")
            return 0.0
    
    def _calculate_consistency_score(self, validation_result: MetadataValidationResult) -> float:
        """Calculate metadata consistency score."""
        try:
            # Check for consistency between related fields
            consistency_checks = [
                self._check_date_consistency(validation_result.extracted_metadata),
                self._check_format_consistency(validation_result.extracted_metadata),
                self._check_content_consistency(validation_result.extracted_metadata)
            ]
            
            passed_checks = sum(1 for check in consistency_checks if check)
            total_checks = len(consistency_checks)
            
            return (passed_checks / total_checks * 100) if total_checks > 0 else 100
            
        except Exception as e:
            logger.error(f"Consistency score calculation failed: {e}")
            return 0.0
    
    def _calculate_richness_score(self, validation_result: MetadataValidationResult) -> float:
        """Calculate metadata richness score."""
        try:
            # Count different types of metadata
            descriptive_fields = len([k for k in validation_result.extracted_metadata.descriptive.keys() if validation_result.extracted_metadata.descriptive[k]])
            technical_fields = len([k for k in validation_result.extracted_metadata.technical.keys() if validation_result.extracted_metadata.technical[k]])
            administrative_fields = len([k for k in validation_result.extracted_metadata.administrative.keys() if validation_result.extracted_metadata.administrative[k]])
            rights_fields = len([k for k in validation_result.extracted_metadata.rights.keys() if validation_result.extracted_metadata.rights[k]])
            
            total_rich_fields = descriptive_fields + technical_fields + administrative_fields + rights_fields
            max_rich_fields = 20  # Estimated maximum richness
            
            richness = min(100, (total_rich_fields / max_rich_fields * 100))
            return richness
            
        except Exception as e:
            logger.error(f"Richness score calculation failed: {e}")
            return 0.0
    
    def _calculate_standardization_score(self, validation_result: MetadataValidationResult) -> float:
        """Calculate metadata standardization score."""
        try:
            # Check adherence to standards
            standard_scores = []
            
            # Check basic field naming conventions
            if validation_result.extracted_metadata.get_field_value(MetadataField.TITLE):
                standard_scores.append(100)
            else:
                standard_scores.append(0)
            
            # Check date format standardization
            creation_date = validation_result.extracted_metadata.get_field_value(MetadataField.CREATION_DATE)
            if creation_date:
                try:
                    datetime.fromisoformat(str(creation_date).replace('Z', '+00:00'))
                    standard_scores.append(100)
                except:
                    standard_scores.append(50)
            else:
                standard_scores.append(0)
            
            # Check encoding and character standards
            title = validation_result.extracted_metadata.get_field_value(MetadataField.TITLE)
            if title:
                try:
                    title.encode('utf-8')
                    standard_scores.append(100)
                except:
                    standard_scores.append(0)
            
            return sum(standard_scores) / len(standard_scores) if standard_scores else 0
            
        except Exception as e:
            logger.error(f"Standardization score calculation failed: {e}")
            return 0.0
    
    def _check_date_consistency(self, metadata: ExtractedMetadata) -> bool:
        """Check consistency between date fields."""
        try:
            creation_date = metadata.get_field_value(MetadataField.CREATION_DATE)
            release_date = metadata.get_field_value(MetadataField.RELEASE_DATE)
            
            if creation_date and release_date:
                # Release date should not be before creation date
                try:
                    creation = datetime.fromisoformat(str(creation_date).replace('Z', '+00:00'))
                    release = datetime.fromisoformat(str(release_date).replace('Z', '+00:00'))
                    return release >= creation
                except:
                    return True  # Can't parse, assume consistent
            
            return True
            
        except Exception as e:
            logger.error(f"Date consistency check failed: {e}")
            return False
    
    def _check_format_consistency(self, metadata: ExtractedMetadata) -> bool:
        """Check consistency between format-related fields."""
        try:
            file_format = metadata.get_field_value(MetadataField.FILE_FORMAT)
            codec = metadata.technical.get("codec")
            
            if file_format and codec:
                # Check if codec is appropriate for format
                format_codec_map = {
                    "mp3": ["mp3", "mpeg"],
                    "mp4": ["aac", "h264", "h265"],
                    "wav": ["pcm", "wav"],
                    "flac": ["flac"],
                    "png": ["png"],
                    "jpg": ["jpeg", "jpg"],
                    "jpeg": ["jpeg", "jpg"]
                }
                
                expected_codecs = format_codec_map.get(file_format.lower(), [])
                if expected_codecs:
                    return any(expected in str(codec).lower() for expected in expected_codecs)
            
            return True
            
        except Exception as e:
            logger.error(f"Format consistency check failed: {e}")
            return False
    
    def _check_content_consistency(self, metadata: ExtractedMetadata) -> bool:
        """Check consistency between content fields."""
        try:
            title = metadata.get_field_value(MetadataField.TITLE)
            description = metadata.get_field_value(MetadataField.DESCRIPTION)
            
            if title and description:
                # Check if title appears in description or vice versa
                title_lower = str(title).lower()
                description_lower = str(description).lower()
                
                # They should be related but not identical
                if title_lower == description_lower:
                    return False  # Identical content
                
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Content consistency check failed: {e}")
            return False
    
    def _update_statistics(self, validation_result: MetadataValidationResult) -> None:
        """Update validator statistics."""
        try:
            # Update processing time
            total_time = self._stats["avg_processing_time"] * self._stats["total_validations"]
            total_time += validation_result.validation_duration
            self._stats["avg_processing_time"] = total_time / (self._stats["total_validations"] + 1)
            
            # Update field counts
            validation_result.total_fields_extracted = len([
                f for f in MetadataField 
                if validation_result.extracted_metadata.get_field_value(f)
            ])
            
        except Exception as e:
            logger.error(f"Statistics update failed: {e}")
    
    # Public utility methods
    
    async def export_metadata(
        self,
        metadata: ExtractedMetadata,
        format_type: MetadataStandard = MetadataStandard.DUBLIN_CORE,
        output_path: Optional[Path] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Export metadata in specified standard format.
        
        Args:
            metadata: Metadata to export
            format_type: Target metadata standard
            output_path: Optional file path to save export
        
        Returns:
            Exported metadata as dict or file path if saved
        """
        try:
            logger.info(f"Exporting metadata in {format_type.value} format")
            
            exported_data = {}
            
            if format_type == MetadataStandard.DUBLIN_CORE:
                exported_data = self._export_dublin_core(metadata)
            elif format_type == MetadataStandard.EXIF:
                exported_data = self._export_exif(metadata)
            elif format_type == MetadataStandard.ID3V2:
                exported_data = self._export_id3(metadata)
            else:
                exported_data = self._export_custom(metadata)
            
            if output_path:
                output_path = Path(output_path)
                output_path.write_text(json.dumps(exported_data, indent=2, ensure_ascii=False))
                logger.info(f"Metadata exported to {output_path}")
                return str(output_path)
            
            return exported_data
            
        except Exception as e:
            logger.error(f"Metadata export failed: {e}")
            return {}
    
    def _export_dublin_core(self, metadata: ExtractedMetadata) -> Dict[str, Any]:
        """Export metadata in Dublin Core format."""
        return {
            "dc:title": metadata.get_field_value(MetadataField.TITLE),
            "dc:creator": metadata.get_field_value(MetadataField.ARTIST),
            "dc:description": metadata.get_field_value(MetadataField.DESCRIPTION),
            "dc:date": metadata.get_field_value(MetadataField.CREATION_DATE),
            "dc:format": metadata.technical.get("format"),
            "dc:language": metadata.get_field_value(MetadataField.LANGUAGE),
            "dc:rights": metadata.get_field_value(MetadataField.COPYRIGHT),
            "dc:subject": metadata.get_field_value(MetadataField.TAGS)
        }
    
    def _export_exif(self, metadata: ExtractedMetadata) -> Dict[str, Any]:
        """Export metadata in EXIF format."""
        return metadata.exif_metadata
    
    def _export_id3(self, metadata: ExtractedMetadata) -> Dict[str, Any]:
        """
Export metadata in ID3 format."""
        return metadata.id3_metadata
    
    def _export_custom(self, metadata: ExtractedMetadata) -> Dict[str, Any]:
        """
Export metadata in custom format."""
        return {
            "descriptive": metadata.descriptive,
            "technical": metadata.technical,
            "administrative": metadata.administrative,
            "rights": metadata.rights,
            "ai_generated": metadata.ai_generated
        }
    
    async def import_metadata(
        self,
        import_data: Union[Dict[str, Any], str, Path],
        source_format: MetadataStandard = MetadataStandard.CUSTOM
    ) -> ExtractedMetadata:
        """
        Import metadata from various formats.
        
        Args:
            import_data: Data to import (dict, JSON string, or file path)
            source_format: Source metadata standard
        
        Returns:
            Imported metadata
        """
        try:
            logger.info(f"Importing metadata from {source_format.value} format")
            
            # Parse input data
            if isinstance(import_data, (str, Path)):
                if Path(import_data).exists():
                    data = json.loads(Path(import_data).read_text())
                else:
                    data = json.loads(import_data)
            else:
                data = import_data
            
            metadata = ExtractedMetadata()
            
            if source_format == MetadataStandard.DUBLIN_CORE:
                self._import_dublin_core(data, metadata)
            elif source_format == MetadataStandard.EXIF:
                self._import_exif(data, metadata)
            elif source_format == MetadataStandard.ID3V2:
                self._import_id3(data, metadata)
            else:
                self._import_custom(data, metadata)
            
            logger.info("Metadata import completed")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata import failed: {e}")
            return ExtractedMetadata()
    
    def _import_dublin_core(self, data: Dict[str, Any], metadata: ExtractedMetadata) -> None:
        """Import Dublin Core metadata."""
        dc_mapping = {
            "dc:title": MetadataField.TITLE,
            "dc:creator": MetadataField.ARTIST,
            "dc:description": MetadataField.DESCRIPTION,
            "dc:date": MetadataField.CREATION_DATE,
            "dc:language": MetadataField.LANGUAGE,
            "dc:rights": MetadataField.COPYRIGHT,
            "dc:subject": MetadataField.TAGS
        }
        
        for dc_field, metadata_field in dc_mapping.items():
            if dc_field in data and data[dc_field]:
                metadata.set_field_value(metadata_field, data[dc_field], "descriptive")
    
    def _import_exif(self, data: Dict[str, Any], metadata: ExtractedMetadata) -> None:
        """Import EXIF metadata."""
        metadata.exif_metadata = data
        
        # Map common EXIF fields
        if "DateTime" in data:
            metadata.set_field_value(MetadataField.CREATION_DATE, data["DateTime"], "administrative")
        if "Artist" in data:
            metadata.set_field_value(MetadataField.ARTIST, data["Artist"], "descriptive")
        if "Copyright" in data:
            metadata.set_field_value(MetadataField.COPYRIGHT, data["Copyright"], "rights")
    
    def _import_id3(self, data: Dict[str, Any], metadata: ExtractedMetadata) -> None:
        """Import ID3 metadata."""
        metadata.id3_metadata = data
        
        # Map common ID3 fields
        id3_mapping = {
            "TIT2": MetadataField.TITLE,
            "TPE1": MetadataField.ARTIST,
            "TALB": MetadataField.ALBUM,
            "TCON": MetadataField.GENRE,
            "TDRC": MetadataField.RELEASE_DATE,
        }
        
        for id3_field, metadata_field in id3_mapping.items():
            if id3_field in data:
                metadata.set_field_value(metadata_field, data[id3_field], "descriptive")
    
    def _import_custom(self, data: Dict[str, Any], metadata: ExtractedMetadata) -> None:
        """Import custom format metadata."""
        if "descriptive" in data:
            metadata.descriptive.update(data["descriptive"])
        if "technical" in data:
            metadata.technical.update(data["technical"])
        if "administrative" in data:
            metadata.administrative.update(data["administrative"])
        if "rights" in data:
            metadata.rights.update(data["rights"])
        if "ai_generated" in data:
            metadata.ai_generated.update(data["ai_generated"])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "total_validations": self._stats["total_validations"],
            "successful_extractions": self._stats["successful_extractions"],
            "enhancements_applied": self._stats["enhancements_applied"],
            "auto_fixes_applied": self._stats["auto_fixes_applied"],
            "average_processing_time": round(self._stats["avg_processing_time"], 3),
            "success_rate": (self._stats["successful_extractions"] / max(1, self._stats["total_validations"])) * 100,
            "ai_enhancement_enabled": self.enable_ai_enhancement,
            "auto_fix_enabled": self.enable_auto_fix,
            "version": self.VERSION
        }
    
    def reset_statistics(self) -> None:
        """Reset validator statistics."""
        self._stats = {
            "total_validations": 0,
            "successful_extractions": 0,
            "enhancements_applied": 0,
            "auto_fixes_applied": 0,
            "avg_processing_time": 0.0
        }
        logger.info("Validator statistics reset")


# Utility functions for common metadata operations

async def extract_metadata_from_file(
    file_path: Union[str, Path],
    validator: Optional[MetadataValidator] = None,
    enhancement_level: str = "standard"
) -> MetadataValidationResult:
    """
    Convenience function to extract metadata from a file.
    
    Args:
        file_path: Path to the file
        validator: Optional validator instance
        enhancement_level: Level of AI enhancement
    
    Returns:
        Metadata validation result
    """
    if validator is None:
        validator = MetadataValidator()
    
    return await validator.validate_metadata_comprehensive(
        file_path,
        content_type="auto",
        enhancement_level=enhancement_level
    )


async def batch_validate_metadata(
    file_paths: List[Union[str, Path]],
    validator: Optional[MetadataValidator] = None,
    max_concurrent: int = 5
) -> List[MetadataValidationResult]:
    """
    Batch validate metadata for multiple files.
    
    Args:
        file_paths: List of file paths
        validator: Optional validator instance
        max_concurrent: Maximum concurrent validations
    
    Returns:
        List of metadata validation results
    """
    if validator is None:
        validator = MetadataValidator()
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def validate_single(file_path):
        async with semaphore:
            return await validator.validate_metadata_comprehensive(file_path)
    
    tasks = [validate_single(fp) for fp in file_paths]
    return await asyncio.gather(*tasks, return_exceptions=True)


def create_metadata_report(
    validation_results: List[MetadataValidationResult],
    output_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Create a comprehensive metadata validation report.
    
    Args:
        validation_results: List of validation results
        output_path: Optional path to save report
    
    Returns:
        Report data
    """
    try:
        total_files = len(validation_results)
        valid_files = len([r for r in validation_results if r.is_valid])
        
        report = {
            "summary": {
                "total_files": total_files,
                "valid_files": valid_files,
                "invalid_files": total_files - valid_files,
                "success_rate": (valid_files / total_files * 100) if total_files > 0 else 0,
                "average_completeness": sum(r.completeness_score for r in validation_results) / total_files if total_files > 0 else 0,
                "average_quality": sum(r.quality_score for r in validation_results) / total_files if total_files > 0 else 0
            },
            "issues": {
                "critical": sum(len(r.get_critical_issues()) for r in validation_results),
                "errors": sum(len(r.issues) for r in validation_results),
                "warnings": sum(len(r.warnings) for r in validation_results),
                "auto_fixable": sum(len(r.get_auto_fixable_issues()) for r in validation_results)
            },
            "enhancement": {
                "files_enhanced": len([r for r in validation_results if r.enhancement_applied]),
                "total_fields_enhanced": sum(r.total_fields_enhanced for r in validation_results)
            },
            "performance": {
                "total_processing_time": sum(r.validation_duration for r in validation_results),
                "average_processing_time": sum(r.validation_duration for r in validation_results) / total_files if total_files > 0 else 0
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
            logger.info(f"Metadata report saved to {output_path}")
        
        return report
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {}
    
    async def _run_validation_rules(self, validation_result: MetadataValidationResult) -> None:
        """Run validation rules on extracted metadata."""
        try:
            logger.debug("Running metadata validation rules")
            
            for field, rules in self._validation_rules.items():
                field_value = validation_result.extracted_metadata.get_field_value(field)
                
                for rule in rules:
                    try:
                        issue = await rule(field_value, field)
                        if issue:
                            if issue.severity == ValidationSeverity.CRITICAL:
                                validation_result.issues.append(issue)
                                validation_result.is_valid = False
                            elif issue.severity == ValidationSeverity.ERROR:
                                validation_result.issues.append(issue)
                            else:
                                validation_result.warnings.append(issue)
                                
                    except Exception as e:
                        logger.error(f"Validation rule failed for {field.value}: {e}")
            
            validation_result.total_fields_validated = len(self._validation_rules)
            
        except Exception as e:
            logger.error(f"Validation rules execution failed: {e}")
    
    async def _validate_title_length(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate title length."""
        if not value:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="missing_value",
                severity=ValidationSeverity.ERROR,
                message="Title is required but missing",
                auto_fixable=False
            )
        
        title_str = str(value)
        if len(title_str) > 200:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="value_too_long",
                severity=ValidationSeverity.WARNING,
                message=f"Title is too long ({len(title_str)} characters, max 200)",
                current_value=title_str,
                suggested_value=title_str[:197] + "...",
                auto_fixable=True
            )
        
        if len(title_str) < 3:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="value_too_short",
                severity=ValidationSeverity.WARNING,
                message=f"Title is very short ({len(title_str)} characters)",
                current_value=title_str,
                auto_fixable=False
            )
        
        return None
    
    async def _validate_title_content(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate title content quality."""
        if not value:
            return None
        
        title_str = str(value).strip()
        
        # Check for placeholder content
        placeholder_patterns = [
            r"^untitled.*",
            r"^new.*track.*",
            r"^track\s*\d*$",
            r"^audio\s*\d*$",
            r"^recording\s*\d*$"
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, title_str, re.IGNORECASE):
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="placeholder_content",
                    severity=ValidationSeverity.WARNING,
                    message="Title appears to be placeholder content",
                    current_value=title_str,
                    auto_fixable=False
                )
        
        # Check for excessive capitalization
        if title_str.isupper() and len(title_str) > 10:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="excessive_caps",
                severity=ValidationSeverity.WARNING,
                message="Title is in all caps, consider proper capitalization",
                current_value=title_str,
                suggested_value=title_str.title(),
                auto_fixable=True
            )
        
        return None
    
    async def _validate_title_encoding(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate title encoding and characters."""
        if not value:
            return None
        
        title_str = str(value)
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        found_invalid = [char for char in invalid_chars if char in title_str]
        
        if found_invalid:
            clean_title = title_str
            for char in found_invalid:
                clean_title = clean_title.replace(char, '')
            
            return MetadataValidationIssue(
                field=field.value,
                issue_type="invalid_characters",
                severity=ValidationSeverity.WARNING,
                message=f"Title contains invalid characters: {', '.join(found_invalid)}",
                current_value=title_str,
                suggested_value=clean_title.strip(),
                auto_fixable=True
            )
        
        return None
    
    async def _validate_artist_format(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate artist field format."""
        if not value:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="missing_value",
                severity=ValidationSeverity.ERROR,
                message="Artist name is required but missing",
                auto_fixable=False
            )
        
        artist_str = str(value).strip()
        
        # Check for common formatting issues
        if artist_str.startswith("feat.") or artist_str.startswith("ft."):
            return MetadataValidationIssue(
                field=field.value,
                issue_type="format_issue",
                severity=ValidationSeverity.WARNING,
                message="Artist field should not start with 'feat.' or 'ft.'",
                current_value=artist_str,
                auto_fixable=False
            )
        
        return None
    
    async def _validate_artist_length(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate artist field length."""
        if not value:
            return None
        
        artist_str = str(value)
        if len(artist_str) > 100:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="value_too_long",
                severity=ValidationSeverity.WARNING,
                message=f"Artist name is very long ({len(artist_str)} characters)",
                current_value=artist_str,
                auto_fixable=False
            )
        
        return None
    
    async def _validate_artist_characters(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate artist field characters."""
        if not value:
            return None
        
        artist_str = str(value)
        
        # Check for excessive special characters
        special_char_count = sum(1 for char in artist_str if not char.isalnum() and char not in [' ', '-', '.', "'"])
        if special_char_count > len(artist_str) * 0.3:  # More than 30% special characters
            return MetadataValidationIssue(
                field=field.value,
                issue_type="excessive_special_chars",
                severity=ValidationSeverity.WARNING,
                message="Artist name contains excessive special characters",
                current_value=artist_str,
                auto_fixable=False
            )
        
        return None
    
    async def _validate_duration_format(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate duration format and range."""
        if not value:
            return None
        
        try:
            duration = float(value)
            
            if duration <= 0:
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="invalid_duration",
                    severity=ValidationSeverity.ERROR,
                    message="Duration must be positive",
                    current_value=duration,
                    auto_fixable=False
                )
            
            # Check for extremely long durations (>24 hours)
            if duration > 86400:
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="duration_too_long",
                    severity=ValidationSeverity.WARNING,
                    message=f"Duration is extremely long ({duration/3600:.1f} hours)",
                    current_value=duration,
                    auto_fixable=False
                )
            
            # Check for extremely short durations (<1 second)
            if duration < 1:
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="duration_too_short",
                    severity=ValidationSeverity.WARNING,
                    message=f"Duration is very short ({duration:.2f} seconds)",
                    current_value=duration,
                    auto_fixable=False
                )
                
        except (ValueError, TypeError):
            return MetadataValidationIssue(
                field=field.value,
                issue_type="invalid_format",
                severity=ValidationSeverity.ERROR,
                message="Duration must be a valid number",
                current_value=value,
                auto_fixable=False
            )
        
        return None
    
    async def _validate_duration_range(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate duration is within reasonable range for content type."""
        if not value:
            return None
        
        try:
            duration = float(value)
            
            # Different ranges for different content types
            # For now, use general audio/video ranges
            if duration < 5:  # Less than 5 seconds
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="unusually_short",
                    severity=ValidationSeverity.INFO,
                    message=f"Content is unusually short ({duration:.1f} seconds)",
                    current_value=duration,
                    auto_fixable=False
                )
            
            if duration > 3600:  # More than 1 hour
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="unusually_long",
                    severity=ValidationSeverity.INFO,
                    message=f"Content is unusually long ({duration/60:.1f} minutes)",
                    current_value=duration,
                    auto_fixable=False
                )
                
        except (ValueError, TypeError):
            pass
        
        return None
    
    async def _validate_date_format(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate date format."""
        if not value:
            return None
        
        date_str = str(value)
        
        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y",
            "%Y-%m",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="invalid_date_format",
                severity=ValidationSeverity.ERROR,
                message=f"Invalid date format: {date_str}",
                current_value=date_str,
                suggested_value="YYYY-MM-DD format recommended",
                auto_fixable=False
            )
        
        return None
    
    async def _validate_date_validity(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate date logical validity."""
        if not value:
            return None
        
        date_str = str(value)
        
        # Extract year if possible
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            year = int(year_match.group())
            current_year = datetime.now().year
            
            if year < 1900:
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="date_too_old",
                    severity=ValidationSeverity.WARNING,
                    message=f"Date appears too old: {year}",
                    current_value=date_str,
                    auto_fixable=False
                )
            
            if year > current_year + 1:
                return MetadataValidationIssue(
                    field=field.value,
                    issue_type="future_date",
                    severity=ValidationSeverity.WARNING,
                    message=f"Date is in the future: {year}",
                    current_value=date_str,
                    auto_fixable=False
                )
        
        return None
    
    async def _validate_copyright_format(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate copyright format."""
        if not value:
            return MetadataValidationIssue(
                field=field.value,
                issue_type="missing_copyright",
                severity=ValidationSeverity.WARNING,
                message="Copyright information is missing",
                auto_fixable=False
            )
        
        copyright_str = str(value)
        
        # Check for proper copyright format
        if not re.search(r'((c)|copyright|\(c\))', copyright_str, re.IGNORECASE):
            return MetadataValidationIssue(
                field=field.value,
                issue_type="missing_copyright_symbol",
                severity=ValidationSeverity.INFO,
                message="Copyright should include (c) symbol or 'Copyright' text",
                current_value=copyright_str,
                suggested_value=f"(c) {copyright_str}",
                auto_fixable=True
            )
        
        return None
    
    async def _validate_copyright_completeness(self, value: Any, field: MetadataField) -> Optional[MetadataValidationIssue]:
        """Validate copyright information completeness."""
        if not value:
            return None
        
        copyright_str = str(value)
        
        # Check for year in copyright
        if not re.search(r'\b(19|20)\d{2}\b', copyright_str):
            return MetadataValidationIssue(
                field=field.value,
                issue_type="missing_copyright_year",
                severity=ValidationSeverity.INFO,
                message="Copyright should include the year",
                current_value=copyright_str,
                auto_fixable=False
            )
        
        return None
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetadataField:
    """Metadata field definition."""
    field_name: str
    field_type: type
    required: bool = False
    default_value: Optional[Any] = None
    
    # Validation rules
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    
    # Field metadata
    description: str = ""
    example: Optional[str] = None
    standard: Optional[MetadataStandard] = None


@dataclass
class MetadataValidationIssue:
    """Metadata validation issue."""
    field_name: str
    issue_type: str
    severity: ValidationSeverity
    message: str
    current_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    suggestion: Optional[str] = None


@dataclass
class MetadataValidationResult:
    """
Metadata validation result."""
    is_valid: bool
    completeness_score: float
    quality_score: float
    compliance_score: float
    
    # Validation details
    validated_fields: int = 0
    missing_fields: List[str] = field(default_factory=list)
    invalid_fields: List[str] = field(default_factory=list)
    
    # Issues and suggestions
    issues: List[MetadataValidationIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # Enrichment opportunities
    enrichment_opportunities: List[str] = field(default_factory=list)
    auto_generated_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Validation metadata
    validator_version: str = "1.0.0"
    validation_timestamp: float = field(default_factory=time.time)
    validation_duration: float = 0.0


class ID3Validator:
    """
    ID3 metadata validator for audio files.
    
    Validates and enriches ID3 tags in audio content with comprehensive
    tag validation, version compatibility, and automatic enrichment.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ID3 validator.
        
        Args:
            config: Validator configuration
        """
        self.config = config or {}
        
        # ID3 field definitions
        self.id3_fields = self._init_id3_fields()
        
        # Version support
        self.supported_versions = ["2.3", "2.4"]
        
        logger.info("ID3Validator initialized")
    
    async def validate_id3_metadata(
        self,
        metadata: Dict[str, Any],
        strict_mode: bool = False
    ) -> MetadataValidationResult:
        """
        Validate ID3 metadata.
        
        Args:
            metadata: ID3 metadata to validate
            strict_mode: Enable strict validation
            
        Returns:
            Validation result
        """
        start_time = time.time()
        
        try:
            result = MetadataValidationResult(
                is_valid=True,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0
            )
            
            # Validate required fields
            await self._validate_required_fields(metadata, result, strict_mode)
            
            # Validate field formats
            await self._validate_field_formats(metadata, result)
            
            # Validate field values
            await self._validate_field_values(metadata, result)
            
            # Check version compatibility
            await self._validate_version_compatibility(metadata, result)
            
            # Calculate scores
            result.completeness_score = await self._calculate_completeness_score(metadata, result)
            result.quality_score = await self._calculate_quality_score(metadata, result)
            result.compliance_score = await self._calculate_compliance_score(metadata, result)
            
            # Generate suggestions
            result.suggestions = await self._generate_id3_suggestions(metadata, result)
            
            # Identify enrichment opportunities
            result.enrichment_opportunities = await self._identify_enrichment_opportunities(metadata)
            
            result.validation_duration = time.time() - start_time
            result.is_valid = len([issue for issue in result.issues if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]) == 0
            
            return result
            
        except Exception as e:
            logger.error(f"ID3 validation failed: {str(e)}")
            return MetadataValidationResult(
                is_valid=False,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0,
                validation_duration=time.time() - start_time,
                issues=[MetadataValidationIssue(
                    field_name="general",
                    issue_type="validation_error",
                    severity=ValidationSeverity.CRITICAL,
                    message=str(e)
                )]
            )
    
    async def enrich_id3_metadata(
        self,
        metadata: Dict[str, Any],
        auto_generate: bool = True
    ) -> Dict[str, Any]:
        """
        Enrich ID3 metadata with missing or improved information.
        
        Args:
            metadata: Existing metadata
            auto_generate: Enable automatic field generation
            
        Returns:
            Enriched metadata
        """
        enriched = metadata.copy()
        
        try:
            # Auto-generate missing basic fields
            if auto_generate:
                if not enriched.get("TALB"):  # Album
                    enriched["TALB"] = "Single Release"
                
                if not enriched.get("TYER"):  # Year
                    enriched["TYER"] = str(datetime.now().year)
                
                if not enriched.get("TCON"):  # Genre
                    enriched["TCON"] = "Other"
                
                if not enriched.get("TPE1") and enriched.get("artist"):  # Artist
                    enriched["TPE1"] = enriched["artist"]
                
                if not enriched.get("TIT2") and enriched.get("title"):  # Title
                    enriched["TIT2"] = enriched["title"]
            
            # Normalize field values
            await self._normalize_id3_fields(enriched)
            
            # Add technical metadata if missing
            await self._add_technical_metadata(enriched)
            
            return enriched
            
        except Exception as e:
            logger.error(f"ID3 enrichment failed: {str(e)}")
            return metadata
    
    async def _validate_required_fields(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult,
        strict_mode: bool
    ):
        """Validate required ID3 fields."""
        required_fields = ["TIT2", "TPE1"]  # Title, Artist
        if strict_mode:
            required_fields.extend(["TALB", "TYER", "TCON"])  # Album, Year, Genre
        
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                result.missing_fields.append(field)
                result.issues.append(MetadataValidationIssue(
                    field_name=field,
                    issue_type="missing_required_field",
                    severity=ValidationSeverity.ERROR,
                    message=f"Required field {field} is missing",
                    suggestion=f"Add {field} field with appropriate value"
                ))
    
    async def _validate_field_formats(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate ID3 field formats."""
        for field_name, field_def in self.id3_fields.items():
            if field_name in metadata:
                value = metadata[field_name]
                
                # Type validation
                if not isinstance(value, field_def.field_type):
                    result.invalid_fields.append(field_name)
                    result.issues.append(MetadataValidationIssue(
                        field_name=field_name,
                        issue_type="invalid_type",
                        severity=ValidationSeverity.ERROR,
                        message=f"Field {field_name} should be {field_def.field_type.__name__}",
                        current_value=value
                    ))
                
                # Length validation
                if isinstance(value, str):
                    if field_def.max_length and len(value) > field_def.max_length:
                        result.issues.append(MetadataValidationIssue(
                            field_name=field_name,
                            issue_type="value_too_long",
                            severity=ValidationSeverity.WARNING,
                            message=f"Field {field_name} exceeds maximum length",
                            current_value=len(value)
                        ))
                    
                    if field_def.min_length and len(value) < field_def.min_length:
                        result.issues.append(MetadataValidationIssue(
                            field_name=field_name,
                            issue_type="value_too_short",
                            severity=ValidationSeverity.WARNING,
                            message=f"Field {field_name} is too short",
                            current_value=len(value)
                        ))
    
    async def _validate_field_values(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate ID3 field values."""
        # Year validation
        if "TYER" in metadata:
            year = metadata["TYER"]
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if year_int < 1900 or year_int > current_year + 1:
                    result.issues.append(MetadataValidationIssue(
                        field_name="TYER",
                        issue_type="invalid_year",
                        severity=ValidationSeverity.WARNING,
                        message="Year appears to be invalid",
                        current_value=year
                    ))
            except (ValueError, TypeError):
                result.issues.append(MetadataValidationIssue(
                    field_name="TYER",
                    issue_type="invalid_format",
                    severity=ValidationSeverity.ERROR,
                    message="Year must be a valid number",
                    current_value=year
                ))
        
        # Track number validation
        if "TRCK" in metadata:
            track = metadata["TRCK"]
            if not re.match(r'^\d+(/\d+)?$', str(track)):
                result.issues.append(MetadataValidationIssue(
                    field_name="TRCK",
                    issue_type="invalid_format",
                    severity=ValidationSeverity.WARNING,
                    message="Track number format should be 'number' or 'number/total'",
                    current_value=track
                ))
    
    async def _validate_version_compatibility(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate ID3 version compatibility."""
        version = metadata.get("version", "2.4")
        
        if version not in self.supported_versions:
            result.issues.append(MetadataValidationIssue(
                field_name="version",
                issue_type="unsupported_version",
                severity=ValidationSeverity.WARNING,
                message=f"ID3 version {version} may have compatibility issues",
                current_value=version,
                suggestion="Consider using ID3v2.3 or ID3v2.4"
            ))
    
    async def _calculate_completeness_score(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """Calculate metadata completeness score."""
        try:
            total_fields = len(self.id3_fields)
            present_fields = len([field for field in self.id3_fields.keys() if field in metadata and metadata[field]])
            
            return (present_fields / total_fields) * 100 if total_fields > 0 else 0
            
        except Exception:
            return 0.0
    
    async def _calculate_quality_score(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """
Calculate metadata quality score."""
        try:
            score = 100.0
            
            # Deduct for issues
            for issue in result.issues:
                if issue.severity == ValidationSeverity.CRITICAL:
                    score -= 25
                elif issue.severity == ValidationSeverity.ERROR:
                    score -= 15
                elif issue.severity == ValidationSeverity.WARNING:
                    score -= 5
            
            return max(0.0, score)
            
        except Exception:
            return 0.0
    
    async def _calculate_compliance_score(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """
Calculate standards compliance score."""
        try:
            compliance_score = 100.0
            
            # Check required fields compliance
            required_fields = ["TIT2", "TPE1"]
            missing_required = [field for field in required_fields if field not in metadata]
            compliance_score -= len(missing_required) * 20
            
            # Check format compliance
            format_issues = [issue for issue in result.issues if issue.issue_type in ["invalid_type", "invalid_format"]]
            compliance_score -= len(format_issues) * 10
            
            return max(0.0, compliance_score)
            
        except Exception:
            return 0.0
    
    async def _generate_id3_suggestions(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> List[str]:
        """Generate ID3 improvement suggestions."""
        suggestions = []
        
        try:
            # Missing field suggestions
            if "TALB" not in metadata:
                suggestions.append("Add album name for better organization")
            
            if "TCON" not in metadata:
                suggestions.append("Add genre information for categorization")
            
            if "TYER" not in metadata:
                suggestions.append("Add release year for chronological organization")
            
            # Quality improvement suggestions
            if "TIT2" in metadata and len(metadata["TIT2"]) > 100:
                suggestions.append("Consider shorter, more concise title")
            
            if not any(field.startswith("TXXX") for field in metadata.keys()):
                suggestions.append("Consider adding custom fields for additional metadata")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {str(e)}")
            return []
    
    async def _identify_enrichment_opportunities(self, metadata: Dict[str, Any]) -> List[str]:
        """Identify metadata enrichment opportunities."""
        opportunities = []
        
        try:
            # Check for missing descriptive fields
            if not metadata.get("COMM"):  # Comments
                opportunities.append("Add comments or description")
            
            if not metadata.get("TPOS"):  # Disc number
                opportunities.append("Add disc number if part of multi-disc release")
            
            if not metadata.get("TPE2"):  # Album artist
                opportunities.append("Add album artist if different from track artist")
            
            # Check for technical metadata
            if not metadata.get("TLEN"):  # Length
                opportunities.append("Add track length information")
            
            return opportunities
            
        except Exception:
            return []
    
    async def _normalize_id3_fields(self, metadata: Dict[str, Any]):
        """Normalize ID3 field values."""
        try:
            # Normalize text fields
            text_fields = ["TIT2", "TPE1", "TALB", "TPE2"]
            for field in text_fields:
                if field in metadata and isinstance(metadata[field], str):
                    # Trim whitespace
                    metadata[field] = metadata[field].strip()
                    
                    # Capitalize properly
                    if field in ["TIT2", "TALB"]:  # Title and Album
                        metadata[field] = metadata[field].title()
            
            # Normalize year
            if "TYER" in metadata:
                year = str(metadata["TYER"]).strip()
                if len(year) == 4 and year.isdigit():
                    metadata["TYER"] = year
                elif len(year) > 4:
                    # Extract year from longer string
                    year_match = re.search(r'\b(19|20)\d{2}\b', year)
                    if year_match:
                        metadata["TYER"] = year_match.group()
            
        except Exception as e:
            logger.error(f"Field normalization failed: {str(e)}")
    
    async def _add_technical_metadata(self, metadata: Dict[str, Any]):
        """Add technical metadata if missing."""
        try:
            # Add encoding settings if missing
            if not metadata.get("TSSE"):  # Software/Hardware and settings used for encoding
                metadata["TSSE"] = "IA Influencer Agent Platform"
            
            # Add timestamp
            if not metadata.get("TDRC"):  # Recording time
                metadata["TDRC"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Technical metadata addition failed: {str(e)}")
    
    def _init_id3_fields(self) -> Dict[str, MetadataField]:
        """Initialize ID3 field definitions."""
        return {
            "TIT2": MetadataField(
                field_name="TIT2",
                field_type=str,
                required=True,
                description="Title/songname/content description",
                max_length=100
            ),
            "TPE1": MetadataField(
                field_name="TPE1",
                field_type=str,
                required=True,
                description="Lead performer(s)/Soloist(s)",
                max_length=100
            ),
            "TALB": MetadataField(
                field_name="TALB",
                field_type=str,
                description="Album/Movie/Show title",
                max_length=100
            ),
            "TYER": MetadataField(
                field_name="TYER",
                field_type=str,
                description="Year",
                pattern=r"^\d{4}$"
            ),
            "TCON": MetadataField(
                field_name="TCON",
                field_type=str,
                description="Content type (Genre)",
                max_length=50
            ),
            "TRCK": MetadataField(
                field_name="TRCK",
                field_type=str,
                description="Track number/Position in set",
                pattern=r"^\d+(/\d+)?$"
            ),
            "TPE2": MetadataField(
                field_name="TPE2",
                field_type=str,
                description="Band/orchestra/accompaniment",
                max_length=100
            ),
            "TPOS": MetadataField(
                field_name="TPOS",
                field_type=str,
                description="Part of a set",
                pattern=r"^\d+(/\d+)?$"
            ),
            "TLEN": MetadataField(
                field_name="TLEN",
                field_type=str,
                description="Length in milliseconds",
                pattern=r"^\d+$"
            ),
            "COMM": MetadataField(
                field_name="COMM",
                field_type=str,
                description="Comments",
                max_length=500
            )
        }


class EXIFValidator:
    """
    EXIF metadata validator for image files.
    
    Validates and enriches EXIF data in image content with comprehensive
    tag validation, technical analysis, and privacy protection.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize EXIF validator.
        
        Args:
            config: Validator configuration
        """
        self.config = config or {}
        
        # EXIF field definitions
        self.exif_fields = self._init_exif_fields()
        
        # Privacy-sensitive fields
        self.privacy_fields = ["GPS", "DateTime", "Software", "Make", "Model"]
        
        logger.info("EXIFValidator initialized")
    
    async def validate_exif_metadata(
        self,
        metadata: Dict[str, Any],
        check_privacy: bool = True
    ) -> MetadataValidationResult:
        """
        Validate EXIF metadata.
        
        Args:
            metadata: EXIF metadata to validate
            check_privacy: Enable privacy checks
            
        Returns:
            Validation result
        """
        start_time = time.time()
        
        try:
            result = MetadataValidationResult(
                is_valid=True,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0
            )
            
            # Validate technical fields
            await self._validate_technical_exif(metadata, result)
            
            # Validate format compliance
            await self._validate_exif_format(metadata, result)
            
            # Privacy validation
            if check_privacy:
                await self._validate_privacy_fields(metadata, result)
            
            # Calculate scores
            result.completeness_score = await self._calculate_exif_completeness(metadata)
            result.quality_score = await self._calculate_exif_quality(metadata, result)
            result.compliance_score = await self._calculate_exif_compliance(metadata, result)
            
            # Generate suggestions
            result.suggestions = await self._generate_exif_suggestions(metadata, result)
            
            result.validation_duration = time.time() - start_time
            result.is_valid = len([issue for issue in result.issues if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]) == 0
            
            return result
            
        except Exception as e:
            logger.error(f"EXIF validation failed: {str(e)}")
            return MetadataValidationResult(
                is_valid=False,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0,
                validation_duration=time.time() - start_time
            )
    
    async def sanitize_exif_for_privacy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove privacy-sensitive EXIF data.
        
        Args:
            metadata: Original EXIF metadata
            
        Returns:
            Sanitized metadata
        """
        sanitized = metadata.copy()
        
        try:
            # Remove GPS data
            gps_fields = [key for key in sanitized.keys() if key.startswith("GPS")]
            for field in gps_fields:
                del sanitized[field]
            
            # Remove timestamp information
            timestamp_fields = ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]
            for field in timestamp_fields:
                if field in sanitized:
                    del sanitized[field]
            
            # Remove device information
            device_fields = ["Make", "Model", "Software", "Artist", "Copyright"]
            for field in device_fields:
                if field in sanitized:
                    del sanitized[field]
            
            # Remove potentially identifying information
            if "UserComment" in sanitized:
                del sanitized["UserComment"]
            
            if "ImageDescription" in sanitized:
                del sanitized["ImageDescription"]
            
            return sanitized
            
        except Exception as e:
            logger.error(f"EXIF sanitization failed: {str(e)}")
            return metadata
    
    async def _validate_technical_exif(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate technical EXIF fields."""
        # Image dimensions validation
        if "ImageWidth" in metadata and "ImageHeight" in metadata:
            width = metadata["ImageWidth"]
            height = metadata["ImageHeight"]
            
            if width <= 0 or height <= 0:
                result.issues.append(MetadataValidationIssue(
                    field_name="ImageDimensions",
                    issue_type="invalid_dimensions",
                    severity=ValidationSeverity.ERROR,
                    message="Invalid image dimensions",
                    current_value=f"{width}x{height}"
                ))
            
            # Check for reasonable dimensions
            if width > 50000 or height > 50000:
                result.issues.append(MetadataValidationIssue(
                    field_name="ImageDimensions",
                    issue_type="unrealistic_dimensions",
                    severity=ValidationSeverity.WARNING,
                    message="Unusually large image dimensions",
                    current_value=f"{width}x{height}"
                ))
        
        # Color space validation
        if "ColorSpace" in metadata:
            color_space = metadata["ColorSpace"]
            valid_color_spaces = [1, 65535]  # sRGB, Uncalibrated
            if color_space not in valid_color_spaces:
                result.issues.append(MetadataValidationIssue(
                    field_name="ColorSpace",
                    issue_type="invalid_color_space",
                    severity=ValidationSeverity.WARNING,
                    message="Unusual color space value",
                    current_value=color_space
                ))
    
    async def _validate_exif_format(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate EXIF format compliance."""
        for field_name, field_def in self.exif_fields.items():
            if field_name in metadata:
                value = metadata[field_name]
                
                # Type validation
                if not isinstance(value, field_def.field_type):
                    result.issues.append(MetadataValidationIssue(
                        field_name=field_name,
                        issue_type="invalid_type",
                        severity=ValidationSeverity.WARNING,
                        message=f"Field {field_name} has unexpected type",
                        current_value=type(value).__name__
                    ))
    
    async def _validate_privacy_fields(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate privacy-sensitive fields."""
        for field in self.privacy_fields:
            matching_fields = [key for key in metadata.keys() if key.startswith(field)]
            
            if matching_fields:
                result.issues.append(MetadataValidationIssue(
                    field_name=field,
                    issue_type="privacy_concern",
                    severity=ValidationSeverity.WARNING,
                    message=f"Privacy-sensitive field {field} present",
                    suggestion="Consider removing for privacy protection"
                ))
    
    async def _calculate_exif_completeness(self, metadata: Dict[str, Any]) -> float:
        """Calculate EXIF completeness score."""
        try:
            essential_fields = ["ImageWidth", "ImageHeight", "Orientation", "XResolution", "YResolution"]
            present_essential = len([field for field in essential_fields if field in metadata])
            
            return (present_essential / len(essential_fields)) * 100
            
        except Exception:
            return 0.0
    
    async def _calculate_exif_quality(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """Calculate EXIF quality score."""
        try:
            score = 100.0
            
            # Deduct for validation issues
            for issue in result.issues:
                if issue.severity == ValidationSeverity.ERROR:
                    score -= 15
                elif issue.severity == ValidationSeverity.WARNING:
                    score -= 5
            
            return max(0.0, score)
            
        except Exception:
            return 0.0
    
    async def _calculate_exif_compliance(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """
Calculate EXIF compliance score."""
        try:
            compliance_score = 100.0
            
            # Check for required fields
            required_fields = ["ImageWidth", "ImageHeight"]
            missing_required = [field for field in required_fields if field not in metadata]
            compliance_score -= len(missing_required) * 25
            
            return max(0.0, compliance_score)
            
        except Exception:
            return 0.0
    
    async def _generate_exif_suggestions(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> List[str]:
        """Generate EXIF improvement suggestions."""
        suggestions = []
        
        try:
            # Resolution suggestions
            if "XResolution" not in metadata or "YResolution" not in metadata:
                suggestions.append("Add resolution information for print quality")
            
            # Orientation suggestions
            if "Orientation" not in metadata:
                suggestions.append("Add orientation information for proper display")
            
            # Privacy suggestions
            privacy_fields_present = [key for key in metadata.keys() 
                                     if any(key.startswith(pf) for pf in self.privacy_fields)]
            if privacy_fields_present:
                suggestions.append("Consider removing privacy-sensitive metadata before sharing")
            
            return suggestions
            
        except Exception:
            return []
    
    def _init_exif_fields(self) -> Dict[str, MetadataField]:
        """Initialize EXIF field definitions."""
        return {
            "ImageWidth": MetadataField(
                field_name="ImageWidth",
                field_type=int,
                required=True,
                description="Image width in pixels"
            ),
            "ImageHeight": MetadataField(
                field_name="ImageHeight",
                field_type=int,
                required=True,
                description="Image height in pixels"
            ),
            "Orientation": MetadataField(
                field_name="Orientation",
                field_type=int,
                description="Image orientation",
                allowed_values=[1, 2, 3, 4, 5, 6, 7, 8]
            ),
            "XResolution": MetadataField(
                field_name="XResolution",
                field_type=float,
                description="Horizontal resolution"
            ),
            "YResolution": MetadataField(
                field_name="YResolution",
                field_type=float,
                description="Vertical resolution"
            ),
            "ColorSpace": MetadataField(
                field_name="ColorSpace",
                field_type=int,
                description="Color space information",
                allowed_values=[1, 65535]
            )
        }


class XMPValidator:
    """
    XMP metadata validator for multimedia files.
    
    Validates and enriches XMP (Extensible Metadata Platform) data
    with comprehensive schema validation and namespace support.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize XMP validator.
        
        Args:
            config: Validator configuration
        """
        self.config = config or {}
        
        # XMP namespaces
        self.xmp_namespaces = self._init_xmp_namespaces()
        
        # XMP field definitions
        self.xmp_fields = self._init_xmp_fields()
        
        logger.info("XMPValidator initialized")
    
    async def validate_xmp_metadata(
        self,
        metadata: Dict[str, Any],
        validate_namespaces: bool = True
    ) -> MetadataValidationResult:
        """
        Validate XMP metadata.
        
        Args:
            metadata: XMP metadata to validate
            validate_namespaces: Enable namespace validation
            
        Returns:
            Validation result
        """
        start_time = time.time()
        
        try:
            result = MetadataValidationResult(
                is_valid=True,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0
            )
            
            # Validate namespaces
            if validate_namespaces:
                await self._validate_xmp_namespaces(metadata, result)
            
            # Validate field formats
            await self._validate_xmp_fields(metadata, result)
            
            # Validate rights and licensing
            await self._validate_rights_metadata(metadata, result)
            
            # Calculate scores
            result.completeness_score = await self._calculate_xmp_completeness(metadata)
            result.quality_score = await self._calculate_xmp_quality(metadata, result)
            result.compliance_score = await self._calculate_xmp_compliance(metadata, result)
            
            # Generate suggestions
            result.suggestions = await self._generate_xmp_suggestions(metadata, result)
            
            result.validation_duration = time.time() - start_time
            result.is_valid = len([issue for issue in result.issues if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]) == 0
            
            return result
            
        except Exception as e:
            logger.error(f"XMP validation failed: {str(e)}")
            return MetadataValidationResult(
                is_valid=False,
                completeness_score=0.0,
                quality_score=0.0,
                compliance_score=0.0,
                validation_duration=time.time() - start_time
            )
    
    async def _validate_xmp_namespaces(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate XMP namespaces."""
        for field_name in metadata.keys():
            if ":" in field_name:
                namespace = field_name.split(":")[0]
                if namespace not in self.xmp_namespaces:
                    result.issues.append(MetadataValidationIssue(
                        field_name=field_name,
                        issue_type="unknown_namespace",
                        severity=ValidationSeverity.WARNING,
                        message=f"Unknown XMP namespace: {namespace}",
                        suggestion="Use standard XMP namespaces"
                    ))
    
    async def _validate_xmp_fields(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate XMP field formats."""
        for field_name, value in metadata.items():
            if field_name in self.xmp_fields:
                field_def = self.xmp_fields[field_name]
                
                # Type validation
                if not isinstance(value, field_def.field_type):
                    result.issues.append(MetadataValidationIssue(
                        field_name=field_name,
                        issue_type="invalid_type",
                        severity=ValidationSeverity.WARNING,
                        message=f"Field {field_name} should be {field_def.field_type.__name__}",
                        current_value=type(value).__name__
                    ))
    
    async def _validate_rights_metadata(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate rights and licensing metadata."""
        rights_fields = ["dc:rights", "xmpRights:Marked", "xmpRights:WebStatement"]
        
        # Check for rights information
        has_rights_info = any(field in metadata for field in rights_fields)
        
        if not has_rights_info:
            result.issues.append(MetadataValidationIssue(
                field_name="rights",
                issue_type="missing_rights_info",
                severity=ValidationSeverity.WARNING,
                message="No rights or licensing information found",
                suggestion="Add copyright and licensing metadata"
            ))
    
    async def _calculate_xmp_completeness(self, metadata: Dict[str, Any]) -> float:
        """Calculate XMP completeness score."""
        try:
            essential_fields = ["dc:title", "dc:creator", "dc:description", "dc:rights"]
            present_essential = len([field for field in essential_fields if field in metadata])
            
            return (present_essential / len(essential_fields)) * 100
            
        except Exception:
            return 0.0
    
    async def _calculate_xmp_quality(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """Calculate XMP quality score."""
        try:
            score = 100.0
            
            # Deduct for validation issues
            for issue in result.issues:
                if issue.severity == ValidationSeverity.ERROR:
                    score -= 10
                elif issue.severity == ValidationSeverity.WARNING:
                    score -= 3
            
            return max(0.0, score)
            
        except Exception:
            return 0.0
    
    async def _calculate_xmp_compliance(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> float:
        """
Calculate XMP compliance score."""
        try:
            compliance_score = 100.0
            
            # Check namespace compliance
            namespace_issues = [issue for issue in result.issues if issue.issue_type == "unknown_namespace"]
            compliance_score -= len(namespace_issues) * 10
            
            return max(0.0, compliance_score)
            
        except Exception:
            return 0.0
    
    async def _generate_xmp_suggestions(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ) -> List[str]:
        """Generate XMP improvement suggestions."""
        suggestions = []
        
        try:
            # Essential field suggestions
            if "dc:title" not in metadata:
                suggestions.append("Add title information (dc:title)")
            
            if "dc:creator" not in metadata:
                suggestions.append("Add creator information (dc:creator)")
            
            if "dc:rights" not in metadata:
                suggestions.append("Add rights and licensing information")
            
            # Technical suggestions
            if "xmp:CreatorTool" not in metadata:
                suggestions.append("Add creator tool information")
            
            return suggestions
            
        except Exception:
            return []
    
    def _init_xmp_namespaces(self) -> List[str]:
        """Initialize standard XMP namespaces."""
        return [
            "dc",       # Dublin Core
            "xmp",      # XMP Basic
            "xmpRights", # XMP Rights Management
            "xmpMM",    # XMP Media Management
            "xmpBJ",    # XMP Basic Job Ticket
            "xmpTPg",   # XMP Paged-Text
            "pdf",      # PDF
            "photoshop", # Photoshop
            "tiff",     # TIFF
            "exif",     # EXIF
            "aux",      # Additional EXIF Properties
            "crs"       # Camera Raw Settings
        ]
    
    def _init_xmp_fields(self) -> Dict[str, MetadataField]:
        """Initialize XMP field definitions."""
        return {
            "dc:title": MetadataField(
                field_name="dc:title",
                field_type=str,
                description="Title of the resource"
            ),
            "dc:creator": MetadataField(
                field_name="dc:creator",
                field_type=str,
                description="Creator of the resource"
            ),
            "dc:description": MetadataField(
                field_name="dc:description",
                field_type=str,
                description="Description of the resource"
            ),
            "dc:rights": MetadataField(
                field_name="dc:rights",
                field_type=str,
                description="Rights statement"
            ),
            "xmp:CreatorTool": MetadataField(
                field_name="xmp:CreatorTool",
                field_type=str,
                description="Tool used to create the resource"
            ),
            "xmp:CreateDate": MetadataField(
                field_name="xmp:CreateDate",
                field_type=str,
                description="Creation date"
            )
        }
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetadataField:
    """Individual metadata field definition."""
    name: str
    field_type: str
    is_required: bool = False
    is_repeatable: bool = False
    
    # Validation rules
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    
    # Metadata properties
    metadata_type: MetadataType = MetadataType.DESCRIPTIVE
    standard: MetadataStandard = MetadataStandard.CUSTOM
    
    # Description
    description: Optional[str] = None
    example: Optional[str] = None


@dataclass
class MetadataIssue:
    """
Metadata validation issue."""
    field_name: str
    issue_type: str
    severity: ValidationSeverity
    message: str
    
    # Issue details
    actual_value: Any = None
    expected_value: Any = None
    suggestion: Optional[str] = None
    
    # Enrichment data
    can_auto_fix: bool = False
    enrichment_source: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataValidationResult:
    """
Comprehensive metadata validation result."""
    is_valid: bool
    completeness_score: float
    quality_score: float
    
    # Validation details
    validation_time: float
    validator_version: str = "1.0.0"
    total_fields: int = 0
    validated_fields: int = 0
    
    # Issues found
    issues: List[MetadataIssue] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    invalid_fields: List[str] = field(default_factory=list)
    
    # Metadata analysis
    detected_standards: List[MetadataStandard] = field(default_factory=list)
    metadata_types: List[MetadataType] = field(default_factory=list)
    
    # Enrichment results
    enriched_fields: List[str] = field(default_factory=list)
    enrichment_sources: Dict[str, str] = field(default_factory=dict)
    
    # Quality metrics
    standardization_score: float = 0.0
    consistency_score: float = 0.0
    richness_score: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Original and validated metadata
    original_metadata: Dict[str, Any] = field(default_factory=dict)
    validated_metadata: Dict[str, Any] = field(default_factory=dict)
    enriched_metadata: Dict[str, Any] = field(default_factory=dict)


class MetadataValidator:
    """
    Comprehensive metadata validator for the IA Influencer Agent Platform.
    
    Provides metadata validation, enrichment, and standardization
    for creator content with support for multiple metadata standards.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enable_enrichment: bool = True,
        enable_auto_fix: bool = False
    ):
        """
        Initialize metadata validator.
        
        Args:
            config: Validator configuration
            enable_enrichment: Enable metadata enrichment
            enable_auto_fix: Enable automatic fixing of issues
        """
        self.config = config or {}
        self.enable_enrichment = enable_enrichment
        self.enable_auto_fix = enable_auto_fix
        
        # Metadata field definitions
        self.field_definitions = self._init_field_definitions()
        
        # Validation rules
        self.validation_rules = self._init_validation_rules()
        
        # Enrichment sources
        self.enrichment_sources = self._init_enrichment_sources()
        
        # Standard mappings
        self.standard_mappings = self._init_standard_mappings()
        
        # Pattern validators
        self.pattern_validators = self._init_pattern_validators()
        
        logger.info("MetadataValidator initialized with enrichment=%s, auto_fix=%s", 
                   enable_enrichment, enable_auto_fix)
    
    async def validate_metadata(
        self,
        metadata: Dict[str, Any],
        content_type: Optional[str] = None,
        standard: MetadataStandard = MetadataStandard.CUSTOM,
        enable_enrichment: Optional[bool] = None
    ) -> MetadataValidationResult:
        """
        Validate and optionally enrich metadata.
        
        Args:
            metadata: Metadata to validate
            content_type: Type of content
            standard: Metadata standard to validate against
            enable_enrichment: Override enrichment setting
            
        Returns:
            Metadata validation result
        """
        start_time = time.time()
        
        try:
            result = MetadataValidationResult(
                is_valid=True,
                completeness_score=0.0,
                quality_score=0.0,
                validation_time=0.0,
                original_metadata=metadata.copy(),
                validated_metadata=metadata.copy()
            )
            
            # Get applicable field definitions
            applicable_fields = self._get_applicable_fields(content_type, standard)
            result.total_fields = len(applicable_fields)
            
            # Validate each field
            for field_def in applicable_fields:
                await self._validate_field(metadata, field_def, result)
            
            # Check for required fields
            await self._check_required_fields(metadata, applicable_fields, result)
            
            # Validate cross-field consistency
            await self._validate_field_consistency(metadata, result)
            
            # Detect metadata standards
            result.detected_standards = await self._detect_metadata_standards(metadata)
            
            # Metadata enrichment
            if (enable_enrichment if enable_enrichment is not None else self.enable_enrichment):
                await self._enrich_metadata(metadata, content_type, result)
            
            # Calculate quality metrics
            result.completeness_score = await self._calculate_completeness_score(result)
            result.quality_score = await self._calculate_quality_score(result)
            result.standardization_score = await self._calculate_standardization_score(result)
            result.consistency_score = await self._calculate_consistency_score(result)
            result.richness_score = await self._calculate_richness_score(result)
            
            # Generate recommendations
            await self._generate_metadata_recommendations(result)
            
            # Auto-fix if enabled
            if self.enable_auto_fix:
                await self._auto_fix_issues(result)
            
            # Finalize result
            result.validation_time = time.time() - start_time
            result.is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                                    for issue in result.issues)
            result.validated_fields = result.total_fields - len(result.invalid_fields)
            
            logger.info(f"Metadata validation completed: valid={result.is_valid}, quality={result.quality_score:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"Metadata validation failed: {str(e)}")
            return self._create_error_result(str(e))
    
    async def extract_metadata(
        self,
        file_path: Optional[str] = None,
        file_data: Optional[bytes] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from file.
        
        Args:
            file_path: Path to file
            file_data: File data bytes
            content_type: Content type hint
            
        Returns:
            Extracted metadata
        """
        try:
            metadata = {}
            
            # Prepare file data
            if file_path:
                file_path = Path(file_path)
                if not file_path.exists():
                    return {"error": "File not found"}
                
                file_data = file_path.read_bytes()
                filename = file_path.name
            else:
                filename = "unknown"
            
            if not file_data:
                return {"error": "No file data provided"}
            
            # Detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type(filename, file_data)
            
            # Extract based on content type
            if content_type in ["image", "photo"]:
                metadata.update(await self._extract_image_metadata(file_data))
            elif content_type in ["audio", "music"]:
                metadata.update(await self._extract_audio_metadata(file_data))
            elif content_type in ["video", "movie"]:
                metadata.update(await self._extract_video_metadata(file_data))
            elif content_type in ["document", "text"]:
                metadata.update(await self._extract_document_metadata(file_data))
            
            # Add technical metadata
            metadata.update(await self._extract_technical_metadata(file_data, filename))
            
            # Add administrative metadata
            metadata.update(await self._extract_administrative_metadata(file_path if file_path else None))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {"error": str(e)}
    
    async def enrich_metadata(
        self,
        metadata: Dict[str, Any],
        content_type: Optional[str] = None,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enrich metadata with additional information.
        
        Args:
            metadata: Original metadata
            content_type: Content type
            sources: Enrichment sources to use
            
        Returns:
            Enriched metadata
        """
        try:
            enriched = metadata.copy()
            enrichment_log = []
            
            # Default sources
            if sources is None:
                sources = list(self.enrichment_sources.keys())
            
            # Enrich with each source
            for source in sources:
                if source in self.enrichment_sources:
                    source_enrichment = await self._enrich_with_source(
                        enriched, content_type, source
                    )
                    
                    for key, value in source_enrichment.items():
                        if key not in enriched or not enriched[key]:
                            enriched[key] = value
                            enrichment_log.append(f"{key} enriched from {source}")
            
            # Add enrichment log
            enriched["_enrichment_log"] = enrichment_log
            
            return enriched
            
        except Exception as e:
            logger.error(f"Metadata enrichment failed: {str(e)}")
            return metadata
    
    async def standardize_metadata(
        self,
        metadata: Dict[str, Any],
        target_standard: MetadataStandard,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Standardize metadata to specific standard.
        
        Args:
            metadata: Original metadata
            target_standard: Target metadata standard
            content_type: Content type
            
        Returns:
            Standardized metadata
        """
        try:
            if target_standard not in self.standard_mappings:
                return metadata
            
            mapping = self.standard_mappings[target_standard]
            standardized = {}
            
            # Map fields to standard
            for original_key, value in metadata.items():
                if original_key in mapping:
                    standard_key = mapping[original_key]
                    standardized[standard_key] = value
                else:
                    # Keep unmapped fields with prefix
                    standardized[f"custom_{original_key}"] = value
            
            # Add standard-specific required fields
            await self._add_standard_required_fields(standardized, target_standard, content_type)
            
            return standardized
            
        except Exception as e:
            logger.error(f"Metadata standardization failed: {str(e)}")
            return metadata
    
    async def validate_against_schema(
        self,
        metadata: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> MetadataValidationResult:
        """
        Validate metadata against custom schema.
        
        Args:
            metadata: Metadata to validate
            schema: Validation schema
            
        Returns:
            Validation result
        """
        try:
            result = MetadataValidationResult(
                is_valid=True,
                completeness_score=0.0,
                quality_score=0.0,
                validation_time=0.0,
                original_metadata=metadata.copy()
            )
            
            # Validate against schema
            for field_name, field_schema in schema.items():
                await self._validate_field_against_schema(
                    metadata, field_name, field_schema, result
                )
            
            # Calculate scores
            result.completeness_score = await self._calculate_completeness_score(result)
            result.quality_score = await self._calculate_quality_score(result)
            
            # Finalize
            result.is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                                    for issue in result.issues)
            
            return result
            
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return self._create_error_result(str(e))
    
    async def _validate_field(
        self,
        metadata: Dict[str, Any],
        field_def: MetadataField,
        result: MetadataValidationResult
    ):
        """Validate individual metadata field."""
        try:
            field_name = field_def.name
            field_value = metadata.get(field_name)
            
            # Check if field exists
            if field_value is None:
                if field_def.is_required:
                    result.missing_required.append(field_name)
                    result.issues.append(MetadataIssue(
                        field_name=field_name,
                        issue_type="missing_required",
                        severity=ValidationSeverity.ERROR,
                        message=f"Required field '{field_name}' is missing"
                    ))
                return
            
            # Type validation
            if not await self._validate_field_type(field_value, field_def.field_type):
                result.invalid_fields.append(field_name)
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="invalid_type",
                    severity=ValidationSeverity.ERROR,
                    message=f"Field '{field_name}' has invalid type",
                    actual_value=type(field_value).__name__,
                    expected_value=field_def.field_type
                ))
                return
            
            # Length validation
            if isinstance(field_value, str):
                await self._validate_field_length(field_name, field_value, field_def, result)
            
            # Pattern validation
            if field_def.pattern and isinstance(field_value, str):
                await self._validate_field_pattern(field_name, field_value, field_def, result)
            
            # Allowed values validation
            if field_def.allowed_values:
                await self._validate_allowed_values(field_name, field_value, field_def, result)
            
            # Repeatability validation
            if not field_def.is_repeatable and isinstance(field_value, list):
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="not_repeatable",
                    severity=ValidationSeverity.WARNING,
                    message=f"Field '{field_name}' should not be repeatable",
                    suggestion="Use single value instead of list"
                ))
            
        except Exception as e:
            logger.error(f"Field validation failed for {field_def.name}: {str(e)}")
    
    async def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type."""
        try:
            type_map = {
                "string": str,
                "integer": int,
                "float": float,
                "boolean": bool,
                "date": (str, datetime),
                "url": str,
                "email": str,
                "array": list,
                "object": dict
            }
            
            if expected_type not in type_map:
                return True  # Unknown type, assume valid
            
            expected_types = type_map[expected_type]
            if not isinstance(expected_types, tuple):
                expected_types = (expected_types,)
            
            return isinstance(value, expected_types)
            
        except Exception:
            return False
    
    async def _validate_field_length(
        self,
        field_name: str,
        value: str,
        field_def: MetadataField,
        result: MetadataValidationResult
    ):
        """Validate field length."""
        try:
            length = len(value)
            
            if field_def.min_length and length < field_def.min_length:
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="too_short",
                    severity=ValidationSeverity.WARNING,
                    message=f"Field '{field_name}' is too short",
                    actual_value=length,
                    expected_value=f"minimum {field_def.min_length}"
                ))
            
            if field_def.max_length and length > field_def.max_length:
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="too_long",
                    severity=ValidationSeverity.WARNING,
                    message=f"Field '{field_name}' is too long",
                    actual_value=length,
                    expected_value=f"maximum {field_def.max_length}",
                    can_auto_fix=True,
                    suggestion=f"Truncate to {field_def.max_length} characters"
                ))
            
        except Exception as e:
            logger.error(f"Length validation failed: {str(e)}")
    
    async def _validate_field_pattern(
        self,
        field_name: str,
        value: str,
        field_def: MetadataField,
        result: MetadataValidationResult
    ):
        """Validate field pattern."""
        try:
            if not re.match(field_def.pattern, value):
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="invalid_pattern",
                    severity=ValidationSeverity.ERROR,
                    message=f"Field '{field_name}' doesn't match required pattern",
                    actual_value=value,
                    expected_value=field_def.pattern,
                    suggestion=f"Format should match: {field_def.pattern}"
                ))
            
        except Exception as e:
            logger.error(f"Pattern validation failed: {str(e)}")
    
    async def _validate_allowed_values(
        self,
        field_name: str,
        value: Any,
        field_def: MetadataField,
        result: MetadataValidationResult
    ):
        """Validate allowed values."""
        try:
            if value not in field_def.allowed_values:
                result.issues.append(MetadataIssue(
                    field_name=field_name,
                    issue_type="invalid_value",
                    severity=ValidationSeverity.ERROR,
                    message=f"Field '{field_name}' has invalid value",
                    actual_value=value,
                    expected_value=field_def.allowed_values,
                    suggestion=f"Use one of: {', '.join(map(str, field_def.allowed_values))}"
                ))
            
        except Exception as e:
            logger.error(f"Allowed values validation failed: {str(e)}")
    
    async def _check_required_fields(
        self,
        metadata: Dict[str, Any],
        field_definitions: List[MetadataField],
        result: MetadataValidationResult
    ):
        """Check for missing required fields."""
        try:
            required_fields = [field.name for field in field_definitions if field.is_required]
            
            for field_name in required_fields:
                if field_name not in metadata or not metadata[field_name]:
                    if field_name not in result.missing_required:
                        result.missing_required.append(field_name)
                        result.issues.append(MetadataIssue(
                            field_name=field_name,
                            issue_type="missing_required",
                            severity=ValidationSeverity.ERROR,
                            message=f"Required field '{field_name}' is missing",
                            can_auto_fix=True,
                            enrichment_source="auto_generation"
                        ))
            
        except Exception as e:
            logger.error(f"Required fields check failed: {str(e)}")
    
    async def _validate_field_consistency(
        self,
        metadata: Dict[str, Any],
        result: MetadataValidationResult
    ):
        """Validate cross-field consistency."""
        try:
            # Date consistency checks
            created_date = metadata.get("created_date")
            modified_date = metadata.get("modified_date")
            
            if created_date and modified_date:
                try:
                    created_dt = self._parse_date(created_date)
                    modified_dt = self._parse_date(modified_date)
                    
                    if created_dt and modified_dt and created_dt > modified_dt:
                        result.issues.append(MetadataIssue(
                            field_name="date_consistency",
                            issue_type="inconsistent_dates",
                            severity=ValidationSeverity.WARNING,
                            message="Created date is after modified date",
                            suggestion="Check date values for accuracy"
                        ))
                except Exception:
                    pass
            
            # Size consistency checks
            file_size = metadata.get("file_size")
            content_length = metadata.get("content_length")
            
            if file_size and content_length and abs(file_size - content_length) > 1000:
                result.issues.append(MetadataIssue(
                    field_name="size_consistency",
                    issue_type="inconsistent_sizes",
                    severity=ValidationSeverity.WARNING,
                    message="File size and content length don't match",
                    actual_value={"file_size": file_size, "content_length": content_length}
                ))
            
        except Exception as e:
            logger.error(f"Field consistency validation failed: {str(e)}")
    
    async def _detect_metadata_standards(self, metadata: Dict[str, Any]) -> List[MetadataStandard]:
        """Detect metadata standards used."""
        try:
            detected = []
            
            # Dublin Core detection
            dc_fields = {"title", "creator", "subject", "description", "publisher", "date", "type", "format"}
            if any(field in metadata for field in dc_fields):
                detected.append(MetadataStandard.DUBLIN_CORE)
            
            # EXIF detection
            exif_fields = {"camera_make", "camera_model", "exposure_time", "f_number", "iso_speed"}
            if any(field in metadata for field in exif_fields):
                detected.append(MetadataStandard.EXIF)
            
            # ID3 detection
            id3_fields = {"artist", "album", "track_number", "genre", "year"}
            if any(field in metadata for field in id3_fields):
                detected.append(MetadataStandard.ID3)
            
            return detected
            
        except Exception as e:
            logger.error(f"Standards detection failed: {str(e)}")
            return []
    
    async def _enrich_metadata(
        self,
        metadata: Dict[str, Any],
        content_type: Optional[str],
        result: MetadataValidationResult
    ):
        """Enrich metadata with additional information."""
        try:
            enriched = {}
            
            # Generate missing required fields
            for field_name in result.missing_required:
                if field_name in self.enrichment_sources.get("auto_generation", {}):
                    generated_value = await self._generate_field_value(field_name, metadata, content_type)
                    if generated_value:
                        enriched[field_name] = generated_value
                        result.enriched_fields.append(field_name)
                        result.enrichment_sources[field_name] = "auto_generation"
            
            # Enhance existing fields
            for source_name, source_config in self.enrichment_sources.items():
                if source_name == "auto_generation":
                    continue
                
                source_enrichment = await self._enrich_with_source(metadata, content_type, source_name)
                for key, value in source_enrichment.items():
                    if key not in metadata or not metadata[key]:
                        enriched[key] = value
                        result.enriched_fields.append(key)
                        result.enrichment_sources[key] = source_name
            
            # Update result
            result.enriched_metadata = enriched
            
        except Exception as e:
            logger.error(f"Metadata enrichment failed: {str(e)}")
    
    async def _calculate_completeness_score(self, result: MetadataValidationResult) -> float:
        """Calculate metadata completeness score."""
        try:
            if result.total_fields == 0:
                return 100.0
            
            completed_fields = result.total_fields - len(result.missing_required)
            return (completed_fields / result.total_fields) * 100
            
        except Exception:
            return 0.0
    
    async def _calculate_quality_score(self, result: MetadataValidationResult) -> float:
        """
Calculate overall metadata quality score."""
        try:
            # Base score
            base_score = result.completeness_score
            
            # Deduct for issues
            for issue in result.issues:
                if issue.severity == ValidationSeverity.CRITICAL:
                    base_score -= 25
                elif issue.severity == ValidationSeverity.ERROR:
                    base_score -= 15
                elif issue.severity == ValidationSeverity.WARNING:
                    base_score -= 5
            
            # Bonus for enrichments
            if result.enriched_fields:
                base_score += len(result.enriched_fields) * 2
            
            return max(0, min(100, base_score))
            
        except Exception:
            return 50.0
    
    async def _calculate_standardization_score(self, result: MetadataValidationResult) -> float:
        """
Calculate standardization score."""
        try:
            # Higher score for using recognized standards
            score = len(result.detected_standards) * 20
            return min(100, score)
            
        except Exception:
            return 0.0
    
    async def _calculate_consistency_score(self, result: MetadataValidationResult) -> float:
        """
Calculate consistency score."""
        try:
            consistency_issues = [issue for issue in result.issues 
                                if "consistency" in issue.issue_type]
            
            if not consistency_issues:
                return 100.0
            
            # Deduct for consistency issues
            score = 100 - (len(consistency_issues) * 20)
            return max(0, score)
            
        except Exception:
            return 50.0
    
    async def _calculate_richness_score(self, result: MetadataValidationResult) -> float:
        """Calculate metadata richness score."""
        try:
            # Score based on number of fields and types
            field_count = len(result.original_metadata)
            type_count = len(result.metadata_types)
            
            richness_score = (field_count * 2) + (type_count * 10)
            return min(100, richness_score)
            
        except Exception:
            return 0.0
    
    def _get_applicable_fields(
        self,
        content_type: Optional[str],
        standard: MetadataStandard
    ) -> List[MetadataField]:
        """
Get applicable field definitions."""
        try:
            applicable = []
            
            for field_def in self.field_definitions:
                # Check standard
                if field_def.standard != standard and standard != MetadataStandard.CUSTOM:
                    continue
                
                # Check content type (would implement content-specific filtering)
                applicable.append(field_def)
            
            return applicable
            
        except Exception as e:
            logger.error(f"Failed to get applicable fields: {str(e)}")
            return []
    
    def _detect_content_type(self, filename: str, file_data: bytes) -> str:
        """Detect content type from filename and data."""
        try:
            ext = Path(filename).suffix.lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                return "image"
            elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
                return "audio"
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                return "video"
            elif ext in ['.txt', '.md', '.doc', '.docx', '.pdf']:
                return "document"
            else:
                return "unknown"
            
        except Exception:
            return "unknown"
    
    async def _extract_image_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract image-specific metadata."""
        try:
            metadata = {}
            
            # Would use libraries like Pillow, exifread, etc.
            # For now, simulate metadata extraction
            
            metadata["content_type"] = "image"
            metadata["extracted_from"] = "image_analysis"
            
            return metadata
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_audio_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract audio-specific metadata."""
        try:
            metadata = {}
            
            # Would use libraries like mutagen, eyed3, etc.
            # For now, simulate metadata extraction
            
            metadata["content_type"] = "audio"
            metadata["extracted_from"] = "audio_analysis"
            
            return metadata
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_video_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract video-specific metadata."""
        try:
            metadata = {}
            
            # Would use libraries like ffmpeg-python, etc.
            # For now, simulate metadata extraction
            
            metadata["content_type"] = "video"
            metadata["extracted_from"] = "video_analysis"
            
            return metadata
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_document_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract document-specific metadata."""
        try:
            metadata = {}
            
            # Would use libraries like python-docx, PyPDF2, etc.
            # For now, simulate metadata extraction
            
            metadata["content_type"] = "document"
            metadata["extracted_from"] = "document_analysis"
            
            return metadata
            
        except Exception as e:
            logger.error(f"Document metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_technical_metadata(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract technical metadata."""
        try:
            import hashlib
            import mimetypes
            
            metadata = {
                "file_size": len(file_data),
                "file_name": filename,
                "file_hash": hashlib.sha256(file_data).hexdigest(),
                "mime_type": mimetypes.guess_type(filename)[0],
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Technical metadata extraction failed: {str(e)}")
            return {}
    
    async def _extract_administrative_metadata(self, file_path: Optional[Path]) -> Dict[str, Any]:
        """Extract administrative metadata."""
        try:
            metadata = {}
            
            if file_path and file_path.exists():
                stat = file_path.stat()
                metadata.update({
                    "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "access_date": datetime.fromtimestamp(stat.st_atime).isoformat(),
                    "file_permissions": oct(stat.st_mode)[-3:]
                })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Administrative metadata extraction failed: {str(e)}")
            return {}
    
    def _create_error_result(self, error_message: str) -> MetadataValidationResult:
        """Create error validation result."""
        return MetadataValidationResult(
            is_valid=False,
            completeness_score=0.0,
            quality_score=0.0,
            validation_time=0.0,
            issues=[MetadataIssue(
                field_name="system",
                issue_type="validation_error",
                severity=ValidationSeverity.CRITICAL,
                message=error_message
            )]
        )
    
    def _init_field_definitions(self) -> List[MetadataField]:
        """Initialize metadata field definitions."""
        return [
            # Core descriptive fields
            MetadataField("title", "string", True, False, min_length=1, max_length=200),
            MetadataField("description", "string", False, False, max_length=2000),
            MetadataField("creator", "string", True, False, min_length=1),
            MetadataField("created_date", "date", True, False),
            MetadataField("content_type", "string", True, False, 
                         allowed_values=["image", "audio", "video", "document", "text"]),
            
            # Technical fields
            MetadataField("file_size", "integer", False, False),
            MetadataField("file_format", "string", False, False),
            MetadataField("mime_type", "string", False, False),
            MetadataField("file_hash", "string", False, False),
            
            # Rights and licensing
            MetadataField("license", "string", False, False),
            MetadataField("copyright", "string", False, False),
            MetadataField("usage_rights", "string", False, False),
            
            # Categorization
            MetadataField("tags", "array", False, True),
            MetadataField("categories", "array", False, True),
            MetadataField("genre", "string", False, False),
            
            # Quality metrics
            MetadataField("quality_score", "float", False, False),
            MetadataField("resolution", "string", False, False, pattern=r'^\d+x\d+$'),
            MetadataField("duration", "float", False, False)
        ]
    
    def _init_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules."""
        return {
            "require_title": True,
            "require_creator": True,
            "require_content_type": True,
            "max_title_length": 200,
            "max_description_length": 2000,
            "max_tags": 20,
            "date_format": "ISO8601"
        }
    
    def _init_enrichment_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize enrichment sources."""
        return {
            "auto_generation": {
                "created_date": "current_timestamp",
                "file_hash": "calculate_hash",
                "extraction_timestamp": "current_timestamp"
            },
            "content_analysis": {
                "quality_score": "analyze_quality",
                "content_tags": "extract_tags"
            },
            "external_apis": {
                "geolocation": "reverse_geocoding",
                "metadata_enrichment": "external_lookup"
            }
        }
    
    def _init_standard_mappings(self) -> Dict[MetadataStandard, Dict[str, str]]:
        """Initialize standard field mappings."""
        return {
            MetadataStandard.DUBLIN_CORE: {
                "title": "dc:title",
                "creator": "dc:creator",
                "description": "dc:description",
                "created_date": "dc:date",
                "content_type": "dc:type",
                "file_format": "dc:format"
            },
            MetadataStandard.EXIF: {
                "camera_make": "exif:Make",
                "camera_model": "exif:Model",
                "created_date": "exif:DateTime",
                "resolution": "exif:ImageLength"
            }
        }
    
    def _init_pattern_validators(self) -> Dict[str, str]:
        """Initialize pattern validators."""
        return {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "url": r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$',
            "date": r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            "resolution": r'^\d+x\d+$',
            "duration": r'^\d+:\d{2}:\d{2}$'
        }
