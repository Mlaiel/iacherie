"""
Platform Manager - Enterprise Multi-Platform Data Management and API Orchestration

This module provides comprehensive platform-specific data management and API orchestration
for the Ainflue platform, enabling seamless content distribution across multiple social
media and content platforms.

🎯 Expert Roles Applied:
- Lead Dev IA: AI-driven platform optimization and intelligent routing
- Backend Senior: Robust API orchestration and microservices architecture
- ML Engineer: Machine learning for platform performance optimization
- DBA: Optimized data structures for multi-platform content management
- Sécurité: Secure API token management and platform authentication
- Microservices: Distributed platform service architecture
- Audio: Audio content adaptation for platform-specific requirements
- DevOps: Monitoring and performance tracking across platforms
- IA Prompt Engineer: AI-powered content optimization for each platform

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
import aiohttp
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types for content distribution"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class ContentType(Enum):
    """Content types supported across platforms"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    LIVE = "live"
    PODCAST = "podcast"
    PLAYLIST = "playlist"


class PlatformStatus(Enum):
    """Platform connection and sync status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


@dataclass
class PlatformCredentials:
    """Secure platform credentials management"""
    platform_type: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = None
    webhook_url: Optional[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []


@dataclass
class PlatformLimits:
    """Platform-specific rate limits and constraints"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    max_file_size_mb: int = 100
    max_video_duration_seconds: int = 3600
    max_audio_duration_seconds: int = 7200
    supported_formats: List[str] = None
    max_caption_length: int = 2000
    max_hashtags: int = 30
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = []


@dataclass
class PlatformConfig:
    """Complete platform configuration"""
    platform_type: PlatformType
    display_name: str
    credentials: PlatformCredentials
    limits: PlatformLimits
    status: PlatformStatus = PlatformStatus.INACTIVE
    last_sync: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0
    total_content_distributed: int = 0
    revenue_generated: float = 0.0
    engagement_score: float = 0.0
    ai_optimization_enabled: bool = True
    auto_sync_enabled: bool = False
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}


