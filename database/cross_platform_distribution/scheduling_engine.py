"""Scheduling Engine - Intelligent Content Scheduling System

Advanced scheduling engine for optimal content distribution timing across multiple platforms.
Provides AI-powered timing optimization, audience analysis, and intelligent scheduling recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import logging
import asyncio
import pytz
import json
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)
Base = declarative_base()

class SchedulingStrategy(str, Enum):
    """
Scheduling optimization strategies"""

    MAXIMUM_REACH = "maximum_reach"
    MAXIMUM_ENGAGEMENT = "maximum_engagement"
    BALANCED_DISTRIBUTION = "balanced_distribution"
    STAGGERED_RELEASE = "staggered_release"
    TIMEZONE_OPTIMIZATION = "timezone_optimization"
    COMPETITOR_AVOIDANCE = "competitor_avoidance"
    TRENDING_ALIGNMENT = "trending_alignment"

class TimeSlotPriority(str, Enum):
    """Time slot priority levels"""

    PEAK = "peak"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    AVOID = "avoid"

class AudienceSegment(str, Enum):
    """Audience segments for timing optimization"""

    GLOBAL = "global"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"

@dataclass
class TimeSlot:
    """Represents a scheduled time slot"""
    start_time: datetime
    end_time: datetime
    priority: TimeSlotPriority
    estimated_reach: int
    estimated_engagement: float
    platform_specific_score: Dict[str, float] = field(default_factory=dict)
    timezone: str = "UTC"
    confidence_score: float = 0.0

@dataclass
class SchedulingRequest:
    """Request for content scheduling optimization"""
    content_id: str
    target_platforms: List[str]
    content_type: str
    target_audience: AudienceSegment
    preferred_date_range: Tuple[datetime, datetime]
    strategy: SchedulingStrategy
    timezone: str = "UTC"
    exclude_weekends: bool = False
    exclude_holidays: bool = True
    custom_constraints: Optional[Dict[str, Any]] = field(default_factory=dict)
    previous_posts_data: Optional[List[Dict]] = field(default_factory=list)

@dataclass
class SchedulingResult:
    """Result of scheduling optimization"""
    content_id: str
    success: bool
    recommended_schedule: Dict[str, datetime] = field(default_factory=dict)
    alternative_times: Dict[str, List[datetime]] = field(default_factory=dict)
    performance_predictions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    optimization_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)

class ScheduleTemplate(Base):
    """
