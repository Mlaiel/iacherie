"""Platform API Cache Configuration for IA-Influencer Agent Platform
================================================================

Professional caching system for external platform APIs including Spotify, YouTube, 
Instagram, TikTok, and other content platforms with intelligent rate limiting and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, Optional, List, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime, timedelta
from pydantic import BaseModel, validator


class PlatformType(str, Enum):
    """Supported external platforms"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"


class APIEndpointType(str, Enum):
    """Types of API endpoints"""
    # User data endpoints
    USER_PROFILE = "user_profile"
    USER_ANALYTICS = "user_analytics"
    USER_CONTENT = "user_content"
    
    # Content endpoints  
    CONTENT_METADATA = "content_metadata"
    CONTENT_ANALYTICS = "content_analytics"
    CONTENT_SEARCH = "content_search"
    CONTENT_UPLOAD = "content_upload"
    
    # Revenue endpoints
    REVENUE_DATA = "revenue_data"
    MONETIZATION_STATUS = "monetization_status"
    PAYMENT_INFO = "payment_info"
    
    # Social endpoints
    FOLLOWERS_DATA = "followers_data"
    ENGAGEMENT_METRICS = "engagement_metrics"
    COLLABORATION_DATA = "collaboration_data"
    
    # Search and discovery
    TRENDING_CONTENT = "trending_content"
    RECOMMENDATIONS = "recommendations"
    HASHTAG_DATA = "hashtag_data"


class CacheDataType(str, Enum):
    """Types of data being cached"""
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    TEXT = "text"
    MEDIA_METADATA = "media_metadata"
    ANALYTICS_DATA = "analytics_data"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for platform APIs"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    retry_after_seconds: int = 60
    backoff_multiplier: float = 2.0
    max_retries: int = 3


@dataclass
class PlatformAPISettings:
    """Cache settings for individual platform API"""
    platform: PlatformType
    endpoint_type: APIEndpointType
    data_type: CacheDataType
    ttl_seconds: int = 3600  # 1 hour default
    max_cache_size_mb: int = 100
    compression_enabled: bool = True
    encryption_required: bool = False
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    priority: int = 3  # 1=highest, 5=lowest
    stale_while_revalidate: bool = True
    stale_if_error: bool = True
    background_refresh: bool = False


