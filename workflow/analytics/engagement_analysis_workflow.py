"""Engagement Analysis Workflow - Advanced Engagement Analytics for Ainflue Platform.

This module provides comprehensive engagement analysis and audience interaction patterns
across all content platforms, enabling deep insights into audience behavior and preferences.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class EngagementType(Enum):
    """Types of engagement interactions."""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    STORY_REPLY = "story_reply"
    DIRECT_MESSAGE = "direct_message"
    MENTION = "mention"
    TAG = "tag"
    CLICK = "click"
    VIEW_COMPLETION = "view_completion"


class SentimentType(Enum):
    """Sentiment analysis types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class EngagementMetrics:
    """Engagement metrics data structure."""
    content_id: str
    platform: str
    timestamp: datetime
    total_engagements: int
    engagement_rate: float
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    story_replies: int = 0
    direct_messages: int = 0
    mentions: int = 0
    tags: int = 0
    clicks: int = 0
    view_completion_rate: float = 0.0
    average_watch_time: float = 0.0
    peak_engagement_time: Optional[datetime] = None
    engagement_velocity: float = 0.0  # Engagements per hour
    unique_engagers: int = 0
    repeat_engagers: int = 0
    sentiment_distribution: Dict[str, float] = None


@dataclass
class AudienceSegment:
    """Audience segment analysis."""
    segment_id: str
    name: str
    size: int
    engagement_rate: float
    demographics: Dict[str, Any]
    interests: List[str]
    engagement_patterns: Dict[str, Any]
    preferred_content_types: List[str]
    peak_activity_times: List[datetime]


@dataclass
class AnalysisResult:
    """Engagement analysis result."""
    content_id: str
    analysis_period: Dict[str, datetime]
    engagement_metrics: List[EngagementMetrics]
    overall_engagement_rate: float
    engagement_trend: str  # 'increasing', 'decreasing', 'stable'
    audience_segments: List[AudienceSegment]
    sentiment_analysis: Dict[str, float]
    engagement_patterns: Dict[str, Any]
    peak_engagement_periods: List[Tuple[datetime, datetime]]
    content_effectiveness_score: float
    recommendations: List[str]
    comparative_analysis: Dict[str, Any]