Database model for reusable schedule templates"""
    __tablename__ = "schedule_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_name = Column(String(200), nullable=False)
    content_type = Column(String(50), nullable=False)
    target_platforms = Column(JSON, nullable=False)
    schedule_pattern = Column(JSON, nullable=False)  # Dict[platform, timing_pattern]
    timezone = Column(String(50), default="UTC", nullable=False)
    strategy = Column(String(30), nullable=False)
    success_rate = Column(JSON, nullable=True)  # Historical performance
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class PerformanceHistory(Base):
    """Database model for tracking scheduling performance"""
    __tablename__ = "scheduling_performance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    actual_publish_time = Column(DateTime, nullable=True)
    predicted_reach = Column(Integer, nullable=True)
    actual_reach = Column(Integer, nullable=True)
    predicted_engagement = Column(JSON, nullable=True)  # Dict[metric, value]
    actual_engagement = Column(JSON, nullable=True)  # Dict[metric, value]
    optimization_score = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SchedulingEngine:
    """
    Enterprise-grade intelligent scheduling engine
    
    Provides AI-powered content scheduling optimization with audience analysis,
    platform-specific timing, and performance prediction capabilities.
    """
    
    # Platform-specific optimal time patterns (24-hour format, UTC)
    PLATFORM_OPTIMAL_TIMES = {
        "youtube": {
            "weekdays": [14, 15, 20, 21],  # 2-3 PM, 8-9 PM UTC
            "weekends": [12, 13, 18, 19],  # 12-1 PM, 6-7 PM UTC
            "peak_days": [1, 2, 4]  # Tuesday, Wednesday, Friday
        },
        "instagram": {
            "weekdays": [6, 12, 17, 18],  # 6 AM, 12 PM, 5-6 PM UTC
            "weekends": [10, 11, 14, 15],  # 10-11 AM, 2-3 PM UTC
            "peak_days": [2, 3, 5]  # Wednesday, Thursday, Saturday
        },
        "tiktok": {
            "weekdays": [18, 19, 21, 22],  # 6-7 PM, 9-10 PM UTC
            "weekends": [9, 10, 19, 20],  # 9-10 AM, 7-8 PM UTC
            "peak_days": [1, 2, 3, 4, 5]  # Monday-Friday
        },
        "twitter": {
            "weekdays": [9, 12, 15, 17],  # 9 AM, 12 PM, 3 PM, 5 PM UTC
            "weekends": [12, 14, 16],  # 12 PM, 2 PM, 4 PM UTC
            "peak_days": [2, 3, 4]  # Wednesday, Thursday, Friday
        },
        "spotify": {
            "weekdays": [7, 8, 17, 18],  # 7-8 AM, 5-6 PM UTC
            "weekends": [10, 11, 16, 17],  # 10-11 AM, 4-5 PM UTC
            "peak_days": [4, 5]  # Friday, Saturday
        },
        "linkedin": {
            "weekdays": [8, 9, 12, 17],  # 8-9 AM, 12 PM, 5 PM UTC
            "weekends": [],  # LinkedIn is business-focused
            "peak_days": [2, 3, 4]  # Wednesday, Thursday, Friday
        }
    }
    
    # Timezone mappings for audience segments
    AUDIENCE_TIMEZONES = {
        AudienceSegment.NORTH_AMERICA: ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
        AudienceSegment.EUROPE: ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome"],
        AudienceSegment.ASIA_PACIFIC: ["Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney", "Asia/Mumbai"],
        AudienceSegment.LATIN_AMERICA: ["America/Sao_Paulo", "America/Mexico_City", "America/Buenos_Aires"],
        AudienceSegment.MIDDLE_EAST: ["Asia/Dubai", "Asia/Tehran", "Asia/Riyadh"],
        AudienceSegment.AFRICA: ["Africa/Cairo", "Africa/Lagos", "Africa/Johannesburg"]
    }
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def optimize_schedule(self, request: SchedulingRequest) -> SchedulingResult:
        """
        Optimize content scheduling based on AI analysis
        
        Args:
            request: Scheduling optimization request
            
        Returns:
            SchedulingResult: Optimized scheduling recommendations
        """
        try:
            self.logger.info(f"Starting schedule optimization for content {request.content_id}")
            
            result = SchedulingResult(
                content_id=request.content_id,
                success=True
            )
            
            # Analyze audience timezone distribution
            audience_analysis = await self._analyze_audience_timezones(request)
            result.analysis_metadata["audience_analysis"] = audience_analysis
            
            # Generate time slots for each platform
            for platform in request.target_platforms:
                time_slots = await self._generate_time_slots(
                    platform, 
                    request, 
                    audience_analysis
                )
                
                # Select optimal time based on strategy
                optimal_time = await self._select_optimal_time(
                    time_slots, 
                    request.strategy
                )
                
                result.recommended_schedule[platform] = optimal_time
                
                # Generate alternative times
                alternatives = await self._generate_alternatives(time_slots, optimal_time)
                result.alternative_times[platform] = alternatives
                
                # Predict performance
                performance = await self._predict_performance(
                    platform, 
                    optimal_time, 
                    request
                )
                result.performance_predictions[platform] = performance
            
            # Calculate overall optimization score
            result.optimization_score = await self._calculate_optimization_score(result)
            
            # Generate recommendations
            result.recommendations = await self._generate_scheduling_recommendations(
                request, 
                result
            )
            
            self.logger.info(f"Schedule optimization completed for {request.content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Schedule optimization failed: {str(e)}")
            return SchedulingResult(
                content_id=request.content_id,
                success=False,
                warnings=[f"Optimization failed: {str(e)}"]
            )
    
    async def _analyze_audience_timezones(
        self, 
        request: SchedulingRequest
    ) -> Dict[str, Any]:
        """Analyze audience timezone distribution"""
        
        target_timezones = self.AUDIENCE_TIMEZONES.get(
            request.target_audience, 
            ["UTC"]
        )
        
        # Calculate timezone weights based on audience segment
        timezone_weights = {}
        
        if request.target_audience == AudienceSegment.GLOBAL:
            # Distribute evenly across major timezones
            all_timezones = []
            for tz_list in self.AUDIENCE_TIMEZONES.values():
                all_timezones.extend(tz_list)
            
            weight_per_tz = 1.0 / len(all_timezones)
            for tz in all_timezones:
                timezone_weights[tz] = weight_per_tz
        else:
            # Focus on specific region
            weight_per_tz = 1.0 / len(target_timezones)
            for tz in target_timezones:
                timezone_weights[tz] = weight_per_tz
        
        return {
            "target_timezones": target_timezones,
            "timezone_weights": timezone_weights,
            "primary_timezone": target_timezones[0] if target_timezones else "UTC"
        }
    
    async def _generate_time_slots(
        self,
        platform: str,
        request: SchedulingRequest,
        audience_analysis: Dict[str, Any]
    ) -> List[TimeSlot]:
        """Generate potential time slots for platform"""
        
        time_slots = []
        platform_config = self.PLATFORM_OPTIMAL_TIMES.get(platform.lower(), {})
        
        start_date, end_date = request.preferred_date_range
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            # Skip weekends if requested
            if request.exclude_weekends and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Generate slots for this day
            day_slots = await self._generate_day_slots(
                current_date,
                platform_config,
                audience_analysis,
                request
            )
            time_slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        return sorted(time_slots, key=lambda x: x.confidence_score, reverse=True)
    
    async def _generate_day_slots(
        self,
        date: datetime.date,
        platform_config: Dict[str, Any],
        audience_analysis: Dict[str, Any],
        request: SchedulingRequest
    ) -> List[TimeSlot]:
        """
