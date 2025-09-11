"""
Metadata Formats Module for Ainflue Platform
Comprehensive metadata format handling and extraction

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataFormat(Enum):
    """Metadata format types"""
    EXIF = "exif"
    IPTC = "iptc"
    XMP = "xmp"
    ID3 = "id3"
    VORBIS_COMMENT = "vorbis_comment"
    MP4_METADATA = "mp4_metadata"
    MATROSKA_TAGS = "matroska_tags"
    RIFF_INFO = "riff_info"
    QUICKTIME_META = "quicktime_meta"
    DUBLIN_CORE = "dublin_core"
    CREATIVE_COMMONS = "creative_commons"


class MediaType(Enum):
    """Media type classifications"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    MIXED = "mixed"


@dataclass
class MetadataField:
    """Metadata field definition"""
    field_id: str
    name: str
    description: str
    data_type: str  # string, integer, float, datetime, binary, array
    required: bool = False
    multiple_values: bool = False
    max_length: Optional[int] = None
    enum_values: Optional[List[str]] = None
    format_pattern: Optional[str] = None


@dataclass
class MetadataSchema:
    """Metadata format schema definition"""
    format_id: str
    name: str
    description: str
    version: str
    specification_url: str
    media_types: List[MediaType]
    
    # Technical details
    encoding: str = "utf-8"
    byte_order: str = "little"  # little, big, variable
    storage_method: str = "embedded"  # embedded, sidecar, database
    
    # Field definitions
    fields: Dict[str, MetadataField] = field(default_factory=dict)
    
    # Format capabilities
    supports_nested: bool = False
    supports_arrays: bool = False
    supports_localization: bool = False
    supports_custom_fields: bool = False
    max_size: Optional[int] = None
    
    # Implementation details
    library_support: Dict[str, str] = field(default_factory=dict)
    platform_support: Dict[str, bool] = field(default_factory=dict)
    
    created_at: str = ""
    updated_at: str = ""


