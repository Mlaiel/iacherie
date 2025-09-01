"""Analytics Module Index - Central access point for all analytics services
========================================================================

Central index file providing unified access to all analytics engines and services.
This file serves as the main entry point for external modules to access analytics functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import redis
import asyncpg
from fastapi import HTTPException, Depends

# Import all analytics engines
from .performance_engine import PerformanceAnalyticsEngine
from .audience_intelligence import AudienceIntelligenceSystem
from .revenue_optimizer import RevenueOptimizationEngine
from .content_insights import ContentInsightsAnalyzer
from .predictive_modeling import PredictiveModelingEngine
from .engagement_tracker import EngagementTrackingSystem
from .platform_comparator import PlatformPerformanceComparator
from .trend_detector import TrendDetectionEngine
from .roi_calculator import ROICalculatorEngine
from .dashboard_aggregator import DashboardAggregatorEngine

logger = logging.getLogger(__name__)

class AnalyticsServiceManager:
    """
    Central manager for all analytics services providing unified access
    and orchestration of analytics engines for the IA Influencer Agent platform.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
        # Initialize all analytics engines
        self.performance_engine = PerformanceAnalyticsEngine(redis_client, db_pool)
        self.audience_intelligence = AudienceIntelligenceSystem(redis_client, db_pool)
        self.revenue_optimizer = RevenueOptimizationEngine(redis_client, db_pool)
        self.content_insights = ContentInsightsAnalyzer(redis_client, db_pool)
        self.predictive_modeling = PredictiveModelingEngine(redis_client, db_pool)
        self.engagement_tracker = EngagementTrackingSystem(redis_client, db_pool)
        self.platform_comparator = PlatformPerformanceComparator(redis_client, db_pool)
        self.trend_detector = TrendDetectionEngine(redis_client, db_pool)
        self.roi_calculator = ROICalculatorEngine(redis_client, db_pool)
        self.dashboard_aggregator = DashboardAggregatorEngine(redis_client, db_pool)
        
        self._initialized = False
        
    async def initialize_all_services(self) -> Dict[str, bool]:
        """
Initialize all analytics services and return status"""
        if self._initialized:
            return {"status": "already_initialized"}
            
        try:
            logger.info("Initializing all analytics services...")
            
            # Initialize all engines in parallel for better performance
            initialization_tasks = [
                ("performance_engine", self.performance_engine.initialize()),
                ("audience_intelligence", self.audience_intelligence.initialize()),
                ("revenue_optimizer", self.revenue_optimizer.initialize()),
                ("content_insights", self.content_insights.initialize()),
                ("predictive_modeling", self.predictive_modeling.initialize()),
                ("engagement_tracker", self.engagement_tracker.initialize()),
                ("platform_comparator", self.platform_comparator.initialize()),
                ("trend_detector", self.trend_detector.initialize()),
                ("roi_calculator", self.roi_calculator.initialize()),
                ("dashboard_aggregator", self.dashboard_aggregator.initialize())
            ]
            
            # Execute all initializations
            results = {}
            for service_name, task in initialization_tasks:
                try:
                    await task
                    results[service_name] = True
                    logger.info(f"✅ {service_name} initialized successfully")
                except Exception as e:
                    results[service_name] = False
                    logger.error(f"❌ Failed to initialize {service_name}: {e}")
            
            # Check if all services initialized successfully
            all_successful = all(results.values())
            if all_successful:
                self._initialized = True
                logger.info("🚀 All analytics services initialized successfully")
            else:
                logger.warning("⚠️ Some analytics services failed to initialize")
            
            return {
                "status": "completed",
                "all_successful": all_successful,
                "services": results
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics services: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "all_successful": False
            }

    async def get_comprehensive_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics data from all services"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            logger.info(f"Generating comprehensive analytics for creator {creator_id}")
            
            # Get overview dashboard (combines all modules)
            overview_data = await self.dashboard_aggregator.get_overview_dashboard(creator_id)
            
            return {
                "creator_id": creator_id,
                "comprehensive_analytics": overview_data,
                "services_status": "operational",
                "generated_at": overview_data.get("generated_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive analytics: {e}")
            raise HTTPException(status_code=500, detail="Comprehensive analytics generation failed")

    async def get_performance_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get performance insights and recommendations"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            performance_data = await self.performance_engine.get_performance_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "performance_analytics",
                "data": performance_data
            }
        except Exception as e:
            logger.error(f"Failed to get performance insights: {e}")
            raise HTTPException(status_code=500, detail="Performance insights generation failed")

    async def get_audience_analysis(self, creator_id: str) -> Dict[str, Any]:
        """Get audience intelligence and segmentation analysis"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            audience_data = await self.audience_intelligence.get_audience_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "audience_intelligence",
                "data": audience_data
            }
        except Exception as e:
            logger.error(f"Failed to get audience analysis: {e}")
            raise HTTPException(status_code=500, detail="Audience analysis generation failed")

    async def get_revenue_optimization(self, creator_id: str) -> Dict[str, Any]:
        """Get revenue optimization strategies and forecasts"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            revenue_data = await self.revenue_optimizer.get_revenue_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "revenue_optimization",
                "data": revenue_data
            }
        except Exception as e:
            logger.error(f"Failed to get revenue optimization: {e}")
            raise HTTPException(status_code=500, detail="Revenue optimization generation failed")

    async def get_content_recommendations(self, creator_id: str) -> Dict[str, Any]:
        """Get content insights and optimization recommendations"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            content_data = await self.content_insights.get_content_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "content_insights",
                "data": content_data
            }
        except Exception as e:
            logger.error(f"Failed to get content recommendations: {e}")
            raise HTTPException(status_code=500, detail="Content recommendations generation failed")

    async def get_trend_opportunities(self, creator_id: str) -> Dict[str, Any]:
        """Get trending opportunities and viral content predictions"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            trends_data = await self.trend_detector.get_trend_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "trend_detection",
                "data": trends_data
            }
        except Exception as e:
            logger.error(f"Failed to get trend opportunities: {e}")
            raise HTTPException(status_code=500, detail="Trend opportunities generation failed")

    async def get_roi_analysis(self, creator_id: str) -> Dict[str, Any]:
        """Get ROI analysis and investment optimization"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            roi_data = await self.roi_calculator.get_roi_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "roi_calculation",
                "data": roi_data
            }
        except Exception as e:
            logger.error(f"Failed to get ROI analysis: {e}")
            raise HTTPException(status_code=500, detail="ROI analysis generation failed")

    async def get_predictions_forecast(self, creator_id: str) -> Dict[str, Any]:
        """Get ML predictions and forecasts"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            predictions_data = await self.predictive_modeling.get_predictions_dashboard_data(creator_id)
            return {
                "creator_id": creator_id,
                "service": "predictive_modeling",
                "data": predictions_data
            }
        except Exception as e:
            logger.error(f"Failed to get predictions forecast: {e}")
            raise HTTPException(status_code=500, detail="Predictions forecast generation failed")

    async def get_real_time_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get real-time engagement and performance metrics"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            # Combine real-time data from multiple sources
            engagement_metrics = await self.engagement_tracker.get_real_time_metrics(creator_id)
            dashboard_metrics = await self.dashboard_aggregator.get_real_time_metrics(creator_id)
            
            return {
                "creator_id": creator_id,
                "service": "real_time_analytics",
                "engagement_metrics": engagement_metrics,
                "dashboard_metrics": dashboard_metrics,
                "timestamp": dashboard_metrics.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            raise HTTPException(status_code=500, detail="Real-time metrics generation failed")

    async def refresh_all_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Refresh all cached analytics data for a creator"""
        if not self._initialized:
            raise HTTPException(status_code=503, detail="Analytics services not initialized")
            
        try:
            logger.info(f"Refreshing all analytics data for creator {creator_id}")
            
            # Refresh dashboard caches
            refresh_results = await self.dashboard_aggregator.refresh_all_dashboards(creator_id)
            
            # Trigger data refresh for other services
            refresh_tasks = [
                self.performance_engine.analyze_performance_metrics(creator_id),
                self.audience_intelligence.perform_audience_analysis(creator_id),
                self.revenue_optimizer.optimize_revenue_strategies(creator_id),
                self.content_insights.analyze_content_performance(creator_id),
                self.trend_detector.detect_trending_content(),
                self.roi_calculator.calculate_comprehensive_roi(creator_id, self.roi_calculator.ROITimeframe.MONTHLY)
            ]
            
            # Execute refresh tasks
            try:
                await asyncio.gather(*refresh_tasks, return_exceptions=True)
                logger.info(f"✅ All analytics data refreshed for creator {creator_id}")
            except Exception as e:
                logger.warning(f"Some analytics refresh tasks failed: {e}")
            
            return {
                "creator_id": creator_id,
                "refresh_status": "completed",
                "dashboard_refresh_results": refresh_results,
                "message": "All analytics data has been refreshed"
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh analytics: {e}")
            raise HTTPException(status_code=500, detail="Analytics refresh failed")

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all analytics services"""
        return {
            "analytics_services_initialized": self._initialized,
            "available_services": [
                "performance_analytics",
                "audience_intelligence", 
                "revenue_optimization",
                "content_insights",
                "predictive_modeling",
                "engagement_tracking",
                "platform_comparison",
                "trend_detection",
                "roi_calculation",
                "dashboard_aggregation"
            ],
            "service_count": 10,
            "status": "operational" if self._initialized else "not_initialized"
        }

# Global instance (will be initialized by the application)
analytics_manager: Optional[AnalyticsServiceManager] = None

def get_analytics_manager() -> AnalyticsServiceManager:
    """Dependency injection for FastAPI to get analytics manager"""
    if analytics_manager is None:
        raise HTTPException(status_code=503, detail="Analytics manager not initialized")
    return analytics_manager

async def initialize_analytics_services(redis_client: redis.Redis, db_pool: asyncpg.Pool) -> AnalyticsServiceManager:
    """Initialize the global analytics manager"""
    global analytics_manager
    
    if analytics_manager is None:
        analytics_manager = AnalyticsServiceManager(redis_client, db_pool)
        await analytics_manager.initialize_all_services()
        logger.info("🚀 Global analytics manager initialized successfully")
    
    return analytics_manager

# Export main classes and functions
__all__ = [
    "AnalyticsServiceManager",
    "get_analytics_manager", 
    "initialize_analytics_services",
    "PerformanceAnalyticsEngine",
    "AudienceIntelligenceSystem",
    "RevenueOptimizationEngine", 
    "ContentInsightsAnalyzer",
    "PredictiveModelingEngine",
    "EngagementTrackingSystem",
    "PlatformPerformanceComparator",
    "TrendDetectionEngine",
    "ROICalculatorEngine",
    "DashboardAggregatorEngine"
]