Generate time slots for a specific day"""
        
        slots = []
        is_weekend = date.weekday() >= 5
        
        # Get optimal hours for this platform
        if is_weekend:
            optimal_hours = platform_config.get("weekends", [])
        else:
            optimal_hours = platform_config.get("weekdays", [])
        
        # Calculate day priority
        day_priority = self._calculate_day_priority(date, platform_config)
        
        for hour in optimal_hours:
            # Create datetime in request timezone
            request_tz = pytz.timezone(request.timezone)
            slot_time = request_tz.localize(
                datetime.combine(date, datetime.min.time().replace(hour=hour))
            )
            
            # Convert to UTC for storage
            utc_time = slot_time.astimezone(pytz.UTC)
            
            # Calculate slot score based on multiple factors
            slot_score = await self._calculate_slot_score(
                utc_time,
                audience_analysis,
                platform_config,
                request
            )
            
            # Determine priority level
            if slot_score >= 0.8:
                priority = TimeSlotPriority.PEAK
            elif slot_score >= 0.6:
                priority = TimeSlotPriority.HIGH
            elif slot_score >= 0.4:
                priority = TimeSlotPriority.MEDIUM
            else:
                priority = TimeSlotPriority.LOW
            
            # Estimate reach and engagement
            estimated_reach = int(10000 * slot_score * (1 + np.random.normal(0, 0.1)))
            estimated_engagement = slot_score * 5.0 * (1 + np.random.normal(0, 0.1))
            
            slot = TimeSlot(
                start_time=utc_time,
                end_time=utc_time + timedelta(hours=1),
                priority=priority,
                estimated_reach=max(1000, estimated_reach),
                estimated_engagement=max(0.5, estimated_engagement),
                confidence_score=slot_score,
                timezone=request.timezone
            )
            
            slots.append(slot)
        
        return slots
    
    def _calculate_day_priority(
        self, 
        date: datetime.date, 
        platform_config: Dict[str, Any]
    ) -> float:
        """Calculate priority score for a specific day"""
        
        peak_days = platform_config.get("peak_days", [])
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        
        if weekday in peak_days:
            return 1.0
        elif weekday < 5:  # Weekday
            return 0.7
        else:  # Weekend
            return 0.5
    
    async def _calculate_slot_score(
        self,
        slot_time: datetime,
        audience_analysis: Dict[str, Any],
        platform_config: Dict[str, Any],
        request: SchedulingRequest
    ) -> float:
        """Calculate comprehensive score for a time slot"""
        
        scores = []
        
        # Base platform optimization score
        platform_score = self._get_platform_time_score(slot_time, platform_config)
        scores.append(platform_score * 0.4)
        
        # Audience timezone alignment score
        audience_score = await self._get_audience_alignment_score(
            slot_time, 
            audience_analysis
        )
        scores.append(audience_score * 0.3)
        
        # Historical performance score (if available)
        if request.previous_posts_data:
            historical_score = await self._get_historical_performance_score(
                slot_time, 
                request.previous_posts_data
            )
            scores.append(historical_score * 0.2)
        else:
            scores.append(0.5 * 0.2)  # Neutral score
        
        # Competition avoidance score
        competition_score = await self._get_competition_avoidance_score(slot_time)
        scores.append(competition_score * 0.1)
        
        return sum(scores)
    
    def _get_platform_time_score(
        self, 
        slot_time: datetime, 
        platform_config: Dict[str, Any]
    ) -> float:
        """
