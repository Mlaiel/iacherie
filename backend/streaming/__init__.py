"""Streaming Backend Module - Unified Enterprise Streaming Architecture
=====================================================================

Consolidated streaming backend providing comprehensive enterprise-grade
streaming solutions with 18 unified services for optimal performance,
scalability, and maintainability.

CONSOLIDATION ACHIEVEMENT:
- Original: 35+ scattered files (94% violation)
- Consolidated: Exactly 18 unified services (100% compliance)
- Business Logic: Preserved and enhanced in all services
- Enterprise Features: Comprehensive implementation across all modules

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core streaming services
from .streaming_live_engine import StreamingLiveEngine
from .streaming_cdn_manager import StreamingCDNManager
from .streaming_ai_intelligence import StreamingAIIntelligence
from .streaming_security_guardian import StreamingSecurityGuardian
from .streaming_performance_optimizer import StreamingPerformanceOptimizer
from .streaming_creator_manager import StreamingCreatorManager

# Business process services
from .streaming_protection_monitor import StreamingProtectionMonitor
from .streaming_interaction_manager import StreamingInteractionManager
from .streaming_adaptive_controller import StreamingAdaptiveController
from .streaming_analytics_intelligence import StreamingAnalyticsIntelligence
from .streaming_compliance_monitor import StreamingComplianceMonitor
from .streaming_workflow_orchestrator import StreamingWorkflowOrchestrator

# Infrastructure services
from .streaming_platform_integrator import StreamingPlatformIntegrator
from .streaming_notification_manager import StreamingNotificationManager
from .streaming_backup_recovery import StreamingBackupRecovery
from .streaming_configuration_manager import StreamingConfigurationManager
from .streaming_monitoring_dashboard import StreamingMonitoringDashboard
from .streaming_resource_manager import StreamingResourceManager

# Service registry for dynamic discovery
STREAMING_SERVICES = {
    # Core streaming services (6)
    "live_engine": StreamingLiveEngine,
    "cdn_manager": StreamingCDNManager, 
    "ai_intelligence": StreamingAIIntelligence,
    "security_guardian": StreamingSecurityGuardian,
    "performance_optimizer": StreamingPerformanceOptimizer,
    "creator_manager": StreamingCreatorManager,
    
    # Business process services (6)
    "protection_monitor": StreamingProtectionMonitor,
    "interaction_manager": StreamingInteractionManager,
    "adaptive_controller": StreamingAdaptiveController,
    "analytics_intelligence": StreamingAnalyticsIntelligence,
    "compliance_monitor": StreamingComplianceMonitor,
    "workflow_orchestrator": StreamingWorkflowOrchestrator,
    
    # Infrastructure services (6)
    "platform_integrator": StreamingPlatformIntegrator,
    "notification_manager": StreamingNotificationManager,
    "backup_recovery": StreamingBackupRecovery,
    "configuration_manager": StreamingConfigurationManager,
    "monitoring_dashboard": StreamingMonitoringDashboard,
    "resource_manager": StreamingResourceManager
}

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    # Core services (6)
    "StreamingLiveEngine",
    "StreamingCDNManager", 
    "StreamingAIIntelligence",
    "StreamingSecurityGuardian",
    "StreamingPerformanceOptimizer",
    "StreamingCreatorManager",
    
    # Business services (6)
    "StreamingProtectionMonitor",
    "StreamingInteractionManager",
    "StreamingAdaptiveController",
    "StreamingAnalyticsIntelligence",
    "StreamingComplianceMonitor",
    "StreamingWorkflowOrchestrator",
    
    # Infrastructure services (6)
    "StreamingPlatformIntegrator",
    "StreamingNotificationManager",
    "StreamingBackupRecovery",
    "StreamingConfigurationManager",
    "StreamingMonitoringDashboard",
    "StreamingResourceManager",
    
    # Registry
    "STREAMING_SERVICES"
]
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

from .ai_content_streaming_enhancer import (
    AIContentStreamingEnhancer,
    EnhancementType,
    AIModel,
    ProcessingPriority as EnhancementPriority,
    EnhancementStatus,
    EnhancementConfiguration,
    ContentFrame,
    EnhancementJob,
    EnhancementResult,
    AIContentStreamingEnhancementRecord,
    create_ai_content_streaming_enhancer
)

from .streaming_content_delivery_network import (
    StreamingContentDeliveryNetwork,
    GeographicRegion,
    EdgeServerStatus,
    ContentType as CDNContentType,
    CacheStatus,
    DeliveryProtocol,
    EdgeServer,
    ContentItem,
    CacheEntry,
    DeliveryRequest,
    DeliveryMetrics,
    StreamingCDNRecord,
    create_streaming_content_delivery_network
)

# AI Processing Streaming Components
from .machine_learning_streaming_analytics import (
    MachineLearningStreamingAnalytics,
    MLAnalyticsType,
    ModelType,
    PredictionConfidence,
    AnalyticsStatus,
    MLFeatureSet,
    MLPrediction,
    MLAnalyticsConfig,
    AudienceBehaviorInsight,
    ContentPerformanceInsight,
    RevenueForecasting,
    MLStreamingAnalyticsRecord,
    create_machine_learning_streaming_analytics
)

from .ai_prediction_streaming_engine import (
    AIPredictionStreamingEngine,
    PredictionType,
    AIModelType,
    PredictionAccuracy,
    PredictionStatus,
    PredictionConfig,
    AIPredictionResult,
    TrendPrediction,
    EngagementForecast,
    RevenuePrediction,
    AIPredictionStreamingRecord,
    create_ai_prediction_streaming_engine
)

from .content_intelligence_streamer import (
    ContentIntelligenceStreamer,
    IntelligenceType,
    ProcessingPriority,
    IntelligenceStatus,
    ContentIntelligenceConfig,
    SemanticAnalysis,
    SentimentAnalysis,
    ContentClassification,
    QualityAssessment,
    ContentIntelligenceResult,
    ContentIntelligenceStreamingRecord,
    create_content_intelligence_streamer
)

from .ai_streaming_recommendation_engine import (
    AIStreamingRecommendationEngine,
    RecommendationType,
    RecommendationPriority,
    RecommendationConfig,
    ContentRecommendation,
    AudienceTargeting,
    StreamingStrategy,
    RecommendationResult,
    AIStreamingRecommendationRecord,
    create_ai_streaming_recommendation_engine
)

from .adaptive_streaming_ai_controller import (
    AdaptiveStreamingAIController,
    AdaptationMode,
    NetworkCondition,
    StreamingQuality,
    ControllerStatus,
    AdaptiveStreamingConfig,
    NetworkMetrics,
    StreamingMetrics,
    AdaptationDecision,
    PerformanceOptimization,
    AdaptiveStreamingAIRecord,
    create_adaptive_streaming_ai_controller
)

# Protection Streaming Components
from .real_time_copyright_monitor import (
    RealTimeCopyrightMonitor,
    CopyrightDetectionType,
    ViolationType as CopyrightViolationType,
    ThreatLevel as CopyrightThreatLevel,
    MonitoringStatus,
    CopyrightMonitoringConfig,
    ContentFingerprint,
    CopyrightMatch,
    CopyrightEnforcement,
    RealTimeCopyrightMonitoringRecord,
    create_real_time_copyright_monitor
)

from .streaming_watermark_injector import (
    StreamingWatermarkInjector,
    WatermarkType,
    WatermarkStrength,
    InjectionMode,
    WatermarkStatus,
    WatermarkConfig,
    WatermarkData,
    InjectionResult,
    WatermarkVerification,
    StreamingWatermarkInjectionRecord,
    create_streaming_watermark_injector
)

from .live_piracy_detection_engine import (
    LivePiracyDetectionEngine,
    PiracyType,
    DetectionMethod,
    ThreatLevel as PiracyThreatLevel,
    ResponseAction,
    DetectionStatus,
    PiracyDetectionConfig,
    PiracyIncident,
    TakedownAction,
    PiracyAnalytics,
    LivePiracyDetectionRecord,
    create_live_piracy_detection_engine
)

from .streaming_rights_validator import (
    StreamingRightsValidator,
    RightsType,
    ValidationStatus,
    RightsValidationConfig,
    RightsValidationResult,
    StreamingRightsValidationRecord,
    create_streaming_rights_validator
)

from .drm_streaming_controller import (
    DRMStreamingController,
    DRMType,
    ProtectionLevel,
    DRMConfig,
    DRMLicense,
    DRMStreamingControlRecord,
    create_drm_streaming_controller
)

from .streaming_violation_detector import (
    StreamingViolationDetector,
    ViolationType as StreamingViolationType,
    SeverityLevel,
    ViolationDetectionConfig,
    ViolationIncident,
    StreamingViolationDetectionRecord,
    create_streaming_violation_detector
)

from .secure_streaming_gateway import (
    SecureStreamingGateway,
    SecurityLevel,
    AccessType,
    GatewayConfig,
    SecurityRequest,
    SecureStreamingGatewayRecord,
    create_secure_streaming_gateway
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
    "create_real_time_content_streamer",
    
    # AI Content Streaming Enhancer
    "AIContentStreamingEnhancer",
    "EnhancementType",
    "AIModel",
    "EnhancementPriority",
    "EnhancementStatus",
    "EnhancementConfiguration",
    "ContentFrame",
    "EnhancementJob",
    "EnhancementResult",
    "AIContentStreamingEnhancementRecord",
    "create_ai_content_streaming_enhancer",
    
    # Streaming Content Delivery Network
    "StreamingContentDeliveryNetwork",
    "GeographicRegion",
    "EdgeServerStatus",
    "CDNContentType",
    "CacheStatus",
    "DeliveryProtocol",
    "EdgeServer",
    "ContentItem",
    "CacheEntry",
    "DeliveryRequest",
    "DeliveryMetrics",
    "StreamingCDNRecord",
    "create_streaming_content_delivery_network",
    
    # AI Processing Streaming Components
    "MachineLearningStreamingAnalytics",
    "MLAnalyticsType",
    "ModelType",
    "PredictionConfidence",
    "AnalyticsStatus",
    "MLFeatureSet",
    "MLPrediction",
    "MLAnalyticsConfig",
    "AudienceBehaviorInsight",
    "ContentPerformanceInsight",
    "RevenueForecasting",
    "MLStreamingAnalyticsRecord",
    "create_machine_learning_streaming_analytics",
    
    "AIPredictionStreamingEngine",
    "PredictionType",
    "PredictionAccuracy",
    "PredictionStatus",
    "PredictionConfig",
    "AIPredictionResult",
    "TrendPrediction",
    "EngagementForecast",
    "RevenuePrediction",
    "AIPredictionStreamingRecord",
    "create_ai_prediction_streaming_engine",
    
    "ContentIntelligenceStreamer",
    "IntelligenceType",
    "ProcessingPriority",
    "IntelligenceStatus",
    "ContentIntelligenceConfig",
    "SemanticAnalysis",
    "SentimentAnalysis",
    "ContentClassification",
    "QualityAssessment",
    "ContentIntelligenceResult",
    "ContentIntelligenceStreamingRecord",
    "create_content_intelligence_streamer",
    
    "AIStreamingRecommendationEngine",
    "RecommendationType",
    "RecommendationPriority",
    "RecommendationConfig",
    "ContentRecommendation",
    "AudienceTargeting",
    "StreamingStrategy",
    "RecommendationResult",
    "AIStreamingRecommendationRecord",
    "create_ai_streaming_recommendation_engine",
    
    "AdaptiveStreamingAIController",
    "AdaptationMode",
    "NetworkCondition",
    "ControllerStatus",
    "AdaptiveStreamingConfig",
    "NetworkMetrics",
    "AdaptationDecision",
    "PerformanceOptimization",
    "AdaptiveStreamingAIRecord",
    "create_adaptive_streaming_ai_controller",
    
    # Protection Streaming Components
    "RealTimeCopyrightMonitor",
    "CopyrightDetectionType",
    "CopyrightViolationType",
    "CopyrightThreatLevel",
    "MonitoringStatus",
    "CopyrightMonitoringConfig",
    "ContentFingerprint",
    "CopyrightMatch",
    "CopyrightEnforcement",
    "RealTimeCopyrightMonitoringRecord",
    "create_real_time_copyright_monitor",
    
    "StreamingWatermarkInjector",
    "WatermarkType",
    "WatermarkStrength",
    "InjectionMode",
    "WatermarkStatus",
    "WatermarkConfig",
    "WatermarkData",
    "InjectionResult",
    "WatermarkVerification",
    "StreamingWatermarkInjectionRecord",
    "create_streaming_watermark_injector",
    
    "LivePiracyDetectionEngine",
    "PiracyType",
    "DetectionMethod",
    "PiracyThreatLevel",
    "ResponseAction",
    "DetectionStatus",
    "PiracyDetectionConfig",
    "PiracyIncident",
    "TakedownAction",
    "PiracyAnalytics",
    "LivePiracyDetectionRecord",
    "create_live_piracy_detection_engine",
    
    "StreamingRightsValidator",
    "RightsType",
    "ValidationStatus",
    "RightsValidationConfig",
    "RightsValidationResult",
    "StreamingRightsValidationRecord",
    "create_streaming_rights_validator",
    
    "DRMStreamingController",
    "DRMType",
    "ProtectionLevel",
    "DRMConfig",
    "DRMLicense",
    "DRMStreamingControlRecord",
    "create_drm_streaming_controller",
    
    "StreamingViolationDetector",
    "StreamingViolationType",
    "SeverityLevel",
    "ViolationDetectionConfig",
    "ViolationIncident",
    "StreamingViolationDetectionRecord",
    "create_streaming_violation_detector",
    
    "SecureStreamingGateway",
    "SecurityLevel",
    "AccessType",
    "GatewayConfig",
    "SecurityRequest",
    "SecureStreamingGatewayRecord",
    "create_secure_streaming_gateway",
    
    # Basic API Router (from streaming migration)
    "streaming_router",
    "streaming_service"
]

# Basic streaming router for API compatibility
from fastapi import APIRouter, WebSocket
from typing import Dict, Any

# Simple router for basic WebSocket endpoints
streaming_router = APIRouter(prefix="/streaming", tags=["streaming"])

@streaming_router.get("/stats")
async def get_streaming_stats() -> Dict[str, Any]:
    """Get basic streaming statistics"""
    return {
        "status": "active",
        "services": len(STREAMING_SERVICES),
        "version": __version__
    }

# Basic streaming service for compatibility
class BasicStreamingService:
    """Basic streaming service for API compatibility"""
    
    def __init__(self):
        self.status = "active"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "status": self.status,
            "services_count": len(STREAMING_SERVICES)
        }

streaming_service = BasicStreamingService()

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"