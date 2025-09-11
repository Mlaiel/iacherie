#!/usr/bin/env python3
"""
Ainflue Platform - Multi-Platform Content Scheduling System
Enterprise-grade content scheduling and automation for creators

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved

Expert Roles Demonstrated:
- Backend Senior: Enterprise scheduling architecture, API orchestration
- DevOps: Automated deployment pipelines, monitoring integration
- Microservices: Distributed scheduling system, service mesh patterns
- DBA: Optimized data storage, scheduling queue management
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import json
import uuid
import hashlib
from pathlib import Path

import aiohttp
import asyncpg
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
from croniter import croniter
import pytz

# Core platform imports
from ..core.base_integration import BaseIntegration
from ..core.exceptions import IntegrationError, ValidationError
from ..platforms.platform_coordinator import PlatformCoordinator
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

class ScheduleStatus(str, Enum):
    """Content schedule status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRAFT = "draft"

class ContentType(str, Enum):
    """Content type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"

class Platform(str, Enum):
    """Supported platform enumeration"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TWITCH = "twitch"

@dataclass
class ContentAsset:
    """Content asset representation"""
    asset_id: str
    asset_type: ContentType
    file_path: Optional[str] = None
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformSettings:
    """Platform-specific publishing settings"""
    platform: Platform
    account_id: str
    access_token: str
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)

