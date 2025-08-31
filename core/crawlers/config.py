"""
Crawler Configuration Management
===============================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  INTELLECTUAL PROPERTY WARNING 
Unauthorized use, copying or distribution prohibited.

Professional configuration management for web crawling operations.
Handles platform-specific settings, rate limiting, API credentials,
and monitoring thresholds for optimal crawling performance.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class CrawlerType(Enum):
    """Supported crawler types for content monitoring."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    GENERIC_WEB = "generic_web"

class ContentType(Enum):
    """Content types for fingerprint matching."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class PlatformConfig:
    """Configuration for individual platform crawlers."""
    
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    base_url: str = ""
    
    # Rate limiting configuration
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # Content detection settings
    supported_content_types: List[ContentType] = field(default_factory=list)
    similarity_threshold: float = 0.85
    
    # Custom headers and user agents
    user_agents: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)

@dataclass 
class CrawlerConfig:
    """Main configuration class for the crawling system."""
    
    # Global crawler settings
    concurrent_crawlers: int = 5
    max_workers_per_crawler: int = 10
    crawl_interval_minutes: int = 30
    
    # Database configuration
    database_url: str = ""
    redis_url: str = ""
    
    # Storage configuration
    evidence_storage_path: str = "/data/evidence"
    screenshot_storage_path: str = "/data/screenshots"
    
    # Monitoring configuration
    alert_webhook_url: Optional[str] = None
    notification_email: Optional[str] = None
    
    # AI/ML configuration
    fingerprint_model_path: str = "/models/fingerprinting"
    similarity_engine_url: str = ""
    
    # Platform configurations
    platforms: Dict[str, PlatformConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default platform configurations."""
        if not self.platforms:
            self._initialize_default_platforms()
    
    def _initialize_default_platforms(self):
        """Set up default configurations for supported platforms."""
        
        # YouTube configuration
        self.platforms[CrawlerType.YOUTUBE.value] = PlatformConfig(
            name="YouTube",
            base_url="https://www.googleapis.com/youtube/v3",
            api_key=os.getenv("YOUTUBE_API_KEY"),
            requests_per_minute=100,
            requests_per_hour=10000,
            supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
            similarity_threshold=0.90,
            user_agents=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            ]
        )
        
        # TikTok configuration
        self.platforms[CrawlerType.TIKTOK.value] = PlatformConfig(
            name="TikTok",
            base_url="https://www.tiktok.com",
            requests_per_minute=30,
            requests_per_hour=500,
            supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
            similarity_threshold=0.85,
            user_agents=[
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
                "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
            ]
        )
        
        # Instagram configuration  
        self.platforms[CrawlerType.INSTAGRAM.value] = PlatformConfig(
            name="Instagram",
            base_url="https://graph.instagram.com",
            api_key=os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            requests_per_minute=200,
            requests_per_hour=5000,
            supported_content_types=[ContentType.IMAGE, ContentType.VIDEO],
            similarity_threshold=0.88,
            user_agents=[
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
                "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36"
            ]
        )
        
        # Twitter configuration
        self.platforms[CrawlerType.TWITTER.value] = PlatformConfig(
            name="Twitter/X",
            base_url="https://api.twitter.com/2",
            api_key=os.getenv("TWITTER_API_KEY"),
            api_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            requests_per_minute=300,
            requests_per_hour=15000,
            supported_content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
            similarity_threshold=0.82,
            custom_headers={
                "Authorization": f"Bearer {os.getenv('TWITTER_BEARER_TOKEN')}"
            }
        )
        
        # Generic web crawler configuration
        self.platforms[CrawlerType.GENERIC_WEB.value] = PlatformConfig(
            name="Generic Web",
            requests_per_minute=20,
            requests_per_hour=300,
            supported_content_types=[ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE, ContentType.TEXT],
            similarity_threshold=0.80,
            user_agents=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
        )
    
    def get_platform_config(self, platform: CrawlerType) -> Optional[PlatformConfig]:
        """Get configuration for a specific platform."""



        return self.platforms.get(platform.value)
    
    def is_platform_enabled(self, platform: CrawlerType) -> bool:
        """Check if a platform crawler is enabled."""
        config = self.get_platform_config(platform)
        return config.enabled if config else False
    
    def get_similarity_threshold(self, platform: CrawlerType, content_type: ContentType) -> float:
        """Get similarity threshold for platform and content type combination."""
        config = self.get_platform_config(platform)
        if not config:
            return 0.80  # Default threshold
        
        # Content-specific threshold adjustments
        threshold_adjustments = {
            ContentType.AUDIO: 0.05,  # Higher threshold for audio
            ContentType.VIDEO: 0.02,  # Slightly higher for video
            ContentType.IMAGE: 0.0,   # Base threshold for images
            ContentType.TEXT: -0.05,  # Lower threshold for text
        }
        
        adjustment = threshold_adjustments.get(content_type, 0.0)
        return min(0.95, config.similarity_threshold + adjustment)
    
    @classmethod
    def from_environment(cls) -> 'CrawlerConfig':
        """Create configuration from environment variables."""



        return cls(
            concurrent_crawlers=int(os.getenv("CRAWLER_CONCURRENT_CRAWLERS", "5")),
            max_workers_per_crawler=int(os.getenv("CRAWLER_MAX_WORKERS", "10")),
            crawl_interval_minutes=int(os.getenv("CRAWLER_INTERVAL_MINUTES", "30")),
            database_url=os.getenv("DATABASE_URL", ""),
            redis_url=os.getenv("REDIS_URL", ""),
            evidence_storage_path=os.getenv("EVIDENCE_STORAGE_PATH", "/data/evidence"),
            screenshot_storage_path=os.getenv("SCREENSHOT_STORAGE_PATH", "/data/screenshots"),
            alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL"),
            notification_email=os.getenv("NOTIFICATION_EMAIL"),
            fingerprint_model_path=os.getenv("FINGERPRINT_MODEL_PATH", "/models/fingerprinting"),
            similarity_engine_url=os.getenv("SIMILARITY_ENGINE_URL", "")
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.database_url:
            errors.append("Database URL is required")
        
        if not self.redis_url:
            errors.append("Redis URL is required")
        
        if self.concurrent_crawlers < 1:
            errors.append("Concurrent crawlers must be at least 1")
        
        if self.crawl_interval_minutes < 5:
            errors.append("Crawl interval must be at least 5 minutes")
        
        # Validate platform configurations
        for platform_name, config in self.platforms.items():
            if config.enabled:
                if platform_name in [CrawlerType.YOUTUBE.value, CrawlerType.INSTAGRAM.value, CrawlerType.TWITTER.value]:
                    if not config.api_key:
                        errors.append(f"{config.name} API key is required when platform is enabled")
                
                if config.requests_per_minute < 1:
                    errors.append(f"{config.name} requests per minute must be at least 1")
                
                if config.similarity_threshold < 0.5 or config.similarity_threshold > 1.0:
                    errors.append(f"{config.name} similarity threshold must be between 0.5 and 1.0")
        
        return errors
