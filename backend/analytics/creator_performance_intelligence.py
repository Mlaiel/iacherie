"""Creator Performance Intelligence - Advanced Creator Analytics Engine
=======================================================================

Comprehensive creator performance analytics system providing deep insights into
multi-format content creator performance, success prediction, optimization
recommendations, and benchmarking across all creator types.

Specialized for musicians, bloggers, photographers, influencers, comedians,
and all content creator categories with cross-format performance correlation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, Counter


# Configure logging
logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Types of content creators"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    EDUCATOR = "educator"
    GAMER = "gamer"
    ARTIST = "artist"
    CHEF = "chef"
    FITNESS = "fitness"
    TECH_REVIEWER = "tech_reviewer"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    NEWS = "news"
    DOCUMENTARY = "documentary"


class ContentFormat(Enum):
    """Content format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    STORY = "story"
    REEL = "reel"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"


class PerformanceMetric(Enum):
    """Performance measurement metrics"""
    VIEWS = "views"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE = "revenue"
    SUBSCRIBER_GROWTH = "subscriber_growth"
    RETENTION_RATE = "retention_rate"
    CONVERSION_RATE = "conversion_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    SAVES = "saves"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    WATCH_TIME = "watch_time"
    CLICK_THROUGH_RATE = "click_through_rate"


