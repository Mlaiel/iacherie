"""
Metadata Formats Management System
Comprehensive metadata format handling and extraction for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata"""
    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    ADMINISTRATIVE = "administrative"
    RIGHTS = "rights"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"


class MetadataStandard(Enum):
    """Metadata standards"""
    EXIF = "exif"
    IPTC = "iptc"
    XMP = "xmp"
    ID3 = "id3"
    VORBIS_COMMENT = "vorbis_comment"
    QUICKTIME = "quicktime"
    MATROSKA_TAGS = "matroska_tags"
    DUBLIN_CORE = "dublin_core"
    CUSTOM = "custom"


@dataclass
class MetadataField:
    """Metadata field specification"""
    name: str
    field_id: str
    metadata_type: MetadataType
    data_type: str  # string, integer, float, boolean, datetime, binary
    description: str
    required: bool = False
    default_value: Any = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
    format_pattern: Optional[str] = None
    human_readable: bool = True
    searchable: bool = True
    display_priority: int = 5  # 1-10, higher = more important


@dataclass 
class MetadataFormat:
    """Metadata format specification"""
    name: str
    standard: MetadataStandard
    file_types: List[str]
    supported_fields: List[MetadataField]
    encoding: str = "utf-8"
    case_sensitive: bool = True
    supports_custom_fields: bool = True
    max_size: int = 0  # 0 = unlimited
    binary_format: bool = False
    hierarchical: bool = False
    description: str = ""


