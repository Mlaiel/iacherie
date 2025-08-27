"""
Platform Aggregator Module

Aggregates data and analytics from multiple platforms for unified insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass
import statistics

from .base import (
    PlatformBase, PlatformManager, AnalyticsData, PlatformType
)

logger = logging.getLogger(__name__)


class AggregationType(Enum):
    """Aggregation type enumeration"""
    SUM = "sum"
    AVERAGE = "average"
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    WEIGHTED_AVERAGE = "weighted_average"
    TOTAL_UNIQUE = "total_unique"


class TimeFrame(Enum):
    """Time frame enumeration"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


@dataclass
class MetricDefinition:
    """Metric definition for aggregation"""
    name: str
    field: str
    aggregation_type: AggregationType
    weight: float = 1.0
    platforms: Optional[List[str]] = None
    description: str = ""


@dataclass
class CrossPlatformContent:
    """Cross-platform content mapping"""
    content_id: str
    title: str
    platform_mappings: Dict[str, str]  # platform_id -> platform_content_id
    created_at: datetime
    content_type: str
    metadata: Dict[str, Any] = None


@dataclass
class AggregatedMetrics:
    """Aggregated metrics result"""
    content_id: str
    time_frame: TimeFrame
    start_date: datetime
    end_date: datetime
    total_views: int
    total_likes: int
    total_shares: int
    total_comments: int
    average_engagement_rate: float
    platform_breakdown: Dict[str, AnalyticsData]
    custom_metrics: Dict[str, Any]
    calculated_at: datetime


@dataclass
class PlatformPerformance:
    """Platform performance metrics"""
    platform_id: str
    total_content: int
    total_views: int
    total_engagement: int
    average_engagement_rate: float
    best_performing_content: Optional[str]
    worst_performing_content: Optional[str]
    growth_rate: float
    last_updated: datetime


@dataclass
class AudienceInsights:
    """Aggregated audience insights"""
    total_reach: int
    unique_viewers: int
    demographics: Dict[str, Any]
    geographic_distribution: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    peak_activity_times: List[datetime]
    platform_preferences: Dict[str, float]


