"""Multi-Platform Distribution Module

Advanced multi-platform content distribution system for the Ainflue platform.
Handles automated publication scheduling, format adaptation, analytics aggregation,
hashtag optimization, and A/B testing across all major social platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel (mlaiel@live.de)
- Distribution Systems Architect: Fahed Mlaiel (mlaiel@live.de)
- Platform Integration Specialist: Fahed Mlaiel (mlaiel@live.de)
- Social Media API Expert: Fahed Mlaiel (mlaiel@live.de)
- Content Optimization Analyst: Fahed Mlaiel (mlaiel@live.de)
"""

from .platform_connectors import (
    PlatformConnectorManager,
    SocialPlatform,
    ContentFormat,
    PublicationResult
)
from .publication_scheduler import (
    PublicationScheduler,
    ScheduledPublication,
    ScheduleStrategy,
    PublicationStatus
)
from .format_adapter import (
    FormatAdapter,
    PlatformSpecifications,
    AdaptationRule,
    ContentVariant
)
from .analytics_aggregator import (
    AnalyticsAggregator,
    UnifiedMetrics,
    PlatformAnalytics,
    CrossPlatformInsights
)
from .hashtag_optimizer import (
    HashtagOptimizer,
    HashtagStrategy,
    TrendingHashtags,
    OptimizedTags
)
from .ab_testing_engine import (
    ABTestingEngine,
    TestVariant,
    TestResult,
    PerformanceMetrics
)
from .distribution_intelligence import (
    DistributionIntelligence,
    OptimizationStrategy,
    PlatformPriority,
    AudienceInsight,
    PlatformPerformance,
    DistributionRecommendation,
    EngagementPrediction
)
from .revenue_distribution import (
    RevenueDistribution,
    RevenueType,
    PaymentStatus,
    Currency,
    RevenueStream,
    PlatformRevenue,
    ROIAnalysis,
    BudgetOptimization,
    RevenueAttribution
)
from .content_security import (
    ContentSecurity,
    SecurityLevel,
    WatermarkType,
    ViolationType,
    GeographicRegion,
    ContentFingerprint,
    WatermarkConfig,
    SecurityViolation,
    ProtectionPolicy,
    MonitoringAlert
)
from .automation_orchestrator import (
    AutomationOrchestrator,
    WorkflowStatus,
    StepStatus,
    ExecutionStrategy,
    ErrorHandlingStrategy,
    WorkflowStep,
    StepExecution,
    WorkflowDefinition,
    WorkflowExecution,
    DistributionPipeline
)
from .cross_platform_sync import (
    CrossPlatformSync,
    SyncStatus,
    ConflictResolutionStrategy,
    SyncDirection,
    ChangeType,
    ContentVersion,
    SyncConflict,
    SyncRule,
    SyncSession,
    PlatformState
)

# New Platform Connectors
from .clubhouse_connector import (
    ClubhouseConnector,
    ClubhouseDistributionManager,
    ClubhouseRoom,
    ClubhouseMetrics,
    ClubhouseCredentials
)
from .telegram_connector import (
    TelegramConnector,
    TelegramDistributionManager,
    TelegramMessage,
    TelegramChannel,
    TelegramMetrics,
    TelegramCredentials
)

# Enhanced Scheduling
from .event_based_scheduler import (
    EventBasedScheduler,
    EventTrigger,
    EventData,
    ScheduledTask,
    EventType,
    EventPriority,
    SchedulingAction
)

