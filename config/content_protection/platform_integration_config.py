"""Platform Integration Configuration Module for Content Protection
===============================================================

Professional platform integration configuration for automated content surveillance,
DMCA enforcement, and revenue tracking across major social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import os


class IntegrationMethod(str, Enum):
    """Platform integration methods."""    API = "api"
    SCRAPING = "scraping"
    HYBRID = "hybrid"
    WEBHOOK = "webhook"


class AuthenticationMethod(str, Enum):
    """Authentication methods for platform integration."""    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class PlatformCapability(str, Enum):
    """Platform capabilities and features."""    CONTENT_UPLOAD = "content_upload"
    CONTENT_SEARCH = "content_search"
    CONTENT_DOWNLOAD = "content_download"
    METADATA_EXTRACTION = "metadata_extraction"
    USER_ANALYTICS = "user_analytics"
    DMCA_TAKEDOWN = "dmca_takedown"
    COPYRIGHT_CLAIM = "copyright_claim"
    REVENUE_TRACKING = "revenue_tracking"
    LIVE_MONITORING = "live_monitoring"
    BATCH_PROCESSING = "batch_processing"


class DataFormat(str, Enum):
    """Supported data formats for platform integration."""    JSON = "json"
    XML = "xml"
    RSS = "rss"
    CSV = "csv"
    ATOM = "atom"
    HTML = "html"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for platform APIs."""    requests_per_second: int = 1
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Burst handling
    burst_limit: int = 10
    burst_window_seconds: int = 60
    
    # Retry configuration
    retry_after_seconds: int = 60
    max_retries: int = 3
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0


@dataclass
class AuthConfig:
    """Authentication configuration for platform integration."""    method: AuthenticationMethod
    
    # OAuth2 settings
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    scope: Optional[List[str]] = None
    
    # API Key settings
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    # Token settings
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[int] = None
    
    # Custom headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Security settings
    enable_token_refresh: bool = True
    token_refresh_buffer_minutes: int = 10


@dataclass
class ContentFilterConfig:
    """Content filtering configuration for platform monitoring."""    # Content type filters
    include_audio: bool = True
    include_video: bool = True
    include_image: bool = True
    include_text: bool = True
    
    # Quality filters
    min_duration_seconds: Optional[int] = 30
    max_duration_seconds: Optional[int] = 3600
    min_resolution: Optional[str] = "480p"
    max_file_size_mb: Optional[int] = 500
    
    # Metadata filters
    required_tags: List[str] = field(default_factory=list)
    excluded_tags: List[str] = field(default_factory=list)
    min_views: Optional[int] = None
    min_likes: Optional[int] = None
    
    # Geographic filters
    allowed_countries: Optional[List[str]] = None
    blocked_countries: Optional[List[str]] = None
    
    # Language filters
    allowed_languages: Optional[List[str]] = None
    detect_language: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration for platform surveillance."""    # Monitoring intervals
    real_time_monitoring: bool = True
    batch_monitoring_interval_minutes: int = 60
    full_scan_interval_hours: int = 24
    
    # Monitoring scope
    monitor_user_uploads: bool = True
    monitor_public_content: bool = True
    monitor_trending_content: bool = True
    monitor_competitor_content: bool = False
    
    # Content discovery
    use_platform_search: bool = True
    use_hashtag_monitoring: bool = True
    use_user_mention_monitoring: bool = True
    use_content_similarity_search: bool = True
    
    # Alert thresholds
    similarity_threshold: float = 0.85
    volume_alert_threshold: int = 100
    velocity_alert_threshold: int = 10  # per hour


@dataclass
class DataExtractionConfig:
    """Data extraction configuration for platform content."""    # Metadata extraction
    extract_basic_metadata: bool = True
    extract_engagement_metrics: bool = True
    extract_user_information: bool = True
    extract_technical_metadata: bool = True
    
    # Content extraction
    download_original_content: bool = False
    download_thumbnails: bool = True
    extract_audio_from_video: bool = True
    extract_text_from_images: bool = True
    
    # Storage settings
    store_raw_data: bool = True
    compress_data: bool = True
    encrypt_sensitive_data: bool = True
    data_retention_days: int = 365


@dataclass
class ErrorHandlingConfig:
    """Error handling configuration for platform integration."""    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 1
    exponential_backoff: bool = True
    max_retry_delay_seconds: int = 300
    
    # Error classification
    transient_errors: List[str] = field(
        default_factory=lambda: ["timeout", "rate_limit", "server_error", "network_error"]
    )
    permanent_errors: List[str] = field(
        default_factory=lambda: ["authentication", "authorization", "not_found", "forbidden"]
    )
    
    # Error handling strategies
    continue_on_error: bool = True
    log_all_errors: bool = True
    alert_on_error: bool = True
    fallback_to_scraping: bool = False


@dataclass
class PlatformConfig:
    """Base platform configuration."""    platform_name: str
    platform_url: str
    integration_method: IntegrationMethod
    capabilities: Set[PlatformCapability] = field(default_factory=set)
    
    # API configuration
    api_base_url: Optional[str] = None
    api_version: Optional[str] = None
    data_format: DataFormat = DataFormat.JSON
    
    # Authentication
    auth_config: AuthConfig = field(default_factory=AuthConfig)
    
    # Component configurations
    rate_limit_config: RateLimitConfig = field(default_factory=RateLimitConfig)
    content_filter_config: ContentFilterConfig = field(default_factory=ContentFilterConfig)
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    data_extraction_config: DataExtractionConfig = field(default_factory=DataExtractionConfig)
    error_handling_config: ErrorHandlingConfig = field(default_factory=ErrorHandlingConfig)
    
    # Platform-specific settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def is_capable(self, capability: PlatformCapability) -> bool:
        """Check if platform supports a specific capability."""        return capability in self.capabilities


@dataclass
class YoutubeConfig(PlatformConfig):
    """YouTube platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "YouTube"
        self.platform_url = "https://youtube.com"
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.api_version = "v3"
        self.integration_method = IntegrationMethod.API
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.DMCA_TAKEDOWN,
            PlatformCapability.COPYRIGHT_CLAIM,
            PlatformCapability.REVENUE_TRACKING,
            PlatformCapability.LIVE_MONITORING
        }
        
        # YouTube-specific rate limits
        self.rate_limit_config.requests_per_day = 1000000
        self.rate_limit_config.requests_per_second = 100
        
        # YouTube-specific settings
        self.custom_settings = {
            "search_order": ["relevance", "date", "viewCount"],
            "content_regions": ["US", "GB", "CA", "AU", "DE", "FR"],
            "enable_content_id": True,
            "enable_live_streaming_api": True,
            "max_results_per_request": 50
        }


