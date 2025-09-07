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

from .ai_streaming_processor import (
    AIStreamingProcessor,
    AIProcessingType,
    ProcessingPriority,
    AIModel,
    ProcessingStatus,
    AIProcessingConfig,
    ContentEnhancement,
    AIProcessingResult,
    StreamingOptimization,
    create_ai_streaming_processor
)

from .intelligent_streaming_optimizer import (
    IntelligentStreamingOptimizer,
    OptimizationType,
    OptimizationStrategy,
    PerformanceMetric,
    OptimizationMode,
    OptimizationConfig,
    PerformanceProfile,
    OptimizationResult,
    AdaptiveSettings,
    PredictiveInsight,
    create_intelligent_streaming_optimizer
)

from .streaming_content_protection import (
    StreamingContentProtection,
    ProtectionType,
    ViolationType,
    ThreatLevel,
    ProtectionStatus,
    ResponseAction,
    ProtectionConfig,
    ContentFingerprint,
    WatermarkData,
    ViolationIncident,
    ProtectionReport,
    create_streaming_content_protection
)

from .streaming_monetization_engine import (
    StreamingMonetizationEngine,
    RevenueType,
    PaymentMethod,
    CurrencyCode,
    TransactionStatus,
    SubscriptionTier,
    AdType,
    MonetizationConfig,
    RevenueTransaction,
    SubscriptionRecord,
    DonationGoal,
    AdRevenueRecord,
    RevenueAnalytics,
    create_streaming_monetization_engine
)

from .collaborative_streaming_engine import (
    CollaborativeStreamingEngine,
    CollaborationType,
    SynchronizationMode,
    CollaborationStatus,
    RevenueShareModel,
    ParticipantRole,
    CollaborationConfig,
    Participant,
    CollaborationSession,
    RevenueShareCalculation,
    SynchronizationStatus,
    CollaborationAnalytics,
    create_collaborative_streaming_engine
)

from .streaming_gamification_engine import (
    StreamingGamificationEngine,
    EngagementType,
    AchievementType,
    ChallengeType,
    RewardType,
    BadgeRarity,
    LeaderboardType,
    GamificationConfig,
    EngagementEvent,
    Achievement,
    UserAchievement,
    Challenge,
    LeaderboardEntry,
    Leaderboard,
    GamificationAnalytics,
    create_streaming_gamification_engine
)

from .streaming_seo_optimizer import (
    StreamingSEOOptimizer,
    SEOOptimizationType,
    ViralPotential,
    SEOMetric,
    ContentCategory,
    SEOConfig,
    KeywordAnalysis,
    SEOOptimization,
    ViralDetectionResult,
    TrendAnalysis,
    SEOPerformanceReport,
    create_streaming_seo_optimizer
)

from .multi_platform_streaming_distributor import (
    MultiPlatformStreamingDistributor,
    StreamingPlatform,
    DistributionStrategy,
    ContentAdaptationType,
    DistributionStatus,
    GeographicRegion,
    DistributionConfig,
    PlatformConfiguration,
    ContentAdaptation,
    DistributionJob,
    AudienceRoutingResult,
    GlobalDistributionReport,
    create_multi_platform_streaming_distributor
)

from .content_streaming_processor import (
    ContentStreamingProcessor,
    ContentType,
    ProcessingStage,
    QualityLevel,
    ProcessingPriority,
    ContentSpecs,
    ProcessingJob,
    ProcessingResult,
    ContentStreamingProcessingRecord,
    create_content_streaming_processor
)

from .platform_streaming_coordinator import (
    PlatformStreamingCoordinator,
    StreamingPlatform as CoordinatorPlatform,
    CoordinationStatus,
    SynchronizationMode,
    PlatformTier,
    PlatformConfiguration as CoordinatorPlatformConfig,
    CoordinationSession,
    SynchronizationMetrics,
    PlatformStreamingCoordinationRecord,
    create_platform_streaming_coordinator
)

from .streaming_quality_optimizer import (
    StreamingQualityOptimizer,
    QualityLevel as OptimizerQualityLevel,
    OptimizationStrategy,
    NetworkCondition,
    OptimizationMode,
    QualitySettings,
    NetworkMetrics,
    QualityMetrics,
    OptimizationJob,
    StreamingQualityOptimizationRecord,
    create_streaming_quality_optimizer
)

