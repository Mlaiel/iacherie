"""
Seasonal Scheduler
=================

Advanced seasonal content scheduling engine for Ainflue Distribution Platform.
Optimizes content timing based on seasonal trends, holidays, and cultural events.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import calendar
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class Season(Enum):
    """Seasonal periods"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class HolidayCategory(Enum):
    """Holiday categories"""
    RELIGIOUS = "religious"
    NATIONAL = "national"
    CULTURAL = "cultural"
    COMMERCIAL = "commercial"
    INTERNATIONAL = "international"

class ContentSeasonality(Enum):
    """Content seasonality types"""
    HIGHLY_SEASONAL = "highly_seasonal"
    MODERATELY_SEASONAL = "moderately_seasonal"
    EVERGREEN = "evergreen"
    COUNTER_SEASONAL = "counter_seasonal"

@dataclass
class Holiday:
    """Holiday/Event definition"""
    name: str
    date: date
    category: str
    countries: List[str] = field(default_factory=list)
    preparation_days: int = 7
    peak_days: int = 3
    followup_days: int = 2
    engagement_multiplier: float = 1.5
    keywords: List[str] = field(default_factory=list)

@dataclass
class SeasonalTrend:
    """Seasonal trend data"""
    season: str
    start_date: date
    end_date: date
    peak_months: List[int]
    engagement_patterns: Dict[str, float]
    content_themes: List[str]
    optimal_posting_times: List[str]

@dataclass
class SeasonalSchedulingResult:
    """Result of seasonal scheduling optimization"""
    original_datetime: datetime
    optimized_datetime: datetime
    optimization_reason: str
    expected_engagement_boost: float
    competing_events: List[str]
    recommended_adjustments: List[str]

