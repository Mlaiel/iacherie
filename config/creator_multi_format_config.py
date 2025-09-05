"""
Creator Multi-Format Configuration - Enterprise Configuration Management
Enterprise configuration for creator multi-format content support and business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass


class ContentFormat(str, Enum):
    """Supported content formats"""
    # Audio Formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"
    M4A = "m4a"
    
    # Video Formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WMV = "wmv"
    WEBM = "webm"
    
    # Image Formats
    JPEG = "jpeg"
    PNG = "png"
    SVG = "svg"
    WEBP = "webp"
    GIF = "gif"
    TIFF = "tiff"
    
    # Text Formats
    MARKDOWN = "markdown"
    HTML = "html"
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    
    # Voice Formats
    VOICE_WAV = "voice_wav"
    VOICE_MP3 = "voice_mp3"
    VOICE_FLAC = "voice_flac"
    VOICE_SYNTHESIS = "voice_synthesis"
    
    # Avatar Formats
    MODELS_3D = "3d_models"
    ANIMATIONS = "animations"
    VRCHAT = "vrchat"
    UNITY = "unity"


class CreatorType(str, Enum):
    """Supported creator types"""
    MUSICIANS = "musicians"
    BLOGGERS = "bloggers" 
    PHOTOGRAPHERS = "photographers"
    INFLUENCERS = "influencers"
    COMEDIANS = "comedians"


class MonetizationStream(str, Enum):
    """Monetization stream types"""
    # Musicians
    STREAMING = "streaming"
    ROYALTIES = "royalties"
    MERCHANDISE = "merchandise"
    CONCERTS = "concerts"
    
    # Bloggers
    ADVERTISING = "advertising"
    AFFILIATE = "affiliate"
    SUBSCRIPTIONS = "subscriptions"
    COURSES = "courses"
    
    # Photographers
    STOCK_PHOTOGRAPHY = "stock_photography"
    PRINT_SALES = "print_sales"
    LICENSING = "licensing"
    NFT = "nft"
    
    # Influencers
    SPONSORED_CONTENT = "sponsored_content"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    
    # Comedians
    SHOW_TICKETS = "show_tickets"
    STREAMING_SPECIALS = "streaming_specials"
    PODCASTS = "podcasts"


class DistributionPlatform(str, Enum):
    """Distribution platform types"""
    # Music Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    
    # Content Platforms
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    LINKEDIN = "linkedin"
    NEWSLETTERS = "newsletters"
    
    # Visual Platforms
    INSTAGRAM = "instagram"
    BEHANCE = "behance"
    SHUTTERSTOCK = "shutterstock"
    PORTFOLIO_SITES = "portfolio_sites"
    
    # Social Platforms
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    
    # Streaming Platforms
    NETFLIX = "netflix"
    PODCAST_PLATFORMS = "podcast_platforms"


@dataclass
class CreatorTypeConfig:
    """Configuration for specific creator type"""
    supported_formats: List[ContentFormat]
    monetization_streams: List[MonetizationStream]
    collaboration_types: List[str]
    distribution_platforms: List[DistributionPlatform]


@dataclass
class ContentFormatConfig:
    """Configuration for content formats"""
    audio_formats: List[str]
    video_formats: List[str]
    image_formats: List[str]
    text_formats: List[str]
    voice_formats: List[str]
    avatar_formats: List[str]


@dataclass
class ContentIngestionConfig:
    """Configuration for content ingestion settings"""
    max_file_size: Dict[str, str]
    quality_standards: Dict[str, str]
    validation_rules: Dict[str, bool]


class CreatorMultiFormatSettings:
    """Creator multi-format configuration settings"""
    
    def __init__(self):
        # Content Format Configuration
        self.content_formats = ContentFormatConfig(
            audio_formats=["mp3", "wav", "flac", "ogg", "aac", "m4a"],
            video_formats=["mp4", "avi", "mov", "mkv", "wmv", "webm"],
            image_formats=["jpeg", "png", "svg", "webp", "gif", "tiff"],
            text_formats=["markdown", "html", "txt", "pdf", "docx"],
            voice_formats=["wav", "mp3", "flac", "voice_synthesis"],
            avatar_formats=["3d_models", "animations", "vrchat", "unity"]
        )
        
        # Creator Type Configurations
        self.creator_types = {
            "musicians": CreatorTypeConfig(
                supported_formats=[ContentFormat.MP3, ContentFormat.WAV, ContentFormat.FLAC, 
                                 ContentFormat.MP4, ContentFormat.JPEG, ContentFormat.PNG],
                monetization_streams=[MonetizationStream.STREAMING, MonetizationStream.ROYALTIES,
                                    MonetizationStream.MERCHANDISE, MonetizationStream.CONCERTS],
                collaboration_types=["remixes", "features", "band_formations", "producer_partnerships"],
                distribution_platforms=[DistributionPlatform.SPOTIFY, DistributionPlatform.APPLE_MUSIC,
                                      DistributionPlatform.YOUTUBE_MUSIC, DistributionPlatform.SOUNDCLOUD]
            ),
            "bloggers": CreatorTypeConfig(
                supported_formats=[ContentFormat.MARKDOWN, ContentFormat.HTML, ContentFormat.TXT,
                                 ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.MP4],
                monetization_streams=[MonetizationStream.ADVERTISING, MonetizationStream.AFFILIATE,
                                    MonetizationStream.SUBSCRIPTIONS, MonetizationStream.COURSES],
                collaboration_types=["guest_posts", "content_partnerships", "cross_promotion"],
                distribution_platforms=[DistributionPlatform.WORDPRESS, DistributionPlatform.MEDIUM,
                                      DistributionPlatform.LINKEDIN, DistributionPlatform.NEWSLETTERS]
            ),
            "photographers": CreatorTypeConfig(
                supported_formats=[ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.TIFF,
                                 ContentFormat.WEBP, ContentFormat.MP4],
                monetization_streams=[MonetizationStream.STOCK_PHOTOGRAPHY, MonetizationStream.PRINT_SALES,
                                    MonetizationStream.LICENSING, MonetizationStream.NFT],
                collaboration_types=["model_partnerships", "brand_collaborations", "event_coordination"],
                distribution_platforms=[DistributionPlatform.INSTAGRAM, DistributionPlatform.BEHANCE,
                                      DistributionPlatform.SHUTTERSTOCK, DistributionPlatform.PORTFOLIO_SITES]
            ),
            "influencers": CreatorTypeConfig(
                supported_formats=[ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.MP4,
                                 ContentFormat.MARKDOWN, ContentFormat.VOICE_MP3],
                monetization_streams=[MonetizationStream.SPONSORED_CONTENT, MonetizationStream.AFFILIATE,
                                    MonetizationStream.BRAND_PARTNERSHIPS, MonetizationStream.MERCHANDISE],
                collaboration_types=["influencer_networks", "brand_campaigns", "cross_promotion"],
                distribution_platforms=[DistributionPlatform.INSTAGRAM, DistributionPlatform.TIKTOK,
                                      DistributionPlatform.YOUTUBE, DistributionPlatform.TWITTER]
            ),
            "comedians": CreatorTypeConfig(
                supported_formats=[ContentFormat.MP4, ContentFormat.MP3, ContentFormat.MARKDOWN],
                monetization_streams=[MonetizationStream.SHOW_TICKETS, MonetizationStream.STREAMING_SPECIALS,
                                    MonetizationStream.MERCHANDISE, MonetizationStream.PODCASTS],
                collaboration_types=["comedy_partnerships", "writing_collaborations", "tour_coordination"],
                distribution_platforms=[DistributionPlatform.YOUTUBE, DistributionPlatform.NETFLIX,
                                      DistributionPlatform.PODCAST_PLATFORMS, DistributionPlatform.INSTAGRAM]
            )
        }
        
        # Content Ingestion Settings
        self.content_ingestion_settings = ContentIngestionConfig(
            max_file_size={
                "audio": "500MB",
                "video": "2GB", 
                "image": "50MB",
                "text": "10MB",
                "voice": "100MB",
                "avatar": "200MB"
            },
            quality_standards={
                "audio_quality": "320kbps minimum",
                "video_quality": "1080p minimum",
                "image_resolution": "2048x2048 minimum",
                "text_readability": "Grade 8 minimum"
            },
            validation_rules={
                "copyright_check": True,
                "content_moderation": True,
                "quality_assessment": True,
                "metadata_extraction": True
            }
        )
        
        # Multi-format Processing Settings
        self.multi_format_processing_enabled = True
        self.cross_format_optimization = True
        self.format_conversion_enabled = True
        self.automatic_format_detection = True
        
        # Business Logic Settings
        self.creator_verification_required = True
        self.content_protection_enabled = True
        self.monetization_tracking_enabled = True
        self.collaboration_matching_enabled = True
        
        # Performance Settings
        self.processing_timeout_seconds = 300
        self.max_concurrent_uploads = 10
        self.cache_processed_content = True
        self.auto_backup_enabled = True
    
    def get_supported_formats_for_creator(self, creator_type: str) -> List[ContentFormat]:
        """Get supported formats for a specific creator type"""
        if creator_type not in self.creator_types:
            raise ValueError(f"Unknown creator type: {creator_type}")
        return self.creator_types[creator_type].supported_formats
    
    def get_monetization_streams_for_creator(self, creator_type: str) -> List[MonetizationStream]:
        """Get monetization streams for a specific creator type"""
        if creator_type not in self.creator_types:
            raise ValueError(f"Unknown creator type: {creator_type}")
        return self.creator_types[creator_type].monetization_streams
    
    def get_distribution_platforms_for_creator(self, creator_type: str) -> List[DistributionPlatform]:
        """Get distribution platforms for a specific creator type"""
        if creator_type not in self.creator_types:
            raise ValueError(f"Unknown creator type: {creator_type}")
        return self.creator_types[creator_type].distribution_platforms
    
    def is_format_supported_by_creator(self, creator_type: str, content_format: ContentFormat) -> bool:
        """Check if a format is supported by a creator type"""
        if creator_type not in self.creator_types:
            return False
        return content_format in self.creator_types[creator_type].supported_formats
    
    def get_max_file_size_for_format(self, format_category: str) -> str:
        """Get maximum file size for a format category"""
        return self.content_ingestion_settings.max_file_size.get(format_category, "10MB")
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete configuration"""
        errors = []
        
        # Validate all creator types have required configurations
        for creator_type, config in self.creator_types.items():
            if not config.supported_formats:
                errors.append(f"Creator type '{creator_type}' has no supported formats")
            if not config.monetization_streams:
                errors.append(f"Creator type '{creator_type}' has no monetization streams")
            if not config.distribution_platforms:
                errors.append(f"Creator type '{creator_type}' has no distribution platforms")
        
        # Validate content ingestion settings
        if not self.content_ingestion_settings.max_file_size:
            errors.append("Content ingestion max file sizes not configured")
        
        return errors


# Global creator multi-format settings instance
creator_multi_format_settings = CreatorMultiFormatSettings()

__all__ = [
    "CreatorMultiFormatSettings",
    "creator_multi_format_settings", 
    "ContentFormat",
    "CreatorType",
    "MonetizationStream",
    "DistributionPlatform",
    "CreatorTypeConfig",
    "ContentFormatConfig",
    "ContentIngestionConfig"
]