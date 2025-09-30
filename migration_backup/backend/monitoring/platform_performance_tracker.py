"""🌐 Platform Performance Tracker - IA Influencer Agent Platform
================================================================

Multi-platform performance tracking system providing real-time analytics
across all social media and content platforms with optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Content Distribution → Platform Tracking → Performance Analysis → Cross-Platform Optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for performance tracking"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    BEHANCE = "behance"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class ContentFormat(Enum):
    """Content formats across platforms"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"
    ARTICLE = "article"


class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SAVES = "saves"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    VIEWS = "views"
    FOLLOWERS = "followers"
    REVENUE = "revenue"


@dataclass
class PlatformMetrics:
    """Performance metrics for a specific platform"""
    platform: Platform
    content_id: str
    creator_id: str
    
    # Basic engagement metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    clicks: int = 0
    
    # Reach and impressions
    reach: int = 0
    impressions: int = 0
    unique_viewers: int = 0
    
    # Growth metrics
    followers_gained: int = 0
    followers_lost: int = 0
    net_follower_growth: int = 0
    
    # Platform-specific metrics
    platform_specific_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Revenue metrics
    revenue_generated: Decimal = Decimal('0')
    monetization_rate: float = 0.0
    
    # Performance ratios
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Time-based data
    post_timestamp: Optional[datetime] = None
    measurement_timestamp: datetime = field(default_factory=datetime.now)
    measurement_period: str = "24h"  # 1h, 24h, 7d, 30d
    
    # Platform algorithm insights
    algorithm_score: float = 0.0
    viral_potential: float = 0.0
    discoverability_score: float = 0.0
    
    # Audience insights
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_engagement_quality: float = 0.0
    
    # Optimization data
    optimal_posting_time: Optional[str] = None
    hashtag_performance: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CrossPlatformAnalytics:
    """Cross-platform analytics and insights"""
    creator_id: str
    content_id: str
    analysis_period: str
    
    # Platform performance comparison
    platform_performances: Dict[Platform, PlatformMetrics] = field(default_factory=dict)
    
    # Cross-platform metrics
    total_reach: int = 0
    total_engagement: int = 0
    total_revenue: Decimal = Decimal('0')
    
    # Platform efficiency metrics
    platform_efficiency_scores: Dict[Platform, float] = field(default_factory=dict)
    best_performing_platform: Optional[Platform] = None
    worst_performing_platform: Optional[Platform] = None
    
    # Content format performance across platforms
    format_platform_performance: Dict[ContentFormat, Dict[Platform, float]] = field(default_factory=dict)
    
    # Optimization opportunities
    cross_platform_opportunities: List[str] = field(default_factory=list)
    platform_specific_recommendations: Dict[Platform, List[str]] = field(default_factory=dict)
    
    # Synchronization insights
    optimal_posting_schedule: Dict[Platform, List[str]] = field(default_factory=dict)
    content_adaptation_suggestions: Dict[Platform, List[str]] = field(default_factory=dict)
    
    # ROI analysis
    platform_roi: Dict[Platform, float] = field(default_factory=dict)
    cost_per_engagement: Dict[Platform, Decimal] = field(default_factory=dict)
    
    # Growth trajectory
    growth_predictions: Dict[Platform, Dict[str, float]] = field(default_factory=dict)
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0