class SeasonalScheduler:
    """
    Advanced Seasonal Content Scheduler
    
    Provides intelligent scheduling based on:
    - Seasonal trends and patterns
    - Holiday and cultural events
    - Regional variations and preferences
    - Historical engagement data
    - Competitive landscape analysis
    """
    
    def __init__(self, region: str = "US", timezone: str = "UTC"):
        """
        Initialize seasonal scheduler
        
        Args:
            region: Target region code (US, EU, UK, etc.)
            timezone: Target timezone
        """
        self.region = region
        self.timezone = timezone
        self.holidays = self._load_holidays()
        self.seasonal_trends = self._load_seasonal_trends()
        self.engagement_history: Dict[str, Dict] = {}
        
    def _load_holidays(self) -> List[Holiday]:
        """Load holiday and event calendar"""
        holidays = []
        
        # Major international holidays
        current_year = datetime.now().year
        
        # New Year
        holidays.append(Holiday(
            name="New Year's Day",
            date=date(current_year, 1, 1),
            category="international",
            countries=["GLOBAL"],
            preparation_days=14,
            peak_days=7,
            followup_days=7,
            engagement_multiplier=2.0,
            keywords=["new year", "resolution", "fresh start", "goals"]
        ))
        
        # Valentine's Day
        holidays.append(Holiday(
            name="Valentine's Day",
            date=date(current_year, 2, 14),
            category="commercial",
            countries=["US", "EU", "UK", "CA", "AU"],
            preparation_days=21,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=1.8,
            keywords=["love", "romance", "valentine", "relationship", "gift"]
        ))
        
        # Easter (approximate - varies by year)
        easter_date = self._calculate_easter(current_year)
        holidays.append(Holiday(
            name="Easter",
            date=easter_date,
            category="religious",
            countries=["US", "EU", "UK", "CA", "AU", "BR"],
            preparation_days=14,
            peak_days=4,
            followup_days=1,
            engagement_multiplier=1.6,
            keywords=["easter", "spring", "renewal", "family", "celebration"]
        ))
        
        # Mother's Day (US - second Sunday in May)
        mothers_day = self._get_nth_weekday(current_year, 5, 6, 2)  # Second Sunday
        holidays.append(Holiday(
            name="Mother's Day",
            date=mothers_day,
            category="cultural",
            countries=["US", "CA", "AU"],
            preparation_days=21,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=2.2,
            keywords=["mother", "mom", "family", "appreciation", "gift"]
        ))
        
        # Memorial Day (US - last Monday in May)
        memorial_day = self._get_last_weekday(current_year, 5, 0)  # Last Monday
        holidays.append(Holiday(
            name="Memorial Day",
            date=memorial_day,
            category="national",
            countries=["US"],
            preparation_days=7,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=1.4,
            keywords=["memorial", "honor", "remember", "patriotic", "summer start"]
        ))
        
        # Father's Day (US - third Sunday in June)
        fathers_day = self._get_nth_weekday(current_year, 6, 6, 3)  # Third Sunday
        holidays.append(Holiday(
            name="Father's Day",
            date=fathers_day,
            category="cultural",
            countries=["US", "CA", "UK"],
            preparation_days=21,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=1.9,
            keywords=["father", "dad", "family", "appreciation", "gift"]
        ))
        
        # Independence Day (US)
        holidays.append(Holiday(
            name="Independence Day",
            date=date(current_year, 7, 4),
            category="national",
            countries=["US"],
            preparation_days=14,
            peak_days=3,
            followup_days=2,
            engagement_multiplier=1.7,
            keywords=["independence", "july 4th", "patriotic", "freedom", "fireworks"]
        ))
        
        # Labor Day (US - first Monday in September)
        labor_day = self._get_nth_weekday(current_year, 9, 0, 1)  # First Monday
        holidays.append(Holiday(
            name="Labor Day",
            date=labor_day,
            category="national",
            countries=["US", "CA"],
            preparation_days=7,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=1.3,
            keywords=["labor", "work", "summer end", "back to school"]
        ))
        
        # Halloween
        holidays.append(Holiday(
            name="Halloween",
            date=date(current_year, 10, 31),
            category="cultural",
            countries=["US", "CA", "UK", "IE"],
            preparation_days=30,
            peak_days=3,
            followup_days=1,
            engagement_multiplier=2.1,
            keywords=["halloween", "costume", "spooky", "trick or treat", "scary"]
        ))
        
        # Thanksgiving (US - fourth Thursday in November)
        thanksgiving = self._get_nth_weekday(current_year, 11, 3, 4)  # Fourth Thursday
        holidays.append(Holiday(
            name="Thanksgiving",
            date=thanksgiving,
            category="national",
            countries=["US"],
            preparation_days=14,
            peak_days=4,
            followup_days=1,
            engagement_multiplier=1.8,
            keywords=["thanksgiving", "gratitude", "family", "feast", "thankful"]
        ))
        
        # Black Friday
        black_friday = thanksgiving + timedelta(days=1)
        holidays.append(Holiday(
            name="Black Friday",
            date=black_friday,
            category="commercial",
            countries=["US", "CA", "UK"],
            preparation_days=30,
            peak_days=4,
            followup_days=3,
            engagement_multiplier=2.5,
            keywords=["black friday", "deals", "shopping", "sale", "discount"]
        ))
        
        # Christmas
        holidays.append(Holiday(
            name="Christmas",
            date=date(current_year, 12, 25),
            category="religious",
            countries=["GLOBAL"],
            preparation_days=45,
            peak_days=7,
            followup_days=7,
            engagement_multiplier=2.3,
            keywords=["christmas", "holiday", "gift", "family", "celebration"]
        ))
        
        return holidays
    
    def _load_seasonal_trends(self) -> List[SeasonalTrend]:
        """Load seasonal trend data"""
        trends = []
        
        # Spring trend
        trends.append(SeasonalTrend(
            season="spring",
            start_date=date(datetime.now().year, 3, 20),
            end_date=date(datetime.now().year, 6, 20),
            peak_months=[4, 5],
            engagement_patterns={
                "morning": 1.2,
                "afternoon": 1.1,
                "evening": 1.0,
                "weekend": 1.3
            },
            content_themes=["renewal", "growth", "fresh start", "outdoors", "fitness"],
            optimal_posting_times=["7:00", "12:00", "17:00"]
        ))
        
        # Summer trend
        trends.append(SeasonalTrend(
            season="summer",
            start_date=date(datetime.now().year, 6, 21),
            end_date=date(datetime.now().year, 9, 22),
            peak_months=[7, 8],
            engagement_patterns={
                "morning": 1.0,
                "afternoon": 0.9,
                "evening": 1.2,
                "weekend": 1.4
            },
            content_themes=["vacation", "outdoor", "relaxation", "adventure", "travel"],
            optimal_posting_times=["6:00", "11:00", "19:00"]
        ))
        
        # Autumn trend
        trends.append(SeasonalTrend(
            season="autumn",
            start_date=date(datetime.now().year, 9, 23),
            end_date=date(datetime.now().year, 12, 20),
            peak_months=[10, 11],
            engagement_patterns={
                "morning": 1.1,
                "afternoon": 1.2,
                "evening": 1.1,
                "weekend": 1.2
            },
            content_themes=["harvest", "preparation", "cozy", "reflection", "education"],
            optimal_posting_times=["8:00", "13:00", "18:00"]
        ))
        
        # Winter trend
        trends.append(SeasonalTrend(
            season="winter",
            start_date=date(datetime.now().year, 12, 21),
            end_date=date(datetime.now().year + 1, 3, 19),
            peak_months=[12, 1, 2],
            engagement_patterns={
                "morning": 1.1,
                "afternoon": 1.0,
                "evening": 1.3,
                "weekend": 1.1
            },
            content_themes=["indoor", "planning", "resolution", "comfort", "reflection"],
            optimal_posting_times=["9:00", "14:00", "20:00"]
        ))
        
        return trends
    
    def _calculate_easter(self, year: int) -> date:
        """Calculate Easter date for given year"""
        # Simplified Easter calculation (Western Christianity)
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)
    
    def _get_nth_weekday(self, year: int, month: int, weekday: int, n: int) -> date:
        """Get the nth occurrence of weekday in month"""
        first_day = date(year, month, 1)
        first_weekday = first_day.weekday()
        
        # Calculate the first occurrence
        days_to_add = (weekday - first_weekday) % 7
        first_occurrence = first_day + timedelta(days=days_to_add)
        
        # Calculate the nth occurrence
        nth_occurrence = first_occurrence + timedelta(weeks=n-1)
        
        # Make sure it's still in the same month
        if nth_occurrence.month != month:
            nth_occurrence -= timedelta(weeks=1)
        
        return nth_occurrence
    
    def _get_last_weekday(self, year: int, month: int, weekday: int) -> date:
        """Get the last occurrence of weekday in month"""
        # Start from the last day of the month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Work backwards to find the last occurrence of the weekday
        days_to_subtract = (last_day.weekday() - weekday) % 7
        return last_day - timedelta(days=days_to_subtract)
    
    def get_current_season(self, target_date: datetime = None) -> SeasonalTrend:
        """
        Get current seasonal trend
        
        Args:
            target_date: Date to check (defaults to now)
            
        Returns:
            SeasonalTrend: Current seasonal trend
        """
        if target_date is None:
            target_date = datetime.now()
        
        target_date_only = target_date.date()
        
        for trend in self.seasonal_trends:
            if trend.start_date <= target_date_only <= trend.end_date:
                return trend
        
        # Default to spring if no match found
        return self.seasonal_trends[0]
    
    def get_upcoming_holidays(self, days_ahead: int = 60) -> List[Holiday]:
        """
        Get upcoming holidays within specified days
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List[Holiday]: Upcoming holidays
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        upcoming = []
        for holiday in self.holidays:
            if today <= holiday.date <= end_date:
                # Include region filtering
                if (self.region in holiday.countries or 
                    "GLOBAL" in holiday.countries):
                    upcoming.append(holiday)
        
        return sorted(upcoming, key=lambda h: h.date)
    
    def optimize_posting_time(self, content_datetime: datetime, 
                             content_type: str = "general",
                             seasonality: str = "moderately_seasonal") -> SeasonalSchedulingResult:
        """
        Optimize posting time based on seasonal factors
        
        Args:
            content_datetime: Original posting datetime
            content_type: Type of content
            seasonality: Content seasonality level
            
        Returns:
            SeasonalSchedulingResult: Optimization result
        """
        original_datetime = content_datetime
        optimized_datetime = content_datetime
        optimization_reason = "No optimization needed"
        expected_boost = 1.0
        competing_events = []
        recommendations = []
        
        # Get current season
        current_season = self.get_current_season(content_datetime)
        
        # Check for holiday conflicts/opportunities
        upcoming_holidays = self.get_upcoming_holidays(30)
        content_date = content_datetime.date()
        
        for holiday in upcoming_holidays:
            days_until = (holiday.date - content_date).days
            
            # Check if content falls within holiday influence period
            if -holiday.followup_days <= days_until <= holiday.preparation_days:
                if days_until <= 0:
                    # Content is during or after holiday
                    if abs(days_until) <= holiday.peak_days:
                        competing_events.append(f"Peak {holiday.name} period")
                        if seasonality != "evergreen":
                            # Suggest moving before peak to avoid competition
                            suggested_datetime = content_datetime - timedelta(days=holiday.peak_days + 1)
                            optimization_reason = f"Moved before {holiday.name} peak to avoid competition"
                            optimized_datetime = suggested_datetime
                            expected_boost = 1.2
                    else:
                        # Content is in followup period
                        competing_events.append(f"Post-{holiday.name} period")
                else:
                    # Content is in preparation period
                    if days_until <= holiday.preparation_days // 2:
                        # Good timing for holiday-related content
                        if any(keyword in content_type.lower() for keyword in holiday.keywords):
                            expected_boost = holiday.engagement_multiplier * 0.8
                            optimization_reason = f"Well-timed for {holiday.name} preparation"
                        else:
                            competing_events.append(f"Pre-{holiday.name} period")
        
        # Apply seasonal timing optimization
        time_hour = optimized_datetime.hour
        day_of_week = optimized_datetime.weekday()
        
        # Weekend adjustment
        if day_of_week >= 5:  # Weekend
            weekend_multiplier = current_season.engagement_patterns.get("weekend", 1.0)
            expected_boost *= weekend_multiplier
        
        # Time of day adjustment
        if 6 <= time_hour < 12:
            time_multiplier = current_season.engagement_patterns.get("morning", 1.0)
        elif 12 <= time_hour < 17:
            time_multiplier = current_season.engagement_patterns.get("afternoon", 1.0)
        else:
            time_multiplier = current_season.engagement_patterns.get("evening", 1.0)
        
        expected_boost *= time_multiplier
        
        # Generate recommendations
        if expected_boost < 1.1:
            recommendations.append("Consider adjusting posting time to optimal hours")
            optimal_times = current_season.optimal_posting_times
            recommendations.append(f"Optimal times for {current_season.season}: {', '.join(optimal_times)}")
        
        if competing_events:
            recommendations.append("Monitor competing events and adjust strategy accordingly")
        
        if seasonality == "highly_seasonal":
            season_themes = current_season.content_themes
            recommendations.append(f"Align content with seasonal themes: {', '.join(season_themes[:3])}")
        
        return SeasonalSchedulingResult(
            original_datetime=original_datetime,
            optimized_datetime=optimized_datetime,
            optimization_reason=optimization_reason,
            expected_engagement_boost=expected_boost,
            competing_events=competing_events,
            recommended_adjustments=recommendations
        )
    
    def get_seasonal_content_suggestions(self, content_type: str, target_date: datetime = None) -> Dict[str, Any]:
        """
        Get seasonal content suggestions
        
        Args:
            content_type: Type of content
            target_date: Target date for content
            
        Returns:
            Dict[str, Any]: Content suggestions
        """
        if target_date is None:
            target_date = datetime.now()
        
        current_season = self.get_current_season(target_date)
        upcoming_holidays = self.get_upcoming_holidays(45)
        
        suggestions = {
            "seasonal_themes": current_season.content_themes,
            "optimal_posting_times": current_season.optimal_posting_times,
            "engagement_patterns": current_season.engagement_patterns,
            "upcoming_opportunities": [],
            "content_adaptations": []
        }
        
        # Add holiday opportunities
        for holiday in upcoming_holidays[:5]:  # Top 5 upcoming
            days_until = (holiday.date - target_date.date()).days
            if 0 <= days_until <= holiday.preparation_days:
                opportunity = {
                    "event": holiday.name,
                    "date": holiday.date.isoformat(),
                    "days_until": days_until,
                    "keywords": holiday.keywords,
                    "engagement_multiplier": holiday.engagement_multiplier,
                    "optimal_posting_window": f"{holiday.preparation_days} days before to {holiday.followup_days} days after"
                }
                suggestions["upcoming_opportunities"].append(opportunity)
        
        # Content adaptations based on season
        if current_season.season == "spring":
            suggestions["content_adaptations"].extend([
                "Emphasize renewal and fresh starts",
                "Include outdoor and fitness themes",
                "Focus on growth and new beginnings"
            ])
        elif current_season.season == "summer":
            suggestions["content_adaptations"].extend([
                "Highlight outdoor activities and travel",
                "Emphasize relaxation and fun",
                "Consider vacation-friendly content timing"
            ])
        elif current_season.season == "autumn":
            suggestions["content_adaptations"].extend([
                "Focus on preparation and planning",
                "Emphasize cozy and comfort themes",
                "Include educational and reflective content"
            ])
        elif current_season.season == "winter":
            suggestions["content_adaptations"].extend([
                "Emphasize indoor and comfort themes",
                "Focus on planning and goal-setting",
                "Include holiday and celebration content"
            ])
        
        return suggestions
    
    def analyze_seasonal_performance(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze historical performance by season
        
        Args:
            historical_data: List of historical content performance data
            
        Returns:
            Dict[str, Any]: Seasonal performance analysis
        """
        seasonal_performance = {
            "spring": {"posts": 0, "total_engagement": 0, "avg_engagement": 0},
            "summer": {"posts": 0, "total_engagement": 0, "avg_engagement": 0},
            "autumn": {"posts": 0, "total_engagement": 0, "avg_engagement": 0},
            "winter": {"posts": 0, "total_engagement": 0, "avg_engagement": 0}
        }
        
        holiday_performance = {}
        
        for data_point in historical_data:
            post_date = datetime.fromisoformat(data_point.get("date", ""))
            engagement = data_point.get("engagement", 0)
            
            # Determine season
            season_trend = self.get_current_season(post_date)
            season = season_trend.season
            
            seasonal_performance[season]["posts"] += 1
            seasonal_performance[season]["total_engagement"] += engagement
            
            # Check if near any holidays
            for holiday in self.holidays:
                days_diff = abs((holiday.date - post_date.date()).days)
                if days_diff <= holiday.peak_days:
                    if holiday.name not in holiday_performance:
                        holiday_performance[holiday.name] = {"posts": 0, "total_engagement": 0}
                    holiday_performance[holiday.name]["posts"] += 1
                    holiday_performance[holiday.name]["total_engagement"] += engagement
        
        # Calculate averages
        for season in seasonal_performance:
            posts = seasonal_performance[season]["posts"]
            if posts > 0:
                seasonal_performance[season]["avg_engagement"] = (
                    seasonal_performance[season]["total_engagement"] / posts
                )
        
        for holiday in holiday_performance:
            posts = holiday_performance[holiday]["posts"]
            if posts > 0:
                holiday_performance[holiday]["avg_engagement"] = (
                    holiday_performance[holiday]["total_engagement"] / posts
                )
        
        return {
            "seasonal_performance": seasonal_performance,
            "holiday_performance": holiday_performance,
            "best_season": max(seasonal_performance.keys(), 
                             key=lambda s: seasonal_performance[s]["avg_engagement"]),
            "recommendations": self._generate_performance_recommendations(
                seasonal_performance, holiday_performance
            )
        }
    
    def _generate_performance_recommendations(self, seasonal_perf: Dict, holiday_perf: Dict) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Find best performing season
        best_season = max(seasonal_perf.keys(), 
                         key=lambda s: seasonal_perf[s]["avg_engagement"])
        recommendations.append(f"Focus more content during {best_season} season")
        
        # Find best performing holidays
        if holiday_perf:
            best_holiday = max(holiday_perf.keys(), 
                             key=lambda h: holiday_perf[h]["avg_engagement"])
            recommendations.append(f"Leverage {best_holiday} for higher engagement")
        
        # Seasonal timing recommendations
        recommendations.extend([
            "Plan seasonal content 2-4 weeks in advance",
            "Adjust posting frequency based on seasonal engagement patterns",
            "Create evergreen content for low-engagement periods"
        ])
        
        return recommendations

# Usage example
async def main():
    """Example usage of SeasonalScheduler"""
    scheduler = SeasonalScheduler(region="US", timezone="EST")
    
    # Optimize posting time
    content_time = datetime(2024, 12, 20, 14, 0)  # Near Christmas
    result = scheduler.optimize_posting_time(
        content_time, 
        content_type="holiday gift guide",
        seasonality="highly_seasonal"
    )
    
    print(f"Original time: {result.original_datetime}")
    print(f"Optimized time: {result.optimized_datetime}")
    print(f"Reason: {result.optimization_reason}")
    print(f"Expected boost: {result.expected_engagement_boost:.2f}x")
    print(f"Competing events: {result.competing_events}")
    print(f"Recommendations: {result.recommended_adjustments}")
    
    # Get seasonal suggestions
    suggestions = scheduler.get_seasonal_content_suggestions("marketing")
    print(f"\nSeasonal suggestions: {suggestions}")

if __name__ == "__main__":
    asyncio.run(main())