from .real_time_content_streamer import (
    RealTimeContentStreamer,
    StreamingMode,
    ContentDeliveryMethod,
    StreamingStatus,
    AudienceEngagementType,
    StreamingConfiguration,
    ContentChunk,
    AudienceEngagement,
    StreamingMetrics,
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
    
    # AI Streaming Processor
    "AIStreamingProcessor",
    "AIProcessingType",
    "ProcessingPriority",
    "AIModel",
    "ProcessingStatus",
    "AIProcessingConfig",
    "ContentEnhancement",
    "AIProcessingResult",
    "StreamingOptimization",
    "create_ai_streaming_processor",
    
    # Intelligent Streaming Optimizer
    "IntelligentStreamingOptimizer",
    "OptimizationType",
    "OptimizationStrategy",
    "PerformanceMetric",
    "OptimizationMode",
    "OptimizationConfig",
    "PerformanceProfile",
    "OptimizationResult",
    "AdaptiveSettings",
    "create_intelligent_streaming_optimizer",
    
    # Streaming Content Protection
    "StreamingContentProtection",
    "ProtectionType",
    "ViolationType",
    "ThreatLevel",
    "ProtectionStatus",
    "ResponseAction",
    "ProtectionConfig",
    "ContentFingerprint",
    "WatermarkData",
    "ViolationIncident",
    "ProtectionReport",
    "create_streaming_content_protection",
    
    # Streaming Monetization Engine
    "StreamingMonetizationEngine",
    "RevenueType",
    "PaymentMethod",
    "CurrencyCode",
    "TransactionStatus",
    "SubscriptionTier",
    "AdType",
    "MonetizationConfig",
    "RevenueTransaction",
    "DonationGoal",
    "AdRevenueRecord",
    "RevenueAnalytics",
    "create_streaming_monetization_engine",
    
    # Collaborative Streaming Engine
    "CollaborativeStreamingEngine",
    "CollaborationType",
    "SynchronizationMode",
    "CollaborationStatus",
    "RevenueShareModel",
    "ParticipantRole",
    "CollaborationConfig",
    "Participant",
    "CollaborationSession",
    "RevenueShareCalculation",
    "SynchronizationStatus",
    "CollaborationAnalytics",
    "create_collaborative_streaming_engine",
    
    # Streaming Gamification Engine
    "StreamingGamificationEngine",
    "EngagementType",
    "AchievementType",
    "ChallengeType",
    "RewardType",
    "BadgeRarity",
    "LeaderboardType",
    "GamificationConfig",
    "EngagementEvent",
    "Achievement",
    "UserAchievement",
    "Challenge",
    "LeaderboardEntry",
    "Leaderboard",
    "GamificationAnalytics",
    "create_streaming_gamification_engine",
    
    # Streaming SEO Optimizer
    "StreamingSEOOptimizer",
    "SEOOptimizationType",
    "ViralPotential",
    "SEOMetric",
    "ContentCategory",
    "SEOConfig",
    "KeywordAnalysis",
    "SEOOptimization",
    "ViralDetectionResult",
    "TrendAnalysis",
    "SEOPerformanceReport",
    "create_streaming_seo_optimizer",
    
    # Multi-Platform Streaming Distributor
    "MultiPlatformStreamingDistributor",
    "StreamingPlatform",
    "DistributionStrategy",
    "ContentAdaptationType",
    "DistributionStatus",
    "GeographicRegion",
    "DistributionConfig",
    "PlatformConfiguration",
    "ContentAdaptation",
    "DistributionJob",
    "AudienceRoutingResult",
    "GlobalDistributionReport",
    "create_multi_platform_streaming_distributor",
    
    # Content Streaming Processor
    "ContentStreamingProcessor",
    "ContentType",
    "ProcessingStage",
    "QualityLevel",
    "ProcessingPriority",
    "ContentSpecs",
    "ProcessingJob",
    "ProcessingResult",
    "ContentStreamingProcessingRecord",
    "create_content_streaming_processor",
    
    # Platform Streaming Coordinator
    "PlatformStreamingCoordinator",
    "CoordinatorPlatform",
    "CoordinationStatus",
    "SynchronizationMode",
    "PlatformTier",
    "CoordinatorPlatformConfig",
    "CoordinationSession",
    "SynchronizationMetrics",
    "PlatformStreamingCoordinationRecord",
    "create_platform_streaming_coordinator",
    
    # Streaming Quality Optimizer
    "StreamingQualityOptimizer",
    "OptimizerQualityLevel",
    "OptimizationStrategy",
    "NetworkCondition",
    "OptimizationMode",
    "QualitySettings",
    "NetworkMetrics",
    "QualityMetrics",
    "OptimizationJob",
    "StreamingQualityOptimizationRecord",
    "create_streaming_quality_optimizer",
    
    # Real-time Content Streamer
    "RealTimeContentStreamer",
    "StreamingMode",
    "ContentDeliveryMethod",
    "StreamingStatus",
    "AudienceEngagementType",
    "StreamingConfiguration",
    "ContentChunk",
    "AudienceEngagement",
    "StreamingMetrics",
    "RealTimeStreamingRecord",
    "create_real_time_content_streamer"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"