# Advanced Distribution Modules (Level 2)
from .viral_optimization import (
    ViralPredictor,
    TrendAnalyzer,
    MomentumTracker,
    InfluenceMapper,
    CascadeOptimizer,
    TimingOracle,
    ViralityAmplifier,
    NetworkDynamics
)
# Advanced Distribution Modules (Level 2) - Temporarily commented out problematic imports
# from .audience_intelligence import (
#     AudienceIntelligenceEngine,
#     AudienceProfiler,
#     BehaviorAnalyzer,
#     PreferenceEngine,
#     DemographicMapper,
#     PsychographicAnalyzer,
#     EngagementPredictor,
#     LookalikeFinder,
#     SegmentOptimizer
# )
# from .content_amplification import (
#     ContentAmplificationEngine,
#     AmplificationEngine,
#     BoostOptimizer,
#     OrganicReachMaximizer,
#     CrossPromotionManager,
#     InfluencerConnector,
#     CommunityBuilder,
#     EngagementMultiplier,
#     ReachAnalytics
# )
# from .platform_optimization import (
#     PlatformOptimizationEngine,
#     PlatformAnalyzer,
#     AlgorithmTracker,
#     FeatureOptimizer,
#     PolicyMonitor,
#     TrendingTracker,
#     CreatorFundOptimizer,
#     MonetizationMaximizer,
#     CompetitionAnalyzer
# )
# from .geographic_optimization import (
#     GeographicOptimizationEngine,
#     GeoTargetingEngine,
#     CulturalAdapter,
#     TimezoneOptimizer,
#     LocalizationManager,
#     RegionalTrendsAnalyzer,
#     LanguageOptimizer,
#     ComplianceChecker,
#     MarketPenetrationAnalyzer
# )
# from .real_time_optimization import (
#     RealTimeOptimizationEngine,
#     LivePerformanceMonitor,
#     AdaptiveOptimizer,
#     EmergencyResponse,
#     TrendSurfingEngine,
#     MomentumCapitalizer,
#     RealTimeABTester,
#     InstantFeedbackProcessor,
#     DynamicContentOptimizer
# )
# from .creator_collaboration_hub import (
#     CreatorCollaborationEngine,
#     CollaborationOrchestrator,
#     CrossCreatorAmplifier,
#     CollaborationMatcher,
#     JointCampaignManager,
#     CreatorNetworkBuilder,
#     CollaborationAnalytics,
#     PartnershipOptimizer,
#     RevenueSharingCalculator
# )
# from .crisis_management import (
#     CrisisManagementEngine,
#     CrisisDetector,
#     DamageControlEngine,
#     ReputationProtector,
#     EmergencyCommunication,
#     SentimentMonitor,
#     RecoveryPlanner,
#     BrandSafetyGuardian,
#     CrisisAnalytics
# )

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Platform Connectors
    "PlatformConnectorManager",
    "SocialPlatform", 
    "ContentFormat",
    "PublicationResult",
    # New Platform Connectors
    "ClubhouseConnector",
    "ClubhouseDistributionManager", 
    "ClubhouseRoom",
    "ClubhouseMetrics",
    "ClubhouseCredentials",
    "TelegramConnector",
    "TelegramDistributionManager",
    "TelegramMessage",
    "TelegramChannel",
    "TelegramMetrics",
    "TelegramCredentials",
    # Publication Scheduler
    "PublicationScheduler",
    "ScheduledPublication",
    "ScheduleStrategy", 
    "PublicationStatus",
    # Enhanced Scheduling
    "EventBasedScheduler",
    "EventTrigger",
    "EventData",
    "ScheduledTask",
    "EventType",
    "EventPriority",
    "SchedulingAction",
    # Format Adapter
    "FormatAdapter",
    "PlatformSpecifications",
    "AdaptationRule",
    "ContentVariant",
    # Analytics Aggregator
    "AnalyticsAggregator",
    "UnifiedMetrics",
    "PlatformAnalytics",
    "CrossPlatformInsights",
    # Hashtag Optimizer
    "HashtagOptimizer",
    "HashtagStrategy",
    "TrendingHashtags",
    "OptimizedTags",
    # A/B Testing Engine
    "ABTestingEngine",
    "TestVariant",
    "TestResult",
    "PerformanceMetrics",
    # Distribution Intelligence
    "DistributionIntelligence",
    "OptimizationStrategy",
    "PlatformPriority",
    "AudienceInsight",
    "PlatformPerformance",
    "DistributionRecommendation",
    "EngagementPrediction",
    # Revenue Distribution
    "RevenueDistribution",
    "RevenueType",
    "PaymentStatus",
    "Currency",
    "RevenueStream",
    "PlatformRevenue",
    "ROIAnalysis",
    "BudgetOptimization",
    "RevenueAttribution",
    # Content Security
    "ContentSecurity",
    "SecurityLevel",
    "WatermarkType",
    "ViolationType",
    "GeographicRegion",
    "ContentFingerprint",
    "WatermarkConfig",
    "SecurityViolation",
    "ProtectionPolicy",
    "MonitoringAlert",
    # Automation Orchestrator
    "AutomationOrchestrator",
    "WorkflowStatus",
    "StepStatus",
    "ExecutionStrategy",
    "ErrorHandlingStrategy",
    "WorkflowStep",
    "StepExecution",
    "WorkflowDefinition",
    "WorkflowExecution",
    "DistributionPipeline",
    # Cross Platform Sync
    "CrossPlatformSync",
    "SyncStatus",
    "ConflictResolutionStrategy",
    "SyncDirection",
    "ChangeType",
    "ContentVersion",
    "SyncConflict",
    "SyncRule",
    "SyncSession",
    "PlatformState",
    # Advanced Distribution Modules (Level 2)
    # Viral Optimization
    "ViralOptimizationEngine",
    "ViralPredictor",
    "TrendAnalyzer",
    "MomentumTracker",
    "InfluenceMapper",
    "CascadeOptimizer",
    "TimingOracle",
    "ViralityAmplifier",
    "NetworkDynamics",
    # Audience Intelligence
    "AudienceIntelligenceEngine",
    "AudienceProfiler",
    "BehaviorAnalyzer",
    "PreferenceEngine",
    "DemographicMapper",
    "PsychographicAnalyzer",
    "EngagementPredictor",
    "LookalikeFinder",
    "SegmentOptimizer",
    # Content Amplification
    "ContentAmplificationEngine",
    "AmplificationEngine",
    "BoostOptimizer",
    "OrganicReachMaximizer",
    "CrossPromotionManager",
    "InfluencerConnector",
    "CommunityBuilder",
    "EngagementMultiplier",
    "ReachAnalytics",
    # Platform Optimization
    "PlatformOptimizationEngine",
    "PlatformAnalyzer",
    "AlgorithmTracker",
    "FeatureOptimizer",
    "PolicyMonitor",
    "TrendingTracker",
    "CreatorFundOptimizer",
    "MonetizationMaximizer",
    "CompetitionAnalyzer",
    # Geographic Optimization
    "GeographicOptimizationEngine",
    "GeoTargetingEngine",
    "CulturalAdapter",
    "TimezoneOptimizer",
    "LocalizationManager",
    "RegionalTrendsAnalyzer",
    "LanguageOptimizer",
    "ComplianceChecker",
    "MarketPenetrationAnalyzer",
    # Real-Time Optimization
    "RealTimeOptimizationEngine",
    "LivePerformanceMonitor",
    "AdaptiveOptimizer",
    "EmergencyResponse",
    "TrendSurfingEngine",
    "MomentumCapitalizer",
    "RealTimeABTester",
    "InstantFeedbackProcessor",
    "DynamicContentOptimizer",
    # Creator Collaboration Hub
    "CreatorCollaborationEngine",
    "CollaborationOrchestrator",
    "CrossCreatorAmplifier",
    "CollaborationMatcher",
    "JointCampaignManager",
    "CreatorNetworkBuilder",
    "CollaborationAnalytics",
    "PartnershipOptimizer",
    "RevenueSharingCalculator",
    # Crisis Management
    "CrisisManagementEngine",
    "CrisisDetector",
    "DamageControlEngine",
    "ReputationProtector",
    "EmergencyCommunication",
    "SentimentMonitor",
    "RecoveryPlanner",
    "BrandSafetyGuardian",
    "CrisisAnalytics"
]