class EngagementAnalysisWorkflow:
    """Advanced engagement analysis workflow for audience interaction insights."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize engagement analysis workflow.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.analysis_window = self.config.get('analysis_window', 24)  # hours
        self.sentiment_enabled = self.config.get('sentiment_analysis', True)
        self.segment_analysis = self.config.get('audience_segmentation', True)
        self.engagement_cache = {}

    async def analyze_engagement(
        self,
        content_id: str,
        platforms: Optional[List[str]] = None,
        time_period: Optional[Dict[str, datetime]] = None,
        include_sentiment: bool = True,
        include_segmentation: bool = True
    ) -> AnalysisResult:
        """Perform comprehensive engagement analysis.
        
        Args:
            content_id: Unique content identifier
            platforms: List of platforms to analyze
            time_period: Time period for analysis
            include_sentiment: Whether to include sentiment analysis
            include_segmentation: Whether to include audience segmentation
            
        Returns:
            AnalysisResult with comprehensive engagement insights
        """
        try:
            logger.info(f"Starting engagement analysis for content: {content_id}")
            
            # Set defaults
            platforms = platforms or ['instagram', 'tiktok', 'youtube']
            time_period = time_period or {
                'start': datetime.now() - timedelta(hours=self.analysis_window),
                'end': datetime.now()
            }
            
            # Collect engagement data
            engagement_metrics = await self._collect_engagement_data(
                content_id, platforms, time_period
            )
            
            # Calculate overall engagement rate
            overall_engagement_rate = self._calculate_overall_engagement_rate(engagement_metrics)
            
            # Analyze engagement trends
            engagement_trend = self._analyze_engagement_trend(engagement_metrics)
            
            # Perform sentiment analysis
            sentiment_analysis = {}
            if include_sentiment and self.sentiment_enabled:
                sentiment_analysis = await self._analyze_sentiment(content_id, engagement_metrics)
            
            # Perform audience segmentation
            audience_segments = []
            if include_segmentation and self.segment_analysis:
                audience_segments = await self._segment_audience(content_id, engagement_metrics)
            
            # Analyze engagement patterns
            engagement_patterns = self._analyze_engagement_patterns(engagement_metrics)
            
            # Identify peak engagement periods
            peak_periods = self._identify_peak_engagement_periods(engagement_metrics)
            
            # Calculate content effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(
                engagement_metrics, sentiment_analysis, engagement_patterns
            )
            
            # Generate recommendations
            recommendations = await self._generate_engagement_recommendations(
                engagement_metrics, sentiment_analysis, audience_segments, engagement_patterns
            )
            
            # Comparative analysis
            comparative_analysis = await self._perform_comparative_analysis(
                content_id, engagement_metrics
            )
            
            result = AnalysisResult(
                content_id=content_id,
                analysis_period=time_period,
                engagement_metrics=engagement_metrics,
                overall_engagement_rate=overall_engagement_rate,
                engagement_trend=engagement_trend,
                audience_segments=audience_segments,
                sentiment_analysis=sentiment_analysis,
                engagement_patterns=engagement_patterns,
                peak_engagement_periods=peak_periods,
                content_effectiveness_score=effectiveness_score,
                recommendations=recommendations,
                comparative_analysis=comparative_analysis
            )
            
            # Cache result
            self.engagement_cache[content_id] = result
            
            logger.info(f"Engagement analysis completed for content: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing engagement for content {content_id}: {str(e)}")
            raise

    async def _collect_engagement_data(
        self,
        content_id: str,
        platforms: List[str],
        time_period: Dict[str, datetime]
    ) -> List[EngagementMetrics]:
        """Collect engagement data from platforms.
        
        Args:
            content_id: Content identifier
            platforms: List of platforms
            time_period: Time period for collection
            
        Returns:
            List of EngagementMetrics
        """
        try:
            engagement_data = []
            
            for platform in platforms:
                platform_data = await self._get_platform_engagement(
                    content_id, platform, time_period
                )
                engagement_data.extend(platform_data)
            
            return engagement_data
            
        except Exception as e:
            logger.error(f"Error collecting engagement data: {str(e)}")
            return []

    async def _get_platform_engagement(
        self,
        content_id: str,
        platform: str,
        time_period: Dict[str, datetime]
    ) -> List[EngagementMetrics]:
        """Get engagement data from specific platform.
        
        Args:
            content_id: Content identifier
            platform: Platform name
            time_period: Time period for data collection
            
        Returns:
            List of EngagementMetrics for the platform
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.2)
            
            # Mock engagement data (in real implementation, call actual platform APIs)
            import random
            
            # Generate hourly engagement data for the time period
            hours = int((time_period['end'] - time_period['start']).total_seconds() / 3600)
            platform_metrics = []
            
            for hour in range(hours):
                timestamp = time_period['start'] + timedelta(hours=hour)
                
                # Simulate realistic engagement patterns
                likes = random.randint(10, 1000)
                comments = random.randint(5, 200)
                shares = random.randint(2, 100)
                saves = random.randint(5, 150)
                total_engagements = likes + comments + shares + saves
                
                # Calculate engagement rate (mock follower count)
                follower_count = random.randint(10000, 100000)
                engagement_rate = (total_engagements / follower_count) * 100
                
                metrics = EngagementMetrics(
                    content_id=content_id,
                    platform=platform,
                    timestamp=timestamp,
                    total_engagements=total_engagements,
                    engagement_rate=engagement_rate,
                    likes=likes,
                    comments=comments,
                    shares=shares,
                    saves=saves,
                    story_replies=random.randint(0, 20),
                    direct_messages=random.randint(0, 30),
                    mentions=random.randint(0, 10),
                    tags=random.randint(0, 15),
                    clicks=random.randint(50, 500),
                    view_completion_rate=random.uniform(60, 95),
                    average_watch_time=random.uniform(30, 120),
                    engagement_velocity=total_engagements,  # Per hour
                    unique_engagers=random.randint(100, 800),
                    repeat_engagers=random.randint(20, 200),
                    sentiment_distribution={
                        'positive': random.uniform(0.6, 0.9),
                        'negative': random.uniform(0.05, 0.2),
                        'neutral': random.uniform(0.1, 0.3)
                    }
                )
                
                platform_metrics.append(metrics)
            
            return platform_metrics
            
        except Exception as e:
            logger.error(f"Error getting {platform} engagement data: {str(e)}")
            return []

    def _calculate_overall_engagement_rate(self, metrics: List[EngagementMetrics]) -> float:
        """Calculate overall engagement rate across all platforms.
        
        Args:
            metrics: List of engagement metrics
            
        Returns:
            Overall engagement rate
        """
        if not metrics:
            return 0.0
        
        total_engagements = sum(m.total_engagements for m in metrics)
        total_unique_engagers = sum(m.unique_engagers for m in metrics)
        
        if total_unique_engagers == 0:
            return 0.0
        
        # Calculate weighted average engagement rate
        weighted_rates = []
        total_weight = 0
        
        for metric in metrics:
            weight = metric.total_engagements
            weighted_rates.append(metric.engagement_rate * weight)
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_rates) / total_weight

    def _analyze_engagement_trend(self, metrics: List[EngagementMetrics]) -> str:
        """Analyze engagement trend over time.
        
        Args:
            metrics: List of engagement metrics
            
        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if len(metrics) < 3:
            return 'stable'
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        
        # Calculate trend using engagement rates
        rates = [m.engagement_rate for m in sorted_metrics]
        
        # Use simple linear regression to determine trend
        n = len(rates)
        x_values = list(range(n))
        
        # Calculate slope
        x_mean = sum(x_values) / n
        y_mean = sum(rates) / n
        
        numerator = sum((x_values[i] - x_mean) * (rates[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Determine trend based on slope
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    async def _analyze_sentiment(
        self,
        content_id: str,
        metrics: List[EngagementMetrics]
    ) -> Dict[str, float]:
        """Analyze sentiment of engagement interactions.
        
        Args:
            content_id: Content identifier
            metrics: List of engagement metrics
            
        Returns:
            Dictionary with sentiment distribution
        """
        try:
            # Aggregate sentiment data from all metrics
            total_positive = 0
            total_negative = 0
            total_neutral = 0
            total_interactions = 0
            
            for metric in metrics:
                if metric.sentiment_distribution:
                    interactions = metric.total_engagements
                    total_positive += metric.sentiment_distribution.get('positive', 0) * interactions
                    total_negative += metric.sentiment_distribution.get('negative', 0) * interactions
                    total_neutral += metric.sentiment_distribution.get('neutral', 0) * interactions
                    total_interactions += interactions
            
            if total_interactions == 0:
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
            
            return {
                'positive': total_positive / total_interactions,
                'negative': total_negative / total_interactions,
                'neutral': total_neutral / total_interactions,
                'sentiment_score': (total_positive - total_negative) / total_interactions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}

    async def _segment_audience(
        self,
        content_id: str,
        metrics: List[EngagementMetrics]
    ) -> List[AudienceSegment]:
        """Perform audience segmentation analysis.
        
        Args:
            content_id: Content identifier
            metrics: List of engagement metrics
            
        Returns:
            List of AudienceSegment objects
        """
        try:
            # Mock audience segmentation (in real implementation, use ML clustering)
            segments = []
            
            # High engagement segment
            high_engagement = AudienceSegment(
                segment_id="high_engagement",
                name="High Engagement Audience",
                size=random.randint(1000, 5000),
                engagement_rate=random.uniform(8.0, 15.0),
                demographics={
                    'age_range': '18-34',
                    'gender_split': {'female': 0.6, 'male': 0.4},
                    'top_locations': ['US', 'UK', 'Canada', 'Australia']
                },
                interests=['fashion', 'lifestyle', 'travel', 'technology'],
                engagement_patterns={
                    'preferred_times': ['18:00-21:00', '12:00-14:00'],
                    'interaction_types': ['likes', 'comments', 'shares'],
                    'engagement_frequency': 'daily'
                },
                preferred_content_types=['video', 'carousel', 'stories'],
                peak_activity_times=[
                    datetime.now().replace(hour=12, minute=0),
                    datetime.now().replace(hour=19, minute=0)
                ]
            )
            segments.append(high_engagement)
            
            # Moderate engagement segment
            moderate_engagement = AudienceSegment(
                segment_id="moderate_engagement",
                name="Moderate Engagement Audience",
                size=random.randint(2000, 8000),
                engagement_rate=random.uniform(3.0, 7.0),
                demographics={
                    'age_range': '25-45',
                    'gender_split': {'female': 0.55, 'male': 0.45},
                    'top_locations': ['US', 'Germany', 'France', 'Spain']
                },
                interests=['business', 'education', 'health', 'entertainment'],
                engagement_patterns={
                    'preferred_times': ['08:00-10:00', '20:00-22:00'],
                    'interaction_types': ['likes', 'saves'],
                    'engagement_frequency': 'weekly'
                },
                preferred_content_types=['image', 'video', 'article'],
                peak_activity_times=[
                    datetime.now().replace(hour=9, minute=0),
                    datetime.now().replace(hour=21, minute=0)
                ]
            )
            segments.append(moderate_engagement)
            
            # Passive audience segment
            passive_audience = AudienceSegment(
                segment_id="passive_audience",
                name="Passive Audience",
                size=random.randint(5000, 15000),
                engagement_rate=random.uniform(0.5, 2.5),
                demographics={
                    'age_range': '35-55',
                    'gender_split': {'female': 0.5, 'male': 0.5},
                    'top_locations': ['US', 'UK', 'India', 'Brazil']
                },
                interests=['news', 'sports', 'music', 'food'],
                engagement_patterns={
                    'preferred_times': ['07:00-09:00', '22:00-23:00'],
                    'interaction_types': ['likes'],
                    'engagement_frequency': 'monthly'
                },
                preferred_content_types=['image', 'short_video'],
                peak_activity_times=[
                    datetime.now().replace(hour=8, minute=0),
                    datetime.now().replace(hour=22, minute=30)
                ]
            )
            segments.append(passive_audience)
            
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting audience: {str(e)}")
            return []

    def _analyze_engagement_patterns(self, metrics: List[EngagementMetrics]) -> Dict[str, Any]:
        """Analyze engagement patterns and behaviors.
        
        Args:
            metrics: List of engagement metrics
            
        Returns:
            Dictionary with engagement pattern analysis
        """
        if not metrics:
            return {}
        
        # Analyze hourly patterns
        hourly_engagement = defaultdict(list)
        for metric in metrics:
            hour = metric.timestamp.hour
            hourly_engagement[hour].append(metric.engagement_rate)
        
        # Find peak hours
        peak_hours = []
        for hour, rates in hourly_engagement.items():
            avg_rate = sum(rates) / len(rates)
            peak_hours.append((hour, avg_rate))
        
        peak_hours.sort(key=lambda x: x[1], reverse=True)
        top_3_hours = [hour for hour, rate in peak_hours[:3]]
        
        # Analyze interaction types
        total_likes = sum(m.likes for m in metrics)
        total_comments = sum(m.comments for m in metrics)
        total_shares = sum(m.shares for m in metrics)
        total_saves = sum(m.saves for m in metrics)
        total_interactions = total_likes + total_comments + total_shares + total_saves
        
        interaction_distribution = {}
        if total_interactions > 0:
            interaction_distribution = {
                'likes': total_likes / total_interactions,
                'comments': total_comments / total_interactions,
                'shares': total_shares / total_interactions,
                'saves': total_saves / total_interactions
            }
        
        # Analyze engagement velocity
        velocities = [m.engagement_velocity for m in metrics if m.engagement_velocity > 0]
        avg_velocity = statistics.mean(velocities) if velocities else 0
        max_velocity = max(velocities) if velocities else 0
        
        return {
            'peak_hours': top_3_hours,
            'interaction_distribution': interaction_distribution,
            'average_engagement_velocity': avg_velocity,
            'max_engagement_velocity': max_velocity,
            'engagement_consistency': statistics.stdev([m.engagement_rate for m in metrics]) if len(metrics) > 1 else 0,
            'repeat_engagement_rate': sum(m.repeat_engagers for m in metrics) / sum(m.unique_engagers for m in metrics) if sum(m.unique_engagers for m in metrics) > 0 else 0
        }

    def _identify_peak_engagement_periods(
        self, 
        metrics: List[EngagementMetrics]
    ) -> List[Tuple[datetime, datetime]]:
        """Identify peak engagement periods.
        
        Args:
            metrics: List of engagement metrics
            
        Returns:
            List of tuples with start and end times of peak periods
        """
        if len(metrics) < 3:
            return []
        
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        
        # Calculate average engagement rate
        avg_engagement = sum(m.engagement_rate for m in sorted_metrics) / len(sorted_metrics)
        
        # Identify periods above average
        peak_periods = []
        current_peak_start = None
        
        for metric in sorted_metrics:
            if metric.engagement_rate > avg_engagement * 1.5:  # 50% above average
                if current_peak_start is None:
                    current_peak_start = metric.timestamp
            else:
                if current_peak_start is not None:
                    peak_periods.append((current_peak_start, metric.timestamp))
                    current_peak_start = None
        
        # Handle case where peak continues to the end
        if current_peak_start is not None:
            peak_periods.append((current_peak_start, sorted_metrics[-1].timestamp))
        
        return peak_periods

    def _calculate_effectiveness_score(
        self,
        metrics: List[EngagementMetrics],
        sentiment_analysis: Dict[str, float],
        engagement_patterns: Dict[str, Any]
    ) -> float:
        """Calculate content effectiveness score.
        
        Args:
            metrics: List of engagement metrics
            sentiment_analysis: Sentiment analysis results
            engagement_patterns: Engagement pattern analysis
            
        Returns:
            Effectiveness score (0-100)
        """
        if not metrics:
            return 0.0
        
        # Base score from engagement rate
        avg_engagement_rate = sum(m.engagement_rate for m in metrics) / len(metrics)
        engagement_score = min(avg_engagement_rate * 10, 40)  # Max 40 points
        
        # Sentiment score
        sentiment_score = 0
        if sentiment_analysis:
            sentiment_ratio = sentiment_analysis.get('sentiment_score', 0)
            sentiment_score = max(sentiment_ratio * 20, 0)  # Max 20 points
        
        # Interaction diversity score
        interaction_score = 0
        if engagement_patterns.get('interaction_distribution'):
            distribution = engagement_patterns['interaction_distribution']
            # Reward balanced interaction types
            entropy = -sum(p * math.log(p) for p in distribution.values() if p > 0)
            max_entropy = math.log(len(distribution))
            if max_entropy > 0:
                interaction_score = (entropy / max_entropy) * 20  # Max 20 points
        
        # Consistency score
        consistency_score = 0
        consistency = engagement_patterns.get('engagement_consistency', float('inf'))
        if consistency != float('inf') and avg_engagement_rate > 0:
            # Lower consistency (less variation) is better
            consistency_ratio = min(consistency / avg_engagement_rate, 1.0)
            consistency_score = (1 - consistency_ratio) * 10  # Max 10 points
        
        # Repeat engagement score
        repeat_rate = engagement_patterns.get('repeat_engagement_rate', 0)
        repeat_score = min(repeat_rate * 50, 10)  # Max 10 points
        
        total_score = engagement_score + sentiment_score + interaction_score + consistency_score + repeat_score
        return round(min(total_score, 100), 2)

    async def _generate_engagement_recommendations(
        self,
        metrics: List[EngagementMetrics],
        sentiment_analysis: Dict[str, float],
        audience_segments: List[AudienceSegment],
        engagement_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate engagement improvement recommendations.
        
        Args:
            metrics: List of engagement metrics
            sentiment_analysis: Sentiment analysis results
            audience_segments: Audience segmentation results
            engagement_patterns: Engagement pattern analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not metrics:
            return ["No engagement data available for analysis"]
        
        avg_engagement_rate = sum(m.engagement_rate for m in metrics) / len(metrics)
        
        # Engagement rate recommendations
        if avg_engagement_rate < 2.0:
            recommendations.append("Low engagement rate detected. Consider improving content quality and relevance")
            recommendations.append("Experiment with different content formats and posting times")
        elif avg_engagement_rate > 8.0:
            recommendations.append("Excellent engagement rate! Scale successful content strategies")
        
        # Sentiment recommendations
        if sentiment_analysis:
            negative_ratio = sentiment_analysis.get('negative', 0)
            if negative_ratio > 0.3:
                recommendations.append("High negative sentiment detected. Review content messaging and tone")
            positive_ratio = sentiment_analysis.get('positive', 0)
            if positive_ratio > 0.8:
                recommendations.append("Strong positive sentiment! Leverage this content style for future posts")
        
        # Timing recommendations
        peak_hours = engagement_patterns.get('peak_hours', [])
        if peak_hours:
            hours_str = ', '.join([f"{h}:00" for h in peak_hours])
            recommendations.append(f"Optimal posting times identified: {hours_str}")
        
        # Interaction type recommendations
        interaction_dist = engagement_patterns.get('interaction_distribution', {})
        if interaction_dist:
            likes_ratio = interaction_dist.get('likes', 0)
            comments_ratio = interaction_dist.get('comments', 0)
            
            if likes_ratio > 0.8 and comments_ratio < 0.1:
                recommendations.append("High likes but low comments. Add engaging questions or CTAs to encourage discussion")
            elif comments_ratio > 0.3:
                recommendations.append("Strong comment engagement! Continue creating discussion-worthy content")
        
        # Audience segment recommendations
        if audience_segments:
            high_engagement_segments = [s for s in audience_segments if s.engagement_rate > 8.0]
            if high_engagement_segments:
                segment_names = [s.name for s in high_engagement_segments]
                recommendations.append(f"Focus on high-engagement segments: {', '.join(segment_names)}")
        
        # Consistency recommendations
        consistency = engagement_patterns.get('engagement_consistency', 0)
        if consistency > avg_engagement_rate:
            recommendations.append("Inconsistent engagement patterns. Develop a more consistent content strategy")
        
        return recommendations

    async def _perform_comparative_analysis(
        self,
        content_id: str,
        metrics: List[EngagementMetrics]
    ) -> Dict[str, Any]:
        """Perform comparative analysis with historical data and benchmarks.
        
        Args:
            content_id: Content identifier
            metrics: Current engagement metrics
            
        Returns:
            Dictionary with comparative analysis
        """
        try:
            # Mock comparative analysis (in real implementation, compare with historical data)
            import random
            
            current_avg_engagement = sum(m.engagement_rate for m in metrics) / len(metrics) if metrics else 0
            
            # Compare with previous period
            previous_period_engagement = random.uniform(1.0, 10.0)
            change_percentage = ((current_avg_engagement - previous_period_engagement) / previous_period_engagement * 100) if previous_period_engagement > 0 else 0
            
            # Industry benchmarks (mock data)
            industry_benchmark = random.uniform(3.0, 8.0)
            vs_industry = ((current_avg_engagement - industry_benchmark) / industry_benchmark * 100) if industry_benchmark > 0 else 0
            
            return {
                'vs_previous_period': {
                    'change_percentage': round(change_percentage, 2),
                    'direction': 'up' if change_percentage > 0 else 'down' if change_percentage < 0 else 'stable'
                },
                'vs_industry_benchmark': {
                    'benchmark_value': industry_benchmark,
                    'difference_percentage': round(vs_industry, 2),
                    'performance': 'above' if vs_industry > 0 else 'below' if vs_industry < 0 else 'at'
                },
                'percentile_ranking': random.randint(65, 95),  # Mock percentile
                'improvement_potential': max(0, industry_benchmark * 1.2 - current_avg_engagement)
            }
            
        except Exception as e:
            logger.error(f"Error performing comparative analysis: {str(e)}")
            return {}

    async def get_engagement_forecast(
        self,
        content_id: str,
        forecast_hours: int = 24
    ) -> Dict[str, Any]:
        """Generate engagement forecast for content.
        
        Args:
            content_id: Content identifier
            forecast_hours: Number of hours to forecast
            
        Returns:
            Dictionary with engagement forecast
        """
        try:
            # Get current engagement trend
            if content_id in self.engagement_cache:
                result = self.engagement_cache[content_id]
                trend = result.engagement_trend
                current_rate = result.overall_engagement_rate
            else:
                # Default values if no cached data
                trend = 'stable'
                current_rate = 5.0
            
            # Generate forecast based on trend
            forecast_points = []
            for hour in range(forecast_hours):
                if trend == 'increasing':
                    predicted_rate = current_rate * (1 + 0.02 * hour)  # 2% growth per hour
                elif trend == 'decreasing':
                    predicted_rate = current_rate * (1 - 0.01 * hour)  # 1% decline per hour
                else:  # stable
                    predicted_rate = current_rate * (1 + random.uniform(-0.005, 0.005))  # Small random variation
                
                forecast_points.append({
                    'hour': hour + 1,
                    'predicted_engagement_rate': max(predicted_rate, 0),
                    'confidence': max(0.95 - 0.01 * hour, 0.5)  # Decreasing confidence over time
                })
            
            return {
                'forecast_period_hours': forecast_hours,
                'base_trend': trend,
                'current_engagement_rate': current_rate,
                'forecast_points': forecast_points,
                'total_predicted_engagement': sum(point['predicted_engagement_rate'] for point in forecast_points)
            }
            
        except Exception as e:
            logger.error(f"Error generating engagement forecast: {str(e)}")
            return {}

import math
import random