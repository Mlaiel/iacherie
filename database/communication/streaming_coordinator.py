"""Streaming Coordinator Database Management

Enterprise streaming coordination system for live content delivery,
multi-platform broadcasting, and real-time performance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""import uuid
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
import logging
from contextlib import asynccontextmanager

Base = declarative_base()
logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of streaming content"""    LIVE_MUSIC = "live_music"
    PODCAST = "podcast"
    GAMING = "gaming"
    TUTORIAL = "tutorial"
    INTERVIEW = "interview"
    PRESENTATION = "presentation"
    COMEDY_SHOW = "comedy_show"
    BRAND_EVENT = "brand_event"
    COLLABORATION = "collaboration"
    WORKSHOP = "workshop"


class StreamStatus(Enum):
    """Stream session status"""    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    STARTING = "starting"
    LIVE = "live"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"
    CANCELLED = "cancelled"
    ERROR = "error"


class StreamQuality(Enum):
    """Stream quality settings"""    LOW = "low"          # 480p, 30fps, 1Mbps
    MEDIUM = "medium"    # 720p, 30fps, 2.5Mbps
    HIGH = "high"        # 1080p, 30fps, 5Mbps
    ULTRA = "ultra"      # 1080p, 60fps, 8Mbps
    PREMIUM = "premium"  # 4K, 30fps, 15Mbps


class PlatformType(Enum):
    """Streaming platforms"""    YOUTUBE = "youtube"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    CUSTOM = "custom"


class StreamEventType(Enum):
    """Stream event types"""    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    QUALITY_CHANGE = "quality_change"
    VIEWER_JOIN = "viewer_join"
    VIEWER_LEAVE = "viewer_leave"
    COMMENT = "comment"
    DONATION = "donation"
    FOLLOW = "follow"
    SHARE = "share"
    ERROR = "error"
    MILESTONE = "milestone"


@dataclass
class StreamSettings:
    """Stream configuration settings"""    title: str
    description: str
    quality: StreamQuality = StreamQuality.HIGH
    max_viewers: int = 1000
    enable_chat: bool = True
    enable_donations: bool = False
    enable_recording: bool = True
    auto_start: bool = False
    auto_end_after_minutes: Optional[int] = None
    content_protection: bool = True
    age_restriction: Optional[int] = None
    tags: List[str] = None


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""    platform: PlatformType
    api_key: str
    secret: str
    stream_key: str
    rtmp_url: str
    quality_settings: Dict[str, Any]
    enabled: bool = True
    auto_publish: bool = False


class StreamSession(Base):
    """Stream session model"""    __tablename__ = "stream_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    streamer_id = Column(String(255), nullable=False, index=True)
    creator_type = Column(String(50))
    
    # Stream details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    stream_type = Column(String(100), nullable=False)
    status = Column(String(50), default=StreamStatus.SCHEDULED.value)
    
    # Technical settings
    quality = Column(String(50), default=StreamQuality.HIGH.value)
    rtmp_url = Column(String(500))
    stream_key = Column(String(255))
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Configuration
    settings = Column(JSON)
    platforms = Column(JSON)  # Platform configurations
    
    # Statistics
    max_concurrent_viewers = Column(Integer, default=0)
    total_viewers = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_donations = Column(Float, default=0.0)
    
    # Performance metrics
    avg_bitrate = Column(Float)
    avg_fps = Column(Float)
    dropped_frames = Column(Integer, default=0)
    connection_issues = Column(Integer, default=0)
    
    # Content protection
    content_fingerprint = Column(String(255))
    protection_level = Column(String(50))
    copyright_claims = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    tags = Column(ARRAY(String))
    thumbnail_url = Column(String(500))
    recording_url = Column(String(500))
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_stream_streamer_status', 'streamer_id', 'status'),
        Index('idx_stream_scheduled_start', 'scheduled_start'),
    )