@dataclass
class InstagramConfig(PlatformConfig):
    """Instagram platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "Instagram"
        self.platform_url = "https://instagram.com"
        self.api_base_url = "https://graph.instagram.com"
        self.api_version = "v18.0"
        self.integration_method = IntegrationMethod.HYBRID
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.LIVE_MONITORING,
            PlatformCapability.BATCH_PROCESSING
        }
        
        # Instagram-specific rate limits
        self.rate_limit_config.requests_per_hour = 200
        self.rate_limit_config.requests_per_minute = 60
        
        # Instagram-specific settings
        self.custom_settings = {
            "media_types": ["image", "video", "carousel", "reel", "story"],
            "hashtag_monitoring": True,
            "story_monitoring": True,
            "reels_monitoring": True,
            "enable_business_api": True
        }


@dataclass
class TiktokConfig(PlatformConfig):
    """TikTok platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "TikTok"
        self.platform_url = "https://tiktok.com"
        self.api_base_url = "https://open-api.tiktok.com"
        self.api_version = "v1.3"
        self.integration_method = IntegrationMethod.HYBRID
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.LIVE_MONITORING
        }
        
        # TikTok-specific rate limits
        self.rate_limit_config.requests_per_minute = 10
        self.rate_limit_config.requests_per_hour = 100
        
        # TikTok-specific settings
        self.custom_settings = {
            "video_formats": ["mp4", "mov"],
            "max_video_duration": 180,
            "enable_music_detection": True,
            "enable_effect_detection": True,
            "trending_monitoring": True
        }


