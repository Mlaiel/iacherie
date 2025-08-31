"""
Content Types - Core Content Type Definitions and Enumerations
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive content type definitions, format specifications,
and quality metrics for the IA Influencer Agent platform.
"""

import logging
from enum import Enum, IntEnum
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Core content types supported by the platform"""
    # Media Types
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    
    # Text Types
    TEXT = "text"
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CAPTION = "caption"
    DESCRIPTION = "description"
    
    # Social Media Types
    SOCIAL_POST = "social_post"
    TWEET = "tweet"
    INSTAGRAM_POST = "instagram_post"
    FACEBOOK_POST = "facebook_post"
    LINKEDIN_POST = "linkedin_post"
    TIKTOK_POST = "tiktok_post"
    
    # Document Types
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    
    # Multimedia Types
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    WEBINAR = "webinar"
    STORY = "story"
    
    # Interactive Types
    POLL = "poll"
    QUIZ = "quiz"
    SURVEY = "survey"
    
    # Creative Types
    ARTWORK = "artwork"
    PHOTOGRAPHY = "photography"
    DESIGN = "design"
    LOGO = "logo"
    
    # Other
    PORTFOLIO = "portfolio"
    PROFILE = "profile"
    REVIEW = "review"
    TUTORIAL = "tutorial"

class ContentFormat(Enum):
    """Supported content formats"""
    # Image Formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    SVG = "svg"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    
    # Video Formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    
    # Audio Formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    
    # Text Formats
    TXT = "txt"
    HTML = "html"
    MARKDOWN = "markdown"
    RTF = "rtf"
    
    # Document Formats
    PDF_FORMAT = "pdf"
    DOCX = "docx"
    DOC = "doc"
    PPTX = "pptx"
    PPT = "ppt"
    XLSX = "xlsx"
    XLS = "xls"
    
    # Data Formats
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    
    # Web Formats
    CSS = "css"
    JS = "js"
    
    # Archive Formats
    ZIP = "zip"
    RAR = "rar"
    TAR = "tar"
    
    # Other
    BINARY = "binary"
    UNKNOWN = "unknown"

class ContentQuality(IntEnum):
    """Content quality levels"""
    VERY_LOW = 1
    LOW = 2
    BELOW_AVERAGE = 3
    AVERAGE = 4
    GOOD = 5
    HIGH = 6
    VERY_HIGH = 7
    EXCELLENT = 8
    OUTSTANDING = 9
    PERFECT = 10

class ContentStatus(Enum):
    """Content processing and publication status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PROCESSING = "processing"
    FAILED = "failed"
    PENDING = "pending"

class ContentCategory(Enum):
    """Content categories for organization"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH = "health"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    FASHION = "fashion"
    BEAUTY = "beauty"
    MUSIC = "music"
    SPORTS = "sports"
    GAMING = "gaming"
    ART = "art"
    PHOTOGRAPHY = "photography"
    DIY = "diy"
    PARENTING = "parenting"
    PETS = "pets"
    FINANCE = "finance"
    POLITICS = "politics"
    COMEDY = "comedy"
    INSPIRATION = "inspiration"
    PROMOTION = "promotion"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    ANNOUNCEMENT = "announcement"
    OTHER = "other"

class ContentPlatform(Enum):
    """Target platforms for content"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    DISCORD = "discord"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    TUMBLR = "tumblr"
    WEBSITE = "website"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    OTHER_PLATFORM = "other_platform"

class ContentRights(Enum):
    """Content rights and licensing"""
    ORIGINAL = "original"
    LICENSED = "licensed"
    CREATIVE_COMMONS = "creative_commons"
    FAIR_USE = "fair_use"
    PUBLIC_DOMAIN = "public_domain"
    COPYRIGHTED = "copyrighted"
    RESTRICTED = "restricted"
    UNKNOWN_RIGHTS = "unknown_rights"

class ContentModerationLevel(Enum):
    """Content moderation levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"

@dataclass
class ContentSpecs:
    """Technical specifications for content"""
    # Size specifications
    max_file_size: Optional[int] = None  # bytes
    min_file_size: Optional[int] = None  # bytes
    
    # Dimension specifications (for images/videos)
    max_width: Optional[int] = None  # pixels
    max_height: Optional[int] = None  # pixels
    min_width: Optional[int] = None  # pixels
    min_height: Optional[int] = None  # pixels
    aspect_ratio: Optional[str] = None  # "16:9", "4:3", etc.
    
    # Duration specifications (for audio/video)
    max_duration: Optional[float] = None  # seconds
    min_duration: Optional[float] = None  # seconds
    
    # Quality specifications
    min_quality: Optional[ContentQuality] = None
    target_quality: Optional[ContentQuality] = ContentQuality.GOOD
    
    # Format specifications
    allowed_formats: Optional[Set[ContentFormat]] = None
    preferred_format: Optional[ContentFormat] = None
    
    # Text specifications
    max_characters: Optional[int] = None
    min_characters: Optional[int] = None
    max_words: Optional[int] = None
    min_words: Optional[int] = None

@dataclass
class ContentMetadata:
    """Metadata associated with content"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[ContentCategory] = None
    creator_id: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    language: Optional[str] = None
    location: Optional[str] = None
    copyright_info: Optional[str] = None
    license: Optional[ContentRights] = None
    visibility: Optional[str] = "public"  # public, private, unlisted
    monetization_enabled: Optional[bool] = False
    age_restriction: Optional[int] = None
    content_warning: Optional[bool] = False
    custom_fields: Optional[Dict[str, Any]] = None

