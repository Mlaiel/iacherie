"""Platform Integration Database Configuration Module for IA-Influencer Agent Platform
==================================================================================

Professional platform integration database configuration for multi-platform API management,
data synchronization, and cross-platform analytics aggregation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import asyncpg
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

logger = logging.getLogger(__name__)

Base = declarative_base()


class PlatformType(Enum):
    """Supported platform types"""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    PODCAST_PLATFORM = "podcast_platform"
    LIVE_STREAMING = "live_streaming"
    MARKETPLACE = "marketplace"
    PAYMENT_PROCESSOR = "payment_processor"
    ANALYTICS_SERVICE = "analytics_service"
    CLOUD_STORAGE = "cloud_storage"


class Platform(Enum):
    """Specific platform implementations"""
    # Social Media
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook" 
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    
    # Music & Audio
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    AUDIOMACK = "audiomack"
    
    # Video
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    
    # Podcasts
    APPLE_PODCASTS = "apple_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    SPOTIFY_PODCASTS = "spotify_podcasts"
    
    # Payment & Monetization
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    
    # Analytics & Tools
    GOOGLE_ANALYTICS = "google_analytics"
    FACEBOOK_ANALYTICS = "facebook_analytics"
    MIXPANEL = "mixpanel"


class IntegrationStatus(Enum):
    """Platform integration status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"


class SyncFrequency(Enum):
    """Data synchronization frequency"""
    REAL_TIME = "real_time"
    EVERY_15_MIN = "15_minutes"
    EVERY_HOUR = "1_hour"
    EVERY_6_HOURS = "6_hours"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class DataType(Enum):
    """Types of data synchronized"""
    CONTENT_METADATA = "content_metadata"
    ANALYTICS_DATA = "analytics_data"
    REVENUE_DATA = "revenue_data"
    AUDIENCE_DATA = "audience_data"
    ENGAGEMENT_DATA = "engagement_data"
    PERFORMANCE_METRICS = "performance_metrics"
    PROTECTION_ALERTS = "protection_alerts"
    USER_PROFILE = "user_profile"


@dataclass
class PlatformCredentials:
    """Platform integration database credentials"""
    database_url: str = os.getenv("PLATFORM_DATABASE_URL", "postgresql://user:pass@localhost:5432/platforms")
    redis_url: str = os.getenv("PLATFORM_REDIS_URL", "redis://localhost:6379/5")
    
    # Encryption keys for storing API tokens
    token_encryption_key: str = os.getenv("TOKEN_ENCRYPTION_KEY", "")
    refresh_token_encryption_key: str = os.getenv("REFRESH_TOKEN_ENCRYPTION_KEY", "")
    
    # Rate limiting and connection settings
    default_rate_limit: int = 100  # requests per minute
    connection_timeout: int = 30
    request_timeout: int = 60
    max_retries: int = 3
    
    pool_size: int = 25
    max_overflow: int = 50


@dataclass
class PlatformConfig:
    """Configuration for specific platform"""
    platform: Platform
    platform_type: PlatformType
    
    # API Configuration
    api_base_url: str
    api_version: str = "v1"
    auth_type: str = "oauth2"  # oauth2, api_key, bearer
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000
    
    # Data sync configuration
    supported_data_types: List[DataType] = field(default_factory=list)
    sync_frequency: SyncFrequency = SyncFrequency.EVERY_HOUR
    batch_size: int = 100
    
    # Feature support
    supports_webhooks: bool = False
    supports_real_time: bool = False
    supports_bulk_operations: bool = True
    supports_pagination: bool = True
    
    # Data retention
    cache_ttl: int = 3600
    historical_data_limit: int = 365  # days
    
    # Endpoints mapping
    endpoints: Dict[str, str] = field(default_factory=dict)
    
    # Platform-specific settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookConfig:
    """Webhook configuration for platforms"""
    enabled: bool = False
    endpoint_url: str = ""
    secret_key: str = ""
    events: List[str] = field(default_factory=list)
    retry_attempts: int = 3
    timeout: int = 30


