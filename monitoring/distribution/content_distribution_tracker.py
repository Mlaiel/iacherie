"""
Content Distribution Tracker - Distribution Module
=================================================

Intelligent content distribution tracking system for the Ainflue platform.
Monitors content flow across platforms, tracks engagement metrics, and 
provides distribution optimization insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class ContentStatus(Enum):
    """Content distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    FAILED = "failed"
    EXPIRED = "expired"
    REMOVED = "removed"

class ContentType(Enum):
    """Types of content being distributed"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"
    LIVE_STREAM = "live_stream"

class EngagementMetric(Enum):
    """Engagement tracking metrics"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    DOWNLOADS = "downloads"
    SAVES = "saves"
    CLICK_THROUGH = "click_through"

@dataclass
class ContentDistribution:
    """Individual content distribution tracking"""
    distribution_id: str
    content_id: str
    content_type: ContentType
    title: str
    creator_id: str
    source_platform: str
    target_platforms: List[str]
    status: ContentStatus
    created_at: datetime
    distributed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_urls: Dict[str, str] = field(default_factory=dict)
    file_size_mb: float = 0.0
    duration_seconds: Optional[float] = None

@dataclass 
class EngagementData:
    """Engagement metrics for distributed content"""
    content_id: str
    platform: str
    metric_type: EngagementMetric
    value: int
    timestamp: datetime
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionAnalytics:
    """Analytics for content distribution performance"""
    content_id: str
    total_reach: int
    total_engagement: int
    platform_performance: Dict[str, Dict[str, Any]]
    best_performing_platform: str
    engagement_rate: float
    viral_coefficient: float
    conversion_metrics: Dict[str, float]
    calculated_at: datetime = field(default_factory=datetime.utcnow)