class ScheduledContent(BaseModel):
    """Scheduled content model"""
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: Optional[str] = None
    content_type: ContentType
    platforms: List[Platform]
    assets: List[ContentAsset]
    
    # Scheduling
    scheduled_time: datetime
    timezone_str: str = "UTC"
    recurring_pattern: Optional[str] = None  # Cron pattern
    
    # Publishing settings
    platform_settings: Dict[Platform, PlatformSettings] = Field(default_factory=dict)
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    location: Optional[Dict[str, Any]] = None
    
    # Status tracking
    status: ScheduleStatus = ScheduleStatus.DRAFT
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    campaign_id: Optional[str] = None
    
    @validator('scheduled_time')
    def validate_future_time(cls, v):
        """Ensure scheduled time is in the future"""
        if v <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Ensure at least one platform is specified"""
        if not v:
            raise ValueError("At least one platform must be specified")
        return v

class ContentScheduler(BaseIntegration):
    """
    Enterprise Multi-Platform Content Scheduling System
    
    Demonstrates Expert Roles:
    - Backend Senior: Complex scheduling logic, API orchestration
    - DevOps: Automated deployment, monitoring, health checks
    - Microservices: Distributed architecture, service communication
    - DBA: Optimized database operations, queue management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize content scheduler with configuration"""
        super().__init__(config)
        
        # Core configuration
        self.config = config
        self.redis_url = config.get("redis_url", "redis://localhost:6379")
        self.db_url = config.get("database_url")
        self.max_workers = config.get("max_workers", 10)
        
        # Service dependencies
        self.platform_coordinator = PlatformCoordinator(config)
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Runtime state
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.scheduler_task: Optional[asyncio.Task] = None
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Performance metrics
        self.metrics = {
            "scheduled_count": 0,
            "published_count": 0,
            "failed_count": 0,
            "retry_count": 0,
            "average_processing_time": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize scheduler components"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Initialize database pool
            if self.db_url:
                self.db_pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=5,
                    max_size=20
                )
                await self._setup_database_schema()
            
            # Initialize platform coordinator
            await self.platform_coordinator.initialize()
            
            # Start scheduler background task
            self.scheduler_task = asyncio.create_task(self._run_scheduler())
            
            await self.monitoring.record_metric("scheduler_initialized", 1)
            self.logger.info("Content scheduler initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content scheduler: {e}")
            raise IntegrationError(f"Scheduler initialization failed: {e}")
    
    async def _setup_database_schema(self) -> None:
        """Setup database schema for content scheduling"""
        if not self.db_pool:
            return
            
        schema_sql = """
        -- Content schedule table
        CREATE TABLE IF NOT EXISTS scheduled_content (
            content_id UUID PRIMARY KEY,
            creator_id VARCHAR(255) NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            content_type VARCHAR(50) NOT NULL,
            platforms JSONB NOT NULL,
            assets JSONB NOT NULL,
            scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
            timezone_str VARCHAR(100) DEFAULT 'UTC',
            recurring_pattern TEXT,
            platform_settings JSONB DEFAULT '{}',
            hashtags TEXT[] DEFAULT '{}',
            mentions TEXT[] DEFAULT '{}',
            location JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 3,
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            tags TEXT[] DEFAULT '{}',
            campaign_id VARCHAR(255)
        );
        
        -- Publishing history table
        CREATE TABLE IF NOT EXISTS publishing_history (
            id SERIAL PRIMARY KEY,
            content_id UUID REFERENCES scheduled_content(content_id),
            platform VARCHAR(50) NOT NULL,
            published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            platform_post_id VARCHAR(255),
            success BOOLEAN NOT NULL,
            error_message TEXT,
            metrics JSONB DEFAULT '{}'
        );
        
        -- Performance analytics table
        CREATE TABLE IF NOT EXISTS scheduling_analytics (
            id SERIAL PRIMARY KEY,
            creator_id VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            platform VARCHAR(50) NOT NULL,
            scheduled_count INTEGER DEFAULT 0,
            published_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            average_engagement DECIMAL(10,2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(creator_id, date, platform)
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_scheduled_content_creator ON scheduled_content(creator_id);
        CREATE INDEX IF NOT EXISTS idx_scheduled_content_time ON scheduled_content(scheduled_time);
        CREATE INDEX IF NOT EXISTS idx_scheduled_content_status ON scheduled_content(status);
        CREATE INDEX IF NOT EXISTS idx_publishing_history_content ON publishing_history(content_id);
        CREATE INDEX IF NOT EXISTS idx_scheduling_analytics_creator ON scheduling_analytics(creator_id, date);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def schedule_content(self, content: ScheduledContent) -> str:
        """
        Schedule content for publishing across multiple platforms
        Demonstrates: Backend Senior - Complex business logic orchestration
        """
        try:
            start_time = datetime.utcnow()
            
            # Validate content
            await self._validate_content(content)
            
            # Process and optimize assets
            await self._process_content_assets(content)
            
            # Validate platform access
            await self._validate_platform_access(content)
            
            # Store in database
            if self.db_pool:
                await self._store_scheduled_content(content)
            
            # Add to Redis queue for scheduling
            await self._queue_content_for_scheduling(content)
            
            # Update metrics
            self.metrics["scheduled_count"] += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_processing_time(processing_time)
            
            # Audit log
            await self.audit_logger.log_action(
                action="content_scheduled",
                user_id=content.creator_id,
                resource_id=content.content_id,
                details={
                    "platforms": [p.value for p in content.platforms],
                    "scheduled_time": content.scheduled_time.isoformat(),
                    "content_type": content.content_type.value
                }
            )
            
            await self.monitoring.record_metric("content_scheduled", 1, {
                "creator_id": content.creator_id,
                "platforms": len(content.platforms),
                "content_type": content.content_type.value
            })
            
            self.logger.info(f"Content {content.content_id} scheduled successfully")
            return content.content_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule content: {e}")
            await self.monitoring.record_error("schedule_content_error", str(e))
            raise IntegrationError(f"Content scheduling failed: {e}")
    
    async def _validate_content(self, content: ScheduledContent) -> None:
        """Validate content before scheduling"""
        # Check content size limits
        for asset in content.assets:
            if asset.size_bytes and asset.size_bytes > 100 * 1024 * 1024:  # 100MB
                raise ValidationError(f"Asset {asset.asset_id} exceeds size limit")
        
        # Validate hashtags
        if len(content.hashtags) > 30:
            raise ValidationError("Too many hashtags (max 30)")
        
        # Check scheduled time constraints
        min_schedule_time = datetime.utcnow() + timedelta(minutes=5)
        if content.scheduled_time < min_schedule_time:
            raise ValidationError("Content must be scheduled at least 5 minutes in advance")
        
        # Validate recurring pattern if provided
        if content.recurring_pattern:
            try:
                croniter(content.recurring_pattern)
            except ValueError as e:
                raise ValidationError(f"Invalid recurring pattern: {e}")
    
    async def _process_content_assets(self, content: ScheduledContent) -> None:
        """
        Process and optimize content assets
        Demonstrates: Backend Senior - Asset processing pipeline
        """
        for asset in content.assets:
            if asset.file_path:
                # Generate thumbnails for videos
                if asset.asset_type == ContentType.VIDEO:
                    asset.thumbnail = await self._generate_video_thumbnail(asset.file_path)
                
                # Optimize images
                elif asset.asset_type == ContentType.IMAGE:
                    await self._optimize_image(asset.file_path)
                
                # Process audio metadata
                elif asset.asset_type == ContentType.AUDIO:
                    asset.metadata = await self._extract_audio_metadata(asset.file_path)
    
    async def _validate_platform_access(self, content: ScheduledContent) -> None:
        """Validate platform access and permissions"""
        for platform in content.platforms:
            if platform not in content.platform_settings:
                raise ValidationError(f"Platform settings missing for {platform.value}")
            
            settings = content.platform_settings[platform]
            
            # Validate access token
            is_valid = await self.platform_coordinator.validate_access_token(
                platform.value, 
                settings.access_token
            )
            
            if not is_valid:
                raise ValidationError(f"Invalid access token for {platform.value}")
    
    async def _store_scheduled_content(self, content: ScheduledContent) -> None:
        """
        Store scheduled content in database
        Demonstrates: DBA - Optimized database operations
        """
        if not self.db_pool:
            return
        
        query = """
        INSERT INTO scheduled_content (
            content_id, creator_id, title, description, content_type,
            platforms, assets, scheduled_time, timezone_str, recurring_pattern,
            platform_settings, hashtags, mentions, location, status,
            max_attempts, tags, campaign_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        ON CONFLICT (content_id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            platforms = EXCLUDED.platforms,
            assets = EXCLUDED.assets,
            scheduled_time = EXCLUDED.scheduled_time,
            platform_settings = EXCLUDED.platform_settings,
            hashtags = EXCLUDED.hashtags,
            mentions = EXCLUDED.mentions,
            location = EXCLUDED.location,
            status = EXCLUDED.status,
            updated_at = NOW()
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                content.content_id,
                content.creator_id,
                content.title,
                content.description,
                content.content_type.value,
                json.dumps([p.value for p in content.platforms]),
                json.dumps([asset.__dict__ for asset in content.assets]),
                content.scheduled_time,
                content.timezone_str,
                content.recurring_pattern,
                json.dumps({k.value: v.__dict__ for k, v in content.platform_settings.items()}),
                content.hashtags,
                content.mentions,
                json.dumps(content.location) if content.location else None,
                content.status.value,
                content.max_attempts,
                content.tags,
                content.campaign_id
            )
    
    async def _queue_content_for_scheduling(self, content: ScheduledContent) -> None:
        """
        Queue content in Redis for time-based scheduling
        Demonstrates: DevOps - Queue management and distributed systems
        """
        if not self.redis_client:
            return
        
        # Add to sorted set with scheduled time as score
        schedule_timestamp = content.scheduled_time.timestamp()
        
        await self.redis_client.zadd(
            "scheduled_content_queue",
            {content.content_id: schedule_timestamp}
        )
        
        # Store content details
        await self.redis_client.setex(
            f"content:{content.content_id}",
            86400 * 7,  # 7 days TTL
            json.dumps(content.dict(), default=str)
        )
        
        # Add to creator's content list
        await self.redis_client.lpush(
            f"creator_content:{content.creator_id}",
            content.content_id
        )
        await self.redis_client.expire(f"creator_content:{content.creator_id}", 86400 * 30)
    
    async def _run_scheduler(self) -> None:
        """
        Main scheduler loop
        Demonstrates: DevOps - Background service management
        """
        while True:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Get content ready for publishing
                if self.redis_client:
                    ready_content_ids = await self.redis_client.zrangebyscore(
                        "scheduled_content_queue",
                        0,
                        current_time,
                        withscores=False
                    )
                    
                    for content_id in ready_content_ids:
                        await self._process_scheduled_content(content_id)
                        
                        # Remove from queue
                        await self.redis_client.zrem("scheduled_content_queue", content_id)
                
                # Check for recurring content
                await self._process_recurring_content()
                
                # Health check
                await self.monitoring.record_metric("scheduler_heartbeat", 1)
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await self.monitoring.record_error("scheduler_loop_error", str(e))
                await asyncio.sleep(60)  # Extended sleep on error
    
    async def _process_scheduled_content(self, content_id: str) -> None:
        """
        Process individual scheduled content
        Demonstrates: Microservices - Distributed content processing
        """
        try:
            # Get content from Redis
            if not self.redis_client:
                return
                
            content_data = await self.redis_client.get(f"content:{content_id}")
            if not content_data:
                self.logger.warning(f"Content {content_id} not found in cache")
                return
            
            content_dict = json.loads(content_data)
            content = ScheduledContent(**content_dict)
            
            # Update status to publishing
            content.status = ScheduleStatus.PUBLISHING
            await self._update_content_status(content)
            
            # Publish to each platform
            success_count = 0
            total_platforms = len(content.platforms)
            
            for platform in content.platforms:
                try:
                    result = await self._publish_to_platform(content, platform)
                    if result.get("success"):
                        success_count += 1
                        await self._record_publishing_success(content, platform, result)
                    else:
                        await self._record_publishing_failure(content, platform, result.get("error"))
                
                except Exception as e:
                    self.logger.error(f"Publishing to {platform.value} failed: {e}")
                    await self._record_publishing_failure(content, platform, str(e))
            
            # Update final status
            if success_count == total_platforms:
                content.status = ScheduleStatus.PUBLISHED
                self.metrics["published_count"] += 1
            elif success_count > 0:
                content.status = ScheduleStatus.PUBLISHED  # Partial success
                self.metrics["published_count"] += 1
            else:
                content.status = ScheduleStatus.FAILED
                self.metrics["failed_count"] += 1
                
                # Retry if not exceeded max attempts
                if content.attempts < content.max_attempts:
                    await self._schedule_retry(content)
            
            await self._update_content_status(content)
            
        except Exception as e:
            self.logger.error(f"Failed to process scheduled content {content_id}: {e}")
            await self.monitoring.record_error("process_content_error", str(e))
    
    async def _publish_to_platform(self, content: ScheduledContent, platform: Platform) -> Dict[str, Any]:
        """
        Publish content to specific platform
        Demonstrates: Backend Senior - Platform-specific integration
        """
        try:
            platform_settings = content.platform_settings[platform]
            
            # Prepare platform-specific payload
            payload = await self._prepare_platform_payload(content, platform)
            
            # Use platform coordinator for publishing
            result = await self.platform_coordinator.publish_content(
                platform=platform.value,
                access_token=platform_settings.access_token,
                content_data=payload
            )
            
            return {
                "success": True,
                "platform_post_id": result.get("post_id"),
                "platform_response": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _prepare_platform_payload(self, content: ScheduledContent, platform: Platform) -> Dict[str, Any]:
        """Prepare platform-specific content payload"""
        base_payload = {
            "title": content.title,
            "description": content.description,
            "hashtags": content.hashtags,
            "mentions": content.mentions,
            "location": content.location,
            "assets": [asset.__dict__ for asset in content.assets]
        }
        
        # Platform-specific customizations
        platform_settings = content.platform_settings[platform]
        base_payload.update(platform_settings.custom_settings)
        
        return base_payload
    
    async def _record_publishing_success(self, content: ScheduledContent, platform: Platform, result: Dict[str, Any]) -> None:
        """Record successful publishing in database"""
        if not self.db_pool:
            return
        
        query = """
        INSERT INTO publishing_history (
            content_id, platform, platform_post_id, success, metrics
        ) VALUES ($1, $2, $3, $4, $5)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                content.content_id,
                platform.value,
                result.get("platform_post_id"),
                True,
                json.dumps(result.get("platform_response", {}))
            )
    
    async def _record_publishing_failure(self, content: ScheduledContent, platform: Platform, error: str) -> None:
        """Record publishing failure in database"""
        if not self.db_pool:
            return
        
        query = """
        INSERT INTO publishing_history (
            content_id, platform, success, error_message
        ) VALUES ($1, $2, $3, $4)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                content.content_id,
                platform.value,
                False,
                error
            )
    
    async def _update_content_status(self, content: ScheduledContent) -> None:
        """Update content status in database and cache"""
        content.updated_at = datetime.utcnow()
        
        # Update database
        if self.db_pool:
            query = """
            UPDATE scheduled_content 
            SET status = $1, attempts = $2, error_message = $3, updated_at = $4
            WHERE content_id = $5
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    content.status.value,
                    content.attempts,
                    content.error_message,
                    content.updated_at,
                    content.content_id
                )
        
        # Update cache
        if self.redis_client:
            await self.redis_client.setex(
                f"content:{content.content_id}",
                86400 * 7,
                json.dumps(content.dict(), default=str)
            )
    
    async def _schedule_retry(self, content: ScheduledContent) -> None:
        """Schedule content for retry"""
        content.attempts += 1
        content.status = ScheduleStatus.PENDING
        
        # Exponential backoff: 5, 15, 45 minutes
        retry_delay = 5 * (3 ** (content.attempts - 1))
        retry_time = datetime.utcnow() + timedelta(minutes=retry_delay)
        
        if self.redis_client:
            await self.redis_client.zadd(
                "scheduled_content_queue",
                {content.content_id: retry_time.timestamp()}
            )
        
        self.metrics["retry_count"] += 1
        self.logger.info(f"Scheduled retry for content {content.content_id} in {retry_delay} minutes")
    
    async def _process_recurring_content(self) -> None:
        """Process recurring content schedules"""
        if not self.db_pool:
            return
        
        # Get recurring content that needs to be scheduled
        query = """
        SELECT content_id, recurring_pattern, scheduled_time, timezone_str
        FROM scheduled_content
        WHERE recurring_pattern IS NOT NULL
        AND status = 'published'
        AND scheduled_time < NOW() - INTERVAL '1 hour'
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            for row in rows:
                await self._create_next_recurring_instance(row)
    
    async def _create_next_recurring_instance(self, recurring_row) -> None:
        """Create next instance of recurring content"""
        try:
            # Calculate next occurrence
            cron = croniter(recurring_row['recurring_pattern'], recurring_row['scheduled_time'])
            next_time = cron.get_next(datetime)
            
            # Only schedule if next time is in the future
            if next_time > datetime.utcnow():
                # Get original content
                if self.db_pool:
                    query = "SELECT * FROM scheduled_content WHERE content_id = $1"
                    async with self.db_pool.acquire() as conn:
                        content_row = await conn.fetchrow(query, recurring_row['content_id'])
                        
                        if content_row:
                            # Create new content instance
                            new_content_dict = dict(content_row)
                            new_content_dict['content_id'] = str(uuid.uuid4())
                            new_content_dict['scheduled_time'] = next_time
                            new_content_dict['status'] = ScheduleStatus.SCHEDULED.value
                            new_content_dict['attempts'] = 0
                            new_content_dict['error_message'] = None
                            
                            # Convert to ScheduledContent object
                            new_content_dict['platforms'] = [Platform(p) for p in json.loads(new_content_dict['platforms'])]
                            new_content_dict['content_type'] = ContentType(new_content_dict['content_type'])
                            new_content_dict['assets'] = [ContentAsset(**asset) for asset in json.loads(new_content_dict['assets'])]
                            new_content_dict['platform_settings'] = {
                                Platform(k): PlatformSettings(**v) 
                                for k, v in json.loads(new_content_dict['platform_settings']).items()
                            }
                            
                            new_content = ScheduledContent(**new_content_dict)
                            
                            # Store and queue new instance
                            await self._store_scheduled_content(new_content)
                            await self._queue_content_for_scheduling(new_content)
                            
                            self.logger.info(f"Created recurring instance for content {new_content.content_id}")
                            
        except Exception as e:
            self.logger.error(f"Failed to create recurring instance: {e}")
    
    async def get_scheduled_content(self, creator_id: str, status: Optional[ScheduleStatus] = None, 
                                  limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get scheduled content for a creator
        Demonstrates: DBA - Efficient data retrieval with pagination
        """
        if not self.db_pool:
            return []
        
        query_parts = ["SELECT * FROM scheduled_content WHERE creator_id = $1"]
        params = [creator_id]
        param_count = 1
        
        if status:
            param_count += 1
            query_parts.append(f"AND status = ${param_count}")
            params.append(status.value)
        
        query_parts.extend([
            "ORDER BY scheduled_time ASC",
            f"LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        ])
        params.extend([limit, offset])
        
        query = " ".join(query_parts)
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def cancel_scheduled_content(self, content_id: str, creator_id: str) -> bool:
        """Cancel scheduled content"""
        try:
            # Update database
            if self.db_pool:
                query = """
                UPDATE scheduled_content 
                SET status = 'cancelled', updated_at = NOW()
                WHERE content_id = $1 AND creator_id = $2 AND status IN ('pending', 'scheduled', 'draft')
                """
                
                async with self.db_pool.acquire() as conn:
                    result = await conn.execute(query, content_id, creator_id)
                    
                    if result == "UPDATE 0":
                        return False
            
            # Remove from Redis queue
            if self.redis_client:
                await self.redis_client.zrem("scheduled_content_queue", content_id)
                await self.redis_client.delete(f"content:{content_id}")
            
            await self.audit_logger.log_action(
                action="content_cancelled",
                user_id=creator_id,
                resource_id=content_id
            )
            
            self.logger.info(f"Cancelled scheduled content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel content {content_id}: {e}")
            return False
    
    async def get_scheduling_analytics(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get scheduling analytics for creator
        Demonstrates: ML Engineer - Analytics and performance metrics
        """
        if not self.db_pool:
            return {}
        
        # Get performance metrics
        query = """
        SELECT 
            platform,
            SUM(scheduled_count) as total_scheduled,
            SUM(published_count) as total_published,
            SUM(failed_count) as total_failed,
            AVG(average_engagement) as avg_engagement
        FROM scheduling_analytics
        WHERE creator_id = $1 AND date >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY platform
        """
        
        async with self.db_pool.acquire() as conn:
            analytics_rows = await conn.fetch(query, creator_id, days)
            
            # Get recent content status distribution
            status_query = """
            SELECT status, COUNT(*) as count
            FROM scheduled_content
            WHERE creator_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
            GROUP BY status
            """
            
            status_rows = await conn.fetch(status_query, creator_id, days)
            
            return {
                "platform_analytics": [dict(row) for row in analytics_rows],
                "status_distribution": [dict(row) for row in status_rows],
                "total_metrics": self.metrics.copy(),
                "period_days": days
            }
    
    async def update_analytics(self, creator_id: str, platform: str, metrics: Dict[str, Any]) -> None:
        """Update analytics data"""
        if not self.db_pool:
            return
        
        query = """
        INSERT INTO scheduling_analytics (
            creator_id, date, platform, scheduled_count, published_count, 
            failed_count, average_engagement
        ) VALUES ($1, CURRENT_DATE, $2, $3, $4, $5, $6)
        ON CONFLICT (creator_id, date, platform) DO UPDATE SET
            scheduled_count = scheduling_analytics.scheduled_count + EXCLUDED.scheduled_count,
            published_count = scheduling_analytics.published_count + EXCLUDED.published_count,
            failed_count = scheduling_analytics.failed_count + EXCLUDED.failed_count,
            average_engagement = (scheduling_analytics.average_engagement + EXCLUDED.average_engagement) / 2
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                creator_id,
                platform,
                metrics.get("scheduled_count", 0),
                metrics.get("published_count", 0),
                metrics.get("failed_count", 0),
                metrics.get("average_engagement", 0.0)
            )
    
    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time metric"""
        current_avg = self.metrics["average_processing_time"]
        total_processed = self.metrics["scheduled_count"]
        
        if total_processed == 1:
            self.metrics["average_processing_time"] = processing_time
        else:
            # Weighted average
            self.metrics["average_processing_time"] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Demonstrates: DevOps - Service monitoring and health validation
        """
        health_status = {
            "service": "content_scheduler",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # Check Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check database connection
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status["components"]["database"] = "healthy"
            else:
                health_status["components"]["database"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check scheduler task
            if self.scheduler_task and not self.scheduler_task.done():
                health_status["components"]["scheduler"] = "running"
            else:
                health_status["components"]["scheduler"] = "stopped"
                health_status["status"] = "unhealthy"
            
            # Add performance metrics
            health_status["metrics"] = self.metrics.copy()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup scheduler resources"""
        try:
            # Stop scheduler task
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close database pool
            if self.db_pool:
                await self.db_pool.close()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("Content scheduler cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Utility methods for asset processing
    async def _generate_video_thumbnail(self, video_path: str) -> Optional[str]:
        """Generate thumbnail for video content"""
        # Implementation would use ffmpeg or similar
        return f"{video_path}_thumbnail.jpg"
    
    async def _optimize_image(self, image_path: str) -> None:
        """Optimize image for platform requirements"""
        # Implementation would use PIL/Pillow for optimization
        pass
    
    async def _extract_audio_metadata(self, audio_path: str) -> Dict[str, Any]:
        """Extract audio metadata"""
        return {
            "duration": 0,
            "bitrate": 0,
            "format": "mp3"
        }


# Export main class
__all__ = ["ContentScheduler", "ScheduledContent", "ContentType", "Platform", "ScheduleStatus"]