class MetadataFormatsRegistry:
    """
    Registry for metadata format specifications and handlers
    Manages metadata extraction and manipulation for multimedia content
    """
    
    def __init__(self):
        self.schemas: Dict[str, MetadataSchema] = {}
        self.media_type_mappings: Dict[MediaType, List[str]] = {
            MediaType.IMAGE: [],
            MediaType.AUDIO: [],
            MediaType.VIDEO: [],
            MediaType.DOCUMENT: [],
            MediaType.MIXED: []
        }
        self._initialize_metadata_schemas()
    
    def _initialize_metadata_schemas(self):
        """Initialize registry with standard metadata schemas"""
        
        # EXIF (Exchangeable Image File Format)
        exif_fields = {
            "make": MetadataField(
                "make", "Camera Make", "Camera manufacturer", "string", max_length=255
            ),
            "model": MetadataField(
                "model", "Camera Model", "Camera model name", "string", max_length=255
            ),
            "datetime": MetadataField(
                "datetime", "Date Time", "Image capture date and time", "datetime", required=True
            ),
            "orientation": MetadataField(
                "orientation", "Orientation", "Image orientation", "integer", 
                enum_values=["1", "2", "3", "4", "5", "6", "7", "8"]
            ),
            "x_resolution": MetadataField(
                "x_resolution", "X Resolution", "Horizontal resolution", "float"
            ),
            "y_resolution": MetadataField(
                "y_resolution", "Y Resolution", "Vertical resolution", "float"
            ),
            "resolution_unit": MetadataField(
                "resolution_unit", "Resolution Unit", "Resolution unit", "integer",
                enum_values=["1", "2", "3"]  # None, inches, centimeters
            ),
            "software": MetadataField(
                "software", "Software", "Software used to create image", "string", max_length=255
            ),
            "artist": MetadataField(
                "artist", "Artist", "Image creator", "string", max_length=255
            ),
            "copyright": MetadataField(
                "copyright", "Copyright", "Copyright information", "string", max_length=255
            ),
            "exposure_time": MetadataField(
                "exposure_time", "Exposure Time", "Shutter speed", "string"
            ),
            "f_number": MetadataField(
                "f_number", "F Number", "Aperture value", "float"
            ),
            "iso_speed_ratings": MetadataField(
                "iso_speed_ratings", "ISO Speed", "ISO sensitivity", "integer"
            ),
            "focal_length": MetadataField(
                "focal_length", "Focal Length", "Lens focal length", "float"
            ),
            "gps_latitude": MetadataField(
                "gps_latitude", "GPS Latitude", "GPS latitude coordinate", "float"
            ),
            "gps_longitude": MetadataField(
                "gps_longitude", "GPS Longitude", "GPS longitude coordinate", "float"
            ),
            "gps_altitude": MetadataField(
                "gps_altitude", "GPS Altitude", "GPS altitude", "float"
            )
        }
        
        exif_schema = MetadataSchema(
            format_id="exif",
            name="Exchangeable Image File Format",
            description="Standard metadata format for digital images",
            version="2.32",
            specification_url="https://www.cipa.jp/std/documents/e/DC-008-Translation-2019-E.pdf",
            media_types=[MediaType.IMAGE],
            encoding="ascii",
            byte_order="variable",
            storage_method="embedded",
            fields=exif_fields,
            supports_nested=True,
            supports_arrays=True,
            supports_localization=False,
            supports_custom_fields=True,
            library_support={
                "exifread": "python library",
                "piexif": "python library",
                "exiftool": "command line tool",
                "imagemagick": "image processing suite"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(exif_schema)
        
        # ID3 (MP3 metadata)
        id3_fields = {
            "title": MetadataField(
                "title", "Title", "Song title", "string", required=True, max_length=255
            ),
            "artist": MetadataField(
                "artist", "Artist", "Performing artist", "string", max_length=255
            ),
            "album": MetadataField(
                "album", "Album", "Album name", "string", max_length=255
            ),
            "date": MetadataField(
                "date", "Date", "Release date", "string", max_length=10
            ),
            "genre": MetadataField(
                "genre", "Genre", "Music genre", "string", max_length=255
            ),
            "track": MetadataField(
                "track", "Track Number", "Track number", "string", max_length=10
            ),
            "duration": MetadataField(
                "duration", "Duration", "Track duration in seconds", "integer"
            ),
            "composer": MetadataField(
                "composer", "Composer", "Music composer", "string", max_length=255
            ),
            "lyrics": MetadataField(
                "lyrics", "Lyrics", "Song lyrics", "string"
            ),
            "albumart": MetadataField(
                "albumart", "Album Art", "Cover art image", "binary"
            ),
            "bpm": MetadataField(
                "bpm", "BPM", "Beats per minute", "integer"
            ),
            "copyright": MetadataField(
                "copyright", "Copyright", "Copyright information", "string", max_length=255
            )
        }
        
        id3_schema = MetadataSchema(
            format_id="id3",
            name="ID3 Metadata",
            description="Standard metadata format for MP3 audio files",
            version="2.4",
            specification_url="https://id3.org/id3v2.4.0-structure",
            media_types=[MediaType.AUDIO],
            encoding="utf-8",
            byte_order="big",
            storage_method="embedded",
            fields=id3_fields,
            supports_nested=False,
            supports_arrays=True,
            supports_localization=True,
            supports_custom_fields=True,
            max_size=256 * 1024 * 1024,  # 256MB
            library_support={
                "mutagen": "python library",
                "eyed3": "python library",
                "taglib": "C++ library with bindings",
                "ffmpeg": "multimedia framework"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(id3_schema)
        
        # XMP (Extensible Metadata Platform)
        xmp_fields = {
            "creator": MetadataField(
                "creator", "Creator", "Content creator", "string", multiple_values=True
            ),
            "title": MetadataField(
                "title", "Title", "Content title", "string", multiple_values=True
            ),
            "description": MetadataField(
                "description", "Description", "Content description", "string"
            ),
            "subject": MetadataField(
                "subject", "Subject", "Content keywords", "array"
            ),
            "rights": MetadataField(
                "rights", "Rights", "Copyright and usage rights", "string"
            ),
            "create_date": MetadataField(
                "create_date", "Create Date", "Content creation date", "datetime"
            ),
            "modify_date": MetadataField(
                "modify_date", "Modify Date", "Last modification date", "datetime"
            ),
            "metadata_date": MetadataField(
                "metadata_date", "Metadata Date", "Metadata modification date", "datetime"
            ),
            "format": MetadataField(
                "format", "Format", "File format", "string"
            ),
            "identifier": MetadataField(
                "identifier", "Identifier", "Unique identifier", "string"
            ),
            "rating": MetadataField(
                "rating", "Rating", "Content rating (1-5)", "integer"
            ),
            "label": MetadataField(
                "label", "Label", "Color label", "string"
            )
        }
        
        xmp_schema = MetadataSchema(
            format_id="xmp",
            name="Extensible Metadata Platform",
            description="Adobe's extensible metadata framework",
            version="2020.1",
            specification_url="https://www.adobe.com/devnet/xmp.html",
            media_types=[MediaType.IMAGE, MediaType.VIDEO, MediaType.AUDIO, MediaType.DOCUMENT],
            encoding="utf-8",
            byte_order="big",
            storage_method="embedded",
            fields=xmp_fields,
            supports_nested=True,
            supports_arrays=True,
            supports_localization=True,
            supports_custom_fields=True,
            library_support={
                "python_xmp_toolkit": "python library",
                "exempi": "C library",
                "adobe_xmp_sdk": "official SDK",
                "exiftool": "command line tool"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(xmp_schema)
        
        # MP4 Metadata (iTunes-style)
        mp4_fields = {
            "title": MetadataField(
                "title", "Title", "Track or video title", "string", required=True
            ),
            "artist": MetadataField(
                "artist", "Artist", "Artist or creator", "string"
            ),
            "album": MetadataField(
                "album", "Album", "Album or collection name", "string"
            ),
            "date": MetadataField(
                "date", "Date", "Release date", "string"
            ),
            "genre": MetadataField(
                "genre", "Genre", "Content genre", "string"
            ),
            "comment": MetadataField(
                "comment", "Comment", "User comment", "string"
            ),
            "track": MetadataField(
                "track", "Track", "Track number/total", "string"
            ),
            "disc": MetadataField(
                "disc", "Disc", "Disc number/total", "string"
            ),
            "composer": MetadataField(
                "composer", "Composer", "Music composer", "string"
            ),
            "albumartist": MetadataField(
                "albumartist", "Album Artist", "Album artist", "string"
            ),
            "grouping": MetadataField(
                "grouping", "Grouping", "Content grouping", "string"
            ),
            "bpm": MetadataField(
                "bpm", "BPM", "Beats per minute", "integer"
            ),
            "cover": MetadataField(
                "cover", "Cover Art", "Album/video artwork", "binary"
            ),
            "copyright": MetadataField(
                "copyright", "Copyright", "Copyright information", "string"
            ),
            "description": MetadataField(
                "description", "Description", "Content description", "string"
            )
        }
        
        mp4_schema = MetadataSchema(
            format_id="mp4_metadata",
            name="MP4 Metadata",
            description="iTunes-style metadata for MP4 containers",
            version="1.0",
            specification_url="https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/Metadata/Metadata.html",
            media_types=[MediaType.VIDEO, MediaType.AUDIO],
            encoding="utf-8",
            byte_order="big",
            storage_method="embedded",
            fields=mp4_fields,
            supports_nested=False,
            supports_arrays=False,
            supports_localization=False,
            supports_custom_fields=True,
            library_support={
                "mutagen": "python library",
                "mp4v2": "C library",
                "ffmpeg": "multimedia framework",
                "taglib": "C++ library"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(mp4_schema)
        
        # Vorbis Comment (OGG, FLAC)
        vorbis_fields = {
            "title": MetadataField(
                "title", "Title", "Track title", "string", multiple_values=True
            ),
            "artist": MetadataField(
                "artist", "Artist", "Track artist", "string", multiple_values=True
            ),
            "album": MetadataField(
                "album", "Album", "Album name", "string"
            ),
            "date": MetadataField(
                "date", "Date", "Release date", "string"
            ),
            "genre": MetadataField(
                "genre", "Genre", "Music genre", "string", multiple_values=True
            ),
            "tracknumber": MetadataField(
                "tracknumber", "Track Number", "Track number", "string"
            ),
            "tracktotal": MetadataField(
                "tracktotal", "Track Total", "Total tracks", "string"
            ),
            "discnumber": MetadataField(
                "discnumber", "Disc Number", "Disc number", "string"
            ),
            "disctotal": MetadataField(
                "disctotal", "Disc Total", "Total discs", "string"
            ),
            "albumartist": MetadataField(
                "albumartist", "Album Artist", "Album artist", "string"
            ),
            "composer": MetadataField(
                "composer", "Composer", "Composer", "string", multiple_values=True
            ),
            "performer": MetadataField(
                "performer", "Performer", "Performer", "string", multiple_values=True
            ),
            "description": MetadataField(
                "description", "Description", "Track description", "string"
            ),
            "comment": MetadataField(
                "comment", "Comment", "User comment", "string", multiple_values=True
            )
        }
        
        vorbis_schema = MetadataSchema(
            format_id="vorbis_comment",
            name="Vorbis Comment",
            description="Metadata format for OGG and FLAC files",
            version="1.0",
            specification_url="https://xiph.org/vorbis/doc/v-comment.html",
            media_types=[MediaType.AUDIO],
            encoding="utf-8",
            byte_order="little",
            storage_method="embedded",
            fields=vorbis_fields,
            supports_nested=False,
            supports_arrays=False,
            supports_localization=False,
            supports_custom_fields=True,
            library_support={
                "mutagen": "python library",
                "vorbiscomment": "command line tool",
                "taglib": "C++ library",
                "ffmpeg": "multimedia framework"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(vorbis_schema)
        
        # IPTC (International Press Telecommunications Council)
        iptc_fields = {
            "object_name": MetadataField(
                "object_name", "Object Name", "Title or headline", "string", max_length=64
            ),
            "caption": MetadataField(
                "caption", "Caption", "Description of image content", "string", max_length=2000
            ),
            "keywords": MetadataField(
                "keywords", "Keywords", "Content keywords", "array"
            ),
            "byline": MetadataField(
                "byline", "Byline", "Creator/photographer name", "string", max_length=32
            ),
            "byline_title": MetadataField(
                "byline_title", "Byline Title", "Creator's job title", "string", max_length=32
            ),
            "credit": MetadataField(
                "credit", "Credit", "Provider credit", "string", max_length=32
            ),
            "source": MetadataField(
                "source", "Source", "Image source", "string", max_length=32
            ),
            "copyright_notice": MetadataField(
                "copyright_notice", "Copyright Notice", "Copyright information", "string", max_length=128
            ),
            "date_created": MetadataField(
                "date_created", "Date Created", "Creation date", "string", format_pattern="YYYYMMDD"
            ),
            "city": MetadataField(
                "city", "City", "City where image was taken", "string", max_length=32
            ),
            "state": MetadataField(
                "state", "State/Province", "State or province", "string", max_length=32
            ),
            "country": MetadataField(
                "country", "Country", "Country name", "string", max_length=64
            ),
            "category": MetadataField(
                "category", "Category", "Subject category", "string", max_length=3
            ),
            "urgency": MetadataField(
                "urgency", "Urgency", "Editorial urgency (1-8)", "string", max_length=1,
                enum_values=["1", "2", "3", "4", "5", "6", "7", "8"]
            )
        }
        
        iptc_schema = MetadataSchema(
            format_id="iptc",
            name="IPTC Information Interchange Model",
            description="Metadata standard for news and editorial images",
            version="4.2",
            specification_url="https://iptc.org/standards/iim/",
            media_types=[MediaType.IMAGE],
            encoding="utf-8",
            byte_order="big",
            storage_method="embedded",
            fields=iptc_fields,
            supports_nested=False,
            supports_arrays=True,
            supports_localization=False,
            supports_custom_fields=False,
            max_size=65535,  # IPTC record size limit
            library_support={
                "iptcinfo3": "python library",
                "exiftool": "command line tool",
                "pyexiv2": "python library",
                "imagemagick": "image processing suite"
            },
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": False
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_schema(iptc_schema)
    
    def register_schema(self, schema: MetadataSchema):
        """Register a metadata schema"""
        self.schemas[schema.format_id] = schema
        
        # Update media type mappings
        for media_type in schema.media_types:
            self.media_type_mappings[media_type].append(schema.format_id)
        
        logger.info(f"Registered metadata schema: {schema.name} ({schema.format_id})")
    
    def get_schema(self, format_id: str) -> Optional[MetadataSchema]:
        """Get metadata schema by format ID"""
        return self.schemas.get(format_id)
    
    def get_schemas_by_media_type(self, media_type: MediaType) -> List[MetadataSchema]:
        """Get all metadata schemas for specific media type"""
        schema_ids = self.media_type_mappings.get(media_type, [])
        return [self.schemas[schema_id] for schema_id in schema_ids]
    
    def get_supported_formats(self, library: str) -> List[MetadataSchema]:
        """Get metadata formats supported by specific library"""
        supported = []
        for schema in self.schemas.values():
            if library.lower() in [lib.lower() for lib in schema.library_support.keys()]:
                supported.append(schema)
        return supported
    
    def find_compatible_formats(
        self,
        media_type: MediaType,
        requirements: Dict[str, Any]
    ) -> List[MetadataSchema]:
        """Find metadata formats compatible with requirements"""
        candidates = self.get_schemas_by_media_type(media_type)
        compatible = []
        
        for schema in candidates:
            is_compatible = True
            
            # Check required features
            if requirements.get("supports_nested", False) and not schema.supports_nested:
                is_compatible = False
            
            if requirements.get("supports_arrays", False) and not schema.supports_arrays:
                is_compatible = False
            
            if requirements.get("supports_localization", False) and not schema.supports_localization:
                is_compatible = False
            
            if requirements.get("supports_custom_fields", False) and not schema.supports_custom_fields:
                is_compatible = False
            
            # Check platform support
            required_platforms = requirements.get("platforms", [])
            for platform in required_platforms:
                if not schema.platform_support.get(platform, False):
                    is_compatible = False
                    break
            
            # Check size requirements
            max_size_req = requirements.get("max_size")
            if max_size_req and schema.max_size and schema.max_size < max_size_req:
                is_compatible = False
            
            if is_compatible:
                compatible.append(schema)
        
        return compatible
    
    def validate_metadata(
        self,
        format_id: str,
        metadata: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate metadata against schema"""
        schema = self.get_schema(format_id)
        if not schema:
            return False, [f"Unknown metadata format: {format_id}"]
        
        errors = []
        
        # Check required fields
        for field_id, field_def in schema.fields.items():
            if field_def.required and field_id not in metadata:
                errors.append(f"Required field missing: {field_def.name}")
        
        # Validate field values
        for field_id, value in metadata.items():
            if field_id not in schema.fields:
                if not schema.supports_custom_fields:
                    errors.append(f"Custom field not supported: {field_id}")
                continue
            
            field_def = schema.fields[field_id]
            
            # Check data type
            if field_def.data_type == "integer":
                try:
                    int(value)
                except (ValueError, TypeError):
                    errors.append(f"Invalid integer value for {field_def.name}: {value}")
            
            elif field_def.data_type == "float":
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"Invalid float value for {field_def.name}: {value}")
            
            elif field_def.data_type == "string":
                if not isinstance(value, str):
                    errors.append(f"Invalid string value for {field_def.name}: {type(value)}")
                elif field_def.max_length and len(value) > field_def.max_length:
                    errors.append(f"String too long for {field_def.name}: {len(value)} > {field_def.max_length}")
            
            elif field_def.data_type == "array":
                if not isinstance(value, (list, tuple)):
                    errors.append(f"Invalid array value for {field_def.name}: {type(value)}")
            
            # Check enum values
            if field_def.enum_values and str(value) not in field_def.enum_values:
                errors.append(f"Invalid enum value for {field_def.name}: {value}")
        
        return len(errors) == 0, errors
    
    def convert_metadata(
        self,
        source_format: str,
        target_format: str,
        metadata: Dict[str, Any],
        mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Convert metadata between formats"""
        source_schema = self.get_schema(source_format)
        target_schema = self.get_schema(target_format)
        
        if not source_schema:
            return {}, [f"Unknown source format: {source_format}"]
        
        if not target_schema:
            return {}, [f"Unknown target format: {target_format}"]
        
        converted = {}
        warnings = []
        
        # Use provided mapping or create automatic mapping
        if not mapping:
            mapping = self._create_automatic_mapping(source_schema, target_schema)
        
        for source_field, value in metadata.items():
            target_field = mapping.get(source_field)
            
            if not target_field:
                warnings.append(f"No mapping for field: {source_field}")
                continue
            
            if target_field not in target_schema.fields:
                warnings.append(f"Target field not supported: {target_field}")
                continue
            
            # Convert data type if necessary
            target_field_def = target_schema.fields[target_field]
            converted_value = self._convert_field_value(
                value, target_field_def.data_type
            )
            
            if converted_value is not None:
                converted[target_field] = converted_value
            else:
                warnings.append(f"Could not convert value for {target_field}: {value}")
        
        return converted, warnings
    
    def _create_automatic_mapping(
        self,
        source_schema: MetadataSchema,
        target_schema: MetadataSchema
    ) -> Dict[str, str]:
        """Create automatic field mapping between schemas"""
        mapping = {}
        
        # Common field mappings
        common_mappings = {
            "title": ["title", "object_name"],
            "artist": ["artist", "creator", "byline"],
            "description": ["description", "caption", "comment"],
            "date": ["date", "datetime", "date_created", "create_date"],
            "creator": ["creator", "artist", "byline"],
            "copyright": ["copyright", "rights", "copyright_notice"],
            "keywords": ["keywords", "subject"],
            "genre": ["genre", "category"]
        }
        
        for source_field in source_schema.fields.keys():
            # Direct match first
            if source_field in target_schema.fields:
                mapping[source_field] = source_field
                continue
            
            # Try common mappings
            for common_field, variants in common_mappings.items():
                if source_field in variants:
                    for target_variant in variants:
                        if target_variant in target_schema.fields:
                            mapping[source_field] = target_variant
                            break
                    break
        
        return mapping
    
    def _convert_field_value(self, value: Any, target_type: str) -> Optional[Any]:
        """Convert field value to target data type"""
        if target_type == "string":
            return str(value)
        
        elif target_type == "integer":
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        elif target_type == "float":
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        elif target_type == "array":
            if isinstance(value, (list, tuple)):
                return list(value)
            else:
                return [str(value)]
        
        elif target_type == "datetime":
            # Basic datetime conversion - could be enhanced
            return str(value)
        
        elif target_type == "binary":
            if isinstance(value, bytes):
                return value
            else:
                return None
        
        return value
    
    def get_format_comparison(self, format_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare metadata formats"""
        comparison = {}
        
        for format_id in format_ids:
            schema = self.get_schema(format_id)
            if not schema:
                continue
            
            comparison[format_id] = {
                "name": schema.name,
                "version": schema.version,
                "media_types": [mt.value for mt in schema.media_types],
                "encoding": schema.encoding,
                "field_count": len(schema.fields),
                "supports_nested": schema.supports_nested,
                "supports_arrays": schema.supports_arrays,
                "supports_localization": schema.supports_localization,
                "supports_custom_fields": schema.supports_custom_fields,
                "max_size": schema.max_size,
                "platform_support_count": sum(schema.platform_support.values()),
                "library_count": len(schema.library_support)
            }
        
        return comparison
    
    def export_registry(self, file_path: Path) -> bool:
        """Export metadata schemas registry to JSON"""
        try:
            registry_data = {
                "schemas": {},
                "media_type_mappings": {
                    mt.value: formats for mt, formats in self.media_type_mappings.items()
                },
                "export_timestamp": datetime.now().isoformat(),
                "total_schemas": len(self.schemas)
            }
            
            for format_id, schema in self.schemas.items():
                schema_data = {
                    "format_id": schema.format_id,
                    "name": schema.name,
                    "description": schema.description,
                    "version": schema.version,
                    "specification_url": schema.specification_url,
                    "media_types": [mt.value for mt in schema.media_types],
                    "encoding": schema.encoding,
                    "byte_order": schema.byte_order,
                    "storage_method": schema.storage_method,
                    "supports_nested": schema.supports_nested,
                    "supports_arrays": schema.supports_arrays,
                    "supports_localization": schema.supports_localization,
                    "supports_custom_fields": schema.supports_custom_fields,
                    "max_size": schema.max_size,
                    "library_support": schema.library_support,
                    "platform_support": schema.platform_support,
                    "created_at": schema.created_at,
                    "updated_at": schema.updated_at,
                    "fields": {}
                }
                
                # Export field definitions
                for field_id, field_def in schema.fields.items():
                    field_data = {
                        "field_id": field_def.field_id,
                        "name": field_def.name,
                        "description": field_def.description,
                        "data_type": field_def.data_type,
                        "required": field_def.required,
                        "multiple_values": field_def.multiple_values,
                        "max_length": field_def.max_length,
                        "enum_values": field_def.enum_values,
                        "format_pattern": field_def.format_pattern
                    }
                    schema_data["fields"][field_id] = field_data
                
                registry_data["schemas"][format_id] = schema_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata formats registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metadata formats registry: {e}")
            return False


# Global metadata formats registry instance
metadata_formats_registry = MetadataFormatsRegistry()


async def get_metadata_formats_registry() -> MetadataFormatsRegistry:
    """Get the global metadata formats registry instance"""
    return metadata_formats_registry


if __name__ == "__main__":
    # Test metadata formats registry
    registry = MetadataFormatsRegistry()
    
    print("Metadata Formats Overview:")
    print(f"Total schemas: {len(registry.schemas)}")
    
    print("\nImage metadata formats:")
    image_formats = registry.get_schemas_by_media_type(MediaType.IMAGE)
    for schema in image_formats:
        print(f"- {schema.name}: {len(schema.fields)} fields")
    
    print("\nAudio metadata formats:")
    audio_formats = registry.get_schemas_by_media_type(MediaType.AUDIO)
    for schema in audio_formats:
        print(f"- {schema.name}: {len(schema.fields)} fields")
    
    # Test metadata validation
    print("\nValidating sample EXIF metadata:")
    sample_exif = {
        "make": "Canon",
        "model": "EOS R5",
        "datetime": "2025:09:11 19:18:00",
        "orientation": "1",
        "iso_speed_ratings": 100
    }
    
    is_valid, errors = registry.validate_metadata("exif", sample_exif)
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Test format conversion
    print("\nConverting EXIF to XMP:")
    converted, warnings = registry.convert_metadata("exif", "xmp", sample_exif)
    print(f"Converted fields: {list(converted.keys())}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")