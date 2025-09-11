"""Distribution Metrics and Platform Analytics
Content distribution tracking and platform-specific performance analytics.

This module provides comprehensive distribution analytics including platform reach,
content performance across channels, and distribution optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"

class DistributionStatus(Enum):
    """Distribution operation status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"
    RESTRICTED = "restricted"

@dataclass
class DistributionRecord:
    """Single content distribution record"""
    distribution_id: str
    content_id: str
    platform: PlatformType
    upload_time: datetime
    
    # Content details
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Distribution settings
    visibility: str = "public"  # public, private, unlisted
    monetization_enabled: bool = False
    content_type: str = "video"  # video, audio, image, text
    
    # Performance metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    
    # Platform-specific metrics
    platform_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Distribution metadata
    status: DistributionStatus = DistributionStatus.PENDING
    platform_url: Optional[str] = None
    platform_id: Optional[str] = None
    
    # Revenue tracking
    revenue: float = 0.0
    impressions: int = 0
    cpm: float = 0.0  # Cost per mille
    
    # Last update info
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.views > 0:
            total_engagement = self.likes + self.shares + self.comments
            return (total_engagement / self.views) * 100
        return 0.0

@dataclass
class PlatformAnalytics:
    """Platform-specific analytics"""
    platform: PlatformType
    analysis_period: Tuple[datetime, datetime]
    
    # Volume metrics
    total_content: int = 0
    active_content: int = 0
    
    # Performance metrics
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    
    # Engagement metrics
    average_engagement_rate: float = 0.0
    best_performing_content: Optional[str] = None
    worst_performing_content: Optional[str] = None
    
    # Revenue metrics
    total_revenue: float = 0.0
    average_cpm: float = 0.0
    monetized_content_count: int = 0
    
    # Content performance distribution
    performance_tiers: Dict[str, int] = field(default_factory=dict)  # high, medium, low
    
    # Growth metrics
    growth_rate: float = 0.0
    viral_content_count: int = 0
    
    # Platform insights
    optimal_posting_times: List[int] = field(default_factory=list)  # Hours of day
    top_performing_categories: List[str] = field(default_factory=list)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReachMetrics:
    """Cross-platform reach analytics"""
    analysis_period: Tuple[datetime, datetime]
    
    # Overall reach
    total_unique_reach: int = 0
    total_impressions: int = 0
    average_frequency: float = 0.0  # Average times content seen per user
    
    # Platform breakdown
    platform_reach: Dict[str, int] = field(default_factory=dict)
    platform_share: Dict[str, float] = field(default_factory=dict)
    
    # Content reach
    top_reaching_content: List[Tuple[str, int]] = field(default_factory=list)
    reach_by_content_type: Dict[str, int] = field(default_factory=dict)
    
    # Demographic reach
    reach_by_age_group: Dict[str, int] = field(default_factory=dict)
    reach_by_location: Dict[str, int] = field(default_factory=dict)
    reach_by_device: Dict[str, int] = field(default_factory=dict)
    
    # Cross-platform insights
    platform_overlap: Dict[str, float] = field(default_factory=dict)
    cross_platform_engagement: float = 0.0
    
    # Virality metrics
    viral_coefficient: float = 0.0  # How much content spreads organically
    viral_content_percentage: float = 0.0


