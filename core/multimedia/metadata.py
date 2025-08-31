"""Multimedia Metadata - Enterprise Metadata Management System

Comprehensive metadata extraction, management, and manipulation for multimedia content.
Supports advanced metadata operations, EXIF data, technical specifications, and custom fields.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import mimetypes

# Image processing and EXIF
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Video and audio metadata
try:
    from pymediainfo import MediaInfo
    MEDIAINFO_AVAILABLE = True
except ImportError:
    MEDIAINFO_AVAILABLE = False

# Advanced media info
try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# XMP metadata
try:
    from libxmp import XMPFiles, XMPMeta
    XMP_AVAILABLE = True
except ImportError:
    XMP_AVAILABLE = False

# Document metadata
try:
    import PyPDF2
    import docx
    DOCUMENT_AVAILABLE = True
except ImportError:
    DOCUMENT_AVAILABLE = False

# FFprobe for media analysis
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetadataFormat(Enum):
    """Metadata formats"""    EXIF = "exif"
    IPTC = "iptc"
    XMP = "xmp"
    ID3 = "id3"
    VORBIS = "vorbis"
    MP4 = "mp4"
    TECHNICAL = "technical"
    CUSTOM = "custom"


class MetadataCategory(Enum):
    """Metadata categories"""    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    ADMINISTRATIVE = "administrative"
    STRUCTURAL = "structural"
    PRESERVATION = "preservation"
    RIGHTS = "rights"
    GEOLOCATION = "geolocation"


@dataclass
class GeolocationData:
    """Geolocation information"""    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    gps_timestamp: Optional[datetime] = None
    location_name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None


@dataclass
class TechnicalMetadata:
    """Technical metadata"""    # File information
    file_size: int = 0
    file_format: Optional[str] = None
    mime_type: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    
    # Media dimensions
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    frame_rate: Optional[float] = None
    
    # Quality information
    bit_depth: Optional[int] = None
    color_space: Optional[str] = None
    compression: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # Camera/recording information
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_info: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso_speed: Optional[int] = None
    flash_info: Optional[str] = None
    
    # Additional technical data
    encoding: Optional[str] = None
    profile: Optional[str] = None
    level: Optional[str] = None
    pixel_aspect_ratio: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result


@dataclass
class DescriptiveMetadata:
    """Descriptive metadata"""    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    creator: Optional[str] = None
    contributor: Optional[str] = None
    publisher: Optional[str] = None
    rights: Optional[str] = None
    copyright: Optional[str] = None
    license: Optional[str] = None
    language: Optional[str] = None
    genre: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {k: v for k, v in asdict(self).items() if v is not None and v != []}


@dataclass
class AdministrativeMetadata:
    """Administrative metadata"""    file_id: Optional[str] = None
    checksum: Optional[str] = None
    ingestion_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    version: Optional[str] = None
    status: Optional[str] = None
    workflow_state: Optional[str] = None
    owner: Optional[str] = None
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        result = {}
        for key, value in asdict(self).items():
            if value is not None and value != {} and value != []:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result


@dataclass
class MultimediaMetadataSet:
    """Complete multimedia metadata set"""    file_path: str
    technical: TechnicalMetadata = field(default_factory=TechnicalMetadata)
    descriptive: DescriptiveMetadata = field(default_factory=DescriptiveMetadata)
    administrative: AdministrativeMetadata = field(default_factory=AdministrativeMetadata)
    geolocation: Optional[GeolocationData] = None
    
    # Raw metadata from various sources
    exif_data: Dict[str, Any] = field(default_factory=dict)
    iptc_data: Dict[str, Any] = field(default_factory=dict)
    xmp_data: Dict[str, Any] = field(default_factory=dict)
    id3_data: Dict[str, Any] = field(default_factory=dict)
    mediainfo_data: Dict[str, Any] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata timestamps
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "file_path": self.file_path,
            "technical": self.technical.to_dict(),
            "descriptive": self.descriptive.to_dict(),
            "administrative": self.administrative.to_dict(),
            "geolocation": asdict(self.geolocation) if self.geolocation else None,
            "exif_data": self.exif_data,
            "iptc_data": self.iptc_data,
            "xmp_data": self.xmp_data,
            "id3_data": self.id3_data,
            "mediainfo_data": self.mediainfo_data,
            "custom_metadata": self.custom_metadata,
            "extracted_at": self.extracted_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    def get_summary(self) -> Dict[str, Any]:
        """Get metadata summary"""        return {
            "title": self.descriptive.title,
            "format": self.technical.file_format,
            "size": self.technical.file_size,
            "dimensions": f"{self.technical.width}x{self.technical.height}" if self.technical.width and self.technical.height else None,
            "duration": self.technical.duration,
            "creator": self.descriptive.creator,
            "creation_date": self.technical.creation_date.isoformat() if self.technical.creation_date else None,
            "keywords_count": len(self.descriptive.keywords),
            "has_geolocation": self.geolocation is not None
        }


class MultimediaMetadata:
    """Enterprise multimedia metadata management system"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        self.extract_thumbnails = config.get("extract_thumbnails", False)
        self.max_keyword_length = config.get("max_keyword_length", 100)
        self.enable_geolocation = config.get("enable_geolocation", True)
        self.preserve_original = config.get("preserve_original", True)
        self.custom_extractors = config.get("custom_extractors", {})
        
        # Metadata cache
        self.metadata_cache: Dict[str, MultimediaMetadataSet] = {}
        self.cache_enabled = config.get("enable_cache", True)
        self.max_cache_size = config.get("max_cache_size", 1000)
        
        # Statistics
        self.extraction_stats = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "format_distribution": {},
            "average_extraction_time": 0.0
        }
        
    async def initialize(self):
        """Initialize metadata system"""        try:
            # Initialize metadata extractors
            await self._initialize_extractors()
            
            logger.info("Multimedia metadata system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize metadata system: {e}")
            raise
            
    async def extract_metadata(
        self, 
        file_path: str, 
        force_refresh: bool = False,
        extract_custom: bool = True
    ) -> MultimediaMetadataSet:
        """Extract comprehensive metadata from multimedia file"""        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(file_path)
            
            if not force_refresh and self.cache_enabled and cache_key in self.metadata_cache:
                self.extraction_stats["cache_hits"] += 1
                return self.metadata_cache[cache_key]
                
            self.extraction_stats["cache_misses"] += 1
            
            # Initialize metadata set
            metadata_set = MultimediaMetadataSet(file_path=file_path)
            
            # Extract basic file information
            await self._extract_file_info(file_path, metadata_set)
            
            # Format-specific extraction
            file_format = metadata_set.technical.file_format
            
            if file_format in ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'bmp']:
                await self._extract_image_metadata(file_path, metadata_set)
                
            elif file_format in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv']:
                await self._extract_video_metadata(file_path, metadata_set)
                
            elif file_format in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']:
                await self._extract_audio_metadata(file_path, metadata_set)
                
            elif file_format in ['pdf', 'docx', 'doc', 'txt']:
                await self._extract_document_metadata(file_path, metadata_set)
                
            # Extract geolocation if available
            if self.enable_geolocation:
                await self._extract_geolocation(metadata_set)
                
            # Extract custom metadata
            if extract_custom:
                await self._extract_custom_metadata(file_path, metadata_set)
                
            # Cache result
            if self.cache_enabled:
                await self._cache_metadata(cache_key, metadata_set)
                
            # Update statistics
            self._update_extraction_stats(start_time, True, file_format)
            
            return metadata_set
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {file_path}: {e}")
            self._update_extraction_stats(start_time, False, "unknown")
            
            # Return minimal metadata set
            metadata_set = MultimediaMetadataSet(file_path=file_path)
            await self._extract_file_info(file_path, metadata_set)
            return metadata_set
            
    async def batch_extract_metadata(
        self, 
        file_paths: List[str],
        max_concurrent: int = 5
    ) -> List[MultimediaMetadataSet]:
        """Extract metadata from multiple files in batch"""        try:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def extract_with_semaphore(file_path):
                async with semaphore:
                    return await self.extract_metadata(file_path)
                    
            tasks = [extract_with_semaphore(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            metadata_sets = []
            for result in results:
                if isinstance(result, MultimediaMetadataSet):
                    metadata_sets.append(result)
                else:
                    logger.error(f"Batch metadata extraction error: {result}")
                    
            return metadata_sets
            
        except Exception as e:
            logger.error(f"Batch metadata extraction failed: {e}")
            return []
            
    async def update_metadata(
        self, 
        file_path: str, 
        updates: Dict[str, Any],
        category: MetadataCategory = MetadataCategory.DESCRIPTIVE
    ) -> bool:
        """Update metadata for a file"""        try:
            # Get existing metadata
            metadata_set = await self.extract_metadata(file_path)
            
            # Apply updates based on category
            if category == MetadataCategory.DESCRIPTIVE:
                for key, value in updates.items():
                    if hasattr(metadata_set.descriptive, key):
                        setattr(metadata_set.descriptive, key, value)
                        
            elif category == MetadataCategory.TECHNICAL:
                for key, value in updates.items():
                    if hasattr(metadata_set.technical, key):
                        setattr(metadata_set.technical, key, value)
                        
            elif category == MetadataCategory.ADMINISTRATIVE:
                for key, value in updates.items():
                    if hasattr(metadata_set.administrative, key):
                        setattr(metadata_set.administrative, key, value)
                        
            elif category == MetadataCategory.CUSTOM:
                metadata_set.custom_metadata.update(updates)
                
            # Update timestamp
            metadata_set.updated_at = datetime.now(timezone.utc)
            
            # Write metadata back to file if supported
            await self._write_metadata_to_file(file_path, metadata_set, updates, category)
            
            # Update cache
            cache_key = self._generate_cache_key(file_path)
            if self.cache_enabled and cache_key in self.metadata_cache:
                self.metadata_cache[cache_key] = metadata_set
                
            return True
            
        except Exception as e:
            logger.error(f"Metadata update failed for {file_path}: {e}")
            return False
            
    async def search_by_metadata(
        self, 
        query: Dict[str, Any],
        file_paths: Optional[List[str]] = None
    ) -> List[MultimediaMetadataSet]:
        """Search metadata by criteria"""        try:
            results = []
            
            # If no file paths provided, search cache
            if file_paths is None:
                file_paths = list(self.metadata_cache.keys())
                
            for file_path in file_paths:
                metadata_set = await self.extract_metadata(file_path)
                
                if self._matches_query(metadata_set, query):
                    results.append(metadata_set)
                    
            return results
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []
            
    async def compare_metadata(
        self, 
        file_path1: str, 
        file_path2: str
    ) -> Dict[str, Any]:
        """Compare metadata between two files"""        try:
            metadata1 = await self.extract_metadata(file_path1)
            metadata2 = await self.extract_metadata(file_path2)
            
            comparison = {
                "file1": file_path1,
                "file2": file_path2,
                "technical_differences": self._compare_technical_metadata(metadata1.technical, metadata2.technical),
                "descriptive_differences": self._compare_descriptive_metadata(metadata1.descriptive, metadata2.descriptive),
                "similarity_score": self._calculate_similarity_score(metadata1, metadata2)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Metadata comparison failed: {e}")
            return {}
            
    async def export_metadata(
        self, 
        file_path: str, 
        export_format: str = "json",
        include_raw: bool = False
    ) -> str:
        """Export metadata to various formats"""        try:
            metadata_set = await self.extract_metadata(file_path)
            
            if export_format.lower() == "json":
                data = metadata_set.to_dict()
                if not include_raw:
                    # Remove raw metadata fields
                    for field in ['exif_data', 'iptc_data', 'xmp_data', 'id3_data', 'mediainfo_data']:
                        data.pop(field, None)
                return json.dumps(data, indent=2, default=str)
                
            elif export_format.lower() == "xml":
                return await self._export_to_xml(metadata_set, include_raw)
                
            elif export_format.lower() == "csv":
                return await self._export_to_csv(metadata_set)
                
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            logger.error(f"Metadata export failed: {e}")
            return ""
            
    async def get_metadata_stats(self) -> Dict[str, Any]:
        """Get metadata extraction statistics"""        return {
            **self.extraction_stats,
            "cache_size": len(self.metadata_cache),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Metadata system health check"""        try:
            status = "healthy"
            
            # Check available libraries
            libraries = {
                "pil": PIL_AVAILABLE,
                "mediainfo": MEDIAINFO_AVAILABLE,
                "mutagen": MUTAGEN_AVAILABLE,
                "xmp": XMP_AVAILABLE,
                "ffmpeg": FFMPEG_AVAILABLE,
                "document": DOCUMENT_AVAILABLE
            }
            
            # Check if critical libraries are missing
            if not any([PIL_AVAILABLE, MEDIAINFO_AVAILABLE, MUTAGEN_AVAILABLE]):
                status = "degraded"
                
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "libraries": libraries,
                "cache_size": len(self.metadata_cache) if self.cache_enabled else 0,
                "statistics": self.extraction_stats
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _initialize_extractors(self):
        """Initialize metadata extractors"""        # This would initialize any external metadata extraction tools
        pass
        
    async def _extract_file_info(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract basic file information"""        try:
            path_obj = Path(file_path)
            stat_info = path_obj.stat()
            
            # Technical metadata
            metadata_set.technical.file_size = stat_info.st_size
            metadata_set.technical.file_format = path_obj.suffix.lower().lstrip('.')
            metadata_set.technical.creation_date = datetime.fromtimestamp(stat_info.st_ctime, timezone.utc)
            metadata_set.technical.modification_date = datetime.fromtimestamp(stat_info.st_mtime, timezone.utc)
            
            # MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            metadata_set.technical.mime_type = mime_type
            
            # Administrative metadata
            metadata_set.administrative.file_id = self._generate_file_id(file_path)
            metadata_set.administrative.checksum = await self._calculate_checksum(file_path)
            metadata_set.administrative.ingestion_date = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Failed to extract file info: {e}")
            
    async def _extract_image_metadata(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract image-specific metadata"""        if not PIL_AVAILABLE:
            return
            
        try:
            with Image.open(file_path) as img:
                # Technical metadata
                metadata_set.technical.width, metadata_set.technical.height = img.size
                metadata_set.technical.color_space = img.mode
                
                # EXIF data
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata_set.exif_data[tag] = value
                        
                        # Map EXIF to structured metadata
                        await self._map_exif_to_metadata(tag, value, metadata_set)
                        
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            
    async def _extract_video_metadata(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract video-specific metadata"""        # Try MediaInfo first
        if MEDIAINFO_AVAILABLE:
            try:
                media_info = MediaInfo.parse(file_path)
                
                for track in media_info.tracks:
                    track_data = track.to_data()
                    metadata_set.mediainfo_data[track.track_type] = track_data
                    
                    if track.track_type == 'Video':
                        metadata_set.technical.width = track.width
                        metadata_set.technical.height = track.height
                        metadata_set.technical.frame_rate = track.frame_rate
                        metadata_set.technical.duration = track.duration / 1000 if track.duration else None
                        metadata_set.technical.bitrate = track.bit_rate
                        
                    elif track.track_type == 'Audio':
                        metadata_set.technical.sample_rate = track.sampling_rate
                        metadata_set.technical.channels = track.channel_s
                        
            except Exception as e:
                logger.error(f"MediaInfo extraction failed: {e}")
                
        # Try ffmpeg as fallback
        if FFMPEG_AVAILABLE:
            try:
                probe = ffmpeg.probe(file_path)
                metadata_set.mediainfo_data['ffmpeg'] = probe
                
                # Extract video stream info
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream:
                    metadata_set.technical.width = video_stream.get('width')
                    metadata_set.technical.height = video_stream.get('height')
                    metadata_set.technical.frame_rate = eval(video_stream.get('r_frame_rate', '0/1'))
                    
                # Extract format info
                format_info = probe.get('format', {})
                if 'duration' in format_info:
                    metadata_set.technical.duration = float(format_info['duration'])
                    
            except Exception as e:
                logger.error(f"FFmpeg probe failed: {e}")
                
    async def _extract_audio_metadata(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract audio-specific metadata"""        if MUTAGEN_AVAILABLE:
            try:
                audio_file = mutagen.File(file_path)
                
                if audio_file:
                    # Technical metadata
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        metadata_set.technical.duration = getattr(info, 'length', None)
                        metadata_set.technical.bitrate = getattr(info, 'bitrate', None)
                        metadata_set.technical.sample_rate = getattr(info, 'sample_rate', None)
                        metadata_set.technical.channels = getattr(info, 'channels', None)
                        
                    # Tags
                    for key, value in audio_file.tags.items() if audio_file.tags else []:
                        metadata_set.id3_data[key] = value
                        
                        # Map to descriptive metadata
                        await self._map_audio_tags_to_metadata(key, value, metadata_set)
                        
            except Exception as e:
                logger.error(f"Audio metadata extraction failed: {e}")
                
    async def _extract_document_metadata(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract document-specific metadata"""        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf' and DOCUMENT_AVAILABLE:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    if pdf_reader.metadata:
                        for key, value in pdf_reader.metadata.items():
                            metadata_set.custom_metadata[key] = value
                            
                        # Map to descriptive metadata
                        if '/Title' in pdf_reader.metadata:
                            metadata_set.descriptive.title = pdf_reader.metadata['/Title']
                        if '/Author' in pdf_reader.metadata:
                            metadata_set.descriptive.creator = pdf_reader.metadata['/Author']
                        if '/Subject' in pdf_reader.metadata:
                            metadata_set.descriptive.subject = pdf_reader.metadata['/Subject']
                            
            except Exception as e:
                logger.error(f"PDF metadata extraction failed: {e}")
                
        elif file_ext in ['.docx', '.doc'] and DOCUMENT_AVAILABLE:
            try:
                doc = docx.Document(file_path)
                
                core_props = doc.core_properties
                if core_props.title:
                    metadata_set.descriptive.title = core_props.title
                if core_props.author:
                    metadata_set.descriptive.creator = core_props.author
                if core_props.subject:
                    metadata_set.descriptive.subject = core_props.subject
                if core_props.keywords:
                    metadata_set.descriptive.keywords = core_props.keywords.split(',')
                    
            except Exception as e:
                logger.error(f"Document metadata extraction failed: {e}")
                
    async def _extract_geolocation(self, metadata_set: MultimediaMetadataSet):
        """Extract geolocation data from EXIF GPS tags"""        try:
            gps_info = metadata_set.exif_data.get('GPSInfo')
            if not gps_info:
                return
                
            geolocation = GeolocationData()
            
            # Extract latitude
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                lat = self._convert_gps_coordinate(gps_info['GPSLatitude'])
                if gps_info['GPSLatitudeRef'] == 'S':
                    lat = -lat
                geolocation.latitude = lat
                
            # Extract longitude
            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                lon = self._convert_gps_coordinate(gps_info['GPSLongitude'])
                if gps_info['GPSLongitudeRef'] == 'W':
                    lon = -lon
                geolocation.longitude = lon
                
            # Extract altitude
            if 'GPSAltitude' in gps_info:
                altitude = float(gps_info['GPSAltitude'])
                if gps_info.get('GPSAltitudeRef') == 1:
                    altitude = -altitude
                geolocation.altitude = altitude
                
            # Extract GPS timestamp
            if 'GPSTimeStamp' in gps_info and 'GPSDateStamp' in gps_info:
                time_stamp = gps_info['GPSTimeStamp']
                date_stamp = gps_info['GPSDateStamp']
                try:
                    dt_str = f"{date_stamp} {time_stamp[0]:02d}:{time_stamp[1]:02d}:{time_stamp[2]:02d}"
                    geolocation.gps_timestamp = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                except:
                    pass
                    
            if geolocation.latitude is not None and geolocation.longitude is not None:
                metadata_set.geolocation = geolocation
                
        except Exception as e:
            logger.error(f"Geolocation extraction failed: {e}")
            
    async def _extract_custom_metadata(self, file_path: str, metadata_set: MultimediaMetadataSet):
        """Extract custom metadata using configured extractors"""        try:
            for extractor_name, extractor_config in self.custom_extractors.items():
                # This would implement custom metadata extraction logic
                # based on the extractor configuration
                pass
                
        except Exception as e:
            logger.error(f"Custom metadata extraction failed: {e}")
            
    async def _map_exif_to_metadata(self, tag: str, value: Any, metadata_set: MultimediaMetadataSet):
        """Map EXIF tags to structured metadata"""        try:
            if tag == 'Make':
                metadata_set.technical.camera_make = str(value)
            elif tag == 'Model':
                metadata_set.technical.camera_model = str(value)
            elif tag == 'LensInfo' or tag == 'LensModel':
                metadata_set.technical.lens_info = str(value)
            elif tag == 'FocalLength':
                metadata_set.technical.focal_length = float(value)
            elif tag == 'FNumber':
                metadata_set.technical.aperture = float(value)
            elif tag == 'ExposureTime':
                metadata_set.technical.shutter_speed = str(value)
            elif tag == 'ISOSpeedRatings':
                metadata_set.technical.iso_speed = int(value)
            elif tag == 'Flash':
                metadata_set.technical.flash_info = str(value)
            elif tag == 'ImageDescription':
                metadata_set.descriptive.description = str(value)
            elif tag == 'Artist':
                metadata_set.descriptive.creator = str(value)
            elif tag == 'Copyright':
                metadata_set.descriptive.copyright = str(value)
            elif tag == 'Software':
                metadata_set.technical.encoding = str(value)
                
        except Exception as e:
            logger.error(f"EXIF mapping failed for {tag}: {e}")
            
    async def _map_audio_tags_to_metadata(self, key: str, value: Any, metadata_set: MultimediaMetadataSet):
        """Map audio tags to structured metadata"""        try:
            key_lower = key.lower()
            
            if 'title' in key_lower:
                metadata_set.descriptive.title = str(value[0]) if isinstance(value, list) else str(value)
            elif 'artist' in key_lower:
                metadata_set.descriptive.creator = str(value[0]) if isinstance(value, list) else str(value)
            elif 'album' in key_lower:
                metadata_set.descriptive.subject = str(value[0]) if isinstance(value, list) else str(value)
            elif 'genre' in key_lower:
                metadata_set.descriptive.genre = str(value[0]) if isinstance(value, list) else str(value)
            elif 'date' in key_lower or 'year' in key_lower:
                try:
                    year_str = str(value[0]) if isinstance(value, list) else str(value)
                    metadata_set.technical.creation_date = datetime.strptime(year_str[:4], "%Y")
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Audio tag mapping failed for {key}: {e}")
            
    async def _write_metadata_to_file(
        self, 
        file_path: str, 
        metadata_set: MultimediaMetadataSet, 
        updates: Dict[str, Any],
        category: MetadataCategory
    ):
        """Write metadata back to file (if supported)"""        try:
            file_format = metadata_set.technical.file_format
            
            # Image files with EXIF support
            if file_format in ['jpg', 'jpeg', 'tiff'] and PIL_AVAILABLE:
                await self._write_image_metadata(file_path, metadata_set, updates, category)
                
            # Audio files with tag support
            elif file_format in ['mp3', 'flac', 'm4a'] and MUTAGEN_AVAILABLE:
                await self._write_audio_metadata(file_path, metadata_set, updates, category)
                
            # Note: Writing metadata to video files is more complex and often requires specialized tools
            
        except Exception as e:
            logger.error(f"Metadata writing failed: {e}")
            
    async def _write_image_metadata(
        self, 
        file_path: str, 
        metadata_set: MultimediaMetadataSet, 
        updates: Dict[str, Any],
        category: MetadataCategory
    ):
        """Write metadata to image files"""        # This is a simplified implementation
        # In production, you would use more sophisticated metadata writing
        pass
        
    async def _write_audio_metadata(
        self, 
        file_path: str, 
        metadata_set: MultimediaMetadataSet, 
        updates: Dict[str, Any],
        category: MetadataCategory
    ):
        """Write metadata to audio files"""        # This is a simplified implementation
        # In production, you would use mutagen to write tags
        pass
        
    def _convert_gps_coordinate(self, coord_tuple: Tuple) -> float:
        """Convert GPS coordinate tuple to decimal degrees"""        degrees, minutes, seconds = coord_tuple
        return float(degrees) + float(minutes)/60 + float(seconds)/3600
        
    def _generate_cache_key(self, file_path: str) -> str:
        """Generate cache key for metadata"""        try:
            stat_info = Path(file_path).stat()
            key_string = f"{file_path}_{stat_info.st_mtime}_{stat_info.st_size}"
            return hashlib.md5(key_string.encode()).hexdigest()
        except:
            return hashlib.md5(file_path.encode()).hexdigest()
            
    def _generate_file_id(self, file_path: str) -> str:
        """Generate unique file ID"""        return hashlib.sha256(file_path.encode()).hexdigest()
        
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""
            
    async def _cache_metadata(self, cache_key: str, metadata_set: MultimediaMetadataSet):
        """Cache metadata set"""        if len(self.metadata_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.metadata_cache))
            del self.metadata_cache[oldest_key]
            
        self.metadata_cache[cache_key] = metadata_set
        
    def _matches_query(self, metadata_set: MultimediaMetadataSet, query: Dict[str, Any]) -> bool:
        """Check if metadata matches search query"""        try:
            for key, value in query.items():
                if key == 'format':
                    if metadata_set.technical.file_format != value:
                        return False
                elif key == 'creator':
                    if metadata_set.descriptive.creator != value:
                        return False
                elif key == 'keywords':
                    if not any(keyword in metadata_set.descriptive.keywords for keyword in value):
                        return False
                elif key == 'min_size':
                    if metadata_set.technical.file_size < value:
                        return False
                elif key == 'max_size':
                    if metadata_set.technical.file_size > value:
                        return False
                # Add more query criteria as needed
                
            return True
            
        except Exception as e:
            logger.error(f"Query matching failed: {e}")
            return False
            
    def _compare_technical_metadata(self, meta1: TechnicalMetadata, meta2: TechnicalMetadata) -> Dict[str, Any]:
        """Compare technical metadata between two files"""        differences = {}
        
        for field in ['width', 'height', 'duration', 'bitrate', 'file_size', 'file_format']:
            value1 = getattr(meta1, field)
            value2 = getattr(meta2, field)
            
            if value1 != value2:
                differences[field] = {"file1": value1, "file2": value2}
                
        return differences
        
    def _compare_descriptive_metadata(self, meta1: DescriptiveMetadata, meta2: DescriptiveMetadata) -> Dict[str, Any]:
        """Compare descriptive metadata between two files"""        differences = {}
        
        for field in ['title', 'creator', 'description', 'keywords', 'tags']:
            value1 = getattr(meta1, field)
            value2 = getattr(meta2, field)
            
            if value1 != value2:
                differences[field] = {"file1": value1, "file2": value2}
                
        return differences
        
    def _calculate_similarity_score(self, meta1: MultimediaMetadataSet, meta2: MultimediaMetadataSet) -> float:
        """Calculate similarity score between two metadata sets"""        score = 0.0
        total_checks = 0
        
        # Format similarity
        if meta1.technical.file_format == meta2.technical.file_format:
            score += 1.0
        total_checks += 1
        
        # Keyword similarity
        keywords1 = set(meta1.descriptive.keywords)
        keywords2 = set(meta2.descriptive.keywords)
        
        if keywords1 or keywords2:
            keyword_sim = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
            score += keyword_sim
        total_checks += 1
        
        # Creator similarity
        if meta1.descriptive.creator and meta2.descriptive.creator:
            if meta1.descriptive.creator == meta2.descriptive.creator:
                score += 1.0
            total_checks += 1
            
        # Technical similarity (resolution, duration, etc.)
        tech_score = 0.0
        tech_checks = 0
        
        if meta1.technical.width and meta2.technical.width:
            ratio = min(meta1.technical.width, meta2.technical.width) / max(meta1.technical.width, meta2.technical.width)
            tech_score += ratio
            tech_checks += 1
            
        if meta1.technical.duration and meta2.technical.duration:
            ratio = min(meta1.technical.duration, meta2.technical.duration) / max(meta1.technical.duration, meta2.technical.duration)
            tech_score += ratio
            tech_checks += 1
            
        if tech_checks > 0:
            score += tech_score / tech_checks
            total_checks += 1
            
        return score / total_checks if total_checks > 0 else 0.0
        
    async def _export_to_xml(self, metadata_set: MultimediaMetadataSet, include_raw: bool) -> str:
        """Export metadata to XML format"""        # This would implement XML export
        # For now, return empty string
        return ""
        
    async def _export_to_csv(self, metadata_set: MultimediaMetadataSet) -> str:
        """Export metadata to CSV format"""        # This would implement CSV export
        # For now, return empty string
        return ""
        
    def _update_extraction_stats(self, start_time: datetime, success: bool, file_format: str):
        """Update extraction statistics"""        self.extraction_stats["total_extractions"] += 1
        
        if success:
            self.extraction_stats["successful_extractions"] += 1
        else:
            self.extraction_stats["failed_extractions"] += 1
            
        # Update format distribution
        if file_format not in self.extraction_stats["format_distribution"]:
            self.extraction_stats["format_distribution"][file_format] = 0
        self.extraction_stats["format_distribution"][file_format] += 1
        
        # Update average extraction time
        extraction_time = (datetime.now() - start_time).total_seconds()
        total_extractions = self.extraction_stats["total_extractions"]
        current_avg = self.extraction_stats["average_extraction_time"]
        new_avg = ((current_avg * (total_extractions - 1)) + extraction_time) / total_extractions
        self.extraction_stats["average_extraction_time"] = new_avg
