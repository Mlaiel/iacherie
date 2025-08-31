"""Parser Configuration Module
===========================

Configuration management for content parsers in the IA Influencer Agent platform.
Provides centralized configuration for all parsing operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path


class ParserType(Enum):
    """Enumeration of parser types"""    PLATFORM = "platform"
    MEDIA = "media"
    METADATA = "metadata"
    CONTENT = "content"
    ANALYTICS = "analytics"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    FINGERPRINT = "fingerprint"


class PlatformType(Enum):
    """Enumeration of supported platforms"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    REDDIT = "reddit"


class MediaFormat(Enum):
    """Enumeration of supported media formats"""    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    
    # Image formats
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    SVG = "svg"
    
    # Text formats
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"


@dataclass
class PlatformConfig:
    """Configuration for platform-specific parsers"""    platform: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    use_api: bool = True
    use_scraping: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class MediaConfig:
    """Configuration for media parsers"""    supported_formats: List[MediaFormat] = field(default_factory=list)
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    quality_threshold: float = 0.7
    enable_compression: bool = True
    compression_quality: int = 85
    extract_metadata: bool = True
    generate_thumbnails: bool = True
    thumbnail_size: tuple = (320, 240)
    audio_sample_rate: int = 44100
    video_resolution: tuple = (1920, 1080)
    frame_rate: int = 30


@dataclass
class FingerprintConfig:
    """Configuration for fingerprint parsing"""    enable_audio_fingerprint: bool = True
    enable_video_fingerprint: bool = True
    enable_image_fingerprint: bool = True
    enable_text_fingerprint: bool = True
    
    # Audio fingerprinting
    audio_duration_limit: int = 300  # seconds
    audio_chunk_size: int = 2048
    audio_hash_size: int = 256
    
    # Video fingerprinting
    video_frame_interval: int = 30  # frames
    video_hash_size: int = 256
    video_quality_threshold: float = 0.8
    
    # Image fingerprinting
    image_hash_size: int = 256
    image_resize_dimensions: tuple = (224, 224)
    
    # Text fingerprinting
    text_chunk_size: int = 1000
    text_overlap: int = 100
    text_min_length: int = 50


@dataclass
class AnalyticsConfig:
    """Configuration for analytics parsers"""    date_range_days: int = 30
    metrics_to_collect: List[str] = field(default_factory=lambda: [
        "views", "likes", "shares", "comments", "engagement_rate"
    ])
    real_time_updates: bool = True
    cache_duration: int = 3600  # seconds
    aggregation_level: str = "daily"  # daily, hourly, weekly
    include_demographics: bool = True
    include_geographic: bool = True


@dataclass
class RevenueConfig:
    """Configuration for revenue parsers"""    currency: str = "EUR"
    decimal_places: int = 2
    include_tax: bool = True
    tax_rate: float = 0.19  # 19% VAT
    payment_platforms: List[str] = field(default_factory=lambda: [
        "stripe", "paypal", "wise", "youtube", "spotify"
    ])
    reporting_period: str = "monthly"
    auto_currency_conversion: bool = True


@dataclass
class ValidationConfig:
    """Configuration for content validation"""    strict_mode: bool = False
    required_fields: List[str] = field(default_factory=list)
    field_validators: Dict[str, Any] = field(default_factory=dict)
    content_safety_check: bool = True
    max_content_length: int = 1000000  # 1MB text
    allowed_content_types: List[str] = field(default_factory=lambda: [
        "text", "image", "audio", "video"
    ])


@dataclass
class CacheConfig:
    """Configuration for parser caching"""    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds
    cache_backend: str = "redis"  # redis, memory, file
    cache_prefix: str = "parser_cache"
    max_cache_size: int = 1000  # number of entries
    cache_compression: bool = True


