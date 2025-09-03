"""Timing Optimizer - Optimisation timing
=======================================

Advanced timing optimization system for maximizing content engagement
through AI-powered audience analysis and optimal posting time prediction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import pytz
from statistics import mean, median
import calendar

logger = logging.getLogger(__name__)


class TimingStrategy(str, Enum):
    """Timing optimization strategies."""
    PEAK_ENGAGEMENT = "peak_engagement"
    MAXIMUM_REACH = "maximum_reach"
    AUDIENCE_ACTIVITY = "audience_activity"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    BALANCED = "balanced"


class AudienceSegment(str, Enum):
    """Audience segments for timing analysis."""
    GENERAL = "general"
    YOUNG_ADULTS = "young_adults"  # 18-25
    MILLENNIALS = "millennials"    # 26-35
    GEN_X = "gen_x"               # 36-50
    BABY_BOOMERS = "baby_boomers" # 51+
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    CREATORS = "creators"


@dataclass
class AudienceInsight:
    """Audience behavior insights."""
    segment: AudienceSegment
    platform: str
    peak_hours: List[int]
    peak_days: List[str]
    engagement_patterns: Dict[str, float]
    timezone_distribution: Dict[str, float]
    activity_score: float
    confidence_level: float


@dataclass
class OptimalTimeRecommendation:
    """Optimal timing recommendation."""
    datetime_utc: datetime
    local_datetime: datetime
    timezone_str: str
    confidence_score: float
    engagement_prediction: float
    reach_prediction: int
    strategy_used: TimingStrategy
    audience_segments: List[AudienceSegment]
    reasoning: List[str]
    alternative_times: List[Tuple[datetime, float]]


@dataclass
class TimingAnalysis:
    """Comprehensive timing analysis result."""
    platform: str
    content_type: str
    analysis_period_days: int
    optimal_recommendations: List[OptimalTimeRecommendation]
    audience_insights: List[AudienceInsight]
    peak_hours_by_day: Dict[str, List[int]]
    seasonal_trends: Dict[str, float]
    competitor_activity: Dict[str, Any]
    platform_algorithm_insights: Dict[str, Any]


class TimingOptimizer:
    """Advanced timing optimization engine."""
    
    def __init__(self):
        """Initialize timing optimizer."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.audience_data_cache = {}
        self.platform_insights = self._initialize_platform_insights()
        self.timezone_cache = {}
    
    def _initialize_platform_insights(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific insights and algorithm behavior."""
        return {
            "youtube": {
                "algorithm_preferences": {
                    "watch_time": 0.4,
                    "click_through_rate": 0.3,
                    "engagement_velocity": 0.2,
                    "subscriber_activity": 0.1
                },
                "peak_performance_windows": {
                    "weekdays": [(14, 16), (19, 21)],  # 2-4 PM, 7-9 PM
                    "weekends": [(10, 12), (15, 17)]   # 10-12 AM, 3-5 PM
                },
                "content_type_modifiers": {
                    "educational": {"weekdays": 1.2, "weekends": 0.8},
                    "entertainment": {"weekdays": 0.9, "weekends": 1.3},
                    "music": {"weekdays": 0.8, "weekends": 1.2}
                },
                "seasonal_factors": {
                    "summer": 0.9,    # Lower engagement in summer
                    "winter": 1.1,    # Higher engagement in winter
                    "holidays": 0.7   # Lower during holidays
                }
            },
            
            "instagram": {
                "algorithm_preferences": {
                    "immediate_engagement": 0.5,
                    "story_completion": 0.2,
                    "profile_visits": 0.2,
                    "saves_shares": 0.1
                },
                "peak_performance_windows": {
                    "weekdays": [(11, 13), (17, 19)],  # 11 AM-1 PM, 5-7 PM
                    "weekends": [(9, 11), (14, 16)]    # 9-11 AM, 2-4 PM
                },
                "content_type_modifiers": {
                    "lifestyle": {"weekdays": 0.9, "weekends": 1.2},
                    "business": {"weekdays": 1.3, "weekends": 0.7},
                    "food": {"weekdays": 1.1, "weekends": 1.1}
                },
                "seasonal_factors": {
                    "summer": 1.1,    # Higher engagement in summer
                    "winter": 0.9,    # Lower engagement in winter
                    "holidays": 1.2   # Higher during holidays
                }
            },
            
            "tiktok": {
                "algorithm_preferences": {
                    "completion_rate": 0.4,
                    "immediate_engagement": 0.3,
                    "shares": 0.2,
                    "comments_quality": 0.1
                },
                "peak_performance_windows": {
                    "weekdays": [(12, 15), (18, 22)],  # 12-3 PM, 6-10 PM
                    "weekends": [(9, 12), (15, 20)]    # 9 AM-12 PM, 3-8 PM
                },
                "content_type_modifiers": {
                    "dance": {"weekdays": 0.8, "weekends": 1.4},
                    "comedy": {"weekdays": 1.0, "weekends": 1.2},
                    "educational": {"weekdays": 1.2, "weekends": 0.8}
                },
                "seasonal_factors": {
                    "summer": 1.2,    # Much higher engagement in summer
                    "winter": 0.8,    # Lower engagement in winter
                    "holidays": 1.3   # Very high during holidays
                }
            },
            
            "spotify": {
                "algorithm_preferences": {
                    "completion_rate": 0.4,
                    "playlist_adds": 0.3,
                    "repeat_listens": 0.2,
                    "skip_rate": 0.1
                },
                "peak_performance_windows": {
                    "weekdays": [(8, 10), (16, 18)],   # Morning & evening commute
                    "weekends": [(10, 14), (20, 22)]   # Late morning & evening
                },
                "content_type_modifiers": {
                    "workout": {"weekdays": 1.3, "weekends": 1.1},
                    "chill": {"weekdays": 0.9, "weekends": 1.2},
                    "focus": {"weekdays": 1.4, "weekends": 0.6}
                },
                "seasonal_factors": {
                    "summer": 1.0,    # Stable year-round
                    "winter": 1.0,    # Stable year-round
                    "holidays": 0.9   # Slightly lower during holidays
                }
            },
            
            "soundcloud": {
                "algorithm_preferences": {
                    "play_duration": 0.4,
                    "likes_reposts": 0.3,
                    "comments": 0.2,
                    "follower_growth": 0.1
                },
                "peak_performance_windows": {
                    "weekdays": [(10, 12), (15, 17), (21, 23)],  # Multiple windows
                    "weekends": [(11, 15), (19, 22)]             # Extended windows
                },
                "content_type_modifiers": {
                    "electronic": {"weekdays": 0.9, "weekends": 1.3},
                    "hip_hop": {"weekdays": 1.1, "weekends": 1.2},
                    "indie": {"weekdays": 1.0, "weekends": 1.1}
                },
                "seasonal_factors": {
                    "summer": 1.1,    # Higher engagement in summer
                    "winter": 0.9,    # Lower engagement in winter
                    "holidays": 0.8   # Lower during holidays
                }
            }
        }
    
    async def optimize_timing(
        self,
        platform: str,
        content_type: str,
        target_audience: Optional[List[AudienceSegment]] = None,
        strategy: TimingStrategy = TimingStrategy.BALANCED,
        timezone_str: str = "UTC",
        days_ahead: int = 7,
        max_recommendations: int = 5
    ) -> TimingAnalysis:
        """Optimize timing for content publication.
        
        Args:
            platform: Target platform
            content_type: Type of content
            target_audience: Target audience segments
            strategy: Optimization strategy
            timezone_str: User timezone
            days_ahead: Days to look ahead
            max_recommendations: Maximum recommendations to return
            
        Returns:
            TimingAnalysis with optimization results
        """
        try:
            self.logger.info(f"Starting timing optimization for {platform} - {content_type}")
            
            # Generate audience insights
            audience_insights = await self._analyze_audience_behavior(
                platform, target_audience or [AudienceSegment.GENERAL], timezone_str
            )
            
            # Generate optimal time recommendations
            recommendations = await self._generate_time_recommendations(
                platform, content_type, audience_insights, strategy, 
                timezone_str, days_ahead, max_recommendations
            )
            
            # Analyze peak hours by day
            peak_hours_by_day = await self._analyze_peak_hours_by_day(
                platform, audience_insights
            )
            
            # Analyze seasonal trends
            seasonal_trends = await self._analyze_seasonal_trends(platform, content_type)
            
            # Analyze competitor activity
            competitor_activity = await self._analyze_competitor_activity(platform)
            
            # Get platform algorithm insights
            algorithm_insights = self.platform_insights.get(platform.lower(), {})
            
            analysis = TimingAnalysis(
                platform=platform,
                content_type=content_type,
                analysis_period_days=days_ahead,
                optimal_recommendations=recommendations,
                audience_insights=audience_insights,
                peak_hours_by_day=peak_hours_by_day,
                seasonal_trends=seasonal_trends,
                competitor_activity=competitor_activity,
                platform_algorithm_insights=algorithm_insights
            )
            
            self.logger.info(f"Timing optimization completed: {len(recommendations)} recommendations generated")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Timing optimization failed: {str(e)}")
            raise
    
    async def _analyze_audience_behavior(
        self,
        platform: str,
        audience_segments: List[AudienceSegment],
        timezone_str: str
    ) -> List[AudienceInsight]:
        """Analyze audience behavior patterns."""
        insights = []
        
        for segment in audience_segments:
            # Simulate audience analysis
            await asyncio.sleep(0.05)
            
            # Generate segment-specific patterns
            if segment == AudienceSegment.YOUNG_ADULTS:
                peak_hours = [12, 15, 18, 21, 23] if platform.lower() == "tiktok" else [11, 14, 17, 20]
                peak_days = ["tuesday", "wednesday", "friday", "saturday"]
                activity_score = 0.85
                
            elif segment == AudienceSegment.PROFESSIONALS:
                peak_hours = [8, 12, 17, 19] if platform.lower() == "linkedin" else [7, 12, 18, 20]
                peak_days = ["monday", "tuesday", "wednesday", "thursday"]
                activity_score = 0.75
                
            elif segment == AudienceSegment.STUDENTS:
                peak_hours = [14, 16, 19, 21, 23]
                peak_days = ["monday", "wednesday", "friday", "saturday", "sunday"]
                activity_score = 0.80
                
            else:  # GENERAL and others
                peak_hours = [11, 14, 17, 19, 21]
                peak_days = ["tuesday", "wednesday", "thursday", "saturday"]
                activity_score = 0.70
            
            # Generate engagement patterns
            engagement_patterns = {
                "morning": 0.6,
                "afternoon": 0.8,
                "evening": 0.9,
                "night": 0.4
            }
            
            # Timezone distribution (simulated)
            timezone_distribution = {
                "America/New_York": 0.3,
                "America/Los_Angeles": 0.25,
                "Europe/London": 0.2,
                "Asia/Tokyo": 0.15,
                "Australia/Sydney": 0.1
            }
            
            insight = AudienceInsight(
                segment=segment,
                platform=platform,
                peak_hours=peak_hours,
                peak_days=peak_days,
                engagement_patterns=engagement_patterns,
                timezone_distribution=timezone_distribution,
                activity_score=activity_score,
                confidence_level=0.82
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_time_recommendations(
        self,
        platform: str,
        content_type: str,
        audience_insights: List[AudienceInsight],
        strategy: TimingStrategy,
        timezone_str: str,
        days_ahead: int,
        max_recommendations: int
    ) -> List[OptimalTimeRecommendation]:
        """Generate optimal time recommendations."""
        recommendations = []
        tz = self._get_timezone(timezone_str)
        platform_insights = self.platform_insights.get(platform.lower(), {})
        
        # Calculate base score for each hour over the next days
        hour_scores = {}
        now = datetime.now(tz)
        
        for day_offset in range(days_ahead):
            target_date = now.date() + timedelta(days=day_offset)
            day_name = calendar.day_name[target_date.weekday()].lower()
            is_weekend = target_date.weekday() >= 5
            
            # Get platform peak windows
            peak_windows = platform_insights.get("peak_performance_windows", {})
            day_type = "weekends" if is_weekend else "weekdays"
            peak_hours_ranges = peak_windows.get(day_type, [(12, 14), (18, 20)])
            
            for hour in range(24):
                dt = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
                dt = tz.localize(dt)
                
                if dt <= now:
                    continue  # Skip past times
                
                score = self._calculate_hour_score(
                    hour, day_name, is_weekend, audience_insights,
                    platform_insights, content_type, strategy
                )
                
                hour_scores[dt] = score
        
        # Sort by score and get top recommendations
        sorted_times = sorted(hour_scores.items(), key=lambda x: x[1], reverse=True)
        
        for i, (dt, score) in enumerate(sorted_times[:max_recommendations]):
            utc_dt = dt.astimezone(timezone.utc)
            
            # Generate alternatives
            alternatives = []
            for j in range(1, 4):  # 3 alternatives
                if i + j < len(sorted_times):
                    alt_dt, alt_score = sorted_times[i + j]
                    alternatives.append((alt_dt.astimezone(timezone.utc), alt_score))
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                dt, score, audience_insights, platform_insights, strategy
            )
            
            recommendation = OptimalTimeRecommendation(
                datetime_utc=utc_dt,
                local_datetime=dt,
                timezone_str=timezone_str,
                confidence_score=min(score, 1.0),
                engagement_prediction=score * 0.8,
                reach_prediction=int(score * 10000),  # Simulated reach
                strategy_used=strategy,
                audience_segments=[insight.segment for insight in audience_insights],
                reasoning=reasoning,
                alternative_times=alternatives
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_hour_score(
        self,
        hour: int,
        day_name: str,
        is_weekend: bool,
        audience_insights: List[AudienceInsight],
        platform_insights: Dict[str, Any],
        content_type: str,
        strategy: TimingStrategy
    ) -> float:
        """Calculate optimization score for a specific hour."""
        base_score = 0.5
        
        # Audience activity score
        audience_score = 0
        for insight in audience_insights:
            if hour in insight.peak_hours:
                audience_score += insight.activity_score * 0.3
            if day_name in insight.peak_days:
                audience_score += insight.activity_score * 0.2
        
        audience_score = audience_score / len(audience_insights) if audience_insights else 0
        
        # Platform peak windows score
        platform_score = 0
        peak_windows = platform_insights.get("peak_performance_windows", {})
        day_type = "weekends" if is_weekend else "weekdays"
        
        for start_hour, end_hour in peak_windows.get(day_type, []):
            if start_hour <= hour <= end_hour:
                platform_score = 0.4
                break
        
        # Content type modifier
        content_modifiers = platform_insights.get("content_type_modifiers", {})
        content_modifier = 1.0
        
        if content_type.lower() in content_modifiers:
            day_modifier_key = "weekends" if is_weekend else "weekdays"
            content_modifier = content_modifiers[content_type.lower()].get(day_modifier_key, 1.0)
        
        # Strategy-specific adjustments
        strategy_bonus = 0
        if strategy == TimingStrategy.PEAK_ENGAGEMENT:
            strategy_bonus = audience_score * 0.5
        elif strategy == TimingStrategy.MAXIMUM_REACH:
            strategy_bonus = platform_score * 0.5
        elif strategy == TimingStrategy.BALANCED:
            strategy_bonus = (audience_score + platform_score) * 0.25
        
        # Calculate final score
        final_score = (base_score + audience_score + platform_score + strategy_bonus) * content_modifier
        
        # Time-of-day adjustments
        if 6 <= hour <= 10:      # Morning
            final_score *= 0.9
        elif 11 <= hour <= 14:   # Midday
            final_score *= 1.1
        elif 15 <= hour <= 18:   # Afternoon
            final_score *= 1.2
        elif 19 <= hour <= 22:   # Evening
            final_score *= 1.3
        elif 23 <= hour or hour <= 5:  # Night/Early morning
            final_score *= 0.6
        
        return max(0.1, min(1.0, final_score))
    
    def _generate_reasoning(
        self,
        dt: datetime,
        score: float,
        audience_insights: List[AudienceInsight],
        platform_insights: Dict[str, Any],
        strategy: TimingStrategy
    ) -> List[str]:
        """Generate reasoning for timing recommendation."""
        reasoning = []
        
        hour = dt.hour
        day_name = calendar.day_name[dt.weekday()]
        is_weekend = dt.weekday() >= 5
        
        # Score-based reasoning
        if score > 0.8:
            reasoning.append("Highly optimal time with excellent engagement potential")
        elif score > 0.6:
            reasoning.append("Good timing with above-average engagement expected")
        else:
            reasoning.append("Moderate timing with standard engagement expected")
        
        # Time-of-day reasoning
        if 6 <= hour <= 10:
            reasoning.append("Morning hours good for professional and commuter audiences")
        elif 11 <= hour <= 14:
            reasoning.append("Midday timing catches lunch break browsing")
        elif 15 <= hour <= 18:
            reasoning.append("Afternoon prime time for most platforms")
        elif 19 <= hour <= 22:
            reasoning.append("Evening peak hours for maximum engagement")
        
        # Day-based reasoning
        if is_weekend:
            reasoning.append("Weekend timing allows for leisure content consumption")
        else:
            reasoning.append("Weekday timing targets active professional audience")
        
        # Audience-based reasoning
        peak_segments = [insight.segment.value for insight in audience_insights 
                        if hour in insight.peak_hours]
        if peak_segments:
            reasoning.append(f"Peak time for {', '.join(peak_segments)} audience segments")
        
        # Strategy reasoning
        if strategy == TimingStrategy.PEAK_ENGAGEMENT:
            reasoning.append("Optimized for maximum audience engagement")
        elif strategy == TimingStrategy.MAXIMUM_REACH:
            reasoning.append("Optimized for maximum content reach")
        elif strategy == TimingStrategy.BALANCED:
            reasoning.append("Balanced optimization for engagement and reach")
        
        return reasoning
    
    async def _analyze_peak_hours_by_day(
        self,
        platform: str,
        audience_insights: List[AudienceInsight]
    ) -> Dict[str, List[int]]:
        """Analyze peak hours for each day of the week."""
        peak_hours_by_day = {}
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for day in days:
            # Aggregate peak hours from audience insights
            all_peak_hours = []
            for insight in audience_insights:
                if day in insight.peak_days:
                    all_peak_hours.extend(insight.peak_hours)
            
            # Get most common hours
            if all_peak_hours:
                from collections import Counter
                hour_counts = Counter(all_peak_hours)
                peak_hours = [hour for hour, count in hour_counts.most_common(5)]
            else:
                # Default peak hours based on platform
                if platform.lower() == "tiktok":
                    peak_hours = [12, 15, 18, 21]
                elif platform.lower() == "instagram":
                    peak_hours = [11, 14, 17, 19]
                else:
                    peak_hours = [12, 14, 18, 20]
            
            peak_hours_by_day[day] = sorted(peak_hours)
        
        return peak_hours_by_day
    
    async def _analyze_seasonal_trends(
        self,
        platform: str,
        content_type: str
    ) -> Dict[str, float]:
        """Analyze seasonal engagement trends."""
        # Simulate seasonal analysis
        await asyncio.sleep(0.02)
        
        platform_insights = self.platform_insights.get(platform.lower(), {})
        seasonal_factors = platform_insights.get("seasonal_factors", {})
        
        # Current season adjustment
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:
            season = "winter"
        elif current_month in [3, 4, 5]:
            season = "spring"
        elif current_month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        return {
            "current_season": season,
            "current_season_factor": seasonal_factors.get(season, 1.0),
            "summer_factor": seasonal_factors.get("summer", 1.0),
            "winter_factor": seasonal_factors.get("winter", 1.0),
            "holiday_factor": seasonal_factors.get("holidays", 1.0),
            "trend_confidence": 0.75
        }
    
    async def _analyze_competitor_activity(self, platform: str) -> Dict[str, Any]:
        """Analyze competitor posting activity."""
        # Simulate competitor analysis
        await asyncio.sleep(0.03)
        
        return {
            "average_posts_per_day": 2.5,
            "peak_posting_hours": [12, 15, 18, 20],
            "competitive_intensity": {
                "low": ["06:00-09:00", "22:00-24:00"],
                "medium": ["09:00-12:00", "14:00-17:00"],
                "high": ["12:00-14:00", "17:00-21:00"]
            },
            "content_gaps": ["09:00-11:00", "21:00-23:00"],
            "recommended_strategy": "Post during content gaps for less competition"
        }
    
    def _get_timezone(self, timezone_str: str) -> pytz.BaseTzInfo:
        """Get timezone object with caching."""
        if timezone_str not in self.timezone_cache:
            try:
                self.timezone_cache[timezone_str] = pytz.timezone(timezone_str)
            except Exception:
                self.logger.warning(f"Invalid timezone {timezone_str}, using UTC")
                self.timezone_cache[timezone_str] = pytz.UTC
        
        return self.timezone_cache[timezone_str]
    
    async def get_quick_recommendation(
        self,
        platform: str,
        timezone_str: str = "UTC"
    ) -> OptimalTimeRecommendation:
        """Get a quick timing recommendation for immediate use.
        
        Args:
            platform: Target platform
            timezone_str: User timezone
            
        Returns:
            Single optimal time recommendation
        """
        try:
            # Quick analysis for immediate recommendation
            analysis = await self.optimize_timing(
                platform=platform,
                content_type="general",
                timezone_str=timezone_str,
                days_ahead=1,
                max_recommendations=1
            )
            
            return analysis.optimal_recommendations[0] if analysis.optimal_recommendations else None
            
        except Exception as e:
            self.logger.error(f"Quick recommendation failed: {str(e)}")
            
            # Fallback recommendation
            tz = self._get_timezone(timezone_str)
            now = datetime.now(tz)
            
            # Default to next peak hour
            peak_hours = [12, 15, 18, 20]
            next_peak = None
            
            for hour in peak_hours:
                candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if candidate > now:
                    next_peak = candidate
                    break
            
            if not next_peak:
                # Tomorrow's first peak
                tomorrow = now + timedelta(days=1)
                next_peak = tomorrow.replace(hour=peak_hours[0], minute=0, second=0, microsecond=0)
            
            return OptimalTimeRecommendation(
                datetime_utc=next_peak.astimezone(timezone.utc),
                local_datetime=next_peak,
                timezone_str=timezone_str,
                confidence_score=0.6,
                engagement_prediction=0.5,
                reach_prediction=5000,
                strategy_used=TimingStrategy.BALANCED,
                audience_segments=[AudienceSegment.GENERAL],
                reasoning=["Fallback recommendation based on general peak hours"],
                alternative_times=[]
            )


# Global timing optimizer instance
_timing_optimizer: Optional[TimingOptimizer] = None


def get_timing_optimizer() -> TimingOptimizer:
    """Get global timing optimizer instance."""
    global _timing_optimizer
    
    if _timing_optimizer is None:
        _timing_optimizer = TimingOptimizer()
    
    return _timing_optimizer


# Convenience functions
async def get_optimal_time(
    platform: str,
    content_type: str = "general",
    timezone_str: str = "UTC"
) -> OptimalTimeRecommendation:
    """Convenience function to get optimal posting time."""
    optimizer = get_timing_optimizer()
    return await optimizer.get_quick_recommendation(platform, timezone_str)


async def analyze_timing(
    platform: str,
    content_type: str,
    audience_segments: Optional[List[str]] = None,
    strategy: str = "balanced"
) -> TimingAnalysis:
    """Convenience function for comprehensive timing analysis."""
    optimizer = get_timing_optimizer()
    
    # Convert string inputs to enums
    audience_enum_segments = []
    if audience_segments:
        for segment in audience_segments:
            try:
                audience_enum_segments.append(AudienceSegment(segment.lower()))
            except ValueError:
                pass
    
    try:
        strategy_enum = TimingStrategy(strategy.lower())
    except ValueError:
        strategy_enum = TimingStrategy.BALANCED
    
    return await optimizer.optimize_timing(
        platform=platform,
        content_type=content_type,
        target_audience=audience_enum_segments,
        strategy=strategy_enum
    )