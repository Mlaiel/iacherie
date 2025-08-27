"""
Content Analysis AI Configuration for IA-Influencer Agent Platform
==================================================================

Professional content analysis AI configuration for multi-format processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class ContentType(str, Enum):
    """Supported content types for analysis."""
    
    AUDIO_MUSIC = "audio_music"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_SPEECH = "audio_speech"
    VIDEO_MUSIC = "video_music"
    VIDEO_ENTERTAINMENT = "video_entertainment"
    VIDEO_EDUCATIONAL = "video_educational"
    IMAGE_PHOTOGRAPHY = "image_photography"
    IMAGE_ARTWORK = "image_artwork"
    IMAGE_MEME = "image_meme"
    TEXT_LYRICS = "text_lyrics"
    TEXT_BLOG = "text_blog"
    TEXT_SOCIAL = "text_social"
    MULTIMODAL_CONTENT = "multimodal_content"


class AnalysisLevel(str, Enum):
    """Analysis depth levels for content processing."""
    
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    FORENSIC = "forensic"


class ContentQuality(str, Enum):
    """Content quality assessment levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROFESSIONAL = "professional"
    ULTRA_HD = "ultra_hd"


@dataclass
class ContentAnalysisSpec:
    """Specification for content analysis pipeline configuration."""
    
    content_type: ContentType
    analysis_level: AnalysisLevel
    quality_threshold: ContentQuality
    processing_timeout: int = 300  # seconds
    extract_metadata: bool = True
    generate_thumbnails: bool = True
    extract_features: bool = True
    perform_classification: bool = True
    detect_copyright: bool = True
    estimate_monetization: bool = True
    analyze_engagement: bool = True
    custom_processors: Optional[List[str]] = None


