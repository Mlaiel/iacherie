"""Content Management Schemas

Comprehensive Pydantic schemas for content fingerprinting, metadata management, 
and content versioning in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt, PositiveFloat


class ContentTypeEnum(str, Enum):
    """Supported content types for fingerprinting"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"


class ContentStatusEnum(str, Enum):
    """Content processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    VERIFIED = "verified"


class FingerprintAlgorithmEnum(str, Enum):
    """Fingerprinting algorithms available"""    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    OPENCV_PHASH = "opencv_phash"
    CLIP_EMBEDDING = "clip_embedding"
    BERT_EMBEDDING = "bert_embedding"
    WAVELET_HASH = "wavelet_hash"
    SPECTRAL_HASH = "spectral_hash"


class ContentQualityEnum(str, Enum):
    """Content quality classifications"""    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PROFESSIONAL = "professional"
    STUDIO = "studio"
    AMATEUR = "amateur"


class AudioMetadataSchema(BaseModel):
    """Audio-specific metadata schema"""    duration_seconds: PositiveFloat = Field(..., description="Audio duration in seconds")
    sample_rate: PositiveInt = Field(..., description="Sample rate in Hz")
    bit_rate: Optional[PositiveInt] = Field(None, description="Bit rate in kbps")
    channels: PositiveInt = Field(..., description="Number of audio channels")
    codec: Optional[str] = Field(None, description="Audio codec used")
    genre: Optional[str] = Field(None, description="Music genre")
    bpm: Optional[PositiveFloat] = Field(None, description="Beats per minute")
    key_signature: Optional[str] = Field(None, description="Musical key signature")
    loudness_lufs: Optional[float] = Field(None, description="Loudness in LUFS")
    dynamic_range: Optional[float] = Field(None, description="Dynamic range in dB")
    spectral_centroid: Optional[float] = Field(None, description="Spectral centroid")
    zero_crossing_rate: Optional[float] = Field(None, description="Zero crossing rate")
    mfcc_features: Optional[List[float]] = Field(None, description="MFCC feature vector")
    
    class Config:
        json_schema_extra = {
            "example": {
                "duration_seconds": 180.5,
                "sample_rate": 44100,
                "bit_rate": 320,
                "channels": 2,
                "codec": "mp3",
                "genre": "electronic",
                "bpm": 128.0,
                "key_signature": "C major",
                "loudness_lufs": -14.0,
                "dynamic_range": 8.5
            }
        }


class VideoMetadataSchema(BaseModel):
    """Video-specific metadata schema"""    duration_seconds: PositiveFloat = Field(..., description="Video duration in seconds")
    width: PositiveInt = Field(..., description="Video width in pixels")
    height: PositiveInt = Field(..., description="Video height in pixels")
    fps: PositiveFloat = Field(..., description="Frames per second")
    codec: Optional[str] = Field(None, description="Video codec")
    bitrate: Optional[PositiveInt] = Field(None, description="Video bitrate in kbps")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio")
    color_space: Optional[str] = Field(None, description="Color space")
    frame_count: Optional[PositiveInt] = Field(None, description="Total frame count")
    has_audio: bool = Field(False, description="Whether video contains audio")
    audio_metadata: Optional[AudioMetadataSchema] = Field(None, description="Audio track metadata")
    keyframes: Optional[List[float]] = Field(None, description="Keyframe timestamps")
    scene_changes: Optional[List[float]] = Field(None, description="Scene change timestamps")
    motion_vectors: Optional[List[Dict]] = Field(None, description="Motion vector analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "duration_seconds": 300.0,
                "width": 1920,
                "height": 1080,
                "fps": 30.0,
                "codec": "h264",
                "bitrate": 5000,
                "aspect_ratio": "16:9",
                "has_audio": True
            }
        }


class ImageMetadataSchema(BaseModel):
    """Image-specific metadata schema"""    width: PositiveInt = Field(..., description="Image width in pixels")
    height: PositiveInt = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format (jpg, png, etc.)")
    color_mode: Optional[str] = Field(None, description="Color mode (RGB, CMYK, etc.)")
    compression: Optional[str] = Field(None, description="Compression type")
    dpi: Optional[PositiveInt] = Field(None, description="Dots per inch")
    exif_data: Optional[Dict] = Field(None, description="EXIF metadata")
    color_palette: Optional[List[str]] = Field(None, description="Dominant colors")
    histogram: Optional[Dict] = Field(None, description="Color histogram")
    edge_density: Optional[float] = Field(None, description="Edge density measure")
    brightness: Optional[float] = Field(None, description="Average brightness")
    contrast: Optional[float] = Field(None, description="Contrast measure")
    saturation: Optional[float] = Field(None, description="Color saturation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "width": 1920,
                "height": 1080,
                "format": "jpg",
                "color_mode": "RGB",
                "dpi": 300,
                "brightness": 0.6,
                "contrast": 0.8
            }
        }


class TextMetadataSchema(BaseModel):
    """Text-specific metadata schema"""    character_count: PositiveInt = Field(..., description="Total character count")
    word_count: PositiveInt = Field(..., description="Total word count")
    paragraph_count: PositiveInt = Field(..., description="Number of paragraphs")
    language: Optional[str] = Field(None, description="Detected language code")
    encoding: Optional[str] = Field(None, description="Text encoding")
    sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score")
    readability_score: Optional[float] = Field(None, description="Readability score")
    keywords: Optional[List[str]] = Field(None, description="Extracted keywords")
    entities: Optional[List[Dict]] = Field(None, description="Named entities")
    topics: Optional[List[str]] = Field(None, description="Topic classifications")
    lexical_diversity: Optional[float] = Field(None, description="Lexical diversity measure")
    avg_sentence_length: Optional[float] = Field(None, description="Average sentence length")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_count": 5000,
                "word_count": 850,
                "paragraph_count": 12,
                "language": "en",
                "sentiment_score": 0.6,
                "readability_score": 0.75
            }
        }


class ContentFingerprintBaseSchema(BaseModel):
    """Base schema for content fingerprinting"""    content_type: ContentTypeEnum = Field(..., description="Type of content being fingerprinted")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_size: PositiveInt = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the content")
    fingerprint_hash: str = Field(..., min_length=32, description="Primary fingerprint hash")
    secondary_hashes: Optional[List[str]] = Field(None, description="Additional fingerprint hashes")
    algorithm_used: FingerprintAlgorithmEnum = Field(..., description="Fingerprinting algorithm")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Fingerprint confidence score")
    quality_assessment: ContentQualityEnum = Field(..., description="Content quality classification")
    
    # Metadata based on content type
    audio_metadata: Optional[AudioMetadataSchema] = Field(None, description="Audio-specific metadata")
    video_metadata: Optional[VideoMetadataSchema] = Field(None, description="Video-specific metadata")
    image_metadata: Optional[ImageMetadataSchema] = Field(None, description="Image-specific metadata")
    text_metadata: Optional[TextMetadataSchema] = Field(None, description="Text-specific metadata")
    
    # Additional metadata
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata fields")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    categories: Optional[List[str]] = Field(None, description="Content categories")
    
    @field_validator('fingerprint_hash')
    @classmethod
    @classmethod
    def validate_fingerprint_hash(cls, v):
        """Validate fingerprint hash format"""        if not v or len(v) < 32:
            raise ValueError("Fingerprint hash must be at least 32 characters long")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_metadata_consistency(self):
        """Ensure metadata matches content type"""        content_type = self.content_type
        
        if content_type == ContentTypeEnum.AUDIO and not self.audio_metadata:
            raise ValueError("Audio metadata required for audio content")
        elif content_type == ContentTypeEnum.VIDEO and not self.video_metadata:
            raise ValueError("Video metadata required for video content")
        elif content_type == ContentTypeEnum.IMAGE and not self.image_metadata:
            raise ValueError("Image metadata required for image content")
        elif content_type == ContentTypeEnum.TEXT and not self.text_metadata:
            raise ValueError("Text metadata required for text content")
            
        return self


class ContentFingerprintCreateSchema(ContentFingerprintBaseSchema):
    """Schema for creating content fingerprints"""    user_id: PositiveInt = Field(..., description="ID of the user uploading content")
    project_id: Optional[PositiveInt] = Field(None, description="Associated project ID")
    collection_id: Optional[PositiveInt] = Field(None, description="Associated collection ID")
    
    # Processing options
    enable_protection: bool = Field(True, description="Enable automatic protection monitoring")
    enable_monetization: bool = Field(False, description="Enable monetization tracking")
    enable_collaboration: bool = Field(False, description="Enable collaboration features")
    protection_level: str = Field("standard", description="Protection monitoring level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "content_type": "audio",
                "filename": "my_song.mp3",
                "file_size": 8388608,
                "mime_type": "audio/mpeg",
                "fingerprint_hash": "a1b2c3d4e5f6789012345678901234567890abcd",
                "algorithm_used": "chromaprint",
                "confidence_score": 0.95,
                "quality_assessment": "high",
                "enable_protection": True,
                "enable_monetization": True
            }
        }


class ContentFingerprintUpdateSchema(BaseModel):
    """Schema for updating content fingerprints"""    tags: Optional[List[str]] = Field(None, description="Updated content tags")
    categories: Optional[List[str]] = Field(None, description="Updated content categories")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Updated custom metadata")
    enable_protection: Optional[bool] = Field(None, description="Toggle protection monitoring")
    enable_monetization: Optional[bool] = Field(None, description="Toggle monetization tracking")
    enable_collaboration: Optional[bool] = Field(None, description="Toggle collaboration features")
    protection_level: Optional[str] = Field(None, description="Updated protection level")
    status: Optional[ContentStatusEnum] = Field(None, description="Updated content status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["electronic", "upbeat", "dance"],
                "categories": ["music", "original"],
                "enable_protection": True,
                "protection_level": "enhanced"
            }
        }


class ContentFingerprintResponseSchema(ContentFingerprintBaseSchema):
    """Schema for content fingerprint responses"""    id: PositiveInt = Field(..., description="Unique fingerprint ID")
    user_id: PositiveInt = Field(..., description="Owner user ID")
    project_id: Optional[PositiveInt] = Field(None, description="Associated project ID")
    collection_id: Optional[PositiveInt] = Field(None, description="Associated collection ID")
    
    # Status and processing info
    status: ContentStatusEnum = Field(..., description="Current processing status")
    processing_progress: float = Field(0.0, ge=0.0, le=1.0, description="Processing progress")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    # Protection and monetization settings
    enable_protection: bool = Field(..., description="Protection monitoring enabled")
    enable_monetization: bool = Field(..., description="Monetization tracking enabled")
    enable_collaboration: bool = Field(..., description="Collaboration features enabled")
    protection_level: str = Field(..., description="Current protection level")
    
    # Statistics
    protection_alerts_count: int = Field(0, description="Number of protection alerts")
    revenue_generated: Decimal = Field(Decimal('0.00'), description="Total revenue generated")
    collaboration_requests: int = Field(0, description="Number of collaboration requests")
    view_count: int = Field(0, description="Total view count across platforms")
    engagement_score: float = Field(0.0, description="Calculated engagement score")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_processed_at: Optional[datetime] = Field(None, description="Last processing timestamp")
    
    # File storage info
    storage_url: Optional[str] = Field(None, description="Storage URL for the content")
    backup_urls: Optional[List[str]] = Field(None, description="Backup storage URLs")
    cdn_urls: Optional[List[str]] = Field(None, description="CDN URLs for content delivery")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 123,
                "content_type": "audio",
                "filename": "my_song.mp3",
                "status": "completed",
                "protection_alerts_count": 2,
                "revenue_generated": "250.75",
                "created_at": "2024-08-24T10:30:00Z",
                "updated_at": "2024-08-24T15:45:00Z"
            }
        }


class ContentFingerprintListSchema(BaseModel):
    """Schema for listing content fingerprints"""    fingerprints: List[ContentFingerprintResponseSchema] = Field(..., description="List of fingerprints")
    total_count: int = Field(..., description="Total number of fingerprints")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_previous: bool = Field(..., description="Whether there's a previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fingerprints": [],
                "total_count": 150,
                "page": 1,
                "per_page": 20,
                "total_pages": 8,
                "has_next": True,
                "has_previous": False
            }
        }


class ContentStatisticsSchema(BaseModel):
    """Schema for content statistics"""    total_content_items: int = Field(..., description="Total content items")
    content_by_type: Dict[str, int] = Field(..., description="Content count by type")
    content_by_status: Dict[str, int] = Field(..., description="Content count by status")
    total_file_size: int = Field(..., description="Total file size in bytes")
    average_quality_score: float = Field(..., description="Average quality score")
    protection_coverage: float = Field(..., description="Percentage with protection enabled")
    monetization_enabled: float = Field(..., description="Percentage with monetization enabled")
    total_revenue: Decimal = Field(..., description="Total revenue generated")
    total_alerts: int = Field(..., description="Total protection alerts")
    engagement_metrics: Dict[str, float] = Field(..., description="Engagement metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_content_items": 1250,
                "content_by_type": {
                    "audio": 800,
                    "video": 300,
                    "image": 150
                },
                "total_revenue": "15750.50",
                "protection_coverage": 0.95,
                "average_quality_score": 0.87
            }
        }


class ContentSearchSchema(BaseModel):
    """Schema for content search requests"""    query: Optional[str] = Field(None, description="Search query")
    content_types: Optional[List[ContentTypeEnum]] = Field(None, description="Filter by content types")
    status: Optional[List[ContentStatusEnum]] = Field(None, description="Filter by status")
    quality: Optional[List[ContentQualityEnum]] = Field(None, description="Filter by quality")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    min_duration: Optional[float] = Field(None, description="Minimum duration for audio/video")
    max_duration: Optional[float] = Field(None, description="Maximum duration for audio/video")
    has_protection: Optional[bool] = Field(None, description="Filter by protection status")
    has_monetization: Optional[bool] = Field(None, description="Filter by monetization status")
    min_revenue: Optional[Decimal] = Field(None, description="Minimum revenue generated")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "electronic music",
                "content_types": ["audio"],
                "status": ["completed"],
                "tags": ["electronic", "dance"],
                "has_protection": True,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class ContentBatchOperationSchema(BaseModel):
    """Schema for batch operations on content"""    fingerprint_ids: List[PositiveInt] = Field(..., description="List of fingerprint IDs")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fingerprint_ids": [123, 124, 125],
                "operation": "update_protection_level",
                "parameters": {
                    "protection_level": "enhanced"
                }
            }
        }


# Export schemas
__all__ = [
    # Enums
    "ContentTypeEnum",
    "ContentStatusEnum", 
    "FingerprintAlgorithmEnum",
    "ContentQualityEnum",
    
    # Metadata schemas
    "AudioMetadataSchema",
    "VideoMetadataSchema", 
    "ImageMetadataSchema",
    "TextMetadataSchema",
    
    # Main schemas
    "ContentFingerprintBaseSchema",
    "ContentFingerprintCreateSchema",
    "ContentFingerprintUpdateSchema",
    "ContentFingerprintResponseSchema",
    "ContentFingerprintListSchema",
    
    # Utility schemas
    "ContentStatisticsSchema",
    "ContentSearchSchema",
    "ContentBatchOperationSchema"
]
