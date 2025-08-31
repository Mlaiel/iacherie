"""Web Crawler Configuration Module
===============================

Professional web crawler configuration for content surveillance and monitoring.
Supports multi-platform crawling with industrial-grade reliability and compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import os


class CrawlerType(str, Enum):
    """Supported crawler types."""
    API_BASED = "api_based"
    SCRAPING = "scraping"
    HYBRID = "hybrid"


class Platform(str, Enum):
    """Supported platforms for content surveillance."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"


class CrawlingStrategy(str, Enum):
    """Crawling strategy types."""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    TARGETED = "targeted"
    SMART_PRIORITY = "smart_priority"


@dataclass
class PlatformCredentials:
    """API credentials for platform access."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    backoff_factor: float = 1.5
    max_backoff_seconds: int = 300
    respect_platform_limits: bool = True


@dataclass
class RetryConfig:
    """Retry configuration for failed requests."""
    max_retries: int = 3
    initial_delay: float = 1.0
    exponential_backoff: bool = True
    retry_on_status_codes: Set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    retry_on_exceptions: List[str] = field(default_factory=lambda: ["ConnectionError", "Timeout", "RequestException"])


@dataclass
class ScrapingConfig:
    """Web scraping configuration."""
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ])
    enable_javascript: bool = True
    page_load_timeout: int = 30
    element_wait_timeout: int = 10
    enable_images: bool = False
    enable_cookies: bool = True
    proxy_rotation: bool = True
    headless_mode: bool = True
    browser_pool_size: int = 3


@dataclass
class ContentFilterConfig:
    """Content filtering and selection configuration."""
    min_content_size_bytes: int = 1024
    max_content_size_bytes: int = 100 * 1024 * 1024  # 100MB
    allowed_content_types: Set[str] = field(default_factory=lambda: {
        "audio/mpeg", "audio/wav", "audio/ogg", "audio/flac",
        "video/mp4", "video/avi", "video/mov", "video/webm",
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "text/plain", "text/html", "application/json"
    })
    blocked_domains: Set[str] = field(default_factory=set)
    required_keywords: List[str] = field(default_factory=list)
    excluded_keywords: List[str] = field(default_factory=list)
    language_filters: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es"])


@dataclass
class StorageConfig:
    """Crawler storage configuration."""
    storage_backend: str = "s3"  # s3, local, gcs, azure
    bucket_name: str = "ia-influencer-crawled-content"
    local_storage_path: str = "/tmp/crawler_storage"
    compression_enabled: bool = True
    compression_algorithm: str = "gzip"
    encryption_enabled: bool = True
    retention_days: int = 90
    cleanup_enabled: bool = True


@dataclass
class MonitoringConfig:
    """Crawler monitoring and logging configuration."""
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    log_level: str = "INFO"
    enable_performance_tracking: bool = True
    enable_error_tracking: bool = True
    alert_on_failure_rate: float = 0.1  # 10%
    alert_on_latency_ms: int = 5000
    health_check_interval: int = 300


@dataclass
class YoutubeCrawlerConfig:
    """YouTube-specific crawler configuration."""
    api_version: str = "v3"
    search_order: str = "relevance"  # relevance, date, rating, viewCount
    max_results_per_query: int = 50
    video_duration_filter: str = "any"  # short, medium, long, any
    video_definition: str = "any"  # high, standard, any
    channel_crawl_enabled: bool = True
    playlist_crawl_enabled: bool = True
    comment_crawl_enabled: bool = False
    metadata_extraction: List[str] = field(default_factory=lambda: [
        "title", "description", "tags", "duration", "view_count", "like_count", "upload_date"
    ])


@dataclass
class TiktokCrawlerConfig:
    """TikTok-specific crawler configuration."""
    api_version: str = "v1"
    hashtag_search_enabled: bool = True
    user_profile_crawl: bool = True
    video_download_enabled: bool = True
    max_videos_per_user: int = 100
    trending_content_priority: bool = True
    metadata_extraction: List[str] = field(default_factory=lambda: [
        "title", "description", "hashtags", "play_count", "like_count", "share_count", "create_time"
    ])


@dataclass
class InstagramCrawlerConfig:
    """Instagram-specific crawler configuration."""
    api_version: str = "v12.0"
    story_crawl_enabled: bool = False
    reel_crawl_enabled: bool = True
    igtv_crawl_enabled: bool = True
    post_type_filters: List[str] = field(default_factory=lambda: ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"])
    hashtag_analysis: bool = True
    metadata_extraction: List[str] = field(default_factory=lambda: [
        "caption", "hashtags", "media_type", "like_count", "comment_count", "timestamp"
    ])


@dataclass
class TwitterCrawlerConfig:
    """Twitter/X-specific crawler configuration."""
    api_version: str = "2"
    tweet_fields: List[str] = field(default_factory=lambda: [
        "created_at", "public_metrics", "lang", "context_annotations", "entities"
    ])
    media_fields: List[str] = field(default_factory=lambda: [
        "duration_ms", "height", "media_key", "preview_image_url", "type", "url", "width"
    ])
    user_fields: List[str] = field(default_factory=lambda: [
        "created_at", "description", "entities", "location", "public_metrics", "verified"
    ])
    max_tweets_per_request: int = 100
    include_retweets: bool = False
    sentiment_analysis: bool = True


class WebCrawlerConfig:
    """
    Professional web crawler configuration manager.
    Provides industrial-grade configuration for multi-platform content surveillance.
    """
    
    def __init__(self):
        # General crawler configuration
        self.crawler_type = CrawlerType.HYBRID
        self.crawling_strategy = CrawlingStrategy.SMART_PRIORITY
        self.max_concurrent_crawlers = 10
        self.crawl_interval_minutes = 30
        self.enable_distributed_crawling = True
        
        # Platform configurations
        self.platforms: Dict[Platform, bool] = {
            Platform.YOUTUBE: True,
            Platform.TIKTOK: True,
            Platform.INSTAGRAM: True,
            Platform.TWITTER: True,
            Platform.FACEBOOK: False,  # Requires special permissions
            Platform.SPOTIFY: True,
            Platform.SOUNDCLOUD: True,
            Platform.TWITCH: False,
            Platform.PINTEREST: False,
            Platform.LINKEDIN: False,
            Platform.REDDIT: False,
            Platform.GENERIC_WEB: True
        }
        
        # Configuration components
        self.rate_limit = RateLimitConfig()
        self.retry = RetryConfig()
        self.scraping = ScrapingConfig()
        self.content_filter = ContentFilterConfig()
        self.storage = StorageConfig()
        self.monitoring = MonitoringConfig()
        
        # Platform-specific configurations
        self.youtube = YoutubeCrawlerConfig()
        self.tiktok = TiktokCrawlerConfig()
        self.instagram = InstagramCrawlerConfig()
        self.twitter = TwitterCrawlerConfig()
        
        # Credentials storage
        self.credentials: Dict[Platform, PlatformCredentials] = {}
        
        # Load environment configurations
        self._load_from_environment()
        self._load_credentials()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        self.max_concurrent_crawlers = int(os.getenv("CRAWLER_MAX_CONCURRENT", "10"))
        self.crawl_interval_minutes = int(os.getenv("CRAWLER_INTERVAL_MINUTES", "30"))
        
        # Rate limiting
        self.rate_limit.requests_per_minute = int(os.getenv("CRAWLER_RATE_LIMIT_MINUTE", "60"))
        self.rate_limit.requests_per_hour = int(os.getenv("CRAWLER_RATE_LIMIT_HOUR", "1000"))
        
        # Storage
        self.storage.bucket_name = os.getenv("CRAWLER_STORAGE_BUCKET", "ia-influencer-crawled-content")
        self.storage.retention_days = int(os.getenv("CRAWLER_RETENTION_DAYS", "90"))
        
        # Monitoring
        self.monitoring.log_level = os.getenv("CRAWLER_LOG_LEVEL", "INFO")
        self.monitoring.alert_on_failure_rate = float(os.getenv("CRAWLER_ALERT_FAILURE_RATE", "0.1"))
    
    def _load_credentials(self) -> None:
        """Load platform credentials from environment variables."""
        platforms = [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM, Platform.TWITTER, Platform.SPOTIFY]
        
        for platform in platforms:
            prefix = f"CRAWLER_{platform.upper()}_"
            credentials = PlatformCredentials(
                api_key=os.getenv(f"{prefix}API_KEY"),
                api_secret=os.getenv(f"{prefix}API_SECRET"),
                access_token=os.getenv(f"{prefix}ACCESS_TOKEN"),
                refresh_token=os.getenv(f"{prefix}REFRESH_TOKEN"),
                client_id=os.getenv(f"{prefix}CLIENT_ID"),
                client_secret=os.getenv(f"{prefix}CLIENT_SECRET"),
                bearer_token=os.getenv(f"{prefix}BEARER_TOKEN"),
                username=os.getenv(f"{prefix}USERNAME"),
                password=os.getenv(f"{prefix}PASSWORD")
            )
            
            # Only store credentials if at least one field is provided
            if any(getattr(credentials, field) for field in credentials.__dataclass_fields__):
                self.credentials[platform] = credentials
    
    def get_platform_config(self, platform: Platform) -> Dict[str, Any]:
        """Get configuration for specific platform."""
        platform_configs = {
            Platform.YOUTUBE: self.youtube.__dict__,
            Platform.TIKTOK: self.tiktok.__dict__,
            Platform.INSTAGRAM: self.instagram.__dict__,
            Platform.TWITTER: self.twitter.__dict__
        }
        
        base_config = {
            "enabled": self.platforms.get(platform, False),
            "rate_limit": self.rate_limit.__dict__,
            "retry": self.retry.__dict__,
            "content_filter": self.content_filter.__dict__,
            "storage": self.storage.__dict__
        }
        
        platform_specific = platform_configs.get(platform, {})
        base_config.update(platform_specific)
        
        return base_config
    
    def get_credentials(self, platform: Platform) -> Optional[PlatformCredentials]:
        """Get credentials for specific platform."""
        return self.credentials.get(platform)
    
    def set_credentials(self, platform: Platform, credentials: PlatformCredentials) -> None:
        """Set credentials for specific platform."""
        self.credentials[platform] = credentials
    
    def is_platform_enabled(self, platform: Platform) -> bool:
        """Check if platform is enabled for crawling."""
        return self.platforms.get(platform, False)
    
    def enable_platform(self, platform: Platform) -> None:
        """Enable crawling for specific platform."""
        self.platforms[platform] = True
    
    def disable_platform(self, platform: Platform) -> None:
        """Disable crawling for specific platform."""
        self.platforms[platform] = False
    
    def get_enabled_platforms(self) -> List[Platform]:
        """Get list of enabled platforms."""
        return [platform for platform, enabled in self.platforms.items() if enabled]
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # Check if at least one platform is enabled
        if not any(self.platforms.values()):
            issues.append("At least one platform must be enabled")
        
        # Validate rate limits
        if self.rate_limit.requests_per_minute <= 0:
            issues.append("Requests per minute must be positive")
        
        if self.rate_limit.requests_per_hour <= 0:
            issues.append("Requests per hour must be positive")
        
        # Validate concurrent crawlers
        if self.max_concurrent_crawlers <= 0:
            issues.append("Max concurrent crawlers must be positive")
        
        # Validate crawler interval
        if self.crawl_interval_minutes <= 0:
            issues.append("Crawl interval must be positive")
        
        # Check credentials for enabled platforms
        for platform, enabled in self.platforms.items():
            if enabled and platform != Platform.GENERIC_WEB:
                credentials = self.get_credentials(platform)
                if not credentials or not any(getattr(credentials, field) for field in credentials.__dataclass_fields__):
                    issues.append(f"No credentials provided for enabled platform: {platform}")
        
        # Validate storage configuration
        if not self.storage.bucket_name:
            issues.append("Storage bucket name is required")
        
        if self.storage.retention_days <= 0:
            issues.append("Retention days must be positive")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "crawler_type": self.crawler_type,
            "crawling_strategy": self.crawling_strategy,
            "max_concurrent_crawlers": self.max_concurrent_crawlers,
            "crawl_interval_minutes": self.crawl_interval_minutes,
            "enable_distributed_crawling": self.enable_distributed_crawling,
            "platforms": {k.value: v for k, v in self.platforms.items()},
            "rate_limit": self.rate_limit.__dict__,
            "retry": self.retry.__dict__,
            "scraping": self.scraping.__dict__,
            "content_filter": self.content_filter.__dict__,
            "storage": self.storage.__dict__,
            "monitoring": self.monitoring.__dict__,
            "youtube": self.youtube.__dict__,
            "tiktok": self.tiktok.__dict__,
            "instagram": self.instagram.__dict__,
            "twitter": self.twitter.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'WebCrawlerConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Load basic settings
        if "crawler_type" in config_dict:
            config.crawler_type = CrawlerType(config_dict["crawler_type"])
        if "crawling_strategy" in config_dict:
            config.crawling_strategy = CrawlingStrategy(config_dict["crawling_strategy"])
        if "max_concurrent_crawlers" in config_dict:
            config.max_concurrent_crawlers = config_dict["max_concurrent_crawlers"]
        if "crawl_interval_minutes" in config_dict:
            config.crawl_interval_minutes = config_dict["crawl_interval_minutes"]
        if "enable_distributed_crawling" in config_dict:
            config.enable_distributed_crawling = config_dict["enable_distributed_crawling"]
        
        # Load platform settings
        if "platforms" in config_dict:
            config.platforms = {Platform(k): v for k, v in config_dict["platforms"].items()}
        
        # Load component configurations
        component_map = {
            "rate_limit": config.rate_limit,
            "retry": config.retry,
            "scraping": config.scraping,
            "content_filter": config.content_filter,
            "storage": config.storage,
            "monitoring": config.monitoring,
            "youtube": config.youtube,
            "tiktok": config.tiktok,
            "instagram": config.instagram,
            "twitter": config.twitter
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        return config
