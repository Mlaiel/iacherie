"""Streaming Module
================

Advanced live streaming functionality for the Ainflue platform including
live stream management, virtual streamers, chat moderation, and donation handling.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

Available modules:
- live_stream: Core live streaming management and RTMP handling
- virtual_streamer: AI-powered virtual streamers and avatars
- chat_moderator: Advanced chat moderation with AI-powered filtering
- donation_handler: Real-time donation processing and goal tracking
"""

from .live_stream import (
    LiveStreamManager,
    LiveStream,
    StreamStatus,
    StreamQuality,
    PlatformType,
    StreamConfig,
    StreamMetrics,
    LiveStreamSession,
    create_live_stream_manager
)

from .virtual_streamer import (
    VirtualStreamerEngine,
    VirtualStreamer,
    AvatarType,
    PersonalityType,
    InteractionMode,
    VirtualStreamerStatus,
    AvatarConfig,
    PersonalityConfig,
    StreamingSchedule,
    InteractionStats,
    VirtualStreamerSession,
    create_virtual_streamer_engine
)

from .chat_moderator import (
    ChatModerator,
    ChatModeration,
    UserModerationRecord,
    ModerationAction,
    ViolationType,
    SeverityLevel,
    UserRole,
    ModerationRule,
    ModerationConfig,
    ChatMessage,
    UserModerationHistory,
    create_chat_moderator
)

from .donation_handler import (
    DonationHandler,
    Donation,
    DonationGoalRecord,
    DonationStatus,
    PaymentMethod,
    DonationType,
    CurrencyCode,
    AlertType,
    DonationGoal,
    DonationAlert,
    DonationConfig,
    DonationMetrics,
    create_donation_handler
)

__all__ = [
    # Live Stream
    "LiveStreamManager",
    "LiveStream",
    "StreamStatus",
    "StreamQuality", 
    "PlatformType",
    "StreamConfig",
    "StreamMetrics",
    "LiveStreamSession",
    "create_live_stream_manager",
    
    # Virtual Streamer
    "VirtualStreamerEngine",
    "VirtualStreamer",
    "AvatarType",
    "PersonalityType",
    "InteractionMode", 
    "VirtualStreamerStatus",
    "AvatarConfig",
    "PersonalityConfig",
    "StreamingSchedule",
    "InteractionStats",
    "VirtualStreamerSession",
    "create_virtual_streamer_engine",
    
    # Chat Moderator
    "ChatModerator",
    "ChatModeration",
    "UserModerationRecord",
    "ModerationAction",
    "ViolationType",
    "SeverityLevel",
    "UserRole",
    "ModerationRule",
    "ModerationConfig",
    "ChatMessage",
    "UserModerationHistory",
    "create_chat_moderator",
    
    # Donation Handler
    "DonationHandler",
    "Donation",
    "DonationGoalRecord",
    "DonationStatus",
    "PaymentMethod",
    "DonationType",
    "CurrencyCode",
    "AlertType",
    "DonationGoal",
    "DonationAlert",
    "DonationConfig", 
    "DonationMetrics",
    "create_donation_handler"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"