@dataclass
class PlatformAPICacheConfig:
    """Complete configuration for platform API caching"""
    
    # Cache identification
    cache_name: str = "platform_apis"
    namespace: str = "ia_influencer_api"
    tenant_id: Optional[str] = None
    
    # Storage configuration
    redis_key_prefix: str = "api"
    default_ttl_seconds: int = 3600
    max_total_cache_size_mb: int = 2048  # 2GB
    
    # Performance settings
    concurrent_requests_limit: int = 50
    request_timeout_seconds: int = 30
    connection_pool_size: int = 100
    keepalive_enabled: bool = True
    
    # Spotify API configuration
    spotify_config: Dict[str, PlatformAPISettings] = field(default_factory=lambda: {
        "user_profile": PlatformAPISettings(
            platform=PlatformType.SPOTIFY,
            endpoint_type=APIEndpointType.USER_PROFILE,
            data_type=CacheDataType.JSON,
            ttl_seconds=7200,  # 2 hours
            priority=1,
            rate_limit=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=3000,
                requests_per_day=50000
            )
        ),
        "user_analytics": PlatformAPISettings(
            platform=PlatformType.SPOTIFY,
            endpoint_type=APIEndpointType.USER_ANALYTICS,
            data_type=CacheDataType.ANALYTICS_DATA,
            ttl_seconds=1800,  # 30 minutes
            priority=1,
            background_refresh=True,
            rate_limit=RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=2000,
                requests_per_day=30000
            )
        ),
        "content_metadata": PlatformAPISettings(
            platform=PlatformType.SPOTIFY,
            endpoint_type=APIEndpointType.CONTENT_METADATA,
            data_type=CacheDataType.MEDIA_METADATA,
            ttl_seconds=14400,  # 4 hours
            priority=2,
            rate_limit=RateLimitConfig(
                requests_per_minute=80,
                requests_per_hour=2500,
                requests_per_day=40000
            )
        )
    })
    
    # YouTube API configuration
    youtube_config: Dict[str, PlatformAPISettings] = field(default_factory=lambda: {
        "analytics": PlatformAPISettings(
            platform=PlatformType.YOUTUBE,
            endpoint_type=APIEndpointType.CONTENT_ANALYTICS,
            data_type=CacheDataType.ANALYTICS_DATA,
            ttl_seconds=900,  # 15 minutes
            priority=1,
            background_refresh=True,
            rate_limit=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=10000,
                requests_per_day=1000000  # YouTube has high limits
            )
        ),
        "revenue_data": PlatformAPISettings(
            platform=PlatformType.YOUTUBE,
            endpoint_type=APIEndpointType.REVENUE_DATA,
            data_type=CacheDataType.JSON,
            ttl_seconds=3600,  # 1 hour
            priority=1,
            encryption_required=True,
            rate_limit=RateLimitConfig(
                requests_per_minute=50,
                requests_per_hour=1000,
                requests_per_day=10000
            )
        )
    })
    
    # Instagram API configuration  
    instagram_config: Dict[str, PlatformAPISettings] = field(default_factory=lambda: {
        "insights": PlatformAPISettings(
            platform=PlatformType.INSTAGRAM,
            endpoint_type=APIEndpointType.ENGAGEMENT_METRICS,
            data_type=CacheDataType.ANALYTICS_DATA,
            ttl_seconds=1800,  # 30 minutes
            priority=2,
            rate_limit=RateLimitConfig(
                requests_per_minute=200,  # Instagram has good limits
                requests_per_hour=5000,
                requests_per_day=100000
            )
        ),
        "content_search": PlatformAPISettings(
            platform=PlatformType.INSTAGRAM,
            endpoint_type=APIEndpointType.CONTENT_SEARCH,
            data_type=CacheDataType.JSON,
            ttl_seconds=600,  # 10 minutes
            priority=3,
            rate_limit=RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=2000,
                requests_per_day=30000
            )
        )
    })
    
    # TikTok API configuration
    tiktok_config: Dict[str, PlatformAPISettings] = field(default_factory=lambda: {
        "user_info": PlatformAPISettings(
            platform=PlatformType.TIKTOK,
            endpoint_type=APIEndpointType.USER_PROFILE,
            data_type=CacheDataType.JSON,
            ttl_seconds=3600,  # 1 hour
            priority=2,
            rate_limit=RateLimitConfig(
                requests_per_minute=20,  # TikTok has stricter limits
                requests_per_hour=500,
                requests_per_day=10000
            )
        ),
        "video_analytics": PlatformAPISettings(
            platform=PlatformType.TIKTOK,
            endpoint_type=APIEndpointType.CONTENT_ANALYTICS,
            data_type=CacheDataType.ANALYTICS_DATA,
            ttl_seconds=1800,  # 30 minutes  
            priority=2,
            rate_limit=RateLimitConfig(
                requests_per_minute=15,
                requests_per_hour=300,
                requests_per_day=5000
            )
        )
    })
    
    # Security and access control
    api_key_encryption: bool = True
    oauth_token_encryption: bool = True
    request_signing_enabled: bool = True
    audit_api_calls: bool = True
    
    # Monitoring and metrics
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    error_tracking: bool = True
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "cache_hit_rate_min": 0.70,
        "response_time_max_ms": 2000,
        "error_rate_max": 0.05,
        "rate_limit_usage_max": 0.80,
        "quota_usage_max": 0.90
    })

    def get_cache_key(self, platform: PlatformType, endpoint: APIEndpointType, 
                      user_id: str, params_hash: str) -> str:
        """Generate standardized cache key for API response"""
        key_components = [
            self.redis_key_prefix,
            self.namespace,
            platform.value,
            endpoint.value,
            user_id,
            params_hash
        ]
        if self.tenant_id:
            key_components.insert(-2, self.tenant_id)
        return ":".join(key_components)
    
    def get_all_platform_configs(self) -> Dict[str, PlatformAPISettings]:
        """Get all configured platform API settings"""
        all_configs = {}
        all_configs.update(self.spotify_config)
        all_configs.update(self.youtube_config)
        all_configs.update(self.instagram_config)
        all_configs.update(self.tiktok_config)
        return all_configs
    
    def get_settings_for_platform_endpoint(self, platform: PlatformType, 
                                         endpoint: APIEndpointType) -> Optional[PlatformAPISettings]:
        """Get cache settings for specific platform and endpoint"""
        all_configs = self.get_all_platform_configs()
        for config in all_configs.values():
            if config.platform == platform and config.endpoint_type == endpoint:
                return config
        return None