class StreamViewer(Base):
    """Stream viewer tracking"""    __tablename__ = "stream_viewers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    viewer_id = Column(String(255), index=True)  # Can be anonymous
    
    # Viewer details
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    location = Column(JSON)
    device_type = Column(String(50))
    
    # Session tracking
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime(timezone=True))
    watch_time_seconds = Column(Integer, default=0)
    
    # Quality metrics
    selected_quality = Column(String(50))
    quality_changes = Column(Integer, default=0)
    buffer_events = Column(Integer, default=0)
    
    # Engagement
    comments_sent = Column(Integer, default=0)
    reactions_sent = Column(Integer, default=0)
    shares_made = Column(Integer, default=0)
    donations_made = Column(Float, default=0.0)
    
    # Analytics
    referrer = Column(String(500))
    platform = Column(String(50))
    is_subscriber = Column(Boolean, default=False)
    is_repeat_viewer = Column(Boolean, default=False)
    
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_viewer_session_joined', 'session_id', 'joined_at'),
        Index('idx_viewer_platform', 'platform'),
    )


class StreamEvent(Base):
    """Stream event tracking"""    __tablename__ = "stream_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    
    # Event details
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    description = Column(Text)
    details = Column(JSON)
    
    # Actor (who caused the event)
    actor_id = Column(String(255))
    actor_type = Column(String(50))  # streamer, viewer, system, platform
    
    # Platform specific
    platform = Column(String(50))
    platform_event_id = Column(String(255))
    
    # Metrics
    viewer_count_at_time = Column(Integer)
    quality_at_time = Column(String(50))
    
    # Processing
    processed = Column(Boolean, default=False)
    ai_analysis = Column(JSON)
    
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_event_session_time', 'session_id', 'timestamp'),
        Index('idx_event_type_platform', 'event_type', 'platform'),
    )


class StreamAnalytics(Base):
    """Stream analytics aggregation"""    __tablename__ = "stream_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Time aggregation
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    aggregation_type = Column(String(50), nullable=False)  # minute, hour, day
    
    # Viewer metrics
    avg_viewers = Column(Float)
    max_viewers = Column(Integer)
    unique_viewers = Column(Integer)
    new_viewers = Column(Integer)
    returning_viewers = Column(Integer)
    
    # Engagement metrics
    total_comments = Column(Integer, default=0)
    total_reactions = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_donations = Column(Float, default=0.0)
    avg_watch_time = Column(Float)
    
    # Quality metrics
    avg_bitrate = Column(Float)
    avg_fps = Column(Float)
    quality_distribution = Column(JSON)  # {quality: percentage}
    buffer_rate = Column(Float)
    
    # Platform breakdown
    platform_stats = Column(JSON)
    
    # Geographic data
    geographic_distribution = Column(JSON)
    
    # Device analytics
    device_distribution = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_analytics_session_period', 'session_id', 'period_start', 'period_end'),
        Index('idx_analytics_aggregation_time', 'aggregation_type', 'period_start'),
    )


class PlatformStream(Base):
    """Platform-specific stream instances"""    __tablename__ = "platform_streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    
    # Platform identifiers
    platform_stream_id = Column(String(255))
    platform_url = Column(String(500))
    rtmp_endpoint = Column(String(500))
    stream_key = Column(String(255))
    
    # Status
    status = Column(String(50))
    enabled = Column(Boolean, default=True)
    
    # Configuration
    quality_settings = Column(JSON)
    platform_settings = Column(JSON)
    
    # Statistics
    platform_viewers = Column(Integer, default=0)
    platform_comments = Column(Integer, default=0)
    platform_shares = Column(Integer, default=0)
    platform_followers_gained = Column(Integer, default=0)
    
    # Performance
    upload_bitrate = Column(Float)
    connection_quality = Column(String(50))
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    last_heartbeat = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_platform_stream_session', 'session_id', 'platform'),
        Index('idx_platform_stream_status', 'platform', 'status'),
    )


