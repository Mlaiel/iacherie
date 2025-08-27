"""
Analytics Agent Module - Enterprise Real-Time Intelligence & Predictive Analytics

Industrial-grade analytics system providing comprehensive performance tracking, predictive insights,
and AI-powered business intelligence for content creators and platform optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Core Features:
- Real-time multi-platform analytics aggregation
- AI-powered predictive modeling and forecasting
- Anomaly detection with automated alerting
- Custom dashboard generation and visualization
- Competitive intelligence and benchmarking
- Revenue optimization insights
- Audience segmentation and behavior analysis
- Multi-format content analysis (audio, video, image, text, blog)
- AI-powered content protection analytics
- Business intelligence dashboards
- Performance monitoring and optimization
- Collaboration insights and monetization analytics
"""

from .analytics_agent import (
    AnalyticsAgent,
    AnalyticsRequest,
    AnalyticsResult,
    AnalyticsType
)

from .content_analytics import (
    ContentAnalyticsEngine,
    ContentOptimizationEngine,
    ContentMetrics,
    ContentType,
    EngagementMetric,
    AudienceSegment,
    TrendAnalysis
)

from .business_intelligence import (
    BusinessIntelligenceEngine,
    BusinessKPI,
    KPICategory,
    RevenueMetrics,
    RevenueStream,
    UserEngagementMetrics,
    EnterpriseKPIManager
)

from .performance_analytics import (
    PerformanceMonitor,
    SystemPerformance,
    ApplicationPerformance,
    PerformanceMetric,
    PerformanceMetricType,
    PerformanceAlert,
    AlertSeverity,
    EnterprisePerformanceAnalyticsEngine
)

__all__ = [
    # Main Analytics Agent
    "AnalyticsAgent",
    "AnalyticsRequest",
    "AnalyticsResult", 
    "AnalyticsType",
    
    # Content Analytics
    "ContentAnalyticsEngine",
    "ContentOptimizationEngine",
    "ContentMetrics",
    "ContentType",
    "EngagementMetric",
    "AudienceSegment",
    "TrendAnalysis",
    
    # Business Intelligence
    "BusinessIntelligenceEngine",
    "BusinessKPI",
    "KPICategory",
    "RevenueMetrics",
    "RevenueStream",
    "UserEngagementMetrics",
    "EnterpriseKPIManager",
    
    # Performance Analytics
    "PerformanceMonitor",
    "SystemPerformance",
    "ApplicationPerformance",
    "PerformanceMetric",
    "PerformanceMetricType",
    "PerformanceAlert",
    "AlertSeverity",
    "EnterprisePerformanceAnalyticsEngine"
]

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Enterprise Analytics Agent for IA Influencer Platform"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."