class ContentDistributionTracker:
    """
    Advanced content distribution tracking and analytics system.
    
    Provides comprehensive monitoring of content across platforms,
    engagement tracking, performance analytics, and optimization insights.
    """
    
    def __init__(self) -> None:
        self.distributions: Dict[str, ContentDistribution] = {}
        self.engagement_data: List[EngagementData] = []
        self.analytics_cache: Dict[str, DistributionAnalytics] = {}
        self.platform_capabilities: Dict[str, Dict[str, Any]] = {}
        self.distribution_rules: Dict[str, Any] = {}
        self._initialize_platform_capabilities()
        self._initialize_distribution_rules()
        logger.info("Content Distribution Tracker initialized")
    
    def _initialize_platform_capabilities(self) -> None:
        """Initialize platform-specific capabilities and limits"""
        self.platform_capabilities = {
            'youtube': {
                'max_file_size_mb': 256000,  # 256 GB
                'supported_formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                'max_duration_hours': 12,
                'supports_live': True,
                'monetization': True,
                'analytics_detail': 'high'
            },
            'tiktok': {
                'max_file_size_mb': 287,  # 287 MB
                'supported_formats': ['mp4', 'mov'],
                'max_duration_seconds': 600,  # 10 minutes
                'supports_live': True,
                'monetization': True,
                'analytics_detail': 'medium'
            },
            'instagram': {
                'max_file_size_mb': 100,
                'supported_formats': ['mp4', 'mov', 'jpg', 'png'],
                'max_duration_seconds': 3600,  # 1 hour for IGTV
                'supports_live': True,
                'monetization': True,
                'analytics_detail': 'high'
            },
            'spotify': {
                'max_file_size_mb': 650,  # Estimate
                'supported_formats': ['mp3', 'wav', 'flac'],
                'max_duration_hours': 24,
                'supports_live': False,
                'monetization': True,
                'analytics_detail': 'high'
            },
            'soundcloud': {
                'max_file_size_mb': 100,  # Free tier
                'supported_formats': ['mp3', 'wav', 'flac', 'aiff'],
                'max_duration_hours': 6,
                'supports_live': False,
                'monetization': True,
                'analytics_detail': 'medium'
            }
        }
    
    def _initialize_distribution_rules(self) -> None:
        """Initialize content distribution rules"""
        self.distribution_rules = {
            'auto_optimize_format': True,
            'auto_resize_content': True,
            'respect_platform_limits': True,
            'schedule_optimal_times': True,
            'cross_platform_tagging': True,
            'audience_targeting': True
        }
    
    async def register_content_distribution(self, content_id: str, content_type: ContentType,
                                           title: str, creator_id: str, source_platform: str,
                                           target_platforms: List[str], 
                                           metadata: Optional[Dict[str, Any]] = None,
                                           file_size_mb: float = 0.0,
                                           duration_seconds: Optional[float] = None) -> str:
        """
        Register new content for distribution tracking
        
        Args:
            content_id: Unique content identifier
            content_type: Type of content
            title: Content title
            creator_id: Creator identifier
            source_platform: Original platform
            target_platforms: List of distribution targets
            metadata: Additional content metadata
            file_size_mb: File size in megabytes
            duration_seconds: Content duration
            
        Returns:
            Distribution tracking ID
        """
        distribution_id = f"dist_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Validate platforms
        valid_platforms = self._validate_platform_compatibility(
            content_type, target_platforms, file_size_mb, duration_seconds
        )
        
        distribution = ContentDistribution(
            distribution_id=distribution_id,
            content_id=content_id,
            content_type=content_type,
            title=title,
            creator_id=creator_id,
            source_platform=source_platform,
            target_platforms=valid_platforms,
            status=ContentStatus.PENDING,
            created_at=datetime.utcnow(),
            metadata=metadata or {},
            file_size_mb=file_size_mb,
            duration_seconds=duration_seconds
        )
        
        self.distributions[distribution_id] = distribution
        
        # Start async distribution process
        asyncio.create_task(self._process_distribution(distribution_id))
        
        logger.info(f"Registered content distribution {distribution_id} for {len(valid_platforms)} platforms")
        return distribution_id
    
    def _validate_platform_compatibility(self, content_type: ContentType,
                                       target_platforms: List[str],
                                       file_size_mb: float,
                                       duration_seconds: Optional[float]) -> List[str]:
        """Validate platform compatibility and filter out incompatible platforms"""
        valid_platforms = []
        
        for platform in target_platforms:
            platform_caps = self.platform_capabilities.get(platform.lower())
            if not platform_caps:
                logger.warning(f"Unknown platform: {platform}")
                continue
            
            # Check file size
            if file_size_mb > platform_caps['max_file_size_mb']:
                logger.warning(f"File too large for {platform}: {file_size_mb}MB > {platform_caps['max_file_size_mb']}MB")
                continue
            
            # Check duration
            if duration_seconds:
                if 'max_duration_seconds' in platform_caps and duration_seconds > platform_caps['max_duration_seconds']:
                    logger.warning(f"Content too long for {platform}: {duration_seconds}s")
                    continue
                elif 'max_duration_hours' in platform_caps and duration_seconds > platform_caps['max_duration_hours'] * 3600:
                    logger.warning(f"Content too long for {platform}: {duration_seconds}s")
                    continue
            
            # Check content type compatibility (simplified)
            if content_type == ContentType.AUDIO and platform.lower() in ['youtube', 'tiktok', 'instagram']:
                # Audio content might need video wrapper for video platforms
                logger.info(f"Audio content for video platform {platform} - will need video wrapper")
            
            valid_platforms.append(platform)
        
        return valid_platforms
    
    async def _process_distribution(self, distribution_id -> None: str) -> None:
        """Process content distribution to platforms"""
        try:
            distribution = self.distributions[distribution_id]
            distribution.status = ContentStatus.PROCESSING
            
            platform_urls = {}
            
            # Simulate distribution to each platform
            for platform in distribution.target_platforms:
                try:
                    url = await self._distribute_to_platform(distribution, platform)
                    platform_urls[platform] = url
                    
                    # Simulate processing delay
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Failed to distribute to {platform}: {e}")
            
            # Update distribution status
            if platform_urls:
                distribution.status = ContentStatus.DISTRIBUTED
                distribution.distributed_at = datetime.utcnow()
                distribution.platform_urls = platform_urls
                
                # Start engagement tracking
                asyncio.create_task(self._start_engagement_tracking(distribution_id))
            else:
                distribution.status = ContentStatus.FAILED
            
            logger.info(f"Distribution {distribution_id} completed with status: {distribution.status}")
            
        except Exception as e:
            logger.error(f"Distribution processing failed for {distribution_id}: {e}")
            if distribution_id in self.distributions:
                self.distributions[distribution_id].status = ContentStatus.FAILED
    
    async def _distribute_to_platform(self, distribution: ContentDistribution, platform: str) -> str:
        """Simulate content distribution to specific platform"""
        # Generate realistic platform URL
        platform_base_urls = {
            'youtube': 'https://youtube.com/watch?v=',
            'tiktok': 'https://tiktok.com/@user/video/',
            'instagram': 'https://instagram.com/p/',
            'spotify': 'https://open.spotify.com/track/',
            'soundcloud': 'https://soundcloud.com/user/'
        }
        
        base_url = platform_base_urls.get(platform.lower(), f'https://{platform}.com/')
        content_hash = hash(distribution.content_id + platform) % 1000000
        return f"{base_url}{content_hash}"
    
    async def _start_engagement_tracking(self, distribution_id -> None: str) -> None:
        """Start tracking engagement for distributed content"""
        distribution = self.distributions[distribution_id]
        
        # Simulate engagement data collection over time
        for _ in range(10):  # Collect 10 data points
            await asyncio.sleep(1)  # Simulate time passing
            
            for platform in distribution.platform_urls:
                # Generate realistic engagement metrics
                engagement_metrics = self._generate_engagement_metrics(distribution.content_id, platform)
                self.engagement_data.extend(engagement_metrics)
        
        # Calculate analytics after engagement collection
        await self._calculate_distribution_analytics(distribution_id)
    
    def _generate_engagement_metrics(self, content_id: str, platform: str) -> List[EngagementData]:
        """Generate realistic engagement metrics"""
        metrics = []
        base_time = datetime.utcnow()
        
        # Generate different types of engagement
        for metric_type in EngagementMetric:
            # Simulate realistic engagement values based on platform
            platform_multipliers = {
                'youtube': {'views': 1000, 'likes': 50, 'shares': 10, 'comments': 25},
                'tiktok': {'views': 5000, 'likes': 250, 'shares': 100, 'comments': 50},
                'instagram': {'views': 2000, 'likes': 100, 'shares': 20, 'comments': 30},
                'spotify': {'views': 500, 'likes': 25, 'saves': 15},
                'soundcloud': {'views': 300, 'likes': 15, 'shares': 5, 'comments': 10}
            }
            
            multiplier = platform_multipliers.get(platform.lower(), {}).get(metric_type.value, 10)
            base_value = hash(content_id + platform + metric_type.value) % multiplier
            
            if base_value > 0:  # Only add if there's engagement
                metrics.append(EngagementData(
                    content_id=content_id,
                    platform=platform,
                    metric_type=metric_type,
                    value=base_value,
                    timestamp=base_time,
                    demographic_data={'age_group': '18-34', 'gender': 'mixed'},
                    geographic_data={'top_country': 'US', 'top_city': 'Los Angeles'}
                ))
        
        return metrics
    
    async def _calculate_distribution_analytics(self, distribution_id -> None: str) -> None:
        """Calculate comprehensive analytics for distribution"""
        distribution = self.distributions[distribution_id]
        content_id = distribution.content_id
        
        # Get all engagement data for this content
        content_engagement = [
            e for e in self.engagement_data 
            if e.content_id == content_id
        ]
        
        if not content_engagement:
            return
        
        # Calculate platform performance
        platform_performance = {}
        total_reach = 0
        total_engagement = 0
        
        for platform in distribution.platform_urls:
            platform_metrics = [e for e in content_engagement if e.platform == platform]
            
            if platform_metrics:
                platform_views = sum(e.value for e in platform_metrics if e.metric_type == EngagementMetric.VIEWS)
                platform_likes = sum(e.value for e in platform_metrics if e.metric_type == EngagementMetric.LIKES)
                platform_shares = sum(e.value for e in platform_metrics if e.metric_type == EngagementMetric.SHARES)
                platform_comments = sum(e.value for e in platform_metrics if e.metric_type == EngagementMetric.COMMENTS)
                
                platform_total_engagement = platform_likes + platform_shares + platform_comments
                engagement_rate = platform_total_engagement / platform_views if platform_views > 0 else 0
                
                platform_performance[platform] = {
                    'views': platform_views,
                    'likes': platform_likes,
                    'shares': platform_shares,
                    'comments': platform_comments,
                    'total_engagement': platform_total_engagement,
                    'engagement_rate': round(engagement_rate, 4)
                }
                
                total_reach += platform_views
                total_engagement += platform_total_engagement
        
        # Find best performing platform
        best_platform = max(
            platform_performance.keys(),
            key=lambda p: platform_performance[p]['total_engagement']
        ) if platform_performance else "none"
        
        # Calculate overall metrics
        overall_engagement_rate = total_engagement / total_reach if total_reach > 0 else 0
        viral_coefficient = total_reach / 1000  # Simplified viral coefficient
        
        # Calculate conversion metrics (simplified)
        conversion_metrics = {
            'view_to_like': total_engagement / total_reach if total_reach > 0 else 0,
            'reach_growth_rate': viral_coefficient / 100
        }
        
        analytics = DistributionAnalytics(
            content_id=content_id,
            total_reach=total_reach,
            total_engagement=total_engagement,
            platform_performance=platform_performance,
            best_performing_platform=best_platform,
            engagement_rate=round(overall_engagement_rate, 4),
            viral_coefficient=round(viral_coefficient, 2),
            conversion_metrics=conversion_metrics
        )
        
        self.analytics_cache[content_id] = analytics
        logger.info(f"Calculated analytics for content {content_id}")
    
    def get_distribution_status(self, distribution_id: str) -> Optional[ContentDistribution]:
        """Get distribution status"""
        return self.distributions.get(distribution_id)
    
    def get_content_analytics(self, content_id: str) -> Optional[DistributionAnalytics]:
        """Get analytics for specific content"""
        return self.analytics_cache.get(content_id)
    
    def get_creator_performance_summary(self, creator_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for creator"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get creator's distributions
        creator_distributions = [
            d for d in self.distributions.values()
            if d.creator_id == creator_id and d.created_at >= cutoff_time
        ]
        
        if not creator_distributions:
            return {"message": f"No distributions found for creator {creator_id} in last {days} days"}
        
        # Calculate summary metrics
        total_distributions = len(creator_distributions)
        successful_distributions = len([d for d in creator_distributions if d.status == ContentStatus.DISTRIBUTED])
        success_rate = successful_distributions / total_distributions
        
        # Get analytics for successful distributions
        creator_analytics = [
            self.analytics_cache[d.content_id] 
            for d in creator_distributions 
            if d.content_id in self.analytics_cache
        ]
        
        total_reach = sum(a.total_reach for a in creator_analytics)
        total_engagement = sum(a.total_engagement for a in creator_analytics)
        avg_engagement_rate = sum(a.engagement_rate for a in creator_analytics) / len(creator_analytics) if creator_analytics else 0
        
        # Platform breakdown
        platform_stats = {}
        for distribution in creator_distributions:
            for platform in distribution.target_platforms:
                if platform not in platform_stats:
                    platform_stats[platform] = {'distributions': 0, 'success': 0}
                platform_stats[platform]['distributions'] += 1
                if distribution.status == ContentStatus.DISTRIBUTED:
                    platform_stats[platform]['success'] += 1
        
        # Calculate success rates per platform
        for platform, stats in platform_stats.items():
            stats['success_rate'] = stats['success'] / stats['distributions']
        
        return {
            'creator_id': creator_id,
            'period_days': days,
            'summary': {
                'total_distributions': total_distributions,
                'successful_distributions': successful_distributions,
                'success_rate': round(success_rate, 4),
                'total_reach': total_reach,
                'total_engagement': total_engagement,
                'avg_engagement_rate': round(avg_engagement_rate, 4)
            },
            'platform_performance': platform_stats,
            'top_performing_content': [
                {
                    'content_id': a.content_id,
                    'total_engagement': a.total_engagement,
                    'best_platform': a.best_performing_platform
                }
                for a in sorted(creator_analytics, key=lambda x: x.total_engagement, reverse=True)[:5]
            ]
        }
    
    async def get_distribution_optimization_insights(self) -> Dict[str, Any]:
        """Get optimization insights for content distribution"""
        insights = []
        
        # Analyze platform performance
        platform_success_rates = {}
        for distribution in self.distributions.values():
            for platform in distribution.target_platforms:
                if platform not in platform_success_rates:
                    platform_success_rates[platform] = {'total': 0, 'success': 0}
                platform_success_rates[platform]['total'] += 1
                if distribution.status == ContentStatus.DISTRIBUTED:
                    platform_success_rates[platform]['success'] += 1
        
        # Calculate success rates and identify problem platforms
        for platform, stats in platform_success_rates.items():
            success_rate = stats['success'] / stats['total']
            if success_rate < 0.8:
                insights.append(f"Low success rate for {platform}: {success_rate:.2%} - investigate platform issues")
            elif success_rate > 0.95:
                insights.append(f"Excellent performance for {platform}: {success_rate:.2%} - prioritize this platform")
        
        # Analyze content type performance
        content_type_analytics = {}
        for content_id, analytics in self.analytics_cache.items():
            distribution = next((d for d in self.distributions.values() if d.content_id == content_id), None)
            if distribution:
                content_type = distribution.content_type.value
                if content_type not in content_type_analytics:
                    content_type_analytics[content_type] = []
                content_type_analytics[content_type].append(analytics.engagement_rate)
        
        # Find best performing content types
        for content_type, engagement_rates in content_type_analytics.items():
            avg_engagement = sum(engagement_rates) / len(engagement_rates)
            if avg_engagement > 0.1:  # 10% engagement rate
                insights.append(f"High engagement for {content_type} content: {avg_engagement:.2%} - focus on this type")
        
        if not insights:
            insights.append("Distribution performance is well optimized across all metrics")
        
        return {
            "optimization_insights": insights,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "total_distributions_analyzed": len(self.distributions),
            "platforms_analyzed": len(platform_success_rates)
        }

# Global tracker instance
content_distribution_tracker = ContentDistributionTracker()

# Export main components
__all__ = [
    'ContentDistributionTracker',
    'ContentDistribution',
    'EngagementData',
    'DistributionAnalytics',
    'ContentStatus',
    'ContentType',
    'EngagementMetric',
    'content_distribution_tracker'
]