"""
Dashboard Aggregator - Real-time dashboard data aggregation system
=================================================================

Comprehensive dashboard aggregation engine that combines data from all analytics
modules to provide unified real-time insights and performance dashboards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import redis
import asyncpg
from fastapi import HTTPException

# Import all analytics modules
from .performance_engine import PerformanceAnalyticsEngine
from .audience_intelligence import AudienceIntelligenceSystem  
from .revenue_optimizer import RevenueOptimizationEngine
from .content_insights import ContentInsightsAnalyzer
from .predictive_modeling import PredictiveModelingEngine
from .engagement_tracker import EngagementTrackingSystem
from .platform_comparator import PlatformPerformanceComparator
from .trend_detector import TrendDetectionEngine
from .roi_calculator import ROICalculatorEngine

logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types of dashboards"""
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    REVENUE = "revenue"
    CONTENT = "content"
    TRENDS = "trends"
    ROI = "roi"

@dataclass
class DashboardCache:
    """Dashboard cache configuration"""
    cache_key: str
    ttl_seconds: int
    data: Dict[str, Any]
    last_updated: datetime

class DashboardAggregatorEngine:
    """
    Real-time dashboard data aggregation system that combines insights
    from all analytics modules into unified performance dashboards.
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
        
    async def initialize(self) -> None:
        """Initialize dashboard aggregator and all engines"""



        try:
            # Initialize all engines
            await asyncio.gather(
                self.performance_engine.initialize(),
                self.audience_intelligence.initialize(),
                self.revenue_optimizer.initialize(),
                self.content_insights.initialize(),
                self.predictive_modeling.initialize(),
                self.engagement_tracker.initialize(),
                self.platform_comparator.initialize(),
                self.trend_detector.initialize(),
                self.roi_calculator.initialize()
            )
            
            await self._setup_database_tables()
            logger.info("Dashboard Aggregator Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Aggregator Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for dashboard caching"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_cache (
                    id SERIAL PRIMARY KEY,
                    creator_id VARCHAR(255) NOT NULL,
                    dashboard_type VARCHAR(50) NOT NULL,
                    cache_key VARCHAR(500) NOT NULL,
                    cached_data JSONB NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_dashboard_cache_lookup (creator_id, dashboard_type, expires_at DESC)
                );
            """)

    async def get_overview_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive overview dashboard combining all modules"""



        try:
            cache_key = f"dashboard_overview_{creator_id}"
            cached_data = await self._get_cached_dashboard(cache_key)
            
            if cached_data:
                return cached_data
            
            # Gather data from all modules in parallel
            dashboard_tasks = [
                self._get_performance_summary(creator_id),
                self._get_audience_summary(creator_id),
                self._get_revenue_summary(creator_id),
                self._get_content_summary(creator_id),
                self._get_trends_summary(creator_id),
                self._get_roi_summary(creator_id),
                self._get_predictions_summary(creator_id)
            ]
            
            results = await asyncio.gather(*dashboard_tasks, return_exceptions=True)
            
            # Combine all data
            overview_dashboard = {
                'creator_id': creator_id,
                'dashboard_type': 'overview',
                'performance_summary': results[0] if not isinstance(results[0], Exception) else {},
                'audience_summary': results[1] if not isinstance(results[1], Exception) else {},
                'revenue_summary': results[2] if not isinstance(results[2], Exception) else {},
                'content_summary': results[3] if not isinstance(results[3], Exception) else {},
                'trends_summary': results[4] if not isinstance(results[4], Exception) else {},
                'roi_summary': results[5] if not isinstance(results[5], Exception) else {},
                'predictions_summary': results[6] if not isinstance(results[6], Exception) else {},
                'key_metrics': await self._get_key_metrics(creator_id),
                'alerts_notifications': await self._get_alerts_notifications(creator_id),
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache the dashboard
            await self._cache_dashboard(cache_key, overview_dashboard, ttl_seconds=300)  # 5 minutes cache
            
            return overview_dashboard
            
        except Exception as e:
            logger.error(f"Failed to get overview dashboard: {e}")
            raise HTTPException(status_code=500, detail="Overview dashboard generation failed")

    async def _get_performance_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get performance summary from performance engine"""



        try:
            analytics_data = await self.performance_engine.get_performance_dashboard_data(creator_id)
            
            return {
                'overall_score': analytics_data.get('performance_score', 0),
                'engagement_rate': analytics_data.get('engagement_metrics', {}).get('avg_engagement_rate', 0),
                'growth_trend': analytics_data.get('growth_analysis', {}).get('growth_trend', 'stable'),
                'top_performing_content': analytics_data.get('top_performing_content', [])[:3],
                'performance_trend': analytics_data.get('performance_trends', {})
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}

    async def _get_audience_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get audience summary from audience intelligence"""



        try:
            audience_data = await self.audience_intelligence.get_audience_dashboard_data(creator_id)
            
            return {
                'total_followers': audience_data.get('audience_overview', {}).get('total_followers', 0),
                'growth_rate': audience_data.get('audience_overview', {}).get('growth_rate', 0),
                'primary_demographics': audience_data.get('demographic_analysis', {}).get('primary_segments', [])[:3],
                'engagement_quality': audience_data.get('engagement_quality', {}).get('overall_quality_score', 0),
                'audience_segments': len(audience_data.get('audience_segments', []))
            }
        except Exception as e:
            logger.error(f"Failed to get audience summary: {e}")
            return {}

    async def _get_revenue_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get revenue summary from revenue optimizer"""



        try:
            revenue_data = await self.revenue_optimizer.get_revenue_dashboard_data(creator_id)
            
            return {
                'total_revenue': revenue_data.get('revenue_overview', {}).get('total_revenue', 0),
                'revenue_growth': revenue_data.get('revenue_overview', {}).get('growth_rate', 0),
                'top_revenue_streams': revenue_data.get('revenue_streams', [])[:3],
                'optimization_score': revenue_data.get('optimization_metrics', {}).get('overall_score', 0),
                'revenue_forecast': revenue_data.get('forecasts', {}).get('next_month_prediction', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get revenue summary: {e}")
            return {}

    async def _get_content_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get content summary from content insights"""



        try:
            content_data = await self.content_insights.get_content_dashboard_data(creator_id)
            
            return {
                'content_quality_score': content_data.get('content_performance', {}).get('avg_quality_score', 0),
                'viral_potential': content_data.get('content_performance', {}).get('avg_viral_potential', 0),
                'top_performing_formats': content_data.get('format_analysis', [])[:3],
                'content_optimization_score': content_data.get('optimization_insights', {}).get('overall_score', 0),
                'trending_topics': content_data.get('trending_analysis', {}).get('relevant_trends', [])[:5]
            }
        except Exception as e:
            logger.error(f"Failed to get content summary: {e}")
            return {}

    async def _get_trends_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get trends summary from trend detector"""



        try:
            trends_data = await self.trend_detector.get_trend_dashboard_data(creator_id)
            
            return {
                'personalized_trends_count': len(trends_data.get('personalized_trends', [])),
                'high_opportunity_trends': len([t for t in trends_data.get('personalized_trends', []) if t.get('opportunity_score', 0) > 0.8]),
                'trending_categories': list(trends_data.get('trending_by_category', {}).keys()),
                'expiring_soon': trends_data.get('trend_summary', {}).get('expiring_soon', 0),
                'top_trends': trends_data.get('personalized_trends', [])[:3]
            }
        except Exception as e:
            logger.error(f"Failed to get trends summary: {e}")
            return {}

    async def _get_roi_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get ROI summary from ROI calculator"""



        try:
            roi_data = await self.roi_calculator.get_roi_dashboard_data(creator_id)
            
            return {
                'overall_roi': roi_data.get('roi_summary', {}).get('overall_roi_percentage', 0),
                'net_profit': roi_data.get('roi_summary', {}).get('net_profit', 0),
                'best_category': roi_data.get('performance_insights', {}).get('best_performing_category', {}),
                'worst_category': roi_data.get('performance_insights', {}).get('worst_performing_category', {}),
                'avg_efficiency': roi_data.get('performance_insights', {}).get('avg_efficiency_score', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get ROI summary: {e}")
            return {}

    async def _get_predictions_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get predictions summary from predictive modeling"""



        try:
            predictions = await self.predictive_modeling.get_predictions_dashboard_data(creator_id)
            
            return {
                'engagement_prediction': predictions.get('engagement_forecast', 0),
                'revenue_prediction': predictions.get('revenue_forecast', 0),
                'growth_prediction': predictions.get('growth_forecast', 0),
                'confidence_level': predictions.get('avg_confidence', 0),
                'prediction_accuracy': predictions.get('model_performance', {}).get('accuracy_score', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get predictions summary: {e}")
            return {}

    async def _get_key_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get key performance indicators across all modules"""



        try:
            async with self.db_pool.acquire() as conn:
                # Get key metrics from database
                metrics = await conn.fetchrow("""
                    SELECT 
                        COALESCE(SUM(total_views), 0) as total_views,
                        COALESCE(SUM(total_engagements), 0) as total_engagements,
                        COALESCE(AVG(engagement_rate), 0) as avg_engagement_rate,
                        COUNT(*) as total_content_pieces
                    FROM content_metrics 
                    WHERE creator_id = $1 
                    AND created_at >= NOW() - INTERVAL '30 days'
                """, creator_id)
                
                revenue_metrics = await conn.fetchrow("""
                    SELECT 
                        COALESCE(SUM(revenue_amount), 0) as total_revenue,
                        COUNT(DISTINCT revenue_stream) as revenue_streams_count
                    FROM revenue_streams 
                    WHERE creator_id = $1 
                    AND transaction_date >= NOW() - INTERVAL '30 days'
                """, creator_id)
                
                return {
                    'total_views_30d': int(metrics['total_views']) if metrics else 0,
                    'total_engagements_30d': int(metrics['total_engagements']) if metrics else 0,
                    'avg_engagement_rate': round(float(metrics['avg_engagement_rate']), 2) if metrics else 0,
                    'total_content_pieces_30d': int(metrics['total_content_pieces']) if metrics else 0,
                    'total_revenue_30d': round(float(revenue_metrics['total_revenue']), 2) if revenue_metrics else 0,
                    'active_revenue_streams': int(revenue_metrics['revenue_streams_count']) if revenue_metrics else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get key metrics: {e}")
            return {}

    async def _get_alerts_notifications(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get alerts and notifications for the creator"""



        try:
            alerts = []
            
            # Performance alerts
            performance_summary = await self._get_performance_summary(creator_id)
            if performance_summary.get('overall_score', 0) < 50:
                alerts.append({
                    'type': 'warning',
                    'category': 'performance',
                    'message': 'Performance score below average - review content strategy',
                    'priority': 'high'
                })
            
            # Revenue alerts  
            revenue_summary = await self._get_revenue_summary(creator_id)
            if revenue_summary.get('revenue_growth', 0) < 0:
                alerts.append({
                    'type': 'alert',
                    'category': 'revenue',
                    'message': 'Revenue declining - implement optimization strategies',
                    'priority': 'high'
                })
            
            # Trend opportunities
            trends_summary = await self._get_trends_summary(creator_id)
            if trends_summary.get('high_opportunity_trends', 0) > 0:
                alerts.append({
                    'type': 'opportunity',
                    'category': 'trends',
                    'message': f"{trends_summary['high_opportunity_trends']} high-opportunity trends available",
                    'priority': 'medium'
                })
            
            # Expiring trends
            if trends_summary.get('expiring_soon', 0) > 0:
                alerts.append({
                    'type': 'urgent',
                    'category': 'trends',
                    'message': f"{trends_summary['expiring_soon']} trends expiring soon - act quickly",
                    'priority': 'high'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts notifications: {e}")
            return []

    async def get_specialized_dashboard(self, creator_id: str, dashboard_type: DashboardType) -> Dict[str, Any]:
        """Get specialized dashboard for specific module"""



        try:
            cache_key = f"dashboard_{dashboard_type.value}_{creator_id}"
            cached_data = await self._get_cached_dashboard(cache_key)
            
            if cached_data:
                return cached_data
            
            # Get data from specific module
            if dashboard_type == DashboardType.PERFORMANCE:
                dashboard_data = await self.performance_engine.get_performance_dashboard_data(creator_id)
            elif dashboard_type == DashboardType.AUDIENCE:
                dashboard_data = await self.audience_intelligence.get_audience_dashboard_data(creator_id)
            elif dashboard_type == DashboardType.REVENUE:
                dashboard_data = await self.revenue_optimizer.get_revenue_dashboard_data(creator_id)
            elif dashboard_type == DashboardType.CONTENT:
                dashboard_data = await self.content_insights.get_content_dashboard_data(creator_id)
            elif dashboard_type == DashboardType.TRENDS:
                dashboard_data = await self.trend_detector.get_trend_dashboard_data(creator_id)
            elif dashboard_type == DashboardType.ROI:
                dashboard_data = await self.roi_calculator.get_roi_dashboard_data(creator_id)
            else:
                dashboard_data = {}
            
            # Add metadata
            dashboard_data.update({
                'creator_id': creator_id,
                'dashboard_type': dashboard_type.value,
                'generated_at': datetime.now().isoformat()
            })
            
            # Cache the specialized dashboard
            await self._cache_dashboard(cache_key, dashboard_data, ttl_seconds=600)  # 10 minutes cache
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get specialized dashboard: {e}")
            raise HTTPException(status_code=500, detail=f"{dashboard_type.value} dashboard generation failed")

    async def _get_cached_dashboard(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached dashboard data from Redis"""



        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached dashboard: {e}")
            return None

    async def _cache_dashboard(self, cache_key: str, data: Dict[str, Any], ttl_seconds: int) -> None:
        """Cache dashboard data in Redis"""



        try:
            import json
            self.redis.setex(cache_key, ttl_seconds, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Failed to cache dashboard: {e}")

    async def refresh_all_dashboards(self, creator_id: str) -> Dict[str, bool]:
        """Refresh all cached dashboards for a creator"""



        try:
            # Clear existing caches
            cache_patterns = [
                f"dashboard_overview_{creator_id}",
                f"dashboard_performance_{creator_id}",
                f"dashboard_audience_{creator_id}",
                f"dashboard_revenue_{creator_id}",
                f"dashboard_content_{creator_id}",
                f"dashboard_trends_{creator_id}",
                f"dashboard_roi_{creator_id}"
            ]
            
            refresh_results = {}
            
            for cache_key in cache_patterns:
                try:
                    # Delete cache
                    self.redis.delete(cache_key)
                    
                    # Regenerate based on dashboard type
                    dashboard_type = cache_key.split('_')[1]
                    if dashboard_type == 'overview':
                        await self.get_overview_dashboard(creator_id)
                    else:
                        await self.get_specialized_dashboard(creator_id, DashboardType(dashboard_type))
                    
                    refresh_results[dashboard_type] = True
                except Exception as e:
                    logger.error(f"Failed to refresh {dashboard_type} dashboard: {e}")
                    refresh_results[dashboard_type] = False
            
            return refresh_results
            
        except Exception as e:
            logger.error(f"Failed to refresh all dashboards: {e}")
            return {}

    async def get_real_time_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get real-time metrics for live dashboard updates"""



        try:
            # Get real-time engagement data
            engagement_data = await self.engagement_tracker.get_real_time_metrics(creator_id)
            
            # Get current trends
            current_trends = await self.trend_detector.detect_trending_content()
            
            # Get latest content performance
            latest_content = await self._get_latest_content_performance(creator_id)
            
            real_time_data = {
                'live_engagement': engagement_data,
                'trending_now': [
                    {
                        'name': trend.name,
                        'category': trend.category.value,
                        'virality_score': trend.virality_score,
                        'opportunity_score': trend.opportunity_score
                    }
                    for trend in current_trends[:5]
                ],
                'latest_content_performance': latest_content,
                'timestamp': datetime.now().isoformat()
            }
            
            return real_time_data
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}

    async def _get_latest_content_performance(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get performance data for latest content"""



        try:
            async with self.db_pool.acquire() as conn:
                latest_content = await conn.fetch("""
                    SELECT 
                        content_id,
                        title,
                        platform,
                        total_views,
                        total_engagements,
                        engagement_rate,
                        created_at
                    FROM content_metrics 
                    WHERE creator_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """, creator_id)
                
                return [
                    {
                        'content_id': content['content_id'],
                        'title': content['title'],
                        'platform': content['platform'],
                        'views': int(content['total_views']),
                        'engagements': int(content['total_engagements']),
                        'engagement_rate': round(float(content['engagement_rate']), 2),
                        'created_at': content['created_at'].isoformat()
                    }
                    for content in latest_content
                ]
                
        except Exception as e:
            logger.error(f"Failed to get latest content performance: {e}")
            return []
