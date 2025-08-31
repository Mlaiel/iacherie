"""Content Serializer Module
=========================

Specialized serialization for multimedia content data and metadata.
Optimized for audio, video, image, and text content processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
import mimetypes
from pathlib import Path
import json
import numpy as np
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Supported content types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED = "mixed"

class AudioFormat(Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"

class VideoFormat(Enum):
    """Supported video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    MKV = "mkv"

class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"

@dataclass
class AudioMetadata:
    """Audio content metadata."""
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    bitrate: int = 128
    codec: str = "mp3"
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track_number: Optional[int] = None

@dataclass
class VideoMetadata:
    """Video content metadata."""
    duration: float = 0.0
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    bitrate: int = 1000
    codec: str = "h264"
    has_audio: bool = True
    audio_codec: Optional[str] = None

@dataclass
class ImageMetadata:
    """Image content metadata."""
    width: int = 0
    height: int = 0
    channels: int = 3
    color_mode: str = "RGB"
    has_transparency: bool = False
    dpi: Optional[int] = None
    camera_model: Optional[str] = None
    taken_at: Optional[datetime] = None

@dataclass
class TextMetadata:
    """Text content metadata."""
    word_count: int = 0
    character_count: int = 0
    language: Optional[str] = None
    encoding: str = "utf-8"
    sentiment_score: Optional[float] = None
    readability_score: Optional[float] = None

