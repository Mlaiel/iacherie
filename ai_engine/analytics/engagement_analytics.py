"""
Engagement Analytics - Advanced Engagement Metrics and Analysis
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive engagement analytics for social media content,
including engagement rate calculation, audience analysis, and performance insights.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics

logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types of engagement metrics"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    VIEW = "view"
    CLICK = "click"
    FOLLOW = "follow"
    REPOST = "repost"
    REACTION = "reaction"
    MENTION = "mention"

class Platform(Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"

class TimeFrame(Enum):
    """Time frames for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class EngagementMetrics:
    """Container for engagement metrics"""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    views: int = 0
    clicks: int = 0
    follows: int = 0
    reactions: Dict[str, int] = field(default_factory=dict)
    custom_metrics: Dict[str, int] = field(default_factory=dict)

@dataclass
class ContentPerformance:
    """Performance data for a piece of content"""
    content_id: str
    platform: Platform
    published_at: datetime
    metrics: EngagementMetrics
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    virality_score: float = 0.0
    quality_score: float = 0.0
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    peak_engagement_time: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class EngagementTrend:
    """Engagement trend over time"""
    platform: Platform
    metric_type: EngagementType
    time_frame: TimeFrame
    data_points: List[Dict[str, Any]] = field(default_factory=list)  # [{timestamp, value}]
    trend_direction: str = "stable"  # up, down, stable
    trend_strength: float = 0.0  # -1.0 to 1.0
    statistical_significance: float = 0.0

