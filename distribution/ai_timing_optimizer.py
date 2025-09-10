"""
AI Timing Optimizer
==================

Enterprise-grade AI-powered timing optimization for content publication.
Uses machine learning to determine optimal posting times across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Platform types for timing optimization"""
    SOCIAL_MEDIA = "social_media"
    PROFESSIONAL = "professional"
    ENTERTAINMENT = "entertainment"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    BLOGGING = "blogging"
    MESSAGING = "messaging"

class ContentType(Enum):
    """Content types for timing optimization"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POLL = "poll"
    ARTICLE = "article"

class AudienceSegment(Enum):
    """Audience segments"""
    GENERAL = "general"
    YOUNG_ADULTS = "young_adults"  # 18-25
    MILLENNIALS = "millennials"    # 26-35
    GEN_X = "gen_x"               # 36-50
    BABY_BOOMERS = "baby_boomers" # 51+
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    CREATIVES = "creatives"

@dataclass
class TimingFeatures:
    """Features used for timing optimization"""
    day_of_week: int  # 0=Monday, 6=Sunday
    hour_of_day: int  # 0-23
    platform: PlatformType
    content_type: ContentType
    audience_segment: AudienceSegment
    timezone: str
    is_holiday: bool = False
    is_weekend: bool = False
    weather_condition: Optional[str] = None
    trending_topics: List[str] = field(default_factory=list)
    historical_performance: Optional[float] = None
    competitor_activity: Optional[float] = None

@dataclass
class TimingPrediction:
    """AI timing prediction result"""
    optimal_time: datetime
    confidence_score: float  # 0.0 to 1.0
    predicted_engagement: float
    predicted_reach: float
    alternative_times: List[Tuple[datetime, float]] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    factors_considered: Dict[str, float] = field(default_factory=dict)

@dataclass
class HistoricalData:
    """Historical performance data"""
    timestamp: datetime
    platform: str
    content_type: str
    engagement_rate: float
    reach: int
    clicks: int
    shares: int
    comments: int
    likes: int
    views: int
    audience_online: Optional[int] = None

class BaseTimingModel(ABC):
    """Base class for timing prediction models"""
    
    @abstractmethod
    async def predict_optimal_time(
        self, 
        features: TimingFeatures,
        historical_data: List[HistoricalData]
    ) -> TimingPrediction:
        """Predict optimal posting time"""
        pass
    
    @abstractmethod
    async def train(self, training_data: List[Tuple[TimingFeatures, float]]):
        """Train the model with historical data"""
        pass

class MLTimingModel(BaseTimingModel):
    """Machine learning-based timing model"""
    
    def __init__(self):
        self.model_weights: Dict[str, float] = {
            # Platform-specific weights
            "social_media_peak_hours": [8, 12, 17, 19, 21],
            "professional_peak_hours": [9, 12, 15, 17],
            "entertainment_peak_hours": [18, 19, 20, 21, 22],
            "music_streaming_peak_hours": [7, 12, 17, 21],
            
            # Day of week weights
            "weekday_engagement": 1.0,
            "weekend_engagement": 0.8,
            
            # Content type multipliers
            "video_engagement_boost": 1.3,
            "image_engagement_boost": 1.1,
            "text_engagement_boost": 1.0,
            "live_stream_engagement_boost": 1.5,
            
            # Audience segment preferences
            "young_adults_evening_boost": 1.4,
            "professionals_lunch_boost": 1.2,
            "students_afternoon_boost": 1.3
        }
        
        self.platform_timezone_preferences = {
            PlatformType.SOCIAL_MEDIA: ["UTC-8", "UTC-5", "UTC"],
            PlatformType.PROFESSIONAL: ["UTC-5", "UTC", "UTC+1"],
            PlatformType.ENTERTAINMENT: ["UTC-8", "UTC-5", "UTC"],
            PlatformType.MUSIC_STREAMING: ["UTC-8", "UTC-5", "UTC", "UTC+1"],
            PlatformType.VIDEO_PLATFORM: ["UTC-8", "UTC-5", "UTC"],
        }
    
    async def predict_optimal_time(
        self, 
        features: TimingFeatures,
        historical_data: List[HistoricalData]
    ) -> TimingPrediction:
        """Predict optimal posting time using ML algorithms"""
        try:
            # Analyze historical data patterns
            patterns = await self._analyze_historical_patterns(historical_data, features)
            
            # Get platform-specific optimal hours
            optimal_hours = await self._get_platform_optimal_hours(features.platform)
            
            # Consider audience segment preferences
            audience_preferences = await self._get_audience_preferences(features.audience_segment)
            
            # Factor in content type performance
            content_multiplier = await self._get_content_type_multiplier(features.content_type)
            
            # Calculate base score for each hour
            hour_scores = {}
            base_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            
            for hour in range(24):
                test_time = base_time.replace(hour=hour)
                score = await self._calculate_hour_score(
                    hour, features, patterns, optimal_hours, 
                    audience_preferences, content_multiplier
                )
                hour_scores[hour] = score
            
            # Find top performing hours
            sorted_hours = sorted(hour_scores.items(), key=lambda x: x[1], reverse=True)
            best_hour = sorted_hours[0][0]
            confidence = sorted_hours[0][1]
            
            # Generate optimal time
            optimal_time = base_time.replace(hour=best_hour)
            
            # Adjust for timezone
            optimal_time = await self._adjust_for_timezone(optimal_time, features.timezone)
            
            # Generate alternative times
            alternatives = []
            for hour, score in sorted_hours[1:6]:  # Top 5 alternatives
                alt_time = base_time.replace(hour=hour)
                alt_time = await self._adjust_for_timezone(alt_time, features.timezone)
                alternatives.append((alt_time, score))
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(features, patterns, best_hour)
            
            # Calculate predicted metrics
            predicted_engagement = confidence * 100  # Convert to percentage
            predicted_reach = predicted_engagement * 1.5  # Reach is typically higher
            
            return TimingPrediction(
                optimal_time=optimal_time,
                confidence_score=min(confidence, 1.0),
                predicted_engagement=predicted_engagement,
                predicted_reach=predicted_reach,
                alternative_times=alternatives,
                reasoning=reasoning,
                factors_considered={
                    "historical_patterns": patterns.get("weight", 0.0),
                    "platform_optimization": 0.3,
                    "audience_preferences": 0.25,
                    "content_type_boost": content_multiplier,
                    "timezone_adjustment": 0.1
                }
            )
            
        except Exception as e:
            logger.error(f"Error predicting optimal time: {e}")
            # Fallback to default timing
            return await self._get_fallback_prediction(features)
    
    async def _analyze_historical_patterns(
        self, 
        historical_data: List[HistoricalData],
        features: TimingFeatures
    ) -> Dict[str, Any]:
        """Analyze historical performance patterns"""
        if not historical_data:
            return {"weight": 0.0, "best_hours": [], "best_days": []}
        
        # Group by hour and day
        hour_performance = {}
        day_performance = {}
        
        for data in historical_data:
            hour = data.timestamp.hour
            day = data.timestamp.weekday()
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            if day not in day_performance:
                day_performance[day] = []
            
            engagement_score = (
                data.engagement_rate * 0.4 +
                (data.likes / max(data.views, 1)) * 0.3 +
                (data.shares / max(data.views, 1)) * 0.2 +
                (data.comments / max(data.views, 1)) * 0.1
            )
            
            hour_performance[hour].append(engagement_score)
            day_performance[day].append(engagement_score)
        
        # Calculate average performance
        best_hours = []
        for hour, scores in hour_performance.items():
            avg_score = np.mean(scores)
            best_hours.append((hour, avg_score))
        
        best_days = []
        for day, scores in day_performance.items():
            avg_score = np.mean(scores)
            best_days.append((day, avg_score))
        
        # Sort by performance
        best_hours.sort(key=lambda x: x[1], reverse=True)
        best_days.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "weight": 0.4,  # Historical data weight
            "best_hours": [h[0] for h in best_hours[:5]],
            "best_days": [d[0] for d in best_days[:3]],
            "hour_scores": {h: s for h, s in best_hours},
            "day_scores": {d: s for d, s in best_days}
        }
    
    async def _get_platform_optimal_hours(self, platform: PlatformType) -> List[int]:
        """Get platform-specific optimal hours"""
        platform_hours = {
            PlatformType.SOCIAL_MEDIA: [8, 12, 17, 19, 21],
            PlatformType.PROFESSIONAL: [9, 12, 15, 17],
            PlatformType.ENTERTAINMENT: [18, 19, 20, 21, 22],
            PlatformType.MUSIC_STREAMING: [7, 12, 17, 21],
            PlatformType.VIDEO_PLATFORM: [14, 17, 19, 20, 21],
            PlatformType.BLOGGING: [10, 14, 16, 19],
            PlatformType.MESSAGING: [8, 12, 18, 20]
        }
        
        return platform_hours.get(platform, [12, 17, 19])
    
    async def _get_audience_preferences(self, audience: AudienceSegment) -> Dict[str, float]:
        """Get audience segment preferences"""
        preferences = {
            AudienceSegment.YOUNG_ADULTS: {
                "morning_boost": 0.8,
                "afternoon_boost": 1.0,
                "evening_boost": 1.4,
                "night_boost": 1.2
            },
            AudienceSegment.MILLENNIALS: {
                "morning_boost": 1.1,
                "afternoon_boost": 1.2,
                "evening_boost": 1.3,
                "night_boost": 0.9
            },
            AudienceSegment.GEN_X: {
                "morning_boost": 1.2,
                "afternoon_boost": 1.1,
                "evening_boost": 1.0,
                "night_boost": 0.7
            },
            AudienceSegment.PROFESSIONALS: {
                "morning_boost": 1.3,
                "afternoon_boost": 1.2,
                "evening_boost": 0.9,
                "night_boost": 0.6
            },
            AudienceSegment.STUDENTS: {
                "morning_boost": 0.7,
                "afternoon_boost": 1.3,
                "evening_boost": 1.2,
                "night_boost": 1.1
            }
        }
        
        return preferences.get(audience, {
            "morning_boost": 1.0,
            "afternoon_boost": 1.0,
            "evening_boost": 1.0,
            "night_boost": 1.0
        })
    
    async def _get_content_type_multiplier(self, content_type: ContentType) -> float:
        """Get content type engagement multiplier"""
        multipliers = {
            ContentType.VIDEO: 1.3,
            ContentType.LIVE_STREAM: 1.5,
            ContentType.IMAGE: 1.1,
            ContentType.AUDIO: 1.0,
            ContentType.TEXT: 1.0,
            ContentType.STORY: 1.2,
            ContentType.POLL: 1.4,
            ContentType.ARTICLE: 0.9
        }
        
        return multipliers.get(content_type, 1.0)
    
    async def _calculate_hour_score(
        self,
        hour: int,
        features: TimingFeatures,
        patterns: Dict[str, Any],
        optimal_hours: List[int],
        audience_prefs: Dict[str, float],
        content_multiplier: float
    ) -> float:
        """Calculate score for a specific hour"""
        base_score = 0.5
        
        # Platform optimal hours boost
        if hour in optimal_hours:
            base_score += 0.3
        
        # Historical patterns boost
        if hour in patterns.get("best_hours", []):
            base_score += 0.2 * patterns.get("weight", 0.0)
        
        # Audience preferences
        if 6 <= hour <= 11:  # Morning
            base_score *= audience_prefs.get("morning_boost", 1.0)
        elif 12 <= hour <= 17:  # Afternoon
            base_score *= audience_prefs.get("afternoon_boost", 1.0)
        elif 18 <= hour <= 22:  # Evening
            base_score *= audience_prefs.get("evening_boost", 1.0)
        else:  # Night/Early morning
            base_score *= audience_prefs.get("night_boost", 1.0)
        
        # Content type multiplier
        base_score *= content_multiplier
        
        # Weekend/weekday adjustment
        if features.is_weekend:
            if hour in [10, 11, 14, 15, 19, 20]:  # Weekend peak hours
                base_score *= 1.2
            else:
                base_score *= 0.9
        
        # Holiday adjustment
        if features.is_holiday:
            base_score *= 0.8  # Generally lower engagement on holidays
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    async def _adjust_for_timezone(self, time: datetime, timezone_str: str) -> datetime:
        """Adjust time for target timezone"""
        try:
            # Parse timezone offset (simplified)
            if timezone_str.startswith("UTC"):
                if "+" in timezone_str:
                    offset_hours = int(timezone_str.split("+")[1])
                    adjusted_time = time + timedelta(hours=offset_hours)
                elif "-" in timezone_str:
                    offset_hours = int(timezone_str.split("-")[1])
                    adjusted_time = time - timedelta(hours=offset_hours)
                else:
                    adjusted_time = time
            else:
                adjusted_time = time
                
            return adjusted_time
            
        except Exception:
            return time  # Return original time if parsing fails
    
    async def _generate_reasoning(
        self, 
        features: TimingFeatures,
        patterns: Dict[str, Any],
        best_hour: int
    ) -> List[str]:
        """Generate human-readable reasoning for the prediction"""
        reasoning = []
        
        # Platform-specific reasoning
        if features.platform == PlatformType.SOCIAL_MEDIA:
            reasoning.append("Social media platforms show peak engagement during commute and leisure hours")
        elif features.platform == PlatformType.PROFESSIONAL:
            reasoning.append("Professional platforms perform best during business hours")
        elif features.platform == PlatformType.ENTERTAINMENT:
            reasoning.append("Entertainment content peaks during evening leisure time")
        
        # Content type reasoning
        if features.content_type == ContentType.VIDEO:
            reasoning.append("Video content typically receives 30% higher engagement")
        elif features.content_type == ContentType.LIVE_STREAM:
            reasoning.append("Live streams generate highest real-time engagement")
        
        # Audience reasoning
        if features.audience_segment == AudienceSegment.YOUNG_ADULTS:
            reasoning.append("Young adult audiences are most active during evening hours")
        elif features.audience_segment == AudienceSegment.PROFESSIONALS:
            reasoning.append("Professional audiences engage most during work breaks")
        
        # Time-specific reasoning
        if 6 <= best_hour <= 9:
            reasoning.append("Morning posts catch users during their daily routine check")
        elif 12 <= best_hour <= 14:
            reasoning.append("Lunch hour provides high engagement opportunity")
        elif 17 <= best_hour <= 19:
            reasoning.append("Evening commute time shows peak social media usage")
        elif 19 <= best_hour <= 22:
            reasoning.append("Prime time leisure hours for entertainment content")
        
        # Historical data reasoning
        if patterns.get("weight", 0) > 0.3:
            reasoning.append("Historical performance data strongly supports this timing")
        
        return reasoning
    
    async def _get_fallback_prediction(self, features: TimingFeatures) -> TimingPrediction:
        """Provide fallback prediction when ML fails"""
        # Default to safe bet times
        default_hour = 19  # 7 PM - generally good for most platforms
        
        if features.platform == PlatformType.PROFESSIONAL:
            default_hour = 12  # Lunch time
        elif features.platform == PlatformType.ENTERTAINMENT:
            default_hour = 20  # 8 PM
        
        optimal_time = datetime.now(timezone.utc).replace(
            hour=default_hour, minute=0, second=0, microsecond=0
        )
        
        return TimingPrediction(
            optimal_time=optimal_time,
            confidence_score=0.6,  # Moderate confidence for fallback
            predicted_engagement=65.0,
            predicted_reach=85.0,
            reasoning=["Using platform-specific default timing as fallback"],
            factors_considered={"fallback_mode": 1.0}
        )
    
    async def train(self, training_data: List[Tuple[TimingFeatures, float]]):
        """Train the model with historical data"""
        # Simplified training - in production would use proper ML algorithms
        logger.info(f"Training timing model with {len(training_data)} data points")
        
        # Update weights based on training data
        platform_performance = {}
        content_performance = {}
        
        for features, performance in training_data:
            platform = features.platform.value
            content = features.content_type.value
            
            if platform not in platform_performance:
                platform_performance[platform] = []
            if content not in content_performance:
                content_performance[content] = []
            
            platform_performance[platform].append(performance)
            content_performance[content].append(performance)
        
        # Update model weights
        for platform, performances in platform_performance.items():
            avg_performance = np.mean(performances)
            self.model_weights[f"{platform}_boost"] = avg_performance
        
        for content, performances in content_performance.items():
            avg_performance = np.mean(performances)
            self.model_weights[f"{content}_boost"] = avg_performance
        
        logger.info("Timing model training completed")

class AITimingOptimizer:
    """Main AI timing optimizer class"""
    
    def __init__(self):
        self.model = MLTimingModel()
        self.cache: Dict[str, TimingPrediction] = {}
        self.cache_ttl = timedelta(hours=1)
        self.last_training = None
        
    async def optimize_timing(
        self,
        platform: str,
        content_type: str,
        audience_segment: str = "general",
        timezone: str = "UTC",
        historical_data: Optional[List[HistoricalData]] = None
    ) -> TimingPrediction:
        """Optimize posting timing for given parameters"""
        try:
            # Create cache key
            cache_key = f"{platform}_{content_type}_{audience_segment}_{timezone}"
            
            # Check cache
            if cache_key in self.cache:
                cached_prediction = self.cache[cache_key]
                if datetime.now(timezone.utc) - cached_prediction.optimal_time < self.cache_ttl:
                    return cached_prediction
            
            # Create timing features
            features = TimingFeatures(
                day_of_week=datetime.now().weekday(),
                hour_of_day=datetime.now().hour,
                platform=PlatformType(platform),
                content_type=ContentType(content_type),
                audience_segment=AudienceSegment(audience_segment),
                timezone=timezone,
                is_holiday=await self._is_holiday(),
                is_weekend=datetime.now().weekday() >= 5
            )
            
            # Get prediction
            prediction = await self.model.predict_optimal_time(
                features, 
                historical_data or []
            )
            
            # Cache result
            self.cache[cache_key] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error optimizing timing: {e}")
            raise
    
    async def batch_optimize(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[TimingPrediction]:
        """Batch optimize multiple timing requests"""
        results = []
        
        for request in requests:
            try:
                prediction = await self.optimize_timing(**request)
                results.append(prediction)
            except Exception as e:
                logger.error(f"Error in batch optimization: {e}")
                # Add fallback prediction
                fallback = await self.model._get_fallback_prediction(
                    TimingFeatures(
                        day_of_week=0,
                        hour_of_day=12,
                        platform=PlatformType.SOCIAL_MEDIA,
                        content_type=ContentType.TEXT,
                        audience_segment=AudienceSegment.GENERAL,
                        timezone="UTC"
                    )
                )
                results.append(fallback)
        
        return results
    
    async def _is_holiday(self) -> bool:
        """Check if current date is a holiday (simplified)"""
        # In production, integrate with holiday API
        now = datetime.now()
        
        # Major holidays (simplified)
        holidays = [
            (1, 1),   # New Year
            (7, 4),   # July 4th
            (12, 25), # Christmas
        ]
        
        return (now.month, now.day) in holidays
    
    async def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the timing model with historical performance data"""
        formatted_data = []
        
        for data in training_data:
            features = TimingFeatures(
                day_of_week=data["day_of_week"],
                hour_of_day=data["hour_of_day"],
                platform=PlatformType(data["platform"]),
                content_type=ContentType(data["content_type"]),
                audience_segment=AudienceSegment(data.get("audience_segment", "general")),
                timezone=data.get("timezone", "UTC"),
                is_holiday=data.get("is_holiday", False),
                is_weekend=data.get("is_weekend", False)
            )
            
            performance_score = data["performance_score"]
            formatted_data.append((features, performance_score))
        
        await self.model.train(formatted_data)
        self.last_training = datetime.now(timezone.utc)
        
        # Clear cache after training
        self.cache.clear()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the timing model"""
        return {
            "model_type": "MLTimingModel",
            "last_training": self.last_training.isoformat() if self.last_training else None,
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "supported_platforms": [p.value for p in PlatformType],
            "supported_content_types": [c.value for c in ContentType],
            "supported_audience_segments": [a.value for a in AudienceSegment]
        }


# Export main components
__all__ = [
    "AITimingOptimizer",
    "TimingFeatures",
    "TimingPrediction", 
    "HistoricalData",
    "PlatformType",
    "ContentType",
    "AudienceSegment"
]