Get score based on platform optimal times"""
        
        hour = slot_time.hour
        weekday = slot_time.weekday()
        
        is_weekend = weekday >= 5
        if is_weekend:
            optimal_hours = platform_config.get("weekends", [])
        else:
            optimal_hours = platform_config.get("weekdays", [])
        
        if hour in optimal_hours:
            return 1.0
        
        # Calculate proximity to optimal hours
        if optimal_hours:
            min_distance = min(abs(hour - opt_hour) for opt_hour in optimal_hours)
            if min_distance <= 2:
                return 1.0 - (min_distance * 0.2)
        
        return 0.3  # Base score for non-optimal times
    
    async def _get_audience_alignment_score(
        self,
        slot_time: datetime,
        audience_analysis: Dict[str, Any]
    ) -> float:
        """Calculate audience timezone alignment score"""
        
        timezone_weights = audience_analysis.get("timezone_weights", {})
        if not timezone_weights:
            return 0.5
        
        total_score = 0.0
        
        for tz_name, weight in timezone_weights.items():
            try:
                tz = pytz.timezone(tz_name)
                local_time = slot_time.astimezone(tz)
                local_hour = local_time.hour
                
                # Score based on general online activity patterns
                if 8 <= local_hour <= 10:  # Morning
                    hour_score = 0.7
                elif 12 <= local_hour <= 14:  # Lunch
                    hour_score = 0.8
                elif 17 <= local_hour <= 22:  # Evening prime time
                    hour_score = 1.0
                elif 22 <= local_hour <= 24 or 0 <= local_hour <= 2:  # Late night
                    hour_score = 0.4
                else:  # Other times
                    hour_score = 0.3
                
                total_score += hour_score * weight
                
            except Exception:
                # Invalid timezone, skip
                continue
        
        return min(1.0, total_score)
    
    async def _get_historical_performance_score(
        self,
        slot_time: datetime,
        previous_posts_data: List[Dict]
    ) -> float:
        """Calculate score based on historical performance"""
        
        if not previous_posts_data:
            return 0.5
        
        hour = slot_time.hour
        weekday = slot_time.weekday()
        
        # Find similar time slots in historical data
        similar_posts = []
        for post in previous_posts_data:
            post_time = datetime.fromisoformat(post.get("published_at", ""))
            if (abs(post_time.hour - hour) <= 1 and 
                post_time.weekday() == weekday):
                similar_posts.append(post)
        
        if not similar_posts:
            return 0.5
        
        # Calculate average performance
        total_engagement = sum(
            post.get("engagement_rate", 0) for post in similar_posts
        )
        avg_engagement = total_engagement / len(similar_posts)
        
        # Normalize to 0-1 scale (assuming max engagement rate of 10%)
        return min(1.0, avg_engagement / 10.0)
    
    async def _get_competition_avoidance_score(self, slot_time: datetime) -> float:
        """Calculate score for avoiding competition"""
        
        # This would integrate with competitor analysis
        # For now, return a base score with some variation
        hour = slot_time.hour
        
        # Avoid peak hours when competition is highest
        if hour in [12, 18, 20]:  # Peak competition hours
            return 0.6
        elif hour in [9, 15, 21]:  # Medium competition
            return 0.8
        else:
            return 1.0
    
    async def _select_optimal_time(
        self,
        time_slots: List[TimeSlot],
        strategy: SchedulingStrategy
    ) -> datetime:
        """
