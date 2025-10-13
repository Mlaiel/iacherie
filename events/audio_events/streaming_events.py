"""Audio Streaming Events - Industrial Grade Streaming Event Management
=====================================================================

This module handles all events related to audio streaming, live broadcasting,
and real-time audio distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class StreamingProtocol(Enum):
    HLS = "hls"
    DASH = "dash"
    RTMP = "rtmp"
    WEBRTC = "webrtc"


class StreamQuality(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"


class StreamingPlatform(Enum):
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    CUSTOM = "custom"


@dataclass
class AudioStreamStartedEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    file_id: UUID
    platform: str
    quality: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.started",
            data={
                "stream_id": str(self.stream_id),
                "file_id": str(self.file_id),
                "platform": self.platform,
                "quality": self.quality
            }
        )


@dataclass
class AudioStreamEndedEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    file_id: UUID
    duration: float
    listeners_count: int
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.ended",
            data={
                "stream_id": str(self.stream_id),
                "file_id": str(self.file_id),
                "duration": self.duration,
                "listeners_count": self.listeners_count
            }
        )


@dataclass
class AudioStreamQualityChangedEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    old_quality: str
    new_quality: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.quality_changed",
            data={
                "stream_id": str(self.stream_id),
                "old_quality": self.old_quality,
                "new_quality": self.new_quality
            }
        )


@dataclass
class AudioLiveStreamStartedEvent(BaseEvent):
    user_id: UUID
    live_stream_id: UUID
    title: str
    expected_duration: Optional[float] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.live_started",
            data={
                "live_stream_id": str(self.live_stream_id),
                "title": self.title,
                "expected_duration": self.expected_duration
            }
        )


@dataclass
class AudioLiveStreamEndedEvent(BaseEvent):
    user_id: UUID
    live_stream_id: UUID
    duration: float
    max_concurrent_listeners: int
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.live_ended",
            data={
                "live_stream_id": str(self.live_stream_id),
                "duration": self.duration,
                "max_concurrent_listeners": self.max_concurrent_listeners
            }
        )


@dataclass
class AudioStreamListenerJoinedEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    listener_id: UUID
    listener_location: Optional[str] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.listener_joined",
            data={
                "stream_id": str(self.stream_id),
                "listener_id": str(self.listener_id),
                "listener_location": self.listener_location
            }
        )


@dataclass
class AudioStreamListenerLeftEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    listener_id: UUID
    listen_duration: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.listener_left",
            data={
                "stream_id": str(self.stream_id),
                "listener_id": str(self.listener_id),
                "listen_duration": self.listen_duration
            }
        )


@dataclass
class AudioStreamBufferingEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    buffer_duration: float
    network_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.buffering",
            data={
                "stream_id": str(self.stream_id),
                "buffer_duration": self.buffer_duration
            }
        )


@dataclass
class AudioStreamAnalyticsEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.analytics",
            data={
                "stream_id": str(self.stream_id),
                "analytics_keys": list(self.analytics_data.keys())
            }
        )


@dataclass
class AudioStreamErrorEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    error_code: str
    error_message: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.error",
            data={
                "stream_id": str(self.stream_id),
                "error_code": self.error_code,
                "error_message": self.error_message
            }
        )


@dataclass
class AudioStreamQualityAdaptationEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    adaptation_reason: str
    new_bitrate: int
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.quality_adaptation",
            data={
                "stream_id": str(self.stream_id),
                "adaptation_reason": self.adaptation_reason,
                "new_bitrate": self.new_bitrate
            }
        )


@dataclass
class AudioMulticastEvent(BaseEvent):
    user_id: UUID
    multicast_id: UUID
    target_platforms: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.multicast",
            data={
                "multicast_id": str(self.multicast_id),
                "platforms_count": len(self.target_platforms)
            }
        )


@dataclass
class AudioLatencyOptimizationEvent(BaseEvent):
    user_id: UUID
    stream_id: UUID
    original_latency: float
    optimized_latency: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.streaming.latency_optimization",
            data={
                "stream_id": str(self.stream_id),
                "original_latency": self.original_latency,
                "optimized_latency": self.optimized_latency,
                "improvement": self.original_latency - self.optimized_latency
            }
        )