@dataclass
class SecurityConfig:
    """Configuration for parser security"""    sanitize_input: bool = True
    validate_urls: bool = True
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    max_redirects: int = 5
    verify_ssl: bool = True
    content_filtering: bool = True
    malware_scanning: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for parser performance"""    max_concurrent_requests: int = 10
    request_timeout: float = 30.0
    connection_pool_size: int = 100
    keep_alive: bool = True
    compression: bool = True
    streaming: bool = True
    batch_size: int = 50
    memory_limit: int = 512 * 1024 * 1024  # 512MB


class ParserConfig:
    """Main configuration class for all parsers"""    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or environment"""        # Default configurations
        self.platform = self._get_platform_configs()
        self.media = MediaConfig()
        self.fingerprint = FingerprintConfig()
        self.analytics = AnalyticsConfig()
        self.revenue = RevenueConfig()
        self.validation = ValidationConfig()
        self.cache = CacheConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
        
        # Load from config file if provided
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
    
    def _get_platform_configs(self) -> Dict[PlatformType, PlatformConfig]:
        """Get default platform configurations"""        return {
            PlatformType.YOUTUBE: PlatformConfig(
                platform=PlatformType.YOUTUBE,
                base_url="https://www.googleapis.com/youtube/v3",
                rate_limit=10000,  # requests per day
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.INSTAGRAM: PlatformConfig(
                platform=PlatformType.INSTAGRAM,
                base_url="https://graph.instagram.com",
                rate_limit=200,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.TIKTOK: PlatformConfig(
                platform=PlatformType.TIKTOK,
                base_url="https://open-api.tiktok.com",
                rate_limit=100,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.TWITTER: PlatformConfig(
                platform=PlatformType.TWITTER,
                base_url="https://api.twitter.com/2",
                rate_limit=300,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.SPOTIFY: PlatformConfig(
                platform=PlatformType.SPOTIFY,
                base_url="https://api.spotify.com/v1",
                rate_limit=100,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.SOUNDCLOUD: PlatformConfig(
                platform=PlatformType.SOUNDCLOUD,
                base_url="https://api.soundcloud.com",
                rate_limit=15000,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.TWITCH: PlatformConfig(
                platform=PlatformType.TWITCH,
                base_url="https://api.twitch.tv/helix",
                rate_limit=800,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.LINKEDIN: PlatformConfig(
                platform=PlatformType.LINKEDIN,
                base_url="https://api.linkedin.com/v2",
                rate_limit=500,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.FACEBOOK: PlatformConfig(
                platform=PlatformType.FACEBOOK,
                base_url="https://graph.facebook.com",
                rate_limit=200,
                user_agent="IA-Influencer-Agent/1.0"
            ),
            PlatformType.REDDIT: PlatformConfig(
                platform=PlatformType.REDDIT,
                base_url="https://oauth.reddit.com",
                rate_limit=60,
                user_agent="IA-Influencer-Agent/1.0"
            )
        }
    
    def _load_from_file(self):
        """Load configuration from YAML/JSON file"""        import yaml
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    import json
                    config_data = json.load(f)
            
            # Update configurations with file data
            self._update_config_from_dict(config_data)
            
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""        # Platform API keys
        for platform_type in PlatformType:
            platform_name = platform_type.value.upper()
            
            api_key = os.getenv(f"{platform_name}_API_KEY")
            if api_key:
                self.platform[platform_type].api_key = api_key
            
            api_secret = os.getenv(f"{platform_name}_API_SECRET")
            if api_secret:
                self.platform[platform_type].api_secret = api_secret
            
            access_token = os.getenv(f"{platform_name}_ACCESS_TOKEN")
            if access_token:
                self.platform[platform_type].access_token = access_token
        
        # Cache configuration
        cache_backend = os.getenv("PARSER_CACHE_BACKEND")
        if cache_backend:
            self.cache.cache_backend = cache_backend
        
        cache_ttl = os.getenv("PARSER_CACHE_TTL")
        if cache_ttl:
            self.cache.cache_ttl = int(cache_ttl)
        
        # Performance configuration
        max_concurrent = os.getenv("PARSER_MAX_CONCURRENT")
        if max_concurrent:
            self.performance.max_concurrent_requests = int(max_concurrent)
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""        # This method would update the config objects from parsed file data
        # Implementation would depend on the specific file structure
        pass
    
    def get_platform_config(self, platform: PlatformType) -> PlatformConfig:
        """Get configuration for specific platform"""        return self.platform.get(platform, PlatformConfig(platform=platform))
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""        try:
            # Validate platform configs
            for platform_type, config in self.platform.items():
                if config.rate_limit <= 0:
                    raise ValueError(f"Invalid rate limit for {platform_type.value}")
                
                if config.timeout <= 0:
                    raise ValueError(f"Invalid timeout for {platform_type.value}")
            
            # Validate media config
            if self.media.max_file_size <= 0:
                raise ValueError("Invalid max file size")
            
            # Validate performance config
            if self.performance.max_concurrent_requests <= 0:
                raise ValueError("Invalid max concurrent requests")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return {
            "platform": {k.value: v.__dict__ for k, v in self.platform.items()},
            "media": self.media.__dict__,
            "fingerprint": self.fingerprint.__dict__,
            "analytics": self.analytics.__dict__,
            "revenue": self.revenue.__dict__,
            "validation": self.validation.__dict__,
            "cache": self.cache.__dict__,
            "security": self.security.__dict__,
            "performance": self.performance.__dict__
        }