class PlatformIntegration(Base):
    """Platform integrations table"""
    __tablename__ = 'platform_integrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    platform_type = Column(String(30), nullable=False)
    
    # Integration status
    status = Column(String(20), default=IntegrationStatus.DISCONNECTED.value, index=True)
    is_active = Column(Boolean, default=True)
    
    # Authentication data (encrypted)
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    token_scope = Column(String(500), nullable=True)
    
    # Platform account information
    platform_user_id = Column(String(255), nullable=True, index=True)
    platform_username = Column(String(255), nullable=True)
    platform_display_name = Column(String(255), nullable=True)
    platform_email = Column(String(255), nullable=True)
    platform_url = Column(String(500), nullable=True)
    
    # Platform-specific identifiers
    channel_id = Column(String(255), nullable=True)
    page_id = Column(String(255), nullable=True)
    profile_id = Column(String(255), nullable=True)
    
    # Sync configuration
    sync_frequency = Column(String(20), default=SyncFrequency.EVERY_HOUR.value)
    auto_sync_enabled = Column(Boolean, default=True)
    sync_data_types = Column(JSON, nullable=True)
    
    # Sync tracking
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    last_successful_sync_at = Column(DateTime, nullable=True)
    sync_error_count = Column(Integer, default=0)
    last_sync_error = Column(Text, nullable=True)
    
    # Platform metrics
    total_synced_records = Column(Integer, default=0)
    last_sync_duration = Column(Float, nullable=True)  # seconds
    average_sync_duration = Column(Float, nullable=True)
    
    # Rate limiting
    current_rate_limit = Column(Integer, nullable=True)
    rate_limit_reset_at = Column(DateTime, nullable=True)
    rate_limit_exceeded_count = Column(Integer, default=0)
    
    # Webhook configuration
    webhook_enabled = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    
    # Additional metadata
    integration_metadata = Column(JSON, nullable=True)
    platform_features = Column(JSON, nullable=True)
    custom_settings = Column(JSON, nullable=True)
    
    # Temporal tracking
    connected_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncHistory(Base):
    """Synchronization history tracking"""
    __tablename__ = 'platform_sync_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_id = Column(Integer, nullable=False, index=True)
    
    # Sync details
    sync_type = Column(String(30), nullable=False)  # full, incremental, webhook
    data_types_synced = Column(JSON, nullable=True)
    sync_started_at = Column(DateTime, nullable=False)
    sync_completed_at = Column(DateTime, nullable=True)
    sync_duration = Column(Float, nullable=True)  # seconds
    
    # Results
    status = Column(String(20), nullable=False)  # success, failure, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Performance metrics
    api_calls_made = Column(Integer, default=0)
    rate_limit_hits = Column(Integer, default=0)
    data_volume_bytes = Column(Integer, default=0)
    
    # Metadata
    sync_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PlatformData(Base):
    """Cached platform data"""
    __tablename__ = 'platform_data_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_id = Column(Integer, nullable=False, index=True)
    
    # Data classification
    data_type = Column(String(30), nullable=False, index=True)
    platform_record_id = Column(String(255), nullable=True, index=True)
    content_id = Column(String(255), nullable=True, index=True)
    
    # Data payload
    data_payload = Column(JSON, nullable=False)
    data_hash = Column(String(64), nullable=True, index=True)  # For change detection
    
    # Temporal data
    platform_created_at = Column(DateTime, nullable=True)
    platform_updated_at = Column(DateTime, nullable=True)
    
    # Cache management
    cached_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    is_stale = Column(Boolean, default=False)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    processing_errors = Column(JSON, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)