class PlatformAggregator:
    """Multi-platform data aggregation and analytics engine"""
    
    def __init__(self, platform_manager: PlatformManager):
        """Initialize aggregator with platform manager"""
        self.platform_manager = platform_manager
        self.content_mappings: Dict[str, CrossPlatformContent] = {}
        self.metric_definitions: List[MetricDefinition] = []
        self.cached_results: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Initialize default metric definitions
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize default metric definitions"""
        default_metrics = [
            MetricDefinition("total_views", "views", AggregationType.SUM, 1.0, description="Total views across platforms"),
            MetricDefinition("total_likes", "likes", AggregationType.SUM, 1.0, description="Total likes across platforms"),
            MetricDefinition("total_shares", "shares", AggregationType.SUM, 1.0, description="Total shares across platforms"),
            MetricDefinition("total_comments", "comments", AggregationType.SUM, 1.0, description="Total comments across platforms"),
            MetricDefinition("avg_engagement_rate", "engagement_rate", AggregationType.WEIGHTED_AVERAGE, 1.0, description="Weighted average engagement rate"),
            MetricDefinition("max_reach", "reach", AggregationType.MAXIMUM, 1.0, description="Maximum reach across platforms"),
            MetricDefinition("total_impressions", "impressions", AggregationType.SUM, 1.0, description="Total impressions across platforms")
        ]
        
        self.metric_definitions.extend(default_metrics)
    
    def register_content_mapping(self, mapping: CrossPlatformContent):
        """Register cross-platform content mapping"""
        self.content_mappings[mapping.content_id] = mapping
        logger.info(f"Registered content mapping for {mapping.title} across {len(mapping.platform_mappings)} platforms")
    
    def add_metric_definition(self, metric: MetricDefinition):
        """Add custom metric definition"""
        self.metric_definitions.append(metric)
        logger.info(f"Added metric definition: {metric.name}")
    
    async def aggregate_content_analytics(
        self,
        content_id: str,
        start_date: datetime,
        end_date: datetime,
        time_frame: TimeFrame = TimeFrame.DAY
    ) -> Optional[AggregatedMetrics]:
        """Aggregate analytics for cross-platform content"""
        
        # Get content mapping
        content_mapping = self.content_mappings.get(content_id)
        if not content_mapping:
            logger.error(f"No content mapping found for {content_id}")
            return None
        
        # Check cache
        cache_key = f"analytics_{content_id}_{start_date}_{end_date}_{time_frame.value}"
        if cache_key in self.cached_results:
            cache_entry = self.cached_results[cache_key]
            if (datetime.utcnow() - cache_entry['timestamp']).seconds < self.cache_ttl:
                return cache_entry['data']
        
        try:
            # Gather analytics from all platforms
            platform_analytics = {}
            
            for platform_id, platform_content_id in content_mapping.platform_mappings.items():
                platform = self.platform_manager.get_platform(platform_id)
                if platform and platform.is_active:
                    try:
                        analytics = await platform.get_analytics(platform_content_id, start_date, end_date)
                        platform_analytics[platform_id] = analytics
                    except Exception as e:
                        logger.warning(f"Failed to get analytics from {platform_id}: {e}")
            
            if not platform_analytics:
                logger.warning(f"No analytics data available for content {content_id}")
                return None
            
            # Aggregate metrics
            aggregated = self._aggregate_platform_data(platform_analytics)
            
            # Create result
            result = AggregatedMetrics(
                content_id=content_id,
                time_frame=time_frame,
                start_date=start_date,
                end_date=end_date,
                total_views=aggregated.get('total_views', 0),
                total_likes=aggregated.get('total_likes', 0),
                total_shares=aggregated.get('total_shares', 0),
                total_comments=aggregated.get('total_comments', 0),
                average_engagement_rate=aggregated.get('avg_engagement_rate', 0.0),
                platform_breakdown=platform_analytics,
                custom_metrics=aggregated.get('custom_metrics', {}),
                calculated_at=datetime.utcnow()
            )
            
            # Cache result
            self.cached_results[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating content analytics: {e}")
            return None
    
    async def get_platform_performance(
        self,
        platform_ids: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, PlatformPerformance]:
        """Get performance metrics for platforms"""
        
        if not platform_ids:
            platform_ids = [p.platform_id for p in self.platform_manager.get_active_platforms()]
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        performance_data = {}
        
        for platform_id in platform_ids:
            platform = self.platform_manager.get_platform(platform_id)
            if not platform or not platform.is_active:
                continue
            
            try:
                # Get all content for this platform
                content_list = await platform.get_user_content()
                
                if not content_list:
                    continue
                
                # Aggregate performance metrics
                total_views = 0
                total_engagement = 0
                engagement_rates = []
                content_performance = {}
                
                for content in content_list[:10]:  # Limit to recent 10 items
                    content_id = content.get('id')
                    if content_id:
                        try:
                            analytics = await platform.get_analytics(content_id, start_date, end_date)
                            
                            total_views += analytics.views
                            content_engagement = analytics.likes + analytics.shares + analytics.comments
                            total_engagement += content_engagement
                            
                            if analytics.engagement_rate:
                                engagement_rates.append(analytics.engagement_rate)
                            
                            content_performance[content_id] = content_engagement
                            
                        except Exception as e:
                            logger.warning(f"Failed to get analytics for {content_id} on {platform_id}: {e}")
                
                # Calculate metrics
                avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0.0
                
                best_content = max(content_performance.items(), key=lambda x: x[1])[0] if content_performance else None
                worst_content = min(content_performance.items(), key=lambda x: x[1])[0] if content_performance else None
                
                # Calculate growth rate (simplified)
                growth_rate = 0.0  # Would need historical data for accurate calculation
                
                performance_data[platform_id] = PlatformPerformance(
                    platform_id=platform_id,
                    total_content=len(content_list),
                    total_views=total_views,
                    total_engagement=total_engagement,
                    average_engagement_rate=avg_engagement_rate,
                    best_performing_content=best_content,
                    worst_performing_content=worst_content,
                    growth_rate=growth_rate,
                    last_updated=datetime.utcnow()
                )
                
            except Exception as e:
                logger.error(f"Error calculating performance for {platform_id}: {e}")
        
        return performance_data
    
    async def get_audience_insights(
        self,
        platform_ids: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> AudienceInsights:
        """Get aggregated audience insights"""
        
        if not platform_ids:
            platform_ids = [p.platform_id for p in self.platform_manager.get_active_platforms()]
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        total_reach = 0
        unique_viewers = 0
        demographics = {}
        geographic_distribution = {}
        engagement_patterns = {}
        platform_preferences = {}
        
        for platform_id in platform_ids:
            platform = self.platform_manager.get_platform(platform_id)
            if not platform or not platform.is_active:
                continue
            
            try:
                # Get platform-specific audience data
                # This would require platform-specific implementations
                # For now, we'll use aggregated content analytics
                
                content_list = await platform.get_user_content()
                platform_reach = 0
                platform_engagement = 0
                
                for content in content_list[:5]:  # Sample recent content
                    content_id = content.get('id')
                    if content_id:
                        try:
                            analytics = await platform.get_analytics(content_id, start_date, end_date)
                            platform_reach += analytics.reach or analytics.views
                            platform_engagement += analytics.likes + analytics.shares + analytics.comments
                        except:
                            continue
                
                total_reach += platform_reach
                platform_preferences[platform_id] = platform_engagement / max(platform_reach, 1)
                
            except Exception as e:
                logger.error(f"Error getting audience insights for {platform_id}: {e}")
        
        # Estimate unique viewers (simplified)
        unique_viewers = int(total_reach * 0.7)  # Assume 70% unique
        
        return AudienceInsights(
            total_reach=total_reach,
            unique_viewers=unique_viewers,
            demographics=demographics,
            geographic_distribution=geographic_distribution,
            engagement_patterns=engagement_patterns,
            peak_activity_times=[],
            platform_preferences=platform_preferences
        )
    
    def _aggregate_platform_data(self, platform_analytics: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """Aggregate data from multiple platforms"""
        aggregated = {}
        custom_metrics = {}
        
        for metric_def in self.metric_definitions:
            # Filter platforms if specified
            relevant_platforms = platform_analytics
            if metric_def.platforms:
                relevant_platforms = {
                    pid: data for pid, data in platform_analytics.items()
                    if pid in metric_def.platforms
                }
            
            if not relevant_platforms:
                continue
            
            # Extract values
            values = []
            weights = []
            
            for platform_id, analytics in relevant_platforms.items():
                value = getattr(analytics, metric_def.field, 0)
                if value is not None:
                    values.append(value)
                    # Use views as weight for weighted averages
                    weights.append(analytics.views * metric_def.weight)
            
            if not values:
                aggregated[metric_def.name] = 0
                continue
            
            # Apply aggregation
            if metric_def.aggregation_type == AggregationType.SUM:
                aggregated[metric_def.name] = sum(values)
            elif metric_def.aggregation_type == AggregationType.AVERAGE:
                aggregated[metric_def.name] = statistics.mean(values)
            elif metric_def.aggregation_type == AggregationType.MAXIMUM:
                aggregated[metric_def.name] = max(values)
            elif metric_def.aggregation_type == AggregationType.MINIMUM:
                aggregated[metric_def.name] = min(values)
            elif metric_def.aggregation_type == AggregationType.WEIGHTED_AVERAGE:
                if sum(weights) > 0:
                    aggregated[metric_def.name] = sum(v * w for v, w in zip(values, weights)) / sum(weights)
                else:
                    aggregated[metric_def.name] = statistics.mean(values)
            elif metric_def.aggregation_type == AggregationType.TOTAL_UNIQUE:
                aggregated[metric_def.name] = len(set(values))
        
        aggregated['custom_metrics'] = custom_metrics
        return aggregated
    
    async def compare_content_performance(
        self,
        content_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """Compare performance across multiple content pieces"""
        
        comparison_data = {}
        
        for content_id in content_ids:
            metrics = await self.aggregate_content_analytics(content_id, start_date, end_date)
            if metrics:
                comparison_data[content_id] = {
                    'total_views': metrics.total_views,
                    'total_likes': metrics.total_likes,
                    'total_shares': metrics.total_shares,
                    'total_comments': metrics.total_comments,
                    'engagement_rate': metrics.average_engagement_rate,
                    'platform_count': len(metrics.platform_breakdown),
                    'best_platform': max(
                        metrics.platform_breakdown.items(),
                        key=lambda x: x[1].views,
                        default=(None, None)
                    )[0]
                }
        
        return comparison_data
    
    async def get_trending_content(
        self,
        platform_ids: List[str] = None,
        limit: int = 10,
        time_frame: TimeFrame = TimeFrame.DAY
    ) -> List[Dict[str, Any]]:
        """Get trending content across platforms"""
        
        if not platform_ids:
            platform_ids = [p.platform_id for p in self.platform_manager.get_active_platforms()]
        
        trending_content = []
        
        for platform_id in platform_ids:
            platform = self.platform_manager.get_platform(platform_id)
            if not platform or not platform.is_active:
                continue
            
            try:
                # Get recent content
                content_list = await platform.get_user_content()
                
                # Get analytics for recent content
                for content in content_list[:20]:  # Check recent 20 items
                    content_id = content.get('id')
                    if content_id:
                        try:
                            end_date = datetime.utcnow()
                            start_date = end_date - timedelta(days=1 if time_frame == TimeFrame.DAY else 7)
                            
                            analytics = await platform.get_analytics(content_id, start_date, end_date)
                            
                            # Calculate trend score
                            trend_score = self._calculate_trend_score(analytics)
                            
                            trending_content.append({
                                'content_id': content_id,
                                'platform_id': platform_id,
                                'title': content.get('title', content.get('name', 'Untitled')),
                                'views': analytics.views,
                                'engagement_rate': analytics.engagement_rate,
                                'trend_score': trend_score,
                                'analytics': analytics
                            })
                        except:
                            continue
            
            except Exception as e:
                logger.error(f"Error getting trending content from {platform_id}: {e}")
        
        # Sort by trend score and return top items
        trending_content.sort(key=lambda x: x['trend_score'], reverse=True)
        return trending_content[:limit]
    
    def _calculate_trend_score(self, analytics: AnalyticsData) -> float:
        """Calculate trending score for content"""
        # Simple trending algorithm
        # In practice, this would be more sophisticated
        
        views_score = min(analytics.views / 1000, 100)  # Cap at 100k views
        engagement_score = analytics.engagement_rate * 10  # Scale engagement rate
        
        # Recent content gets bonus
        time_bonus = 1.0  # Would need creation time for accurate calculation
        
        return (views_score + engagement_score) * time_bonus
    
    async def export_aggregated_data(
        self,
        content_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export aggregated data in specified format"""
        
        export_data = {
            'export_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'content_count': len(content_ids),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'format': format
            },
            'content_analytics': {},
            'summary': {}
        }
        
        # Get analytics for all content
        total_views = 0
        total_engagement = 0
        platform_distribution = {}
        
        for content_id in content_ids:
            metrics = await self.aggregate_content_analytics(content_id, start_date, end_date)
            if metrics:
                export_data['content_analytics'][content_id] = {
                    'total_views': metrics.total_views,
                    'total_likes': metrics.total_likes,
                    'total_shares': metrics.total_shares,
                    'total_comments': metrics.total_comments,
                    'engagement_rate': metrics.average_engagement_rate,
                    'platforms': list(metrics.platform_breakdown.keys())
                }
                
                total_views += metrics.total_views
                total_engagement += metrics.total_likes + metrics.total_shares + metrics.total_comments
                
                for platform_id in metrics.platform_breakdown.keys():
                    platform_distribution[platform_id] = platform_distribution.get(platform_id, 0) + 1
        
        # Add summary
        export_data['summary'] = {
            'total_views': total_views,
            'total_engagement': total_engagement,
            'average_engagement_rate': total_engagement / max(total_views, 1) * 100,
            'platform_distribution': platform_distribution,
            'top_performing_content': max(
                export_data['content_analytics'].items(),
                key=lambda x: x[1]['total_views'],
                default=(None, None)
            )[0]
        }
        
        return export_data
    
    def clear_cache(self):
        """Clear aggregation cache"""
        self.cached_results.clear()
        logger.info("Aggregation cache cleared")
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics"""
        return {
            'content_mappings': len(self.content_mappings),
            'metric_definitions': len(self.metric_definitions),
            'cached_results': len(self.cached_results),
            'cache_ttl': self.cache_ttl,
            'active_platforms': len(self.platform_manager.get_active_platforms())
        }
