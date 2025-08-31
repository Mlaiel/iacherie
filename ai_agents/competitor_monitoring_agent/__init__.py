"""Competitor Monitoring Agent - Advanced AI-powered competitive intelligence system.

This module provides comprehensive competitor monitoring, market analysis,
and strategic intelligence for content creators and businesses.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""

from .competitor_agent import CompetitorMonitoringAgent

from .data_collection import DataCollectionManager

from .market_intelligence import MarketIntelligenceEngine

from .alert_system import AlertSystem

from .strategic_analysis import StrategicAnalysisEngine

from .config_manager import ConfigurationManager

from .report_generator import ReportGenerator

from .index import CompetitorMonitoringSystem, create_competitor_monitoring_system, get_system_info

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "CompetitorMonitoringAgent",
    "DataCollectionManager", 
    "MarketIntelligenceEngine",
    "AlertSystem",
    "StrategicAnalysisEngine",
    "ConfigurationManager",
    "ReportGenerator",
    "CompetitorMonitoringSystem",
    "create_competitor_monitoring_system",
    "get_system_info"
]

from .core.monitoring_engine import CompetitorMonitoringEngine

from .core.competitive_analyzer import CompetitiveAnalyzer

from .core.market_intelligence import MarketIntelligenceEngine

from .services.monitoring_service import MonitoringService

from .services.intelligence_service import IntelligenceService

from .models.competitor_models import (
    CompetitorProfile,
    CompetitorMetrics,
    CompetitorContent,
    CompetitorTrend
)
from .models.monitoring_models import (
    MonitoringSession,
    MonitoringAlert,
    MonitoringReport,
    MonitoringConfiguration
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All rights reserved"

# Module exports
__all__ = [
    "CompetitorMonitoringEngine",
    "CompetitiveAnalyzer", 
    "MarketIntelligenceEngine",
    "MonitoringService",
    "IntelligenceService",
    "CompetitorProfile",
    "CompetitorMetrics",
    "CompetitorContent",
    "CompetitorTrend",
    "MonitoringSession",
    "MonitoringAlert",
    "MonitoringReport",
    "MonitoringConfiguration"
]

# Agent configuration
COMPETITOR_MONITORING_CONFIG = {
    "agent_name": "competitor_monitoring_agent",
    "version": "2.0.0",
    "description": "Advanced competitive intelligence and monitoring system",
    "capabilities": [
        "multi_platform_monitoring",
        "competitive_analysis",
        "market_intelligence",
        "trend_analysis",
        "sentiment_analysis",
        "performance_benchmarking",
        "strategic_recommendations"
    ],
    "supported_platforms": [
        "instagram",
        "tiktok", 
        "youtube",
        "twitter",
        "linkedin",
        "facebook",
        "spotify",
        "soundcloud"
    ],
    "monitoring_intervals": {
        "real_time": 300,      # 5 minutes
        "frequent": 1800,      # 30 minutes
        "regular": 3600,       # 1 hour
        "daily": 86400,        # 24 hours
        "weekly": 604800       # 7 days
    },
    "analysis_types": [
        "content_performance",
        "engagement_analysis",
        "growth_tracking",
        "sentiment_monitoring",
        "trend_identification",
        "market_positioning"
    ]
}