class DistributionTracker:
    """Main distribution tracking system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.distribution_records: Dict[str, DistributionRecord] = {}
        self.platform_cache: Dict[PlatformType, List[DistributionRecord]] = defaultdict(list)
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=10000)
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
    def _initialize_platform_configs(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            PlatformType.YOUTUBE: {
                'api_endpoint': 'https://www.googleapis.com/youtube/v3',
                'max_title_length': 100,
                'max_description_length': 5000,
                'supports_monetization': True,
                'content_types': ['video'],
                'optimal_aspect_ratios': ['16:9', '9:16'],
                'recommended_upload_times': [14, 15, 16, 17, 18, 19, 20]
            },
            PlatformType.INSTAGRAM: {
                'api_endpoint': 'https://graph.instagram.com',
                'max_title_length': 125,
                'max_description_length': 2200,
                'supports_monetization': True,
                'content_types': ['image', 'video'],
                'optimal_aspect_ratios': ['1:1', '4:5', '9:16'],
                'recommended_upload_times': [11, 12, 13, 17, 18, 19]
            },
            PlatformType.TIKTOK: {
                'api_endpoint': 'https://open-api.tiktok.com',
                'max_title_length': 150,
                'max_description_length': 150,
                'supports_monetization': True,
                'content_types': ['video'],
                'optimal_aspect_ratios': ['9:16'],
                'recommended_upload_times': [9, 12, 19, 21, 22]
            }
            # Add more platform configurations as needed
        }
    
    async def track_distribution(self, distribution_data: Dict[str, Any]) -> str:
        """Start tracking a content distribution"""
        try:
            record = DistributionRecord(
                distribution_id=distribution_data['distribution_id'],
                content_id=distribution_data['content_id'],
                platform=PlatformType(distribution_data['platform']),
                upload_time=datetime.now(),
                title=distribution_data.get('title'),
                description=distribution_data.get('description'),
                tags=distribution_data.get('tags', []),
                category=distribution_data.get('category'),
                visibility=distribution_data.get('visibility', 'public'),
                monetization_enabled=distribution_data.get('monetization_enabled', False),
                content_type=distribution_data.get('content_type', 'video')
            )
            
            # Store record
            self.distribution_records[record.distribution_id] = record
            self.platform_cache[record.platform].append(record)
            
            self.logger.info(f"Started tracking distribution {record.distribution_id} on {record.platform.value}")
            return record.distribution_id
            
        except Exception as e:
            self.logger.error(f"Failed to track distribution: {e}")
            raise
    
    async def update_distribution_metrics(self, distribution_id: str, metrics: Dict[str, Any]):
        """Update distribution performance metrics"""
        try:
            if distribution_id not in self.distribution_records:
                self.logger.warning(f"Distribution {distribution_id} not found")
                return
            
            record = self.distribution_records[distribution_id]
            
            # Update basic metrics
            if 'views' in metrics:
                record.views = metrics['views']
            if 'likes' in metrics:
                record.likes = metrics['likes']
            if 'shares' in metrics:
                record.shares = metrics['shares']
            if 'comments' in metrics:
                record.comments = metrics['comments']
            if 'downloads' in metrics:
                record.downloads = metrics['downloads']
            
            # Update revenue metrics
            if 'revenue' in metrics:
                record.revenue = metrics['revenue']
            if 'impressions' in metrics:
                record.impressions = metrics['impressions']
            if 'cpm' in metrics:
                record.cpm = metrics['cpm']
            
            # Update platform-specific metrics
            if 'platform_metrics' in metrics:
                record.platform_metrics.update(metrics['platform_metrics'])
            
            # Update status
            if 'status' in metrics:
                record.status = DistributionStatus(metrics['status'])
            
            # Update platform identifiers
            if 'platform_url' in metrics:
                record.platform_url = metrics['platform_url']
            if 'platform_id' in metrics:
                record.platform_id = metrics['platform_id']
            
            record.last_updated = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Failed to update distribution metrics: {e}")
    
    async def get_platform_analytics(self, platform: PlatformType,
                                   period_days: int = 30) -> PlatformAnalytics:
        """Get comprehensive platform analytics"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Filter records for this platform and period
            platform_records = [
                record for record in self.platform_cache[platform]
                if start_time <= record.upload_time <= end_time
            ]
            
            analytics = PlatformAnalytics(
                platform=platform,
                analysis_period=(start_time, end_time)
            )
            
            if not platform_records:
                return analytics
            
            # Calculate metrics
            await self._calculate_platform_volume_metrics(platform_records, analytics)
            await self._calculate_platform_performance_metrics(platform_records, analytics)
            await self._calculate_platform_engagement_metrics(platform_records, analytics)
            await self._calculate_platform_revenue_metrics(platform_records, analytics)
            await self._calculate_platform_insights(platform_records, analytics)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Platform analytics calculation failed: {e}")
            return PlatformAnalytics(platform=platform, analysis_period=(start_time, end_time))
    
    async def _calculate_platform_volume_metrics(self, records: List[DistributionRecord],
                                               analytics: PlatformAnalytics):
        """Calculate platform volume metrics"""
        try:
            analytics.total_content = len(records)
            analytics.active_content = sum(
                1 for record in records
                if record.status == DistributionStatus.PUBLISHED
            )
            
        except Exception as e:
            self.logger.error(f"Platform volume metrics calculation failed: {e}")
    
    async def _calculate_platform_performance_metrics(self, records: List[DistributionRecord],
                                                     analytics: PlatformAnalytics):
        """Calculate platform performance metrics"""
        try:
            published_records = [r for r in records if r.status == DistributionStatus.PUBLISHED]
            
            if published_records:
                analytics.total_views = sum(r.views for r in published_records)
                analytics.total_likes = sum(r.likes for r in published_records)
                analytics.total_shares = sum(r.shares for r in published_records)
                analytics.total_comments = sum(r.comments for r in published_records)
                
                # Find best and worst performing content
                if published_records:
                    best_record = max(published_records, key=lambda r: r.views)
                    worst_record = min(published_records, key=lambda r: r.views)
                    
                    analytics.best_performing_content = best_record.content_id
                    analytics.worst_performing_content = worst_record.content_id
            
        except Exception as e:
            self.logger.error(f"Platform performance metrics calculation failed: {e}")
    
    async def _calculate_platform_engagement_metrics(self, records: List[DistributionRecord],
                                                   analytics: PlatformAnalytics):
        """Calculate platform engagement metrics"""
        try:
            published_records = [r for r in records if r.status == DistributionStatus.PUBLISHED]
            
            if published_records:
                engagement_rates = [r.calculate_engagement_rate() for r in published_records]
                analytics.average_engagement_rate = np.mean(engagement_rates)
                
                # Categorize content performance
                high_threshold = np.percentile(engagement_rates, 75) if engagement_rates else 0
                low_threshold = np.percentile(engagement_rates, 25) if engagement_rates else 0
                
                high_performers = sum(1 for rate in engagement_rates if rate >= high_threshold)
                low_performers = sum(1 for rate in engagement_rates if rate <= low_threshold)
                medium_performers = len(engagement_rates) - high_performers - low_performers
                
                analytics.performance_tiers = {
                    'high': high_performers,
                    'medium': medium_performers,
                    'low': low_performers
                }
                
                # Count viral content (top 10% by engagement)
                viral_threshold = np.percentile(engagement_rates, 90) if engagement_rates else 0
                analytics.viral_content_count = sum(1 for rate in engagement_rates if rate >= viral_threshold)
            
        except Exception as e:
            self.logger.error(f"Platform engagement metrics calculation failed: {e}")
    
    async def _calculate_platform_revenue_metrics(self, records: List[DistributionRecord],
                                                analytics: PlatformAnalytics):
        """Calculate platform revenue metrics"""
        try:
            monetized_records = [r for r in records if r.monetization_enabled and r.revenue > 0]
            
            if monetized_records:
                analytics.total_revenue = sum(r.revenue for r in monetized_records)
                analytics.monetized_content_count = len(monetized_records)
                
                # Calculate average CPM
                cpm_values = [r.cpm for r in monetized_records if r.cpm > 0]
                if cpm_values:
                    analytics.average_cpm = np.mean(cpm_values)
            
        except Exception as e:
            self.logger.error(f"Platform revenue metrics calculation failed: {e}")
    
    async def _calculate_platform_insights(self, records: List[DistributionRecord],
                                         analytics: PlatformAnalytics):
        """Calculate platform insights and optimization recommendations"""
        try:
            published_records = [r for r in records if r.status == DistributionStatus.PUBLISHED]
            
            if not published_records:
                return
            
            # Analyze optimal posting times
            posting_hours = [r.upload_time.hour for r in published_records]
            hour_performance = defaultdict(list)
            
            for record in published_records:
                hour = record.upload_time.hour
                hour_performance[hour].append(record.calculate_engagement_rate())
            
            # Find hours with best average performance
            hour_averages = {
                hour: np.mean(rates) 
                for hour, rates in hour_performance.items()
                if rates
            }
            
            sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)
            analytics.optimal_posting_times = [hour for hour, avg in sorted_hours[:5]]
            
            # Analyze top performing categories
            category_performance = defaultdict(list)
            
            for record in published_records:
                if record.category:
                    category_performance[record.category].append(record.calculate_engagement_rate())
            
            category_averages = {
                category: np.mean(rates)
                for category, rates in category_performance.items()
                if rates
            }
            
            sorted_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
            analytics.top_performing_categories = [category for category, avg in sorted_categories[:5]]
            
            # Calculate growth rate (simplified)
            if len(published_records) >= 2:
                recent_records = [r for r in published_records if r.upload_time >= datetime.now() - timedelta(days=7)]
                older_records = [r for r in published_records if r.upload_time < datetime.now() - timedelta(days=7)]
                
                if older_records:
                    recent_avg_views = np.mean([r.views for r in recent_records]) if recent_records else 0
                    older_avg_views = np.mean([r.views for r in older_records])
                    
                    if older_avg_views > 0:
                        analytics.growth_rate = ((recent_avg_views - older_avg_views) / older_avg_views) * 100
            
        except Exception as e:
            self.logger.error(f"Platform insights calculation failed: {e}")


