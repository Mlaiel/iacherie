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
    DistributionStrategy,
    EngagementPrediction,
    PlatformPriority,
    ContentType,
    AudienceSegment
)
from .content_security import (
    ContentSecurity,
    SecurityConfiguration,
    WatermarkInfo,
    ContentFingerprint,
    SecurityViolation,
    SecurityLevel,
    WatermarkType,
    ProtectionMethod
)
from .automation_orchestrator import (
    AutomationOrchestrator,
    DistributionWorkflow,
    WorkflowStep,
    WorkflowStatus,
    ExecutionReport,
    WorkflowTemplate,
    StepType,
    Priority
)
from .revenue_distribution import (
    RevenueDistribution,
    RevenueStream,
    RevenueRecord,
    PlatformMetrics,
    ROIAnalysis,
    BudgetAllocation,
    ConsolidatedReport,
    RevenueType,
    Currency
)
from .cross_platform_sync import (
    CrossPlatformSync,
    PlatformContent,
    SyncRule,
    SyncSession,
    SyncConflict,
    SyncStatus,
    ConflictType,
    ConflictResolution
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Existing modules
    "PlatformConnectorManager",
    "SocialPlatform", 
    "ContentFormat",
    "PublicationResult",
    "PublicationScheduler",
    "ScheduledPublication",
    "ScheduleStrategy", 
    "PublicationStatus",
    "FormatAdapter",
    "PlatformSpecifications",
    "AdaptationRule",
    "ContentVariant",
    "AnalyticsAggregator",
    "UnifiedMetrics",
    "PlatformAnalytics",
    "CrossPlatformInsights",
    "HashtagOptimizer",
    "HashtagStrategy",
    "TrendingHashtags",
    "OptimizedTags",
    "ABTestingEngine",
    "TestVariant",
    "TestResult",
    "PerformanceMetrics",
    # New distribution intelligence module
    "DistributionIntelligence",
    "DistributionStrategy",
    "EngagementPrediction",
    "PlatformPriority",
    "ContentType",
    "AudienceSegment",
    # New content security module
    "ContentSecurity",
    "SecurityConfiguration",
    "WatermarkInfo",
    "ContentFingerprint",
    "SecurityViolation",
    "SecurityLevel",
    "WatermarkType",
    "ProtectionMethod",
    # New automation orchestrator module
    "AutomationOrchestrator",
    "DistributionWorkflow",
    "WorkflowStep",
    "WorkflowStatus",
    "ExecutionReport",
    "WorkflowTemplate",
    "StepType",
    "Priority",
    # New revenue distribution module
    "RevenueDistribution",
    "RevenueStream",
    "RevenueRecord",
    "PlatformMetrics",
    "ROIAnalysis",
    "BudgetAllocation",
    "ConsolidatedReport",
    "RevenueType",
    "Currency",
    # New cross-platform sync module
    "CrossPlatformSync",
    "PlatformContent",
    "SyncRule",
    "SyncSession",
    "SyncConflict",
    "SyncStatus",
    "ConflictType",
    "ConflictResolution"
]