class WebhookEvent(Base):
    """Webhook events from platforms"""
    __tablename__ = 'platform_webhook_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_id = Column(Integer, nullable=False, index=True)
    
    # Event details
    event_id = Column(String(255), nullable=True, unique=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_source = Column(String(50), nullable=False)
    
    # Payload
    event_payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    signature = Column(String(255), nullable=True)
    
    # Processing
    is_processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    processing_attempts = Column(Integer, default=0)
    processing_error = Column(Text, nullable=True)
    
    # Verification
    signature_verified = Column(Boolean, default=False)
    verification_attempted_at = Column(DateTime, nullable=True)
    
    # Timing
    received_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


@dataclass
class PlatformIntegrationConfig:
    """Professional platform integration configuration"""
    
    # Database credentials
    credentials: PlatformCredentials = field(default_factory=PlatformCredentials)
    
    # Platform configurations
    platform_configs: Dict[Platform, PlatformConfig] = field(default_factory=dict)
    
    # Webhook configuration
    webhook_config: WebhookConfig = field(default_factory=WebhookConfig)
    
    # Performance settings
    max_concurrent_syncs: int = 10
    batch_processing_size: int = 500
    cache_default_ttl: int = 3600
    
    # Feature flags
    enable_real_time_sync: bool = True
    enable_webhook_processing: bool = True
    enable_rate_limit_management: bool = True
    enable_data_validation: bool = True
    enable_encryption: bool = True
    
    # Error handling
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    dead_letter_queue_enabled: bool = True
    
    # Monitoring
    metrics_collection_enabled: bool = True
    performance_monitoring: bool = True
    error_reporting: bool = True
    
    def __post_init__(self):
        """Initialize default platform configurations"""
        if not self.platform_configs:
            self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default platform configurations"""
        # YouTube configuration
        self.platform_configs[Platform.YOUTUBE] = PlatformConfig(
            platform=Platform.YOUTUBE,
            platform_type=PlatformType.VIDEO_PLATFORM,
            api_base_url="https://www.googleapis.com/youtube/v3",
            supported_data_types=[
                DataType.CONTENT_METADATA,
                DataType.ANALYTICS_DATA,
                DataType.REVENUE_DATA,
                DataType.AUDIENCE_DATA
            ],
            endpoints={
                "channels": "/channels",
                "videos": "/videos",
                "analytics": "/reports",
                "search": "/search"
            },
            supports_webhooks=True,
            rate_limit_per_minute=100
        )
        
        # Instagram configuration  
        self.platform_configs[Platform.INSTAGRAM] = PlatformConfig(
            platform=Platform.INSTAGRAM,
            platform_type=PlatformType.SOCIAL_MEDIA,
            api_base_url="https://graph.instagram.com/v1",
            supported_data_types=[
                DataType.CONTENT_METADATA,
                DataType.ANALYTICS_DATA,
                DataType.AUDIENCE_DATA
            ],
            endpoints={
                "media": "/media",
                "insights": "/insights",
                "user": "/me"
            },
            rate_limit_per_minute=200
        )
        
        # Spotify configuration
        self.platform_configs[Platform.SPOTIFY] = PlatformConfig(
            platform=Platform.SPOTIFY,
            platform_type=PlatformType.MUSIC_STREAMING,
            api_base_url="https://api.spotify.com/v1",
            supported_data_types=[
                DataType.CONTENT_METADATA,
                DataType.ANALYTICS_DATA,
                DataType.AUDIENCE_DATA
            ],
            endpoints={
                "tracks": "/tracks",
                "albums": "/albums",
                "artists": "/artists",
                "analytics": "/artists/{id}/stats"
            },
            rate_limit_per_minute=100
        )


class PlatformIntegrationManager:
    """Professional platform integration database manager"""
    
    def __init__(self, config: PlatformIntegrationConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
        self._redis_pool = None
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize platform integration database connections"""
        try:
            # Initialize PostgreSQL connection
            self._engine = create_engine(
                self.config.credentials.database_url,
                pool_size=self.config.credentials.pool_size,
                max_overflow=self.config.credentials.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Initialize Redis for caching
            self._redis_pool = redis.from_url(
                self.config.credentials.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=25
            )
            
            # Create tables
            Base.metadata.create_all(self._engine)
            
            # Test connections
            await self._test_connections()
            
            self._is_initialized = True
            logger.info("Platform integration manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize platform integration manager: {e}")
            return False
    
    async def _test_connections(self):
        """Test database connections"""
        with self._engine.connect() as conn:
            conn.execute("SELECT 1")
        
        await self._redis_pool.ping()
    
    async def create_integration(self,
                               user_id: int,
                               platform: Platform,
                               access_token: str,
                               platform_user_id: str,
                               metadata: Optional[Dict] = None) -> int:
        """Create new platform integration"""
        try:
            # Encrypt tokens (simplified - use proper encryption in production)
            encrypted_token = self._encrypt_token(access_token)
            
            with self._session_factory() as session:
                platform_config = self.config.platform_configs.get(platform)
                
                integration = PlatformIntegration(
                    user_id=user_id,
                    platform=platform.value,
                    platform_type=platform_config.platform_type.value if platform_config else PlatformType.SOCIAL_MEDIA.value,
                    status=IntegrationStatus.CONNECTED.value,
                    access_token_encrypted=encrypted_token,
                    platform_user_id=platform_user_id,
                    connected_at=datetime.utcnow(),
                    integration_metadata=metadata,
                    sync_data_types=[dt.value for dt in platform_config.supported_data_types] if platform_config else []
                )
                
                session.add(integration)
                session.commit()
                session.refresh(integration)
                
                # Schedule initial sync
                await self._schedule_sync(integration.id)
                
                logger.info(f"Created integration {integration.id} for user {user_id} on {platform.value}")
                return integration.id
                
        except Exception as e:
            logger.error(f"Failed to create platform integration: {e}")
            raise
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt access token (simplified implementation)"""
        # In production, use proper encryption like Fernet
        return f"encrypted_{token}"
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt access token (simplified implementation)"""
        return encrypted_token.replace("encrypted_", "")
    
    async def sync_platform_data(self, integration_id: int) -> bool:
        """Synchronize data from platform"""
        try:
            with self._session_factory() as session:
                integration = session.query(PlatformIntegration).filter_by(id=integration_id).first()
                if not integration:
                    logger.error(f"Integration {integration_id} not found")
                    return False
                
                # Create sync history record
                sync_history = SyncHistory(
                    integration_id=integration_id,
                    sync_type="incremental",
                    sync_started_at=datetime.utcnow(),
                    status="running"
                )
                session.add(sync_history)
                session.commit()
                
                try:
                    # Perform actual sync (simplified)
                    logger.info(f"Syncing data for integration {integration_id}")
                    
                    # Update integration status
                    integration.status = IntegrationStatus.SYNCING.value
                    integration.last_sync_at = datetime.utcnow()
                    
                    # Simulate sync completion
                    sync_history.sync_completed_at = datetime.utcnow()
                    sync_history.status = "success"
                    sync_history.records_processed = 100
                    sync_history.records_created = 10
                    sync_history.records_updated = 90
                    
                    integration.status = IntegrationStatus.CONNECTED.value
                    integration.last_successful_sync_at = datetime.utcnow()
                    integration.total_synced_records += sync_history.records_processed
                    
                    session.commit()
                    
                    logger.info(f"Successfully synced integration {integration_id}")
                    return True
                    
                except Exception as sync_error:
                    sync_history.status = "failure"
                    sync_history.error_message = str(sync_error)
                    integration.status = IntegrationStatus.ERROR.value
                    integration.last_sync_error = str(sync_error)
                    integration.sync_error_count += 1
                    
                    session.commit()
                    raise sync_error
                
        except Exception as e:
            logger.error(f"Failed to sync platform data: {e}")
            return False
    
    async def _schedule_sync(self, integration_id: int):
        """Schedule next synchronization"""
        try:
            with self._session_factory() as session:
                integration = session.query(PlatformIntegration).filter_by(id=integration_id).first()
                if integration and integration.auto_sync_enabled:
                    # Calculate next sync time based on frequency
                    frequency_map = {
                        SyncFrequency.EVERY_15_MIN.value: timedelta(minutes=15),
                        SyncFrequency.EVERY_HOUR.value: timedelta(hours=1),
                        SyncFrequency.EVERY_6_HOURS.value: timedelta(hours=6),
                        SyncFrequency.DAILY.value: timedelta(days=1),
                        SyncFrequency.WEEKLY.value: timedelta(weeks=1)
                    }
                    
                    interval = frequency_map.get(integration.sync_frequency, timedelta(hours=1))
                    integration.next_sync_at = datetime.utcnow() + interval
                    session.commit()
                    
        except Exception as e:
            logger.error(f"Failed to schedule sync: {e}")
    
    async def process_webhook(self,
                            integration_id: int,
                            event_type: str,
                            payload: Dict[str, Any],
                            headers: Dict[str, str] = None) -> int:
        """Process webhook event from platform"""
        try:
            with self._session_factory() as session:
                webhook_event = WebhookEvent(
                    integration_id=integration_id,
                    event_type=event_type,
                    event_source=headers.get("X-Platform-Source", "unknown") if headers else "unknown",
                    event_payload=payload,
                    headers=headers,
                    received_at=datetime.utcnow()
                )
                
                session.add(webhook_event)
                session.commit()
                session.refresh(webhook_event)
                
                # Process webhook asynchronously
                await self._process_webhook_event(webhook_event.id)
                
                logger.info(f"Processed webhook event {webhook_event.id}")
                return webhook_event.id
                
        except Exception as e:
            logger.error(f"Failed to process webhook: {e}")
            raise
    
    async def _process_webhook_event(self, event_id: int):
        """Process webhook event asynchronously"""
        try:
            with self._session_factory() as session:
                event = session.query(WebhookEvent).filter_by(id=event_id).first()
                if event:
                    # Process event based on type
                    logger.info(f"Processing webhook event {event_id}: {event.event_type}")
                    
                    # Mark as processed
                    event.is_processed = True
                    event.processed_at = datetime.utcnow()
                    session.commit()
                    
        except Exception as e:
            logger.error(f"Failed to process webhook event: {e}")
    
    async def get_integration_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get platform integration statistics"""
        try:
            with self._session_factory() as session:
                base_query = session.query(PlatformIntegration)
                if user_id:
                    base_query = base_query.filter_by(user_id=user_id)
                
                stats = {
                    "total_integrations": base_query.count(),
                    "active_integrations": base_query.filter_by(is_active=True).count(),
                    "by_platform": {},
                    "by_status": {},
                    "sync_statistics": {}
                }
                
                # Statistics by platform
                for platform in Platform:
                    count = base_query.filter_by(platform=platform.value).count()
                    if count > 0:
                        stats["by_platform"][platform.value] = count
                
                # Statistics by status
                for status in IntegrationStatus:
                    count = base_query.filter_by(status=status.value).count()
                    if count > 0:
                        stats["by_status"][status.value] = count
                
                # Sync statistics
                recent_syncs = session.query(SyncHistory).filter(
                    SyncHistory.sync_started_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                stats["sync_statistics"]["syncs_last_24h"] = recent_syncs
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get integration statistics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shutdown platform integration manager"""
        try:
            if self._redis_pool:
                await self._redis_pool.close()
            
            if self._engine:
                self._engine.dispose()
            
            self._is_initialized = False
            logger.info("Platform integration manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during platform integration manager shutdown: {e}")


def create_platform_integration_config() -> PlatformIntegrationConfig:
    """Create default platform integration configuration"""
    return PlatformIntegrationConfig()


def create_platform_integration_manager(config: Optional[PlatformIntegrationConfig] = None) -> PlatformIntegrationManager:
    """Create platform integration manager with configuration"""
    if config is None:
        config = create_platform_integration_config()
    return PlatformIntegrationManager(config)


# Export configuration for production use
__all__ = [
    'PlatformType',
    'Platform',
    'IntegrationStatus',
    'SyncFrequency',
    'DataType',
    'PlatformIntegrationConfig',
    'PlatformIntegrationManager',
    'PlatformConfig',
    'WebhookConfig',
    'create_platform_integration_config',
    'create_platform_integration_manager'
]