class ContentData(BaseModel):
    """
    Comprehensive content data model.
    
    Represents multimedia content with metadata, fingerprints,
    and processing information for the IA-Influencer-Agent platform.
    """
    
    # Basic information
    content_id: str = Field(..., description="Unique content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    format: str = Field(..., description="Content format/extension")
    file_size: int = Field(default=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    
    # Content data
    content_data: Optional[bytes] = Field(default=None, description="Raw content data")
    content_url: Optional[str] = Field(default=None, description="Content URL if remote")
    thumbnail_data: Optional[bytes] = Field(default=None, description="Thumbnail image data")
    
    # Metadata by type
    audio_metadata: Optional[AudioMetadata] = Field(default=None)
    video_metadata: Optional[VideoMetadata] = Field(default=None)
    image_metadata: Optional[ImageMetadata] = Field(default=None)
    text_metadata: Optional[TextMetadata] = Field(default=None)
    
    # Fingerprinting and protection
    fingerprint_hash: Optional[str] = Field(default=None, description="Content fingerprint")
    similarity_vectors: Optional[List[float]] = Field(default=None, description="AI similarity vectors")
    protection_enabled: bool = Field(default=True, description="Content protection status")
    
    # Processing information
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = Field(default=None)
    last_modified: datetime = Field(default_factory=datetime.now)
    processing_status: str = Field(default="pending")
    
    # Platform information
    platform_id: Optional[str] = Field(default=None, description="Source platform")
    original_url: Optional[str] = Field(default=None, description="Original platform URL")
    platform_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Creator information
    creator_id: Optional[str] = Field(default=None)
    creator_name: Optional[str] = Field(default=None)
    creator_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content_type', pre=True)
    def validate_content_type(cls, v):
        if isinstance(v, str):
            return ContentType(v.lower())
        return v
    
    @validator('mime_type', pre=True)
    def validate_mime_type(cls, v):
        if not v or '/' not in v:
            raise ValueError("Invalid MIME type format")
        return v.lower()
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v < 0:
            raise ValueError("File size cannot be negative")
        return v

class ContentSerializer:
    """
    Advanced content serialization system.
    
    Handles efficient serialization and deserialization of multimedia content
    with optimizations for different content types and platform requirements.
    """
    
    def __init__(self):
        """Initialize content serializer."""
        self.supported_formats = {
            ContentType.AUDIO: [f.value for f in AudioFormat],
            ContentType.VIDEO: [f.value for f in VideoFormat],
            ContentType.IMAGE: [f.value for f in ImageFormat],
            ContentType.TEXT: ['txt', 'md', 'html', 'json', 'xml']
        }
        
        logger.info("Content serializer initialized")
    
    def serialize_content(
        self,
        content_data: ContentData,
        include_binary: bool = True,
        compress_binary: bool = True
    ) -> Dict[str, Any]:
        """
        Serialize content data to dictionary format.
        
        Args:
            content_data: Content data to serialize
            include_binary: Whether to include binary data
            compress_binary: Whether to compress binary data
            
        Returns:
            Serialized content dictionary
        """
        try:
            # Convert to dictionary
            data = content_data.dict()
            
            # Handle binary data serialization
            if include_binary:
                if content_data.content_data:
                    data['content_data'] = self._encode_binary_data(
                        content_data.content_data,
                        compress=compress_binary
                    )
                
                if content_data.thumbnail_data:
                    data['thumbnail_data'] = self._encode_binary_data(
                        content_data.thumbnail_data,
                        compress=compress_binary
                    )
            else:
                # Remove binary data
                data.pop('content_data', None)
                data.pop('thumbnail_data', None)
            
            # Convert datetime objects
            data['uploaded_at'] = content_data.uploaded_at.isoformat()
            data['last_modified'] = content_data.last_modified.isoformat()
            if content_data.processed_at:
                data['processed_at'] = content_data.processed_at.isoformat()
            
            # Convert metadata objects
            if content_data.audio_metadata:
                data['audio_metadata'] = self._serialize_audio_metadata(content_data.audio_metadata)
            
            if content_data.video_metadata:
                data['video_metadata'] = self._serialize_video_metadata(content_data.video_metadata)
            
            if content_data.image_metadata:
                data['image_metadata'] = self._serialize_image_metadata(content_data.image_metadata)
            
            if content_data.text_metadata:
                data['text_metadata'] = self._serialize_text_metadata(content_data.text_metadata)
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_binary': include_binary,
                'binary_compressed': compress_binary,
                'content_type': content_data.content_type.value
            }
            
            logger.debug(f"Serialized content {content_data.content_id}")
            return data
            
        except Exception as e:
            logger.error(f"Content serialization failed: {e}")
            raise
    
    def deserialize_content(
        self,
        data: Dict[str, Any],
        decode_binary: bool = True
    ) -> ContentData:
        """
        Deserialize content data from dictionary format.
        
        Args:
            data: Serialized content dictionary
            decode_binary: Whether to decode binary data
            
        Returns:
            Deserialized ContentData object
        """
        try:
            # Handle binary data deserialization
            if decode_binary:
                if 'content_data' in data and isinstance(data['content_data'], str):
                    data['content_data'] = self._decode_binary_data(data['content_data'])
                
                if 'thumbnail_data' in data and isinstance(data['thumbnail_data'], str):
                    data['thumbnail_data'] = self._decode_binary_data(data['thumbnail_data'])
            
            # Convert datetime strings
            if isinstance(data.get('uploaded_at'), str):
                data['uploaded_at'] = datetime.fromisoformat(data['uploaded_at'])
            
            if isinstance(data.get('last_modified'), str):
                data['last_modified'] = datetime.fromisoformat(data['last_modified'])
            
            if isinstance(data.get('processed_at'), str):
                data['processed_at'] = datetime.fromisoformat(data['processed_at'])
            
            # Deserialize metadata objects
            if 'audio_metadata' in data and data['audio_metadata']:
                data['audio_metadata'] = self._deserialize_audio_metadata(data['audio_metadata'])
            
            if 'video_metadata' in data and data['video_metadata']:
                data['video_metadata'] = self._deserialize_video_metadata(data['video_metadata'])
            
            if 'image_metadata' in data and data['image_metadata']:
                data['image_metadata'] = self._deserialize_image_metadata(data['image_metadata'])
            
            if 'text_metadata' in data and data['text_metadata']:
                data['text_metadata'] = self._deserialize_text_metadata(data['text_metadata'])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create ContentData object
            content_data = ContentData(**data)
            
            logger.debug(f"Deserialized content {content_data.content_id}")
            return content_data
            
        except Exception as e:
            logger.error(f"Content deserialization failed: {e}")
            raise
    
    def serialize_content_batch(
        self,
        content_list: List[ContentData],
        include_binary: bool = False
    ) -> List[Dict[str, Any]]:
        """Serialize multiple content objects efficiently."""
        try:
            serialized_list = []
            
            for content in content_list:
                serialized = self.serialize_content(
                    content,
                    include_binary=include_binary,
                    compress_binary=True
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(content_list)} content objects")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Content batch serialization failed: {e}")
            raise
    
    def deserialize_content_batch(
        self,
        data_list: List[Dict[str, Any]],
        decode_binary: bool = False
    ) -> List[ContentData]:
        """Deserialize multiple content objects efficiently."""
        try:
            content_list = []
            
            for data in data_list:
                content = self.deserialize_content(
                    data,
                    decode_binary=decode_binary
                )
                content_list.append(content)
            
            logger.info(f"Deserialized {len(data_list)} content objects")
            return content_list
            
        except Exception as e:
            logger.error(f"Content batch deserialization failed: {e}")
            raise
    
    def _encode_binary_data(self, binary_data: bytes, compress: bool = True) -> str:
        """Encode binary data to base64 string with optional compression."""
        try:
            if compress and len(binary_data) > 1024:  # Compress if > 1KB
                import gzip
                binary_data = gzip.compress(binary_data)
                encoded = base64.b64encode(binary_data).decode('utf-8')
                return f"gzip:{encoded}"
            else:
                encoded = base64.b64encode(binary_data).decode('utf-8')
                return f"raw:{encoded}"
                
        except Exception as e:
            logger.error(f"Binary data encoding failed: {e}")
            raise
    
    def _decode_binary_data(self, encoded_data: str) -> bytes:
        """Decode binary data from base64 string with decompression."""
        try:
            if encoded_data.startswith('gzip:'):
                import gzip
                encoded = encoded_data[5:]  # Remove 'gzip:' prefix
                compressed_data = base64.b64decode(encoded)
                return gzip.decompress(compressed_data)
            elif encoded_data.startswith('raw:'):
                encoded = encoded_data[4:]  # Remove 'raw:' prefix
                return base64.b64decode(encoded)
            else:
                # Legacy format without prefix
                return base64.b64decode(encoded_data)
                
        except Exception as e:
            logger.error(f"Binary data decoding failed: {e}")
            raise
    
    def _serialize_audio_metadata(self, metadata: AudioMetadata) -> Dict[str, Any]:
        """Serialize audio metadata."""
        return {
            'duration': metadata.duration,
            'sample_rate': metadata.sample_rate,
            'channels': metadata.channels,
            'bitrate': metadata.bitrate,
            'codec': metadata.codec,
            'title': metadata.title,
            'artist': metadata.artist,
            'album': metadata.album,
            'genre': metadata.genre,
            'year': metadata.year,
            'track_number': metadata.track_number
        }
    
    def _deserialize_audio_metadata(self, data: Dict[str, Any]) -> AudioMetadata:
        """Deserialize audio metadata."""
        return AudioMetadata(**data)
    
    def _serialize_video_metadata(self, metadata: VideoMetadata) -> Dict[str, Any]:
        """Serialize video metadata."""
        return {
            'duration': metadata.duration,
            'width': metadata.width,
            'height': metadata.height,
            'fps': metadata.fps,
            'bitrate': metadata.bitrate,
            'codec': metadata.codec,
            'has_audio': metadata.has_audio,
            'audio_codec': metadata.audio_codec
        }
    
    def _deserialize_video_metadata(self, data: Dict[str, Any]) -> VideoMetadata:
        """Deserialize video metadata."""
        return VideoMetadata(**data)
    
    def _serialize_image_metadata(self, metadata: ImageMetadata) -> Dict[str, Any]:
        """Serialize image metadata."""
        data = {
            'width': metadata.width,
            'height': metadata.height,
            'channels': metadata.channels,
            'color_mode': metadata.color_mode,
            'has_transparency': metadata.has_transparency,
            'dpi': metadata.dpi,
            'camera_model': metadata.camera_model
        }
        
        if metadata.taken_at:
            data['taken_at'] = metadata.taken_at.isoformat()
        
        return data
    
    def _deserialize_image_metadata(self, data: Dict[str, Any]) -> ImageMetadata:
        """Deserialize image metadata."""
        if 'taken_at' in data and isinstance(data['taken_at'], str):
            data['taken_at'] = datetime.fromisoformat(data['taken_at'])
        
        return ImageMetadata(**data)
    
    def _serialize_text_metadata(self, metadata: TextMetadata) -> Dict[str, Any]:
        """Serialize text metadata."""
        return {
            'word_count': metadata.word_count,
            'character_count': metadata.character_count,
            'language': metadata.language,
            'encoding': metadata.encoding,
            'sentiment_score': metadata.sentiment_score,
            'readability_score': metadata.readability_score
        }
    
    def _deserialize_text_metadata(self, data: Dict[str, Any]) -> TextMetadata:
        """Deserialize text metadata."""
        return TextMetadata(**data)
    
    def calculate_content_fingerprint(self, content_data: ContentData) -> str:
        """Calculate unique fingerprint for content."""
        try:
            # Create hash from key content properties
            hash_input = f"{content_data.content_id}_{content_data.file_size}_{content_data.mime_type}"
            
            if content_data.content_data:
                content_hash = hashlib.sha256(content_data.content_data).hexdigest()
                hash_input += f"_{content_hash}"
            
            fingerprint = hashlib.sha256(hash_input.encode()).hexdigest()
            
            logger.debug(f"Calculated fingerprint for {content_data.content_id}: {fingerprint[:16]}...")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint calculation failed: {e}")
            raise
    
    def validate_content_format(self, content_data: ContentData) -> bool:
        """Validate content format compatibility."""
        try:
            content_type = content_data.content_type
            format_ext = content_data.format.lower()
            
            supported = self.supported_formats.get(content_type, [])
            
            if format_ext not in supported:
                logger.warning(f"Unsupported format {format_ext} for type {content_type.value}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Content format validation failed: {e}")
            return False
    
    def get_content_summary(self, content_data: ContentData) -> Dict[str, Any]:
        """Get content summary information."""
        try:
            summary = {
                'content_id': content_data.content_id,
                'content_type': content_data.content_type.value,
                'format': content_data.format,
                'file_size': content_data.file_size,
                'uploaded_at': content_data.uploaded_at.isoformat(),
                'protection_enabled': content_data.protection_enabled,
                'processing_status': content_data.processing_status
            }
            
            # Add type-specific metadata
            if content_data.audio_metadata:
                summary['duration'] = content_data.audio_metadata.duration
                summary['artist'] = content_data.audio_metadata.artist
                summary['title'] = content_data.audio_metadata.title
            
            elif content_data.video_metadata:
                summary['duration'] = content_data.video_metadata.duration
                summary['resolution'] = f"{content_data.video_metadata.width}x{content_data.video_metadata.height}"
                summary['fps'] = content_data.video_metadata.fps
            
            elif content_data.image_metadata:
                summary['resolution'] = f"{content_data.image_metadata.width}x{content_data.image_metadata.height}"
                summary['color_mode'] = content_data.image_metadata.color_mode
            
            elif content_data.text_metadata:
                summary['word_count'] = content_data.text_metadata.word_count
                summary['language'] = content_data.text_metadata.language
            
            return summary
            
        except Exception as e:
            logger.error(f"Content summary generation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'ContentSerializer',
    'ContentData',
    'ContentType',
    'AudioFormat',
    'VideoFormat',
    'ImageFormat',
    'AudioMetadata',
    'VideoMetadata',
    'ImageMetadata',
    'TextMetadata'
]
