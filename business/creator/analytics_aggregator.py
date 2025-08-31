"""
Analytics Aggregator - Comprehensive Multi-Platform Analytics Engine

Ultra-sophisticated analytics system aggregating data from all platforms and content types
to provide creators with unified insights, predictions, and optimization recommendations.

Project: IA Influencer Agent + Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json

from ...core.cache import CacheManager
from ...core.logging import get_logger
from .profile_manager import CreatorProfileManager

logger = get_logger(__name__)


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MetricCategory(Enum):
    """Analytics metric categories"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    GROWTH = "growth"
    REVENUE = "revenue"
    CONTENT = "content"
    AUDIENCE = "audience"


@dataclass
class AnalyticsMetric:
    """Analytics metric data point"""
    metric_id: str
    creator_id: str
    platform: str
    category: MetricCategory
    name: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformConnector:
    """Platform API connector for analytics data"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
        self.supported_platforms = [
            'youtube', 'instagram', 'tiktok', 'twitter', 'facebook',
            'linkedin', 'pinterest', 'snapchat', 'twitch', 'spotify'
        ]
    
    async def fetch_platform_analytics(self, creator_id: str, platform: str, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Fetch analytics data from specific platform"""
        cache_key = f"platform_analytics:{creator_id}:{platform}:{timeframe.value}"
        
        # Check cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Mock platform-specific analytics
        platform_data = await self._get_mock_platform_data(creator_id, platform, timeframe)
        
        # Cache for 1 hour
        await self.cache.set(cache_key, platform_data, ttl=3600)
        
        return platform_data
    
    async def _get_mock_platform_data(self, creator_id: str, platform: str, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Generate mock platform analytics data"""
        base_data = {
            'platform': platform,
            'timeframe': timeframe.value,
            'creator_id': creator_id,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        if platform == 'youtube':
            base_data.update({
                'subscribers': 125000,
                'total_views': 2500000,
                'watch_time_hours': 45000,
                'videos_published': 145,
                'average_view_duration': '4:23',
                'engagement_rate': 8.7,
                'monthly_growth': 12.5
            })
        elif platform == 'instagram':
            base_data.update({
                'followers': 89000,
                'posts': 320,
                'stories': 150,
                'reels': 85,
                'total_likes': 1200000,
                'total_comments': 45000,
                'engagement_rate': 11.2,
                'reach': 750000
            })
        elif platform == 'tiktok':
            base_data.update({
                'followers': 250000,
                'videos': 185,
                'total_views': 15000000,
                'total_likes': 2100000,
                'shares': 125000,
                'engagement_rate': 15.8,
                'viral_videos': 8
            })
        
        return base_data


class DataAggregator:
    """Multi-platform data aggregation engine"""
    
    def __init__(self, platform_connector: PlatformConnector, cache_manager: CacheManager):
        self.platform_connector = platform_connector
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def aggregate_cross_platform_metrics(self, creator_id: str, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Aggregate metrics across all platforms"""



        try:
            # Get connected platforms for creator
            connected_platforms = await self._get_connected_platforms(creator_id)
            
            aggregated_data = {
                'creator_id': creator_id,
                'timeframe': timeframe.value,
                'total_followers': 0,
                'total_engagement': 0,
                'total_reach': 0,
                'platform_breakdown': {},
                'cross_platform_metrics': {},
                'last_aggregated': datetime.utcnow().isoformat()
            }
            
            # Fetch data from each platform
            for platform in connected_platforms:
                platform_data = await self.platform_connector.fetch_platform_analytics(
                    creator_id, platform, timeframe
                )
                
                aggregated_data['platform_breakdown'][platform] = platform_data
                
                # Aggregate totals
                if 'followers' in platform_data:
                    aggregated_data['total_followers'] += platform_data['followers']
                elif 'subscribers' in platform_data:
                    aggregated_data['total_followers'] += platform_data['subscribers']
            
            # Calculate cross-platform metrics
            aggregated_data['cross_platform_metrics'] = await self._calculate_cross_platform_metrics(
                aggregated_data['platform_breakdown']
            )
            
            return aggregated_data
            
        except Exception as e:
            self.logger.error(f"Data aggregation failed for creator {creator_id}: {e}")
            raise
    
    async def _get_connected_platforms(self, creator_id: str) -> List[str]:
        """Get connected platforms for creator"""
        # Mock connected platforms
        return ['youtube', 'instagram', 'tiktok']
    
    async def _calculate_cross_platform_metrics(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cross-platform aggregated metrics"""
        metrics = {
            'average_engagement_rate': 0,
            'total_content_pieces': 0,
            'best_performing_platform': None,
            'platform_distribution': {},
            'growth_trends': {}
        }
        
        # Calculate averages and totals
        engagement_rates = []
        content_counts = {}
        
        for platform, data in platform_data.items():
            if 'engagement_rate' in data:
                engagement_rates.append(data['engagement_rate'])
            
            # Count content pieces
            content_count = 0
            if 'videos_published' in data:
                content_count += data['videos_published']
            if 'posts' in data:
                content_count += data['posts']
            if 'videos' in data:
                content_count += data['videos']
            
            content_counts[platform] = content_count
            metrics['total_content_pieces'] += content_count
        
        if engagement_rates:
            metrics['average_engagement_rate'] = sum(engagement_rates) / len(engagement_rates)
        
        # Best performing platform
        if engagement_rates and platform_data:
            platforms = list(platform_data.keys())
            best_platform_index = engagement_rates.index(max(engagement_rates))
            metrics['best_performing_platform'] = platforms[best_platform_index]
        
        # Platform distribution
        total_followers = sum(
            data.get('followers', data.get('subscribers', 0)) 
            for data in platform_data.values()
        )
        
        if total_followers > 0:
            for platform, data in platform_data.items():
                follower_count = data.get('followers', data.get('subscribers', 0))
                metrics['platform_distribution'][platform] = {
                    'percentage': (follower_count / total_followers) * 100,
                    'follower_count': follower_count
                }
        
        return metrics


class InsightGenerator:
    """AI-powered insights and recommendations generator"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
    
    async def generate_performance_insights(self, aggregated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance insights from aggregated data"""
        insights = []
        
        # Engagement insight
        avg_engagement = aggregated_data.get('cross_platform_metrics', {}).get('average_engagement_rate', 0)
        if avg_engagement > 10:
            insights.append({
                'type': 'positive_trend',
                'title': 'Excellent Engagement Performance',
                'description': f'Your {avg_engagement:.1f}% engagement rate is above industry average',
                'priority': 'low',
                'actionable': False
            })
        elif avg_engagement < 5:
            insights.append({
                'type': 'improvement_opportunity',
                'title': 'Boost Engagement Rate',
                'description': 'Consider more interactive content to improve engagement',
                'priority': 'high',
                'actionable': True,
                'recommendations': [
                    'Post questions in captions',
                    'Use polls and interactive stickers',
                    'Respond to comments quickly'
                ]
            })
        
        # Platform performance insight
        best_platform = aggregated_data.get('cross_platform_metrics', {}).get('best_performing_platform')
        if best_platform:
            insights.append({
                'type': 'optimization',
                'title': f'{best_platform.title()} is Your Top Performer',
                'description': f'Focus more content creation efforts on {best_platform}',
                'priority': 'medium',
                'actionable': True,
                'recommendations': [
                    f'Increase posting frequency on {best_platform}',
                    f'Adapt successful {best_platform} content to other platforms'
                ]
            })
        
        # Content volume insight
        total_content = aggregated_data.get('cross_platform_metrics', {}).get('total_content_pieces', 0)
        if total_content < 50:
            insights.append({
                'type': 'growth_opportunity',
                'title': 'Increase Content Volume',
                'description': 'More consistent posting could boost your reach',
                'priority': 'medium',
                'actionable': True,
                'recommendations': [
                    'Create a content calendar',
                    'Batch create content',
                    'Repurpose content across platforms'
                ]
            })
        
        return insights
    
    async def generate_growth_predictions(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate growth predictions based on historical data"""
        # Mock growth predictions
        return {
            'predicted_follower_growth': {
                '30_days': 8.5,
                '90_days': 28.2,
                '1_year': 156.7
            },
            'predicted_engagement_trend': {
                'direction': 'upward',
                'confidence': 87.3,
                'expected_change': '+2.1%'
            },
            'revenue_forecast': {
                '30_days': 3200,
                '90_days': 10800,
                '1_year': 52000
            },
            'confidence_score': 84.2,
            'generated_at': datetime.utcnow().isoformat()
        }


class AnalyticsAggregator:
    """
    Main analytics aggregator system
    
    Orchestrates multi-platform data collection, aggregation, analysis,
    and insight generation to provide creators with comprehensive analytics.
    """
    
    def __init__(self, profile_manager: CreatorProfileManager, cache_manager: CacheManager):
        self.profile_manager = profile_manager
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize components
        self.platform_connector = PlatformConnector(cache_manager)
        self.data_aggregator = DataAggregator(self.platform_connector, cache_manager)
        self.insight_generator = InsightGenerator(cache_manager)
    
    async def get_comprehensive_analytics(self, creator_id: str, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY) -> Dict[str, Any]:
        """
        Get comprehensive analytics for creator
        
        Args:
            creator_id: Creator identifier
            timeframe: Analytics timeframe
            
        Returns:
            Complete analytics dashboard data
        """



        try:
            # Get creator profile
            profile = await self.profile_manager.get_creator_profile(creator_id)
            if not profile:
                raise ValueError("Creator not found")
            
            # Aggregate cross-platform data
            aggregated_data = await self.data_aggregator.aggregate_cross_platform_metrics(
                creator_id, timeframe
            )
            
            # Generate insights
            insights = await self.insight_generator.generate_performance_insights(aggregated_data)
            
            # Generate predictions
            predictions = await self.insight_generator.generate_growth_predictions(aggregated_data)
            
            # Get trending metrics
            trending_metrics = await self._get_trending_metrics(creator_id)
            
            return {
                'creator_id': creator_id,
                'timeframe': timeframe.value,
                'summary_metrics': {
                    'total_followers': aggregated_data['total_followers'],
                    'average_engagement_rate': aggregated_data['cross_platform_metrics']['average_engagement_rate'],
                    'total_content_pieces': aggregated_data['cross_platform_metrics']['total_content_pieces'],
                    'best_performing_platform': aggregated_data['cross_platform_metrics']['best_performing_platform']
                },
                'platform_breakdown': aggregated_data['platform_breakdown'],
                'cross_platform_metrics': aggregated_data['cross_platform_metrics'],
                'performance_insights': insights,
                'growth_predictions': predictions,
                'trending_metrics': trending_metrics,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive analytics failed for creator {creator_id}: {e}")
            raise
    
    async def _get_trending_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get trending metrics and comparisons"""



        return {
            'engagement_trend': {
                'direction': 'up',
                'change_percentage': 15.7,
                'period': 'vs_last_month'
            },
            'follower_growth_trend': {
                'direction': 'up',
                'change_percentage': 12.3,
                'period': 'vs_last_month'
            },
            'content_performance_trend': {
                'direction': 'stable',
                'change_percentage': 2.1,
                'period': 'vs_last_month'
            },
            'top_performing_content': [
                {
                    'content_id': 'content_001',
                    'title': 'Tech Review: Latest Smartphone',
                    'platform': 'youtube',
                    'views': 25000,
                    'engagement_rate': 12.5
                }
            ]
        }
    
    async def export_analytics_data(self, creator_id: str, format_type: str = "json") -> Dict[str, Any]:
        """Export analytics data in specified format"""



        try:
            # Get comprehensive analytics
            analytics_data = await self.get_comprehensive_analytics(creator_id)
            
            if format_type.lower() == "json":
                return {
                    'export_id': f"export_{creator_id}_{datetime.utcnow().timestamp()}",
                    'format': format_type,
                    'data': analytics_data,
                    'exported_at': datetime.utcnow().isoformat()
                }
            elif format_type.lower() == "csv":
                # Mock CSV export preparation
                return {
                    'export_id': f"export_{creator_id}_{datetime.utcnow().timestamp()}",
                    'format': format_type,
                    'download_url': f"/exports/analytics_{creator_id}.csv",
                    'exported_at': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"Analytics export failed for creator {creator_id}: {e}")
            raise


# Export classes
__all__ = [
    'AnalyticsAggregator',
    'PlatformConnector',
    'DataAggregator',
    'InsightGenerator'
]
