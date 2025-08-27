"""
Core Analytics Module - Industrial IA Influencer Agent Platform

Enterprise-grade analytics framework for multi-format content creators with advanced
business intelligence, performance monitoring, and predictive analytics capabilities.

Business Logic Flow:
User Upload → Content Processing → Analytics Collection → Performance Monitoring →
Business Intelligence → Revenue Tracking → Collaboration Analytics → Platform Optimization

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""

from .collector import MetricsCollector, BusinessMetricsCollector
from .aggregator import DataAggregator, TimeSeriesAggregator
from .dashboard import AnalyticsDashboard, RealtimeDashboard
from .intelligence import BusinessIntelligence, PredictiveAnalytics
from .reporting import ReportGenerator, PerformanceReporter
from .tracking import UserTracker, ContentTracker, RevenueTracker
from .processor import AnalyticsProcessor, MetricsProcessor
from .engine import AnalyticsEngine
from .exceptions import AnalyticsError, MetricsError, ReportingError

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core Components
    "AnalyticsEngine",
    "MetricsCollector", 
    "BusinessMetricsCollector",
    "DataAggregator",
    "TimeSeriesAggregator",
    "AnalyticsProcessor",
    "MetricsProcessor",
    
    # Dashboard & Visualization
    "AnalyticsDashboard",
    "RealtimeDashboard",
    
    # Business Intelligence
    "BusinessIntelligence",
    "PredictiveAnalytics",
    
    # Reporting
    "ReportGenerator",
    "PerformanceReporter",
    
    # Tracking
    "UserTracker",
    "ContentTracker", 
    "RevenueTracker",
    
    # Exceptions
    "AnalyticsError",
    "MetricsError",
    "ReportingError"
]