class PlatformSpecs:
    """Platform-specific content specifications"""
    
    # YouTube specifications
    YOUTUBE_SPECS = {
        ContentType.VIDEO: ContentSpecs(
            max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
            max_duration=12 * 60 * 60,  # 12 hours
            allowed_formats={ContentFormat.MP4, ContentFormat.MOV, ContentFormat.AVI, ContentFormat.WMV, ContentFormat.FLV, ContentFormat.WEBM, ContentFormat.MKV},
            preferred_format=ContentFormat.MP4,
            max_width=7680,  # 8K
            max_height=4320
        ),
        ContentType.AUDIO: ContentSpecs(
            max_file_size=128 * 1024 * 1024,  # 128MB
            allowed_formats={ContentFormat.MP3, ContentFormat.WAV, ContentFormat.FLAC, ContentFormat.AAC, ContentFormat.OGG, ContentFormat.WMA},
            preferred_format=ContentFormat.MP3
        )
    }
    
    # Instagram specifications
    INSTAGRAM_SPECS = {
        ContentType.IMAGE: ContentSpecs(
            max_file_size=30 * 1024 * 1024,  # 30MB
            min_width=320,
            min_height=320,
            max_width=1080,
            max_height=1080,
            allowed_formats={ContentFormat.JPEG, ContentFormat.PNG},
            preferred_format=ContentFormat.JPEG
        ),
        ContentType.VIDEO: ContentSpecs(
            max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
            max_duration=60,  # 60 seconds for feed posts
            min_duration=3,
            allowed_formats={ContentFormat.MP4, ContentFormat.MOV},
            preferred_format=ContentFormat.MP4,
            max_width=1080,
            max_height=1080
        ),
        ContentType.STORY: ContentSpecs(
            max_duration=15,  # 15 seconds per story
            aspect_ratio="9:16",
            max_width=1080,
            max_height=1920
        )
    }
    
    # Twitter specifications
    TWITTER_SPECS = {
        ContentType.IMAGE: ContentSpecs(
            max_file_size=5 * 1024 * 1024,  # 5MB
            allowed_formats={ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.GIF, ContentFormat.WEBP},
            preferred_format=ContentFormat.JPEG,
            max_width=4096,
            max_height=4096
        ),
        ContentType.VIDEO: ContentSpecs(
            max_file_size=512 * 1024 * 1024,  # 512MB
            max_duration=140,  # 140 seconds
            allowed_formats={ContentFormat.MP4, ContentFormat.MOV},
            preferred_format=ContentFormat.MP4
        ),
        ContentType.TEXT: ContentSpecs(
            max_characters=280
        )
    }
    
    # LinkedIn specifications
    LINKEDIN_SPECS = {
        ContentType.IMAGE: ContentSpecs(
            max_file_size=10 * 1024 * 1024,  # 10MB
            allowed_formats={ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.GIF},
            preferred_format=ContentFormat.JPEG,
            min_width=552,
            min_height=552
        ),
        ContentType.VIDEO: ContentSpecs(
            max_file_size=5 * 1024 * 1024 * 1024,  # 5GB
            max_duration=10 * 60,  # 10 minutes
            min_duration=3,
            allowed_formats={ContentFormat.MP4, ContentFormat.MOV, ContentFormat.WEBM},
            preferred_format=ContentFormat.MP4
        ),
        ContentType.DOCUMENT: ContentSpecs(
            max_file_size=100 * 1024 * 1024,  # 100MB
            allowed_formats={ContentFormat.PDF_FORMAT, ContentFormat.PPTX, ContentFormat.DOCX}
        )
    }
    
    # TikTok specifications
    TIKTOK_SPECS = {
        ContentType.VIDEO: ContentSpecs(
            max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
            max_duration=10 * 60,  # 10 minutes
            min_duration=15,  # 15 seconds
            aspect_ratio="9:16",
            max_width=1080,
            max_height=1920,
            allowed_formats={ContentFormat.MP4, ContentFormat.MOV, ContentFormat.WEBM},
            preferred_format=ContentFormat.MP4
        )
    }
    
    @classmethod
    def get_platform_specs(cls, platform: ContentPlatform, content_type: ContentType) -> Optional[ContentSpecs]:
        """Get specifications for a specific platform and content type"""
        platform_specs_map = {
            ContentPlatform.YOUTUBE: cls.YOUTUBE_SPECS,
            ContentPlatform.INSTAGRAM: cls.INSTAGRAM_SPECS,
            ContentPlatform.TWITTER: cls.TWITTER_SPECS,
            ContentPlatform.LINKEDIN: cls.LINKEDIN_SPECS,
            ContentPlatform.TIKTOK: cls.TIKTOK_SPECS
        }
        
        specs = platform_specs_map.get(platform, {})
        return specs.get(content_type)
    
    @classmethod
    def validate_content_for_platform(cls, platform: ContentPlatform, content_type: ContentType, 
                                    content_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content against platform specifications"""
        specs = cls.get_platform_specs(platform, content_type)
        
        if not specs:
            return {"valid": True, "warnings": [f"No specifications found for {platform.value} {content_type.value}"]}
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Validate file size
        if specs.max_file_size and content_info.get("file_size", 0) > specs.max_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File size ({content_info['file_size']} bytes) exceeds maximum ({specs.max_file_size} bytes)")
        
        if specs.min_file_size and content_info.get("file_size", 0) < specs.min_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File size ({content_info['file_size']} bytes) is below minimum ({specs.min_file_size} bytes)")
        
        # Validate dimensions
        if specs.max_width and content_info.get("width", 0) > specs.max_width:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Width ({content_info['width']}) exceeds maximum ({specs.max_width})")
        
        if specs.max_height and content_info.get("height", 0) > specs.max_height:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Height ({content_info['height']}) exceeds maximum ({specs.max_height})")
        
        # Validate duration
        if specs.max_duration and content_info.get("duration", 0) > specs.max_duration:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Duration ({content_info['duration']}s) exceeds maximum ({specs.max_duration}s)")
        
        if specs.min_duration and content_info.get("duration", 0) < specs.min_duration:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Duration ({content_info['duration']}s) is below minimum ({specs.min_duration}s)")
        
        # Validate format
        content_format = content_info.get("format")
        if content_format and specs.allowed_formats and ContentFormat(content_format) not in specs.allowed_formats:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Format ({content_format}) is not allowed. Allowed formats: {[f.value for f in specs.allowed_formats]}")
        
        # Add suggestions
        if specs.preferred_format and content_format != specs.preferred_format.value:
            validation_result["suggestions"].append(f"Consider using {specs.preferred_format.value} format for better compatibility")
        
        if specs.target_quality:
            validation_result["suggestions"].append(f"Target quality level: {specs.target_quality.name}")
        
        return validation_result

class ContentTypeUtils:
    """Utility functions for content types"""
    
    @staticmethod
    def get_content_type_from_filename(filename: str) -> ContentType:
        """Determine content type from filename extension"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'tiff', 'bmp'}
        video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv'}
        audio_extensions = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'}
        document_extensions = {'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls'}
        text_extensions = {'txt', 'md', 'html', 'rtf'}
        
        if extension in image_extensions:
            return ContentType.IMAGE
        elif extension in video_extensions:
            return ContentType.VIDEO
        elif extension in audio_extensions:
            return ContentType.AUDIO
        elif extension in document_extensions:
            return ContentType.DOCUMENT
        elif extension in text_extensions:
            return ContentType.TEXT
        else:
            return ContentType.TEXT  # Default fallback
    
    @staticmethod
    def get_content_format_from_filename(filename: str) -> ContentFormat:
        """Determine content format from filename extension"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        format_mapping = {
            'jpg': ContentFormat.JPEG,
            'jpeg': ContentFormat.JPEG,
            'png': ContentFormat.PNG,
            'gif': ContentFormat.GIF,
            'svg': ContentFormat.SVG,
            'webp': ContentFormat.WEBP,
            'tiff': ContentFormat.TIFF,
            'bmp': ContentFormat.BMP,
            'mp4': ContentFormat.MP4,
            'avi': ContentFormat.AVI,
            'mov': ContentFormat.MOV,
            'mkv': ContentFormat.MKV,
            'webm': ContentFormat.WEBM,
            'flv': ContentFormat.FLV,
            'wmv': ContentFormat.WMV,
            'mp3': ContentFormat.MP3,
            'wav': ContentFormat.WAV,
            'flac': ContentFormat.FLAC,
            'aac': ContentFormat.AAC,
            'ogg': ContentFormat.OGG,
            'm4a': ContentFormat.M4A,
            'wma': ContentFormat.WMA,
            'pdf': ContentFormat.PDF_FORMAT,
            'docx': ContentFormat.DOCX,
            'doc': ContentFormat.DOC,
            'pptx': ContentFormat.PPTX,
            'ppt': ContentFormat.PPT,
            'xlsx': ContentFormat.XLSX,
            'xls': ContentFormat.XLS,
            'txt': ContentFormat.TXT,
            'html': ContentFormat.HTML,
            'md': ContentFormat.MARKDOWN,
            'rtf': ContentFormat.RTF,
            'json': ContentFormat.JSON,
            'xml': ContentFormat.XML,
            'csv': ContentFormat.CSV,
            'yaml': ContentFormat.YAML,
            'css': ContentFormat.CSS,
            'js': ContentFormat.JS
        }
        
        return format_mapping.get(extension, ContentFormat.UNKNOWN)
    
    @staticmethod
    def is_media_content(content_type: ContentType) -> bool:
        """Check if content type is media (image, video, audio)"""



        return content_type in {ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO, ContentType.MUSIC}
    
    @staticmethod
    def is_text_content(content_type: ContentType) -> bool:
        """Check if content type is text-based"""



        return content_type in {
            ContentType.TEXT, ContentType.BLOG_POST, ContentType.ARTICLE,
            ContentType.CAPTION, ContentType.DESCRIPTION, ContentType.SOCIAL_POST,
            ContentType.TWEET
        }
    
    @staticmethod
    def requires_processing(content_type: ContentType) -> bool:
        """Check if content type typically requires AI processing"""
        processing_types = {
            ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO, ContentType.MUSIC,
            ContentType.TEXT, ContentType.BLOG_POST, ContentType.ARTICLE, ContentType.SOCIAL_POST
        }
        return content_type in processing_types
    
    @staticmethod
    def get_recommended_platforms(content_type: ContentType, category: ContentCategory = None) -> List[ContentPlatform]:
        """Get recommended platforms for content type and category"""
        recommendations = {
            ContentType.IMAGE: [ContentPlatform.INSTAGRAM, ContentPlatform.PINTEREST, ContentPlatform.FACEBOOK],
            ContentType.VIDEO: [ContentPlatform.YOUTUBE, ContentPlatform.TIKTOK, ContentPlatform.INSTAGRAM],
            ContentType.AUDIO: [ContentPlatform.SPOTIFY, ContentPlatform.SOUNDCLOUD, ContentPlatform.YOUTUBE],
            ContentType.MUSIC: [ContentPlatform.SPOTIFY, ContentPlatform.SOUNDCLOUD, ContentPlatform.YOUTUBE],
            ContentType.BLOG_POST: [ContentPlatform.MEDIUM, ContentPlatform.WORDPRESS, ContentPlatform.LINKEDIN],
            ContentType.ARTICLE: [ContentPlatform.MEDIUM, ContentPlatform.LINKEDIN, ContentPlatform.WORDPRESS],
            ContentType.SOCIAL_POST: [ContentPlatform.FACEBOOK, ContentPlatform.TWITTER, ContentPlatform.LINKEDIN],
            ContentType.TWEET: [ContentPlatform.TWITTER],
            ContentType.STORY: [ContentPlatform.INSTAGRAM, ContentPlatform.FACEBOOK, ContentPlatform.SNAPCHAT],
            ContentType.LIVESTREAM: [ContentPlatform.YOUTUBE, ContentPlatform.TWITCH, ContentPlatform.FACEBOOK],
            ContentType.PODCAST: [ContentPlatform.SPOTIFY, ContentPlatform.SOUNDCLOUD, ContentPlatform.YOUTUBE]
        }
        
        base_recommendations = recommendations.get(content_type, [ContentPlatform.WEBSITE])
        
        # Adjust based on category
        if category == ContentCategory.BUSINESS:
            if ContentPlatform.LINKEDIN not in base_recommendations:
                base_recommendations.insert(0, ContentPlatform.LINKEDIN)
        elif category == ContentCategory.ENTERTAINMENT:
            if ContentPlatform.TIKTOK not in base_recommendations:
                base_recommendations.append(ContentPlatform.TIKTOK)
        elif category == ContentCategory.MUSIC:
            music_platforms = [ContentPlatform.SPOTIFY, ContentPlatform.SOUNDCLOUD]
            base_recommendations = music_platforms + [p for p in base_recommendations if p not in music_platforms]
        
        return base_recommendations

# Create alias for backwards compatibility
SocialPlatform = ContentPlatform

# Export all classes and enums
__all__ = [
    'ContentType', 'ContentFormat', 'ContentQuality', 'ContentStatus', 'ContentCategory',
    'ContentPlatform', 'SocialPlatform', 'ContentRights', 'ContentModerationLevel',
    'ContentSpecs', 'ContentMetadata', 'PlatformSpecs', 'ContentTypeUtils'
]

logger.info("Content types module loaded successfully")
