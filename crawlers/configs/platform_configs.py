"""
Platform-specific Crawler Configurations
=======================================

Advanced configuration system for platform-specific web crawlers.
Supports multi-platform content surveillance and violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

class PlatformType(Enum):
    """Supported platform types for content surveillance."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"

class ContentType(Enum):
    """Content types for surveillance and protection."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class AuthMethod(Enum):
    """Authentication methods for platform APIs."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    SESSION_COOKIES = "session_cookies"
    JWT = "jwt"
    NONE = "none"

class ScrapeMethod(Enum):
    """Scraping methods for content extraction."""
    API_OFFICIAL = "api_official"
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    REQUESTS = "requests"
    SCRAPY = "scrapy"
    PUPPETEER = "puppeteer"

@dataclass
class RateLimitConfig:
    """Rate limiting configuration for platform crawlers."""
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_limit: int = 10
    backoff_factor: float = 2.0
    max_retries: int = 3
    retry_delay: float = 5.0
    respect_429_headers: bool = True
    custom_delays: Dict[str, float] = field(default_factory=dict)

@dataclass
class ProxyConfig:
    """Proxy configuration for crawler anonymity."""
    enabled: bool = True
    rotation_enabled: bool = True
    proxy_list: List[str] = field(default_factory=list)
    proxy_type: str = "http"  # http, https, socks4, socks5
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    health_check_url: str = "https://httpbin.org/ip"
    timeout_seconds: int = 30
    max_failures: int = 3

@dataclass
class UserAgentConfig:
    """User-Agent rotation configuration."""
    enabled: bool = True
    rotation_enabled: bool = True
    custom_agents: List[str] = field(default_factory=list)
    browser_types: List[str] = field(default_factory=lambda: ["chrome", "firefox", "safari", "edge"])
    mobile_enabled: bool = True
    desktop_enabled: bool = True
    update_frequency_hours: int = 24

@dataclass
class ContentExtractionConfig:
    """Content extraction configuration."""
    extract_metadata: bool = True
    extract_thumbnails: bool = True
    extract_transcripts: bool = True
    extract_comments: bool = True
    extract_engagement_metrics: bool = True
    extract_author_info: bool = True
    extract_publication_date: bool = True
    max_content_size_mb: int = 100
    supported_formats: List[str] = field(default_factory=lambda: ["mp4", "mp3", "jpg", "png", "gif", "webp"])

@dataclass
class PlatformAPIConfig:
    """Platform API configuration."""
    api_base_url: str
    api_version: str = "v1"
    auth_method: AuthMethod = AuthMethod.API_KEY
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    scope: List[str] = field(default_factory=list)
    redirect_uri: Optional[str] = None
    token_expiry: Optional[int] = None
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

@dataclass
class PlatformScrapingConfig:
    """Platform scraping configuration."""
    scrape_method: ScrapeMethod = ScrapeMethod.REQUESTS
    base_urls: List[str] = field(default_factory=list)
    search_endpoints: Dict[str, str] = field(default_factory=dict)
    content_selectors: Dict[str, str] = field(default_factory=dict)
    pagination_selectors: Dict[str, str] = field(default_factory=dict)
    anti_bot_detection: bool = True
    javascript_rendering: bool = False
    wait_for_elements: bool = True
    implicit_wait_seconds: int = 10
    page_load_timeout_seconds: int = 30
    screenshot_on_error: bool = True

@dataclass
class ViolationDetectionConfig:
    """Violation detection configuration."""
    enabled: bool = True
    similarity_threshold: float = 0.85
    fingerprint_matching: bool = True
    audio_fingerprinting: bool = True
    video_fingerprinting: bool = True
    image_fingerprinting: bool = True
    text_similarity: bool = True
    metadata_matching: bool = True
    real_time_alerts: bool = True
    alert_webhooks: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=lambda: ["email", "webhook", "dashboard"])

