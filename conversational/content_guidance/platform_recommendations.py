"""Platform Recommendations Engine - AI-Powered Multi-Platform Strategy System
=========================================================================

This module provides intelligent platform-specific recommendations and content
strategy analysis for creators across major social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.ai.ml.predictive_models import PredictiveModelEngine
from backend.analytics.platform_analytics import PlatformAnalyticsService

logger = get_logger(__name__)
settings = get_settings()


class PlatformType(Enum):
    """Supported platform types for recommendations."""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    DISCORD = "discord"
    PINTEREST = "pinterest"


class ContentFormat(Enum):
    """Content format types for platform optimization."""    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    STORY = "story"
    LIVE_STREAM = "live_stream"
    AUDIO = "audio"
    TEXT_POST = "text_post"
    ARTICLE = "article"
    REEL = "reel"


class AudienceSegment(Enum):
    """Target audience segments."""    GEN_Z = "gen_z"
    MILLENNIALS = "millennials"
    GEN_X = "gen_x"
    BOOMERS = "boomers"
    CREATORS = "creators"
    PROFESSIONALS = "professionals"
    MUSIC_LOVERS = "music_lovers"
    GAMERS = "gamers"


@dataclass
class PlatformMetrics:
    """Platform-specific performance metrics."""    platform: PlatformType
    reach: int
    engagement_rate: float
    follower_count: int
    average_views: int
    best_posting_times: List[str]
    top_content_types: List[ContentFormat]
    audience_demographics: Dict[str, Any]
    growth_rate: float
    monetization_rate: float


@dataclass
class ContentStrategy:
    """Content strategy recommendation."""    strategy_id: str
    platform: PlatformType
    content_format: ContentFormat
    posting_frequency: str
    optimal_times: List[str]
    content_pillars: List[str]
    hashtag_strategy: Dict[str, Any]
    engagement_tactics: List[str]
    expected_performance: Dict[str, float]
    priority_score: float


@dataclass
class PlatformRecommendation:
    """Platform-specific recommendation."""    platform: PlatformType
    recommendation_type: str
    title: str
    description: str
    implementation_steps: List[str]
    expected_impact: float
    difficulty_level: str
    timeframe: str
    success_metrics: List[str]
    priority: str


@dataclass
class CrossPlatformStrategy:
    """Cross-platform content strategy."""    strategy_name: str
    primary_platforms: List[PlatformType]
    content_flow: Dict[str, Any]
    content_adaptation: Dict[PlatformType, Dict[str, Any]]
    posting_schedule: Dict[str, List[str]]
    performance_kpis: Dict[str, float]
    budget_allocation: Dict[PlatformType, float]


class PlatformRecommendationEngine:
    """    Advanced AI-powered platform recommendation engine that analyzes creator
    performance across platforms and provides strategic recommendations.
    """    
    def __init__(self):
        """Initialize the platform recommendation engine."""        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.analytics_service = PlatformAnalyticsService()
        self.ml_engine = PredictiveModelEngine()
        
        # Platform characteristics and algorithms
        self.platform_characteristics = self._initialize_platform_data()
        
        # ML models for different recommendation types
        self.performance_predictor = RandomForestRegressor(n_estimators=100)
        self.audience_classifier = KMeans(n_clusters=5)
        self.scaler = StandardScaler()
        
        # Platform-specific optimization rules
        self.optimization_rules = self._load_optimization_rules()
        
        # Content format compatibility matrix
        self.format_compatibility = self._build_format_compatibility_matrix()
        
    def _initialize_platform_data(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize comprehensive platform characteristics data."""        
        return {
            PlatformType.YOUTUBE: {
                "algorithm_factors": {
                    "watch_time": 0.4,
                    "click_through_rate": 0.25,
                    "engagement_rate": 0.2,
                    "session_duration": 0.15
                },
                "optimal_content_length": {
                    "short_form": {"min": 15, "max": 60},
                    "long_form": {"min": 600, "max": 1800}
                },
                "peak_hours": ["19:00", "20:00", "21:00"],
                "audience_age_groups": {
                    "13-17": 0.15,
                    "18-24": 0.23,
                    "25-34": 0.28,
                    "35-44": 0.20,
                    "45+": 0.14
                },
                "monetization_requirements": {
                    "subscribers": 1000,
                    "watch_hours": 4000
                },
                "content_formats": [
                    ContentFormat.LONG_VIDEO,
                    ContentFormat.SHORT_VIDEO,
                    ContentFormat.LIVE_STREAM
                ]
            },
            
            PlatformType.TIKTOK: {
                "algorithm_factors": {
                    "completion_rate": 0.35,
                    "engagement_rate": 0.30,
                    "shares": 0.20,
                    "comments": 0.15
                },
                "optimal_content_length": {
                    "standard": {"min": 15, "max": 60},
                    "extended": {"min": 60, "max": 180}
                },
                "peak_hours": ["18:00", "19:00", "20:00", "21:00"],
                "audience_age_groups": {
                    "13-17": 0.32,
                    "18-24": 0.29,
                    "25-34": 0.22,
                    "35-44": 0.12,
                    "45+": 0.05
                },
                "trending_factors": ["sounds", "effects", "challenges", "hashtags"],
                "content_formats": [ContentFormat.SHORT_VIDEO, ContentFormat.LIVE_STREAM]
            },
            
            PlatformType.INSTAGRAM: {
                "algorithm_factors": {
                    "engagement_rate": 0.30,
                    "saves": 0.25,
                    "shares": 0.20,
                    "time_spent": 0.15,
                    "story_interactions": 0.10
                },
                "optimal_content_dimensions": {
                    "feed_post": {"width": 1080, "height": 1080},
                    "story": {"width": 1080, "height": 1920},
                    "reel": {"width": 1080, "height": 1920}
                },
                "peak_hours": ["11:00", "14:00", "17:00", "20:00"],
                "audience_age_groups": {
                    "13-17": 0.18,
                    "18-24": 0.31,
                    "25-34": 0.33,
                    "35-44": 0.13,
                    "45+": 0.05
                },
                "content_formats": [
                    ContentFormat.IMAGE,
                    ContentFormat.CAROUSEL,
                    ContentFormat.REEL,
                    ContentFormat.STORY,
                    ContentFormat.LIVE_STREAM
                ]
            },
            
            PlatformType.SPOTIFY: {
                "algorithm_factors": {
                    "completion_rate": 0.40,
                    "saves": 0.25,
                    "playlist_adds": 0.20,
                    "skip_rate": -0.15
                },
                "optimal_track_length": {"min": 120, "max": 300},
                "release_strategy": {
                    "frequency": "monthly",
                    "best_days": ["friday", "thursday"]
                },
                "discovery_methods": ["playlists", "radio", "search", "recommendations"],
                "content_formats": [ContentFormat.AUDIO]
            },
            
            PlatformType.TWITTER: {
                "algorithm_factors": {
                    "engagement_rate": 0.35,
                    "retweets": 0.25,
                    "replies": 0.20,
                    "recency": 0.20
                },
                "optimal_content_length": {"characters": 280, "optimal": 100},
                "peak_hours": ["9:00", "12:00", "15:00", "18:00"],
                "trending_factors": ["hashtags", "mentions", "topics"],
                "content_formats": [
                    ContentFormat.TEXT_POST,
                    ContentFormat.IMAGE,
                    ContentFormat.SHORT_VIDEO
                ]
            },
            
            PlatformType.LINKEDIN: {
                "algorithm_factors": {
                    "engagement_rate": 0.30,
                    "dwell_time": 0.25,
                    "comments": 0.25,
                    "shares": 0.20
                },
                "optimal_content_length": {"min": 150, "max": 1300},
                "peak_hours": ["8:00", "12:00", "17:00"],
                "audience_focus": "professionals",
                "content_formats": [
                    ContentFormat.ARTICLE,
                    ContentFormat.TEXT_POST,
                    ContentFormat.IMAGE,
                    ContentFormat.SHORT_VIDEO
                ]
            }
        }
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load platform-specific optimization rules."""        
        return {
            "hashtag_strategies": {
                "instagram": {
                    "optimal_count": 11,
                    "max_count": 30,
                    "mix_ratio": {"trending": 0.3, "niche": 0.4, "branded": 0.3}
                },
                "tiktok": {
                    "optimal_count": 5,
                    "max_count": 10,
                    "focus": "trending"
                },
                "twitter": {
                    "optimal_count": 2,
                    "max_count": 5,
                    "timing": "during_events"
                }
            },
            
            "posting_frequency": {
                "youtube": {"optimal": 3, "max": 7, "unit": "week"},
                "instagram": {"optimal": 1, "max": 3, "unit": "day"},
                "tiktok": {"optimal": 2, "max": 5, "unit": "day"},
                "twitter": {"optimal": 5, "max": 15, "unit": "day"},
                "linkedin": {"optimal": 2, "max": 5, "unit": "week"}
            },
            
            "content_adaptation": {
                "vertical_video": ["tiktok", "instagram_reels", "youtube_shorts"],
                "horizontal_video": ["youtube", "facebook", "linkedin"],
                "square_image": ["instagram_feed", "facebook"],
                "landscape_image": ["twitter", "linkedin"]
            }
        }
    
    def _build_format_compatibility_matrix(self) -> Dict[PlatformType, List[ContentFormat]]:
        """Build content format compatibility matrix for platforms."""        
        return {
            PlatformType.YOUTUBE: [
                ContentFormat.LONG_VIDEO,
                ContentFormat.SHORT_VIDEO,
                ContentFormat.LIVE_STREAM
            ],
            PlatformType.TIKTOK: [
                ContentFormat.SHORT_VIDEO,
                ContentFormat.LIVE_STREAM
            ],
            PlatformType.INSTAGRAM: [
                ContentFormat.IMAGE,
                ContentFormat.CAROUSEL,
                ContentFormat.REEL,
                ContentFormat.STORY,
                ContentFormat.LIVE_STREAM
            ],
            PlatformType.TWITTER: [
                ContentFormat.TEXT_POST,
                ContentFormat.IMAGE,
                ContentFormat.SHORT_VIDEO
            ],
            PlatformType.SPOTIFY: [
                ContentFormat.AUDIO
            ],
            PlatformType.LINKEDIN: [
                ContentFormat.ARTICLE,
                ContentFormat.TEXT_POST,
                ContentFormat.IMAGE,
                ContentFormat.SHORT_VIDEO
            ]
        }
    
    async def analyze_platform_performance(
        self, 
        creator_id: str, 
        platforms: List[PlatformType]
    ) -> Dict[PlatformType, PlatformMetrics]:
        """Analyze creator's performance across specified platforms."""        
        platform_performance = {}
        
        for platform in platforms:
            try:
                # Fetch platform-specific analytics
                analytics_data = await self.analytics_service.get_platform_analytics(
                    creator_id, platform.value
                )
                
                # Calculate comprehensive metrics
                metrics = await self._calculate_platform_metrics(
                    analytics_data, platform
                )
                
                platform_performance[platform] = metrics
                
            except Exception as e:
                self.logger.error(f"Failed to analyze {platform.value}: {e}")
                # Provide default metrics if analysis fails
                platform_performance[platform] = self._get_default_metrics(platform)
        
        return platform_performance
    
    async def _calculate_platform_metrics(
        self, 
        analytics_data: Dict[str, Any], 
        platform: PlatformType
    ) -> PlatformMetrics:
        """Calculate comprehensive platform metrics."""        
        # Extract key metrics from analytics data
        reach = analytics_data.get("reach", 0)
        impressions = analytics_data.get("impressions", 0)
        engagements = analytics_data.get("engagements", 0)
        followers = analytics_data.get("followers", 0)
        
        # Calculate engagement rate
        engagement_rate = (engagements / impressions) if impressions > 0 else 0.0
        
        # Calculate average views/plays
        content_count = analytics_data.get("content_count", 1)
        average_views = reach // content_count if content_count > 0 else 0
        
        # Analyze posting patterns for optimal times
        posting_history = analytics_data.get("posting_history", [])
        best_times = self._analyze_best_posting_times(posting_history)
        
        # Identify top-performing content types
        content_performance = analytics_data.get("content_performance", {})
        top_content_types = self._identify_top_content_types(content_performance)
        
        # Extract audience demographics
        demographics = analytics_data.get("demographics", {})
        
        # Calculate growth rate (last 30 days)
        growth_data = analytics_data.get("growth_history", [])
        growth_rate = self._calculate_growth_rate(growth_data)
        
        # Estimate monetization rate
        revenue_data = analytics_data.get("revenue", 0)
        monetization_rate = (revenue_data / reach) if reach > 0 else 0.0
        
        return PlatformMetrics(
            platform=platform,
            reach=reach,
            engagement_rate=engagement_rate,
            follower_count=followers,
            average_views=average_views,
            best_posting_times=best_times,
            top_content_types=top_content_types,
            audience_demographics=demographics,
            growth_rate=growth_rate,
            monetization_rate=monetization_rate
        )
    
    def _analyze_best_posting_times(self, posting_history: List[Dict[str, Any]]) -> List[str]:
        """Analyze posting history to identify optimal posting times."""        
        if not posting_history:
            return ["12:00", "18:00", "20:00"]  # Default times
        
        # Group posts by hour and calculate average engagement
        hourly_performance = {}
        
        for post in posting_history:
            post_time = post.get("timestamp", "")
            engagement = post.get("engagement", 0)
            
            if post_time:
                try:
                    hour = datetime.fromisoformat(post_time).hour
                    if hour not in hourly_performance:
                        hourly_performance[hour] = []
                    hourly_performance[hour].append(engagement)
                except:
                    continue
        
        # Calculate average engagement per hour
        hourly_averages = {}
        for hour, engagements in hourly_performance.items():
            hourly_averages[hour] = statistics.mean(engagements)
        
        # Sort and return top 3 hours
        top_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return [f"{hour:02d}:00" for hour, _ in top_hours]
    
    def _identify_top_content_types(
        self, 
        content_performance: Dict[str, Any]
    ) -> List[ContentFormat]:
        """Identify top-performing content types."""        
        if not content_performance:
            return [ContentFormat.IMAGE, ContentFormat.SHORT_VIDEO]  # Defaults
        
        # Sort content types by performance
        sorted_types = sorted(
            content_performance.items(), 
            key=lambda x: x[1].get("avg_engagement", 0), 
            reverse=True
        )
        
        top_types = []
        for content_type, _ in sorted_types[:3]:
            try:
                format_enum = ContentFormat(content_type)
                top_types.append(format_enum)
            except ValueError:
                continue
        
        return top_types
    
    def _calculate_growth_rate(self, growth_history: List[Dict[str, Any]]) -> float:
        """Calculate follower growth rate over the last 30 days."""        
        if len(growth_history) < 2:
            return 0.0
        
        # Get most recent and 30-day-ago follower counts
        current_followers = growth_history[-1].get("followers", 0)
        past_followers = growth_history[0].get("followers", 0)
        
        if past_followers == 0:
            return 0.0
        
        growth_rate = ((current_followers - past_followers) / past_followers) * 100
        
        return round(growth_rate, 2)
    
    def _get_default_metrics(self, platform: PlatformType) -> PlatformMetrics:
        """Provide default metrics when data is unavailable."""        
        default_times = self.platform_characteristics[platform].get("peak_hours", ["12:00"])
        default_formats = self.platform_characteristics[platform].get("content_formats", [ContentFormat.IMAGE])
        
        return PlatformMetrics(
            platform=platform,
            reach=0,
            engagement_rate=0.05,  # 5% default
            follower_count=0,
            average_views=0,
            best_posting_times=default_times,
            top_content_types=default_formats,
            audience_demographics={},
            growth_rate=0.0,
            monetization_rate=0.0
        )
    
    async def generate_platform_recommendations(
        self, 
        creator_id: str,
        platform_metrics: Dict[PlatformType, PlatformMetrics],
        goals: List[str]
    ) -> List[PlatformRecommendation]:
        """Generate actionable platform-specific recommendations."""        
        recommendations = []
        
        for platform, metrics in platform_metrics.items():
            # Analyze performance gaps
            platform_recs = await self._analyze_platform_gaps(platform, metrics, goals)
            recommendations.extend(platform_recs)
            
            # Content optimization recommendations
            content_recs = await self._generate_content_recommendations(platform, metrics)
            recommendations.extend(content_recs)
            
            # Growth strategy recommendations
            growth_recs = await self._generate_growth_recommendations(platform, metrics)
            recommendations.extend(growth_recs)
            
            # Monetization recommendations
            monetization_recs = await self._generate_monetization_recommendations(platform, metrics)
            recommendations.extend(monetization_recs)
        
        # Sort recommendations by priority and expected impact
        recommendations.sort(key=lambda x: (x.priority == "high", x.expected_impact), reverse=True)
        
        return recommendations[:20]  # Return top 20 recommendations
    
    async def _analyze_platform_gaps(
        self, 
        platform: PlatformType, 
        metrics: PlatformMetrics, 
        goals: List[str]
    ) -> List[PlatformRecommendation]:
        """Analyze performance gaps and generate improvement recommendations."""        
        recommendations = []
        platform_data = self.platform_characteristics[platform]
        
        # Engagement rate analysis
        if metrics.engagement_rate < 0.03:  # Less than 3%
            recommendations.append(
                PlatformRecommendation(
                    platform=platform,
                    recommendation_type="engagement",
                    title="Improve Engagement Rate",
                    description=f"Your engagement rate ({metrics.engagement_rate:.2%}) is below average. Focus on creating more interactive content.",
                    implementation_steps=[
                        "Ask questions in your captions",
                        "Create polls and interactive stories",
                        "Respond to all comments within 2 hours",
                        "Use trending hashtags relevant to your niche",
                        "Post at optimal times for your audience"
                    ],
                    expected_impact=0.7,
                    difficulty_level="medium",
                    timeframe="2-4 weeks",
                    success_metrics=["Engagement rate increase", "Comment volume growth"],
                    priority="high"
                )
            )
        
        # Posting frequency analysis
        optimal_frequency = self.optimization_rules["posting_frequency"].get(
            platform.value, {"optimal": 3, "unit": "week"}
        )
        
        recommendations.append(
            PlatformRecommendation(
                platform=platform,
                recommendation_type="frequency",
                title="Optimize Posting Frequency",
                description=f"Post {optimal_frequency['optimal']} times per {optimal_frequency['unit']} for optimal algorithm performance.",
                implementation_steps=[
                    "Create a content calendar",
                    "Batch create content for efficiency",
                    "Use scheduling tools for consistency",
                    "Monitor performance metrics weekly"
                ],
                expected_impact=0.5,
                difficulty_level="easy",
                timeframe="1-2 weeks",
                success_metrics=["Consistent posting schedule", "Reach improvement"],
                priority="medium"
            )
        )
        
        # Growth rate analysis
        if metrics.growth_rate < 5:  # Less than 5% monthly growth
            recommendations.append(
                PlatformRecommendation(
                    platform=platform,
                    recommendation_type="growth",
                    title="Accelerate Follower Growth",
                    description="Your follower growth is slower than average. Implement targeted growth strategies.",
                    implementation_steps=[
                        "Collaborate with creators in your niche",
                        "Participate in trending challenges or topics",
                        "Cross-promote on other platforms",
                        "Optimize your profile for discoverability",
                        "Create shareable, valuable content"
                    ],
                    expected_impact=0.8,
                    difficulty_level="medium",
                    timeframe="4-8 weeks",
                    success_metrics=["Follower growth rate", "Profile visits"],
                    priority="high"
                )
            )
        
        return recommendations
        self.scaler = StandardScaler()
        self.audience_clusterer = KMeans(n_clusters=8)
        
        # Load historical data and train models
        self._load_and_train_models()
        
        logger.info("Platform recommendation engine initialized successfully")
    
    def _initialize_platform_data(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific characteristics and optimization data."""        
        return {
            PlatformType.YOUTUBE: {
                'algorithm_type': 'watch_time_focused',
                'optimal_length': {'min': 8*60, 'max': 15*60},
                'peak_hours': ['18:00', '19:00', '20:00', '21:00'],
                'content_formats': [ContentFormat.LONG_VIDEO, ContentFormat.SHORT_VIDEO],
                'audience_retention_threshold': 0.5,
                'monetization_threshold': 1000,  # subscribers
                'hashtag_limit': 15,
                'description_limit': 5000,
                'title_limit': 100,
                'engagement_factors': {
                    'watch_time': 0.4,
                    'likes': 0.2,
                    'comments': 0.2,
                    'shares': 0.1,
                    'subscribers': 0.1
                }
            },
            PlatformType.INSTAGRAM: {
                'algorithm_type': 'engagement_focused',
                'optimal_length': {'reel': 30, 'story': 15, 'igtv': 60},
                'peak_hours': ['11:00', '13:00', '17:00', '19:00'],
                'content_formats': [ContentFormat.IMAGE, ContentFormat.REEL, ContentFormat.STORY, ContentFormat.CAROUSEL],
                'hashtag_limit': 30,
                'caption_limit': 2200,
                'engagement_factors': {
                    'likes': 0.3,
                    'comments': 0.25,
                    'shares': 0.2,
                    'saves': 0.15,
                    'reach': 0.1
                }
            },
            PlatformType.TIKTOK: {
                'algorithm_type': 'viral_focused',
                'optimal_length': {'min': 15, 'max': 60},
                'peak_hours': ['18:00', '19:00', '20:00', '21:00', '22:00'],
                'content_formats': [ContentFormat.SHORT_VIDEO],
                'hashtag_limit': 20,
                'caption_limit': 300,
                'engagement_factors': {
                    'completion_rate': 0.35,
                    'shares': 0.25,
                    'likes': 0.2,
                    'comments': 0.15,
                    'follows': 0.05
                }
            },
            PlatformType.SPOTIFY: {
                'algorithm_type': 'discovery_focused',
                'optimal_length': {'min': 2*60, 'max': 4*60},
                'peak_hours': ['07:00', '08:00', '17:00', '18:00', '22:00'],
                'content_formats': [ContentFormat.AUDIO],
                'genre_tags_limit': 10,
                'playlist_placement_importance': 0.6,
                'engagement_factors': {
                    'completion_rate': 0.4,
                    'saves': 0.25,
                    'playlist_adds': 0.2,
                    'shares': 0.1,
                    'follows': 0.05
                }
            },
            PlatformType.TWITTER: {
                'algorithm_type': 'real_time_focused',
                'optimal_length': {'tweet': 280, 'thread': 25},
                'peak_hours': ['12:00', '15:00', '17:00'],
                'content_formats': [ContentFormat.TEXT_POST, ContentFormat.IMAGE, ContentFormat.SHORT_VIDEO],
                'hashtag_limit': 2,
                'engagement_factors': {
                    'retweets': 0.35,
                    'likes': 0.25,
                    'replies': 0.25,
                    'clicks': 0.15
                }
            },
            PlatformType.LINKEDIN: {
                'algorithm_type': 'professional_focused',
                'optimal_length': {'post': 1300, 'article': 2000},
                'peak_hours': ['08:00', '12:00', '17:00', '18:00'],
                'content_formats': [ContentFormat.TEXT_POST, ContentFormat.ARTICLE, ContentFormat.IMAGE],
                'engagement_factors': {
                    'comments': 0.4,
                    'shares': 0.3,
                    'likes': 0.2,
                    'clicks': 0.1
                }
            }
        }
    
    def _load_and_train_models(self):
        """Load historical data and train ML models for recommendations."""        try:
            # This would load actual historical data in production
            # For now, we'll use synthetic data for model training
            
            # Generate synthetic training data
            n_samples = 10000
            features = np.random.rand(n_samples, 15)  # 15 features
            targets = np.random.rand(n_samples)  # Performance targets
            
            # Train performance predictor
            self.performance_predictor.fit(features, targets)
            
            # Train scaler
            self.scaler.fit(features)
            
            # Train audience clustering model
            audience_features = np.random.rand(5000, 10)
            self.audience_clusterer.fit(audience_features)
            
            logger.info("ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train ML models: {e}")
            # Continue with default models
    
    async def generate_platform_recommendations(
        self,
        user_id: str,
        current_platforms: List[PlatformType],
        content_types: List[ContentFormat],
        goals: List[str],
        target_audience: Optional[AudienceSegment] = None
    ) -> List[PlatformRecommendation]:
        """        Generate comprehensive platform-specific recommendations.
        
        Args:
            user_id: User identifier
            current_platforms: Platforms user is currently active on
            content_types: Types of content user creates
            goals: User's goals (growth, monetization, engagement, etc.)
            target_audience: Primary target audience segment
            
        Returns:
            List of platform-specific recommendations
        """        recommendations = []
        
        try:
            # Get current performance data
            performance_data = await self.analytics_service.get_user_performance(
                user_id, current_platforms
            )
            
            # Analyze current strategy effectiveness
            strategy_analysis = await self._analyze_current_strategy(
                performance_data, current_platforms, content_types
            )
            
            # Generate recommendations for each platform
            for platform in current_platforms:
                platform_recs = await self._generate_platform_specific_recommendations(
                    platform, performance_data.get(platform), goals, target_audience
                )
                recommendations.extend(platform_recs)
            
            # Suggest new platforms if beneficial
            new_platform_recs = await self._suggest_new_platforms(
                user_id, current_platforms, content_types, goals, target_audience
            )
            recommendations.extend(new_platform_recs)
            
            # Sort recommendations by priority and impact
            recommendations.sort(key=lambda x: (x.priority, x.expected_impact), reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate platform recommendations: {e}")
            return []
    
    async def _analyze_current_strategy(
        self,
        performance_data: Dict[PlatformType, Dict[str, Any]],
        platforms: List[PlatformType],
        content_types: List[ContentFormat]
    ) -> Dict[str, Any]:
        """Analyze effectiveness of current content strategy."""        
        analysis = {
            'overall_performance': 0.0,
            'best_performing_platform': None,
            'content_type_performance': {},
            'timing_optimization': {},
            'audience_growth_trends': {},
            'engagement_patterns': {},
            'opportunities': []
        }
        
        if not performance_data:
            return analysis
        
        # Calculate overall performance score
        platform_scores = []
        for platform, data in performance_data.items():
            if data and 'engagement_rate' in data:
                platform_scores.append(data['engagement_rate'])
        
        if platform_scores:
            analysis['overall_performance'] = statistics.mean(platform_scores)
            
            # Identify best performing platform
            best_platform = max(
                performance_data.items(),
                key=lambda x: x[1].get('engagement_rate', 0) if x[1] else 0
            )
            analysis['best_performing_platform'] = best_platform[0]
        
        # Analyze content type performance
        for platform, data in performance_data.items():
            if data and 'content_performance' in data:
                content_perf = data['content_performance']
                analysis['content_type_performance'][platform] = content_perf
        
        # Identify optimization opportunities
        opportunities = []
        
        for platform in platforms:
            platform_data = performance_data.get(platform, {})
            if not platform_data:
                continue
                
            # Check posting frequency
            posting_freq = platform_data.get('posting_frequency', 0)
            platform_chars = self.platform_characteristics.get(platform, {})
            
            if posting_freq < 3:  # Less than 3 posts per week
                opportunities.append({
                    'type': 'posting_frequency',
                    'platform': platform,
                    'description': 'Increase posting frequency for better algorithm performance',
                    'impact': 'medium'
                })
            
            # Check engagement rate
            engagement_rate = platform_data.get('engagement_rate', 0)
            if engagement_rate < 0.02:  # Less than 2% engagement
                opportunities.append({
                    'type': 'engagement',
                    'platform': platform,
                    'description': 'Improve content engagement through better hooks and CTAs',
                    'impact': 'high'
                })
        
        analysis['opportunities'] = opportunities
        return analysis
    
    async def _generate_platform_specific_recommendations(
        self,
        platform: PlatformType,
        performance_data: Optional[Dict[str, Any]],
        goals: List[str],
        target_audience: Optional[AudienceSegment]
    ) -> List[PlatformRecommendation]:
        """Generate recommendations specific to a platform."""        
        recommendations = []
        platform_chars = self.platform_characteristics.get(platform, {})
        
        if not platform_chars:
            return recommendations
        
        # Content optimization recommendations
        if not performance_data or performance_data.get('engagement_rate', 0) < 0.03:
            recommendations.append(PlatformRecommendation(
                platform=platform,
                recommendation_type='content_optimization',
                title=f'Optimize Content for {platform.value.title()}',
                description=f'Improve content quality and format optimization for better {platform.value} performance',
                implementation_steps=[
                    f'Analyze top-performing content in your niche on {platform.value}',
                    'Identify content formats with highest engagement',
                    'Optimize posting times based on audience activity',
                    'A/B test different content styles and formats'
                ],
                expected_impact=0.25,
                difficulty_level='medium',
                timeframe='2-4 weeks',
                success_metrics=['engagement_rate', 'reach', 'follower_growth'],
                priority='high'
            ))
        
        # Posting schedule optimization
        if 'growth' in goals or 'engagement' in goals:
            optimal_times = platform_chars.get('peak_hours', [])
            recommendations.append(PlatformRecommendation(
                platform=platform,
                recommendation_type='posting_schedule',
                title=f'Optimize Posting Schedule for {platform.value.title()}',
                description=f'Post during peak hours to maximize reach and engagement',
                implementation_steps=[
                    f'Schedule posts during peak hours: {", ".join(optimal_times)}',
                    'Use scheduling tools to maintain consistency',
                    'Monitor audience insights for personalized timing',
                    'Experiment with different time slots weekly'
                ],
                expected_impact=0.15,
                difficulty_level='easy',
                timeframe='1-2 weeks',
                success_metrics=['reach', 'engagement_rate'],
                priority='medium'
            ))
        
        # Monetization optimization
        if 'monetization' in goals:
            monetization_rec = await self._generate_monetization_recommendation(
                platform, performance_data
            )
            if monetization_rec:
                recommendations.append(monetization_rec)
        
        # Platform-specific advanced recommendations
        if platform == PlatformType.YOUTUBE:
            recommendations.extend(await self._generate_youtube_recommendations(
                performance_data, goals
            ))
        elif platform == PlatformType.INSTAGRAM:
            recommendations.extend(await self._generate_instagram_recommendations(
                performance_data, goals
            ))
        elif platform == PlatformType.TIKTOK:
            recommendations.extend(await self._generate_tiktok_recommendations(
                performance_data, goals
            ))
        elif platform == PlatformType.SPOTIFY:
            recommendations.extend(await self._generate_spotify_recommendations(
                performance_data, goals
            ))
        
        return recommendations
    
    async def _suggest_new_platforms(
        self,
        user_id: str,
        current_platforms: List[PlatformType],
        content_types: List[ContentFormat],
        goals: List[str],
        target_audience: Optional[AudienceSegment]
    ) -> List[PlatformRecommendation]:
        """Suggest new platforms based on user profile and goals."""        
        suggestions = []
        all_platforms = set(PlatformType)
        new_platforms = all_platforms - set(current_platforms)
        
        # Score potential platforms
        platform_scores = {}
        
        for platform in new_platforms:
            score = await self._calculate_platform_fit_score(
                platform, content_types, goals, target_audience
            )
            platform_scores[platform] = score
        
        # Get top 3 platform suggestions
        top_platforms = sorted(
            platform_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for platform, score in top_platforms:
            if score > 0.6:  # Only suggest platforms with good fit
                suggestion = PlatformRecommendation(
                    platform=platform,
                    recommendation_type='platform_expansion',
                    title=f'Expand to {platform.value.title()}',
                    description=f'Strong potential for growth on {platform.value} based on your content style',
                    implementation_steps=[
                        f'Research {platform.value} content trends in your niche',
                        f'Create {platform.value}-optimized content strategy',
                        'Set up professional profile with consistent branding',
                        'Plan cross-promotion from existing platforms'
                    ],
                    expected_impact=score * 0.5,
                    difficulty_level='medium',
                    timeframe='4-8 weeks',
                    success_metrics=['follower_growth', 'engagement_rate', 'reach'],
                    priority='medium' if score > 0.8 else 'low'
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    async def _calculate_platform_fit_score(
        self,
        platform: PlatformType,
        content_types: List[ContentFormat],
        goals: List[str],
        target_audience: Optional[AudienceSegment]
    ) -> float:
        """Calculate how well a platform fits user's profile and goals."""        
        score = 0.0
        platform_chars = self.platform_characteristics.get(platform, {})
        
        if not platform_chars:
            return 0.0
        
        # Content format compatibility
        supported_formats = platform_chars.get('content_formats', [])
        format_match = len(set(content_types) & set(supported_formats)) / len(content_types)
        score += format_match * 0.3
        
        # Goal alignment
        goal_platform_mapping = {
            'growth': {
                PlatformType.TIKTOK: 0.9,
                PlatformType.INSTAGRAM: 0.8,
                PlatformType.YOUTUBE: 0.7
            },
            'monetization': {
                PlatformType.YOUTUBE: 0.9,
                PlatformType.SPOTIFY: 0.8,
                PlatformType.INSTAGRAM: 0.7
            },
            'engagement': {
                PlatformType.INSTAGRAM: 0.9,
                PlatformType.TIKTOK: 0.8,
                PlatformType.TWITTER: 0.7
            },
            'reach': {
                PlatformType.TIKTOK: 0.9,
                PlatformType.YOUTUBE: 0.8,
                PlatformType.INSTAGRAM: 0.7
            }
        }
        
        goal_scores = []
        for goal in goals:
            if goal in goal_platform_mapping:
                platform_score = goal_platform_mapping[goal].get(platform, 0.5)
                goal_scores.append(platform_score)
        
        if goal_scores:
            score += statistics.mean(goal_scores) * 0.4
        
        # Audience alignment
        if target_audience:
            audience_platform_mapping = {
                AudienceSegment.GEN_Z: {
                    PlatformType.TIKTOK: 0.9,
                    PlatformType.INSTAGRAM: 0.8,
                    PlatformType.YOUTUBE: 0.7
                },
                AudienceSegment.MILLENNIALS: {
                    PlatformType.INSTAGRAM: 0.9,
                    PlatformType.YOUTUBE: 0.8,
                    PlatformType.SPOTIFY: 0.8
                },
                AudienceSegment.PROFESSIONALS: {
                    PlatformType.LINKEDIN: 0.9,
                    PlatformType.TWITTER: 0.7,
                    PlatformType.YOUTUBE: 0.6
                },
                AudienceSegment.MUSIC_LOVERS: {
                    PlatformType.SPOTIFY: 0.9,
                    PlatformType.YOUTUBE: 0.8,
                    PlatformType.INSTAGRAM: 0.7
                }
            }
            
            audience_score = audience_platform_mapping.get(target_audience, {}).get(platform, 0.5)
            score += audience_score * 0.3
        
        return min(1.0, score)
    
    async def _generate_youtube_recommendations(
        self,
        performance_data: Optional[Dict[str, Any]],
        goals: List[str]
    ) -> List[PlatformRecommendation]:
        """Generate YouTube-specific recommendations."""        
        recommendations = []
        
        # Watch time optimization
        if not performance_data or performance_data.get('average_watch_time', 0) < 0.4:
            recommendations.append(PlatformRecommendation(
                platform=PlatformType.YOUTUBE,
                recommendation_type='watch_time_optimization',
                title='Improve Video Retention and Watch Time',
                description='Optimize video structure and content to increase audience retention',
                implementation_steps=[
                    'Create compelling hooks in first 15 seconds',
                    'Use pattern interrupts every 30-60 seconds',
                    'Add preview of what\'s coming at the beginning',
                    'Analyze retention graphs to identify drop-off points',
                    'Use YouTube Analytics to optimize content length'
                ],
                expected_impact=0.3,
                difficulty_level='medium',
                timeframe='3-6 weeks',
                success_metrics=['average_watch_time', 'session_duration'],
                priority='high'
            ))
        
        # Thumbnail optimization
        recommendations.append(PlatformRecommendation(
            platform=PlatformType.YOUTUBE,
            recommendation_type='thumbnail_optimization',
            title='Create High-Converting Thumbnails',
            description='Design thumbnails that increase click-through rates',
            implementation_steps=[
                'A/B test different thumbnail styles',
                'Use bright colors and high contrast',
                'Include faces with clear emotions',
                'Add text overlays for context',
                'Maintain consistent branding elements'
            ],
            expected_impact=0.2,
            difficulty_level='easy',
            timeframe='1-2 weeks',
            success_metrics=['click_through_rate', 'impressions'],
            priority='medium'
        ))
        
        return recommendations
    
    async def _generate_instagram_recommendations(
        self,
        performance_data: Optional[Dict[str, Any]],
        goals: List[str]
    ) -> List[PlatformRecommendation]:
        """Generate Instagram-specific recommendations."""        
        recommendations = []
        
        # Reels strategy
        if 'growth' in goals or 'reach' in goals:
            recommendations.append(PlatformRecommendation(
                platform=PlatformType.INSTAGRAM,
                recommendation_type='reels_strategy',
                title='Optimize Instagram Reels Strategy',
                description='Leverage Reels algorithm for maximum reach and growth',
                implementation_steps=[
                    'Post 3-5 Reels per week consistently',
                    'Use trending audio and hashtags',
                    'Create vertical videos with good lighting',
                    'Add captions and text overlays',
                    'Engage with comments in first hour after posting'
                ],
                expected_impact=0.35,
                difficulty_level='medium',
                timeframe='2-4 weeks',
                success_metrics=['reach', 'reel_plays', 'follower_growth'],
                priority='high'
            ))
        
        # Hashtag strategy
        recommendations.append(PlatformRecommendation(
            platform=PlatformType.INSTAGRAM,
            recommendation_type='hashtag_strategy',
            title='Implement Strategic Hashtag Mix',
            description='Use data-driven hashtag strategy for better discoverability',
            implementation_steps=[
                'Research niche-specific hashtags with good engagement',
                'Mix popular (1M+), medium (100K-1M), and niche (10K-100K) hashtags',
                'Create branded hashtags for campaigns',
                'Track hashtag performance and adjust weekly',
                'Use 20-30 hashtags per post for maximum reach'
            ],
            expected_impact=0.2,
            difficulty_level='easy',
            timeframe='1 week',
            success_metrics=['reach', 'hashtag_impressions'],
            priority='medium'
        ))
        
        return recommendations
    
    async def _generate_tiktok_recommendations(
        self,
        performance_data: Optional[Dict[str, Any]],
        goals: List[str]
    ) -> List[PlatformRecommendation]:
        """Generate TikTok-specific recommendations."""        
        recommendations = []
        
        # Trend participation
        recommendations.append(PlatformRecommendation(
            platform=PlatformType.TIKTOK,
            recommendation_type='trend_participation',
            title='Leverage TikTok Trends and Challenges',
            description='Participate in trending content while maintaining brand voice',
            implementation_steps=[
                'Monitor trending hashtags and sounds daily',
                'Put unique spin on trending formats',
                'Post trend-based content within 24-48 hours',
                'Use trending audio but add original commentary',
                'Collaborate with other creators on trends'
            ],
            expected_impact=0.4,
            difficulty_level='medium',
            timeframe='Ongoing',
            success_metrics=['views', 'shares', 'trend_performance'],
            priority='high'
        ))
        
        # Algorithm optimization
        recommendations.append(PlatformRecommendation(
            platform=PlatformType.TIKTOK,
            recommendation_type='algorithm_optimization',
            title='Optimize for TikTok Algorithm',
            description='Create content that performs well with TikTok\'s recommendation system',
            implementation_steps=[
                'Focus on completion rate - keep viewers watching till the end',
                'Add captions for accessibility and engagement',
                'Post during peak hours (6-10 PM)',
                'Encourage comments through questions and CTAs',
                'Use 3-5 relevant hashtags including trending ones'
            ],
            expected_impact=0.3,
            difficulty_level='medium',
            timeframe='2-3 weeks',
            success_metrics=['completion_rate', 'engagement_rate', 'fyp_performance'],
            priority='high'
        ))
        
        return recommendations
    
    async def _generate_content_recommendations(
        self, 
        platform: PlatformType, 
        metrics: PlatformMetrics
    ) -> List[PlatformRecommendation]:
        """Generate content-specific recommendations for the platform."""        
        recommendations = []
        platform_data = self.platform_characteristics[platform]
        
        # Content format optimization
        if platform in [PlatformType.YOUTUBE, PlatformType.TIKTOK]:
            recommendations.append(
                PlatformRecommendation(
                    platform=platform,
                    recommendation_type="content_format",
                    title="Optimize Video Content Format",
                    description="Focus on video formats that perform best on this platform.",
                    implementation_steps=self._get_video_optimization_steps(platform),
                    expected_impact=0.6,
                    difficulty_level="medium",
                    timeframe="2-4 weeks",
                    success_metrics=["Average view duration", "Completion rate"],
                    priority="high"
                )
            )
        
        # Hashtag strategy
        if platform in [PlatformType.INSTAGRAM, PlatformType.TIKTOK, PlatformType.TWITTER]:
            hashtag_rules = self.optimization_rules["hashtag_strategies"].get(platform.value, {})
            
            recommendations.append(
                PlatformRecommendation(
                    platform=platform,
                    recommendation_type="hashtag_strategy",
                    title="Optimize Hashtag Strategy",
                    description=f"Use {hashtag_rules.get('optimal_count', 5)} hashtags for optimal reach.",
                    implementation_steps=[
                        f"Research trending hashtags in your niche",
                        f"Use {hashtag_rules.get('optimal_count', 5)} hashtags per post",
                        "Mix popular and niche-specific hashtags",
                        "Create branded hashtags for campaigns",
                        "Monitor hashtag performance weekly"
                    ],
                    expected_impact=0.4,
                    difficulty_level="easy",
                    timeframe="1-2 weeks",
                    success_metrics=["Reach increase", "Hashtag impressions"],
                    priority="medium"
                )
            )
        
        # Platform-specific content recommendations
        if platform == PlatformType.SPOTIFY:
            recommendations.extend(await self._generate_spotify_content_recommendations(metrics))
        elif platform == PlatformType.LINKEDIN:
            recommendations.extend(await self._generate_linkedin_content_recommendations(metrics))
        
        return recommendations
    
    async def _generate_monetization_recommendation(
        self,
        platform: PlatformType,
        performance_data: Optional[Dict[str, Any]]
    ) -> Optional[PlatformRecommendation]:
        """Generate platform-specific monetization recommendations."""        
        if not performance_data:
            return None
        
        followers = performance_data.get('follower_count', 0)
        engagement_rate = performance_data.get('engagement_rate', 0)
        
        # Platform-specific monetization thresholds and strategies
        monetization_strategies = {
            PlatformType.YOUTUBE: {
                'threshold': 1000,
                'strategies': ['AdSense', 'Channel Memberships', 'Super Chat', 'Brand Sponsorships']
            },
            PlatformType.INSTAGRAM: {
                'threshold': 1000,
                'strategies': ['Creator Fund', 'Brand Partnerships', 'Affiliate Marketing', 'Product Sales']
            },
            PlatformType.TIKTOK: {
                'threshold': 10000,
                'strategies': ['Creator Fund', 'Live Gifts', 'Brand Partnerships', 'Product Placement']
            },
            PlatformType.SPOTIFY: {
                'threshold': 1000,
                'strategies': ['Streaming Royalties', 'Merchandise', 'Concert Promotion', 'Brand Sync']
            }
        }
        
        platform_monetization = monetization_strategies.get(platform)
        if not platform_monetization:
            return None
        
        threshold = platform_monetization['threshold']
        strategies = platform_monetization['strategies']
        
        if followers >= threshold and engagement_rate >= 0.02:
            return PlatformRecommendation(
                platform=platform,
                recommendation_type='monetization',
                title=f'Activate Monetization on {platform.value.title()}',
                description=f'You meet the requirements for monetization on {platform.value}',
                implementation_steps=[
                    f'Apply for {platform.value} monetization programs',
                    'Set up payment and tax information',
                    f'Implement {", ".join(strategies[:2])} strategies',
                    'Track revenue and optimize high-performing content',
                    'Diversify income streams within platform'
                ],
                expected_impact=0.4,
                difficulty_level='easy',
                timeframe='2-4 weeks',
                success_metrics=['revenue', 'monetized_views', 'conversion_rate'],
                priority='high'
            )
        
        return None


class ContentStrategyAnalyzer:
    """    Advanced content strategy analyzer that evaluates and optimizes
    cross-platform content strategies for maximum impact.
    """    
    def __init__(self):
        """Initialize the content strategy analyzer."""        self.recommendation_engine = PlatformRecommendationEngine()
        self.performance_history = {}
        logger.info("Content strategy analyzer initialized")
    
    async def analyze_cross_platform_strategy(
        self,
        user_id: str,
        platforms: List[PlatformType],
        content_calendar: List[Dict[str, Any]],
        performance_goals: Dict[str, float]
    ) -> CrossPlatformStrategy:
        """        Analyze and optimize cross-platform content strategy.
        
        Args:
            user_id: User identifier
            platforms: Active platforms
            content_calendar: Planned content schedule
            performance_goals: Target performance metrics
            
        Returns:
            Optimized cross-platform strategy
        """        
        # Analyze current content distribution
        content_analysis = await self._analyze_content_distribution(
            content_calendar, platforms
        )
        
        # Optimize content flow between platforms
        optimized_flow = await self._optimize_content_flow(
            platforms, content_analysis
        )
        
        # Generate platform-specific adaptations
        adaptations = await self._generate_content_adaptations(
            platforms, content_calendar
        )
        
        # Create optimized posting schedule
        posting_schedule = await self._optimize_posting_schedule(
            platforms, content_calendar, performance_goals
        )
        
        # Calculate budget allocation
        budget_allocation = await self._calculate_budget_allocation(
            platforms, performance_goals
        )
        
        # Define performance KPIs
        kpis = await self._define_performance_kpis(
            platforms, performance_goals
        )
        
        strategy = CrossPlatformStrategy(
            strategy_name=f"Cross-Platform Strategy for {user_id}",
            primary_platforms=platforms,
            content_flow=optimized_flow,
            content_adaptation=adaptations,
            posting_schedule=posting_schedule,
            performance_kpis=kpis,
            budget_allocation=budget_allocation
        )
        
        logger.info(f"Generated cross-platform strategy for user {user_id}")
        return strategy
    
    async def _analyze_content_distribution(
        self,
        content_calendar: List[Dict[str, Any]],
        platforms: List[PlatformType]
    ) -> Dict[str, Any]:
        """Analyze how content is distributed across platforms."""        
        distribution = {
            'content_by_platform': {},
            'content_by_type': {},
            'posting_frequency': {},
            'content_overlap': 0.0,
            'platform_utilization': {}
        }
        
        # Count content by platform
        for platform in platforms:
            platform_content = [
                item for item in content_calendar
                if platform in item.get('target_platforms', [])
            ]
            distribution['content_by_platform'][platform] = len(platform_content)
        
        # Count content by type
        content_types = {}
        for item in content_calendar:
            content_type = item.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        distribution['content_by_type'] = content_types
        
        # Calculate posting frequency per platform
        for platform in platforms:
            platform_posts = distribution['content_by_platform'].get(platform, 0)
            weeks = len(content_calendar) / 7 if content_calendar else 1
            distribution['posting_frequency'][platform] = platform_posts / weeks
        
        # Calculate content overlap (content shared across multiple platforms)
        multi_platform_content = [
            item for item in content_calendar
            if len(item.get('target_platforms', [])) > 1
        ]
        if content_calendar:
            distribution['content_overlap'] = len(multi_platform_content) / len(content_calendar)
        
        return distribution
    
    async def _optimize_content_flow(
        self,
        platforms: List[PlatformType],
        content_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize content flow between platforms."""        
        flow = {
            'primary_platform': None,
            'content_repurposing': {},
            'cross_promotion': {},
            'timing_strategy': {}
        }
        
        # Determine primary platform (highest engagement/reach potential)
        platform_priorities = {
            PlatformType.YOUTUBE: 0.9,  # High retention value
            PlatformType.INSTAGRAM: 0.8,  # Good engagement
            PlatformType.TIKTOK: 0.85,  # High reach potential
            PlatformType.SPOTIFY: 0.7,  # Monetization focused
            PlatformType.TWITTER: 0.6,  # Real-time engagement
            PlatformType.LINKEDIN: 0.65  # Professional network
        }
        
        if platforms:
            primary = max(platforms, key=lambda p: platform_priorities.get(p, 0.5))
            flow['primary_platform'] = primary
        
        # Define content repurposing strategy
        repurposing_map = {
            PlatformType.YOUTUBE: {
                PlatformType.INSTAGRAM: ['highlights_reel', 'carousel_quotes', 'story_clips'],
                PlatformType.TIKTOK: ['short_clips', 'trending_moments'],
                PlatformType.TWITTER: ['key_quotes', 'thread_summary']
            },
            PlatformType.INSTAGRAM: {
                PlatformType.TIKTOK: ['reels_repurpose', 'trend_adaptation'],
                PlatformType.TWITTER: ['quote_cards', 'behind_scenes'],
                PlatformType.YOUTUBE: ['compilation_videos', 'extended_content']
            },
            PlatformType.TIKTOK: {
                PlatformType.INSTAGRAM: ['reels_cross_post', 'story_content'],
                PlatformType.YOUTUBE: ['compilation_videos', 'reaction_content'],
                PlatformType.TWITTER: ['viral_moments', 'trend_commentary']
            }
        }
        
        for source_platform in platforms:
            if source_platform in repurposing_map:
                flow['content_repurposing'][source_platform] = {}
                for target_platform in platforms:
                    if target_platform != source_platform:
                        adaptations = repurposing_map[source_platform].get(target_platform, [])
                        if adaptations:
                            flow['content_repurposing'][source_platform][target_platform] = adaptations
        
        return flow
    
    async def _generate_content_adaptations(
        self,
        platforms: List[PlatformType],
        content_calendar: List[Dict[str, Any]]
    ) -> Dict[PlatformType, Dict[str, Any]]:
        """Generate platform-specific content adaptations."""        
        adaptations = {}
        
        for platform in platforms:
            platform_chars = self.recommendation_engine.platform_characteristics.get(platform, {})
            
            adaptations[platform] = {
                'format_requirements': {},
                'content_modifications': [],
                'optimization_tips': []
            }
            
            # Format requirements
            if platform == PlatformType.YOUTUBE:
                adaptations[platform]['format_requirements'] = {
                    'aspect_ratio': '16:9',
                    'resolution': '1920x1080',
                    'length': '8-15 minutes',
                    'thumbnail': 'required'
                }
                adaptations[platform]['content_modifications'] = [
                    'Add intro and outro sequences',
                    'Include subscribe reminders',
                    'Add chapters for longer videos',
                    'Optimize for watch time retention'
                ]
            
            elif platform == PlatformType.INSTAGRAM:
                adaptations[platform]['format_requirements'] = {
                    'aspect_ratio': '1:1 or 4:5',
                    'resolution': '1080x1080',
                    'reel_length': '15-90 seconds',
                    'story_length': '15 seconds'
                }
                adaptations[platform]['content_modifications'] = [
                    'Add captions and text overlays',
                    'Use Instagram-specific hashtags',
                    'Create visually appealing thumbnails',
                    'Optimize for mobile viewing'
                ]
            
            elif platform == PlatformType.TIKTOK:
                adaptations[platform]['format_requirements'] = {
                    'aspect_ratio': '9:16',
                    'resolution': '1080x1920',
                    'length': '15-60 seconds',
                    'format': 'vertical video'
                }
                adaptations[platform]['content_modifications'] = [
                    'Hook viewers in first 3 seconds',
                    'Use trending audio and effects',
                    'Add captions for accessibility',
                    'Include trending hashtags'
                ]
            
            # General optimization tips
            adaptations[platform]['optimization_tips'] = [
                f'Post during {platform.value} peak hours',
                f'Engage with {platform.value} community',
                f'Use {platform.value}-specific features',
                f'Monitor {platform.value} analytics'
            ]
        
        return adaptations
    
    async def _optimize_posting_schedule(
        self,
        platforms: List[PlatformType],
        content_calendar: List[Dict[str, Any]],
        performance_goals: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """Optimize posting schedule across platforms."""        
        schedule = {}
        
        # Platform-specific optimal posting times
        optimal_times = {
            PlatformType.YOUTUBE: ['18:00', '19:00', '20:00'],
            PlatformType.INSTAGRAM: ['11:00', '13:00', '17:00', '19:00'],
            PlatformType.TIKTOK: ['18:00', '19:00', '20:00', '21:00'],
            PlatformType.TWITTER: ['12:00', '15:00', '17:00'],
            PlatformType.LINKEDIN: ['08:00', '12:00', '17:00'],
            PlatformType.SPOTIFY: ['07:00', '17:00', '22:00']
        }
        
        # Platform-specific optimal days
        optimal_days = {
            PlatformType.YOUTUBE: ['Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            PlatformType.INSTAGRAM: ['Tuesday', 'Wednesday', 'Thursday'],
            PlatformType.TIKTOK: ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            PlatformType.TWITTER: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            PlatformType.LINKEDIN: ['Tuesday', 'Wednesday', 'Thursday'],
            PlatformType.SPOTIFY: ['Friday', 'Saturday']  # New music releases
        }
        
        for platform in platforms:
            platform_times = optimal_times.get(platform, ['12:00', '17:00'])
            platform_days = optimal_days.get(platform, ['Tuesday', 'Wednesday', 'Thursday'])
            
            # Create posting schedule
            platform_schedule = []
            for day in platform_days:
                for time in platform_times[:2]:  # Max 2 times per day
                    platform_schedule.append(f"{day} {time}")
            
            schedule[platform.value] = platform_schedule
        
        return schedule
    
    async def _calculate_budget_allocation(
        self,
        platforms: List[PlatformType],
        performance_goals: Dict[str, float]
    ) -> Dict[PlatformType, float]:
        """Calculate optimal budget allocation across platforms."""        
        allocation = {}
        total_platforms = len(platforms)
        
        if total_platforms == 0:
            return allocation
        
        # Base allocation (equal distribution)
        base_allocation = 1.0 / total_platforms
        
        # Platform ROI multipliers based on typical performance
        roi_multipliers = {
            PlatformType.YOUTUBE: 1.2,  # High retention and monetization
            PlatformType.INSTAGRAM: 1.0,  # Balanced performance
            PlatformType.TIKTOK: 1.1,  # High reach potential
            PlatformType.SPOTIFY: 1.15,  # Direct monetization
            PlatformType.TWITTER: 0.8,  # Lower monetization
            PlatformType.LINKEDIN: 0.9   # Niche but valuable audience
        }
        
        # Calculate weighted allocation
        total_weight = sum(roi_multipliers.get(platform, 1.0) for platform in platforms)
        
        for platform in platforms:
            weight = roi_multipliers.get(platform, 1.0)
            allocation[platform] = weight / total_weight
        
        return allocation
    
    async def _define_performance_kpis(
        self,
        platforms: List[PlatformType],
        performance_goals: Dict[str, float]
    ) -> Dict[str, float]:
        """Define cross-platform performance KPIs."""        
        kpis = {}
        
        # Overall KPIs
        kpis['total_reach'] = performance_goals.get('reach', 100000)
        kpis['total_engagement'] = performance_goals.get('engagement', 10000)
        kpis['follower_growth'] = performance_goals.get('growth', 1000)
        kpis['monetization_target'] = performance_goals.get('revenue', 5000)
        
        # Platform-specific KPIs
        for platform in platforms:
            platform_key = platform.value
            
            if platform == PlatformType.YOUTUBE:
                kpis[f'{platform_key}_watch_time'] = 10000  # minutes
                kpis[f'{platform_key}_subscribers'] = 1000
                kpis[f'{platform_key}_revenue'] = 500  # USD
            
            elif platform == PlatformType.INSTAGRAM:
                kpis[f'{platform_key}_reach'] = 50000
                kpis[f'{platform_key}_engagement_rate'] = 0.05  # 5%
                kpis[f'{platform_key}_story_completion'] = 0.7  # 70%
            
            elif platform == PlatformType.TIKTOK:
                kpis[f'{platform_key}_views'] = 1000000
                kpis[f'{platform_key}_shares'] = 10000
                kpis[f'{platform_key}_completion_rate'] = 0.6  # 60%
            
            elif platform == PlatformType.SPOTIFY:
                kpis[f'{platform_key}_streams'] = 100000
                kpis[f'{platform_key}_monthly_listeners'] = 10000
                kpis[f'{platform_key}_playlist_adds'] = 1000
        
        return kpis
    
    async def evaluate_strategy_performance(
        self,
        strategy: CrossPlatformStrategy,
        actual_performance: Dict[str, float],
        time_period: int = 30  # days
    ) -> Dict[str, Any]:
        """        Evaluate the performance of a cross-platform strategy.
        
        Args:
            strategy: The implemented strategy
            actual_performance: Actual performance metrics
            time_period: Evaluation period in days
            
        Returns:
            Performance evaluation results
        """        
        evaluation = {
            'overall_score': 0.0,
            'kpi_achievement': {},
            'platform_performance': {},
            'recommendations': [],
            'next_steps': []
        }
        
        # Calculate KPI achievement
        total_kpis = len(strategy.performance_kpis)
        achieved_kpis = 0
        
        for kpi, target in strategy.performance_kpis.items():
            actual = actual_performance.get(kpi, 0)
            achievement = actual / target if target > 0 else 0
            evaluation['kpi_achievement'][kpi] = {
                'target': target,
                'actual': actual,
                'achievement': achievement,
                'status': 'achieved' if achievement >= 1.0 else 'in_progress'
            }
            
            if achievement >= 1.0:
                achieved_kpis += 1
        
        # Calculate overall score
        if total_kpis > 0:
            evaluation['overall_score'] = achieved_kpis / total_kpis
        
        # Evaluate platform-specific performance
        for platform in strategy.primary_platforms:
            platform_key = platform.value
            platform_kpis = {
                k: v for k, v in strategy.performance_kpis.items()
                if k.startswith(platform_key)
            }
            
            if platform_kpis:
                platform_achieved = sum(
                    1 for kpi in platform_kpis.keys()
                    if evaluation['kpi_achievement'].get(kpi, {}).get('achievement', 0) >= 1.0
                )
                platform_score = platform_achieved / len(platform_kpis)
                evaluation['platform_performance'][platform] = platform_score
        
        # Generate recommendations based on performance
        if evaluation['overall_score'] < 0.7:
            evaluation['recommendations'].append({
                'type': 'strategy_adjustment',
                'description': 'Consider adjusting content strategy for better performance',
                'priority': 'high'
            })
        
        if evaluation['overall_score'] > 0.8:
            evaluation['recommendations'].append({
                'type': 'scale_up',
                'description': 'Strategy performing well - consider scaling successful tactics',
                'priority': 'medium'
            })
        
        return evaluation