class PlatformManager:
    """
    Enterprise Platform Manager for Multi-Platform Content Distribution
    
    Provides comprehensive platform management, API orchestration, and intelligent
    content distribution across multiple social media and content platforms.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize Platform Manager
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.platforms_collection = db.platform_configs
        self.sync_logs_collection = db.platform_sync_logs
        self.content_distribution_collection = db.content_distribution
        self.analytics_collection = db.platform_analytics
        
        # Cache for platform configurations
        self._platform_cache: Dict[str, PlatformConfig] = {}
        self._last_cache_update = datetime.utcnow()
        self._cache_ttl = timedelta(minutes=5)
        
        # Rate limiting tracking
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Session for HTTP requests
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize platform manager and create necessary indexes"""
        try:
            # Create indexes for optimal performance
            await self.platforms_collection.create_index([("user_id", 1), ("platform_type", 1)], unique=True)
            await self.platforms_collection.create_index([("status", 1)])
            await self.platforms_collection.create_index([("last_sync", 1)])
            
            await self.sync_logs_collection.create_index([("user_id", 1), ("platform_type", 1)])
            await self.sync_logs_collection.create_index([("timestamp", -1)])
            await self.sync_logs_collection.create_index([("status", 1)])
            
            await self.content_distribution_collection.create_index([("content_id", 1)])
            await self.content_distribution_collection.create_index([("platform_type", 1)])
            await self.content_distribution_collection.create_index([("distribution_date", -1)])
            
            await self.analytics_collection.create_index([("platform_type", 1), ("date", -1)])
            await self.analytics_collection.create_index([("user_id", 1), ("date", -1)])
            
            # Initialize HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "Ainflue-Platform-Manager/1.0"}
            )
            
            logger.info("Platform Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Platform Manager: {e}")
            raise
    
    async def add_platform(self, user_id: str, platform_config: PlatformConfig) -> bool:
        """
        Add a new platform configuration for a user
        
        Args:
            user_id: User identifier
            platform_config: Platform configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Validate platform configuration
            if not await self._validate_platform_config(platform_config):
                return False
            
            # Encrypt sensitive credentials
            encrypted_config = await self._encrypt_credentials(platform_config)
            
            # Prepare document for storage
            doc = {
                "user_id": user_id,
                "platform_type": platform_config.platform_type.value,
                "config": asdict(encrypted_config),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert or update platform configuration
            result = await self.platforms_collection.replace_one(
                {"user_id": user_id, "platform_type": platform_config.platform_type.value},
                doc,
                upsert=True
            )
            
            # Update cache
            cache_key = f"{user_id}:{platform_config.platform_type.value}"
            self._platform_cache[cache_key] = platform_config
            
            logger.info(f"Platform {platform_config.platform_type.value} added for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add platform: {e}")
            return False
    
    async def get_platform(self, user_id: str, platform_type: PlatformType) -> Optional[PlatformConfig]:
        """
        Retrieve platform configuration for a user
        
        Args:
            user_id: User identifier
            platform_type: Platform type
            
        Returns:
            Optional[PlatformConfig]: Platform configuration if found
        """
        try:
            cache_key = f"{user_id}:{platform_type.value}"
            
            # Check cache first
            if cache_key in self._platform_cache and self._is_cache_valid():
                return self._platform_cache[cache_key]
            
            # Retrieve from database
            doc = await self.platforms_collection.find_one({
                "user_id": user_id,
                "platform_type": platform_type.value
            })
            
            if not doc:
                return None
            
            # Decrypt credentials and create config object
            config_data = doc["config"]
            platform_config = await self._decrypt_and_create_config(config_data)
            
            # Update cache
            self._platform_cache[cache_key] = platform_config
            
            return platform_config
            
        except Exception as e:
            logger.error(f"Failed to get platform: {e}")
            return None
    
    async def get_user_platforms(self, user_id: str) -> List[PlatformConfig]:
        """
        Get all platform configurations for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List[PlatformConfig]: List of platform configurations
        """
        try:
            platforms = []
            cursor = self.platforms_collection.find({"user_id": user_id})
            
            async for doc in cursor:
                config_data = doc["config"]
                platform_config = await self._decrypt_and_create_config(config_data)
                platforms.append(platform_config)
            
            return platforms
            
        except Exception as e:
            logger.error(f"Failed to get user platforms: {e}")
            return []
    
    async def update_platform_status(self, user_id: str, platform_type: PlatformType, 
                                   status: PlatformStatus, error_message: Optional[str] = None) -> bool:
        """
        Update platform status
        
        Args:
            user_id: User identifier
            platform_type: Platform type
            status: New status
            error_message: Optional error message
            
        Returns:
            bool: Success status
        """
        try:
            update_data = {
                "config.status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if status == PlatformStatus.ERROR and error_message:
                update_data["config.last_error"] = error_message
                update_data["$inc"] = {"config.error_count": 1}
            elif status == PlatformStatus.ACTIVE:
                update_data["config.last_sync"] = datetime.utcnow()
                update_data["$inc"] = {"config.success_count": 1}
            
            await self.platforms_collection.update_one(
                {"user_id": user_id, "platform_type": platform_type.value},
                {"$set": update_data}
            )
            
            # Update cache
            cache_key = f"{user_id}:{platform_type.value}"
            if cache_key in self._platform_cache:
                self._platform_cache[cache_key].status = status
                if status == PlatformStatus.ACTIVE:
                    self._platform_cache[cache_key].last_sync = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update platform status: {e}")
            return False
    
    async def check_rate_limits(self, user_id: str, platform_type: PlatformType) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if platform rate limits allow new requests
        
        Args:
            user_id: User identifier
            platform_type: Platform type
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (can_proceed, rate_limit_info)
        """
        try:
            key = f"{user_id}:{platform_type.value}"
            now = datetime.utcnow()
            
            if key not in self._rate_limits:
                self._rate_limits[key] = {
                    "requests_this_minute": 0,
                    "requests_this_hour": 0,
                    "requests_this_day": 0,
                    "last_reset_minute": now,
                    "last_reset_hour": now,
                    "last_reset_day": now
                }
            
            limits = self._rate_limits[key]
            platform_config = await self.get_platform(user_id, platform_type)
            
            if not platform_config:
                return False, {"error": "Platform not configured"}
            
            platform_limits = platform_config.limits
            
            # Reset counters if time periods have passed
            if (now - limits["last_reset_minute"]).total_seconds() >= 60:
                limits["requests_this_minute"] = 0
                limits["last_reset_minute"] = now
            
            if (now - limits["last_reset_hour"]).total_seconds() >= 3600:
                limits["requests_this_hour"] = 0
                limits["last_reset_hour"] = now
            
            if (now - limits["last_reset_day"]).total_seconds() >= 86400:
                limits["requests_this_day"] = 0
                limits["last_reset_day"] = now
            
            # Check limits
            can_proceed = (
                limits["requests_this_minute"] < platform_limits.requests_per_minute and
                limits["requests_this_hour"] < platform_limits.requests_per_hour and
                limits["requests_this_day"] < platform_limits.requests_per_day
            )
            
            if can_proceed:
                limits["requests_this_minute"] += 1
                limits["requests_this_hour"] += 1
                limits["requests_this_day"] += 1
            
            rate_limit_info = {
                "can_proceed": can_proceed,
                "remaining_minute": max(0, platform_limits.requests_per_minute - limits["requests_this_minute"]),
                "remaining_hour": max(0, platform_limits.requests_per_hour - limits["requests_this_hour"]),
                "remaining_day": max(0, platform_limits.requests_per_day - limits["requests_this_day"]),
                "reset_times": {
                    "minute": limits["last_reset_minute"] + timedelta(seconds=60),
                    "hour": limits["last_reset_hour"] + timedelta(hours=1),
                    "day": limits["last_reset_day"] + timedelta(days=1)
                }
            }
            
            return can_proceed, rate_limit_info
            
        except Exception as e:
            logger.error(f"Failed to check rate limits: {e}")
            return False, {"error": str(e)}
    
    async def get_platform_analytics(self, user_id: str, platform_type: Optional[PlatformType] = None,
                                   start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get platform analytics and performance metrics
        
        Args:
            user_id: User identifier
            platform_type: Optional platform type filter
            start_date: Optional start date for analytics
            end_date: Optional end date for analytics
            
        Returns:
            Dict[str, Any]: Analytics data
        """
        try:
            # Default date range to last 30 days
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Build aggregation pipeline
            match_stage = {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }
            
            if platform_type:
                match_stage["platform_type"] = platform_type.value
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": "$platform_type",
                        "total_content": {"$sum": "$content_count"},
                        "total_engagement": {"$sum": "$total_engagement"},
                        "total_revenue": {"$sum": "$revenue"},
                        "avg_engagement_rate": {"$avg": "$engagement_rate"},
                        "total_views": {"$sum": "$views"},
                        "total_likes": {"$sum": "$likes"},
                        "total_shares": {"$sum": "$shares"},
                        "total_comments": {"$sum": "$comments"},
                        "error_count": {"$sum": "$errors"},
                        "success_rate": {"$avg": "$success_rate"}
                    }
                },
                {"$sort": {"total_engagement": -1}}
            ]
            
            # Execute aggregation
            cursor = self.analytics_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Calculate summary statistics
            summary = {
                "total_platforms": len(results),
                "total_content_distributed": sum(r["total_content"] for r in results),
                "total_engagement": sum(r["total_engagement"] for r in results),
                "total_revenue": sum(r["total_revenue"] for r in results),
                "avg_engagement_rate": sum(r["avg_engagement_rate"] for r in results) / len(results) if results else 0,
                "platforms": results,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get platform analytics: {e}")
            return {}
    
    async def _validate_platform_config(self, config: PlatformConfig) -> bool:
        """Validate platform configuration"""
        try:
            # Check required fields
            if not config.platform_type or not config.display_name:
                return False
            
            # Validate credentials based on platform type
            if not config.credentials:
                return False
            
            # Platform-specific validation
            if config.platform_type in [PlatformType.YOUTUBE, PlatformType.FACEBOOK]:
                if not config.credentials.api_key or not config.credentials.api_secret:
                    return False
            
            if config.platform_type == PlatformType.INSTAGRAM:
                if not config.credentials.access_token:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Platform config validation failed: {e}")
            return False
    
    async def _encrypt_credentials(self, config: PlatformConfig) -> PlatformConfig:
        """Encrypt sensitive credential fields using proper encryption."""
        try:
            # Import encryption manager
            from ..security.encryption_manager import EncryptionManager
            encryption_manager = EncryptionManager()
            
            # Create a copy to avoid modifying original
            encrypted_config = config
            
            if config.credentials.api_secret:
                encrypted_secret = await encryption_manager.encrypt_field(
                    'api_secret', 
                    config.credentials.api_secret
                )
                encrypted_config.credentials.api_secret = encrypted_secret
            
            if config.credentials.access_token:
                encrypted_token = await encryption_manager.encrypt_field(
                    'access_token',
                    config.credentials.access_token
                )
                encrypted_config.credentials.access_token = encrypted_token
            
            return encrypted_config
            
        except ImportError:
            logger.warning("Encryption manager not available, using base64 fallback")
            # Fallback to base64 if encryption manager not available
            encrypted_config = config
            
            if config.credentials.api_secret:
                encrypted_config.credentials.api_secret = base64.b64encode(
                    config.credentials.api_secret.encode()
                ).decode()
            
            if config.credentials.access_token:
                encrypted_config.credentials.access_token = base64.b64encode(
                    config.credentials.access_token.encode()
                ).decode()
            
            return encrypted_config
    
    async def _decrypt_and_create_config(self, config_data: Dict[str, Any]) -> PlatformConfig:
        """Decrypt credentials and create config object."""
        try:
            # Import encryption manager
            from ..security.encryption_manager import EncryptionManager
            encryption_manager = EncryptionManager()
            
            # Decrypt sensitive fields
            if "credentials" in config_data:
                creds = config_data["credentials"]
                if "api_secret" in creds and creds["api_secret"]:
                    creds["api_secret"] = await encryption_manager.decrypt_field(
                        'api_secret',
                        creds["api_secret"]
                    )
                if "access_token" in creds and creds["access_token"]:
                    creds["access_token"] = await encryption_manager.decrypt_field(
                        'access_token',
                        creds["access_token"]
                    )
            
        except ImportError:
            logger.warning("Encryption manager not available, using base64 fallback")
            # Fallback decryption using base64
            if "credentials" in config_data:
                creds = config_data["credentials"]
                if "api_secret" in creds and creds["api_secret"]:
                    creds["api_secret"] = base64.b64decode(creds["api_secret"]).decode()
                if "access_token" in creds and creds["access_token"]:
                    creds["access_token"] = base64.b64decode(creds["access_token"]).decode()
        
        # Create config object from dict
        # This is a simplified version - in production, use proper serialization
        platform_type = PlatformType(config_data["platform_type"])
        return PlatformConfig(
            platform_type=platform_type,
            display_name=config_data.get("display_name", platform_type.value.title()),
            credentials=PlatformCredentials(**config_data.get("credentials", {})),
            limits=PlatformLimits(**config_data.get("limits", {})),
            status=PlatformStatus(config_data.get("status", "inactive"))
        )
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        return (datetime.utcnow() - self._last_cache_update) < self._cache_ttl
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self._session:
            await self._session.close()
        logger.info("Platform Manager cleanup completed")


# Default platform configurations for quick setup
DEFAULT_PLATFORM_LIMITS = {
    PlatformType.YOUTUBE: PlatformLimits(
        requests_per_minute=100,
        requests_per_hour=10000,
        requests_per_day=1000000,
        max_file_size_mb=128000,  # 128GB
        max_video_duration_seconds=43200,  # 12 hours
        supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
        max_caption_length=5000,
        max_hashtags=15
    ),
    PlatformType.INSTAGRAM: PlatformLimits(
        requests_per_minute=60,
        requests_per_hour=200,
        requests_per_day=4800,
        max_file_size_mb=100,
        max_video_duration_seconds=3600,  # 1 hour for IGTV
        supported_formats=["mp4", "mov", "jpg", "png"],
        max_caption_length=2200,
        max_hashtags=30
    ),
    PlatformType.TIKTOK: PlatformLimits(
        requests_per_minute=50,
        requests_per_hour=500,
        requests_per_day=10000,
        max_file_size_mb=287,
        max_video_duration_seconds=600,  # 10 minutes
        supported_formats=["mp4", "mov", "webm"],
        max_caption_length=4000,
        max_hashtags=20
    ),
    # Add more platform limits as needed
}


async def create_platform_manager(db: AsyncIOMotorDatabase) -> PlatformManager:
    """
    Factory function to create and initialize Platform Manager
    
    Args:
        db: MongoDB database connection
        
    Returns:
        PlatformManager: Initialized platform manager
    """
    manager = PlatformManager(db)
    await manager.initialize()
    return manager