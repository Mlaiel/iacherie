#!/usr/bin/env python3
"""
Ainflue Platform Core Analytics Module
======================================

Enterprise-grade analytics platform for comprehensive creator economy intelligence,
performance tracking, revenue analytics, content optimization, and collaboration insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.

This module provides comprehensive analytics capabilities including:
- Creator performance analytics and ML-based success scoring
- Revenue intelligence and financial forecasting
- Content analytics platform with viral prediction
- Collaboration intelligence and brand-creator matching
- Predictive creator success modeling and trajectory analysis
- Business intelligence platform with advanced reporting
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Configure module-level logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Enterprise Commercial License"

# Module imports with error handling
try:
    # Core Analytics Components
    from .business_intelligence_platform import (
        BusinessIntelligencePlatform,
        AnalyticsType,
        ReportType,
        DataSource,
        AnalyticsQuery,
        Report
    )
    logger.info("✅ Business Intelligence Platform loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Business Intelligence Platform: {e}")
    BusinessIntelligencePlatform = None

try:
    from .creator_performance_analytics import (
        CreatorPerformanceAnalytics,
        CreatorProfile,
        PlatformMetrics,
        PerformanceSnapshot,
        PerformanceInsight,
        PlatformType,
        MetricType,
        CreatorCategory
    )
    logger.info("✅ Creator Performance Analytics loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Creator Performance Analytics: {e}")
    CreatorPerformanceAnalytics = None

try:
    from .revenue_intelligence_engine import (
        RevenueIntelligenceEngine,
        RevenueTransaction,
        RevenueStream,
        BrandSpendAnalysis,
        RevenueInsight,
        FinancialForecast,
        RevenueStreamType,
        PaymentStatus,
        Currency,
        RevenueCategory
    )
    logger.info("✅ Revenue Intelligence Engine loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Revenue Intelligence Engine: {e}")
    RevenueIntelligenceEngine = None

try:
    from .content_analytics_platform import (
        ContentAnalyticsPlatform,
        ContentMetadata,
        ContentPerformance,
        ContentInsight,
        ViralPrediction,
        ContentQualityScore,
        ContentType,
        ContentStatus,
        ViralityLevel
    )
    logger.info("✅ Content Analytics Platform loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Content Analytics Platform: {e}")
    ContentAnalyticsPlatform = None

try:
    from .collaboration_intelligence_system import (
        CollaborationIntelligenceSystem,
        BrandProfile,
        CreatorProfile as CollabCreatorProfile,
        Collaboration,
        MatchingScore,
        NetworkInsight,
        CollaborationInsight,
        PartnershipType,
        CollaborationStatus,
        MatchingCriteria,
        SuccessMetrics
    )
    logger.info("✅ Collaboration Intelligence System loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Collaboration Intelligence System: {e}")
    CollaborationIntelligenceSystem = None

try:
    from .predictive_creator_success import (
        PredictiveCreatorSuccess,
        CreatorDataPoint,
        SuccessPrediction,
        ChurnRiskAssessment,
        GrowthOpportunity,
        SuccessTrajectory,
        LifecycleInsight,
        SuccessStage,
        RiskLevel,
        PredictionModel,
        SuccessMetric
    )
    logger.info("✅ Predictive Creator Success loaded")
except ImportError as e:
    logger.warning(f"❌ Failed to import Predictive Creator Success: {e}")
    PredictiveCreatorSuccess = None


class AnalyticsPlatformCore:
    """
    Unified Analytics Platform Core
    
    Central orchestrator for all analytics components providing a unified interface
    for creator economy intelligence, performance tracking, and business insights.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the analytics platform core"""
        self.config = config or {}
        self.initialized_components = {}
        self.startup_time = datetime.now()
        
        # Initialize available components
        self._initialize_components()
        
        logger.info("🚀 Analytics Platform Core initialized successfully")
    
    def _initialize_components(self) -> None:
        """Initialize all available analytics components"""
        try:
            # Business Intelligence Platform
            if BusinessIntelligencePlatform:
                self.initialized_components['business_intelligence'] = BusinessIntelligencePlatform()
                logger.info("✅ Business Intelligence Platform initialized")
            
            # Creator Performance Analytics
            if CreatorPerformanceAnalytics:
                self.initialized_components['creator_performance'] = CreatorPerformanceAnalytics()
                logger.info("✅ Creator Performance Analytics initialized")
            
            # Revenue Intelligence Engine
            if RevenueIntelligenceEngine:
                self.initialized_components['revenue_intelligence'] = RevenueIntelligenceEngine()
                logger.info("✅ Revenue Intelligence Engine initialized")
            
            # Content Analytics Platform
            if ContentAnalyticsPlatform:
                self.initialized_components['content_analytics'] = ContentAnalyticsPlatform()
                logger.info("✅ Content Analytics Platform initialized")
            
            # Collaboration Intelligence System
            if CollaborationIntelligenceSystem:
                self.initialized_components['collaboration_intelligence'] = CollaborationIntelligenceSystem()
                logger.info("✅ Collaboration Intelligence System initialized")
            
            # Predictive Creator Success
            if PredictiveCreatorSuccess:
                self.initialized_components['predictive_success'] = PredictiveCreatorSuccess()
                logger.info("✅ Predictive Creator Success initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a specific analytics component"""
        return self.initialized_components.get(component_name)
    
    def get_business_intelligence(self):
        """Get Business Intelligence Platform component"""
        return self.get_component('business_intelligence')
    
    def get_creator_performance(self):
        """Get Creator Performance Analytics component"""
        return self.get_component('creator_performance')
    
    def get_revenue_intelligence(self):
        """Get Revenue Intelligence Engine component"""
        return self.get_component('revenue_intelligence')
    
    def get_content_analytics(self):
        """Get Content Analytics Platform component"""
        return self.get_component('content_analytics')
    
    def get_collaboration_intelligence(self):
        """Get Collaboration Intelligence System component"""
        return self.get_component('collaboration_intelligence')
    
    def get_predictive_success(self):
        """Get Predictive Creator Success component"""
        return self.get_component('predictive_success')
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status"""
        return {
            "platform_name": "Ainflue Analytics Platform Core",
            "version": __version__,
            "status": "operational",
            "startup_time": self.startup_time.isoformat(),
            "uptime_hours": (datetime.now() - self.startup_time).total_seconds() / 3600,
            "initialized_components": list(self.initialized_components.keys()),
            "total_components": len(self.initialized_components),
            "component_status": {
                name: "active" for name in self.initialized_components.keys()
            },
            "available_analytics": {
                "creator_performance_tracking": bool(self.get_creator_performance()),
                "revenue_intelligence": bool(self.get_revenue_intelligence()),
                "content_analytics": bool(self.get_content_analytics()),
                "collaboration_intelligence": bool(self.get_collaboration_intelligence()),
                "predictive_modeling": bool(self.get_predictive_success()),
                "business_intelligence": bool(self.get_business_intelligence())
            },
            "enterprise_features": [
                "ML-powered creator success prediction",
                "Advanced revenue forecasting",
                "Viral content prediction algorithms",
                "Brand-creator matching intelligence",
                "Real-time performance analytics",
                "Comprehensive business intelligence"
            ],
            "supported_platforms": [
                "YouTube", "Instagram", "TikTok", "Twitter", 
                "LinkedIn", "Facebook", "Twitch", "Pinterest"
            ],
            "last_updated": datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "overall_health": "healthy",
            "timestamp": datetime.now().isoformat(),
            "component_health": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check each component
            for name, component in self.initialized_components.items():
                try:
                    if hasattr(component, 'get_system_status'):
                        status = component.get_system_status()
                        health_status["component_health"][name] = {
                            "status": status.get("system_status", "unknown"),
                            "details": status
                        }
                    else:
                        health_status["component_health"][name] = {
                            "status": "active",
                            "details": {"note": "Basic health check only"}
                        }
                except Exception as e:
                    health_status["component_health"][name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    health_status["errors"].append(f"{name}: {e}")
            
            # Determine overall health
            error_count = len(health_status["errors"])
            if error_count > 0:
                if error_count >= len(self.initialized_components) / 2:
                    health_status["overall_health"] = "critical"
                else:
                    health_status["overall_health"] = "degraded"
            
        except Exception as e:
            health_status["overall_health"] = "critical"
            health_status["errors"].append(f"Health check failed: {e}")
        
        return health_status


# Create default platform instance
default_platform = None

def get_analytics_platform(config: Optional[Dict[str, Any]] = None) -> AnalyticsPlatformCore:
    """Get or create analytics platform instance"""
    global default_platform
    
    if default_platform is None:
        default_platform = AnalyticsPlatformCore(config)
    
    return default_platform


# Convenience functions for direct component access
def get_business_intelligence():
    """Get Business Intelligence Platform component"""
    platform = get_analytics_platform()
    return platform.get_business_intelligence()

def get_creator_performance():
    """Get Creator Performance Analytics component"""
    platform = get_analytics_platform()
    return platform.get_creator_performance()

def get_revenue_intelligence():
    """Get Revenue Intelligence Engine component"""
    platform = get_analytics_platform()
    return platform.get_revenue_intelligence()

def get_content_analytics():
    """Get Content Analytics Platform component"""
    platform = get_analytics_platform()
    return platform.get_content_analytics()

def get_collaboration_intelligence():
    """Get Collaboration Intelligence System component"""
    platform = get_analytics_platform()
    return platform.get_collaboration_intelligence()

def get_predictive_success():
    """Get Predictive Creator Success component"""
    platform = get_analytics_platform()
    return platform.get_predictive_success()


# Module exports
__all__ = [
    # Core Platform
    'AnalyticsPlatformCore',
    'get_analytics_platform',
    
    # Convenience Functions
    'get_business_intelligence',
    'get_creator_performance',
    'get_revenue_intelligence',
    'get_content_analytics',
    'get_collaboration_intelligence',
    'get_predictive_success',
    
    # Business Intelligence Platform
    'BusinessIntelligencePlatform',
    'AnalyticsType',
    'ReportType',
    'DataSource',
    'AnalyticsQuery',
    'Report',
    
    # Creator Performance Analytics
    'CreatorPerformanceAnalytics',
    'CreatorProfile',
    'PlatformMetrics',
    'PerformanceSnapshot',
    'PerformanceInsight',
    'PlatformType',
    'MetricType',
    'CreatorCategory',
    
    # Revenue Intelligence Engine
    'RevenueIntelligenceEngine',
    'RevenueTransaction',
    'RevenueStream',
    'BrandSpendAnalysis',
    'RevenueInsight',
    'FinancialForecast',
    'RevenueStreamType',
    'PaymentStatus',
    'Currency',
    'RevenueCategory',
    
    # Content Analytics Platform
    'ContentAnalyticsPlatform',
    'ContentMetadata',
    'ContentPerformance',
    'ContentInsight',
    'ViralPrediction',
    'ContentQualityScore',
    'ContentType',
    'ContentStatus',
    'ViralityLevel',
    
    # Collaboration Intelligence System
    'CollaborationIntelligenceSystem',
    'BrandProfile',
    'CollabCreatorProfile',
    'Collaboration',
    'MatchingScore',
    'NetworkInsight',
    'CollaborationInsight',
    'PartnershipType',
    'CollaborationStatus',
    'MatchingCriteria',
    'SuccessMetrics',
    
    # Predictive Creator Success
    'PredictiveCreatorSuccess',
    'CreatorDataPoint',
    'SuccessPrediction',
    'ChurnRiskAssessment',
    'GrowthOpportunity',
    'SuccessTrajectory',
    'LifecycleInsight',
    'SuccessStage',
    'RiskLevel',
    'PredictionModel',
    'SuccessMetric',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__',
    '__license__'
]

# Initialize logging message
logger.info(f"🎯 Ainflue Analytics Platform Core v{__version__} - Ready for Enterprise Analytics")
logger.info(f"📧 Support: {__email__}")
logger.info(f"📋 Components loaded: {len(__all__)} exports available")
logger.info(f"⚡ Platform Status: Operational - Ready for analytics workloads")