@dataclass
class PlatformConfig:
    """Complete platform configuration."""
    platform: PlatformType
    enabled: bool = True
    priority: int = 1  # 1=highest, 5=lowest
    supported_content_types: List[ContentType] = field(default_factory=lambda: [ContentType.MIXED])
    
    # API Configuration
    api_config: Optional[PlatformAPIConfig] = None
    
    # Scraping Configuration
    scraping_config: PlatformScrapingConfig = field(default_factory=PlatformScrapingConfig)
    
    # Network Configuration
    proxy_config: ProxyConfig = field(default_factory=ProxyConfig)
    user_agent_config: UserAgentConfig = field(default_factory=UserAgentConfig)
    
    # Content Configuration
    content_extraction: ContentExtractionConfig = field(default_factory=ContentExtractionConfig)
    violation_detection: ViolationDetectionConfig = field(default_factory=ViolationDetectionConfig)
    
    # Monitoring Configuration
    monitoring_enabled: bool = True
    health_check_interval_seconds: int = 300
    performance_metrics_enabled: bool = True
    error_reporting_enabled: bool = True
    
    # Storage Configuration
    data_retention_days: int = 90
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    backup_enabled: bool = True

class PlatformConfigManager:
    """Manager for platform configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize platform config manager."""
        self.config_dir = Path(config_dir or os.getenv("CRAWLER_CONFIG_DIR", "./configs"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._configs: Dict[PlatformType, PlatformConfig] = {}
        self._load_default_configs()
    
    def _load_default_configs(self) -> None:
        """Load default platform configurations."""
        # Load YouTube configuration
        self._configs[PlatformType.YOUTUBE] = PlatformConfig(
            platform=PlatformType.YOUTUBE,
            enabled=True,
            priority=1,
            supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
            api_config=PlatformAPIConfig(
                api_base_url="https://www.googleapis.com/youtube/v3",
                api_version="v3",
                auth_method=AuthMethod.API_KEY,
                api_key=os.getenv("YOUTUBE_API_KEY"),
                scope=["https://www.googleapis.com/auth/youtube.readonly"],
                rate_limit=RateLimitConfig(
                    requests_per_second=0.5,
                    requests_per_minute=30,
                    requests_per_hour=1800
                )
            ),
            scraping_config=PlatformScrapingConfig(
                scrape_method=ScrapeMethod.API_OFFICIAL,
                base_urls=["https://www.youtube.com"],
                search_endpoints={
                    "search": "/search",
                    "video_details": "/watch"
                },
                content_selectors={
                    "video_title": "h1.title",
                    "video_description": "#description",
                    "view_count": "#count .view-count",
                    "upload_date": "#date",
                    "author": "#owner-name"
                }
            ),
            violation_detection=ViolationDetectionConfig(
                similarity_threshold=0.90,
                audio_fingerprinting=True,
                video_fingerprinting=True
            )
        )
        
        # Load Instagram configuration
        self._configs[PlatformType.INSTAGRAM] = PlatformConfig(
            platform=PlatformType.INSTAGRAM,
            enabled=True,
            priority=1,
            supported_content_types=[ContentType.IMAGE, ContentType.VIDEO],
            api_config=PlatformAPIConfig(
                api_base_url="https://graph.instagram.com",
                api_version="v18.0",
                auth_method=AuthMethod.OAUTH2,
                access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
                scope=["instagram_basic", "instagram_content_publish"],
                rate_limit=RateLimitConfig(
                    requests_per_second=0.2,
                    requests_per_minute=12,
                    requests_per_hour=720
                )
            ),
            scraping_config=PlatformScrapingConfig(
                scrape_method=ScrapeMethod.SELENIUM,
                base_urls=["https://www.instagram.com"],
                javascript_rendering=True,
                anti_bot_detection=True,
                wait_for_elements=True
            )
        )
        
        # Load TikTok configuration
        self._configs[PlatformType.TIKTOK] = PlatformConfig(
            platform=PlatformType.TIKTOK,
            enabled=True,
            priority=1,
            supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
            scraping_config=PlatformScrapingConfig(
                scrape_method=ScrapeMethod.PLAYWRIGHT,
                base_urls=["https://www.tiktok.com"],
                javascript_rendering=True,
                anti_bot_detection=True,
                implicit_wait_seconds=15
            ),
            violation_detection=ViolationDetectionConfig(
                similarity_threshold=0.88,
                video_fingerprinting=True,
                audio_fingerprinting=True
            )
        )
        
        # Load Twitter/X configuration
        self._configs[PlatformType.TWITTER] = PlatformConfig(
            platform=PlatformType.TWITTER,
            enabled=True,
            priority=2,
            supported_content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
            api_config=PlatformAPIConfig(
                api_base_url="https://api.twitter.com",
                api_version="2",
                auth_method=AuthMethod.BEARER_TOKEN,
                access_token=os.getenv("TWITTER_BEARER_TOKEN"),
                rate_limit=RateLimitConfig(
                    requests_per_second=0.1,
                    requests_per_minute=6,
                    requests_per_hour=360
                )
            )
        )
        
        # Load Spotify configuration
        self._configs[PlatformType.SPOTIFY] = PlatformConfig(
            platform=PlatformType.SPOTIFY,
            enabled=True,
            priority=1,
            supported_content_types=[ContentType.AUDIO],
            api_config=PlatformAPIConfig(
                api_base_url="https://api.spotify.com",
                api_version="v1",
                auth_method=AuthMethod.OAUTH2,
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                scope=["user-read-private", "playlist-read-private"],
                rate_limit=RateLimitConfig(
                    requests_per_second=0.5,
                    requests_per_minute=30,
                    requests_per_hour=1800
                )
            ),
            violation_detection=ViolationDetectionConfig(
                similarity_threshold=0.95,
                audio_fingerprinting=True,
                metadata_matching=True
            )
        )
    
    def get_config(self, platform: PlatformType) -> Optional[PlatformConfig]:
        """Get configuration for specific platform."""



        return self._configs.get(platform)
    
    def get_enabled_configs(self) -> Dict[PlatformType, PlatformConfig]:
        """Get all enabled platform configurations."""



        return {
            platform: config 
            for platform, config in self._configs.items() 
            if config.enabled
        }
    
    def update_config(self, platform: PlatformType, config: PlatformConfig) -> None:
        """Update platform configuration."""
        self._configs[platform] = config
        self.save_config(platform)
    
    def save_config(self, platform: PlatformType) -> None:
        """Save platform configuration to file."""
        config = self._configs.get(platform)
        if config:
            config_file = self.config_dir / f"{platform.value}_config.json"
            with open(config_file, 'w') as f:
                json.dump(config.__dict__, f, indent=2, default=str)
    
    def load_config(self, platform: PlatformType) -> Optional[PlatformConfig]:
        """Load platform configuration from file."""
        config_file = self.config_dir / f"{platform.value}_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                # Convert back to PlatformConfig object
                # This would need proper deserialization logic
                return self._deserialize_config(data)
        return None
    
    def _deserialize_config(self, data: dict) -> PlatformConfig:
        """Deserialize configuration data to PlatformConfig object."""
        # Implementation for converting dict back to PlatformConfig
        # This would include proper enum conversion and nested object creation
        pass
    
    def validate_config(self, config: PlatformConfig) -> List[str]:
        """Validate platform configuration."""
        errors = []
        
        if not config.platform:
            errors.append("Platform type is required")
        
        if config.api_config:
            if not config.api_config.api_base_url:
                errors.append("API base URL is required")
            
            if config.api_config.auth_method == AuthMethod.API_KEY and not config.api_config.api_key:
                errors.append("API key is required for API key authentication")
            
            if config.api_config.auth_method == AuthMethod.OAUTH2:
                if not config.api_config.client_id or not config.api_config.client_secret:
                    errors.append("Client ID and secret are required for OAuth2")
        
        if config.violation_detection.similarity_threshold < 0 or config.violation_detection.similarity_threshold > 1:
            errors.append("Similarity threshold must be between 0 and 1")
        
        return errors
    
    def export_configs(self, file_path: str) -> None:
        """Export all configurations to a single file."""
        export_data = {
            platform.value: config.__dict__ 
            for platform, config in self._configs.items()
        }
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def import_configs(self, file_path: str) -> None:
        """Import configurations from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            for platform_name, config_data in data.items():
                platform = PlatformType(platform_name)
                config = self._deserialize_config(config_data)
                self._configs[platform] = config

# Global platform config manager instance
platform_config_manager = PlatformConfigManager()
