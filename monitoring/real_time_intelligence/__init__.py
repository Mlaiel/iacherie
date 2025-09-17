"""
⚡ Real-Time Intelligence - Surveillance Temps Réel
==================================================

Module intelligence temps réel pour surveillance instantanée.
Analytics live, détection anomalies et réponse automatique.

Architecture: monitoring/real_time_intelligence/ (NIVEAU 2)
Responsabilité: Intelligence temps réel, analytics live, alertes instantanées

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

from .index import (
    RealTimeIntelligence,
    LiveMetrics,
    InstantAlert,
    TrendDetector,
    MetricType
)

from .live_creator_analytics import (
    LiveCreatorAnalytics,
    CreatorMetrics,
    AudienceInsight,
    ContentPerformance,
    CreatorJourney,
    EngagementType,
    PlatformType,
    AudienceSegment,
    create_live_creator_analytics
)

from .instant_revenue_monitor import (
    InstantRevenueMonitor,
    RevenueTransaction,
    RevenueMetrics,
    FraudAlert,
    RevenueForcast,
    RevenueStream,
    PaymentStatus,
    FraudRisk,
    Currency,
    create_instant_revenue_monitor
)

from .real_time_collaboration_tracker import (
    RealTimeCollaborationTracker,
    CollaborationMatch,
    CollaborationProposal,
    CollaborationContract,
    CollaborationMetrics,
    InteractionEvent,
    CollaborationType,
    CollaborationStatus,
    MatchingCriteria,
    IndustryCategory,
    create_real_time_collaboration_tracker
)

from .content_performance_stream import (
    ContentPerformanceStream,
    ContentMetrics,
    ViralAnalysis,
    SEOPerformance,
    CrossPlatformAnalysis,
    ContentOptimization,
    ContentType,
    ContentCategory,
    Platform,
    ViralStage,
    QualityMetric,
    create_content_performance_stream
)

__all__ = [
    # Core components
    'RealTimeIntelligence',
    'LiveMetrics',
    'InstantAlert',
    'TrendDetector',
    'MetricType',
    
    # Live Creator Analytics
    'LiveCreatorAnalytics',
    'CreatorMetrics',
    'AudienceInsight',
    'ContentPerformance',
    'CreatorJourney',
    'EngagementType',
    'PlatformType',
    'AudienceSegment',
    'create_live_creator_analytics',
    
    # Instant Revenue Monitor
    'InstantRevenueMonitor',
    'RevenueTransaction',
    'RevenueMetrics',
    'FraudAlert',
    'RevenueForcast',
    'RevenueStream',
    'PaymentStatus',
    'FraudRisk',
    'Currency',
    'create_instant_revenue_monitor',
    
    # Real-Time Collaboration Tracker
    'RealTimeCollaborationTracker',
    'CollaborationMatch',
    'CollaborationProposal',
    'CollaborationContract',
    'CollaborationMetrics',
    'InteractionEvent',
    'CollaborationType',
    'CollaborationStatus',
    'MatchingCriteria',
    'IndustryCategory',
    'create_real_time_collaboration_tracker',
    
    # Content Performance Stream
    'ContentPerformanceStream',
    'ContentMetrics',
    'ViralAnalysis',
    'SEOPerformance',
    'CrossPlatformAnalysis',
    'ContentOptimization',
    'ContentType',
    'ContentCategory',
    'Platform',
    'ViralStage',
    'QualityMetric',
    'create_content_performance_stream'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"