class ContentAnalysisConfig(BaseSettings):
    """
    Professional Content Analysis AI Configuration.
    
    Manages comprehensive analysis of multi-format content including
    audio, video, image, and text processing for the influencer platform.
    """
    
    # Core Analysis Configuration
    ANALYSIS_OUTPUT_PATH: str = "/data/analysis"
    SUPPORTED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "flac", "m4a", "ogg", "aac"]
    SUPPORTED_VIDEO_FORMATS: List[str] = ["mp4", "mov", "avi", "mkv", "webm", "wmv"]
    SUPPORTED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
    SUPPORTED_TEXT_FORMATS: List[str] = ["txt", "md", "json", "csv", "srt", "vtt"]
    
    # Processing Limits
    MAX_FILE_SIZE_MB: int = 2048  # 2GB
    MAX_DURATION_SECONDS: int = 7200  # 2 hours
    MAX_CONCURRENT_ANALYSES: int = 8
    ANALYSIS_QUEUE_SIZE: int = 100
    
    # Audio Analysis Configuration
    AUDIO_SAMPLE_RATE: int = 44100
    AUDIO_BIT_DEPTH: int = 16
    AUDIO_CHANNELS: str = "stereo"  # mono, stereo, surround
    EXTRACT_AUDIO_FEATURES: bool = True
    DETECT_AUDIO_GENRE: bool = True
    ANALYZE_AUDIO_MOOD: bool = True
    EXTRACT_AUDIO_TEMPO: bool = True
    DETECT_AUDIO_KEY: bool = True
    IDENTIFY_INSTRUMENTS: bool = True
    
    # Video Analysis Configuration
    VIDEO_FRAME_RATE: int = 30
    VIDEO_RESOLUTION: str = "1920x1080"
    EXTRACT_VIDEO_FRAMES: bool = True
    ANALYZE_VIDEO_SCENES: bool = True
    DETECT_VIDEO_OBJECTS: bool = True
    RECOGNIZE_VIDEO_FACES: bool = True
    EXTRACT_VIDEO_TEXT: bool = True
    ANALYZE_VIDEO_MOTION: bool = True
    
    # Image Analysis Configuration
    IMAGE_MAX_RESOLUTION: str = "4096x4096"
    EXTRACT_IMAGE_METADATA: bool = True
    DETECT_IMAGE_OBJECTS: bool = True
    RECOGNIZE_IMAGE_FACES: bool = True
    EXTRACT_IMAGE_TEXT: bool = True
    ANALYZE_IMAGE_STYLE: bool = True
    DETECT_IMAGE_NSFW: bool = True
    
    # Text Analysis Configuration
    TEXT_MAX_LENGTH: int = 1000000  # characters
    EXTRACT_TEXT_ENTITIES: bool = True
    ANALYZE_TEXT_SENTIMENT: bool = True
    DETECT_TEXT_LANGUAGE: bool = True
    EXTRACT_TEXT_KEYWORDS: bool = True
    ANALYZE_TEXT_READABILITY: bool = True
    DETECT_TEXT_PLAGIARISM: bool = True
    
    # Content Protection Integration
    ENABLE_COPYRIGHT_DETECTION: bool = True
    COPYRIGHT_CONFIDENCE_THRESHOLD: float = 0.85
    WATERMARK_DETECTION: bool = True
    BRAND_DETECTION: bool = True
    LOGO_RECOGNITION: bool = True
    
    # Monetization Analysis
    ANALYZE_COMMERCIAL_POTENTIAL: bool = True
    ESTIMATE_REVENUE_POTENTIAL: bool = True
    ANALYZE_TARGET_AUDIENCE: bool = True
    EXTRACT_MARKET_KEYWORDS: bool = True
    ASSESS_VIRAL_POTENTIAL: bool = True
    
    # Quality Assessment
    QUALITY_ASSESSMENT_ENABLED: bool = True
    MIN_QUALITY_THRESHOLD: float = 0.6
    TECHNICAL_QUALITY_ANALYSIS: bool = True
    ARTISTIC_QUALITY_ANALYSIS: bool = True
    COMMERCIAL_QUALITY_ANALYSIS: bool = True
    
    # AI Model Configuration
    CONTENT_CLASSIFIER_MODEL: str = "transformers/content-classifier-v2"
    QUALITY_ASSESSOR_MODEL: str = "custom/quality-assessor-v1"
    COPYRIGHT_DETECTOR_MODEL: str = "custom/copyright-detector-v2"
    MONETIZATION_ESTIMATOR_MODEL: str = "custom/monetization-estimator-v1"
    
    # Performance Optimization
    USE_GPU_ACCELERATION: bool = True
    GPU_MEMORY_FRACTION: float = 0.7
    BATCH_PROCESSING_SIZE: int = 16
    ENABLE_MODEL_CACHING: bool = True
    CACHE_SIZE_MB: int = 4096
    
    # Output Configuration
    GENERATE_ANALYSIS_REPORT: bool = True
    REPORT_FORMAT: str = "json"  # json, xml, html
    INCLUDE_VISUALIZATIONS: bool = True
    SAVE_INTERMEDIATE_RESULTS: bool = True
    COMPRESS_OUTPUT: bool = True
    
    # Security and Privacy
    ENCRYPT_ANALYSIS_DATA: bool = True
    ANONYMIZE_PERSONAL_DATA: bool = True
    SECURE_DELETE_TEMP_FILES: bool = True
    AUDIT_ANALYSIS_OPERATIONS: bool = True
    
    @validator("MAX_FILE_SIZE_MB")
    def validate_max_file_size(cls, v):
        if v <= 0 or v > 10240:  # Max 10GB
            raise ValueError("Max file size must be between 1MB and 10GB")
        return v
    
    @validator("MAX_CONCURRENT_ANALYSES")
    def validate_concurrent_analyses(cls, v):
        if v <= 0 or v > 32:
            raise ValueError("Concurrent analyses must be between 1 and 32")
        return v
    
    @validator("COPYRIGHT_CONFIDENCE_THRESHOLD")
    def validate_confidence_threshold(cls, v):
        if v < 0.5 or v > 1.0:
            raise ValueError("Confidence threshold must be between 0.5 and 1.0")
        return v
    
    def get_analysis_spec(self, content_type: ContentType) -> ContentAnalysisSpec:
        """Get analysis specification for content type."""
        
        # Standard specifications by content type
        specs = {
            ContentType.AUDIO_MUSIC: ContentAnalysisSpec(
                content_type=content_type,
                analysis_level=AnalysisLevel.COMPREHENSIVE,
                quality_threshold=ContentQuality.HIGH,
                processing_timeout=600,
                extract_metadata=True,
                generate_thumbnails=True,
                extract_features=True,
                perform_classification=True,
                detect_copyright=True,
                estimate_monetization=True,
                analyze_engagement=True
            ),
            ContentType.VIDEO_MUSIC: ContentAnalysisSpec(
                content_type=content_type,
                analysis_level=AnalysisLevel.COMPREHENSIVE,
                quality_threshold=ContentQuality.HIGH,
                processing_timeout=1200,
                extract_metadata=True,
                generate_thumbnails=True,
                extract_features=True,
                perform_classification=True,
                detect_copyright=True,
                estimate_monetization=True,
                analyze_engagement=True
            ),
            ContentType.IMAGE_PHOTOGRAPHY: ContentAnalysisSpec(
                content_type=content_type,
                analysis_level=AnalysisLevel.STANDARD,
                quality_threshold=ContentQuality.HIGH,
                processing_timeout=300,
                extract_metadata=True,
                generate_thumbnails=True,
                extract_features=True,
                perform_classification=True,
                detect_copyright=True,
                estimate_monetization=True,
                analyze_engagement=True
            ),
            ContentType.TEXT_BLOG: ContentAnalysisSpec(
                content_type=content_type,
                analysis_level=AnalysisLevel.STANDARD,
                quality_threshold=ContentQuality.MEDIUM,
                processing_timeout=120,
                extract_metadata=True,
                generate_thumbnails=False,
                extract_features=True,
                perform_classification=True,
                detect_copyright=True,
                estimate_monetization=True,
                analyze_engagement=True
            )
        }
        
        return specs.get(content_type, ContentAnalysisSpec(
            content_type=content_type,
            analysis_level=AnalysisLevel.BASIC,
            quality_threshold=ContentQuality.MEDIUM,
            processing_timeout=300
        ))
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get all supported file formats by category."""
        return {
            "audio": self.SUPPORTED_AUDIO_FORMATS,
            "video": self.SUPPORTED_VIDEO_FORMATS,
            "image": self.SUPPORTED_IMAGE_FORMATS,
            "text": self.SUPPORTED_TEXT_FORMATS
        }
    
    def is_format_supported(self, file_extension: str) -> bool:
        """Check if file format is supported."""
        ext = file_extension.lower().lstrip('.')
        all_formats = (
            self.SUPPORTED_AUDIO_FORMATS + 
            self.SUPPORTED_VIDEO_FORMATS + 
            self.SUPPORTED_IMAGE_FORMATS + 
            self.SUPPORTED_TEXT_FORMATS
        )
        return ext in all_formats
    
    class Config:
        env_prefix = "CONTENT_ANALYSIS_"
        case_sensitive = True


# Global instance for easy import
content_analysis_config = ContentAnalysisConfig()
