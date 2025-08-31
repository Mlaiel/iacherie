"""Audio Streaming Events - Industrial Grade Real-time Streaming & Broadcasting
===========================================================================

This module handles all events related to audio streaming, live broadcasting,
real-time audio processing, and streaming analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class StreamingProtocol(Enum):
    """Streaming protocols supported"""
    RTMP = "rtmp"
    HLS = "hls"
    DASH = "dash"
    WEBRTC = "webrtc"
    ICECAST = "icecast"
    SRT = "srt"
    HTTP_STREAMING = "http_streaming"
    UDP_STREAMING = "udp_streaming"


class StreamQuality(Enum):
    """Audio streaming quality levels"""
    LOW = "low"          # 64 kbps
    MEDIUM = "medium"    # 128 kbps
    HIGH = "high"        # 256 kbps
    LOSSLESS = "lossless"  # 1411 kbps
    ULTRA = "ultra"      # > 1411 kbps


class StreamingPlatform(Enum):
    """Supported streaming platforms"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    MIXCLOUD = "mixcloud"
    BANDCAMP = "bandcamp"
    CUSTOM = "custom"


@dataclass
class AudioStreamStartedEvent(BaseEvent):
    """
    Event triggered when an audio stream is initiated.
    
    Handles real-time streaming setup and configuration.
    """
    user_id: UUID
    file_id: UUID
    stream_id: UUID
    stream_title: str
    streaming_protocol: StreamingProtocol
    stream_quality: StreamQuality
    bitrate: int
    sample_rate: int
    channels: int
    codec: str
    stream_url: str
    estimated_duration: Optional[float] = None
    buffer_size: int = 8192
    latency_target: float = 2.0  # seconds
    adaptive_bitrate: bool = True
    encryption_enabled: bool = True
    geoblocking_enabled: bool = False
    allowed_regions: List[str] = field(default_factory=list)
    max_concurrent_listeners: int = 1000
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.started",
            event_category=EventCategory.STREAMING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "stream_id": str(self.stream_id),
                "protocol": self.streaming_protocol.value,
                "quality": self.stream_quality.value,
                "bitrate": self.bitrate,
                "latency_target": self.latency_target,
                "max_listeners": self.max_concurrent_listeners
            }
        )


@dataclass
class AudioStreamEndedEvent(BaseEvent):
    """
    Event triggered when an audio stream ends.
    
    Contains comprehensive streaming session metrics and analytics.
    """
    user_id: UUID
    file_id: UUID
    stream_id: UUID
    stream_duration: float
    total_listeners: int
    peak_concurrent_listeners: int
    average_concurrent_listeners: float
    total_data_transmitted: int  # bytes
    average_bitrate: float
    buffer_health: Dict[str, float]
    connection_quality_metrics: Dict[str, float]
    geographic_distribution: Dict[str, int]  # country -> listener_count
    device_distribution: Dict[str, int]  # device_type -> count
    engagement_metrics: Dict[str, float]
    stream_interruptions: int
    reconnection_count: int
    error_rate: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.ended",
            event_category=EventCategory.STREAMING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "stream_id": str(self.stream_id),
                "duration": self.stream_duration,
                "total_listeners": self.total_listeners,
                "peak_listeners": self.peak_concurrent_listeners,
                "data_transmitted_mb": self.total_data_transmitted / (1024 * 1024),
                "error_rate": self.error_rate
            }
        )


@dataclass
class AudioStreamQualityChangedEvent(BaseEvent):
    """
    Event triggered when streaming quality is dynamically adjusted.
    
    Handles adaptive bitrate streaming and quality optimization.
    """
    user_id: UUID
    stream_id: UUID
    previous_quality: StreamQuality
    new_quality: StreamQuality
    previous_bitrate: int
    new_bitrate: int
    quality_change_reason: str  # bandwidth_limitation, user_preference, system_optimization
    network_conditions: Dict[str, float]
    buffer_status: Dict[str, float]
    quality_change_timestamp: datetime
    affected_listeners: int
    automatic_adjustment: bool = True
    user_notification_sent: bool = False
    quality_stability_score: float = 1.0
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.quality_changed",
            event_category=EventCategory.STREAMING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "stream_id": str(self.stream_id),
                "quality_change": f"{self.previous_quality.value}->{self.new_quality.value}",
                "bitrate_change": f"{self.previous_bitrate}->{self.new_bitrate}",
                "change_reason": self.quality_change_reason,
                "affected_listeners": self.affected_listeners,
                "automatic": self.automatic_adjustment
            }
        )


