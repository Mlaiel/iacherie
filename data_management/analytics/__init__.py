"""Analytics Module - Enterprise Business Intelligence System
==========================================================

Comprehensive analytics and business intelligence system for the 
IA Influencer Agent platform. Provides real-time metrics collection,
advanced data processing, executive reporting, and strategic insights.

Core Features:
- Business metrics collection and KPI tracking
- User behavior analytics and segmentation  
- Content performance and protection analytics
- Revenue optimization and financial analysis
- Advanced data processing and trend analysis
- Executive dashboards and automated reporting
- Multi-tier storage architecture with caching
- Data visualization and business intelligence
- Multi-format export capabilities and integrations

System Architecture:
- Collectors: Real-time data collection from platform operations
- Processors: Advanced analytics, ML-based insights, and predictions
- Storage: Multi-tier data architecture (hot/warm/cold/archive)
- Reporters: Executive dashboards and business intelligence reports
- Exporters: Multi-format data export and external integrations

Author: Fahed Mlaiel  
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved

Enterprise Warning:
===================
This analytics system contains proprietary algorithms, methodologies,
and business intelligence frameworks developed by Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
All concepts, data models, and analytical approaches are protected
intellectual property.
"""

from .collectors import BusinessMetricsCollector

from .user_behavior import UserBehaviorCollector  
from .content_analytics import ContentAnalyticsCollector

from .revenue_metrics import RevenueMetricsCollector

from .processors import MetricsProcessor, TrendAnalyzer, AnomalyDetector
from .reporters import BusinessReporter, ExecutiveDashboard
from .storage import AnalyticsStorage, MetricsWarehouse, TimeSeriesStore, CacheManager
from .predictive_analytics import PredictiveAnalyticsEngine, PredictionScheduler
from .realtime_dashboard import RealTimeDashboard

from .business_intelligence import BusinessIntelligenceEngine

from .metrics_aggregator import AdvancedMetricsAggregator

from .exporters import (
    ExcelExporter, 
    PDFReporter, 
    APIExporter, 
    DataLakeExporter, 
    ScheduledExporter,
    ExportFormat,
    ExportDestination,
    ExportConfiguration,
    ExportJob,
    create_exporter
)

from .collectors import (
    BusinessMetricsCollector,
    UserBehaviorCollector,
    ContentAnalyticsCollector,
    RevenueMetricsCollector,
    MLPerformanceCollector,
    SecurityMetricsCollector
)

from .processors import (
    MetricsProcessor,
    TrendAnalyzer,
    AnomalyDetector,
    PredictiveAnalyzer,
    PerformanceOptimizer
)

from .reporters import (
    BusinessReporter,
    ExecutiveDashboard,
    TechnicalReporter,
    ComplianceReporter,
    RealTimeReporter
)

from .storage import (
    AnalyticsStorage,
    MetricsWarehouse,
    TimeSeriesStore,
    CacheManager
)

from .exporters import (
    ExcelExporter,
    PDFReporter,
    APIExporter,
    DataLakeExporter
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Collectors
    "BusinessMetricsCollector",
    "UserBehaviorCollector", 
    "ContentAnalyticsCollector",
    "RevenueMetricsCollector",
    "MLPerformanceCollector",
    "SecurityMetricsCollector",
    
    # Processors
    "MetricsProcessor",
    "TrendAnalyzer",
    "AnomalyDetector", 
    # Predictive Analytics
    "PredictiveAnalyticsEngine",
    "PredictionScheduler",
    
    # Real-time Dashboard
    "RealTimeDashboard",
    
    # Business Intelligence
    "BusinessIntelligenceEngine",
    
    # Metrics Aggregation
    "AdvancedMetricsAggregator",
    
    # Analysis Tools
    "PredictiveAnalyzer",
    "PerformanceOptimizer",
    
    # Reporters
    "BusinessReporter",
    "ExecutiveDashboard",
    "TechnicalReporter",
    "ComplianceReporter",
    "RealTimeReporter",
    
    # Storage
    "AnalyticsStorage",
    "MetricsWarehouse",
    "TimeSeriesStore",
    "CacheManager",
    
    # Exporters
    "ExcelExporter",
    "PDFReporter", 
    "APIExporter",
    "DataLakeExporter"
]