@dataclass
class TwitterConfig(PlatformConfig):
    """Twitter/X platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "Twitter"
        self.platform_url = "https://twitter.com"
        self.api_base_url = "https://api.twitter.com"
        self.api_version = "2"
        self.integration_method = IntegrationMethod.API
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.LIVE_MONITORING,
            PlatformCapability.DMCA_TAKEDOWN
        }
        
        # Twitter-specific rate limits
        self.rate_limit_config.requests_per_minute = 300
        self.rate_limit_config.requests_per_hour = 500
        
        # Twitter-specific settings
        self.custom_settings = {
            "tweet_types": ["text", "image", "video", "gif"],
            "enable_spaces_monitoring": True,
            "enable_fleets_monitoring": False,
            "real_time_streaming": True,
            "max_tweet_length": 280
        }


@dataclass
class SpotifyConfig(PlatformConfig):
    """Spotify platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "Spotify"
        self.platform_url = "https://spotify.com"
        self.api_base_url = "https://api.spotify.com"
        self.api_version = "v1"
        self.integration_method = IntegrationMethod.API
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.REVENUE_TRACKING
        }
        
        # Spotify-specific rate limits
        self.rate_limit_config.requests_per_second = 10
        self.rate_limit_config.requests_per_minute = 100
        
        # Spotify-specific settings
        self.custom_settings = {
            "audio_features": ["tempo", "energy", "danceability", "valence"],
            "market_codes": ["US", "GB", "DE", "FR", "ES", "IT"],
            "track_analysis": True,
            "playlist_monitoring": True
        }


@dataclass
class SoundcloudConfig(PlatformConfig):
    """SoundCloud platform integration configuration."""    
    def __post_init__(self):
        self.platform_name = "SoundCloud"
        self.platform_url = "https://soundcloud.com"
        self.api_base_url = "https://api.soundcloud.com"
        self.integration_method = IntegrationMethod.HYBRID
        self.capabilities = {
            PlatformCapability.CONTENT_SEARCH,
            PlatformCapability.METADATA_EXTRACTION,
            PlatformCapability.USER_ANALYTICS,
            PlatformCapability.LIVE_MONITORING
        }
        
        # SoundCloud-specific rate limits
        self.rate_limit_config.requests_per_hour = 15000
        self.rate_limit_config.requests_per_minute = 60
        
        # SoundCloud-specific settings
        self.custom_settings = {
            "audio_formats": ["mp3", "wav", "flac", "aac"],
            "max_track_duration": 7200,  # 2 hours
            "enable_waveform_data": True,
            "enable_reposts_tracking": True
        }


