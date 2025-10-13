#!/usr/bin/env python3
"""
🕷️ Crawler Configuration Module
===============================

Configuration settings for crawler components.

Author: Fahed Mlaiel (mlaiel@live.de)
Crawler Configuration Module
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import os

@dataclass
class CrawlerConfig:
    """Crawler system configuration."""
    
    # General Crawler Settings
    max_workers: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    delay_between_requests: float = 1.0
    
    # User Agent Configuration
    user_agents: List[str] = None
    rotate_user_agents: bool = True
    
    # Rate Limiting
    requests_per_second: float = 1.0

@dataclass
class CrawlerServiceConfig:
    """Configuration for crawler services."""
    
    # Service Configuration
    service_name: str = "crawler_service"
    service_port: int = 8080
    service_host: str = "localhost"
    
    # Database Configuration
    database_url: str = "sqlite:///crawler.db"
    redis_url: str = "redis://localhost:6379"
    
    # API Keys
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    # Crawler Settings
    crawler_config: CrawlerConfig = field(default_factory=CrawlerConfig)
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'CrawlerServiceConfig':
        """Create configuration from environment variables."""
        return cls(
            service_name=os.getenv('CRAWLER_SERVICE_NAME', 'crawler_service'),
            service_port=int(os.getenv('CRAWLER_SERVICE_PORT', '8080')),
            service_host=os.getenv('CRAWLER_SERVICE_HOST', 'localhost'),
            database_url=os.getenv('DATABASE_URL', 'sqlite:///crawler.db'),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE'),
            api_keys={
                'openai': os.getenv('OPENAI_API_KEY', ''),
                'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
                'google': os.getenv('GOOGLE_API_KEY', ''),
            }
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlerServiceConfig':
        """Create configuration from dictionary."""
        crawler_config_data = data.pop('crawler_config', {})
        crawler_config = CrawlerConfig(**crawler_config_data)
        
        return cls(
            crawler_config=crawler_config,
            **data
        )

@dataclass
class PlatformAPIConfig:
    """Platform API configuration."""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    youtube_api_key: str = ""
    instagram_access_token: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    soundcloud_client_id: str = ""
    soundcloud_client_secret: str = ""
    api_timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_buffer: float = 0.8  # Use 80% of rate limit

@dataclass
class DatabaseConfig:
    """Database configuration."""
    database_url: str = "sqlite:///protection.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

@dataclass
class CacheConfig:
    """Cache configuration."""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    ttl_seconds: int = 3600
    max_connections: int = 10

@dataclass
class SecuritySettings:
    """Security configuration settings."""
    enable_encryption: bool = True
    encryption_algorithm: str = "AES-256"
    key_rotation_interval: int = 86400  # 24 hours
    max_login_attempts: int = 3
    session_timeout: int = 3600  # 1 hour
    enable_two_factor: bool = True
    password_policy_min_length: int = 8
    enable_audit_logging: bool = True
    burst_requests: int = 5
    
    # Headers Configuration
    default_headers: Dict[str, str] = None
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    # Proxy Configuration
    proxy_enabled: bool = False
    proxy_list: List[str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
        
        if self.default_headers is None:
            self.default_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }

@dataclass
class MarketIntelligenceCrawlerConfig(CrawlerConfig):
    """Market intelligence crawler specific configuration."""
    
    # Market Intelligence Settings
    social_platforms: List[str] = None
    analysis_depth: str = "deep"
    trend_analysis_enabled: bool = True
    competitor_tracking_enabled: bool = True
    
    # AI Processing Settings
    ai_processing_enabled: bool = True
    sentiment_analysis_enabled: bool = True
    virality_prediction_enabled: bool = True
    
    def __post_init__(self):
        if self.social_platforms is None:
            self.social_platforms = [
                "twitter", "instagram", "tiktok", "youtube", 
                "linkedin", "facebook", "pinterest"
            ]

@dataclass
class CollaborationCrawlerConfig(CrawlerConfig):
    """Collaboration discovery crawler specific configuration."""
    
    # Collaboration Settings
    matchmaking_enabled: bool = True
    brand_partnership_enabled: bool = True
    influencer_network_enabled: bool = True
    roi_prediction_enabled: bool = True
    
    # Scoring Configuration
    matching_score_threshold: float = 0.7
    partnership_score_threshold: float = 0.8
    roi_prediction_threshold: float = 0.6

# Default configuration instances
default_crawler_config = CrawlerConfig()
default_market_intelligence_config = MarketIntelligenceCrawlerConfig()
default_collaboration_config = CollaborationCrawlerConfig()

def get_crawler_config(crawler_type: str = "default") -> CrawlerConfig:
    """Get crawler configuration by type."""
    configs = {
        "default": default_crawler_config,
        "market_intelligence": default_market_intelligence_config,
        "collaboration": default_collaboration_config
    }
    return configs.get(crawler_type, default_crawler_config)

# Export configuration classes and functions
__all__ = [
    "CrawlerConfig",
    "MarketIntelligenceCrawlerConfig", 
    "CollaborationCrawlerConfig",
    "default_crawler_config",
    "default_market_intelligence_config",
    "default_collaboration_config",
    "get_crawler_config"
]