Select optimal time based on strategy"""
        
        if not time_slots:
            return datetime.utcnow() + timedelta(hours=1)
        
        if strategy == SchedulingStrategy.MAXIMUM_REACH:
            return max(time_slots, key=lambda x: x.estimated_reach).start_time
        elif strategy == SchedulingStrategy.MAXIMUM_ENGAGEMENT:
            return max(time_slots, key=lambda x: x.estimated_engagement).start_time
        elif strategy == SchedulingStrategy.BALANCED_DISTRIBUTION:
            # Balance between reach and engagement
            best_slot = max(
                time_slots,
                key=lambda x: (x.estimated_reach * 0.5 + x.estimated_engagement * 1000 * 0.5)
            )
            return best_slot.start_time
        else:
            # Default to highest confidence score
            return max(time_slots, key=lambda x: x.confidence_score).start_time
    
    async def _generate_alternatives(
        self,
        time_slots: List[TimeSlot],
        optimal_time: datetime
    ) -> List[datetime]:
        """
Generate alternative time options"""
        
        # Filter out the selected optimal time and get top alternatives
        alternatives = [
            slot.start_time for slot in time_slots 
            if slot.start_time != optimal_time
        ]
        
        # Sort by confidence score and return top 3
        time_slots_filtered = [
            slot for slot in time_slots 
            if slot.start_time != optimal_time
        ]
        time_slots_filtered.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return [slot.start_time for slot in time_slots_filtered[:3]]
    
    async def _predict_performance(
        self,
        platform: str,
        scheduled_time: datetime,
        request: SchedulingRequest
    ) -> Dict[str, float]:
        """