@dataclass
class PlatformIntegrationConfig:
    """Main configuration for platform integrations."""    
    # Enabled platforms
    enabled_platforms: Set[str] = field(
        default_factory=lambda: {"youtube", "instagram", "tiktok", "twitter", "spotify"}
    )
    
    # Platform configurations
    platforms: Dict[str, PlatformConfig] = field(default_factory=dict)
    
    # Global settings
    enable_parallel_processing: bool = True
    max_parallel_platforms: int = 5
    global_timeout_seconds: int = 300
    enable_failover: bool = True
    
    # Data management
    unified_data_format: bool = True
    enable_data_normalization: bool = True
    enable_cross_platform_correlation: bool = True
    
    # Monitoring settings
    enable_health_checks: bool = True
    health_check_interval_minutes: int = 5
    platform_status_cache_minutes: int = 15
    
    def __post_init__(self):
        """Initialize platform configurations."""        if not self.platforms:
            self._initialize_default_platforms()
    
    def _initialize_default_platforms(self):
        """Initialize default platform configurations."""        if "youtube" in self.enabled_platforms:
            self.platforms["youtube"] = YoutubeConfig()
        
        if "instagram" in self.enabled_platforms:
            self.platforms["instagram"] = InstagramConfig()
        
        if "tiktok" in self.enabled_platforms:
            self.platforms["tiktok"] = TiktokConfig()
        
        if "twitter" in self.enabled_platforms:
            self.platforms["twitter"] = TwitterConfig()
        
        if "spotify" in self.enabled_platforms:
            self.platforms["spotify"] = SpotifyConfig()
        
        if "soundcloud" in self.enabled_platforms:
            self.platforms["soundcloud"] = SoundcloudConfig()
    
    def get_platform_config(self, platform_name: str) -> Optional[PlatformConfig]:
        """Get configuration for a specific platform."""        return self.platforms.get(platform_name.lower())
    
    def is_platform_enabled(self, platform_name: str) -> bool:
        """Check if a platform is enabled."""        return platform_name.lower() in self.enabled_platforms
    
    def get_platforms_with_capability(self, capability: PlatformCapability) -> List[str]:
        """Get list of platforms that support a specific capability."""        platforms = []
        for name, config in self.platforms.items():
            if config.is_capable(capability):
                platforms.append(name)
        return platforms
    
    def validate_config(self) -> bool:
        """Validate the platform integration configuration."""        try:
            if not self.enabled_platforms:
                raise ValueError("At least one platform must be enabled")
            
            for platform_name in self.enabled_platforms:
                if platform_name not in self.platforms:
                    raise ValueError(f"Configuration missing for enabled platform: {platform_name}")
                
                platform_config = self.platforms[platform_name]
                if not platform_config.api_base_url and platform_config.integration_method == IntegrationMethod.API:
                    raise ValueError(f"API base URL required for platform: {platform_name}")
            
            if self.max_parallel_platforms <= 0:
                raise ValueError("Max parallel platforms must be positive")
            
            if self.global_timeout_seconds <= 0:
                raise ValueError("Global timeout must be positive")
            
            return True
            
        except Exception as e:
            print(f"Platform integration configuration validation error: {e}")
            return False
    
    @classmethod
    def from_environment(cls) -> 'PlatformIntegrationConfig':
        """Create configuration from environment variables."""        config = cls()
        
        # Load enabled platforms from environment
        enabled_platforms_env = os.getenv('ENABLED_PLATFORMS', 'youtube,instagram,tiktok')
        config.enabled_platforms = set(platform.strip() for platform in enabled_platforms_env.split(','))
        
        # Load global settings
        if os.getenv('MAX_PARALLEL_PLATFORMS'):
            config.max_parallel_platforms = int(os.getenv('MAX_PARALLEL_PLATFORMS'))
        
        if os.getenv('GLOBAL_TIMEOUT_SECONDS'):
            config.global_timeout_seconds = int(os.getenv('GLOBAL_TIMEOUT_SECONDS'))
        
        # Load platform-specific credentials
        for platform_name in config.enabled_platforms:
            platform_config = config.get_platform_config(platform_name)
            if platform_config:
                # Load API credentials from environment
                api_key_env = f'{platform_name.upper()}_API_KEY'
                if os.getenv(api_key_env):
                    platform_config.auth_config.api_key = os.getenv(api_key_env)
                
                client_id_env = f'{platform_name.upper()}_CLIENT_ID'
                if os.getenv(client_id_env):
                    platform_config.auth_config.client_id = os.getenv(client_id_env)
                
                client_secret_env = f'{platform_name.upper()}_CLIENT_SECRET'
                if os.getenv(client_secret_env):
                    platform_config.auth_config.client_secret = os.getenv(client_secret_env)
        
        return config


# Factory functions for different environments

def create_production_platform_config() -> PlatformIntegrationConfig:
    """Create production platform integration configuration."""    config = PlatformIntegrationConfig()
    
    # Production settings
    config.enable_parallel_processing = True
    config.max_parallel_platforms = 10
    config.enable_failover = True
    config.enable_health_checks = True
    
    # Configure platforms for production
    for platform_config in config.platforms.values():
        platform_config.monitoring_config.real_time_monitoring = True
        platform_config.error_handling_config.log_all_errors = True
        platform_config.error_handling_config.alert_on_error = True
        platform_config.data_extraction_config.encrypt_sensitive_data = True
    
    return config


def create_development_platform_config() -> PlatformIntegrationConfig:
    """Create development platform integration configuration."""    config = PlatformIntegrationConfig()
    
    # Development settings
    config.enabled_platforms = {"youtube"}  # Single platform for development
    config.max_parallel_platforms = 1
    config.enable_failover = False
    config.global_timeout_seconds = 60
    
    # Configure for development
    for platform_config in config.platforms.values():
        platform_config.rate_limit_config.requests_per_minute = 10
        platform_config.monitoring_config.real_time_monitoring = False
        platform_config.error_handling_config.continue_on_error = True
    
    return config


def create_testing_platform_config() -> PlatformIntegrationConfig:
    """Create testing platform integration configuration."""    config = PlatformIntegrationConfig()
    
    # Testing settings
    config.enabled_platforms = {"youtube"}
    config.max_parallel_platforms = 1
    config.enable_parallel_processing = False
    config.enable_health_checks = False
    
    # Configure for testing
    for platform_config in config.platforms.values():
        platform_config.rate_limit_config.requests_per_minute = 5
        platform_config.monitoring_config.batch_monitoring_interval_minutes = 1440  # Daily
        platform_config.error_handling_config.max_retries = 1
    
    return config