class PlatformAPICacheManager:
    """Manager for platform API cache operations"""
    
    def __init__(self, config: PlatformAPICacheConfig):
        self.config = config
        self._rate_limit_counters = {}
        self._performance_metrics = {}
        self._api_quotas = {}
    
    def generate_params_hash(self, params: Dict[str, Any]) -> str:
        """Generate consistent hash for API parameters"""
        # Sort parameters for consistent hashing
        sorted_params = sorted(params.items())
        params_str = str(sorted_params)
        return hashlib.sha256(params_str.encode()).hexdigest()[:16]
    
    def check_rate_limit(self, platform: PlatformType, endpoint: APIEndpointType) -> bool:
        """Check if request is within rate limits"""
        settings = self.config.get_settings_for_platform_endpoint(platform, endpoint)
        if not settings:
            return True
            
        key = f"{platform.value}:{endpoint.value}"
        current_time = datetime.now()
        
        # Initialize counters if not exists
        if key not in self._rate_limit_counters:
            self._rate_limit_counters[key] = {
                "minute": {"count": 0, "reset_time": current_time + timedelta(minutes=1)},
                "hour": {"count": 0, "reset_time": current_time + timedelta(hours=1)},
                "day": {"count": 0, "reset_time": current_time + timedelta(days=1)}
            }
        
        counters = self._rate_limit_counters[key]
        
        # Reset counters if time windows have passed
        for period in ["minute", "hour", "day"]:
            if current_time >= counters[period]["reset_time"]:
                counters[period]["count"] = 0
                if period == "minute":
                    counters[period]["reset_time"] = current_time + timedelta(minutes=1)
                elif period == "hour":
                    counters[period]["reset_time"] = current_time + timedelta(hours=1)
                else:  # day
                    counters[period]["reset_time"] = current_time + timedelta(days=1)
        
        # Check limits
        rate_limit = settings.rate_limit
        if (counters["minute"]["count"] >= rate_limit.requests_per_minute or
            counters["hour"]["count"] >= rate_limit.requests_per_hour or
            counters["day"]["count"] >= rate_limit.requests_per_day):
            return False
        
        return True
    
    def record_api_call(self, platform: PlatformType, endpoint: APIEndpointType):
        """Record an API call for rate limiting"""
        key = f"{platform.value}:{endpoint.value}"
        if key in self._rate_limit_counters:
            for period in ["minute", "hour", "day"]:
                self._rate_limit_counters[key][period]["count"] += 1
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive API cache statistics"""
        return {
            "total_platforms": len(set(config.platform for config in self.config.get_all_platform_configs().values())),
            "total_endpoints": len(self.config.get_all_platform_configs()),
            "cache_hit_rate": self._performance_metrics.get("cache_hit_rate", 0.0),
            "avg_response_time_ms": self._performance_metrics.get("avg_response_time", 0.0),
            "rate_limit_status": self._get_rate_limit_status(),
            "quota_usage": self._api_quotas,
            "error_rate": self._performance_metrics.get("error_rate", 0.0),
            "background_refresh_jobs": self._performance_metrics.get("background_jobs", 0)
        }
    
    def _get_rate_limit_status(self) -> Dict[str, Dict[str, int]]:
        """Get current rate limit status for all platforms"""
        status = {}
        for key, counters in self._rate_limit_counters.items():
            status[key] = {
                "requests_this_minute": counters["minute"]["count"],
                "requests_this_hour": counters["hour"]["count"],
                "requests_this_day": counters["day"]["count"]
            }
        return status


# Environment-specific configurations
DEVELOPMENT_CONFIG = PlatformAPICacheConfig(
    cache_name="dev_platform_apis",
    max_total_cache_size_mb=256,  # Smaller for dev
    concurrent_requests_limit=10,
    api_key_encryption=False,
    oauth_token_encryption=False,
    audit_api_calls=False,
    performance_monitoring=False
)

TESTING_CONFIG = PlatformAPICacheConfig(
    cache_name="test_platform_apis",
    max_total_cache_size_mb=128,  # Minimal for tests
    concurrent_requests_limit=5,
    default_ttl_seconds=300,  # Shorter TTL for tests
    api_key_encryption=False,
    metrics_enabled=False,
    error_tracking=False
)

PRODUCTION_CONFIG = PlatformAPICacheConfig(
    cache_name="prod_platform_apis",
    max_total_cache_size_mb=8192,  # 8GB for production
    concurrent_requests_limit=200,
    api_key_encryption=True,
    oauth_token_encryption=True,
    request_signing_enabled=True,
    audit_api_calls=True,
    performance_monitoring=True,
    error_tracking=True
)

# Export main classes
__all__ = [
    'PlatformType',
    'APIEndpointType',
    'CacheDataType',
    'RateLimitConfig',
    'PlatformAPISettings',
    'PlatformAPICacheConfig',
    'PlatformAPICacheManager',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'PRODUCTION_CONFIG'
]