class EngagementAnalyzer:
    """Main engagement analytics engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.content_performance_data = []
        self.engagement_benchmarks = self._load_engagement_benchmarks()
        self.audience_insights = {}
        self.trend_history = []
        self.logger.info("EngagementAnalyzer initialized successfully")
    
    def _load_engagement_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load platform-specific engagement benchmarks"""
        return {
            Platform.INSTAGRAM.value: {
                "engagement_rate": {"excellent": 0.06, "good": 0.03, "average": 0.015},
                "save_rate": {"excellent": 0.02, "good": 0.01, "average": 0.005},
                "comment_rate": {"excellent": 0.004, "good": 0.002, "average": 0.001}
            },
            Platform.FACEBOOK.value: {
                "engagement_rate": {"excellent": 0.09, "good": 0.045, "average": 0.025},
                "share_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001},
                "comment_rate": {"excellent": 0.003, "good": 0.0015, "average": 0.0008}
            },
            Platform.TWITTER.value: {
                "engagement_rate": {"excellent": 0.05, "good": 0.025, "average": 0.015},
                "retweet_rate": {"excellent": 0.01, "good": 0.005, "average": 0.002},
                "reply_rate": {"excellent": 0.003, "good": 0.0015, "average": 0.0008}
            },
            Platform.LINKEDIN.value: {
                "engagement_rate": {"excellent": 0.06, "good": 0.03, "average": 0.02},
                "share_rate": {"excellent": 0.008, "good": 0.004, "average": 0.002},
                "comment_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001}
            },
            Platform.YOUTUBE.value: {
                "engagement_rate": {"excellent": 0.04, "good": 0.02, "average": 0.01},
                "comment_rate": {"excellent": 0.005, "good": 0.0025, "average": 0.001},
                "like_rate": {"excellent": 0.03, "good": 0.015, "average": 0.008}
            },
            Platform.TIKTOK.value: {
                "engagement_rate": {"excellent": 0.18, "good": 0.09, "average": 0.055},
                "share_rate": {"excellent": 0.02, "good": 0.01, "average": 0.005},
                "comment_rate": {"excellent": 0.008, "good": 0.004, "average": 0.002}
            }
        }
    
    def analyze_content_performance(self, content_id: str, platform: Platform, 
                                  metrics: EngagementMetrics, 
                                  reach: int = 0, impressions: int = 0,
                                  published_at: Optional[datetime] = None) -> ContentPerformance:
        """Analyze performance of a specific piece of content"""
        try:
            if published_at is None:
                published_at = datetime.utcnow()
            
            # Calculate engagement rate
            total_engagement = (metrics.likes + metrics.comments + 
                              metrics.shares + metrics.saves + metrics.clicks)
            
            engagement_rate = total_engagement / max(reach, impressions, 1)
            
            # Calculate virality score
            virality_score = self._calculate_virality_score(metrics, reach, platform)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(metrics, engagement_rate, platform)
            
            # Determine peak engagement time
            peak_time = self._estimate_peak_engagement_time(published_at, platform)
            
            performance = ContentPerformance(
                content_id=content_id,
                platform=platform,
                published_at=published_at,
                metrics=metrics,
                reach=reach,
                impressions=impressions,
                engagement_rate=engagement_rate,
                virality_score=virality_score,
                quality_score=quality_score,
                peak_engagement_time=peak_time
            )
            
            # Store for trend analysis
            self.content_performance_data.append(performance)
            
            self.logger.info(f"Analyzed content {content_id}: ER={engagement_rate:.4f}, VS={virality_score:.2f}")
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content performance: {e}")
            raise
    
    def _calculate_virality_score(self, metrics: EngagementMetrics, reach: int, platform: Platform) -> float:
        """Calculate virality score based on sharing behavior"""
        if reach == 0:
            return 0.0
        
        # Weight different sharing actions
        sharing_actions = metrics.shares + metrics.saves + (metrics.comments * 0.3)
        
        # Platform-specific adjustments
        platform_multiplier = {
            Platform.TIKTOK: 1.5,
            Platform.INSTAGRAM: 1.2,
            Platform.TWITTER: 1.3,
            Platform.FACEBOOK: 1.0,
            Platform.LINKEDIN: 0.8,
            Platform.YOUTUBE: 1.1
        }.get(platform, 1.0)
        
        virality_score = (sharing_actions / reach) * platform_multiplier * 100
        
        # Cap at 100
        return min(virality_score, 100.0)
    
    def _calculate_quality_score(self, metrics: EngagementMetrics, engagement_rate: float, platform: Platform) -> float:
        """Calculate content quality score"""
        benchmarks = self.engagement_benchmarks.get(platform.value, {})
        engagement_benchmark = benchmarks.get("engagement_rate", {})
        
        # Base score from engagement rate
        if engagement_rate >= engagement_benchmark.get("excellent", 0.05):
            base_score = 90
        elif engagement_rate >= engagement_benchmark.get("good", 0.03):
            base_score = 70
        elif engagement_rate >= engagement_benchmark.get("average", 0.015):
            base_score = 50
        else:
            base_score = 30
        
        # Adjust based on engagement diversity
        engagement_types = sum([1 for metric in [metrics.likes, metrics.comments, metrics.shares, metrics.saves] if metric > 0])
        diversity_bonus = engagement_types * 5
        
        # Adjust based on comment ratio (indicates meaningful engagement)
        total_engagement = metrics.likes + metrics.comments + metrics.shares + metrics.saves
        if total_engagement > 0:
            comment_ratio = metrics.comments / total_engagement
            comment_bonus = comment_ratio * 20  # Comments are high-quality engagement
        else:
            comment_bonus = 0
        
        quality_score = base_score + diversity_bonus + comment_bonus
        
        return min(quality_score, 100.0)
    
    def _estimate_peak_engagement_time(self, published_at: datetime, platform: Platform) -> datetime:
        """Estimate when peak engagement occurred"""
        # Platform-specific peak engagement timing (hours after posting)
        peak_timing = {
            Platform.INSTAGRAM: 2,
            Platform.FACEBOOK: 3,
            Platform.TWITTER: 1,
            Platform.LINKEDIN: 4,
            Platform.YOUTUBE: 6,
            Platform.TIKTOK: 1.5
        }
        
        hours_to_peak = peak_timing.get(platform, 2)
        return published_at + timedelta(hours=hours_to_peak)
    
    def calculate_engagement_rate(self, metrics: EngagementMetrics, reach: int = 0, followers: int = 0) -> float:
        """Calculate engagement rate with flexible denominators"""
        total_engagement = (metrics.likes + metrics.comments + 
                          metrics.shares + metrics.saves + metrics.clicks)
        
        # Use reach if available, otherwise followers
        denominator = reach if reach > 0 else followers
        
        if denominator == 0:
            return 0.0
        
        return total_engagement / denominator
    
    def analyze_engagement_trend(self, platform: Platform, metric_type: EngagementType, 
                               time_frame: TimeFrame, days_back: int = 30) -> EngagementTrend:
        """Analyze engagement trends over time"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Filter relevant data
            relevant_data = [
                perf for perf in self.content_performance_data
                if perf.platform == platform and 
                   start_date <= perf.published_at <= end_date
            ]
            
            if not relevant_data:
                return EngagementTrend(
                    platform=platform,
                    metric_type=metric_type,
                    time_frame=time_frame,
                    trend_direction="no_data",
                    trend_strength=0.0
                )
            
            # Group data by time frame
            data_points = self._group_data_by_timeframe(relevant_data, time_frame, metric_type)
            
            # Calculate trend
            trend_direction, trend_strength = self._calculate_trend(data_points)
            
            # Calculate statistical significance
            significance = self._calculate_trend_significance(data_points)
            
            trend = EngagementTrend(
                platform=platform,
                metric_type=metric_type,
                time_frame=time_frame,
                data_points=data_points,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                statistical_significance=significance
            )
            
            self.trend_history.append(trend)
            
            self.logger.info(f"Analyzed {platform.value} {metric_type.value} trend: {trend_direction} ({trend_strength:.2f})")
            
            return trend
            
        except Exception as e:
            self.logger.error(f"Failed to analyze engagement trend: {e}")
            raise
    
    def _group_data_by_timeframe(self, data: List[ContentPerformance], 
                               time_frame: TimeFrame, metric_type: EngagementType) -> List[Dict[str, Any]]:
        """Group performance data by specified time frame"""
        grouped_data = {}
        
        for performance in data:
            # Get the appropriate time bucket
            if time_frame == TimeFrame.HOUR:
                bucket = performance.published_at.replace(minute=0, second=0, microsecond=0)
            elif time_frame == TimeFrame.DAY:
                bucket = performance.published_at.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == TimeFrame.WEEK:
                days_since_monday = performance.published_at.weekday()
                bucket = (performance.published_at - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == TimeFrame.MONTH:
                bucket = performance.published_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                bucket = performance.published_at.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Extract the relevant metric value
            metric_value = self._extract_metric_value(performance.metrics, metric_type)
            
            if bucket not in grouped_data:
                grouped_data[bucket] = []
            
            grouped_data[bucket].append(metric_value)
        
        # Convert to list of data points with averages
        data_points = []
        for timestamp, values in sorted(grouped_data.items()):
            data_points.append({
                'timestamp': timestamp,
                'value': statistics.mean(values),
                'count': len(values)
            })
        
        return data_points
    
    def _extract_metric_value(self, metrics: EngagementMetrics, metric_type: EngagementType) -> int:
        """Extract specific metric value from engagement metrics"""
        metric_mapping = {
            EngagementType.LIKE: metrics.likes,
            EngagementType.COMMENT: metrics.comments,
            EngagementType.SHARE: metrics.shares,
            EngagementType.SAVE: metrics.saves,
            EngagementType.VIEW: metrics.views,
            EngagementType.CLICK: metrics.clicks,
            EngagementType.FOLLOW: metrics.follows
        }
        
        return metric_mapping.get(metric_type, 0)
    
    def _calculate_trend(self, data_points: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Calculate trend direction and strength"""
        if len(data_points) < 2:
            return "stable", 0.0
        
        values = [point['value'] for point in data_points]
        
        # Simple linear regression to find trend
        x_values = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x_squared = sum(x * x for x in x_values)
        
        # Calculate slope (trend strength)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
        
        # Normalize trend strength
        avg_value = statistics.mean(values)
        if avg_value > 0:
            trend_strength = slope / avg_value  # Normalize by average value
        else:
            trend_strength = 0.0
        
        # Determine direction
        if abs(trend_strength) < 0.05:
            direction = "stable"
        elif trend_strength > 0:
            direction = "up"
        else:
            direction = "down"
        
        return direction, trend_strength
    
    def _calculate_trend_significance(self, data_points: List[Dict[str, Any]]) -> float:
        """Calculate statistical significance of trend"""
        if len(data_points) < 3:
            return 0.0
        
        values = [point['value'] for point in data_points]
        
        # Simple approach: calculate coefficient of variation
        if statistics.mean(values) == 0:
            return 0.0
        
        cv = statistics.stdev(values) / statistics.mean(values)
        
        # Lower CV indicates more significant trend
        significance = max(0.0, 1.0 - cv)
        
        return significance
    
    def compare_platform_performance(self, platforms: List[Platform], 
                                   metric_type: EngagementType,
                                   days_back: int = 30) -> Dict[str, Any]:
        """Compare performance across multiple platforms"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            platform_stats = {}
            
            for platform in platforms:
                # Filter data for this platform
                platform_data = [
                    perf for perf in self.content_performance_data
                    if perf.platform == platform and 
                       start_date <= perf.published_at <= end_date
                ]
                
                if not platform_data:
                    platform_stats[platform.value] = {
                        "average_metric": 0,
                        "total_posts": 0,
                        "best_performing_post": None,
                        "engagement_rate": 0
                    }
                    continue
                
                # Calculate statistics
                metric_values = [self._extract_metric_value(perf.metrics, metric_type) for perf in platform_data]
                engagement_rates = [perf.engagement_rate for perf in platform_data]
                
                # Find best performing post
                best_post = max(platform_data, key=lambda x: self._extract_metric_value(x.metrics, metric_type))
                
                platform_stats[platform.value] = {
                    "average_metric": statistics.mean(metric_values) if metric_values else 0,
                    "total_posts": len(platform_data),
                    "best_performing_post": {
                        "content_id": best_post.content_id,
                        "metric_value": self._extract_metric_value(best_post.metrics, metric_type),
                        "engagement_rate": best_post.engagement_rate
                    },
                    "average_engagement_rate": statistics.mean(engagement_rates) if engagement_rates else 0,
                    "median_engagement_rate": statistics.median(engagement_rates) if engagement_rates else 0
                }
            
            # Rank platforms
            ranked_platforms = sorted(
                platform_stats.items(),
                key=lambda x: x[1]["average_engagement_rate"],
                reverse=True
            )
            
            comparison = {
                "metric_type": metric_type.value,
                "time_period": f"Last {days_back} days",
                "platform_stats": platform_stats,
                "platform_ranking": [platform for platform, stats in ranked_platforms],
                "top_performer": ranked_platforms[0] if ranked_platforms else None
            }
            
            self.logger.info(f"Platform comparison completed for {metric_type.value}")
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Failed to compare platform performance: {e}")
            raise
    
    def get_content_recommendations(self, platform: Platform, 
                                 target_audience: Optional[str] = None) -> Dict[str, Any]:
        """Get content recommendations based on performance analysis"""
        try:
            # Analyze recent performance data
            recent_data = [
                perf for perf in self.content_performance_data
                if perf.platform == platform and 
                   (datetime.utcnow() - perf.published_at).days <= 30
            ]
            
            if not recent_data:
                return {"message": "Insufficient data for recommendations"}
            
            # Analyze best performing content
            top_performers = sorted(recent_data, key=lambda x: x.engagement_rate, reverse=True)[:5]
            
            # Extract common characteristics
            common_tags = self._find_common_tags(top_performers)
            optimal_posting_times = self._find_optimal_posting_times(top_performers)
            content_patterns = self._analyze_content_patterns(top_performers)
            
            recommendations = {
                "platform": platform.value,
                "based_on_posts": len(recent_data),
                "top_performing_tags": common_tags[:10],
                "optimal_posting_times": optimal_posting_times,
                "content_patterns": content_patterns,
                "engagement_benchmarks": self.engagement_benchmarks.get(platform.value, {}),
                "recommended_posting_frequency": self._calculate_optimal_frequency(recent_data),
                "content_suggestions": [
                    "Focus on content types that generated highest engagement",
                    "Post during identified optimal times",
                    "Use trending hashtags from your top performers",
                    "Encourage comments with questions and calls-to-action",
                    "Maintain consistent quality standards"
                ]
            }
            
            self.logger.info(f"Generated content recommendations for {platform.value}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate content recommendations: {e}")
            raise
    
    def _find_common_tags(self, performances: List[ContentPerformance]) -> List[str]:
        """Find most common tags in high-performing content"""
        tag_counts = {}
        
        for perf in performances:
            for tag in perf.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    def _find_optimal_posting_times(self, performances: List[ContentPerformance]) -> Dict[str, Any]:
        """Find optimal posting times based on performance"""
        hour_performance = {}
        day_performance = {}
        
        for perf in performances:
            hour = perf.published_at.hour
            day = perf.published_at.strftime('%A')
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(perf.engagement_rate)
            
            if day not in day_performance:
                day_performance[day] = []
            day_performance[day].append(perf.engagement_rate)
        
        # Calculate average performance by hour and day
        best_hours = sorted(
            [(hour, statistics.mean(rates)) for hour, rates in hour_performance.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        best_days = sorted(
            [(day, statistics.mean(rates)) for day, rates in day_performance.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "best_hours": [{"hour": hour, "avg_engagement": rate} for hour, rate in best_hours],
            "best_days": [{"day": day, "avg_engagement": rate} for day, rate in best_days]
        }
    
    def _analyze_content_patterns(self, performances: List[ContentPerformance]) -> Dict[str, Any]:
        """Analyze patterns in high-performing content"""
        engagement_rates = [perf.engagement_rate for perf in performances]
        virality_scores = [perf.virality_score for perf in performances]
        quality_scores = [perf.quality_score for perf in performances]
        
        return {
            "average_engagement_rate": statistics.mean(engagement_rates),
            "average_virality_score": statistics.mean(virality_scores),
            "average_quality_score": statistics.mean(quality_scores),
            "engagement_consistency": 1 - (statistics.stdev(engagement_rates) / statistics.mean(engagement_rates)) if statistics.mean(engagement_rates) > 0 else 0
        }
    
    def _calculate_optimal_frequency(self, performances: List[ContentPerformance]) -> Dict[str, Any]:
        """Calculate optimal posting frequency"""
        if len(performances) < 7:
            return {"recommendation": "Insufficient data", "posts_per_week": 0}
        
        # Group by week and calculate average engagement
        weekly_data = {}
        for perf in performances:
            week_start = perf.published_at.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = week_start - timedelta(days=week_start.weekday())
            
            if week_start not in weekly_data:
                weekly_data[week_start] = []
            weekly_data[week_start].append(perf)
        
        # Calculate posts per week and corresponding engagement
        frequency_performance = []
        for week, posts in weekly_data.items():
            posts_count = len(posts)
            avg_engagement = statistics.mean([p.engagement_rate for p in posts])
            frequency_performance.append((posts_count, avg_engagement))
        
        # Find optimal frequency
        if frequency_performance:
            optimal = max(frequency_performance, key=lambda x: x[1])
            return {
                "posts_per_week": optimal[0],
                "expected_engagement": optimal[1],
                "recommendation": f"Post {optimal[0]} times per week for optimal engagement"
            }
        
        return {"recommendation": "Post consistently 3-5 times per week", "posts_per_week": 4}
    
    def get_analytics_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Filter recent data
            recent_data = [
                perf for perf in self.content_performance_data
                if start_date <= perf.published_at <= end_date
            ]
            
            if not recent_data:
                return {"message": f"No data available for the last {days_back} days"}
            
            # Calculate overall statistics
            total_posts = len(recent_data)
            avg_engagement_rate = statistics.mean([perf.engagement_rate for perf in recent_data])
            avg_virality_score = statistics.mean([perf.virality_score for perf in recent_data])
            avg_quality_score = statistics.mean([perf.quality_score for perf in recent_data])
            
            # Platform breakdown
            platform_breakdown = {}
            for perf in recent_data:
                platform = perf.platform.value
                if platform not in platform_breakdown:
                    platform_breakdown[platform] = {"count": 0, "engagement_rates": []}
                platform_breakdown[platform]["count"] += 1
                platform_breakdown[platform]["engagement_rates"].append(perf.engagement_rate)
            
            # Calculate platform averages
            for platform, data in platform_breakdown.items():
                data["avg_engagement_rate"] = statistics.mean(data["engagement_rates"])
                del data["engagement_rates"]  # Remove raw data
            
            # Find best and worst performers
            best_performer = max(recent_data, key=lambda x: x.engagement_rate)
            worst_performer = min(recent_data, key=lambda x: x.engagement_rate)
            
            summary = {
                "period": f"Last {days_back} days",
                "total_posts": total_posts,
                "overall_metrics": {
                    "average_engagement_rate": avg_engagement_rate,
                    "average_virality_score": avg_virality_score,
                    "average_quality_score": avg_quality_score
                },
                "platform_breakdown": platform_breakdown,
                "best_performer": {
                    "content_id": best_performer.content_id,
                    "platform": best_performer.platform.value,
                    "engagement_rate": best_performer.engagement_rate,
                    "published_at": best_performer.published_at.isoformat()
                },
                "worst_performer": {
                    "content_id": worst_performer.content_id,
                    "platform": worst_performer.platform.value,
                    "engagement_rate": worst_performer.engagement_rate,
                    "published_at": worst_performer.published_at.isoformat()
                },
                "trends": len(self.trend_history),
                "data_quality": "good" if total_posts > 10 else "limited"
            }
            
            self.logger.info(f"Generated analytics summary for {days_back} days")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics summary: {e}")
            raise

# Export main classes
__all__ = [
    'EngagementAnalyzer',
    'EngagementMetrics',
    'ContentPerformance',
    'EngagementTrend',
    'EngagementType',
    'Platform',
    'TimeFrame'
]

logger.info("Engagement analytics module loaded successfully")