class MetadataRegistry:
    """Registry for multimedia metadata formats and standards"""
    
    def __init__(self):
        self.formats: Dict[MetadataStandard, MetadataFormat] = {}
        self.field_registry: Dict[str, MetadataField] = {}
        self.cross_format_mappings: Dict[str, Dict[MetadataStandard, str]] = {}
        self._initialize_metadata_formats()
    
    def _initialize_metadata_formats(self):
        """Initialize comprehensive metadata format definitions"""
        
        # EXIF Metadata Format
        self._register_exif_format()
        
        # IPTC Metadata Format
        self._register_iptc_format()
        
        # XMP Metadata Format
        self._register_xmp_format()
        
        # ID3 Audio Metadata Format
        self._register_id3_format()
        
        # Vorbis Comment Format
        self._register_vorbis_format()
        
        # QuickTime Metadata Format
        self._register_quicktime_format()
        
        # Matroska Tags Format
        self._register_matroska_format()
        
        # Initialize cross-format field mappings
        self._initialize_field_mappings()
    
    def _register_exif_format(self):
        """Register EXIF metadata format"""
        exif_fields = [
            MetadataField("Camera Make", "make", MetadataType.TECHNICAL, "string", "Camera manufacturer"),
            MetadataField("Camera Model", "model", MetadataType.TECHNICAL, "string", "Camera model"),
            MetadataField("Date Taken", "datetime", MetadataType.ADMINISTRATIVE, "datetime", "Date photo was taken"),
            MetadataField("ISO Speed", "iso", MetadataType.TECHNICAL, "integer", "ISO sensitivity"),
            MetadataField("Focal Length", "focal_length", MetadataType.TECHNICAL, "float", "Lens focal length (mm)"),
            MetadataField("Aperture", "f_number", MetadataType.TECHNICAL, "float", "Lens aperture f-stop"),
            MetadataField("Shutter Speed", "exposure_time", MetadataType.TECHNICAL, "float", "Exposure time (seconds)"),
            MetadataField("Image Width", "width", MetadataType.TECHNICAL, "integer", "Image width in pixels", True),
            MetadataField("Image Height", "height", MetadataType.TECHNICAL, "integer", "Image height in pixels", True),
            MetadataField("Orientation", "orientation", MetadataType.TECHNICAL, "integer", "Image orientation", 
                         allowed_values=[1, 2, 3, 4, 5, 6, 7, 8]),
            MetadataField("Color Space", "color_space", MetadataType.TECHNICAL, "string", "Color space information"),
            MetadataField("GPS Latitude", "gps_latitude", MetadataType.DESCRIPTIVE, "float", "GPS latitude coordinates"),
            MetadataField("GPS Longitude", "gps_longitude", MetadataType.DESCRIPTIVE, "float", "GPS longitude coordinates"),
            MetadataField("Artist", "artist", MetadataType.RIGHTS, "string", "Name of image creator"),
            MetadataField("Copyright", "copyright", MetadataType.RIGHTS, "string", "Copyright information"),
            MetadataField("Software", "software", MetadataType.ADMINISTRATIVE, "string", "Software used to create image"),
            MetadataField("White Balance", "white_balance", MetadataType.TECHNICAL, "string", "White balance setting"),
            MetadataField("Flash", "flash", MetadataType.TECHNICAL, "integer", "Flash settings and mode"),
            MetadataField("Scene Type", "scene_type", MetadataType.DESCRIPTIVE, "string", "Scene capture type"),
        ]
        
        exif_format = MetadataFormat(
            name="Exchangeable Image File Format",
            standard=MetadataStandard.EXIF,
            file_types=["jpeg", "jpg", "tiff", "tif", "raw", "dng"],
            supported_fields=exif_fields,
            encoding="ascii",
            case_sensitive=False,
            supports_custom_fields=False,
            max_size=65535,  # 64KB limit
            binary_format=True,
            hierarchical=False,
            description="Standard metadata format for digital images"
        )
        
        self.formats[MetadataStandard.EXIF] = exif_format
        for field in exif_fields:
            self.field_registry[f"exif_{field.field_id}"] = field
    
    def _register_iptc_format(self):
        """Register IPTC metadata format"""
        iptc_fields = [
            MetadataField("Headline", "headline", MetadataType.DESCRIPTIVE, "string", "Brief publishable synopsis", max_length=256),
            MetadataField("Caption", "caption", MetadataType.DESCRIPTIVE, "string", "Description of image content", max_length=2000),
            MetadataField("Keywords", "keywords", MetadataType.DESCRIPTIVE, "string", "Searchable keywords"),
            MetadataField("Category", "category", MetadataType.DESCRIPTIVE, "string", "Subject category", max_length=3),
            MetadataField("Supplemental Categories", "supplemental_categories", MetadataType.DESCRIPTIVE, "string", "Additional categories"),
            MetadataField("Urgency", "urgency", MetadataType.ADMINISTRATIVE, "integer", "Editorial urgency", 
                         allowed_values=[1, 2, 3, 4, 5, 6, 7, 8, 9]),
            MetadataField("Byline", "byline", MetadataType.RIGHTS, "string", "Creator/photographer name", max_length=32),
            MetadataField("Byline Title", "byline_title", MetadataType.RIGHTS, "string", "Creator's job title", max_length=32),
            MetadataField("Credit", "credit", MetadataType.RIGHTS, "string", "Provider credit", max_length=32),
            MetadataField("Source", "source", MetadataType.RIGHTS, "string", "Original owner", max_length=32),
            MetadataField("Copyright Notice", "copyright_notice", MetadataType.RIGHTS, "string", "Copyright notice", max_length=128),
            MetadataField("City", "city", MetadataType.DESCRIPTIVE, "string", "City where created", max_length=32),
            MetadataField("Province State", "province_state", MetadataType.DESCRIPTIVE, "string", "Province/state", max_length=32),
            MetadataField("Country Name", "country_name", MetadataType.DESCRIPTIVE, "string", "Country name", max_length=64),
            MetadataField("Date Created", "date_created", MetadataType.ADMINISTRATIVE, "datetime", "Creation date"),
            MetadataField("Time Created", "time_created", MetadataType.ADMINISTRATIVE, "string", "Creation time"),
            MetadataField("Object Name", "object_name", MetadataType.DESCRIPTIVE, "string", "Title/object name", max_length=64),
            MetadataField("Special Instructions", "special_instructions", MetadataType.ADMINISTRATIVE, "string", "Usage instructions", max_length=256),
        ]
        
        iptc_format = MetadataFormat(
            name="International Press Telecommunications Council",
            standard=MetadataStandard.IPTC,
            file_types=["jpeg", "jpg", "tiff", "tif"],
            supported_fields=iptc_fields,
            encoding="utf-8",
            case_sensitive=False,
            supports_custom_fields=False,
            max_size=32768,  # 32KB typical
            binary_format=True,
            hierarchical=False,
            description="News industry standard for image metadata"
        )
        
        self.formats[MetadataStandard.IPTC] = iptc_format
        for field in iptc_fields:
            self.field_registry[f"iptc_{field.field_id}"] = field
    
    def _register_xmp_format(self):
        """Register XMP metadata format"""
        xmp_fields = [
            MetadataField("Title", "title", MetadataType.DESCRIPTIVE, "string", "Document title"),
            MetadataField("Description", "description", MetadataType.DESCRIPTIVE, "string", "Document description"),
            MetadataField("Subject", "subject", MetadataType.DESCRIPTIVE, "string", "Document subject/keywords"),
            MetadataField("Creator", "creator", MetadataType.RIGHTS, "string", "Document creator"),
            MetadataField("Rights", "rights", MetadataType.RIGHTS, "string", "Copyright and usage rights"),
            MetadataField("Create Date", "create_date", MetadataType.ADMINISTRATIVE, "datetime", "Creation date"),
            MetadataField("Modify Date", "modify_date", MetadataType.ADMINISTRATIVE, "datetime", "Last modification date"),
            MetadataField("Creator Tool", "creator_tool", MetadataType.ADMINISTRATIVE, "string", "Software/tool used"),
            MetadataField("Format", "format", MetadataType.TECHNICAL, "string", "File format/MIME type"),
            MetadataField("Document ID", "document_id", MetadataType.ADMINISTRATIVE, "string", "Unique document identifier"),
            MetadataField("Instance ID", "instance_id", MetadataType.ADMINISTRATIVE, "string", "Unique instance identifier"),
            MetadataField("Rating", "rating", MetadataType.DESCRIPTIVE, "integer", "User rating", 
                         allowed_values=[0, 1, 2, 3, 4, 5]),
            MetadataField("Label", "label", MetadataType.DESCRIPTIVE, "string", "Color label or category"),
            MetadataField("Urgency", "urgency", MetadataType.ADMINISTRATIVE, "integer", "Editorial urgency",
                         allowed_values=[1, 2, 3, 4, 5, 6, 7, 8, 9]),
            MetadataField("Instructions", "instructions", MetadataType.ADMINISTRATIVE, "string", "Special instructions"),
            MetadataField("Source", "source", MetadataType.RIGHTS, "string", "Content source"),
            MetadataField("State", "state", MetadataType.DESCRIPTIVE, "string", "Geographic state/province"),
            MetadataField("Country", "country", MetadataType.DESCRIPTIVE, "string", "Geographic country"),
        ]
        
        xmp_format = MetadataFormat(
            name="Extensible Metadata Platform",
            standard=MetadataStandard.XMP,
            file_types=["jpeg", "jpg", "png", "tiff", "pdf", "dng", "psd", "ai", "eps"],
            supported_fields=xmp_fields,
            encoding="utf-8",
            case_sensitive=True,
            supports_custom_fields=True,
            max_size=0,  # No specific limit
            binary_format=False,  # XML-based
            hierarchical=True,
            description="Adobe's extensible metadata platform"
        )
        
        self.formats[MetadataStandard.XMP] = xmp_format
        for field in xmp_fields:
            self.field_registry[f"xmp_{field.field_id}"] = field
    
    def _register_id3_format(self):
        """Register ID3 audio metadata format"""
        id3_fields = [
            MetadataField("Title", "title", MetadataType.DESCRIPTIVE, "string", "Song title", True, max_length=30),
            MetadataField("Artist", "artist", MetadataType.DESCRIPTIVE, "string", "Artist name", True, max_length=30),
            MetadataField("Album", "album", MetadataType.DESCRIPTIVE, "string", "Album name", max_length=30),
            MetadataField("Year", "year", MetadataType.DESCRIPTIVE, "integer", "Release year"),
            MetadataField("Genre", "genre", MetadataType.DESCRIPTIVE, "string", "Music genre"),
            MetadataField("Track Number", "track", MetadataType.STRUCTURAL, "integer", "Track number"),
            MetadataField("Total Tracks", "total_tracks", MetadataType.STRUCTURAL, "integer", "Total tracks on album"),
            MetadataField("Disc Number", "disc", MetadataType.STRUCTURAL, "integer", "Disc number"),
            MetadataField("Comment", "comment", MetadataType.DESCRIPTIVE, "string", "User comment", max_length=28),
            MetadataField("Composer", "composer", MetadataType.DESCRIPTIVE, "string", "Song composer"),
            MetadataField("Album Artist", "album_artist", MetadataType.DESCRIPTIVE, "string", "Album artist"),
            MetadataField("Duration", "duration", MetadataType.TECHNICAL, "integer", "Track duration (seconds)"),
            MetadataField("Bitrate", "bitrate", MetadataType.TECHNICAL, "integer", "Audio bitrate (kbps)"),
            MetadataField("Sample Rate", "sample_rate", MetadataType.TECHNICAL, "integer", "Sample rate (Hz)"),
            MetadataField("Channels", "channels", MetadataType.TECHNICAL, "integer", "Number of audio channels"),
            MetadataField("BPM", "bpm", MetadataType.DESCRIPTIVE, "integer", "Beats per minute"),
            MetadataField("ISRC", "isrc", MetadataType.RIGHTS, "string", "International Standard Recording Code", max_length=12),
            MetadataField("Publisher", "publisher", MetadataType.RIGHTS, "string", "Music publisher"),
            MetadataField("Copyright", "copyright", MetadataType.RIGHTS, "string", "Copyright information"),
        ]
        
        id3_format = MetadataFormat(
            name="ID3 Audio Metadata",
            standard=MetadataStandard.ID3,
            file_types=["mp3"],
            supported_fields=id3_fields,
            encoding="utf-8",  # ID3v2.4
            case_sensitive=False,
            supports_custom_fields=True,
            max_size=16777216,  # 16MB limit for ID3v2
            binary_format=True,
            hierarchical=False,
            description="Standard metadata format for MP3 audio files"
        )
        
        self.formats[MetadataStandard.ID3] = id3_format
        for field in id3_fields:
            self.field_registry[f"id3_{field.field_id}"] = field
    
    def _register_vorbis_format(self):
        """Register Vorbis Comment metadata format"""
        vorbis_fields = [
            MetadataField("Title", "title", MetadataType.DESCRIPTIVE, "string", "Track title", True),
            MetadataField("Artist", "artist", MetadataType.DESCRIPTIVE, "string", "Artist name", True),
            MetadataField("Album", "album", MetadataType.DESCRIPTIVE, "string", "Album name"),
            MetadataField("Date", "date", MetadataType.DESCRIPTIVE, "string", "Release date"),
            MetadataField("Genre", "genre", MetadataType.DESCRIPTIVE, "string", "Music genre"),
            MetadataField("Track Number", "tracknumber", MetadataType.STRUCTURAL, "string", "Track number"),
            MetadataField("Album Artist", "albumartist", MetadataType.DESCRIPTIVE, "string", "Album artist"),
            MetadataField("Composer", "composer", MetadataType.DESCRIPTIVE, "string", "Composer name"),
            MetadataField("Performer", "performer", MetadataType.DESCRIPTIVE, "string", "Performer name"),
            MetadataField("Comment", "comment", MetadataType.DESCRIPTIVE, "string", "User comment"),
            MetadataField("Description", "description", MetadataType.DESCRIPTIVE, "string", "Content description"),
            MetadataField("Organization", "organization", MetadataType.RIGHTS, "string", "Organization/label"),
            MetadataField("Contact", "contact", MetadataType.RIGHTS, "string", "Contact information"),
            MetadataField("License", "license", MetadataType.RIGHTS, "string", "License information"),
            MetadataField("Copyright", "copyright", MetadataType.RIGHTS, "string", "Copyright notice"),
            MetadataField("ISRC", "isrc", MetadataType.RIGHTS, "string", "International Standard Recording Code"),
        ]
        
        vorbis_format = MetadataFormat(
            name="Vorbis Comment",
            standard=MetadataStandard.VORBIS_COMMENT,
            file_types=["ogg", "oga", "flac", "opus"],
            supported_fields=vorbis_fields,
            encoding="utf-8",
            case_sensitive=False,
            supports_custom_fields=True,
            max_size=0,  # No specific limit
            binary_format=False,  # Text-based
            hierarchical=False,
            description="Flexible metadata format for Ogg-based audio"
        )
        
        self.formats[MetadataStandard.VORBIS_COMMENT] = vorbis_format
        for field in vorbis_fields:
            self.field_registry[f"vorbis_{field.field_id}"] = field
    
    def _register_quicktime_format(self):
        """Register QuickTime metadata format"""
        quicktime_fields = [
            MetadataField("Title", "title", MetadataType.DESCRIPTIVE, "string", "Media title", True),
            MetadataField("Artist", "artist", MetadataType.DESCRIPTIVE, "string", "Artist/author name"),
            MetadataField("Album", "album", MetadataType.DESCRIPTIVE, "string", "Album/collection name"),
            MetadataField("Year", "year", MetadataType.DESCRIPTIVE, "integer", "Release year"),
            MetadataField("Genre", "genre", MetadataType.DESCRIPTIVE, "string", "Content genre"),
            MetadataField("Comment", "comment", MetadataType.DESCRIPTIVE, "string", "User comment"),
            MetadataField("Track", "track", MetadataType.STRUCTURAL, "integer", "Track number"),
            MetadataField("Composer", "composer", MetadataType.DESCRIPTIVE, "string", "Composer name"),
            MetadataField("Description", "description", MetadataType.DESCRIPTIVE, "string", "Content description"),
            MetadataField("Duration", "duration", MetadataType.TECHNICAL, "float", "Media duration (seconds)", True),
            MetadataField("Creation Time", "creation_time", MetadataType.ADMINISTRATIVE, "datetime", "Creation timestamp"),
            MetadataField("Modification Time", "modification_time", MetadataType.ADMINISTRATIVE, "datetime", "Last modification"),
            MetadataField("Encoder", "encoder", MetadataType.ADMINISTRATIVE, "string", "Encoding software"),
            MetadataField("Copyright", "copyright", MetadataType.RIGHTS, "string", "Copyright information"),
            MetadataField("Language", "language", MetadataType.DESCRIPTIVE, "string", "Content language"),
            MetadataField("Location", "location", MetadataType.DESCRIPTIVE, "string", "Recording location"),
            MetadataField("Keywords", "keywords", MetadataType.DESCRIPTIVE, "string", "Content keywords"),
        ]
        
        quicktime_format = MetadataFormat(
            name="QuickTime Metadata",
            standard=MetadataStandard.QUICKTIME,
            file_types=["mov", "mp4", "m4v", "m4a"],
            supported_fields=quicktime_fields,
            encoding="utf-8",
            case_sensitive=True,
            supports_custom_fields=True,
            max_size=0,  # No specific limit
            binary_format=True,
            hierarchical=True,
            description="Apple QuickTime metadata format"
        )
        
        self.formats[MetadataStandard.QUICKTIME] = quicktime_format
        for field in quicktime_fields:
            self.field_registry[f"quicktime_{field.field_id}"] = field
    
    def _register_matroska_format(self):
        """Register Matroska Tags metadata format"""
        matroska_fields = [
            MetadataField("Title", "title", MetadataType.DESCRIPTIVE, "string", "Media title", True),
            MetadataField("Artist", "artist", MetadataType.DESCRIPTIVE, "string", "Artist name"),
            MetadataField("Album", "album", MetadataType.DESCRIPTIVE, "string", "Album name"),
            MetadataField("Date", "date_released", MetadataType.DESCRIPTIVE, "datetime", "Release date"),
            MetadataField("Genre", "genre", MetadataType.DESCRIPTIVE, "string", "Content genre"),
            MetadataField("Comment", "comment", MetadataType.DESCRIPTIVE, "string", "User comment"),
            MetadataField("Part Number", "part_number", MetadataType.STRUCTURAL, "integer", "Part/track number"),
            MetadataField("Total Parts", "total_parts", MetadataType.STRUCTURAL, "integer", "Total parts"),
            MetadataField("Director", "director", MetadataType.DESCRIPTIVE, "string", "Director name"),
            MetadataField("Encoded By", "encoded_by", MetadataType.ADMINISTRATIVE, "string", "Encoding person/tool"),
            MetadataField("Encoded Date", "date_encoded", MetadataType.ADMINISTRATIVE, "datetime", "Encoding date"),
            MetadataField("Synopsis", "synopsis", MetadataType.DESCRIPTIVE, "string", "Content synopsis"),
            MetadataField("Keywords", "keywords", MetadataType.DESCRIPTIVE, "string", "Content keywords"),
            MetadataField("Language", "language", MetadataType.DESCRIPTIVE, "string", "Content language"),
            MetadataField("Copyright", "copyright", MetadataType.RIGHTS, "string", "Copyright notice"),
            MetadataField("Production Studio", "production_studio", MetadataType.RIGHTS, "string", "Production company"),
            MetadataField("URL", "url", MetadataType.DESCRIPTIVE, "string", "Related URL"),
        ]
        
        matroska_format = MetadataFormat(
            name="Matroska Tags",
            standard=MetadataStandard.MATROSKA_TAGS,
            file_types=["mkv", "mka", "mks", "mk3d"],
            supported_fields=matroska_fields,
            encoding="utf-8",
            case_sensitive=False,
            supports_custom_fields=True,
            max_size=0,  # No specific limit
            binary_format=False,  # XML-based
            hierarchical=True,
            description="Matroska container metadata format"
        )
        
        self.formats[MetadataStandard.MATROSKA_TAGS] = matroska_format
        for field in matroska_fields:
            self.field_registry[f"matroska_{field.field_id}"] = field
    
    def _initialize_field_mappings(self):
        """Initialize cross-format field mappings"""
        # Title mappings
        self.cross_format_mappings["title"] = {
            MetadataStandard.EXIF: "object_name",
            MetadataStandard.IPTC: "object_name", 
            MetadataStandard.XMP: "title",
            MetadataStandard.ID3: "title",
            MetadataStandard.VORBIS_COMMENT: "title",
            MetadataStandard.QUICKTIME: "title",
            MetadataStandard.MATROSKA_TAGS: "title"
        }
        
        # Artist/Creator mappings
        self.cross_format_mappings["artist"] = {
            MetadataStandard.EXIF: "artist",
            MetadataStandard.IPTC: "byline",
            MetadataStandard.XMP: "creator",
            MetadataStandard.ID3: "artist",
            MetadataStandard.VORBIS_COMMENT: "artist",
            MetadataStandard.QUICKTIME: "artist",
            MetadataStandard.MATROSKA_TAGS: "artist"
        }
        
        # Copyright mappings
        self.cross_format_mappings["copyright"] = {
            MetadataStandard.EXIF: "copyright",
            MetadataStandard.IPTC: "copyright_notice",
            MetadataStandard.XMP: "rights",
            MetadataStandard.ID3: "copyright",
            MetadataStandard.VORBIS_COMMENT: "copyright",
            MetadataStandard.QUICKTIME: "copyright",
            MetadataStandard.MATROSKA_TAGS: "copyright"
        }
        
        # Date mappings
        self.cross_format_mappings["date"] = {
            MetadataStandard.EXIF: "datetime",
            MetadataStandard.IPTC: "date_created",
            MetadataStandard.XMP: "create_date",
            MetadataStandard.ID3: "year",
            MetadataStandard.VORBIS_COMMENT: "date",
            MetadataStandard.QUICKTIME: "creation_time",
            MetadataStandard.MATROSKA_TAGS: "date_released"
        }
        
        # Description mappings
        self.cross_format_mappings["description"] = {
            MetadataStandard.IPTC: "caption",
            MetadataStandard.XMP: "description",
            MetadataStandard.ID3: "comment",
            MetadataStandard.VORBIS_COMMENT: "description",
            MetadataStandard.QUICKTIME: "description",
            MetadataStandard.MATROSKA_TAGS: "synopsis"
        }
    
    def get_format(self, standard: MetadataStandard) -> Optional[MetadataFormat]:
        """Get metadata format by standard"""
        return self.formats.get(standard)
    
    def get_formats_for_file_type(self, file_type: str) -> List[MetadataFormat]:
        """Get all metadata formats supported by file type"""
        file_type = file_type.lower().lstrip('.')
        return [fmt for fmt in self.formats.values() if file_type in fmt.file_types]
    
    def get_field(self, field_key: str) -> Optional[MetadataField]:
        """Get metadata field by key"""
        return self.field_registry.get(field_key)
    
    def get_cross_format_mapping(self, field_name: str, target_standard: MetadataStandard) -> Optional[str]:
        """Get field name mapping for target format"""
        mapping = self.cross_format_mappings.get(field_name)
        return mapping.get(target_standard) if mapping else None
    
    def convert_metadata(self, 
                        source_data: Dict[str, Any], 
                        source_standard: MetadataStandard,
                        target_standard: MetadataStandard) -> Dict[str, Any]:
        """Convert metadata between formats"""
        converted = {}
        
        for field_name, value in source_data.items():
            # Try direct mapping first
            target_field = self.get_cross_format_mapping(field_name, target_standard)
            
            if target_field:
                converted[target_field] = value
            else:
                # Try to find equivalent field
                source_format = self.get_format(source_standard)
                target_format = self.get_format(target_standard)
                
                if source_format and target_format:
                    # Find field in source format
                    source_field = None
                    for field in source_format.supported_fields:
                        if field.field_id == field_name or field.name == field_name:
                            source_field = field
                            break
                    
                    if source_field:
                        # Find equivalent field in target format
                        for field in target_format.supported_fields:
                            if (field.metadata_type == source_field.metadata_type and 
                                field.data_type == source_field.data_type and
                                field.name.lower().replace(" ", "_") == source_field.name.lower().replace(" ", "_")):
                                converted[field.field_id] = value
                                break
        
        return converted
    
    def validate_metadata(self, 
                         data: Dict[str, Any], 
                         standard: MetadataStandard) -> Dict[str, Any]:
        """Validate metadata against format specification"""
        format_spec = self.get_format(standard)
        if not format_spec:
            return {"valid": False, "errors": ["Unknown metadata standard"]}
        
        errors = []
        warnings = []
        validated_data = {}
        
        # Check required fields
        required_fields = [f.field_id for f in format_spec.supported_fields if f.required]
        for field_id in required_fields:
            if field_id not in data or data[field_id] is None:
                errors.append(f"Required field '{field_id}' is missing")
        
        # Validate each field
        for field_id, value in data.items():
            field_spec = None
            for field in format_spec.supported_fields:
                if field.field_id == field_id:
                    field_spec = field
                    break
            
            if not field_spec and not format_spec.supports_custom_fields:
                warnings.append(f"Unknown field '{field_id}' not supported")
                continue
            
            if field_spec:
                # Validate data type
                valid_value = self._validate_field_value(value, field_spec)
                if valid_value is None:
                    errors.append(f"Invalid value for field '{field_id}': {value}")
                else:
                    validated_data[field_id] = valid_value
            else:
                # Custom field
                validated_data[field_id] = value
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validated_data": validated_data
        }
    
    def _validate_field_value(self, value: Any, field_spec: MetadataField) -> Any:
        """Validate individual field value"""
        if value is None:
            return field_spec.default_value
        
        # Type validation
        if field_spec.data_type == "string":
            value = str(value)
            if field_spec.max_length and len(value) > field_spec.max_length:
                return None
        elif field_spec.data_type == "integer":
            try:
                value = int(value)
            except (ValueError, TypeError):
                return None
        elif field_spec.data_type == "float":
            try:
                value = float(value)
            except (ValueError, TypeError):
                return None
        elif field_spec.data_type == "boolean":
            if isinstance(value, str):
                value = value.lower() in ["true", "1", "yes", "on"]
            else:
                value = bool(value)
        elif field_spec.data_type == "datetime":
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return None
        
        # Value constraints validation
        if field_spec.allowed_values and value not in field_spec.allowed_values:
            return None
        
        return value
    
    def extract_common_metadata(self, metadata_dict: Dict[MetadataStandard, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common metadata fields from multiple formats"""
        common_metadata = {}
        
        for common_field, format_mappings in self.cross_format_mappings.items():
            for standard, field_name in format_mappings.items():
                if standard in metadata_dict and field_name in metadata_dict[standard]:
                    common_metadata[common_field] = metadata_dict[standard][field_name]
                    break  # Use first found value
        
        return common_metadata
    
    def generate_metadata_schema(self, standard: MetadataStandard) -> Dict[str, Any]:
        """Generate JSON schema for metadata format"""
        format_spec = self.get_format(standard)
        if not format_spec:
            return {}
        
        schema = {
            "type": "object",
            "title": format_spec.name,
            "description": format_spec.description,
            "properties": {},
            "required": []
        }
        
        for field in format_spec.supported_fields:
            field_schema = {
                "title": field.name,
                "description": field.description,
                "type": self._get_json_type(field.data_type)
            }
            
            if field.max_length:
                field_schema["maxLength"] = field.max_length
            
            if field.allowed_values:
                field_schema["enum"] = field.allowed_values
            
            if field.default_value is not None:
                field_schema["default"] = field.default_value
            
            schema["properties"][field.field_id] = field_schema
            
            if field.required:
                schema["required"].append(field.field_id)
        
        return schema
    
    def _get_json_type(self, data_type: str) -> str:
        """Convert internal data type to JSON schema type"""
        type_mapping = {
            "string": "string",
            "integer": "integer", 
            "float": "number",
            "boolean": "boolean",
            "datetime": "string",
            "binary": "string"
        }
        return type_mapping.get(data_type, "string")
    
    def export_format_registry(self) -> Dict[str, Any]:
        """Export complete metadata format registry"""
        return {
            "formats": {
                standard.value: {
                    "name": fmt.name,
                    "file_types": fmt.file_types,
                    "encoding": fmt.encoding,
                    "supports_custom_fields": fmt.supports_custom_fields,
                    "binary_format": fmt.binary_format,
                    "hierarchical": fmt.hierarchical,
                    "field_count": len(fmt.supported_fields)
                }
                for standard, fmt in self.formats.items()
            },
            "cross_format_mappings": {
                field: {std.value: mapping for std, mapping in mappings.items()}
                for field, mappings in self.cross_format_mappings.items()
            },
            "total_fields": len(self.field_registry)
        }


# Global registry instance
metadata_registry = MetadataRegistry()


# Export main classes and functions
__all__ = [
    'MetadataType',
    'MetadataStandard',
    'MetadataField',
    'MetadataFormat',
    'MetadataRegistry',
    'metadata_registry'
]