@dataclass
class AudioLiveStreamStartedEvent(BaseEvent):
    """
    Event triggered when a live audio broadcast begins.
    
    Handles live streaming events, concerts, and real-time broadcasts.
    """
    user_id: UUID
    live_stream_id: UUID
    event_title: str
    event_description: str
    streaming_platforms: List[StreamingPlatform]
    stream_urls: Dict[str, str]  # platform -> url
    scheduled_start_time: datetime
    actual_start_time: datetime
    estimated_duration: Optional[float] = None
    stream_category: str = "music"
    is_monetized: bool = False
    ticket_required: bool = False
    age_restriction: Optional[int] = None
    content_warnings: List[str] = field(default_factory=list)
    recording_enabled: bool = True
    chat_enabled: bool = True
    donations_enabled: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.live_started",
            event_category=EventCategory.LIVE_STREAMING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "live_stream_id": str(self.live_stream_id),
                "platforms_count": len(self.streaming_platforms),
                "start_delay": (self.actual_start_time - self.scheduled_start_time).total_seconds(),
                "monetized": self.is_monetized,
                "recording": self.recording_enabled,
                "donations": self.donations_enabled
            }
        )


@dataclass
class AudioLiveStreamEndedEvent(BaseEvent):
    """
    Event triggered when a live audio broadcast ends.
    
    Contains comprehensive live streaming analytics and performance metrics.
    """
    user_id: UUID
    live_stream_id: UUID
    actual_duration: float
    total_unique_viewers: int
    peak_concurrent_viewers: int
    average_concurrent_viewers: float
    viewer_retention_rate: float
    chat_messages_count: int
    donations_received: float = 0.0
    subscription_conversions: int = 0
    follow_conversions: int = 0
    replay_views: int = 0
    platform_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    technical_issues: List[str] = field(default_factory=list)
    audience_engagement_score: float = 0.0
    content_quality_score: float = 0.0
    recording_saved: bool = False
    recording_file_id: Optional[UUID] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.live_ended",
            event_category=EventCategory.LIVE_STREAMING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "live_stream_id": str(self.live_stream_id),
                "duration": self.actual_duration,
                "total_viewers": self.total_unique_viewers,
                "peak_viewers": self.peak_concurrent_viewers,
                "retention_rate": self.viewer_retention_rate,
                "engagement_score": self.audience_engagement_score,
                "donations": self.donations_received
            }
        )


@dataclass
class AudioStreamListenerJoinedEvent(BaseEvent):
    """
    Event triggered when a listener joins an audio stream.
    
    Tracks audience engagement and listener behavior.
    """
    stream_id: UUID
    listener_id: UUID
    listener_session_id: UUID
    join_timestamp: datetime
    listener_location: str
    device_type: str
    app_version: str
    connection_quality: float
    listener_tier: str  # free, premium, vip
    referral_source: str
    is_returning_listener: bool = False
    previous_sessions_count: int = 0
    estimated_session_duration: Optional[float] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.listener_joined",
            event_category=EventCategory.AUDIENCE,
            priority=EventPriority.LOW,
            metadata={
                "stream_id": str(self.stream_id),
                "listener_id": str(self.listener_id),
                "session_id": str(self.listener_session_id),
                "location": self.listener_location,
                "device": self.device_type,
                "tier": self.listener_tier,
                "returning": self.is_returning_listener
            }
        )