class PlatformPerformanceTracker:
    """
    Multi-Platform Performance Tracker
    
    Comprehensive tracking and analytics system for monitoring content performance
    across all major social media and content platforms with cross-platform optimization.
    """
    
    def __init__(self):
        self.platform_metrics: Dict[str, Dict[Platform, PlatformMetrics]] = defaultdict(dict)
        self.cross_platform_analytics: Dict[str, List[CrossPlatformAnalytics]] = defaultdict(list)
        self.platform_benchmarks: Dict[Platform, Dict[str, float]] = defaultdict(dict)
        
        # Platform-specific configurations
        self.platform_configs = self._initialize_platform_configs()
        self.optimization_strategies = self._initialize_optimization_strategies()
        self.api_integrations = self._initialize_api_integrations()
        
        # Tracking configuration
        self.tracking_config = {
            "update_frequency_minutes": 15,  # Real-time updates every 15 minutes
            "batch_analysis_hours": 6,       # Batch analysis every 6 hours
            "trend_analysis_days": 7,        # Trend analysis over 7 days
            "benchmark_update_days": 30      # Update benchmarks monthly
        }
        
        logger.info("🌐 Platform Performance Tracker initialized")
    
    def _initialize_platform_configs(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            Platform.INSTAGRAM: {
                "content_formats": [ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.STORY, ContentFormat.REEL],
                "key_metrics": ["likes", "comments", "shares", "saves", "reach", "impressions"],
                "optimal_posting_times": ["09:00", "12:00", "17:00", "19:00"],
                "hashtag_limit": 30,
                "algorithm_factors": ["engagement_rate", "save_rate", "comment_quality", "story_completion"],
                "revenue_streams": ["sponsored_posts", "affiliate", "shopping", "reels_play_bonus"]
            },
            Platform.TIKTOK: {
                "content_formats": [ContentFormat.SHORT, ContentFormat.LIVE_STREAM],
                "key_metrics": ["views", "likes", "shares", "comments", "completion_rate"],
                "optimal_posting_times": ["06:00", "10:00", "14:00", "18:00", "22:00"],
                "hashtag_limit": 100,
                "algorithm_factors": ["completion_rate", "like_rate", "share_rate", "user_interaction"],
                "revenue_streams": ["creator_fund", "live_gifts", "brand_partnerships"]
            },
            Platform.YOUTUBE: {
                "content_formats": [ContentFormat.VIDEO, ContentFormat.SHORT, ContentFormat.LIVE_STREAM],
                "key_metrics": ["views", "watch_time", "subscribers", "likes", "comments", "shares"],
                "optimal_posting_times": ["14:00", "15:00", "16:00", "17:00"],
                "algorithm_factors": ["watch_time", "click_through_rate", "session_duration", "subscriber_growth"],
                "revenue_streams": ["ad_revenue", "channel_memberships", "super_chat", "merchandise"]
            },
            Platform.FACEBOOK: {
                "content_formats": [ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.TEXT, ContentFormat.LIVE_STREAM],
                "key_metrics": ["likes", "comments", "shares", "reach", "page_views"],
                "optimal_posting_times": ["09:00", "13:00", "15:00"],
                "algorithm_factors": ["meaningful_interactions", "time_spent", "completion_rate"],
                "revenue_streams": ["ad_breaks", "fan_subscriptions", "stars"]
            },
            Platform.TWITTER: {
                "content_formats": [ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO],
                "key_metrics": ["likes", "retweets", "comments", "impressions", "profile_visits"],
                "optimal_posting_times": ["08:00", "12:00", "17:00", "19:00"],
                "hashtag_limit": 2,
                "algorithm_factors": ["engagement_rate", "recency", "relevance", "user_relationship"],
                "revenue_streams": ["super_follows", "tip_jar", "spaces_monetization"]
            },
            Platform.LINKEDIN: {
                "content_formats": [ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.ARTICLE],
                "key_metrics": ["likes", "comments", "shares", "views", "clicks"],
                "optimal_posting_times": ["07:00", "08:00", "12:00", "17:00"],
                "algorithm_factors": ["professional_relevance", "engagement_quality", "network_activity"],
                "revenue_streams": ["newsletter", "course_sales", "consulting"]
            },
            Platform.SPOTIFY: {
                "content_formats": [ContentFormat.AUDIO, ContentFormat.PODCAST],
                "key_metrics": ["streams", "monthly_listeners", "playlist_adds", "completion_rate"],
                "algorithm_factors": ["completion_rate", "skip_rate", "playlist_performance", "user_saves"],
                "revenue_streams": ["streaming_royalties", "podcast_ads", "fan_funding"]
            },
            Platform.MEDIUM: {
                "content_formats": [ContentFormat.ARTICLE],
                "key_metrics": ["views", "reads", "claps", "comments", "highlights"],
                "optimal_posting_times": ["07:00", "19:00", "21:00"],
                "algorithm_factors": ["read_time", "engagement_depth", "topic_relevance"],
                "revenue_streams": ["partner_program", "membership", "publications"]
            }
        }
    
    def _initialize_optimization_strategies(self) -> Dict[Platform, List[str]]:
        """Initialize platform-specific optimization strategies"""
        return {
            Platform.INSTAGRAM: [
                "Use high-quality visuals with consistent aesthetic",
                "Optimize hashtag mix (trending + niche + branded)",
                "Post during peak audience activity times",
                "Create engaging stories with interactive elements",
                "Collaborate with other creators for cross-promotion"
            ],
            Platform.TIKTOK: [
                "Hook viewers in first 3 seconds",
                "Use trending sounds and hashtags",
                "Create content that encourages completion",
                "Engage authentically with comments",
                "Post consistently during peak hours"
            ],
            Platform.YOUTUBE: [
                "Optimize thumbnails and titles for CTR",
                "Focus on watch time and session duration",
                "Create compelling video descriptions",
                "Use end screens and cards effectively",
                "Build consistent upload schedule"
            ],
            Platform.TWITTER: [
                "Tweet during high-engagement periods",
                "Use 1-2 relevant hashtags maximum",
                "Engage in real-time conversations",
                "Share timely and relevant content",
                "Retweet and engage with community"
            ],
            Platform.LINKEDIN: [
                "Share professional insights and expertise",
                "Use native video for higher engagement",
                "Post during business hours",
                "Engage meaningfully in comments",
                "Share industry-relevant content"
            ]
        }
    
    def _initialize_api_integrations(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize API integration configurations"""
        return {
            Platform.INSTAGRAM: {
                "api_version": "v18.0",
                "endpoints": ["insights", "media", "user"],
                "rate_limits": {"requests_per_hour": 200},
                "required_permissions": ["instagram_basic", "instagram_manage_insights"]
            },
            Platform.YOUTUBE: {
                "api_version": "v3",
                "endpoints": ["analytics", "videos", "channels"],
                "rate_limits": {"quota_per_day": 10000},
                "required_permissions": ["youtube.readonly", "youtube.analytics.readonly"]
            },
            Platform.TIKTOK: {
                "api_version": "v1",
                "endpoints": ["video.list", "video.insights"],
                "rate_limits": {"requests_per_day": 1000},
                "required_permissions": ["video.insights", "user.info.basic"]
            }
            # Additional platform API configs would be added here
        }
    
    async def track_platform_performance(
        self,
        content_id: str,
        creator_id: str,
        platform: Platform,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Track performance metrics for content on specific platform"""
        try:
            # Create or update platform metrics
            if content_id not in self.platform_metrics:
                self.platform_metrics[content_id] = {}
            
            if platform not in self.platform_metrics[content_id]:
                self.platform_metrics[content_id][platform] = PlatformMetrics(
                    platform=platform,
                    content_id=content_id,
                    creator_id=creator_id
                )
            
            metrics = self.platform_metrics[content_id][platform]
            
            # Update metrics with new data
            for field_name, value in performance_data.items():
                if hasattr(metrics, field_name):
                    setattr(metrics, field_name, value)
            
            # Calculate derived metrics
            await self._calculate_derived_metrics(metrics)
            
            # Update platform-specific metrics
            await self._update_platform_specific_metrics(metrics, performance_data)
            
            # Calculate algorithm and optimization scores
            await self._calculate_algorithm_scores(metrics)
            
            # Generate optimization insights
            await self._generate_platform_optimization_insights(metrics)
            
            metrics.measurement_timestamp = datetime.now()
            
            logger.info(f"✅ Platform performance tracked: {content_id} on {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track platform performance: {e}")
            return False
    
    async def _calculate_derived_metrics(self, metrics: PlatformMetrics):
        """Calculate derived performance metrics"""
        try:
            # Calculate engagement rate
            if metrics.impressions > 0:
                total_engagement = metrics.likes + metrics.comments + metrics.shares + metrics.saves
                metrics.engagement_rate = total_engagement / metrics.impressions
            elif metrics.views > 0:
                total_engagement = metrics.likes + metrics.comments + metrics.shares
                metrics.engagement_rate = total_engagement / metrics.views
            
            # Calculate click-through rate
            if metrics.impressions > 0 and metrics.clicks > 0:
                metrics.click_through_rate = metrics.clicks / metrics.impressions
            
            # Calculate conversion rate (if revenue data available)
            if metrics.clicks > 0 and metrics.revenue_generated > 0:
                metrics.conversion_rate = float(metrics.revenue_generated) / metrics.clicks
            
            # Calculate net follower growth
            metrics.net_follower_growth = metrics.followers_gained - metrics.followers_lost
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate derived metrics: {e}")
    
    async def _update_platform_specific_metrics(
        self,
        metrics: PlatformMetrics,
        performance_data: Dict[str, Any]
    ):
        """Update platform-specific metrics"""
        try:
            platform_config = self.platform_configs.get(metrics.platform, {})
            
            if metrics.platform == Platform.INSTAGRAM:
                metrics.platform_specific_metrics.update({
                    "story_completion_rate": performance_data.get("story_completion_rate", 0.0),
                    "save_rate": metrics.saves / max(1, metrics.views),
                    "profile_visits": performance_data.get("profile_visits", 0),
                    "website_clicks": performance_data.get("website_clicks", 0)
                })
            
            elif metrics.platform == Platform.TIKTOK:
                metrics.platform_specific_metrics.update({
                    "completion_rate": performance_data.get("completion_rate", 0.0),
                    "average_watch_time": performance_data.get("average_watch_time", 0.0),
                    "profile_view_rate": performance_data.get("profile_view_rate", 0.0),
                    "duet_count": performance_data.get("duet_count", 0)
                })
            
            elif metrics.platform == Platform.YOUTUBE:
                metrics.platform_specific_metrics.update({
                    "watch_time_minutes": performance_data.get("watch_time_minutes", 0),
                    "average_view_duration": performance_data.get("average_view_duration", 0.0),
                    "subscriber_growth": performance_data.get("subscriber_growth", 0),
                    "thumbnail_ctr": performance_data.get("thumbnail_ctr", 0.0)
                })
            
            elif metrics.platform == Platform.TWITTER:
                metrics.platform_specific_metrics.update({
                    "retweet_rate": performance_data.get("retweets", 0) / max(1, metrics.impressions),
                    "quote_tweets": performance_data.get("quote_tweets", 0),
                    "url_clicks": performance_data.get("url_clicks", 0),
                    "hashtag_clicks": performance_data.get("hashtag_clicks", 0)
                })
            
            elif metrics.platform == Platform.LINKEDIN:
                metrics.platform_specific_metrics.update({
                    "connection_requests": performance_data.get("connection_requests", 0),
                    "company_page_clicks": performance_data.get("company_page_clicks", 0),
                    "job_inquiries": performance_data.get("job_inquiries", 0),
                    "article_reads": performance_data.get("article_reads", 0)
                })
        
        except Exception as e:
            logger.error(f"❌ Failed to update platform-specific metrics: {e}")
    
    async def _calculate_algorithm_scores(self, metrics: PlatformMetrics):
        """Calculate platform algorithm and optimization scores"""
        try:
            platform_config = self.platform_configs.get(metrics.platform, {})
            algorithm_factors = platform_config.get("algorithm_factors", [])
            
            algorithm_score = 0.0
            
            if metrics.platform == Platform.INSTAGRAM:
                # Instagram algorithm factors
                engagement_score = min(1.0, metrics.engagement_rate * 20)  # Normalize to 0-1
                save_rate = metrics.platform_specific_metrics.get("save_rate", 0.0)
                save_score = min(1.0, save_rate * 10)
                
                algorithm_score = (engagement_score * 0.4 + save_score * 0.3 + 
                                 metrics.click_through_rate * 0.3)
            
            elif metrics.platform == Platform.TIKTOK:
                # TikTok algorithm factors
                completion_rate = metrics.platform_specific_metrics.get("completion_rate", 0.0)
                like_rate = metrics.likes / max(1, metrics.views)
                share_rate = metrics.shares / max(1, metrics.views)
                
                algorithm_score = (completion_rate * 0.5 + like_rate * 10 * 0.3 + 
                                 share_rate * 20 * 0.2)
            
            elif metrics.platform == Platform.YOUTUBE:
                # YouTube algorithm factors
                watch_time = metrics.platform_specific_metrics.get("watch_time_minutes", 0)
                ctr = metrics.platform_specific_metrics.get("thumbnail_ctr", 0.0)
                
                watch_time_score = min(1.0, watch_time / 1000)  # Normalize to 1000 minutes
                ctr_score = min(1.0, ctr * 10)  # Normalize CTR
                
                algorithm_score = (watch_time_score * 0.6 + ctr_score * 0.4)
            
            else:
                # Generic algorithm score based on engagement
                algorithm_score = min(1.0, metrics.engagement_rate * 15)
            
            metrics.algorithm_score = max(0.0, min(1.0, algorithm_score))
            
            # Calculate viral potential
            metrics.viral_potential = await self._calculate_viral_potential(metrics)
            
            # Calculate discoverability score
            metrics.discoverability_score = await self._calculate_discoverability_score(metrics)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate algorithm scores: {e}")
    
    async def _calculate_viral_potential(self, metrics: PlatformMetrics) -> float:
        """Calculate viral potential score"""
        try:
            # Viral potential based on share rate and growth velocity
            share_rate = metrics.shares / max(1, metrics.views)
            engagement_velocity = metrics.engagement_rate * 100  # Normalize
            
            # Platform-specific viral factors
            if metrics.platform == Platform.TIKTOK:
                completion_rate = metrics.platform_specific_metrics.get("completion_rate", 0.0)
                viral_score = (share_rate * 20 + completion_rate + engagement_velocity) / 3
            elif metrics.platform == Platform.TWITTER:
                retweet_rate = metrics.platform_specific_metrics.get("retweet_rate", 0.0)
                viral_score = (retweet_rate * 15 + engagement_velocity) / 2
            else:
                viral_score = (share_rate * 15 + engagement_velocity) / 2
            
            return min(1.0, viral_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate viral potential: {e}")
            return 0.0
    
    async def _calculate_discoverability_score(self, metrics: PlatformMetrics) -> float:
        """Calculate content discoverability score"""
        try:
            # Discoverability based on reach vs impressions and hashtag performance
            reach_rate = metrics.reach / max(1, metrics.impressions)
            hashtag_effectiveness = statistics.mean(metrics.hashtag_performance.values()) if metrics.hashtag_performance else 0.5
            
            discoverability = (reach_rate + hashtag_effectiveness + metrics.algorithm_score) / 3
            
            return min(1.0, discoverability)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate discoverability score: {e}")
            return 0.5
    
    async def _generate_platform_optimization_insights(self, metrics: PlatformMetrics):
        """Generate platform-specific optimization insights"""
        try:
            optimization_strategies = self.optimization_strategies.get(metrics.platform, [])
            
            # Update optimal posting time based on performance
            current_hour = metrics.post_timestamp.hour if metrics.post_timestamp else 12
            
            # Simple heuristic: if engagement is high, this might be an optimal time
            if metrics.engagement_rate > 0.05:  # 5% threshold
                metrics.optimal_posting_time = f"{current_hour:02d}:00"
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization insights: {e}")
    
    async def analyze_cross_platform_performance(
        self,
        creator_id: str,
        content_id: str,
        analysis_period: str = "7d"
    ) -> CrossPlatformAnalytics:
        """Analyze performance across all platforms for specific content"""
        try:
            analytics = CrossPlatformAnalytics(
                creator_id=creator_id,
                content_id=content_id,
                analysis_period=analysis_period
            )
            
            # Get platform metrics for this content
            content_metrics = self.platform_metrics.get(content_id, {})
            
            if not content_metrics:
                logger.warning(f"No platform metrics found for content {content_id}")
                return analytics
            
            analytics.platform_performances = content_metrics.copy()
            
            # Calculate cross-platform totals
            analytics.total_reach = sum(m.reach for m in content_metrics.values())
            analytics.total_engagement = sum(
                m.likes + m.comments + m.shares + m.saves for m in content_metrics.values()
            )
            analytics.total_revenue = sum(m.revenue_generated for m in content_metrics.values())
            
            # Calculate platform efficiency scores
            for platform, metrics in content_metrics.items():
                efficiency = (metrics.engagement_rate * 0.4 + 
                            metrics.algorithm_score * 0.3 + 
                            metrics.discoverability_score * 0.3)
                analytics.platform_efficiency_scores[platform] = efficiency
            
            # Identify best and worst performing platforms
            if analytics.platform_efficiency_scores:
                analytics.best_performing_platform = max(
                    analytics.platform_efficiency_scores,
                    key=analytics.platform_efficiency_scores.get
                )
                analytics.worst_performing_platform = min(
                    analytics.platform_efficiency_scores,
                    key=analytics.platform_efficiency_scores.get
                )
            
            # Generate cross-platform opportunities
            analytics.cross_platform_opportunities = await self._identify_cross_platform_opportunities(analytics)
            
            # Generate platform-specific recommendations
            analytics.platform_specific_recommendations = await self._generate_platform_recommendations(analytics)
            
            # Calculate ROI for each platform
            for platform, metrics in content_metrics.items():
                if metrics.revenue_generated > 0:
                    # Simple ROI calculation (would need cost data for accurate calculation)
                    analytics.platform_roi[platform] = float(metrics.revenue_generated) / max(1, metrics.impressions) * 1000
                
                # Cost per engagement (estimated)
                total_engagement = metrics.likes + metrics.comments + metrics.shares
                if total_engagement > 0:
                    analytics.cost_per_engagement[platform] = Decimal('0.01')  # Placeholder cost
            
            # Store analytics
            self.cross_platform_analytics[content_id].append(analytics)
            
            logger.info(f"✅ Cross-platform analysis completed for {content_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze cross-platform performance: {e}")
            return CrossPlatformAnalytics(creator_id=creator_id, content_id=content_id, analysis_period=analysis_period)
    
    async def _identify_cross_platform_opportunities(self, analytics: CrossPlatformAnalytics) -> List[str]:
        """Identify cross-platform optimization opportunities"""
        opportunities = []
        
        try:
            platform_scores = analytics.platform_efficiency_scores
            
            # Identify underperforming platforms
            if platform_scores:
                avg_score = statistics.mean(platform_scores.values())
                underperforming = [
                    platform for platform, score in platform_scores.items()
                    if score < avg_score * 0.8
                ]
                
                if underperforming:
                    opportunities.append(f"Optimize content for underperforming platforms: {', '.join(p.value for p in underperforming)}")
            
            # Check for missing platforms
            active_platforms = set(analytics.platform_performances.keys())
            major_platforms = {Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE, Platform.TWITTER}
            missing_platforms = major_platforms - active_platforms
            
            if missing_platforms:
                opportunities.append(f"Expand to missing major platforms: {', '.join(p.value for p in missing_platforms)}")
            
            # Cross-promotion opportunities
            if len(active_platforms) > 1:
                opportunities.append("Create cross-platform content series to leverage audience across platforms")
                opportunities.append("Use platform-specific features to drive traffic between platforms")
            
            # Content format optimization
            best_platform = analytics.best_performing_platform
            if best_platform:
                best_formats = self.platform_configs.get(best_platform, {}).get("content_formats", [])
                opportunities.append(f"Adapt content to formats that work well on {best_platform.value}: {', '.join(f.value for f in best_formats)}")
        
        except Exception as e:
            logger.error(f"❌ Failed to identify cross-platform opportunities: {e}")
        
        return opportunities
    
    async def _generate_platform_recommendations(self, analytics: CrossPlatformAnalytics) -> Dict[Platform, List[str]]:
        """Generate platform-specific recommendations"""
        recommendations = {}
        
        try:
            for platform, metrics in analytics.platform_performances.items():
                platform_recs = []
                
                # Engagement optimization
                if metrics.engagement_rate < 0.03:  # 3% threshold
                    platform_recs.append("Improve content engagement through interactive elements and community building")
                
                # Algorithm optimization
                if metrics.algorithm_score < 0.6:
                    platform_strategies = self.optimization_strategies.get(platform, [])
                    platform_recs.extend(platform_strategies[:2])  # Top 2 strategies
                
                # Discoverability optimization
                if metrics.discoverability_score < 0.5:
                    platform_recs.append("Optimize hashtags, keywords, and posting times for better discoverability")
                
                # Platform-specific recommendations
                if platform == Platform.INSTAGRAM:
                    if metrics.platform_specific_metrics.get("save_rate", 0) < 0.02:
                        platform_recs.append("Create more saveable content like tutorials, quotes, or infographics")
                
                elif platform == Platform.TIKTOK:
                    completion_rate = metrics.platform_specific_metrics.get("completion_rate", 0)
                    if completion_rate < 0.7:
                        platform_recs.append("Improve video completion rate with stronger hooks and pacing")
                
                elif platform == Platform.YOUTUBE:
                    watch_time = metrics.platform_specific_metrics.get("watch_time_minutes", 0)
                    if watch_time < 100:
                        platform_recs.append("Focus on increasing watch time through better content retention strategies")
                
                recommendations[platform] = platform_recs
        
        except Exception as e:
            logger.error(f"❌ Failed to generate platform recommendations: {e}")
        
        return recommendations
    
    async def get_platform_performance_summary(
        self,
        creator_id: str,
        platform: Platform,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get performance summary for creator on specific platform"""
        try:
            # Get all content for this creator on this platform
            creator_content = []
            for content_id, platform_metrics in self.platform_metrics.items():
                if platform in platform_metrics and platform_metrics[platform].creator_id == creator_id:
                    metrics = platform_metrics[platform]
                    # Filter by time period
                    days_ago = (datetime.now() - metrics.measurement_timestamp).days
                    if days_ago <= period_days:
                        creator_content.append(metrics)
            
            if not creator_content:
                return {"error": f"No content found for creator {creator_id} on {platform.value}"}
            
            # Calculate summary metrics
            total_views = sum(m.views for m in creator_content)
            total_engagement = sum(m.likes + m.comments + m.shares + m.saves for m in creator_content)
            avg_engagement_rate = statistics.mean(m.engagement_rate for m in creator_content)
            total_revenue = sum(m.revenue_generated for m in creator_content)
            avg_algorithm_score = statistics.mean(m.algorithm_score for m in creator_content)
            
            # Growth metrics
            follower_growth = sum(m.net_follower_growth for m in creator_content)
            
            # Top performing content
            top_content = max(creator_content, key=lambda x: x.engagement_rate)
            
            return {
                "platform": platform.value,
                "creator_id": creator_id,
                "period_days": period_days,
                "total_content_pieces": len(creator_content),
                "total_views": total_views,
                "total_engagement": total_engagement,
                "average_engagement_rate": avg_engagement_rate,
                "total_revenue": float(total_revenue),
                "follower_growth": follower_growth,
                "average_algorithm_score": avg_algorithm_score,
                "top_performing_content": {
                    "content_id": top_content.content_id,
                    "engagement_rate": top_content.engagement_rate,
                    "views": top_content.views
                },
                "platform_specific_insights": await self._get_platform_specific_insights(platform, creator_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get platform performance summary: {e}")
            return {"error": str(e)}
    
    async def _get_platform_specific_insights(
        self,
        platform: Platform,
        content_metrics: List[PlatformMetrics]
    ) -> Dict[str, Any]:
        """Get platform-specific insights and recommendations"""
        insights = {}
        
        try:
            if platform == Platform.INSTAGRAM:
                avg_save_rate = statistics.mean(
                    m.platform_specific_metrics.get("save_rate", 0) for m in content_metrics
                )
                insights["average_save_rate"] = avg_save_rate
                insights["story_performance"] = "data_needed"  # Would calculate from story metrics
                
            elif platform == Platform.TIKTOK:
                avg_completion_rate = statistics.mean(
                    m.platform_specific_metrics.get("completion_rate", 0) for m in content_metrics
                )
                insights["average_completion_rate"] = avg_completion_rate
                insights["viral_potential"] = statistics.mean(m.viral_potential for m in content_metrics)
                
            elif platform == Platform.YOUTUBE:
                total_watch_time = sum(
                    m.platform_specific_metrics.get("watch_time_minutes", 0) for m in content_metrics
                )
                insights["total_watch_time_hours"] = total_watch_time / 60
                insights["average_ctr"] = statistics.mean(
                    m.platform_specific_metrics.get("thumbnail_ctr", 0) for m in content_metrics
                )
        
        except Exception as e:
            logger.error(f"❌ Failed to get platform-specific insights: {e}")
        
        return insights
    
    async def get_cross_platform_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive cross-platform performance dashboard"""
        try:
            dashboard = {
                "creator_id": creator_id,
                "timestamp": datetime.now().isoformat(),
                "platform_overview": {},
                "total_metrics": {
                    "total_followers": 0,
                    "total_content": 0,
                    "total_engagement": 0,
                    "total_revenue": 0.0
                },
                "platform_rankings": [],
                "optimization_priorities": [],
                "growth_opportunities": []
            }
            
            # Get metrics for all platforms for this creator
            platform_summaries = {}
            for platform in Platform:
                summary = await self.get_platform_performance_summary(creator_id, platform, 30)
                if "error" not in summary:
                    platform_summaries[platform] = summary
                    dashboard["platform_overview"][platform.value] = summary
            
            if not platform_summaries:
                return {"error": f"No platform data found for creator {creator_id}"}
            
            # Calculate total metrics
            dashboard["total_metrics"]["total_content"] = sum(
                s["total_content_pieces"] for s in platform_summaries.values()
            )
            dashboard["total_metrics"]["total_engagement"] = sum(
                s["total_engagement"] for s in platform_summaries.values()
            )
            dashboard["total_metrics"]["total_revenue"] = sum(
                s["total_revenue"] for s in platform_summaries.values()
            )
            
            # Platform rankings by engagement rate
            platform_rankings = [
                {"platform": platform.value, "engagement_rate": summary["average_engagement_rate"]}
                for platform, summary in platform_summaries.items()
            ]
            platform_rankings.sort(key=lambda x: x["engagement_rate"], reverse=True)
            dashboard["platform_rankings"] = platform_rankings
            
            # Optimization priorities
            for platform, summary in platform_summaries.items():
                if summary["average_engagement_rate"] < 0.03:
                    dashboard["optimization_priorities"].append(
                        f"Improve engagement on {platform.value} (currently {summary['average_engagement_rate']:.3f})"
                    )
            
            # Growth opportunities
            active_platforms = set(platform_summaries.keys())
            major_platforms = {Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE, Platform.TWITTER}
            missing_platforms = major_platforms - active_platforms
            
            if missing_platforms:
                dashboard["growth_opportunities"].append(
                    f"Expand to: {', '.join(p.value for p in missing_platforms)}"
                )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Failed to generate cross-platform dashboard: {e}")
            return {"error": str(e)}


# Global instance for easy access
platform_performance_tracker = PlatformPerformanceTracker()

# Convenience functions
async def track_platform_performance(content_id: str, creator_id: str, platform: Platform, performance_data: Dict[str, Any]) -> bool:
    """Track platform performance - convenience function"""
    return await platform_performance_tracker.track_platform_performance(content_id, creator_id, platform, performance_data)

async def analyze_cross_platform_performance(creator_id: str, content_id: str, analysis_period: str = "7d") -> CrossPlatformAnalytics:
    """Analyze cross-platform performance - convenience function"""
    return await platform_performance_tracker.analyze_cross_platform_performance(creator_id, content_id, analysis_period)

async def get_platform_performance_summary(creator_id: str, platform: Platform, period_days: int = 30) -> Dict[str, Any]:
    """Get platform performance summary - convenience function"""
    return await platform_performance_tracker.get_platform_performance_summary(creator_id, platform, period_days)

async def get_cross_platform_dashboard(creator_id: str) -> Dict[str, Any]:
    """Get cross-platform dashboard - convenience function"""
    return await platform_performance_tracker.get_cross_platform_dashboard(creator_id)