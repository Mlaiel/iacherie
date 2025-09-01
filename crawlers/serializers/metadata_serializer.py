"""Metadata Serializer Module
==========================

Specialized serialization for metadata extraction and processing.
Optimized for content metadata, EXIF data, and technical specifications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pathlib import Path
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class MetadataType(Enum):
    """
Types of metadata."""

    EXIF = "exif"
    TECHNICAL = "technical"
    DESCRIPTIVE = "descriptive"
    STRUCTURAL = "structural"
    PRESERVATION = "preservation"
    RIGHTS = "rights"
    PROVENANCE = "provenance"
    CUSTOM = "custom"

class DataFormat(Enum):
    """Data format types."""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    BINARY = "binary"

@dataclass
class TechnicalMetadata:
    """Technical metadata for digital content."""
    file_size: int = 0
    file_format: str = ""
    mime_type: str = ""
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    compression: Optional[str] = None
    checksum: Optional[str] = None
    creation_tool: Optional[str] = None
    creation_tool_version: Optional[str] = None

@dataclass
class ExifMetadata:
    """EXIF metadata for images and videos."""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso_speed: Optional[int] = None
    flash: Optional[bool] = None
    orientation: Optional[int] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None
    datetime_original: Optional[datetime] = None
    software: Optional[str] = None
    copyright: Optional[str] = None

@dataclass
class AudioMetadata:
    """
Audio-specific metadata."""
    duration: float = 0.0
    channels: int = 2
    sample_rate: int = 44100
    bit_depth: int = 16
    bitrate: int = 128
    codec: str = "mp3"
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None
    album_artist: Optional[str] = None
    composer: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None

@dataclass
class VideoMetadata:
    """Video-specific metadata."""
    duration: float = 0.0
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    aspect_ratio: Optional[str] = None
    video_codec: str = "h264"
    video_bitrate: Optional[int] = None
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    audio_channels: int = 2
    color_space: Optional[str] = None
    pixel_format: Optional[str] = None
    has_subtitles: bool = False
    subtitle_languages: List[str] = field(default_factory=list)
    chapters: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ImageMetadata:
    """Image-specific metadata."""
    width: int = 0
    height: int = 0
    color_depth: int = 24
    color_space: str = "RGB"
    has_transparency: bool = False
    compression: Optional[str] = None
    resolution_x: Optional[int] = None
    resolution_y: Optional[int] = None
    resolution_unit: Optional[str] = None
    color_profile: Optional[str] = None
    histogram: Optional[List[int]] = None
    dominant_colors: List[str] = field(default_factory=list)

@dataclass
class RightsMetadata:
    """Rights and ownership metadata."""
    copyright: Optional[str] = None
    license: Optional[str] = None
    rights_holder: Optional[str] = None
    usage_terms: Optional[str] = None
    attribution_required: bool = False
    commercial_use_allowed: bool = False
    modification_allowed: bool = False
    distribution_allowed: bool = False
    license_url: Optional[str] = None
    rights_statement: Optional[str] = None

class MetadataData(BaseModel):
    """
    Comprehensive metadata model.
    
    Represents extracted metadata from multimedia content
    for the IA-Influencer-Agent content protection platform.
    """
    
    # Basic information
    metadata_id: str = Field(..., description="Unique metadata identifier")
    content_id: str = Field(..., description="Associated content identifier")
    metadata_type: MetadataType = Field(default=MetadataType.TECHNICAL)
    data_format: DataFormat = Field(..., description="Content data format")
    
    # Technical metadata
    technical: Optional[TechnicalMetadata] = Field(default=None)
    exif: Optional[ExifMetadata] = Field(default=None)
    audio: Optional[AudioMetadata] = Field(default=None)
    video: Optional[VideoMetadata] = Field(default=None)
    image: Optional[ImageMetadata] = Field(default=None)
    rights: Optional[RightsMetadata] = Field(default=None)
    
    # Descriptive metadata
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    keywords: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    language: Optional[str] = Field(default=None)
    
    # Structural metadata
    file_structure: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    
    # Provenance metadata
    source_url: Optional[str] = Field(default=None)
    extraction_method: str = Field(default="automated")
    extraction_tools: List[str] = Field(default_factory=list)
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Quality metrics
    metadata_quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    accuracy_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Processing information
    extracted_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    extraction_duration: Optional[float] = Field(default=None)
    
    # Custom metadata
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    platform_specific: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('metadata_type', pre=True)
    def validate_metadata_type(cls, v):
        if isinstance(v, str):
            return MetadataType(v.lower())
        return v
    
    @validator('data_format', pre=True)
    def validate_data_format(cls, v):
        if isinstance(v, str):
            return DataFormat(v.lower())
        return v

class MetadataSerializer:
    """
    Advanced metadata serialization system.
    
    Handles efficient serialization and deserialization of metadata
    with support for various formats and extraction methods.
    """
    
    def __init__(self):
        """