class StreamingCoordinator:
    """Enterprise streaming coordination system"""    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_subscribers: Dict[str, Set[Callable]] = {}
        self.platform_handlers: Dict[PlatformType, Any] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
    
    async def initialize(self):
        """Initialize streaming coordinator"""        try:
            # Load active streams
            await self._load_active_streams()
            
            # Initialize platform handlers
            await self._initialize_platform_handlers()
            
            # Start background workers
            await self._start_workers()
            
            self.running = True
            logger.info("Streaming coordinator initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize streaming coordinator: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""        self.running = False
        
        # End all active streams
        for session_id in list(self.active_streams.keys()):
            await self._emergency_stop_stream(session_id)
        
        # Stop workers
        for task in self.worker_tasks:
            task.cancel()
        
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("Streaming coordinator shutdown completed")
    
    async def create_stream(
        self,
        streamer_id: str,
        title: str,
        stream_type: StreamType,
        settings: StreamSettings,
        platforms: List[PlatformConfig],
        scheduled_start: Optional[datetime] = None,
        scheduled_end: Optional[datetime] = None
    ) -> str:
        """Create new stream session"""        try:
            session_id = f"stream_{uuid.uuid4().hex[:12]}"
            
            # Create stream session
            stream = StreamSession(
                session_id=session_id,
                streamer_id=streamer_id,
                title=title,
                description=settings.description,
                stream_type=stream_type.value,
                quality=settings.quality.value,
                scheduled_start=scheduled_start or datetime.now(timezone.utc),
                scheduled_end=scheduled_end,
                settings=asdict(settings),
                platforms=[asdict(p) for p in platforms],
                tags=settings.tags or [],
                status=StreamStatus.SCHEDULED.value
            )
            
            self.db.add(stream)
            
            # Create platform stream instances
            for platform_config in platforms:
                platform_stream = PlatformStream(
                    session_id=session_id,
                    platform=platform_config.platform.value,
                    platform_settings=asdict(platform_config),
                    quality_settings=platform_config.quality_settings,
                    enabled=platform_config.enabled
                )
                
                self.db.add(platform_stream)
            
            self.db.commit()
            
            # Initialize in Redis
            await self._initialize_stream_redis(session_id)
            
            # Track creation event
            await self._log_stream_event(
                session_id=session_id,
                event_type=StreamEventType.START,
                description=f"Stream created: {title}",
                actor_id=streamer_id,
                actor_type="streamer"
            )
            
            logger.info(f"Created stream session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create stream: {e}")
            self.db.rollback()
            raise
    
    async def start_stream(self, session_id: str, streamer_id: str) -> bool:
        """Start stream session"""        try:
            # Get stream
            stream = self.db.query(StreamSession).filter(
                StreamSession.session_id == session_id,
                StreamSession.streamer_id == streamer_id,
                StreamSession.status.in_([StreamStatus.SCHEDULED.value, StreamStatus.PREPARING.value])
            ).first()
            
            if not stream:
                raise ValueError(f"Stream {session_id} not found or not startable")
            
            # Update status
            stream.status = StreamStatus.STARTING.value
            stream.actual_start = datetime.now(timezone.utc)
            self.db.commit()
            
            # Start on all enabled platforms
            platform_streams = self.db.query(PlatformStream).filter(
                PlatformStream.session_id == session_id,
                PlatformStream.enabled == True
            ).all()
            
            success_count = 0
            for platform_stream in platform_streams:
                try:
                    await self._start_platform_stream(platform_stream)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to start stream on {platform_stream.platform}: {e}")
                    platform_stream.last_error = str(e)
                    platform_stream.error_count += 1
            
            if success_count > 0:
                # Update stream status to live
                stream.status = StreamStatus.LIVE.value
                self.active_streams[session_id] = {
                    "status": StreamStatus.LIVE.value,
                    "started_at": datetime.now(timezone.utc),
                    "platforms": [p.platform for p in platform_streams if p.enabled]
                }
                
                # Log event
                await self._log_stream_event(
                    session_id=session_id,
                    event_type=StreamEventType.START,
                    description=f"Stream started on {success_count} platforms",
                    actor_id=streamer_id,
                    actor_type="streamer"
                )
                
                # Start monitoring
                await self._start_stream_monitoring(session_id)
                
                logger.info(f"Started stream {session_id} on {success_count} platforms")
                return True
            else:
                stream.status = StreamStatus.ERROR.value
                logger.error(f"Failed to start stream {session_id} on any platform")
                return False
            
        except Exception as e:
            logger.error(f"Failed to start stream {session_id}: {e}")
            self.db.rollback()
            return False
    
    async def stop_stream(self, session_id: str, streamer_id: str) -> bool:
        """Stop stream session"""        try:
            # Get stream
            stream = self.db.query(StreamSession).filter(
                StreamSession.session_id == session_id,
                StreamSession.streamer_id == streamer_id,
                StreamSession.status == StreamStatus.LIVE.value
            ).first()
            
            if not stream:
                raise ValueError(f"Stream {session_id} not found or not live")
            
            # Update status
            stream.status = StreamStatus.ENDING.value
            self.db.commit()
            
            # Stop on all platforms
            platform_streams = self.db.query(PlatformStream).filter(
                PlatformStream.session_id == session_id
            ).all()
            
            for platform_stream in platform_streams:
                try:
                    await self._stop_platform_stream(platform_stream)
                except Exception as e:
                    logger.error(f"Failed to stop stream on {platform_stream.platform}: {e}")
            
            # Finalize stream
            stream.status = StreamStatus.ENDED.value
            stream.actual_end = datetime.now(timezone.utc)
            
            if stream.actual_start:
                duration = (stream.actual_end - stream.actual_start).total_seconds()
                # Update analytics would go here
            
            self.db.commit()
            
            # Remove from active streams
            self.active_streams.pop(session_id, None)
            
            # Stop monitoring
            await self._stop_stream_monitoring(session_id)
            
            # Log event
            await self._log_stream_event(
                session_id=session_id,
                event_type=StreamEventType.STOP,
                description="Stream ended",
                actor_id=streamer_id,
                actor_type="streamer"
            )
            
            logger.info(f"Stopped stream {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {session_id}: {e}")
            self.db.rollback()
            return False
    
    async def add_viewer(
        self,
        session_id: str,
        viewer_id: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        platform: Optional[str] = None
    ) -> str:
        """Add viewer to stream"""        try:
            # Generate viewer ID if anonymous
            if not viewer_id:
                viewer_id = f"anon_{uuid.uuid4().hex[:8]}"
            
            # Check if stream is live
            stream = self.db.query(StreamSession).filter(
                StreamSession.session_id == session_id,
                StreamSession.status == StreamStatus.LIVE.value
            ).first()
            
            if not stream:
                raise ValueError(f"Stream {session_id} not live")
            
            # Create viewer record
            viewer = StreamViewer(
                session_id=session_id,
                viewer_id=viewer_id,
                device_type=device_info.get("type") if device_info else None,
                user_agent=device_info.get("user_agent") if device_info else None,
                ip_address=device_info.get("ip") if device_info else None,
                platform=platform,
                joined_at=datetime.now(timezone.utc)
            )
            
            self.db.add(viewer)
            
            # Update stream stats
            current_viewers = await self.redis.scard(f"stream:{session_id}:viewers")
            await self.redis.sadd(f"stream:{session_id}:viewers", viewer_id)
            
            new_viewer_count = current_viewers + 1
            if new_viewer_count > stream.max_concurrent_viewers:
                stream.max_concurrent_viewers = new_viewer_count
            
            stream.total_viewers += 1
            self.db.commit()
            
            # Log event
            await self._log_stream_event(
                session_id=session_id,
                event_type=StreamEventType.VIEWER_JOIN,
                description=f"Viewer joined",
                actor_id=viewer_id,
                actor_type="viewer",
                details={"viewer_count": new_viewer_count}
            )
            
            # Broadcast viewer update
            await self._broadcast_viewer_update(session_id, new_viewer_count)
            
            logger.debug(f"Viewer {viewer_id} joined stream {session_id}")
            return viewer_id
            
        except Exception as e:
            logger.error(f"Failed to add viewer to stream {session_id}: {e}")
            self.db.rollback()
            raise
    
    async def remove_viewer(self, session_id: str, viewer_id: str) -> bool:
        """Remove viewer from stream"""        try:
            # Update viewer record
            viewer = self.db.query(StreamViewer).filter(
                StreamViewer.session_id == session_id,
                StreamViewer.viewer_id == viewer_id,
                StreamViewer.left_at.is_(None)
            ).first()
            
            if viewer:
                viewer.left_at = datetime.now(timezone.utc)
                if viewer.joined_at:
                    watch_time = (viewer.left_at - viewer.joined_at).total_seconds()
                    viewer.watch_time_seconds = int(watch_time)
            
            # Remove from Redis
            await self.redis.srem(f"stream:{session_id}:viewers", viewer_id)
            current_viewers = await self.redis.scard(f"stream:{session_id}:viewers")
            
            self.db.commit()
            
            # Log event
            await self._log_stream_event(
                session_id=session_id,
                event_type=StreamEventType.VIEWER_LEAVE,
                description=f"Viewer left",
                actor_id=viewer_id,
                actor_type="viewer",
                details={"viewer_count": current_viewers}
            )
            
            # Broadcast viewer update
            await self._broadcast_viewer_update(session_id, current_viewers)
            
            logger.debug(f"Viewer {viewer_id} left stream {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove viewer from stream {session_id}: {e}")
            self.db.rollback()
            return False
    
    async def get_stream_stats(self, session_id: str) -> Dict[str, Any]:
        """Get real-time stream statistics"""        try:
            # Get stream info
            stream = self.db.query(StreamSession).filter(
                StreamSession.session_id == session_id
            ).first()
            
            if not stream:
                return {}
            
            # Get current viewer count
            current_viewers = await self.redis.scard(f"stream:{session_id}:viewers")
            
            # Get platform stats
            platform_streams = self.db.query(PlatformStream).filter(
                PlatformStream.session_id == session_id
            ).all()
            
            platform_stats = {}
            for ps in platform_streams:
                platform_stats[ps.platform] = {
                    "status": ps.status,
                    "viewers": ps.platform_viewers,
                    "connection_quality": ps.connection_quality,
                    "errors": ps.error_count
                }
            
            # Calculate duration
            duration_seconds = 0
            if stream.actual_start:
                end_time = stream.actual_end or datetime.now(timezone.utc)
                duration_seconds = int((end_time - stream.actual_start).total_seconds())
            
            return {
                "session_id": session_id,
                "status": stream.status,
                "title": stream.title,
                "current_viewers": current_viewers,
                "max_viewers": stream.max_concurrent_viewers,
                "total_viewers": stream.total_viewers,
                "duration_seconds": duration_seconds,
                "platform_stats": platform_stats,
                "quality": stream.quality,
                "started_at": stream.actual_start.isoformat() if stream.actual_start else None,
                "stats": {
                    "comments": stream.total_comments,
                    "shares": stream.total_shares,
                    "donations": stream.total_donations
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stream stats: {e}")
            return {}
    
    async def subscribe_to_stream(self, session_id: str, callback: Callable):
        """Subscribe to stream events"""        if session_id not in self.stream_subscribers:
            self.stream_subscribers[session_id] = set()
        
        self.stream_subscribers[session_id].add(callback)
        
        # Subscribe to Redis events
        await self.redis.subscribe(f"stream:{session_id}")
        
        logger.info(f"Subscribed to stream events: {session_id}")
    
    async def unsubscribe_from_stream(self, session_id: str, callback: Callable):
        """Unsubscribe from stream events"""        if session_id in self.stream_subscribers:
            self.stream_subscribers[session_id].discard(callback)
            
            if not self.stream_subscribers[session_id]:
                del self.stream_subscribers[session_id]
                await self.redis.unsubscribe(f"stream:{session_id}")
    
    # Private methods
    
    async def _load_active_streams(self):
        """Load active streams from database"""        active = self.db.query(StreamSession).filter(
            StreamSession.status.in_([StreamStatus.LIVE.value, StreamStatus.STARTING.value])
        ).all()
        
        for stream in active:
            self.active_streams[stream.session_id] = {
                "status": stream.status,
                "started_at": stream.actual_start,
                "streamer_id": stream.streamer_id
            }
    
    async def _initialize_platform_handlers(self):
        """Initialize platform-specific handlers"""        try:
            # YouTube Live handler
            self.platform_handlers[StreamPlatform.YOUTUBE] = await self._create_youtube_handler()
            
            # Twitch handler
            self.platform_handlers[StreamPlatform.TWITCH] = await self._create_twitch_handler()
            
            # Facebook Live handler
            self.platform_handlers[StreamPlatform.FACEBOOK] = await self._create_facebook_handler()
            
            # Instagram Live handler
            self.platform_handlers[StreamPlatform.INSTAGRAM] = await self._create_instagram_handler()
            
            # TikTok Live handler
            self.platform_handlers[StreamPlatform.TIKTOK] = await self._create_tiktok_handler()
            
            # LinkedIn Live handler
            self.platform_handlers[StreamPlatform.LINKEDIN] = await self._create_linkedin_handler()
            
            logger.info(f"Initialized {len(self.platform_handlers)} platform handlers")
            
        except Exception as e:
            logger.error(f"Failed to initialize platform handlers: {e}")
            raise
    
    async def _create_youtube_handler(self):
        """Create YouTube Live streaming handler"""        return {
            'api_endpoint': 'https://www.googleapis.com/youtube/v3/liveStreams',
            'rtmp_base': 'rtmp://a.rtmp.youtube.com/live2',
            'max_bitrate': 8000000,  # 8 Mbps
            'supported_formats': ['H.264', 'HEVC'],
            'required_scopes': ['https://www.googleapis.com/auth/youtube.force-ssl']
        }
    
    async def _create_twitch_handler(self):
        """Create Twitch streaming handler"""        return {
            'api_endpoint': 'https://api.twitch.tv/helix/streams',
            'rtmp_base': 'rtmp://live.twitch.tv/app',
            'max_bitrate': 6000000,  # 6 Mbps
            'supported_formats': ['H.264'],
            'required_scopes': ['channel:manage:broadcast']
        }
    
    async def _create_facebook_handler(self):
        """Create Facebook Live streaming handler"""        return {
            'api_endpoint': 'https://graph.facebook.com/v18.0/live_videos',
            'rtmp_base': 'rtmps://live-api-s.facebook.com:443/rtmp',
            'max_bitrate': 4000000,  # 4 Mbps
            'supported_formats': ['H.264'],
            'required_scopes': ['publish_video', 'manage_pages']
        }
    
    async def _create_instagram_handler(self):
        """Create Instagram Live streaming handler"""        return {
            'api_endpoint': 'https://graph.instagram.com/live_media',
            'rtmp_base': 'rtmps://live-upload.instagram.com:443/rtmp',
            'max_bitrate': 3500000,  # 3.5 Mbps
            'supported_formats': ['H.264'],
            'required_scopes': ['instagram_basic', 'instagram_content_publish']
        }
    
    async def _create_tiktok_handler(self):
        """Create TikTok Live streaming handler"""        return {
            'api_endpoint': 'https://open-api.tiktok.com/live/create',
            'rtmp_base': 'rtmp://push.tiktokcdn.com/live',
            'max_bitrate': 3000000,  # 3 Mbps
            'supported_formats': ['H.264'],
            'required_scopes': ['live.room']
        }
    
    async def _create_linkedin_handler(self):
        """Create LinkedIn Live streaming handler"""        return {
            'api_endpoint': 'https://api.linkedin.com/v2/liveVideoSessions',
            'rtmp_base': 'rtmp://linkedin-live.com/live',
            'max_bitrate': 2500000,  # 2.5 Mbps
            'supported_formats': ['H.264'],
            'required_scopes': ['w_member_social']
        }
    
    async def _start_workers(self):
        """Start background worker tasks"""        self.worker_tasks.extend([
            asyncio.create_task(self._stream_health_monitor()),
            asyncio.create_task(self._analytics_aggregator()),
            asyncio.create_task(self._platform_sync_worker())
        ])
    
    async def _initialize_stream_redis(self, session_id: str):
        """Initialize Redis structures for stream"""        await self.redis.delete(f"stream:{session_id}:viewers")
        await self.redis.setex(
            f"stream:{session_id}:created",
            86400,
            datetime.now(timezone.utc).isoformat()
        )
    
    async def _start_platform_stream(self, platform_stream: PlatformStream):
        """Start stream on specific platform"""        # Platform-specific implementation
        platform_stream.started_at = datetime.now(timezone.utc)
        platform_stream.status = StreamStatus.LIVE.value
        self.db.commit()
    
    async def _stop_platform_stream(self, platform_stream: PlatformStream):
        """Stop stream on specific platform"""        platform_stream.ended_at = datetime.now(timezone.utc)
        platform_stream.status = StreamStatus.ENDED.value
        self.db.commit()
    
    async def _start_stream_monitoring(self, session_id: str):
        """Start monitoring stream health"""        await self.redis.setex(f"stream:{session_id}:monitoring", 3600, "active")
    
    async def _stop_stream_monitoring(self, session_id: str):
        """Stop monitoring stream"""        await self.redis.delete(f"stream:{session_id}:monitoring")
        await self.redis.delete(f"stream:{session_id}:viewers")
    
    async def _emergency_stop_stream(self, session_id: str):
        """Emergency stop for stream"""        try:
            stream = self.db.query(StreamSession).filter(
                StreamSession.session_id == session_id
            ).first()
            
            if stream:
                stream.status = StreamStatus.ERROR.value
                stream.actual_end = datetime.now(timezone.utc)
                self.db.commit()
            
            # Cleanup Redis
            await self._stop_stream_monitoring(session_id)
            
        except Exception as e:
            logger.error(f"Emergency stop failed for {session_id}: {e}")
    
    async def _log_stream_event(
        self,
        session_id: str,
        event_type: StreamEventType,
        description: str,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log stream event"""        event = StreamEvent(
            session_id=session_id,
            event_type=event_type.value,
            description=description,
            actor_id=actor_id,
            actor_type=actor_type,
            details=details or {},
            timestamp=datetime.now(timezone.utc)
        )
        
        self.db.add(event)
        self.db.commit()
    
    async def _broadcast_viewer_update(self, session_id: str, viewer_count: int):
        """Broadcast viewer count update"""        message = {
            "type": "viewer_update",
            "session_id": session_id,
            "viewer_count": viewer_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish to Redis
        await self.redis.publish(f"stream:{session_id}", json.dumps(message))
        
        # Call local subscribers
        if session_id in self.stream_subscribers:
            for callback in self.stream_subscribers[session_id]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Stream subscriber callback failed: {e}")
    
    async def _stream_health_monitor(self):
        """Monitor stream health"""        while self.running:
            try:
                await asyncio.sleep(30)
                # Monitor stream health metrics
                
            except Exception as e:
                logger.error(f"Stream health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _analytics_aggregator(self):
        """Aggregate streaming analytics"""        while self.running:
            try:
                await asyncio.sleep(60)
                # Aggregate analytics data
                
            except Exception as e:
                logger.error(f"Analytics aggregator error: {e}")
                await asyncio.sleep(30)
    
    async def _platform_sync_worker(self):
        """Sync with platform APIs"""        while self.running:
            try:
                await asyncio.sleep(120)
                # Sync platform data
                
            except Exception as e:
                logger.error(f"Platform sync worker error: {e}")
                await asyncio.sleep(60)


@asynccontextmanager
async def get_streaming_coordinator(redis_client: redis.Redis, db_session: Session):
    """Context manager for streaming coordinator"""    coordinator = StreamingCoordinator(redis_client, db_session)
    try:
        await coordinator.initialize()
        yield coordinator
    finally:
        await coordinator.shutdown()
