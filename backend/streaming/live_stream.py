"""Live Streaming Management System
===================================

Enterprise-grade live streaming management for multi-platform broadcasting,
real-time performance monitoring, and viewer engagement analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import websockets
from websockets.server import WebSocketServerProtocol

Base = declarative_base()
logger = logging.getLogger(__name__)


class StreamStatus(Enum):
    """Live stream status enumeration"""
    IDLE = "idle"
    STARTING = "starting"
    LIVE = "live"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class StreamQuality(Enum):
    """Stream quality settings"""
    LOW = "low"        # 480p, 1 Mbps
    MEDIUM = "medium"  # 720p, 2.5 Mbps
    HIGH = "high"      # 1080p, 5 Mbps
    ULTRA = "ultra"    # 4K, 15 Mbps


class PlatformType(Enum):
    """Supported streaming platforms"""
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    KICK = "kick"
    CUSTOM = "custom"


@dataclass
class StreamMetrics:
    """Real-time stream performance metrics"""
    stream_id: str
    viewer_count: int = 0
    peak_viewers: int = 0
    avg_bitrate: float = 0.0
    dropped_frames: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    upload_speed: float = 0.0
    latency_ms: float = 0.0
    chat_messages: int = 0
    likes: int = 0
    shares: int = 0
    donations_total: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StreamConfig:
    """Stream configuration settings"""
    title: str
    description: str = ""
    quality: StreamQuality = StreamQuality.HIGH
    platforms: List[PlatformType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_private: bool = False
    enable_chat: bool = True
    enable_donations: bool = True
    auto_record: bool = True
    max_duration_minutes: Optional[int] = None
    thumbnail_url: Optional[str] = None
    rtmp_settings: Dict[str, Any] = field(default_factory=dict)


class LiveStream(Base):
    """Database model for live streams"""
    __tablename__ = "live_streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=StreamStatus.IDLE.value)
    quality = Column(String(50), default=StreamQuality.HIGH.value)
    
    # Stream configuration
    platforms = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    is_private = Column(Boolean, default=False)
    enable_chat = Column(Boolean, default=True)
    enable_donations = Column(Boolean, default=True)
    auto_record = Column(Boolean, default=True)
    
    # Technical settings
    rtmp_url = Column(String(500))
    stream_key = Column(String(255))
    rtmp_settings = Column(JSON, default=dict)
    
    # Metrics
    viewer_count = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    total_duration_minutes = Column(Integer, default=0)
    chat_messages_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    donations_total = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LiveStreamManager:
    """Enterprise live streaming management system"""
    
    def __init__(self, redis_client: Any, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.active_streams: Dict[str, "LiveStreamSession"] = {}
        self.websocket_connections: Dict[str, List[WebSocketServerProtocol]] = {}
        self.metrics_update_interval = 5  # seconds
        self.is_running = False
        
    async def start_manager(self):
        """Start the live streaming manager"""
        self.is_running = True
        logger.info("Live streaming manager started")
        
        # Start background tasks
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._cleanup_inactive_streams())
        
    async def stop_manager(self):
        """Stop the live streaming manager"""
        self.is_running = False
        
        # Stop all active streams
        for stream_id in list(self.active_streams.keys()):
            await self.stop_stream(stream_id)
            
        logger.info("Live streaming manager stopped")
        
    async def create_stream(self, user_id: str, config: StreamConfig) -> str:
        """Create a new live stream"""
        try:
            stream_id = str(uuid.uuid4())
            
            # Create database record
            stream_record = LiveStream(
                id=stream_id,
                user_id=user_id,
                title=config.title,
                description=config.description,
                quality=config.quality.value,
                platforms=[p.value for p in config.platforms],
                tags=config.tags,
                is_private=config.is_private,
                enable_chat=config.enable_chat,
                enable_donations=config.enable_donations,
                auto_record=config.auto_record,
                rtmp_settings=config.rtmp_settings
            )
            
            self.db.add(stream_record)
            self.db.commit()
            
            # Generate RTMP settings
            rtmp_config = await self._generate_rtmp_config(stream_id, config)
            stream_record.rtmp_url = rtmp_config["url"]
            stream_record.stream_key = rtmp_config["key"]
            self.db.commit()
            
            # Create stream session
            session = LiveStreamSession(
                stream_id=stream_id,
                user_id=user_id,
                config=config,
                rtmp_config=rtmp_config
            )
            
            self.active_streams[stream_id] = session
            
            # Store in Redis for quick access
            await self.redis.hset(
                f"stream:{stream_id}",
                mapping={
                    "user_id": user_id,
                    "status": StreamStatus.IDLE.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "config": json.dumps(asdict(config), default=str)
                }
            )
            
            logger.info(f"Stream created: {stream_id} for user: {user_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to create stream: {str(e)}")
            raise
            
    async def start_stream(self, stream_id: str) -> bool:
        """Start a live stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                logger.error(f"Stream session not found: {stream_id}")
                return False
                
            # Update status
            session.status = StreamStatus.STARTING
            await self._update_stream_status(stream_id, StreamStatus.STARTING)
            
            # Initialize streaming components
            await self._initialize_rtmp_server(session)
            await self._start_platform_streams(session)
            await self._initialize_chat_system(session)
            
            # Update to live status
            session.status = StreamStatus.LIVE
            session.started_at = datetime.now(timezone.utc)
            await self._update_stream_status(stream_id, StreamStatus.LIVE)
            
            # Update database
            stream_record = self.db.query(LiveStream).filter(LiveStream.id == stream_id).first()
            if stream_record:
                stream_record.status = StreamStatus.LIVE.value
                stream_record.started_at = session.started_at
                self.db.commit()
            
            # Notify connected clients
            await self._broadcast_stream_event(stream_id, "stream_started", {
                "stream_id": stream_id,
                "rtmp_url": session.rtmp_config["url"],
                "stream_key": session.rtmp_config["key"]
            })
            
            logger.info(f"Stream started: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {str(e)}")
            await self._update_stream_status(stream_id, StreamStatus.ERROR)
            return False
            
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop a live stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                logger.warning(f"Stream session not found: {stream_id}")
                return False
                
            # Update status
            session.status = StreamStatus.STOPPING
            await self._update_stream_status(stream_id, StreamStatus.STOPPING)
            
            # Stop streaming components
            await self._stop_platform_streams(session)
            await self._cleanup_rtmp_server(session)
            
            # Calculate duration
            if session.started_at:
                duration = datetime.now(timezone.utc) - session.started_at
                session.total_duration_minutes = int(duration.total_seconds() / 60)
            
            # Update status
            session.status = StreamStatus.STOPPED
            session.ended_at = datetime.now(timezone.utc)
            await self._update_stream_status(stream_id, StreamStatus.STOPPED)
            
            # Update database
            stream_record = self.db.query(LiveStream).filter(LiveStream.id == stream_id).first()
            if stream_record:
                stream_record.status = StreamStatus.STOPPED.value
                stream_record.ended_at = session.ended_at
                stream_record.total_duration_minutes = session.total_duration_minutes
                stream_record.peak_viewers = session.metrics.peak_viewers
                stream_record.chat_messages_count = session.metrics.chat_messages
                stream_record.donations_total = session.metrics.donations_total
                self.db.commit()
            
            # Notify connected clients
            await self._broadcast_stream_event(stream_id, "stream_stopped", {
                "stream_id": stream_id,
                "duration_minutes": session.total_duration_minutes,
                "peak_viewers": session.metrics.peak_viewers
            })
            
            # Clean up session
            del self.active_streams[stream_id]
            await self.redis.delete(f"stream:{stream_id}")
            
            logger.info(f"Stream stopped: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {str(e)}")
            return False
            
    async def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                return None
                
            return {
                "stream_id": stream_id,
                "user_id": session.user_id,
                "status": session.status.value,
                "config": asdict(session.config),
                "metrics": asdict(session.metrics),
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "duration_minutes": session.total_duration_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to get stream info {stream_id}: {str(e)}")
            return None
            
    async def connect_websocket(self, stream_id: str, websocket: WebSocketServerProtocol):
        """Connect a WebSocket client to stream events"""
        if stream_id not in self.websocket_connections:
            self.websocket_connections[stream_id] = []
            
        self.websocket_connections[stream_id].append(websocket)
        logger.info(f"WebSocket connected to stream {stream_id}")
        
    async def disconnect_websocket(self, stream_id: str, websocket: WebSocketServerProtocol):
        """Disconnect a WebSocket client"""
        if stream_id in self.websocket_connections:
            try:
                self.websocket_connections[stream_id].remove(websocket)
                if not self.websocket_connections[stream_id]:
                    del self.websocket_connections[stream_id]
            except ValueError:
                pass
                
        logger.info(f"WebSocket disconnected from stream {stream_id}")
        
    async def _generate_rtmp_config(self, stream_id: str, config: StreamConfig) -> Dict[str, str]:
        """Generate RTMP configuration for stream"""
        rtmp_url = f"rtmp://live.ainflue.com/live"
        stream_key = f"{stream_id}_{uuid.uuid4().hex[:8]}"
        
        return {
            "url": rtmp_url,
            "key": stream_key,
            "quality": config.quality.value
        }
        
    async def _update_stream_status(self, stream_id: str, status: StreamStatus):
        """Update stream status in Redis"""
        await self.redis.hset(f"stream:{stream_id}", "status", status.value)
        await self.redis.hset(f"stream:{stream_id}", "updated_at", datetime.now(timezone.utc).isoformat())
        
    async def _initialize_rtmp_server(self, session: "LiveStreamSession"):
        """Initialize RTMP server for stream"""
        # Implementation would integrate with RTMP server
        logger.info(f"RTMP server initialized for stream {session.stream_id}")
        
    async def _start_platform_streams(self, session: "LiveStreamSession"):
        """Start streaming to configured platforms"""
        for platform in session.config.platforms:
            logger.info(f"Starting {platform.value} stream for {session.stream_id}")
            # Implementation would integrate with platform APIs
            
    async def _stop_platform_streams(self, session: "LiveStreamSession"):
        """Stop streaming to all platforms"""
        for platform in session.config.platforms:
            logger.info(f"Stopping {platform.value} stream for {session.stream_id}")
            # Implementation would stop platform streams
            
    async def _initialize_chat_system(self, session: "LiveStreamSession"):
        """Initialize chat system for stream"""
        if session.config.enable_chat:
            logger.info(f"Chat system initialized for stream {session.stream_id}")
            # Implementation would initialize chat moderator
            
    async def _cleanup_rtmp_server(self, session: "LiveStreamSession"):
        """Clean up RTMP server resources"""
        logger.info(f"RTMP server cleaned up for stream {session.stream_id}")
        
    async def _broadcast_stream_event(self, stream_id: str, event_type: str, data: Dict[str, Any]):
        """Broadcast event to connected WebSocket clients"""
        if stream_id not in self.websocket_connections:
            return
            
        message = json.dumps({
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data
        })
        
        disconnected = []
        for websocket in self.websocket_connections[stream_id]:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
                
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect_websocket(stream_id, ws)
            
    async def _metrics_updater(self):
        """Background task to update stream metrics"""
        while self.is_running:
            try:
                for stream_id, session in self.active_streams.items():
                    if session.status == StreamStatus.LIVE:
                        await self._update_stream_metrics(session)
                        
                await asyncio.sleep(self.metrics_update_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics updater: {str(e)}")
                await asyncio.sleep(5)
                
    async def _update_stream_metrics(self, session: "LiveStreamSession"):
        """Update metrics for a live stream"""
        try:
            # Get current metrics (implementation would collect real metrics)
            session.metrics.timestamp = datetime.now(timezone.utc)
            
            # Store metrics in Redis
            await self.redis.hset(
                f"stream:{session.stream_id}:metrics",
                mapping=asdict(session.metrics)
            )
            
            # Broadcast metrics to connected clients
            await self._broadcast_stream_event(session.stream_id, "metrics_update", {
                "metrics": asdict(session.metrics)
            })
            
        except Exception as e:
            logger.error(f"Failed to update metrics for stream {session.stream_id}: {str(e)}")
            
    async def _cleanup_inactive_streams(self):
        """Background task to clean up inactive streams"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                inactive_streams = []
                
                for stream_id, session in self.active_streams.items():
                    # Check for streams that haven't been active
                    if session.status == StreamStatus.IDLE:
                        time_diff = current_time - session.created_at
                        if time_diff.total_seconds() > 3600:  # 1 hour timeout
                            inactive_streams.append(stream_id)
                            
                # Clean up inactive streams
                for stream_id in inactive_streams:
                    logger.info(f"Cleaning up inactive stream: {stream_id}")
                    await self.stop_stream(stream_id)
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)


@dataclass
class LiveStreamSession:
    """Active live stream session"""
    stream_id: str
    user_id: str
    config: StreamConfig
    rtmp_config: Dict[str, str]
    status: StreamStatus = StreamStatus.IDLE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    total_duration_minutes: int = 0
    metrics: StreamMetrics = field(init=False)
    
    def __post_init__(self):
        self.metrics = StreamMetrics(stream_id=self.stream_id)


# Factory function for easy integration
def create_live_stream_manager(redis_client: Any, db_session: Session) -> LiveStreamManager:
    """Create and return a configured LiveStreamManager instance"""
    return LiveStreamManager(redis_client, db_session)