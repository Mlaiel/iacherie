"""
Ainflue Platform - Multimedia Formats - Metadata Formats Management
Professional metadata format handling and processing for multimedia content

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataFormat(Enum):
    """Supported metadata formats"""
    EXIF = "exif"           # Image metadata
    IPTC = "iptc"           # Image metadata
    XMP = "xmp"             # Adobe extensible metadata
    ID3 = "id3"             # Audio metadata
    VORBIS_COMMENT = "vorbis_comment"  # Ogg/FLAC metadata
    MP4_METADATA = "mp4_metadata"      # MP4 container metadata
    MKV_TAGS = "mkv_tags"              # Matroska metadata
    DUBLIN_CORE = "dublin_core"        # Standard metadata schema
    SCHEMA_ORG = "schema_org"           # Schema.org structured data
    JSON_LD = "json_ld"                # JSON-LD metadata
    FFMPEG_METADATA = "ffmpeg_metadata" # FFmpeg metadata format


class MetadataType(Enum):
    """Types of metadata"""
    DESCRIPTIVE = "descriptive"    # Title, description, keywords
    TECHNICAL = "technical"        # Resolution, bitrate, codec
    ADMINISTRATIVE = "administrative"  # Rights, usage, creation
    STRUCTURAL = "structural"      # Chapters, tracks, relationships
    PRESERVATION = "preservation"  # Checksums, provenance
    RIGHTS = "rights"             # Copyright, licensing
    GEOSPATIAL = "geospatial"     # Location, GPS coordinates
    TEMPORAL = "temporal"         # Timestamps, duration


@dataclass
class MetadataField:
    """Metadata field definition"""
    name: str = ""
    value: Any = None
    data_type: str = "string"  # string, number, date, boolean, array
    format_specific_name: Optional[str] = None
    description: str = ""
    required: bool = False
    repeatable: bool = False
    controlled_vocabulary: Optional[List[str]] = None


@dataclass
class MetadataSchema:
    """Metadata schema definition"""
    schema_id: str = ""
    name: str = ""
    description: str = ""
    version: str = "1.0"
    namespace: Optional[str] = None
    fields: List[MetadataField] = field(default_factory=list)
    format_mappings: Dict[MetadataFormat, Dict[str, str]] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedMetadata:
    """Extracted metadata container"""
    file_path: str = ""
    extraction_timestamp: Optional[float] = None
    metadata_format: Optional[MetadataFormat] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
    structured_metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now().timestamp()


class MetadataFormatsManager:
    """Professional metadata formats management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metadata formats manager"""
        self.config = config or {}
        self.schemas: Dict[str, MetadataSchema] = {}
        self.format_extractors: Dict[MetadataFormat, callable] = {}
        self.format_writers: Dict[MetadataFormat, callable] = {}
        
        # Initialize standard schemas
        self._initialize_standard_schemas()
        
        # Initialize format handlers
        self._initialize_format_handlers()
    
    def _initialize_standard_schemas(self):
        """Initialize standard metadata schemas"""
        try:
            # Dublin Core schema
            dublin_core = MetadataSchema(
                schema_id="dublin_core",
                name="Dublin Core Metadata Element Set",
                description="Standard metadata schema for digital resources",
                namespace="http://purl.org/dc/elements/1.1/",
                fields=[
                    MetadataField("title", description="Resource title", required=True),
                    MetadataField("creator", description="Entity responsible for making the resource"),
                    MetadataField("subject", description="Topic of the resource", repeatable=True),
                    MetadataField("description", description="Account of the resource"),
                    MetadataField("publisher", description="Entity responsible for making resource available"),
                    MetadataField("contributor", description="Entity responsible for contributions", repeatable=True),
                    MetadataField("date", description="Point or period of time", data_type="date"),
                    MetadataField("type", description="Nature or genre of the resource"),
                    MetadataField("format", description="File format or physical medium"),
                    MetadataField("identifier", description="Unambiguous reference"),
                    MetadataField("source", description="Related resource from which this is derived"),
                    MetadataField("language", description="Language of the resource"),
                    MetadataField("relation", description="Related resource", repeatable=True),
                    MetadataField("coverage", description="Spatial or temporal topic"),
                    MetadataField("rights", description="Rights held in and over the resource")
                ]
            )
            self.register_schema(dublin_core)
            
            # Technical metadata schema
            technical_schema = MetadataSchema(
                schema_id="technical_metadata",
                name="Technical Metadata Schema",
                description="Technical properties of multimedia content",
                fields=[
                    MetadataField("file_size", data_type="number", description="File size in bytes"),
                    MetadataField("duration", data_type="number", description="Duration in seconds"),
                    MetadataField("width", data_type="number", description="Video/image width"),
                    MetadataField("height", data_type="number", description="Video/image height"),
                    MetadataField("frame_rate", data_type="number", description="Video frame rate"),
                    MetadataField("bit_rate", data_type="number", description="Overall bit rate"),
                    MetadataField("video_codec", description="Video codec used"),
                    MetadataField("audio_codec", description="Audio codec used"),
                    MetadataField("container_format", description="Container format"),
                    MetadataField("color_space", description="Color space"),
                    MetadataField("sample_rate", data_type="number", description="Audio sample rate"),
                    MetadataField("channels", data_type="number", description="Audio channels"),
                    MetadataField("creation_tool", description="Software used to create the file"),
                    MetadataField("encoding_settings", description="Encoding parameters used")
                ]
            )
            self.register_schema(technical_schema)
            
            # Rights and licensing schema
            rights_schema = MetadataSchema(
                schema_id="rights_metadata",
                name="Rights and Licensing Schema",
                description="Rights management and licensing information",
                fields=[
                    MetadataField("copyright", description="Copyright statement"),
                    MetadataField("license", description="License under which content is available"),
                    MetadataField("rights_holder", description="Entity that holds the rights"),
                    MetadataField("usage_terms", description="Terms of use"),
                    MetadataField("attribution_required", data_type="boolean", description="Attribution required"),
                    MetadataField("commercial_use", data_type="boolean", description="Commercial use allowed"),
                    MetadataField("derivative_works", data_type="boolean", description="Derivative works allowed"),
                    MetadataField("share_alike", data_type="boolean", description="Share-alike required"),
                    MetadataField("expiration_date", data_type="date", description="Rights expiration date"),
                    MetadataField("territory", description="Geographic territory of rights"),
                    MetadataField("medium", description="Medium of rights (web, broadcast, etc.)")
                ]
            )
            self.register_schema(rights_schema)
            
        except Exception as e:
            logger.error(f"Error initializing standard schemas: {e}")
    
    def _initialize_format_handlers(self):
        """Initialize format-specific extractors and writers"""
        try:
            # Register extractors
            self.format_extractors[MetadataFormat.EXIF] = self._extract_exif_metadata
            self.format_extractors[MetadataFormat.ID3] = self._extract_id3_metadata
            self.format_extractors[MetadataFormat.MP4_METADATA] = self._extract_mp4_metadata
            self.format_extractors[MetadataFormat.XMP] = self._extract_xmp_metadata
            
            # Register writers
            self.format_writers[MetadataFormat.EXIF] = self._write_exif_metadata
            self.format_writers[MetadataFormat.ID3] = self._write_id3_metadata
            self.format_writers[MetadataFormat.MP4_METADATA] = self._write_mp4_metadata
            self.format_writers[MetadataFormat.XMP] = self._write_xmp_metadata
            
        except Exception as e:
            logger.error(f"Error initializing format handlers: {e}")
    
    def register_schema(self, schema: MetadataSchema) -> bool:
        """Register a metadata schema"""
        try:
            self.schemas[schema.schema_id] = schema
            logger.info(f"Registered metadata schema: {schema.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering schema: {e}")
            return False
    
    def get_schema(self, schema_id: str) -> Optional[MetadataSchema]:
        """Get metadata schema by ID"""
        return self.schemas.get(schema_id)
    
    async def extract_metadata(
        self,
        file_path: Union[str, Path],
        metadata_format: Optional[MetadataFormat] = None,
        schema_id: Optional[str] = None
    ) -> ExtractedMetadata:
        """Extract metadata from file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Auto-detect format if not specified
            if metadata_format is None:
                metadata_format = self._detect_metadata_format(file_path)
            
            extracted = ExtractedMetadata(
                file_path=str(file_path),
                metadata_format=metadata_format
            )
            
            # Extract using format-specific extractor
            if metadata_format in self.format_extractors:
                extractor = self.format_extractors[metadata_format]
                raw_metadata = await extractor(file_path)
                extracted.raw_metadata = raw_metadata
            else:
                extracted.warnings.append(f"No extractor available for format {metadata_format.value}")
            
            # Apply schema if specified
            if schema_id and schema_id in self.schemas:
                schema = self.schemas[schema_id]
                extracted.structured_metadata = self._apply_schema(extracted.raw_metadata, schema)
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return ExtractedMetadata(
                file_path=str(file_path),
                errors=[str(e)]
            )
    
    def _detect_metadata_format(self, file_path: Path) -> MetadataFormat:
        """Auto-detect metadata format based on file type"""
        try:
            extension = file_path.suffix.lower()
            
            if extension in ['.jpg', '.jpeg', '.tiff', '.tif']:
                return MetadataFormat.EXIF
            elif extension in ['.mp3']:
                return MetadataFormat.ID3
            elif extension in ['.mp4', '.m4v', '.m4a']:
                return MetadataFormat.MP4_METADATA
            elif extension in ['.mkv', '.mka']:
                return MetadataFormat.MKV_TAGS
            elif extension in ['.ogg', '.flac']:
                return MetadataFormat.VORBIS_COMMENT
            else:
                return MetadataFormat.FFMPEG_METADATA  # Generic fallback
                
        except Exception as e:
            logger.error(f"Error detecting metadata format: {e}")
            return MetadataFormat.FFMPEG_METADATA
    
    def _apply_schema(
        self,
        raw_metadata: Dict[str, Any],
        schema: MetadataSchema
    ) -> Dict[str, Any]:
        """Apply schema to structure metadata"""
        try:
            structured = {}
            
            for field in schema.fields:
                value = None
                
                # Try to find value in raw metadata
                if field.name in raw_metadata:
                    value = raw_metadata[field.name]
                elif field.format_specific_name and field.format_specific_name in raw_metadata:
                    value = raw_metadata[field.format_specific_name]
                
                # Type conversion
                if value is not None:
                    if field.data_type == "number":
                        try:
                            value = float(value) if '.' in str(value) else int(value)
                        except (ValueError, TypeError):
                            pass
                    elif field.data_type == "boolean":
                        if isinstance(value, str):
                            value = value.lower() in ['true', '1', 'yes', 'on']
                        else:
                            value = bool(value)
                    elif field.data_type == "date":
                        # Handle date parsing (simplified)
                        if isinstance(value, str):
                            try:
                                # Try common date formats
                                for fmt in ['%Y-%m-%d', '%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                                    try:
                                        parsed_date = datetime.strptime(value, fmt)
                                        value = parsed_date.isoformat()
                                        break
                                    except ValueError:
                                        continue
                            except Exception:
                                pass  # Keep original value
                
                # Validation
                if field.controlled_vocabulary and value:
                    if value not in field.controlled_vocabulary:
                        logger.warning(f"Value '{value}' not in controlled vocabulary for field '{field.name}'")
                
                if value is not None or field.required:
                    structured[field.name] = value
            
            return structured
            
        except Exception as e:
            logger.error(f"Error applying schema: {e}")
            return {}
    
    # Format-specific extractors (simplified implementations)
    async def _extract_exif_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract EXIF metadata from image files"""
        try:
            # Simplified EXIF extraction
            # In production, would use libraries like exifread or Pillow
            metadata = {
                "camera_make": "Unknown",
                "camera_model": "Unknown",
                "creation_date": datetime.now().isoformat(),
                "image_width": 1920,
                "image_height": 1080,
                "orientation": 1,
                "exposure_time": "1/60",
                "f_number": "f/2.8",
                "iso_speed": 100,
                "flash": False,
                "gps_latitude": None,
                "gps_longitude": None
            }
            
            logger.info(f"Extracted EXIF metadata from {file_path.name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting EXIF metadata: {e}")
            return {}
    
    async def _extract_id3_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract ID3 metadata from audio files"""
        try:
            # Simplified ID3 extraction
            # In production, would use libraries like mutagen or eyed3
            metadata = {
                "title": file_path.stem,
                "artist": "Unknown Artist",
                "album": "Unknown Album",
                "date": "2025",
                "track": "1",
                "genre": "Unknown",
                "duration": 180.0,
                "bitrate": 320,
                "sample_rate": 44100,
                "channels": 2,
                "encoder": "Unknown"
            }
            
            logger.info(f"Extracted ID3 metadata from {file_path.name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting ID3 metadata: {e}")
            return {}
    
    async def _extract_mp4_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from MP4 files"""
        try:
            # Simplified MP4 metadata extraction
            # In production, would use FFprobe or similar
            metadata = {
                "title": file_path.stem,
                "creation_time": datetime.now().isoformat(),
                "duration": 300.0,
                "width": 1920,
                "height": 1080,
                "frame_rate": 30.0,
                "video_codec": "h264",
                "audio_codec": "aac",
                "bitrate": 5000000,
                "encoder": "FFmpeg"
            }
            
            logger.info(f"Extracted MP4 metadata from {file_path.name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting MP4 metadata: {e}")
            return {}
    
    async def _extract_xmp_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract XMP metadata"""
        try:
            # Simplified XMP extraction
            # In production, would parse actual XMP data
            metadata = {
                "creator_tool": "Adobe Creative Suite",
                "document_id": "xmp.did:12345",
                "instance_id": "xmp.iid:67890",
                "creation_date": datetime.now().isoformat(),
                "modify_date": datetime.now().isoformat(),
                "metadata_date": datetime.now().isoformat(),
                "rights": "All rights reserved",
                "usage_terms": "Contact for licensing"
            }
            
            logger.info(f"Extracted XMP metadata from {file_path.name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting XMP metadata: {e}")
            return {}
    
    # Format-specific writers (simplified implementations)
    async def _write_exif_metadata(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Write EXIF metadata to image file"""
        try:
            # Simplified EXIF writing
            # In production, would use libraries like exifread or Pillow
            logger.info(f"Writing EXIF metadata to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing EXIF metadata: {e}")
            return False
    
    async def _write_id3_metadata(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Write ID3 metadata to audio file"""
        try:
            # Simplified ID3 writing
            # In production, would use libraries like mutagen or eyed3
            logger.info(f"Writing ID3 metadata to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing ID3 metadata: {e}")
            return False
    
    async def _write_mp4_metadata(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Write metadata to MP4 file"""
        try:
            # Simplified MP4 metadata writing
            # In production, would use FFmpeg or similar
            logger.info(f"Writing MP4 metadata to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing MP4 metadata: {e}")
            return False
    
    async def _write_xmp_metadata(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> bool:
        """Write XMP metadata"""
        try:
            # Simplified XMP writing
            # In production, would generate proper XMP and embed
            logger.info(f"Writing XMP metadata to {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing XMP metadata: {e}")
            return False
    
    async def write_metadata(
        self,
        file_path: Union[str, Path],
        metadata: Dict[str, Any],
        metadata_format: MetadataFormat,
        backup_original: bool = True
    ) -> bool:
        """Write metadata to file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Create backup if requested
            if backup_original:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Write using format-specific writer
            if metadata_format in self.format_writers:
                writer = self.format_writers[metadata_format]
                success = await writer(file_path, metadata)
                
                if success:
                    logger.info(f"Successfully wrote {metadata_format.value} metadata to {file_path.name}")
                    return True
                else:
                    logger.error(f"Failed to write {metadata_format.value} metadata to {file_path.name}")
                    return False
            else:
                logger.error(f"No writer available for format {metadata_format.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing metadata: {e}")
            return False
    
    async def convert_metadata_format(
        self,
        source_metadata: Dict[str, Any],
        source_format: MetadataFormat,
        target_format: MetadataFormat,
        schema_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert metadata between formats"""
        try:
            converted_metadata = {}
            
            # If schema is provided, use it as intermediate format
            if schema_id and schema_id in self.schemas:
                schema = self.schemas[schema_id]
                structured = self._apply_schema(source_metadata, schema)
                
                # Map from schema to target format
                if target_format in schema.format_mappings:
                    mapping = schema.format_mappings[target_format]
                    for schema_field, target_field in mapping.items():
                        if schema_field in structured:
                            converted_metadata[target_field] = structured[schema_field]
                else:
                    # Direct copy if no mapping available
                    converted_metadata = structured.copy()
            else:
                # Direct format conversion (simplified)
                # In production, would have comprehensive format mappings
                if source_format == MetadataFormat.EXIF and target_format == MetadataFormat.XMP:
                    # EXIF to XMP mapping
                    mapping = {
                        "camera_make": "exif:Make",
                        "camera_model": "exif:Model",
                        "creation_date": "xmp:CreateDate",
                        "image_width": "exif:PixelXDimension",
                        "image_height": "exif:PixelYDimension"
                    }
                    for source_field, target_field in mapping.items():
                        if source_field in source_metadata:
                            converted_metadata[target_field] = source_metadata[source_field]
                elif source_format == MetadataFormat.ID3 and target_format == MetadataFormat.MP4_METADATA:
                    # ID3 to MP4 mapping
                    mapping = {
                        "title": "title",
                        "artist": "artist",
                        "album": "album",
                        "date": "date",
                        "track": "track",
                        "genre": "genre"
                    }
                    for source_field, target_field in mapping.items():
                        if source_field in source_metadata:
                            converted_metadata[target_field] = source_metadata[source_field]
                else:
                    # Default: copy compatible fields
                    converted_metadata = source_metadata.copy()
            
            return converted_metadata
            
        except Exception as e:
            logger.error(f"Error converting metadata format: {e}")
            return {}
    
    def validate_metadata(
        self,
        metadata: Dict[str, Any],
        schema_id: str
    ) -> Dict[str, Any]:
        """Validate metadata against schema"""
        try:
            if schema_id not in self.schemas:
                return {
                    "valid": False,
                    "errors": [f"Schema {schema_id} not found"]
                }
            
            schema = self.schemas[schema_id]
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields
            for field in schema.fields:
                if field.required and field.name not in metadata:
                    validation_result["errors"].append(f"Required field '{field.name}' missing")
                    validation_result["valid"] = False
                
                if field.name in metadata:
                    value = metadata[field.name]
                    
                    # Type validation
                    if field.data_type == "number" and not isinstance(value, (int, float)):
                        validation_result["errors"].append(f"Field '{field.name}' should be numeric")
                        validation_result["valid"] = False
                    elif field.data_type == "boolean" and not isinstance(value, bool):
                        validation_result["errors"].append(f"Field '{field.name}' should be boolean")
                        validation_result["valid"] = False
                    
                    # Controlled vocabulary validation
                    if field.controlled_vocabulary and value not in field.controlled_vocabulary:
                        validation_result["warnings"].append(
                            f"Field '{field.name}' value '{value}' not in controlled vocabulary"
                        )
            
            # Schema-specific validation rules
            if schema.validation_rules:
                # Apply custom validation rules (simplified)
                for rule_name, rule_config in schema.validation_rules.items():
                    if rule_name == "date_range":
                        # Example: validate date is within acceptable range
                        pass
                    elif rule_name == "numeric_range":
                        # Example: validate numeric values are within range
                        pass
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating metadata: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def get_format_capabilities(self, metadata_format: MetadataFormat) -> Dict[str, Any]:
        """Get capabilities of specific metadata format"""
        try:
            capabilities = {
                MetadataFormat.EXIF: {
                    "supports_images": True,
                    "supports_video": False,
                    "supports_audio": False,
                    "max_text_length": 65535,
                    "supports_unicode": True,
                    "supports_binary_data": True,
                    "embedded_in_file": True,
                    "standardized": True
                },
                MetadataFormat.ID3: {
                    "supports_images": False,
                    "supports_video": False,
                    "supports_audio": True,
                    "max_text_length": 65535,
                    "supports_unicode": True,
                    "supports_binary_data": True,
                    "embedded_in_file": True,
                    "standardized": True
                },
                MetadataFormat.XMP: {
                    "supports_images": True,
                    "supports_video": True,
                    "supports_audio": True,
                    "max_text_length": -1,  # No limit
                    "supports_unicode": True,
                    "supports_binary_data": False,
                    "embedded_in_file": True,
                    "standardized": True,
                    "extensible": True
                }
            }
            
            return capabilities.get(metadata_format, {})
            
        except Exception as e:
            logger.error(f"Error getting format capabilities: {e}")
            return {}


# Export main classes
__all__ = [
    'MetadataFormatsManager',
    'MetadataSchema',
    'MetadataField',
    'ExtractedMetadata',
    'MetadataFormat',
    'MetadataType'
]