@dataclass
class AudioStreamListenerLeftEvent(BaseEvent):
    """
    Event triggered when a listener leaves an audio stream.
    
    Captures listener session analytics and departure reasons.
    """
    stream_id: UUID
    listener_id: UUID
    listener_session_id: UUID
    leave_timestamp: datetime
    session_duration: float
    data_consumed: int  # bytes
    buffer_health_average: float
    connection_stability: float
    leave_reason: str  # user_choice, connection_issue, stream_ended, error
    engagement_score: float
    skip_count: int = 0
    replay_count: int = 0
    interaction_count: int = 0
    feedback_provided: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.listener_left",
            event_category=EventCategory.AUDIENCE,
            priority=EventPriority.LOW,
            metadata={
                "stream_id": str(self.stream_id),
                "listener_id": str(self.listener_id),
                "session_id": str(self.listener_session_id),
                "duration": self.session_duration,
                "leave_reason": self.leave_reason,
                "engagement_score": self.engagement_score,
                "data_consumed_mb": self.data_consumed / (1024 * 1024)
            }
        )


@dataclass
class AudioStreamBufferingEvent(BaseEvent):
    """
    Event triggered when stream buffering occurs.
    
    Monitors streaming performance and connection quality.
    """
    stream_id: UUID
    listener_id: Optional[UUID] = None
    buffering_start_time: datetime
    buffering_duration: float
    buffer_level_before: float
    buffer_level_after: float
    network_bandwidth: float
    connection_type: str
    buffering_cause: str  # low_bandwidth, high_latency, server_overload, codec_issue
    recovery_action: str
    quality_adjusted: bool = False
    user_experience_impact: float = 0.0
    automatic_recovery: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.buffering",
            event_category=EventCategory.PERFORMANCE,
            priority=EventPriority.MEDIUM,
            metadata={
                "stream_id": str(self.stream_id),
                "listener_id": str(self.listener_id) if self.listener_id else None,
                "duration": self.buffering_duration,
                "cause": self.buffering_cause,
                "bandwidth": self.network_bandwidth,
                "quality_adjusted": self.quality_adjusted,
                "ux_impact": self.user_experience_impact
            }
        )


@dataclass
class AudioStreamAnalyticsEvent(BaseEvent):
    """
    Event triggered for periodic streaming analytics updates.
    
    Provides comprehensive streaming performance insights.
    """
    user_id: UUID
    stream_id: UUID
    analytics_period_start: datetime
    analytics_period_end: datetime
    total_listening_time: float
    unique_listeners: int
    repeat_listeners: int
    listener_engagement_metrics: Dict[str, float]
    geographic_reach: Dict[str, int]
    device_distribution: Dict[str, int]
    quality_distribution: Dict[str, float]
    revenue_generated: float = 0.0
    performance_metrics: Dict[str, float]
    content_performance_score: float = 0.0
    audience_growth_rate: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.analytics",
            event_category=EventCategory.ANALYTICS,
            priority=EventPriority.LOW,
            user_id=self.user_id,
            metadata={
                "stream_id": str(self.stream_id),
                "listening_time_hours": self.total_listening_time / 3600,
                "unique_listeners": self.unique_listeners,
                "repeat_listeners": self.repeat_listeners,
                "revenue": self.revenue_generated,
                "performance_score": self.content_performance_score,
                "growth_rate": self.audience_growth_rate
            }
        )


@dataclass
class AudioStreamErrorEvent(BaseEvent):
    """
    Event triggered when streaming errors occur.
    
    Handles error tracking and recovery procedures.
    """
    stream_id: UUID
    error_id: UUID
    error_type: str  # connection, encoding, decoding, network, server
    error_code: str
    error_message: str
    error_timestamp: datetime
    affected_listeners: int
    error_duration: float
    recovery_action_taken: str
    error_severity: str  # low, medium, high, critical
    root_cause: Optional[str] = None
    system_logs: List[str] = field(default_factory=list)
    user_impact_assessment: Dict[str, Any] = field(default_factory=dict)
    resolution_status: str = "investigating"
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.error",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH if self.error_severity in ["high", "critical"] else EventPriority.MEDIUM,
            metadata={
                "stream_id": str(self.stream_id),
                "error_id": str(self.error_id),
                "error_type": self.error_type,
                "error_code": self.error_code,
                "affected_listeners": self.affected_listeners,
                "severity": self.error_severity,
                "resolution_status": self.resolution_status
            }
        )
