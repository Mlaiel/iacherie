"""
Predictive Analytics Agent Module - Enterprise AI-Powered Forecasting & Intelligence System

Industrial-grade predictive analytics system providing comprehensive forecasting, trend prediction,
market intelligence, and AI-powered business insights for content creators and platform optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Core Features:
- Advanced predictive modeling with ensemble machine learning
- Time series forecasting for content performance and revenue
- Market trend analysis and competitive intelligence
- Audience behavior prediction and segmentation
- Risk assessment and opportunity identification
- Multi-format content performance forecasting
- Collaboration success prediction
- Monetization optimization forecasting
- Real-time predictive insights and alerting
- Business intelligence dashboards and recommendations
"""

from .predictive_analytics_agent import (
    PredictiveAnalyticsAgent,
    PredictionRequest,
    PredictionResult,
    TrendForecast,
    MarketInsight,
    RiskAssessment,
    OpportunityAnalysis,
    PredictionConfig,
    ForecastMetrics,
    PredictiveModel,
    ModelPerformance
)

from .forecasting_engine import (
    ForecastingEngine,
    TimeSeriesForecaster,
    ContentPerformancePredictor,
    RevenueForecaster,
    AudienceGrowthPredictor,
    CollaborationSuccessPredictor
)

from .trend_analyzer import (
    TrendAnalyzer,
    MarketTrendDetector,
    ViralContentPredictor,
    SeasonalPatternAnalyzer,
    CompetitorAnalyzer
)

from .risk_analyzer import (
    RiskAnalyzer,
    ContentRiskAssessor,
    PlatformRiskAnalyzer,
    MarketRiskEvaluator,
    ReputationRiskPredictor
)

from .opportunity_detector import (
    OpportunityDetector,
    CollaborationOpportunityFinder,
    MonetizationOptimizer,
    GrowthOpportunityAnalyzer,
    TrendOpportunityIdentifier
)

# Import all main components
from .predictive_analytics_agent import PredictiveAnalyticsAgent
from .forecasting_engine import ForecastingEngine, TimeSeriesPredictor, MLPredictor, EnsemblePredictor, AccuracyMetrics
from .trend_analyzer import TrendAnalyzer, TrendPattern, ViralContentPredictor, MarketIntelligenceEngine
from .risk_analyzer import RiskAnalyzer, RiskFactor, RiskCategory, ContentRiskAssessor, PlatformRiskAnalyzer, MarketRiskEvaluator, ReputationRiskPredictor
from .opportunity_detector import (
    OpportunityDetector, CollaborationOpportunityFinder, MonetizationOptimizer, 
    GrowthOpportunityAnalyzer, TrendOpportunityIdentifier, 
    GrowthOpportunity, CollaborationOpportunity, MonetizationOpportunity, TrendOpportunity,
    OpportunityType, OpportunityPriority, OpportunityStage
)
from .performance_optimizer import (
    PerformanceOptimizer, ContentPerformanceAnalyzer, EngagementOptimizationEngine, ConversionOptimizationSpecialist,
    OptimizationRecommendation, PerformanceAnalysis, A_BTestConfiguration,
    OptimizationType, OptimizationPriority, MetricImpactLevel
)
from .realtime_monitoring import (
    RealTimeMonitoringSystem, AlertManager, MetricCollector, AnomalyDetector,
    MonitoringAlert, RealTimeMetrics, MetricThreshold,
    AlertSeverity, MetricType, MonitoringStatus, AlertType
)
from .metadata import (
    MODULE_METADATA, ARCHITECTURE_OVERVIEW, PERFORMANCE_SPECIFICATIONS,
    INTEGRATION_SPECIFICATIONS, DEPLOYMENT_SPECIFICATIONS,
    ModuleDocumentation, module_documentation
)
from .index import (
    PredictiveAnalyticsModule, predictive_analytics_module,
    analyze_creator, get_quick_insights, get_module_info, get_features
)

# Export all components
__all__ = [
    # Main agent
    'PredictiveAnalyticsAgent',
    
    # Forecasting components
    'ForecastingEngine',
    'TimeSeriesPredictor', 
    'MLPredictor',
    'EnsemblePredictor',
    'AccuracyMetrics',
    
    # Trend analysis components
    'TrendAnalyzer',
    'TrendPattern',
    'ViralContentPredictor',
    'MarketIntelligenceEngine',
    
    # Risk analysis components
    'RiskAnalyzer',
    'RiskFactor',
    'RiskCategory',
    'ContentRiskAssessor',
    'PlatformRiskAnalyzer', 
    'MarketRiskEvaluator',
    'ReputationRiskPredictor',
    
    # Opportunity detection components
    'OpportunityDetector',
    'CollaborationOpportunityFinder',
    'MonetizationOptimizer', 
    'GrowthOpportunityAnalyzer',
    'TrendOpportunityIdentifier',
    'GrowthOpportunity',
    'CollaborationOpportunity',
    'MonetizationOpportunity', 
    'TrendOpportunity',
    'OpportunityType',
    'OpportunityPriority',
    'OpportunityStage',
    
    # Performance optimization components
    'PerformanceOptimizer',
    'ContentPerformanceAnalyzer',
    'EngagementOptimizationEngine', 
    'ConversionOptimizationSpecialist',
    'OptimizationRecommendation',
    'PerformanceAnalysis',
    'A_BTestConfiguration',
    'OptimizationType',
    'OptimizationPriority',
    'MetricImpactLevel',
    
    # Real-time monitoring components
    'RealTimeMonitoringSystem',
    'AlertManager',
    'MetricCollector',
    'AnomalyDetector',
    'MonitoringAlert',
    'RealTimeMetrics', 
    'MetricThreshold',
    'AlertSeverity',
    'MetricType',
    'MonitoringStatus',
    'AlertType',
    
    # Module documentation and metadata
    'MODULE_METADATA',
    'ARCHITECTURE_OVERVIEW',
    'PERFORMANCE_SPECIFICATIONS',
    'INTEGRATION_SPECIFICATIONS', 
    'DEPLOYMENT_SPECIFICATIONS',
    'ModuleDocumentation',
    'module_documentation',
    
    # Module integration and convenience functions
    'PredictiveAnalyticsModule',
    'predictive_analytics_module',
    'analyze_creator',
    'get_quick_insights',
    'get_module_info', 
    'get_features'
]

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Team specialties for this advanced AI system
TEAM_SPECIALTIES = [
    "Lead Dev IA",
    "Backend Senior Engineer", 
    "ML Engineer",
    "DBA Specialist",
    "Security Expert",
    "Microservices Architect",
    "Audio Processing Engineer", 
    "DevOps Engineer",
    "IA Prompt Engineer"
]
