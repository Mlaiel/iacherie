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

from .creator_streaming_orchestrator import (
    CreatorStreamingOrchestrator,
    CreatorType,
    ContentType,
    StreamingStatus,
    PlatformType,
    StreamingConfig,
    StreamingMetrics,
    StreamingAnalytics,
    CreatorStreamingSession,
    create_creator_streaming_orchestrator
)

from .multi_format_streaming_engine import (
    MultiFormatStreamingEngine,
    ContentFormat,
    StreamingQuality,
    ProcessingStatus,
    ContentSpecs,
    StreamingProfile,
    ProcessingJob,
    ProcessingResult,
    StreamingContent,
    create_multi_format_streaming_engine
)

from .creator_type_streaming_manager import (
    CreatorTypeStreamingManager,
    SpecializationLevel,
    AudienceSegment,
    CreatorProfile,
    StreamingStrategy,
    PlatformOptimization,
    PerformanceMetrics,
    CreatorStreamingProfile,
    create_creator_type_streaming_manager
)

from .streaming_analytics_engine import (
    StreamingAnalyticsEngine,
    MetricType,
    AnalyticsTimeframe,
    InsightPriority,
    MetricPoint,
    AnalyticsReport,
    RealTimeMetrics,
    AudienceInsights,
    PredictiveInsight,
    StreamingAnalyticsRecord,
    create_streaming_analytics_engine
)

from .content_streaming_processor import (
    ContentStreamingProcessor,
    ProcessingType,
    ContentFormat,
    ProcessingStatus,
    QualityLevel,
    ContentSpec,
    ProcessingJob,
    ProcessingResult,
    ContentStreamingProcessingRecord,
    create_content_streaming_processor
)

from .platform_streaming_coordinator import (
    PlatformStreamingCoordinator,
    PlatformType,
    StreamingMode,
    SyncStatus,
    PlatformStatus,
    PlatformConfig,
    StreamingSession,
    PlatformMetrics,
    CoordinationResult,
    PlatformStreamingRecord,
    create_platform_streaming_coordinator
)

from .streaming_quality_optimizer import (
    StreamingQualityOptimizer,
    QualityLevel,
    OptimizationType,
    MetricType,
    OptimizationStrategy,
    QualitySettings,
    QualityMetrics,
    OptimizationResult,
    AdaptiveProfile,
    StreamingQualityRecord,
    create_streaming_quality_optimizer
)

from .real_time_content_streamer import (
    RealTimeContentStreamer,
    StreamingProtocol,
    ContentType,
    StreamingState,
    LatencyMode,
    InteractionType,
    StreamingEndpoint,
    RealTimeMetrics,
    StreamingConfig,
    StreamChunk,
    InteractionEvent,
    RealTimeStreamingRecord,
    create_real_time_content_streamer
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
    "create_donation_handler",
    
    # Creator Streaming Orchestrator
    "CreatorStreamingOrchestrator",
    "CreatorType",
    "ContentType",
    "StreamingStatus",
    "StreamingConfig",
    "StreamingMetrics",
    "StreamingAnalytics",
    "CreatorStreamingSession",
    "create_creator_streaming_orchestrator",
    
    # Multi-Format Streaming Engine
    "MultiFormatStreamingEngine",
    "ContentFormat",
    "StreamingQuality",
    "ProcessingStatus",
    "ContentSpecs",
    "StreamingProfile",
    "ProcessingJob",
    "ProcessingResult",
    "StreamingContent",
    "create_multi_format_streaming_engine",
    
    # Creator Type Streaming Manager
    "CreatorTypeStreamingManager",
    "SpecializationLevel",
    "AudienceSegment",
    "CreatorProfile",
    "StreamingStrategy",
    "PlatformOptimization",
    "PerformanceMetrics",
    "CreatorStreamingProfile",
    "create_creator_type_streaming_manager",
    
    # Streaming Analytics Engine
    "StreamingAnalyticsEngine",
    "MetricType",
    "AnalyticsTimeframe",
    "InsightPriority",
    "MetricPoint",
    "AnalyticsReport",
    "RealTimeMetrics",
    "AudienceInsights",
    "PredictiveInsight",
    "StreamingAnalyticsRecord",
    "create_streaming_analytics_engine",
    
    # Content Streaming Processor
    "ContentStreamingProcessor",
    "ProcessingType",
    "ContentFormat",
    "ProcessingStatus",
    "QualityLevel",
    "ContentSpec",
    "ProcessingJob",
    "ProcessingResult",
    "ContentStreamingProcessingRecord",
    "create_content_streaming_processor",
    
    # Platform Streaming Coordinator
    "PlatformStreamingCoordinator",
    "PlatformType",
    "StreamingMode",
    "SyncStatus",
    "PlatformStatus",
    "PlatformConfig",
    "StreamingSession",
    "PlatformMetrics",
    "CoordinationResult",
    "PlatformStreamingRecord",
    "create_platform_streaming_coordinator",
    
    # Streaming Quality Optimizer
    "StreamingQualityOptimizer",
    "QualityLevel",
    "OptimizationType",
    "OptimizationStrategy",
    "QualitySettings",
    "QualityMetrics",
    "OptimizationResult",
    "AdaptiveProfile",
    "StreamingQualityRecord",
    "create_streaming_quality_optimizer",
    
    # Real-time Content Streamer
    "RealTimeContentStreamer",
    "StreamingProtocol",
    "ContentType",
    "StreamingState",
    "LatencyMode",
    "InteractionType",
    "StreamingEndpoint",
    "StreamChunk",
    "InteractionEvent",
    "RealTimeStreamingRecord",
    "create_real_time_content_streamer"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"