"""
Content Analytics Engine
========================

Advanced content analytics and metrics processing for multi-format content.
Handles performance tracking, engagement analysis, and content optimization insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis
import json

from ..models.content_model import ContentModel
from ..models.analytics_model import AnalyticsModel
from ..storage.storage_manager import StorageManager
from ..vector_db.vector_db_manager import VectorDBManager


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class MetricType(Enum):
    """Analytics metric types"""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    SHARES = "shares"
    DOWNLOADS = "downloads"
    REVENUE = "revenue"
    PROTECTION_ALERTS = "protection_alerts"
    PLATFORM_PERFORMANCE = "platform_performance"


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    content_id: str
    content_type: ContentType
    views: int
    engagement_rate: float
    shares: int
    downloads: int
    revenue: float
    protection_score: float
    platform_performance: Dict[str, Any]
    timestamp: datetime


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    user_id: str
    period_start: datetime
    period_end: datetime
    total_content: int
    total_views: int
    total_revenue: float
    engagement_rate: float
    protection_effectiveness: float
    top_performing_content: List[Dict]
    platform_breakdown: Dict[str, Any]
    trends: Dict[str, Any]


class ContentAnalytics:
    """
    Professional content analytics engine for IA Influencer Agent platform.
    
    Provides comprehensive analytics for content performance, engagement,
    revenue tracking, and protection effectiveness across multiple platforms.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis, 
                 storage_manager: StorageManager, vector_db: VectorDBManager):
        """
        Initialize ContentAnalytics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            storage_manager: Storage management service
            vector_db: Vector database manager
        """
        self.db_session = db_session
        self.redis = redis_client
        self.storage = storage_manager
        self.vector_db = vector_db
        self.logger = logging.getLogger(__name__)
        
        # Cache configuration
        self.cache_ttl = 3600  # 1 hour
        self.batch_size = 1000
        
    async def track_content_metrics(self, content_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Track content performance metrics.
        
        Args:
            content_id: Unique content identifier
            metrics: Dictionary containing metric values
            
        Returns:
            Success status
        """



        try:
            # Validate content exists
            content = await self._get_content_by_id(content_id)
            if not content:
                self.logger.warning(f"Content not found: {content_id}")
                return False
                
            # Create analytics record
            analytics_data = AnalyticsModel(
                content_id=content_id,
                user_id=content.user_id,
                metric_type=MetricType.PLATFORM_PERFORMANCE.value,
                metric_value=json.dumps(metrics),
                platform=metrics.get('platform', 'unknown'),
                timestamp=datetime.utcnow()
            )
            
            self.db_session.add(analytics_data)
            await self.db_session.commit()
            
            # Update cache
            await self._update_metrics_cache(content_id, metrics)
            
            # Trigger real-time analytics update
            await self._trigger_realtime_update(content_id, metrics)
            
            self.logger.info(f"Tracked metrics for content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking metrics for {content_id}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def get_content_performance(self, content_id: str, 
                                    period_days: int = 30) -> Optional[ContentMetrics]:
        """
        Get comprehensive performance metrics for specific content.
        
        Args:
            content_id: Content identifier
            period_days: Analysis period in days
            
        Returns:
            Content metrics or None if not found
        """



        try:
            # Check cache first
            cache_key = f"content_metrics:{content_id}:{period_days}"
            cached_data = await self._get_from_cache(cache_key)
            
            if cached_data:
                return ContentMetrics(**cached_data)
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Query metrics from database
            query = select(AnalyticsModel).where(
                and_(
                    AnalyticsModel.content_id == content_id,
                    AnalyticsModel.timestamp >= start_date,
                    AnalyticsModel.timestamp <= end_date
                )
            )
            
            result = await self.db_session.execute(query)
            analytics_records = result.scalars().all()
            
            if not analytics_records:
                return None
            
            # Aggregate metrics
            metrics = await self._aggregate_content_metrics(analytics_records)
            
            # Get content info
            content = await self._get_content_by_id(content_id)
            
            content_metrics = ContentMetrics(
                content_id=content_id,
                content_type=ContentType(content.content_type),
                views=metrics.get('total_views', 0),
                engagement_rate=metrics.get('engagement_rate', 0.0),
                shares=metrics.get('total_shares', 0),
                downloads=metrics.get('total_downloads', 0),
                revenue=metrics.get('total_revenue', 0.0),
                protection_score=metrics.get('protection_score', 0.0),
                platform_performance=metrics.get('platform_breakdown', {}),
                timestamp=datetime.utcnow()
            )
            
            # Cache results
            await self._save_to_cache(cache_key, content_metrics.__dict__)
            
            return content_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting performance for {content_id}: {str(e)}")
            return None
    
    async def generate_analytics_report(self, user_id: str, 
                                      period_days: int = 30) -> Optional[AnalyticsReport]:
        """
        Generate comprehensive analytics report for user.
        
        Args:
            user_id: User identifier
            period_days: Report period in days
            
        Returns:
            Analytics report or None
        """



        try:
            # Check cache
            cache_key = f"analytics_report:{user_id}:{period_days}"
            cached_report = await self._get_from_cache(cache_key)
            
            if cached_report:
                return AnalyticsReport(**cached_report)
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get user content
            user_content = await self._get_user_content(user_id)
            content_ids = [content.id for content in user_content]
            
            if not content_ids:
                return None
            
            # Query analytics data
            query = select(AnalyticsModel).where(
                and_(
                    AnalyticsModel.user_id == user_id,
                    AnalyticsModel.timestamp >= start_date,
                    AnalyticsModel.timestamp <= end_date
                )
            )
            
            result = await self.db_session.execute(query)
            analytics_data = result.scalars().all()
            
            # Process analytics
            report_data = await self._process_analytics_data(analytics_data, user_content)
            
            # Generate trends analysis
            trends = await self._analyze_trends(user_id, analytics_data, period_days)
            
            # Create report
            report = AnalyticsReport(
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                total_content=len(content_ids),
                total_views=report_data.get('total_views', 0),
                total_revenue=report_data.get('total_revenue', 0.0),
                engagement_rate=report_data.get('avg_engagement_rate', 0.0),
                protection_effectiveness=report_data.get('protection_effectiveness', 0.0),
                top_performing_content=report_data.get('top_content', []),
                platform_breakdown=report_data.get('platform_breakdown', {}),
                trends=trends
            )
            
            # Cache report
            await self._save_to_cache(cache_key, report.__dict__, ttl=1800)  # 30 min cache
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report for user {user_id}: {str(e)}")
            return None
    
    async def get_real_time_metrics(self, content_id: str) -> Dict[str, Any]:
        """
        Get real-time metrics for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Real-time metrics dictionary
        """



        try:
            # Get from real-time cache
            rt_cache_key = f"realtime_metrics:{content_id}"
            metrics = await self._get_from_cache(rt_cache_key)
            
            if not metrics:
                # Fallback to latest stored metrics
                metrics = await self._get_latest_metrics(content_id)
            
            return metrics or {}
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics for {content_id}: {str(e)}")
            return {}
    
    async def analyze_content_similarity(self, content_id: str, 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar content based on performance patterns.
        
        Args:
            content_id: Reference content ID
            limit: Maximum number of similar content to return
            
        Returns:
            List of similar content with similarity scores
        """



        try:
            # Get content metrics vector
            content_vector = await self._get_content_vector(content_id)
            if not content_vector:
                return []
            
            # Search for similar vectors
            similar_vectors = await self.vector_db.similarity_search(
                content_vector, 
                limit=limit,
                threshold=0.7
            )
            
            # Enrich with content information
            similar_content = []
            for vector_result in similar_vectors:
                content_info = await self._get_content_by_id(vector_result['content_id'])
                if content_info and content_info.id != content_id:
                    similar_content.append({
                        'content_id': content_info.id,
                        'title': content_info.title,
                        'content_type': content_info.content_type,
                        'similarity_score': vector_result['score'],
                        'performance_metrics': await self._get_latest_metrics(content_info.id)
                    })
            
            return similar_content
            
        except Exception as e:
            self.logger.error(f"Error analyzing similarity for {content_id}: {str(e)}")
            return []
    
    async def predict_content_performance(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict content performance based on historical data and ML models.
        
        Args:
            content_metadata: Content metadata for prediction
            
        Returns:
            Performance predictions
        """



        try:
            # Extract features from metadata
            features = await self._extract_prediction_features(content_metadata)
            
            # Get similar historical content
            similar_content = await self._find_similar_historical_content(features)
            
            # Calculate predictions
            predictions = await self._calculate_performance_predictions(
                features, similar_content
            )
            
            return {
                'predicted_views': predictions.get('views', 0),
                'predicted_engagement_rate': predictions.get('engagement_rate', 0.0),
                'predicted_revenue': predictions.get('revenue', 0.0),
                'confidence_score': predictions.get('confidence', 0.0),
                'recommendations': predictions.get('recommendations', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting performance: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _get_content_by_id(self, content_id: str) -> Optional[ContentModel]:
        """Get content by ID from database"""
        query = select(ContentModel).where(ContentModel.id == content_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_user_content(self, user_id: str) -> List[ContentModel]:
        """Get all content for a user"""
        query = select(ContentModel).where(ContentModel.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def _update_metrics_cache(self, content_id: str, metrics: Dict[str, Any]):
        """Update metrics in cache"""
        cache_key = f"current_metrics:{content_id}"
        await self.redis.setex(cache_key, self.cache_ttl, json.dumps(metrics))
    
    async def _trigger_realtime_update(self, content_id: str, metrics: Dict[str, Any]):
        """Trigger real-time analytics update"""
        rt_key = f"realtime_metrics:{content_id}"
        await self.redis.setex(rt_key, 300, json.dumps(metrics))  # 5 min cache
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""



        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """Save data to cache"""



        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    async def _aggregate_content_metrics(self, analytics_records: List[AnalyticsModel]) -> Dict[str, Any]:
        """Aggregate metrics from analytics records"""
        # Implementation for metrics aggregation
        total_views = 0
        total_shares = 0
        total_downloads = 0
        total_revenue = 0.0
        engagement_scores = []
        platform_data = {}
        
        for record in analytics_records:
            try:
                metric_data = json.loads(record.metric_value)
                
                if record.metric_type == MetricType.VIEWS.value:
                    total_views += metric_data.get('count', 0)
                elif record.metric_type == MetricType.SHARES.value:
                    total_shares += metric_data.get('count', 0)
                elif record.metric_type == MetricType.DOWNLOADS.value:
                    total_downloads += metric_data.get('count', 0)
                elif record.metric_type == MetricType.REVENUE.value:
                    total_revenue += metric_data.get('amount', 0.0)
                elif record.metric_type == MetricType.ENGAGEMENT.value:
                    engagement_scores.append(metric_data.get('rate', 0.0))
                
                # Platform breakdown
                platform = record.platform or 'unknown'
                if platform not in platform_data:
                    platform_data[platform] = {'views': 0, 'revenue': 0.0}
                
                platform_data[platform]['views'] += metric_data.get('views', 0)
                platform_data[platform]['revenue'] += metric_data.get('revenue', 0.0)
                
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Failed to parse metric data: {str(e)}")
                continue
        
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.0
        
        return {
            'total_views': total_views,
            'total_shares': total_shares,
            'total_downloads': total_downloads,
            'total_revenue': total_revenue,
            'engagement_rate': avg_engagement,
            'protection_score': 0.95,  # Placeholder - to be calculated from protection module
            'platform_breakdown': platform_data
        }
    
    async def _process_analytics_data(self, analytics_data: List[AnalyticsModel], 
                                    user_content: List[ContentModel]) -> Dict[str, Any]:
        """Process analytics data for report generation"""
        # Implementation for comprehensive data processing
        # This would include aggregation, calculations, and analysis
        
        total_views = 0
        total_revenue = 0.0
        engagement_rates = []
        platform_performance = {}
        content_performance = {}
        
        # Process each analytics record
        for record in analytics_data:
            try:
                metric_data = json.loads(record.metric_value)
                content_id = record.content_id
                
                # Initialize content tracking
                if content_id not in content_performance:
                    content_performance[content_id] = {
                        'views': 0, 'revenue': 0.0, 'engagement': []
                    }
                
                # Aggregate by metric type
                if record.metric_type == MetricType.VIEWS.value:
                    views = metric_data.get('count', 0)
                    total_views += views
                    content_performance[content_id]['views'] += views
                    
                elif record.metric_type == MetricType.REVENUE.value:
                    revenue = metric_data.get('amount', 0.0)
                    total_revenue += revenue
                    content_performance[content_id]['revenue'] += revenue
                    
                elif record.metric_type == MetricType.ENGAGEMENT.value:
                    engagement = metric_data.get('rate', 0.0)
                    engagement_rates.append(engagement)
                    content_performance[content_id]['engagement'].append(engagement)
                
                # Platform breakdown
                platform = record.platform or 'unknown'
                if platform not in platform_performance:
                    platform_performance[platform] = {'views': 0, 'revenue': 0.0}
                
                platform_performance[platform]['views'] += metric_data.get('views', 0)
                platform_performance[platform]['revenue'] += metric_data.get('revenue', 0.0)
                
            except Exception as e:
                self.logger.warning(f"Error processing analytics record: {str(e)}")
                continue
        
        # Calculate top performing content
        top_content = []
        for content_id, performance in content_performance.items():
            # Find content info
            content_info = next((c for c in user_content if c.id == content_id), None)
            if content_info:
                avg_engagement = np.mean(performance['engagement']) if performance['engagement'] else 0.0
                top_content.append({
                    'content_id': content_id,
                    'title': content_info.title,
                    'views': performance['views'],
                    'revenue': performance['revenue'],
                    'engagement_rate': avg_engagement,
                    'score': performance['views'] * avg_engagement + performance['revenue']
                })
        
        # Sort by performance score
        top_content.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'total_views': total_views,
            'total_revenue': total_revenue,
            'avg_engagement_rate': np.mean(engagement_rates) if engagement_rates else 0.0,
            'protection_effectiveness': 0.94,  # Placeholder
            'top_content': top_content[:10],  # Top 10
            'platform_breakdown': platform_performance
        }
    
    async def _analyze_trends(self, user_id: str, analytics_data: List[AnalyticsModel], 
                            period_days: int) -> Dict[str, Any]:
        """Analyze trends in user analytics data"""
        # Implementation for trend analysis
        # This would calculate growth rates, seasonal patterns, etc.
        
        # Group data by time periods
        daily_metrics = {}
        
        for record in analytics_data:
            date_key = record.timestamp.date().isoformat()
            
            if date_key not in daily_metrics:
                daily_metrics[date_key] = {'views': 0, 'revenue': 0.0, 'engagement': []}
            
            try:
                metric_data = json.loads(record.metric_value)
                
                if record.metric_type == MetricType.VIEWS.value:
                    daily_metrics[date_key]['views'] += metric_data.get('count', 0)
                elif record.metric_type == MetricType.REVENUE.value:
                    daily_metrics[date_key]['revenue'] += metric_data.get('amount', 0.0)
                elif record.metric_type == MetricType.ENGAGEMENT.value:
                    daily_metrics[date_key]['engagement'].append(metric_data.get('rate', 0.0))
                    
            except Exception:
                continue
        
        # Calculate trends
        dates = sorted(daily_metrics.keys())
        
        if len(dates) >= 2:
            # Views trend
            first_half_views = sum(daily_metrics[date]['views'] for date in dates[:len(dates)//2])
            second_half_views = sum(daily_metrics[date]['views'] for date in dates[len(dates)//2:])
            views_trend = ((second_half_views - first_half_views) / max(first_half_views, 1)) * 100
            
            # Revenue trend
            first_half_revenue = sum(daily_metrics[date]['revenue'] for date in dates[:len(dates)//2])
            second_half_revenue = sum(daily_metrics[date]['revenue'] for date in dates[len(dates)//2:])
            revenue_trend = ((second_half_revenue - first_half_revenue) / max(first_half_revenue, 1)) * 100
        else:
            views_trend = 0.0
            revenue_trend = 0.0
        
        return {
            'views_trend_percent': views_trend,
            'revenue_trend_percent': revenue_trend,
            'best_performing_day': max(dates, key=lambda d: daily_metrics[d]['views']) if dates else None,
            'growth_rate': (views_trend + revenue_trend) / 2,
            'daily_breakdown': daily_metrics
        }
    
    async def _get_latest_metrics(self, content_id: str) -> Dict[str, Any]:
        """Get latest metrics for content"""
        query = select(AnalyticsModel).where(
            AnalyticsModel.content_id == content_id
        ).order_by(AnalyticsModel.timestamp.desc()).limit(10)
        
        result = await self.db_session.execute(query)
        records = result.scalars().all()
        
        if not records:
            return {}
        
        return await self._aggregate_content_metrics(records)
    
    async def _get_content_vector(self, content_id: str) -> Optional[List[float]]:
        """Get content performance vector for similarity analysis"""
        # Implementation would extract performance features as vector
        # This is a simplified placeholder
        metrics = await self._get_latest_metrics(content_id)
        
        if not metrics:
            return None
        
        # Create feature vector from metrics
        vector = [
            metrics.get('total_views', 0) / 10000,  # Normalized views
            metrics.get('engagement_rate', 0.0),
            metrics.get('total_revenue', 0.0) / 1000,  # Normalized revenue
            metrics.get('protection_score', 0.0)
        ]
        
        return vector
    
    async def _extract_prediction_features(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for performance prediction"""
        # Implementation would extract relevant features
        return {
            'content_type': content_metadata.get('content_type'),
            'duration': content_metadata.get('duration', 0),
            'tags_count': len(content_metadata.get('tags', [])),
            'title_length': len(content_metadata.get('title', '')),
            'description_length': len(content_metadata.get('description', '')),
            'upload_time': content_metadata.get('upload_time', datetime.utcnow()).hour
        }
    
    async def _find_similar_historical_content(self, features: Dict[str, Any]) -> List[Dict]:
        """Find similar historical content for prediction"""
        # Implementation would use ML models or similarity search
        # Placeholder implementation
        return []
    
    async def _calculate_performance_predictions(self, features: Dict[str, Any], 
                                               similar_content: List[Dict]) -> Dict[str, Any]:
        """Calculate performance predictions using ML models"""
        # Implementation would use trained ML models
        # Placeholder with basic heuristics
        
        base_views = 1000
        base_engagement = 0.05
        base_revenue = 10.0
        
        # Simple feature-based adjustments
        if features.get('content_type') == 'video':
            base_views *= 1.5
            base_revenue *= 1.3
        
        if features.get('tags_count', 0) > 5:
            base_engagement *= 1.2
        
        return {
            'views': int(base_views),
            'engagement_rate': min(base_engagement, 1.0),
            'revenue': base_revenue,
            'confidence': 0.75,
            'recommendations': [
                'Add more relevant tags for better discoverability',
                'Optimize upload timing for better engagement'
            ]
        }
