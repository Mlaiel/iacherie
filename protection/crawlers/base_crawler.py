"""
Enterprise Base Platform Crawler Infrastructure
=================================================

Enterprise-grade base crawler class providing comprehensive functionality for
multi-platform content crawling with advanced security, monitoring, and
performance optimization capabilities.

Key Features:
- Rate limiting and circuit breaker patterns
- Comprehensive monitoring and analytics
- Content deduplication and caching
- Anti-detection mechanisms
- Webhook integration
- Error handling and recovery
- Performance optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrawlerStatus(str, Enum):
    """Comprehensive crawler status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    INACTIVE = "inactive"
    RECOVERING = "recovering"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"


class ContentType(str, Enum):
    """Content type enumeration for standardized classification."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PLAYLIST = "playlist"
    CHANNEL = "channel"
    LIVESTREAM = "livestream"
    SHORTS = "shorts"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POST = "post"
    REEL = "reel"
    COMMENT = "comment"
    PODCAST = "podcast"
    METADATA = "metadata"
    ARTICLE = "article"
    PROFILE = "profile"


class Priority(str, Enum):
    """Task priority levels for intelligent scheduling."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"
    MEDIUM = "medium"
    BACKGROUND = "background"


class PlatformType(str, Enum):
    """Platform type enumeration for multi-platform support."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    SNAPCHAT = "snapchat"
    UNKNOWN = "unknown"


@dataclass
class CrawlResult:
    """Enhanced standardized crawl result structure with comprehensive metadata."""
    url: str
    content_type: ContentType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    retry_count: int = 0
    source_platform: str = ""
    content_id: Optional[str] = None
    size_bytes: int = 0
    encoding: str = "utf-8"
    language: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    content_hash: Optional[str] = None
    author_info: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []


@dataclass
class RateLimitInfo:
    """Rate limiting information and status."""
    requests_per_minute: int = 60
    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    backoff_until: Optional[datetime] = None
    is_limited: bool = False

    def reset_if_needed(self):
        """Reset rate limit window if needed."""
        now = datetime.now()
        if (now - self.window_start).total_seconds() >= 60:
            self.requests_made = 0
            self.window_start = now


class BasePlatformCrawler(ABC):
    """
    Abstract base class for enterprise platform crawlers.
    
    Provides comprehensive interface for multi-platform content discovery
    with industrial-strength monitoring, rate limiting, and analytics.
    """
    
    def __init__(self, platform_name: str, config: Dict[str, Any] = None):
        self.platform_name = platform_name
        self.config = config or {}
        self.status = CrawlerStatus.INACTIVE
        self.rate_limit = RateLimitInfo()
        self.session_id = hashlib.md5(f"{platform_name}_{time.time()}".encode()).hexdigest()
        self.logger = logging.getLogger(f"{__name__}.{platform_name}")
        
    @abstractmethod
    async def crawl(self, url: str, **kwargs) -> CrawlResult:
        """Abstract method for crawling content."""
        pass
    
    @abstractmethod
    async def get_metadata(self, content_id: str) -> Dict[str, Any]:
        """Abstract method for retrieving metadata."""
        pass
    
    def get_status(self) -> CrawlerStatus:
        """Get current crawler status."""
        return self.status
    
    def set_status(self, status: CrawlerStatus):
        """Set crawler status."""
        self.status = status
        self.logger.info(f"Status changed to: {status}")


@dataclass
class CrawlerConfig:
    """Configuration class for crawler settings."""
    rate_limit: int = 60
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "IA Chérie-Crawler/1.0"
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_monitoring: bool = True
    webhook_url: Optional[str] = None


@dataclass
class CrawlerMetrics:
    """Metrics tracking for crawler performance."""
    requests_made: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    average_response_time: float = 0.0
    total_data_processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_activity: Optional[datetime] = None
    uptime_seconds: float = 0.0
    error_rate: float = 0.0


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting behavior."""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_limit: int = 10
    backoff_factor: float = 2.0
    max_backoff_seconds: int = 300
    enable_adaptive_rate_limiting: bool = True
    respect_server_limits: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration for crawler operations."""
    enable_ssl_verification: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    enable_user_agent_rotation: bool = True
    proxy_list: List[str] = field(default_factory=list)
    enable_proxy_rotation: bool = False
    max_redirect_follow: int = 5
    enable_cookie_jar: bool = True
    enable_session_persistence: bool = True
    request_timeout: int = 30
    enable_retry_with_backoff: bool = True
    suspicious_response_detection: bool = True