class PlatformAnalytics:
    """Platform-specific analytics and optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def compare_platform_performance(self, platforms: List[PlatformType],
                                         period_days: int = 30) -> Dict[str, Any]:
        """Compare performance across multiple platforms"""
        try:
            comparison = {
                'platforms': [],
                'best_performing_platform': None,
                'total_reach': 0,
                'platform_rankings': {},
                'cross_platform_insights': []
            }
            
            platform_analytics = {}
            
            # Get analytics for each platform
            for platform in platforms:
                # This would integrate with DistributionTracker
                # For now, using placeholder data
                analytics = await self._get_platform_analytics_placeholder(platform, period_days)
                platform_analytics[platform] = analytics
            
            # Calculate total reach
            total_views = sum(analytics.get('total_views', 0) for analytics in platform_analytics.values())
            comparison['total_reach'] = total_views
            
            # Rank platforms by performance
            platform_scores = {}
            for platform, analytics in platform_analytics.items():
                score = self._calculate_platform_score(analytics)
                platform_scores[platform] = score
            
            # Sort by score
            sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
            comparison['platform_rankings'] = {
                platform.value: {'rank': i+1, 'score': score}
                for i, (platform, score) in enumerate(sorted_platforms)
            }
            
            if sorted_platforms:
                comparison['best_performing_platform'] = sorted_platforms[0][0].value
            
            # Generate cross-platform insights
            comparison['cross_platform_insights'] = self._generate_cross_platform_insights(platform_analytics)
            
            # Add detailed platform data
            comparison['platforms'] = [
                {
                    'platform': platform.value,
                    'analytics': analytics
                }
                for platform, analytics in platform_analytics.items()
            ]
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Platform comparison failed: {e}")
            return {}
    
    async def _get_platform_analytics_placeholder(self, platform: PlatformType, period_days: int) -> Dict[str, Any]:
        """Placeholder for platform analytics"""
        # This would integrate with actual analytics data
        return {
            'total_views': np.random.randint(1000, 100000),
            'total_likes': np.random.randint(100, 10000),
            'total_shares': np.random.randint(50, 5000),
            'total_comments': np.random.randint(20, 2000),
            'engagement_rate': np.random.uniform(2.0, 15.0),
            'revenue': np.random.uniform(100, 10000)
        }
    
    def _calculate_platform_score(self, analytics: Dict[str, Any]) -> float:
        """Calculate overall platform performance score"""
        try:
            # Normalize metrics and calculate weighted score
            factors = [
                min(analytics.get('total_views', 0) / 100000, 1.0) * 0.3,      # 30% weight for reach
                min(analytics.get('engagement_rate', 0) / 10.0, 1.0) * 0.4,   # 40% weight for engagement
                min(analytics.get('revenue', 0) / 5000, 1.0) * 0.3             # 30% weight for revenue
            ]
            
            return sum(factors)
            
        except Exception as e:
            self.logger.error(f"Platform score calculation failed: {e}")
            return 0.0
    
    def _generate_cross_platform_insights(self, platform_analytics: Dict[PlatformType, Dict[str, Any]]) -> List[str]:
        """Generate insights across platforms"""
        insights = []
        
        try:
            # Find best performing metrics across platforms
            best_engagement_platform = max(
                platform_analytics.items(),
                key=lambda x: x[1].get('engagement_rate', 0),
                default=(None, {})
            )
            
            if best_engagement_platform[0]:
                insights.append(
                    f"{best_engagement_platform[0].value} has the highest engagement rate at "
                    f"{best_engagement_platform[1].get('engagement_rate', 0):.1f}%"
                )
            
            # Find best revenue platform
            best_revenue_platform = max(
                platform_analytics.items(),
                key=lambda x: x[1].get('revenue', 0),
                default=(None, {})
            )
            
            if best_revenue_platform[0]:
                insights.append(
                    f"{best_revenue_platform[0].value} generates the highest revenue at "
                    f"${best_revenue_platform[1].get('revenue', 0):.2f}"
                )
            
            # Calculate diversity score
            engagement_rates = [analytics.get('engagement_rate', 0) for analytics in platform_analytics.values()]
            if engagement_rates:
                diversity_score = np.std(engagement_rates) / np.mean(engagement_rates) if np.mean(engagement_rates) > 0 else 0
                
                if diversity_score > 0.5:
                    insights.append("High variation in engagement across platforms - consider optimizing content strategy")
                else:
                    insights.append("Consistent engagement across platforms - content strategy is well-aligned")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Cross-platform insights generation failed: {e}")
            return []


class ReachAnalyzer:
    """Cross-platform reach analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def calculate_cross_platform_reach(self, distributions: List[DistributionRecord],
                                           period_days: int = 30) -> ReachMetrics:
        """Calculate comprehensive reach metrics across platforms"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Filter distributions for period
            period_distributions = [
                dist for dist in distributions
                if start_time <= dist.upload_time <= end_time
            ]
            
            metrics = ReachMetrics(analysis_period=(start_time, end_time))
            
            if not period_distributions:
                return metrics
            
            # Calculate metrics
            await self._calculate_total_reach(period_distributions, metrics)
            await self._calculate_platform_breakdown(period_distributions, metrics)
            await self._calculate_content_reach(period_distributions, metrics)
            await self._calculate_virality_metrics(period_distributions, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Cross-platform reach calculation failed: {e}")
            return ReachMetrics(analysis_period=(start_time, end_time))
    
    async def _calculate_total_reach(self, distributions: List[DistributionRecord],
                                   metrics: ReachMetrics):
        """Calculate total reach metrics"""
        try:
            # Sum unique reach (simplified - assumes no overlap)
            metrics.total_unique_reach = sum(dist.views for dist in distributions)
            metrics.total_impressions = sum(dist.impressions for dist in distributions)
            
            if metrics.total_unique_reach > 0:
                metrics.average_frequency = metrics.total_impressions / metrics.total_unique_reach
            
        except Exception as e:
            self.logger.error(f"Total reach calculation failed: {e}")
    
    async def _calculate_platform_breakdown(self, distributions: List[DistributionRecord],
                                          metrics: ReachMetrics):
        """Calculate platform-specific reach breakdown"""
        try:
            platform_reach = defaultdict(int)
            
            for dist in distributions:
                platform_reach[dist.platform.value] += dist.views
            
            metrics.platform_reach = dict(platform_reach)
            
            # Calculate platform share
            total_reach = sum(platform_reach.values())
            if total_reach > 0:
                metrics.platform_share = {
                    platform: (reach / total_reach) * 100
                    for platform, reach in platform_reach.items()
                }
            
        except Exception as e:
            self.logger.error(f"Platform breakdown calculation failed: {e}")
    
    async def _calculate_content_reach(self, distributions: List[DistributionRecord],
                                     metrics: ReachMetrics):
        """Calculate content-specific reach metrics"""
        try:
            # Top reaching content
            sorted_by_reach = sorted(distributions, key=lambda d: d.views, reverse=True)
            metrics.top_reaching_content = [
                (dist.content_id, dist.views) for dist in sorted_by_reach[:10]
            ]
            
            # Reach by content type
            content_type_reach = defaultdict(int)
            for dist in distributions:
                content_type_reach[dist.content_type] += dist.views
            
            metrics.reach_by_content_type = dict(content_type_reach)
            
        except Exception as e:
            self.logger.error(f"Content reach calculation failed: {e}")
    
    async def _calculate_virality_metrics(self, distributions: List[DistributionRecord],
                                        metrics: ReachMetrics):
        """Calculate virality and sharing metrics"""
        try:
            total_shares = sum(dist.shares for dist in distributions)
            total_views = sum(dist.views for dist in distributions)
            
            if total_views > 0:
                metrics.viral_coefficient = total_shares / total_views
            
            # Count viral content (top 10% by shares/views ratio)
            share_ratios = [
                dist.shares / max(dist.views, 1) for dist in distributions
            ]
            
            if share_ratios:
                viral_threshold = np.percentile(share_ratios, 90)
                viral_count = sum(1 for ratio in share_ratios if ratio >= viral_threshold)
                metrics.viral_content_percentage = (viral_count / len(distributions)) * 100
            
        except Exception as e:
            self.logger.error(f"Virality metrics calculation failed: {e}")