Predict performance metrics for scheduled time"""
        
        # Base performance metrics by platform
        base_metrics = {
            "youtube": {"views": 5000, "likes": 250, "comments": 50, "shares": 25},
            "instagram": {"reach": 3000, "likes": 180, "comments": 30, "saves": 45},
            "tiktok": {"views": 10000, "likes": 800, "comments": 120, "shares": 200},
            "twitter": {"impressions": 2000, "likes": 100, "retweets": 25, "replies": 15},
            "spotify": {"streams": 1500, "saves": 180, "playlist_adds": 45}
        }
        
        platform_base = base_metrics.get(platform.lower(), {
            "reach": 2000, "engagement": 100
        })
        
        # Apply time-based multipliers
        hour = scheduled_time.hour
        if 17 <= hour <= 21:  # Prime time
            multiplier = 1.3
        elif 12 <= hour <= 14:  # Lunch time
            multiplier = 1.1
        elif 8 <= hour <= 10:  # Morning
            multiplier = 0.9
        else:
            multiplier = 0.7
        
        # Calculate predicted metrics
        predictions = {}
        for metric, base_value in platform_base.items():
            predicted_value = base_value * multiplier * (1 + np.random.normal(0, 0.1))
            predictions[metric] = max(0, int(predicted_value))
        
        return predictions
    
    async def _calculate_optimization_score(self, result: SchedulingResult) -> float:
        """Calculate overall optimization score"""
        
        if not result.recommended_schedule:
            return 0.0
        
        # Calculate average confidence from time slot selections
        # This would be based on the actual confidence scores of selected slots
        # For now, simulate based on number of platforms optimized
        
        platform_count = len(result.recommended_schedule)
        base_score = min(1.0, platform_count / 5.0)  # Normalize for up to 5 platforms
        
        # Add bonus for having performance predictions
        if result.performance_predictions:
            base_score += 0.1
        
        # Add bonus for having alternatives
        if result.alternative_times:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _generate_scheduling_recommendations(
        self,
        request: SchedulingRequest,
        result: SchedulingResult
    ) -> List[str]:
        """
Generate scheduling recommendations"""
        
        recommendations = []
        
        if request.strategy == SchedulingStrategy.MAXIMUM_REACH:
            recommendations.append(
                "Focus on peak hours to maximize audience reach"
            )
        elif request.strategy == SchedulingStrategy.MAXIMUM_ENGAGEMENT:
            recommendations.append(
                "Prioritize engagement-friendly time slots for better interaction"
            )
        
        if request.target_audience == AudienceSegment.GLOBAL:
            recommendations.append(
                "Consider staggered posting across timezones for global reach"
            )
        
        # Platform-specific recommendations
        for platform in request.target_platforms:
            if platform.lower() == "tiktok":
                recommendations.append(
                    "TikTok: Post during evening hours for maximum engagement"
                )
            elif platform.lower() == "linkedin":
                recommendations.append(
                    "LinkedIn: Avoid weekends, focus on weekday business hours"
                )
            elif platform.lower() == "instagram":
                recommendations.append(
                    "Instagram: Use Stories to promote your main post"
                )
        
        return recommendations
    
    async def create_schedule_template(
        self,
        user_id: int,
        template_name: str,
        content_type: str,
        target_platforms: List[str],
        schedule_pattern: Dict[str, Any],
        strategy: SchedulingStrategy,
        timezone: str = "UTC"
    ) -> Optional[ScheduleTemplate]:
        """Create a reusable schedule template"""
        
        if not self.db_session:
            self.logger.error("Database session not available")
            return None
        
        try:
            template = ScheduleTemplate(
                user_id=user_id,
                template_name=template_name,
                content_type=content_type,
                target_platforms=target_platforms,
                schedule_pattern=schedule_pattern,
                strategy=strategy.value,
                timezone=timezone
            )
            
            self.db_session.add(template)
            await self.db_session.commit()
            
            self.logger.info(f"Schedule template created: {template_name}")
            return template
            
        except Exception as e:
            self.logger.error(f"Failed to create schedule template: {str(e)}")
            await self.db_session.rollback()
            return None
    
    async def get_user_schedule_templates(
        self,
        user_id: int
    ) -> List[ScheduleTemplate]:
        """Get user's schedule templates"""
        
        if not self.db_session:
            return []
        
        try:
            templates = await self.db_session.query(ScheduleTemplate).filter(
                ScheduleTemplate.user_id == user_id
            ).order_by(ScheduleTemplate.usage_count.desc()).all()
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to get schedule templates: {str(e)}")
            return []

# Export all classes for external use
__all__ = [
    "SchedulingEngine",
    "SchedulingRequest",
    "SchedulingResult",
    "TimeSlot",
    "ScheduleTemplate",
    "PerformanceHistory",
    "SchedulingStrategy",
    "TimeSlotPriority",
    "AudienceSegment"
]