class SuccessLevel(Enum):
    """Creator success classification levels"""
    EMERGING = "emerging"
    RISING = "rising"
    ESTABLISHED = "established"
    ELITE = "elite"
    SUPER_ELITE = "super_elite"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile data"""
    creator_id: str
    creator_type: CreatorType
    content_formats: List[ContentFormat]
    follower_count: int
    total_content: int
    account_age_days: int
    verified: bool = False
    premium_member: bool = False
    collaboration_count: int = 0
    platform_presence: Dict[str, Dict] = field(default_factory=dict)
    niche_categories: List[str] = field(default_factory=list)
    target_demographics: Dict[str, Any] = field(default_factory=dict)
    content_languages: List[str] = field(default_factory=list)
    posting_frequency: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceData:
    """Performance metrics data structure"""
    timestamp: datetime
    metric_type: PerformanceMetric
    value: float
    content_id: Optional[str] = None
    platform: Optional[str] = None
    content_format: Optional[ContentFormat] = None
    audience_segment: Optional[str] = None
    geographic_region: Optional[str] = None
    device_type: Optional[str] = None


@dataclass
class ContentPerformance:
    """Individual content performance analysis"""
    content_id: str
    creator_id: str
    content_format: ContentFormat
    publish_date: datetime
    title: str
    description: str
    tags: List[str]
    duration_seconds: Optional[int] = None
    file_size_mb: Optional[float] = None
    thumbnail_quality: Optional[float] = None
    
    # Performance metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    engagement_rate: float = 0.0
    watch_time_seconds: int = 0
    retention_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_generated: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Quality scores
    content_quality_score: float = 0.0
    seo_score: float = 0.0
    viral_potential_score: float = 0.0
    
    # Platform-specific data
    platform_metrics: Dict[str, Dict] = field(default_factory=dict)


@dataclass
class PerformanceAnalysis:
    """Comprehensive performance analysis results"""
    creator_id: str
    analysis_period: Tuple[datetime, datetime]
    success_level: SuccessLevel
    overall_score: float
    
    # Performance metrics
    average_engagement_rate: float
    total_revenue: Decimal
    subscriber_growth_rate: float
    content_consistency_score: float
    cross_format_performance: Dict[ContentFormat, float]
    
    # Predictions and recommendations
    growth_trajectory: Dict[str, float]
    optimization_recommendations: List[str]
    predicted_success_probability: float
    estimated_revenue_potential: Decimal
    
    # Benchmarking
    peer_comparison_score: float
    market_position_percentile: float
    competitive_advantage_areas: List[str]
    improvement_areas: List[str]
    
    # Advanced analytics
    audience_insights: Dict[str, Any]
    content_strategy_effectiveness: Dict[str, float]
    collaboration_impact_score: float
    platform_optimization_scores: Dict[str, float]


class CreatorPerformanceIntelligence:
    """
    Advanced Creator Performance Intelligence Engine
    
    Provides comprehensive analytics for multi-format content creators,
    including performance tracking, success prediction, optimization
    recommendations, and competitive benchmarking.
    """
    
    def __init__(self) -> None:
        """Initialize the Creator Performance Intelligence Engine"""
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.performance_data: Dict[str, List[PerformanceData]] = defaultdict(list)
        self.content_performances: Dict[str, List[ContentPerformance]] = defaultdict(list)
        self.benchmark_data: Dict[CreatorType, Dict[str, float]] = defaultdict(dict)
        self.success_models: Dict[CreatorType, Dict] = defaultdict(dict)
        
        # Performance thresholds by creator type
        self.performance_thresholds = self._initialize_performance_thresholds()
        
        # Cross-format correlation matrices
        self.format_correlation_matrix = self._initialize_format_correlations()
        
        # Success prediction weights
        self.success_weights = self._initialize_success_weights()
        
        logger.info("🎵 Creator Performance Intelligence Engine initialized")
    
    def _initialize_performance_thresholds(self) -> Dict[CreatorType, Dict[SuccessLevel, Dict[str, float]]]:
        """Initialize performance thresholds for different creator types and success levels"""
        return {
            CreatorType.MUSICIAN: {
                SuccessLevel.EMERGING: {
                    "engagement_rate": 2.0,
                    "monthly_revenue": 100.0,
                    "subscriber_growth": 5.0
                },
                SuccessLevel.RISING: {
                    "engagement_rate": 4.0,
                    "monthly_revenue": 1000.0,
                    "subscriber_growth": 15.0
                },
                SuccessLevel.ESTABLISHED: {
                    "engagement_rate": 6.0,
                    "monthly_revenue": 5000.0,
                    "subscriber_growth": 25.0
                },
                SuccessLevel.ELITE: {
                    "engagement_rate": 8.0,
                    "monthly_revenue": 25000.0,
                    "subscriber_growth": 35.0
                },
                SuccessLevel.SUPER_ELITE: {
                    "engagement_rate": 12.0,
                    "monthly_revenue": 100000.0,
                    "subscriber_growth": 50.0
                }
            },
            CreatorType.BLOGGER: {
                SuccessLevel.EMERGING: {
                    "engagement_rate": 1.5,
                    "monthly_revenue": 50.0,
                    "subscriber_growth": 3.0
                },
                SuccessLevel.RISING: {
                    "engagement_rate": 3.0,
                    "monthly_revenue": 500.0,
                    "subscriber_growth": 10.0
                },
                SuccessLevel.ESTABLISHED: {
                    "engagement_rate": 5.0,
                    "monthly_revenue": 2500.0,
                    "subscriber_growth": 20.0
                },
                SuccessLevel.ELITE: {
                    "engagement_rate": 7.0,
                    "monthly_revenue": 15000.0,
                    "subscriber_growth": 30.0
                },
                SuccessLevel.SUPER_ELITE: {
                    "engagement_rate": 10.0,
                    "monthly_revenue": 75000.0,
                    "subscriber_growth": 45.0
                }
            },
            CreatorType.INFLUENCER: {
                SuccessLevel.EMERGING: {
                    "engagement_rate": 3.0,
                    "monthly_revenue": 200.0,
                    "subscriber_growth": 8.0
                },
                SuccessLevel.RISING: {
                    "engagement_rate": 5.0,
                    "monthly_revenue": 1500.0,
                    "subscriber_growth": 20.0
                },
                SuccessLevel.ESTABLISHED: {
                    "engagement_rate": 7.0,
                    "monthly_revenue": 8000.0,
                    "subscriber_growth": 35.0
                },
                SuccessLevel.ELITE: {
                    "engagement_rate": 10.0,
                    "monthly_revenue": 40000.0,
                    "subscriber_growth": 50.0
                },
                SuccessLevel.SUPER_ELITE: {
                    "engagement_rate": 15.0,
                    "monthly_revenue": 200000.0,
                    "subscriber_growth": 75.0
                }
            }
        }
    
    def _initialize_format_correlations(self) -> Dict[ContentFormat, Dict[ContentFormat, float]]:
        """Initialize cross-format performance correlation matrix"""
        return {
            ContentFormat.VIDEO: {
                ContentFormat.AUDIO: 0.75,
                ContentFormat.IMAGE: 0.65,
                ContentFormat.TEXT: 0.55,
                ContentFormat.LIVESTREAM: 0.85,
                ContentFormat.SHORT_FORM: 0.90,
                ContentFormat.LONG_FORM: 0.70
            },
            ContentFormat.AUDIO: {
                ContentFormat.VIDEO: 0.75,
                ContentFormat.PODCAST: 0.95,
                ContentFormat.TEXT: 0.45,
                ContentFormat.LIVESTREAM: 0.60
            },
            ContentFormat.IMAGE: {
                ContentFormat.VIDEO: 0.65,
                ContentFormat.STORY: 0.80,
                ContentFormat.SOCIAL_POST: 0.85,
                ContentFormat.TEXT: 0.50
            },
            ContentFormat.TEXT: {
                ContentFormat.BLOG_POST: 0.90,
                ContentFormat.SOCIAL_POST: 0.70,
                ContentFormat.VIDEO: 0.55,
                ContentFormat.AUDIO: 0.45
            }
        }
    
    def _initialize_success_weights(self) -> Dict[str, float]:
        """Initialize success prediction weight factors"""
        return {
            "engagement_rate": 0.25,
            "revenue_consistency": 0.20,
            "growth_trajectory": 0.20,
            "content_quality": 0.15,
            "audience_loyalty": 0.10,
            "platform_diversity": 0.05,
            "collaboration_success": 0.05
        }
    
    async def register_creator(self, profile: CreatorProfile) -> bool:
        """Register a new creator profile"""
        try:
            if profile.creator_id in self.creator_profiles:
                logger.warning(f"Creator {profile.creator_id} already registered, updating profile")
            
            self.creator_profiles[profile.creator_id] = profile
            
            # Initialize performance tracking
            if profile.creator_id not in self.performance_data:
                self.performance_data[profile.creator_id] = []
            
            if profile.creator_id not in self.content_performances:
                self.content_performances[profile.creator_id] = []
            
            logger.info(f"✅ Creator {profile.creator_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register creator {profile.creator_id}: {e}")
            return False
    
    async def track_performance(self, creator_id: str, performance_data: PerformanceData) -> bool:
        """Track creator performance metrics"""
        try:
            if creator_id not in self.creator_profiles:
                logger.error(f"Creator {creator_id} not found")
                return False
            
            self.performance_data[creator_id].append(performance_data)
            
            # Keep only last 90 days of performance data for efficiency
            cutoff_date = datetime.now() - timedelta(days=90)
            self.performance_data[creator_id] = [
                data for data in self.performance_data[creator_id]
                if data.timestamp >= cutoff_date
            ]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track performance for creator {creator_id}: {e}")
            return False
    
    async def track_content_performance(self, content_performance: ContentPerformance) -> bool:
        """Track individual content performance"""
        try:
            creator_id = content_performance.creator_id
            
            if creator_id not in self.creator_profiles:
                logger.error(f"Creator {creator_id} not found")
                return False
            
            self.content_performances[creator_id].append(content_performance)
            
            # Keep only last 1000 content performances per creator
            if len(self.content_performances[creator_id]) > 1000:
                self.content_performances[creator_id] = self.content_performances[creator_id][-1000:]
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track content performance: {e}")
            return False
    
    async def analyze_creator_performance(
        self,
        creator_id: str,
        analysis_period_days: int = 30
    ) -> Optional[PerformanceAnalysis]:
        """
        Perform comprehensive creator performance analysis
        
        Args:
            creator_id: Creator identifier
            analysis_period_days: Analysis period in days (default: 30)
            
        Returns:
            PerformanceAnalysis object with comprehensive insights
        """
        try:
            if creator_id not in self.creator_profiles:
                logger.error(f"Creator {creator_id} not found")
                return None
            
            profile = self.creator_profiles[creator_id]
            
            # Define analysis period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Get performance data for period
            period_data = [
                data for data in self.performance_data[creator_id]
                if start_date <= data.timestamp <= end_date
            ]
            
            # Get content performances for period
            period_content = [
                content for content in self.content_performances[creator_id]
                if start_date <= content.publish_date <= end_date
            ]
            
            if not period_data and not period_content:
                logger.warning(f"No performance data found for creator {creator_id} in specified period")
                return None
            
            # Calculate performance metrics
            analysis = await self._calculate_performance_analysis(
                profile, period_data, period_content, (start_date, end_date)
            )
            
            logger.info(f"✅ Performance analysis completed for creator {creator_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze creator performance: {e}")
            return None
    
    async def _calculate_performance_analysis(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance],
        period: Tuple[datetime, datetime]
    ) -> PerformanceAnalysis:
        """Calculate comprehensive performance analysis"""
        
        # Calculate engagement metrics
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0.0
        
        # Calculate revenue metrics
        revenue_data = [data.value for data in performance_data 
                       if data.metric_type == PerformanceMetric.REVENUE]
        total_revenue = Decimal(str(sum(revenue_data))) if revenue_data else Decimal('0')
        
        # Calculate growth metrics
        growth_data = [data.value for data in performance_data 
                      if data.metric_type == PerformanceMetric.SUBSCRIBER_GROWTH]
        subscriber_growth_rate = statistics.mean(growth_data) if growth_data else 0.0
        
        # Calculate content consistency
        content_consistency_score = await self._calculate_content_consistency(content_data)
        
        # Calculate cross-format performance
        cross_format_performance = await self._calculate_cross_format_performance(content_data)
        
        # Determine success level
        success_level = await self._determine_success_level(
            profile, avg_engagement_rate, total_revenue, subscriber_growth_rate
        )
        
        # Calculate overall performance score
        overall_score = await self._calculate_overall_score(
            avg_engagement_rate, total_revenue, subscriber_growth_rate,
            content_consistency_score, cross_format_performance
        )
        
        # Generate predictions and recommendations
        growth_trajectory = await self._predict_growth_trajectory(
            profile, performance_data, content_data
        )
        
        optimization_recommendations = await self._generate_optimization_recommendations(
            profile, performance_data, content_data
        )
        
        predicted_success_probability = await self._predict_success_probability(
            profile, performance_data, content_data
        )
        
        estimated_revenue_potential = await self._estimate_revenue_potential(
            profile, performance_data, content_data
        )
        
        # Perform benchmarking
        peer_comparison_score = await self._calculate_peer_comparison(profile, overall_score)
        market_position_percentile = await self._calculate_market_position(profile, overall_score)
        
        competitive_advantage_areas = await self._identify_competitive_advantages(
            profile, performance_data, content_data
        )
        
        improvement_areas = await self._identify_improvement_areas(
            profile, performance_data, content_data
        )
        
        # Advanced analytics
        audience_insights = await self._analyze_audience_insights(content_data)
        
        content_strategy_effectiveness = await self._analyze_content_strategy_effectiveness(content_data)
        
        collaboration_impact_score = await self._calculate_collaboration_impact(
            profile, performance_data
        )
        
        platform_optimization_scores = await self._calculate_platform_optimization_scores(
            content_data
        )
        
        return PerformanceAnalysis(
            creator_id=profile.creator_id,
            analysis_period=period,
            success_level=success_level,
            overall_score=overall_score,
            average_engagement_rate=avg_engagement_rate,
            total_revenue=total_revenue,
            subscriber_growth_rate=subscriber_growth_rate,
            content_consistency_score=content_consistency_score,
            cross_format_performance=cross_format_performance,
            growth_trajectory=growth_trajectory,
            optimization_recommendations=optimization_recommendations,
            predicted_success_probability=predicted_success_probability,
            estimated_revenue_potential=estimated_revenue_potential,
            peer_comparison_score=peer_comparison_score,
            market_position_percentile=market_position_percentile,
            competitive_advantage_areas=competitive_advantage_areas,
            improvement_areas=improvement_areas,
            audience_insights=audience_insights,
            content_strategy_effectiveness=content_strategy_effectiveness,
            collaboration_impact_score=collaboration_impact_score,
            platform_optimization_scores=platform_optimization_scores
        )
    
    async def _calculate_content_consistency(self, content_data: List[ContentPerformance]) -> float:
        """Calculate content posting consistency score"""
        if not content_data:
            return 0.0
        
        # Calculate posting frequency consistency
        dates = [content.publish_date for content in content_data]
        dates.sort()
        
        if len(dates) < 2:
            return 0.5
        
        # Calculate intervals between posts
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return 0.5
        
        # Calculate consistency based on standard deviation of intervals
        avg_interval = statistics.mean(intervals)
        if avg_interval == 0:
            return 1.0
        
        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 0
        consistency_score = max(0.0, 1.0 - (std_dev / avg_interval))
        
        return min(1.0, consistency_score)
    
    async def _calculate_cross_format_performance(
        self, 
        content_data: List[ContentPerformance]
    ) -> Dict[ContentFormat, float]:
        """Calculate performance scores across different content formats"""
        format_performance = {}
        
        format_groups = defaultdict(list)
        for content in content_data:
            format_groups[content.content_format].append(content.engagement_rate)
        
        for content_format, engagement_rates in format_groups.items():
            if engagement_rates:
                avg_engagement = statistics.mean(engagement_rates)
                format_performance[content_format] = avg_engagement
        
        return format_performance
    
    async def _determine_success_level(
        self,
        profile: CreatorProfile,
        engagement_rate: float,
        revenue: Decimal,
        growth_rate: float
    ) -> SuccessLevel:
        """Determine creator success level based on performance metrics"""
        
        creator_type = profile.creator_type
        thresholds = self.performance_thresholds.get(creator_type, 
                                                   self.performance_thresholds[CreatorType.INFLUENCER])
        
        monthly_revenue = float(revenue)
        
        # Check against thresholds from highest to lowest
        for level in [SuccessLevel.SUPER_ELITE, SuccessLevel.ELITE, 
                     SuccessLevel.ESTABLISHED, SuccessLevel.RISING]:
            
            if level in thresholds:
                threshold = thresholds[level]
                
                if (engagement_rate >= threshold["engagement_rate"] and
                    monthly_revenue >= threshold["monthly_revenue"] and
                    growth_rate >= threshold["subscriber_growth"]):
                    return level
        
        return SuccessLevel.EMERGING
    
    async def _calculate_overall_score(
        self,
        engagement_rate: float,
        revenue: Decimal,
        growth_rate: float,
        consistency_score: float,
        cross_format_performance: Dict[ContentFormat, float]
    ) -> float:
        """Calculate overall creator performance score"""
        
        # Normalize metrics to 0-1 scale
        normalized_engagement = min(1.0, engagement_rate / 15.0)  # 15% max
        normalized_revenue = min(1.0, float(revenue) / 100000.0)  # $100k max
        normalized_growth = min(1.0, growth_rate / 50.0)  # 50% max
        
        # Calculate format diversity bonus
        format_diversity = len(cross_format_performance) / len(ContentFormat)
        
        # Average cross-format performance
        avg_format_performance = (
            statistics.mean(cross_format_performance.values()) / 15.0
            if cross_format_performance else 0.0
        )
        
        # Weighted score calculation
        overall_score = (
            normalized_engagement * 0.3 +
            normalized_revenue * 0.25 +
            normalized_growth * 0.2 +
            consistency_score * 0.15 +
            avg_format_performance * 0.05 +
            format_diversity * 0.05
        )
        
        return min(1.0, overall_score)
    
    async def _predict_growth_trajectory(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> Dict[str, float]:
        """Predict creator growth trajectory"""
        
        # Get historical growth data
        growth_data = [data.value for data in performance_data 
                      if data.metric_type == PerformanceMetric.SUBSCRIBER_GROWTH]
        
        if len(growth_data) < 3:
            # Insufficient data for prediction
            return {
                "next_30_days": 5.0,
                "next_90_days": 15.0,
                "next_180_days": 30.0,
                "confidence": 0.3
            }
        
        # Calculate trend
        recent_growth = statistics.mean(growth_data[-5:]) if len(growth_data) >= 5 else statistics.mean(growth_data)
        historical_growth = statistics.mean(growth_data)
        
        # Calculate acceleration factor
        acceleration = recent_growth / historical_growth if historical_growth > 0 else 1.0
        
        # Predict future growth with diminishing returns
        base_growth = recent_growth
        
        predictions = {
            "next_30_days": base_growth * acceleration * 1.0,
            "next_90_days": base_growth * acceleration * 2.8,
            "next_180_days": base_growth * acceleration * 5.2,
            "confidence": min(0.95, 0.5 + (len(growth_data) * 0.05))
        }
        
        return predictions
    
    async def _generate_optimization_recommendations(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> List[str]:
        """Generate personalized optimization recommendations"""
        
        recommendations = []
        
        # Analyze engagement patterns
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        
        if engagement_rates:
            avg_engagement = statistics.mean(engagement_rates)
            
            if avg_engagement < 3.0:
                recommendations.append(
                    "Focus on improving content engagement through interactive elements, "
                    "polls, questions, and community building activities"
                )
            
            if avg_engagement < 1.0:
                recommendations.append(
                    "Consider revising content strategy to better align with audience interests "
                    "and trending topics in your niche"
                )
        
        # Analyze content consistency
        if content_data:
            publish_dates = [content.publish_date for content in content_data]
            if len(publish_dates) > 1:
                avg_interval = sum(
                    (publish_dates[i] - publish_dates[i-1]).days 
                    for i in range(1, len(publish_dates))
                ) / (len(publish_dates) - 1)
                
                if avg_interval > 7:
                    recommendations.append(
                        "Increase posting frequency to maintain audience engagement. "
                        "Aim for at least one post per week"
                    )
                elif avg_interval > 3:
                    recommendations.append(
                        "Consider more frequent posting to boost algorithm visibility "
                        "and audience retention"
                    )
        
        # Analyze format diversity
        format_count = len(set(content.content_format for content in content_data))
        if format_count < 3:
            recommendations.append(
                "Diversify content formats to reach broader audiences and "
                "leverage cross-format performance correlation"
            )
        
        # Analyze revenue optimization
        revenue_data = [data.value for data in performance_data 
                       if data.metric_type == PerformanceMetric.REVENUE]
        
        if not revenue_data or statistics.mean(revenue_data) < 100:
            recommendations.append(
                "Explore additional monetization strategies including affiliate marketing, "
                "sponsored content, and premium offerings"
            )
        
        # Platform-specific recommendations
        if len(profile.platform_presence) < 3:
            recommendations.append(
                "Expand platform presence to reduce dependency and increase "
                "reach across multiple channels"
            )
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _predict_success_probability(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> float:
        """Predict probability of creator success in next period"""
        
        success_factors = {
            "engagement_consistency": 0.0,
            "growth_momentum": 0.0,
            "content_quality": 0.0,
            "format_diversity": 0.0,
            "platform_presence": 0.0
        }
        
        # Engagement consistency
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        if engagement_rates and len(engagement_rates) > 1:
            consistency = 1.0 - (statistics.stdev(engagement_rates) / statistics.mean(engagement_rates))
            success_factors["engagement_consistency"] = max(0.0, min(1.0, consistency))
        
        # Growth momentum
        growth_data = [data.value for data in performance_data 
                      if data.metric_type == PerformanceMetric.SUBSCRIBER_GROWTH]
        if growth_data:
            recent_growth = statistics.mean(growth_data[-3:]) if len(growth_data) >= 3 else statistics.mean(growth_data)
            success_factors["growth_momentum"] = min(1.0, recent_growth / 20.0)  # 20% as max
        
        # Content quality
        if content_data:
            quality_scores = [content.content_quality_score for content in content_data 
                            if content.content_quality_score > 0]
            if quality_scores:
                success_factors["content_quality"] = statistics.mean(quality_scores)
        
        # Format diversity
        unique_formats = len(set(content.content_format for content in content_data))
        success_factors["format_diversity"] = min(1.0, unique_formats / 6.0)  # 6 formats as max
        
        # Platform presence
        success_factors["platform_presence"] = min(1.0, len(profile.platform_presence) / 8.0)  # 8 platforms as max
        
        # Calculate weighted success probability
        weights = {
            "engagement_consistency": 0.3,
            "growth_momentum": 0.25,
            "content_quality": 0.2,
            "format_diversity": 0.15,
            "platform_presence": 0.1
        }
        
        success_probability = sum(
            success_factors[factor] * weights[factor]
            for factor in success_factors
        )
        
        return min(1.0, success_probability)
    
    async def _estimate_revenue_potential(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> Decimal:
        """Estimate creator revenue potential for next period"""
        
        # Get current revenue baseline
        current_revenue_data = [data.value for data in performance_data 
                              if data.metric_type == PerformanceMetric.REVENUE]
        
        current_revenue = Decimal(str(statistics.mean(current_revenue_data))) if current_revenue_data else Decimal('0')
        
        # Calculate growth multipliers
        engagement_multiplier = 1.0
        growth_multiplier = 1.0
        format_multiplier = 1.0
        
        # Engagement impact on revenue
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        if engagement_rates:
            avg_engagement = statistics.mean(engagement_rates)
            engagement_multiplier = 1.0 + (avg_engagement / 10.0)  # 1% revenue increase per 0.1% engagement
        
        # Growth impact on revenue
        growth_data = [data.value for data in performance_data 
                      if data.metric_type == PerformanceMetric.SUBSCRIBER_GROWTH]
        if growth_data:
            avg_growth = statistics.mean(growth_data)
            growth_multiplier = 1.0 + (avg_growth / 100.0)  # 1% revenue increase per 1% growth
        
        # Format diversity impact
        unique_formats = len(set(content.content_format for content in content_data))
        format_multiplier = 1.0 + (unique_formats * 0.05)  # 5% per additional format
        
        # Calculate potential revenue
        base_potential = max(current_revenue, Decimal('100'))  # Minimum $100 baseline
        
        revenue_potential = base_potential * Decimal(str(
            engagement_multiplier * growth_multiplier * format_multiplier
        ))
        
        # Add creator type specific multipliers
        type_multipliers = {
            CreatorType.INFLUENCER: 1.5,
            CreatorType.MUSICIAN: 1.3,
            CreatorType.EDUCATOR: 1.2,
            CreatorType.GAMER: 1.4,
            CreatorType.BLOGGER: 1.1
        }
        
        type_multiplier = type_multipliers.get(profile.creator_type, 1.0)
        revenue_potential *= Decimal(str(type_multiplier))
        
        return revenue_potential.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_peer_comparison(self, profile: CreatorProfile, overall_score: float) -> float:
        """Calculate performance score compared to peers"""
        
        # Get benchmark data for creator type
        creator_type = profile.creator_type
        
        if creator_type not in self.benchmark_data:
            # No benchmark data available, return neutral score
            return 0.5
        
        peer_scores = self.benchmark_data[creator_type].get('overall_scores', [0.5])
        
        if not peer_scores:
            return 0.5
        
        # Calculate percentile ranking
        scores_below = sum(1 for score in peer_scores if score < overall_score)
        percentile = scores_below / len(peer_scores)
        
        return percentile
    
    async def _calculate_market_position(self, profile: CreatorProfile, overall_score: float) -> float:
        """Calculate market position percentile"""
        
        # Simulate market position calculation
        # In production, this would use comprehensive market data
        
        # Base percentile on overall score with some randomization for realism
        base_percentile = overall_score * 85  # Scale to 0-85%
        
        # Add creator type specific adjustments
        type_adjustments = {
            CreatorType.INFLUENCER: 5,
            CreatorType.MUSICIAN: 0,
            CreatorType.GAMER: 8,
            CreatorType.EDUCATOR: -2,
            CreatorType.BLOGGER: -3
        }
        
        adjustment = type_adjustments.get(profile.creator_type, 0)
        market_position = min(99.0, max(1.0, base_percentile + adjustment))
        
        return market_position
    
    async def _identify_competitive_advantages(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> List[str]:
        """Identify creator's competitive advantages"""
        
        advantages = []
        
        # Analyze engagement strength
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        if engagement_rates and statistics.mean(engagement_rates) > 5.0:
            advantages.append("High audience engagement and community loyalty")
        
        # Analyze content diversity
        unique_formats = len(set(content.content_format for content in content_data))
        if unique_formats >= 4:
            advantages.append("Strong multi-format content strategy")
        
        # Analyze posting consistency
        if content_data:
            consistency_score = await self._calculate_content_consistency(content_data)
            if consistency_score > 0.8:
                advantages.append("Exceptional content posting consistency")
        
        # Analyze growth rate
        growth_data = [data.value for data in performance_data 
                      if data.metric_type == PerformanceMetric.SUBSCRIBER_GROWTH]
        if growth_data and statistics.mean(growth_data) > 15.0:
            advantages.append("Rapid audience growth and expansion")
        
        # Analyze platform presence
        if len(profile.platform_presence) >= 5:
            advantages.append("Strong multi-platform presence and reach")
        
        # Analyze niche expertise
        if len(profile.niche_categories) >= 3:
            advantages.append("Diverse niche expertise and authority")
        
        # Analyze collaboration success
        if profile.collaboration_count > 10:
            advantages.append("Strong collaboration network and partnerships")
        
        return advantages
    
    async def _identify_improvement_areas(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData],
        content_data: List[ContentPerformance]
    ) -> List[str]:
        """Identify areas for improvement"""
        
        improvements = []
        
        # Analyze engagement gaps
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        if not engagement_rates or statistics.mean(engagement_rates) < 2.0:
            improvements.append("Improve audience engagement and interaction")
        
        # Analyze revenue opportunities
        revenue_data = [data.value for data in performance_data 
                       if data.metric_type == PerformanceMetric.REVENUE]
        if not revenue_data or statistics.mean(revenue_data) < 500:
            improvements.append("Explore additional monetization strategies")
        
        # Analyze content frequency
        if len(content_data) < 10:  # Less than 10 pieces in analysis period
            improvements.append("Increase content creation frequency")
        
        # Analyze format diversity
        unique_formats = len(set(content.content_format for content in content_data))
        if unique_formats < 2:
            improvements.append("Diversify content formats and styles")
        
        # Analyze platform expansion
        if len(profile.platform_presence) < 3:
            improvements.append("Expand presence across more platforms")
        
        # Analyze SEO optimization
        seo_scores = [content.seo_score for content in content_data if content.seo_score > 0]
        if not seo_scores or statistics.mean(seo_scores) < 0.6:
            improvements.append("Optimize content for search and discoverability")
        
        return improvements
    
    async def _analyze_audience_insights(self, content_data: List[ContentPerformance]) -> Dict[str, Any]:
        """Analyze audience behavior and preferences"""
        
        insights = {
            "preferred_content_length": "medium",
            "peak_engagement_times": [],
            "top_performing_tags": [],
            "content_preferences": {},
            "geographic_distribution": {},
            "device_preferences": {}
        }
        
        if not content_data:
            return insights
        
        # Analyze content length preferences
        duration_performance = {}
        for content in content_data:
            if content.duration_seconds and content.engagement_rate > 0:
                duration_category = "short" if content.duration_seconds < 60 else \
                                 "medium" if content.duration_seconds < 300 else "long"
                
                if duration_category not in duration_performance:
                    duration_performance[duration_category] = []
                duration_performance[duration_category].append(content.engagement_rate)
        
        if duration_performance:
            best_duration = max(duration_performance.keys(), 
                              key=lambda k: statistics.mean(duration_performance[k]))
            insights["preferred_content_length"] = best_duration
        
        # Analyze top performing tags
        tag_performance = defaultdict(list)
        for content in content_data:
            for tag in content.tags:
                tag_performance[tag].append(content.engagement_rate)
        
        top_tags = sorted(tag_performance.items(), 
                         key=lambda x: statistics.mean(x[1]) if x[1] else 0, 
                         reverse=True)[:10]
        
        insights["top_performing_tags"] = [tag for tag, _ in top_tags]
        
        # Analyze format preferences
        format_performance = defaultdict(list)
        for content in content_data:
            format_performance[content.content_format.value].append(content.engagement_rate)
        
        insights["content_preferences"] = {
            format: statistics.mean(rates) if rates else 0
            for format, rates in format_performance.items()
        }
        
        return insights
    
    async def _analyze_content_strategy_effectiveness(
        self, 
        content_data: List[ContentPerformance]
    ) -> Dict[str, float]:
        """Analyze effectiveness of different content strategies"""
        
        strategy_effectiveness = {
            "seo_optimization": 0.0,
            "viral_potential": 0.0,
            "engagement_focus": 0.0,
            "revenue_generation": 0.0,
            "cross_format_synergy": 0.0
        }
        
        if not content_data:
            return strategy_effectiveness
        
        # SEO strategy effectiveness
        seo_scores = [content.seo_score for content in content_data if content.seo_score > 0]
        if seo_scores:
            strategy_effectiveness["seo_optimization"] = statistics.mean(seo_scores)
        
        # Viral potential strategy
        viral_scores = [content.viral_potential_score for content in content_data 
                       if content.viral_potential_score > 0]
        if viral_scores:
            strategy_effectiveness["viral_potential"] = statistics.mean(viral_scores)
        
        # Engagement strategy
        engagement_rates = [content.engagement_rate for content in content_data 
                          if content.engagement_rate > 0]
        if engagement_rates:
            strategy_effectiveness["engagement_focus"] = min(1.0, statistics.mean(engagement_rates) / 10.0)
        
        # Revenue generation strategy
        revenue_generating = [content for content in content_data if content.revenue_generated > 0]
        if content_data:
            strategy_effectiveness["revenue_generation"] = len(revenue_generating) / len(content_data)
        
        # Cross-format synergy
        formats_used = len(set(content.content_format for content in content_data))
        strategy_effectiveness["cross_format_synergy"] = min(1.0, formats_used / 6.0)
        
        return strategy_effectiveness
    
    async def _calculate_collaboration_impact(
        self,
        profile: CreatorProfile,
        performance_data: List[PerformanceData]
    ) -> float:
        """Calculate impact of collaborations on performance"""
        
        if profile.collaboration_count == 0:
            return 0.0
        
        # Simulate collaboration impact calculation
        # In production, this would analyze performance before/after collaborations
        
        base_impact = min(1.0, profile.collaboration_count / 20.0)  # Up to 20 collaborations for max impact
        
        # Adjust based on overall performance
        engagement_rates = [data.value for data in performance_data 
                          if data.metric_type == PerformanceMetric.ENGAGEMENT_RATE]
        
        if engagement_rates:
            avg_engagement = statistics.mean(engagement_rates)
            engagement_factor = min(2.0, avg_engagement / 5.0)  # Engagement multiplier
            return min(1.0, base_impact * engagement_factor)
        
        return base_impact
    
    async def _calculate_platform_optimization_scores(
        self, 
        content_data: List[ContentPerformance]
    ) -> Dict[str, float]:
        """Calculate optimization scores for different platforms"""
        
        platform_scores = {}
        
        # Group content by platform
        platform_content = defaultdict(list)
        for content in content_data:
            for platform, metrics in content.platform_metrics.items():
                platform_content[platform].append(metrics.get('engagement_rate', 0))
        
        # Calculate average performance per platform
        for platform, engagement_rates in platform_content.items():
            if engagement_rates:
                avg_engagement = statistics.mean(engagement_rates)
                # Normalize to 0-1 scale (15% engagement as max)
                platform_scores[platform] = min(1.0, avg_engagement / 15.0)
        
        # Add default scores for common platforms if not present
        common_platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
        for platform in common_platforms:
            if platform not in platform_scores:
                platform_scores[platform] = 0.5  # Neutral score for unoptimized platforms
        
        return platform_scores
    
    async def get_creator_recommendations(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive recommendations for creator improvement"""
        try:
            analysis = await self.analyze_creator_performance(creator_id)
            
            if not analysis:
                return {"error": "Unable to generate recommendations"}
            
            recommendations = {
                "optimization_actions": analysis.optimization_recommendations,
                "focus_areas": analysis.improvement_areas,
                "competitive_advantages": analysis.competitive_advantage_areas,
                "growth_opportunities": [],
                "monetization_strategies": [],
                "content_strategy": {}
            }
            
            # Growth opportunities based on predictions
            if analysis.predicted_success_probability > 0.7:
                recommendations["growth_opportunities"].append(
                    "High success probability - consider scaling content production"
                )
            
            if analysis.growth_trajectory["next_90_days"] > 20:
                recommendations["growth_opportunities"].append(
                    "Strong growth momentum - invest in audience retention strategies"
                )
            
            # Monetization strategies based on revenue potential
            if analysis.estimated_revenue_potential > Decimal('1000'):
                recommendations["monetization_strategies"].append(
                    "High revenue potential - explore premium content offerings"
                )
            
            if analysis.total_revenue < Decimal('500'):
                recommendations["monetization_strategies"].extend([
                    "Implement affiliate marketing strategies",
                    "Explore brand partnership opportunities",
                    "Consider creating exclusive paid content"
                ])
            
            # Content strategy recommendations
            best_format = max(analysis.cross_format_performance.items(), 
                            key=lambda x: x[1], default=(None, 0))
            
            if best_format[0]:
                recommendations["content_strategy"]["primary_format"] = best_format[0].value
                recommendations["content_strategy"]["focus_recommendation"] = (
                    f"Focus on {best_format[0].value} content - highest performing format"
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations for creator {creator_id}: {e}")
            return {"error": str(e)}
    
    async def benchmark_creator_performance(
        self, 
        creator_id: str, 
        comparison_group: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Benchmark creator performance against peers or specific group"""
        try:
            if creator_id not in self.creator_profiles:
                return {"error": "Creator not found"}
            
            analysis = await self.analyze_creator_performance(creator_id)
            if not analysis:
                return {"error": "Unable to analyze creator performance"}
            
            creator_profile = self.creator_profiles[creator_id]
            
            # If no comparison group specified, use creators of same type
            if not comparison_group:
                comparison_group = [
                    cid for cid, profile in self.creator_profiles.items()
                    if profile.creator_type == creator_profile.creator_type and cid != creator_id
                ]
            
            if not comparison_group:
                return {"error": "No comparable creators found"}
            
            # Analyze comparison group
            comparison_analyses = []
            for comp_creator_id in comparison_group[:20]:  # Limit to 20 for performance
                comp_analysis = await self.analyze_creator_performance(comp_creator_id)
                if comp_analysis:
                    comparison_analyses.append(comp_analysis)
            
            if not comparison_analyses:
                return {"error": "Unable to analyze comparison group"}
            
            # Calculate benchmarks
            benchmark_metrics = {
                "engagement_rate": [comp.average_engagement_rate for comp in comparison_analyses],
                "revenue": [float(comp.total_revenue) for comp in comparison_analyses],
                "growth_rate": [comp.subscriber_growth_rate for comp in comparison_analyses],
                "overall_score": [comp.overall_score for comp in comparison_analyses]
            }
            
            # Calculate percentiles
            def calculate_percentile(value, benchmark_list) -> None:
                if not benchmark_list:
                    return 50.0
                sorted_list = sorted(benchmark_list)
                position = sum(1 for x in sorted_list if x < value)
                return (position / len(sorted_list)) * 100
            
            benchmarks = {
                "engagement_rate": {
                    "creator_value": analysis.average_engagement_rate,
                    "peer_average": statistics.mean(benchmark_metrics["engagement_rate"]),
                    "peer_median": statistics.median(benchmark_metrics["engagement_rate"]),
                    "percentile": calculate_percentile(analysis.average_engagement_rate, 
                                                     benchmark_metrics["engagement_rate"])
                },
                "revenue": {
                    "creator_value": float(analysis.total_revenue),
                    "peer_average": statistics.mean(benchmark_metrics["revenue"]),
                    "peer_median": statistics.median(benchmark_metrics["revenue"]),
                    "percentile": calculate_percentile(float(analysis.total_revenue), 
                                                     benchmark_metrics["revenue"])
                },
                "growth_rate": {
                    "creator_value": analysis.subscriber_growth_rate,
                    "peer_average": statistics.mean(benchmark_metrics["growth_rate"]),
                    "peer_median": statistics.median(benchmark_metrics["growth_rate"]),
                    "percentile": calculate_percentile(analysis.subscriber_growth_rate, 
                                                     benchmark_metrics["growth_rate"])
                },
                "overall_performance": {
                    "creator_value": analysis.overall_score,
                    "peer_average": statistics.mean(benchmark_metrics["overall_score"]),
                    "peer_median": statistics.median(benchmark_metrics["overall_score"]),
                    "percentile": calculate_percentile(analysis.overall_score, 
                                                     benchmark_metrics["overall_score"])
                }
            }
            
            # Generate insights
            insights = []
            
            for metric, data in benchmarks.items():
                if data["percentile"] >= 75:
                    insights.append(f"Excellent {metric.replace('_', ' ')} - top 25% performer")
                elif data["percentile"] >= 50:
                    insights.append(f"Above average {metric.replace('_', ' ')} performance")
                elif data["percentile"] >= 25:
                    insights.append(f"Below average {metric.replace('_', ' ')} - improvement opportunity")
                else:
                    insights.append(f"Low {metric.replace('_', ' ')} - urgent attention needed")
            
            return {
                "creator_id": creator_id,
                "comparison_group_size": len(comparison_analyses),
                "benchmarks": benchmarks,
                "insights": insights,
                "market_position": analysis.market_position_percentile,
                "success_level": analysis.success_level.value
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to benchmark creator {creator_id}: {e}")
            return {"error": str(e)}


# Module initialization
logger.info("🎵 Creator Performance Intelligence Engine module loaded")