Initialize metadata serializer."""
        self.supported_formats = {
            DataFormat.AUDIO: ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
            DataFormat.VIDEO: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'],
            DataFormat.IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
            DataFormat.TEXT: ['txt', 'md', 'html', 'xml', 'json'],
            DataFormat.DOCUMENT: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
        }
        
        logger.info("Metadata serializer initialized")
    
    def serialize_metadata(
        self,
        metadata: MetadataData,
        include_binary: bool = False,
        compress_large_fields: bool = True
    ) -> Dict[str, Any]:
        """
        Serialize metadata to dictionary format.
        
        Args:
            metadata: Metadata to serialize
            include_binary: Whether to include binary data
            compress_large_fields: Whether to compress large text fields
            
        Returns:
            Serialized metadata dictionary
        """
        try:
            # Convert to dictionary
            data = metadata.dict()
            
            # Handle datetime conversions
            data['extracted_at'] = metadata.extracted_at.isoformat()
            data['last_updated'] = metadata.last_updated.isoformat()
            
            # Serialize complex metadata objects
            if metadata.technical:
                data['technical'] = self._serialize_technical_metadata(metadata.technical)
            
            if metadata.exif:
                data['exif'] = self._serialize_exif_metadata(metadata.exif)
            
            if metadata.audio:
                data['audio'] = self._serialize_audio_metadata(metadata.audio)
            
            if metadata.video:
                data['video'] = self._serialize_video_metadata(metadata.video)
            
            if metadata.image:
                data['image'] = self._serialize_image_metadata(metadata.image)
            
            if metadata.rights:
                data['rights'] = self._serialize_rights_metadata(metadata.rights)
            
            # Convert enums
            data['metadata_type'] = metadata.metadata_type.value
            data['data_format'] = metadata.data_format.value
            
            # Handle large text fields compression
            if compress_large_fields:
                for field in ['description', 'file_structure']:
                    if field in data and isinstance(data[field], str) and len(data[field]) > 1024:
                        data[field] = self._compress_text_field(data[field])
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_binary': include_binary,
                'compressed': compress_large_fields,
                'data_format': metadata.data_format.value
            }
            
            logger.debug(f"Serialized metadata {metadata.metadata_id}")
            return data
            
        except Exception as e:
            logger.error(f"Metadata serialization failed: {e}")
            raise
    
    def deserialize_metadata(
        self,
        data: Dict[str, Any]
    ) -> MetadataData:
        """
        Deserialize metadata from dictionary format.
        
        Args:
            data: Serialized metadata dictionary
            
        Returns:
            Deserialized MetadataData object
        """
        try:
            # Handle datetime conversions
            if isinstance(data.get('extracted_at'), str):
                data['extracted_at'] = datetime.fromisoformat(data['extracted_at'])
            
            if isinstance(data.get('last_updated'), str):
                data['last_updated'] = datetime.fromisoformat(data['last_updated'])
            
            # Deserialize complex metadata objects
            if 'technical' in data and data['technical']:
                data['technical'] = self._deserialize_technical_metadata(data['technical'])
            
            if 'exif' in data and data['exif']:
                data['exif'] = self._deserialize_exif_metadata(data['exif'])
            
            if 'audio' in data and data['audio']:
                data['audio'] = self._deserialize_audio_metadata(data['audio'])
            
            if 'video' in data and data['video']:
                data['video'] = self._deserialize_video_metadata(data['video'])
            
            if 'image' in data and data['image']:
                data['image'] = self._deserialize_image_metadata(data['image'])
            
            if 'rights' in data and data['rights']:
                data['rights'] = self._deserialize_rights_metadata(data['rights'])
            
            # Handle compressed text fields
            serialization_info = data.get('_serialization', {})
            if serialization_info.get('compressed', False):
                for field in ['description', 'file_structure']:
                    if field in data and isinstance(data[field], str) and data[field].startswith('compressed:'):
                        data[field] = self._decompress_text_field(data[field])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create MetadataData object
            metadata = MetadataData(**data)
            
            logger.debug(f"Deserialized metadata {metadata.metadata_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata deserialization failed: {e}")
            raise
    
    def serialize_metadata_batch(
        self,
        metadata_list: List[MetadataData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple metadata objects efficiently."""
        try:
            serialized_list = []
            
            for metadata in metadata_list:
                serialized = self.serialize_metadata(
                    metadata,
                    include_binary=not compact_mode,
                    compress_large_fields=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(metadata_list)} metadata objects")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Metadata batch serialization failed: {e}")
            raise
    
    def deserialize_metadata_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[MetadataData]:
        """Deserialize multiple metadata objects efficiently."""
        try:
            metadata_list = []
            
            for data in data_list:
                metadata = self.deserialize_metadata(data)
                metadata_list.append(metadata)
            
            logger.info(f"Deserialized {len(data_list)} metadata objects")
            return metadata_list
            
        except Exception as e:
            logger.error(f"Metadata batch deserialization failed: {e}")
            raise
    
    def _serialize_technical_metadata(self, tech: TechnicalMetadata) -> Dict[str, Any]:
        """Serialize technical metadata."""
        return {
            'file_size': tech.file_size,
            'file_format': tech.file_format,
            'mime_type': tech.mime_type,
            'codec': tech.codec,
            'bitrate': tech.bitrate,
            'sample_rate': tech.sample_rate,
            'bit_depth': tech.bit_depth,
            'compression': tech.compression,
            'checksum': tech.checksum,
            'creation_tool': tech.creation_tool,
            'creation_tool_version': tech.creation_tool_version
        }
    
    def _deserialize_technical_metadata(self, data: Dict[str, Any]) -> TechnicalMetadata:
        """
Deserialize technical metadata."""
        return TechnicalMetadata(**data)
    
    def _serialize_exif_metadata(self, exif: ExifMetadata) -> Dict[str, Any]:
        """
Serialize EXIF metadata."""
        data = {
            'camera_make': exif.camera_make,
            'camera_model': exif.camera_model,
            'lens_model': exif.lens_model,
            'focal_length': exif.focal_length,
            'aperture': exif.aperture,
            'shutter_speed': exif.shutter_speed,
            'iso_speed': exif.iso_speed,
            'flash': exif.flash,
            'orientation': exif.orientation,
            'gps_latitude': exif.gps_latitude,
            'gps_longitude': exif.gps_longitude,
            'gps_altitude': exif.gps_altitude,
            'software': exif.software,
            'copyright': exif.copyright
        }
        
        if exif.datetime_original:
            data['datetime_original'] = exif.datetime_original.isoformat()
        
        return data
    
    def _deserialize_exif_metadata(self, data: Dict[str, Any]) -> ExifMetadata:
        """
Deserialize EXIF metadata."""
        if 'datetime_original' in data and isinstance(data['datetime_original'], str):
            data['datetime_original'] = datetime.fromisoformat(data['datetime_original'])
        
        return ExifMetadata(**data)
    
    def _serialize_audio_metadata(self, audio: AudioMetadata) -> Dict[str, Any]:
        """
Serialize audio metadata."""
        return {
            'duration': audio.duration,
            'channels': audio.channels,
            'sample_rate': audio.sample_rate,
            'bit_depth': audio.bit_depth,
            'bitrate': audio.bitrate,
            'codec': audio.codec,
            'title': audio.title,
            'artist': audio.artist,
            'album': audio.album,
            'genre': audio.genre,
            'year': audio.year,
            'track_number': audio.track_number,
            'album_artist': audio.album_artist,
            'composer': audio.composer,
            'bpm': audio.bpm,
            'key': audio.key,
            'energy': audio.energy,
            'danceability': audio.danceability,
            'valence': audio.valence,
            'acousticness': audio.acousticness,
            'instrumentalness': audio.instrumentalness,
            'liveness': audio.liveness,
            'speechiness': audio.speechiness
        }
    
    def _deserialize_audio_metadata(self, data: Dict[str, Any]) -> AudioMetadata:
        """
Deserialize audio metadata."""
        return AudioMetadata(**data)
    
    def _serialize_video_metadata(self, video: VideoMetadata) -> Dict[str, Any]:
        """
Serialize video metadata."""
        return {
            'duration': video.duration,
            'width': video.width,
            'height': video.height,
            'fps': video.fps,
            'aspect_ratio': video.aspect_ratio,
            'video_codec': video.video_codec,
            'video_bitrate': video.video_bitrate,
            'audio_codec': video.audio_codec,
            'audio_bitrate': video.audio_bitrate,
            'audio_channels': video.audio_channels,
            'color_space': video.color_space,
            'pixel_format': video.pixel_format,
            'has_subtitles': video.has_subtitles,
            'subtitle_languages': video.subtitle_languages,
            'chapters': video.chapters
        }
    
    def _deserialize_video_metadata(self, data: Dict[str, Any]) -> VideoMetadata:
        """
Deserialize video metadata."""
        return VideoMetadata(**data)
    
    def _serialize_image_metadata(self, image: ImageMetadata) -> Dict[str, Any]:
        """
Serialize image metadata."""
        return {
            'width': image.width,
            'height': image.height,
            'color_depth': image.color_depth,
            'color_space': image.color_space,
            'has_transparency': image.has_transparency,
            'compression': image.compression,
            'resolution_x': image.resolution_x,
            'resolution_y': image.resolution_y,
            'resolution_unit': image.resolution_unit,
            'color_profile': image.color_profile,
            'histogram': image.histogram,
            'dominant_colors': image.dominant_colors
        }
    
    def _deserialize_image_metadata(self, data: Dict[str, Any]) -> ImageMetadata:
        """
Deserialize image metadata."""
        return ImageMetadata(**data)
    
    def _serialize_rights_metadata(self, rights: RightsMetadata) -> Dict[str, Any]:
        """
Serialize rights metadata."""
        return {
            'copyright': rights.copyright,
            'license': rights.license,
            'rights_holder': rights.rights_holder,
            'usage_terms': rights.usage_terms,
            'attribution_required': rights.attribution_required,
            'commercial_use_allowed': rights.commercial_use_allowed,
            'modification_allowed': rights.modification_allowed,
            'distribution_allowed': rights.distribution_allowed,
            'license_url': rights.license_url,
            'rights_statement': rights.rights_statement
        }
    
    def _deserialize_rights_metadata(self, data: Dict[str, Any]) -> RightsMetadata:
        """
Deserialize rights metadata."""
        return RightsMetadata(**data)
    
    def _compress_text_field(self, text: str) -> str:
        """
Compress large text field."""
        try:
            import gzip
            import base64
            
            compressed = gzip.compress(text.encode('utf-8'))
            encoded = base64.b64encode(compressed).decode('utf-8')
            return f"compressed:{encoded}"
        except Exception:
            return text  # Return original if compression fails
    
    def _decompress_text_field(self, compressed_text: str) -> str:
        """Decompress compressed text field."""
        try:
            import gzip
            import base64
            
            if compressed_text.startswith('compressed:'):
                encoded = compressed_text[11:]  # Remove 'compressed:' prefix
                compressed = base64.b64decode(encoded)
                return gzip.decompress(compressed).decode('utf-8')
            else:
                return compressed_text  # Not compressed
        except Exception:
            return compressed_text  # Return as-is if decompression fails
    
    def calculate_metadata_quality_score(self, metadata: MetadataData) -> float:
        """
Calculate quality score for metadata completeness."""
        try:
            total_fields = 0
            filled_fields = 0
            
            # Check basic fields
            basic_fields = ['title', 'description', 'language']
            for field in basic_fields:
                total_fields += 1
                if getattr(metadata, field):
                    filled_fields += 1
            
            # Check format-specific metadata
            if metadata.data_format == DataFormat.AUDIO and metadata.audio:
                audio_fields = ['title', 'artist', 'album', 'genre', 'duration']
                for field in audio_fields:
                    total_fields += 1
                    if getattr(metadata.audio, field):
                        filled_fields += 1
            
            elif metadata.data_format == DataFormat.VIDEO and metadata.video:
                video_fields = ['duration', 'width', 'height', 'video_codec']
                for field in video_fields:
                    total_fields += 1
                    if getattr(metadata.video, field):
                        filled_fields += 1
            
            elif metadata.data_format == DataFormat.IMAGE and metadata.image:
                image_fields = ['width', 'height', 'color_space']
                for field in image_fields:
                    total_fields += 1
                    if getattr(metadata.image, field):
                        filled_fields += 1
            
            # Check technical metadata
            if metadata.technical:
                tech_fields = ['file_size', 'file_format', 'mime_type']
                for field in tech_fields:
                    total_fields += 1
                    if getattr(metadata.technical, field):
                        filled_fields += 1
            
            return filled_fields / max(total_fields, 1)
            
        except Exception as e:
            logger.error(f"Metadata quality score calculation failed: {e}")
            return 0.0
    
    def extract_metadata_summary(self, metadata: MetadataData) -> Dict[str, Any]:
        """Extract summary information from metadata."""
        try:
            summary = {
                'metadata_id': metadata.metadata_id,
                'content_id': metadata.content_id,
                'data_format': metadata.data_format.value,
                'metadata_type': metadata.metadata_type.value,
                'title': metadata.title,
                'description': metadata.description[:200] if metadata.description else None,
                'keywords_count': len(metadata.keywords),
                'tags_count': len(metadata.tags),
                'quality_score': self.calculate_metadata_quality_score(metadata),
                'extracted_at': metadata.extracted_at.isoformat()
            }
            
            # Add format-specific summary
            if metadata.data_format == DataFormat.AUDIO and metadata.audio:
                summary.update({
                    'duration': metadata.audio.duration,
                    'artist': metadata.audio.artist,
                    'album': metadata.audio.album,
                    'genre': metadata.audio.genre
                })
            
            elif metadata.data_format == DataFormat.VIDEO and metadata.video:
                summary.update({
                    'duration': metadata.video.duration,
                    'resolution': f"{metadata.video.width}x{metadata.video.height}",
                    'fps': metadata.video.fps,
                    'codec': metadata.video.video_codec
                })
            
            elif metadata.data_format == DataFormat.IMAGE and metadata.image:
                summary.update({
                    'resolution': f"{metadata.image.width}x{metadata.image.height}",
                    'color_space': metadata.image.color_space,
                    'has_transparency': metadata.image.has_transparency
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Metadata summary extraction failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'MetadataSerializer',
    'MetadataData',
    'MetadataType',
    'DataFormat',
    'TechnicalMetadata',
    'ExifMetadata',
    'AudioMetadata',
    'VideoMetadata',
    'ImageMetadata',
    'RightsMetadata'
]
