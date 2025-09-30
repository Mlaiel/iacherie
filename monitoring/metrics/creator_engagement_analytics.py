"""🎯 Creator Engagement Analytics - ML-Powered Engagement Intelligence
================================================================

Advanced creator engagement analytics with machine learning predictions for the IA Chérie platform.
Provides deep insights into creator behavior, audience interaction, content performance,
and predictive analytics for creator success optimization.

Enhanced Features:
- ML-powered engagement prediction algorithms
- Real-time creator retention analytics
- Advanced audience growth tracking with churn prediction
- Content virality detection and prediction
- Cross-platform engagement correlation analysis
- Creator journey optimization insights
- Behavioral pattern recognition and classification
- Predictive content performance modeling

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class EngagementMetricType(Enum):
    """Types of engagement metrics for creator analytics."""
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    VIEWS = "views"
    SAVES = "saves"
    CLICK_THROUGH = "click_through"
    WATCH_TIME = "watch_time"
    INTERACTION_RATE = "interaction_rate"
    RETENTION_RATE = "retention_rate"
    GROWTH_RATE = "growth_rate"
    VIRALITY_SCORE = "virality_score"
    AUDIENCE_QUALITY = "audience_quality"


class CreatorTier(Enum):
    """Creator tier classification based on performance."""
    MICRO = "micro"           # 1K-10K followers
    NANO = "nano"             # <1K followers
    MACRO = "macro"           # 10K-100K followers
    MEGA = "mega"             # 100K-1M followers
    CELEBRITY = "celebrity"   # >1M followers


class PlatformType(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


@dataclass
class EngagementEvent:
    """Individual engagement event data structure."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    content_id: str = ""
    platform: PlatformType = PlatformType.INSTAGRAM
    metric_type: EngagementMetricType = EngagementMetricType.LIKES
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    user_demographics: Dict[str, Any] = field(default_factory=dict)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorProfile:
    """Creator profile with engagement metrics."""
    creator_id: str = ""
    username: str = ""
    tier: CreatorTier = CreatorTier.NANO
    platforms: Set[PlatformType] = field(default_factory=set)
    total_followers: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    engagement_score: float = 0.0
    growth_rate: float = 0.0
    content_categories: List[str] = field(default_factory=list)
    demographics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementPrediction:
    """ML-powered engagement prediction results."""
    creator_id: str = ""
    prediction_type: str = ""
    predicted_value: float = 0.0
    confidence_score: float = 0.0
    prediction_horizon: timedelta = field(default_factory=lambda: timedelta(days=7))
    features_importance: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "1.0.0"


class CreatorEngagementAnalytics:
    """Advanced creator engagement analytics with ML predictions."""
    
    def __init__(self):
        """Initialize the creator engagement analytics system."""
        self.events: deque = deque(maxlen=1000000)  # Store last 1M events
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.engagement_cache: Dict[str, Dict] = defaultdict(dict)
        self.predictions_cache: Dict[str, List[EngagementPrediction]] = defaultdict(list)
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # ML Model placeholders (would be actual trained models in production)
        self.engagement_predictor = None
        self.churn_predictor = None
        self.virality_predictor = None
        self.growth_predictor = None
        
        # Configuration
        self.prediction_intervals = [1, 7, 30, 90]  # days
        self.min_data_points = 10
        self.cache_ttl = 3600  # 1 hour
        
        logger.info("CreatorEngagementAnalytics initialized successfully")
    
    async def record_engagement(self, event: EngagementEvent) -> bool:
        """Record a new engagement event."""
        try:
            with self.lock:
                self.events.append(event)
                
                # Update creator profile if needed
                if event.creator_id not in self.creator_profiles:
                    await self._create_creator_profile(event.creator_id)
                
                # Update real-time metrics
                await self._update_realtime_metrics(event)
                
            logger.debug(f"Recorded engagement event: {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording engagement event: {e}")
            return False
    
    async def get_creator_engagement_metrics(
        self, 
        creator_id: str, 
        timeframe: timedelta = timedelta(days=30),
        platforms: Optional[List[PlatformType]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive engagement metrics for a creator."""
        try:
            cache_key = f"{creator_id}_{timeframe.days}_{hash(str(platforms))}"
            
            # Check cache
            if cache_key in self.engagement_cache:
                cached_data = self.engagement_cache[cache_key]
                if (datetime.utcnow() - cached_data['timestamp']).seconds < self.cache_ttl:
                    return cached_data['metrics']
            
            # Calculate metrics
            metrics = await self._calculate_engagement_metrics(creator_id, timeframe, platforms)
            
            # Cache results
            self.engagement_cache[cache_key] = {
                'metrics': metrics,
                'timestamp': datetime.utcnow()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting engagement metrics for creator {creator_id}: {e}")
            return {}
    
    async def predict_engagement(
        self, 
        creator_id: str, 
        prediction_horizon: timedelta = timedelta(days=7)
    ) -> EngagementPrediction:
        """Predict future engagement for a creator using ML."""
        try:
            # Get historical data
            historical_data = await self._get_historical_engagement_data(creator_id)
            
            if len(historical_data) < self.min_data_points:
                logger.warning(f"Insufficient data for creator {creator_id} prediction")
                return EngagementPrediction(
                    creator_id=creator_id,
                    prediction_type="insufficient_data",
                    confidence_score=0.0
                )
            
            # Feature engineering
            features = await self._extract_prediction_features(creator_id, historical_data)
            
            # ML prediction (placeholder - would use actual trained model)
            prediction_value = await self._ml_predict_engagement(features)
            confidence = await self._calculate_prediction_confidence(features, historical_data)
            
            prediction = EngagementPrediction(
                creator_id=creator_id,
                prediction_type="engagement_rate",
                predicted_value=prediction_value,
                confidence_score=confidence,
                prediction_horizon=prediction_horizon,
                features_importance=await self._get_feature_importance(features)
            )
            
            # Cache prediction
            self.predictions_cache[creator_id].append(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting engagement for creator {creator_id}: {e}")
            return EngagementPrediction(creator_id=creator_id, prediction_type="error")
    
    async def analyze_content_virality(self, content_id: str) -> Dict[str, Any]:
        """Analyze content virality potential and performance."""
        try:
            content_events = [
                event for event in self.events 
                if event.content_id == content_id
            ]
            
            if not content_events:
                return {"error": "No data found for content"}
            
            # Calculate virality metrics
            total_engagement = sum(event.value for event in content_events)
            unique_users = len(set(event.user_id for event in content_events if event.user_id))
            time_span = (max(event.timestamp for event in content_events) - 
                        min(event.timestamp for event in content_events)).total_seconds()
            
            engagement_velocity = total_engagement / max(time_span / 3600, 1)  # per hour
            
            # Virality score calculation
            virality_score = await self._calculate_virality_score(content_events)
            
            # Platform distribution
            platform_distribution = defaultdict(int)
            for event in content_events:
                platform_distribution[event.platform.value] += event.value
            
            return {
                "content_id": content_id,
                "total_engagement": total_engagement,
                "unique_users": unique_users,
                "engagement_velocity": engagement_velocity,
                "virality_score": virality_score,
                "platform_distribution": dict(platform_distribution),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "recommendation": await self._get_virality_recommendations(virality_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content virality for {content_id}: {e}")
            return {"error": str(e)}
    
    async def get_cross_platform_correlation(self, creator_id: str) -> Dict[str, Any]:
        """Analyze cross-platform engagement correlation for a creator."""
        try:
            creator_events = [
                event for event in self.events 
                if event.creator_id == creator_id
            ]
            
            if not creator_events:
                return {"error": "No data found for creator"}
            
            # Group by platform
            platform_metrics = defaultdict(lambda: defaultdict(float))
            
            for event in creator_events:
                platform = event.platform.value
                metric_type = event.metric_type.value
                platform_metrics[platform][metric_type] += event.value
            
            # Calculate correlations
            correlations = await self._calculate_platform_correlations(platform_metrics)
            
            # Performance comparison
            platform_performance = {}
            for platform, metrics in platform_metrics.items():
                total_engagement = sum(metrics.values())
                platform_performance[platform] = {
                    "total_engagement": total_engagement,
                    "metrics_breakdown": dict(metrics),
                    "engagement_rate": total_engagement / max(len([
                        e for e in creator_events if e.platform.value == platform
                    ]), 1)
                }
            
            return {
                "creator_id": creator_id,
                "platform_correlations": correlations,
                "platform_performance": platform_performance,
                "best_performing_platform": max(
                    platform_performance.keys(),
                    key=lambda p: platform_performance[p]["total_engagement"]
                ) if platform_performance else None,
                "recommendations": await self._get_cross_platform_recommendations(correlations)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cross-platform correlation for {creator_id}: {e}")
            return {"error": str(e)}
    
    async def predict_churn_risk(self, creator_id: str) -> Dict[str, Any]:
        """Predict creator churn risk using ML algorithms."""
        try:
            # Get creator activity data
            recent_activity = await self._get_recent_activity(creator_id, days=30)
            historical_pattern = await self._get_historical_activity_pattern(creator_id)
            
            # Calculate activity trends
            activity_trend = await self._calculate_activity_trend(recent_activity)
            engagement_trend = await self._calculate_engagement_trend(creator_id)
            
            # ML-based churn prediction (placeholder)
            churn_features = {
                "days_since_last_activity": (datetime.utcnow() - max(
                    event.timestamp for event in recent_activity
                )).days if recent_activity else 999,
                "activity_decline_rate": activity_trend,
                "engagement_decline_rate": engagement_trend,
                "content_frequency": len(recent_activity) / 30,
                "platform_diversity": len(set(event.platform for event in recent_activity))
            }
            
            churn_probability = await self._ml_predict_churn(churn_features)
            
            # Risk classification
            if churn_probability > 0.7:
                risk_level = "HIGH"
            elif churn_probability > 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                "creator_id": creator_id,
                "churn_probability": churn_probability,
                "risk_level": risk_level,
                "key_factors": churn_features,
                "recommendations": await self._get_retention_recommendations(risk_level),
                "predicted_churn_date": (
                    datetime.utcnow() + timedelta(days=int(30 * (1 - churn_probability)))
                ).isoformat() if churn_probability > 0.5 else None
            }
            
        except Exception as e:
            logger.error(f"Error predicting churn risk for creator {creator_id}: {e}")
            return {"error": str(e)}
    
    async def get_audience_growth_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get detailed audience growth analytics and predictions."""
        try:
            growth_data = await self._get_growth_history(creator_id)
            
            if not growth_data:
                return {"error": "No growth data available"}
            
            # Calculate growth metrics
            current_followers = growth_data[-1]["followers"] if growth_data else 0
            growth_rate = await self._calculate_growth_rate(growth_data)
            growth_acceleration = await self._calculate_growth_acceleration(growth_data)
            
            # Predict future growth
            future_growth = await self._predict_audience_growth(creator_id, growth_data)
            
            # Identify growth patterns
            growth_patterns = await self._identify_growth_patterns(growth_data)
            
            return {
                "creator_id": creator_id,
                "current_followers": current_followers,
                "growth_rate_daily": growth_rate["daily"],
                "growth_rate_weekly": growth_rate["weekly"],
                "growth_rate_monthly": growth_rate["monthly"],
                "growth_acceleration": growth_acceleration,
                "growth_patterns": growth_patterns,
                "future_predictions": future_growth,
                "milestones": await self._calculate_milestone_predictions(current_followers, growth_rate),
                "recommendations": await self._get_growth_recommendations(growth_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error getting growth analytics for creator {creator_id}: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _create_creator_profile(self, creator_id: str) -> None:
        """Create a new creator profile."""
        self.creator_profiles[creator_id] = CreatorProfile(
            creator_id=creator_id,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
    
    async def _update_realtime_metrics(self, event: EngagementEvent) -> None:
        """Update real-time metrics for the creator."""
        creator_id = event.creator_id
        if creator_id in self.creator_profiles:
            profile = self.creator_profiles[creator_id]
            profile.last_active = event.timestamp
            profile.platforms.add(event.platform)
    
    async def _calculate_engagement_metrics(
        self, 
        creator_id: str, 
        timeframe: timedelta,
        platforms: Optional[List[PlatformType]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive engagement metrics."""
        cutoff_time = datetime.utcnow() - timeframe
        
        relevant_events = [
            event for event in self.events
            if (event.creator_id == creator_id and 
                event.timestamp >= cutoff_time and
                (platforms is None or event.platform in platforms))
        ]
        
        if not relevant_events:
            return {"error": "No data in specified timeframe"}
        
        # Basic metrics
        total_engagement = sum(event.value for event in relevant_events)
        unique_content = len(set(event.content_id for event in relevant_events))
        total_events = len(relevant_events)
        
        # Engagement by type
        engagement_by_type = defaultdict(float)
        for event in relevant_events:
            engagement_by_type[event.metric_type.value] += event.value
        
        # Time-based metrics
        daily_engagement = defaultdict(float)
        for event in relevant_events:
            day_key = event.timestamp.date()
            daily_engagement[day_key] += event.value
        
        avg_daily_engagement = statistics.mean(daily_engagement.values()) if daily_engagement else 0
        
        return {
            "total_engagement": total_engagement,
            "unique_content_pieces": unique_content,
            "total_events": total_events,
            "avg_daily_engagement": avg_daily_engagement,
            "engagement_by_type": dict(engagement_by_type),
            "daily_breakdown": {str(k): v for k, v in daily_engagement.items()},
            "engagement_rate": total_engagement / max(total_events, 1),
            "content_efficiency": total_engagement / max(unique_content, 1)
        }
    
    async def _get_historical_engagement_data(self, creator_id: str) -> List[Dict]:
        """Get historical engagement data for ML predictions."""
        creator_events = [
            event for event in self.events
            if event.creator_id == creator_id
        ]
        
        # Aggregate by day
        daily_data = defaultdict(lambda: defaultdict(float))
        for event in creator_events:
            day_key = event.timestamp.date()
            daily_data[day_key][event.metric_type.value] += event.value
        
        return [
            {
                "date": day,
                "metrics": dict(metrics),
                "total_engagement": sum(metrics.values())
            }
            for day, metrics in daily_data.items()
        ]
    
    async def _extract_prediction_features(self, creator_id: str, historical_data: List[Dict]) -> Dict[str, float]:
        """Extract features for ML prediction."""
        if not historical_data:
            return {}
        
        engagements = [day["total_engagement"] for day in historical_data]
        
        return {
            "avg_engagement": statistics.mean(engagements),
            "engagement_std": statistics.stdev(engagements) if len(engagements) > 1 else 0,
            "max_engagement": max(engagements),
            "min_engagement": min(engagements),
            "recent_trend": engagements[-7:] if len(engagements) >= 7 else engagements,
            "data_points": len(engagements),
            "days_active": len([day for day in historical_data if day["total_engagement"] > 0])
        }
    
    async def _ml_predict_engagement(self, features: Dict[str, float]) -> float:
        """ML prediction placeholder - would use actual trained model."""
        # Simplified prediction based on recent trends and averages
        if not features:
            return 0.0
        
        base_prediction = features.get("avg_engagement", 0)
        trend_factor = 1.0
        
        if "recent_trend" in features and features["recent_trend"]:
            recent_avg = statistics.mean(features["recent_trend"])
            if recent_avg > features.get("avg_engagement", 0):
                trend_factor = 1.1
            else:
                trend_factor = 0.9
        
        return base_prediction * trend_factor
    
    async def _calculate_prediction_confidence(self, features: Dict, historical_data: List[Dict]) -> float:
        """Calculate confidence score for predictions."""
        if not historical_data or len(historical_data) < self.min_data_points:
            return 0.1
        
        # Base confidence on data quality and consistency
        data_consistency = 1.0 - (features.get("engagement_std", 0) / max(features.get("avg_engagement", 1), 1))
        data_volume_factor = min(len(historical_data) / 30, 1.0)  # Max confidence at 30+ days
        
        return max(0.1, min(0.95, data_consistency * data_volume_factor))
    
    async def _get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get feature importance for predictions."""
        return {
            "recent_activity": 0.3,
            "historical_consistency": 0.25,
            "engagement_quality": 0.2,
            "content_frequency": 0.15,
            "platform_diversity": 0.1
        }
    
    async def _calculate_virality_score(self, content_events: List[EngagementEvent]) -> float:
        """Calculate virality score for content."""
        if not content_events:
            return 0.0
        
        # Virality factors
        total_engagement = sum(event.value for event in content_events)
        unique_users = len(set(event.user_id for event in content_events if event.user_id))
        time_span_hours = (max(event.timestamp for event in content_events) - 
                          min(event.timestamp for event in content_events)).total_seconds() / 3600
        
        # Velocity and reach factors
        engagement_velocity = total_engagement / max(time_span_hours, 1)
        user_reach = unique_users / max(total_engagement, 1)
        
        # Weighted virality score (0-100)
        virality_score = min(100, (engagement_velocity * 0.6 + user_reach * 40) / 10)
        
        return round(virality_score, 2)
    
    async def _get_virality_recommendations(self, virality_score: float) -> List[str]:
        """Get recommendations based on virality score."""
        if virality_score >= 80:
            return [
                "Excellent viral potential! Consider boosting with paid promotion",
                "Engage with comments quickly to maintain momentum",
                "Cross-post to other platforms immediately"
            ]
        elif virality_score >= 60:
            return [
                "Good viral potential. Optimize hashtags and timing",
                "Encourage user-generated content and shares",
                "Consider collaboration opportunities"
            ]
        elif virality_score >= 40:
            return [
                "Moderate engagement. Focus on content quality improvements",
                "Analyze successful competitors' content strategies",
                "Experiment with different posting times"
            ]
        else:
            return [
                "Low viral potential. Review content strategy",
                "Focus on audience building and engagement",
                "Consider content format changes"
            ]
    
    async def _calculate_platform_correlations(self, platform_metrics: Dict) -> Dict[str, float]:
        """Calculate correlations between platform performances."""
        platforms = list(platform_metrics.keys())
        correlations = {}
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                # Simplified correlation calculation
                metrics1 = list(platform_metrics[platform1].values())
                metrics2 = list(platform_metrics[platform2].values())
                
                if len(metrics1) > 1 and len(metrics2) > 1:
                    # Calculate Pearson correlation (simplified)
                    correlation = await self._calculate_correlation(metrics1, metrics2)
                    correlations[f"{platform1}_{platform2}"] = correlation
        
        return correlations
    
    async def _calculate_correlation(self, values1: List[float], values2: List[float]) -> float:
        """Calculate correlation between two value lists."""
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
        denominator = (
            sum((v1 - mean1) ** 2 for v1 in values1) * 
            sum((v2 - mean2) ** 2 for v2 in values2)
        ) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0.0
    
    async def _get_cross_platform_recommendations(self, correlations: Dict[str, float]) -> List[str]:
        """Get recommendations based on cross-platform analysis."""
        recommendations = []
        
        high_correlation_pairs = [
            pair for pair, corr in correlations.items() 
            if corr > 0.7
        ]
        
        if high_correlation_pairs:
            recommendations.append("Strong cross-platform synergy detected. Maintain consistent posting schedule across correlated platforms.")
        
        low_correlation_pairs = [
            pair for pair, corr in correlations.items() 
            if corr < 0.3
        ]
        
        if low_correlation_pairs:
            recommendations.append("Consider platform-specific content strategies for weakly correlated platforms.")
        
        return recommendations
    
    async def _get_recent_activity(self, creator_id: str, days: int = 30) -> List[EngagementEvent]:
        """Get recent activity for a creator."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        return [
            event for event in self.events
            if event.creator_id == creator_id and event.timestamp >= cutoff_time
        ]
    
    async def _get_historical_activity_pattern(self, creator_id: str) -> Dict[str, Any]:
        """Get historical activity patterns for a creator."""
        creator_events = [
            event for event in self.events
            if event.creator_id == creator_id
        ]
        
        if not creator_events:
            return {}
        
        # Activity by day of week
        day_activity = defaultdict(int)
        for event in creator_events:
            day_activity[event.timestamp.weekday()] += 1
        
        # Activity by hour
        hour_activity = defaultdict(int)
        for event in creator_events:
            hour_activity[event.timestamp.hour] += 1
        
        return {
            "total_events": len(creator_events),
            "activity_by_day": dict(day_activity),
            "activity_by_hour": dict(hour_activity),
            "most_active_day": max(day_activity, key=day_activity.get) if day_activity else None,
            "most_active_hour": max(hour_activity, key=hour_activity.get) if hour_activity else None
        }
    
    async def _calculate_activity_trend(self, recent_activity: List[EngagementEvent]) -> float:
        """Calculate activity trend (positive = increasing, negative = decreasing)."""
        if len(recent_activity) < 7:
            return 0.0
        
        # Group by week
        weekly_counts = defaultdict(int)
        for event in recent_activity:
            week_key = event.timestamp.strftime("%Y-%W")
            weekly_counts[week_key] += 1
        
        weeks = sorted(weekly_counts.keys())
        if len(weeks) < 2:
            return 0.0
        
        # Simple trend calculation
        first_half = statistics.mean([weekly_counts[week] for week in weeks[:len(weeks)//2]])
        second_half = statistics.mean([weekly_counts[week] for week in weeks[len(weeks)//2:]])
        
        return (second_half - first_half) / max(first_half, 1)
    
    async def _calculate_engagement_trend(self, creator_id: str) -> float:
        """Calculate engagement trend for a creator."""
        recent_events = await self._get_recent_activity(creator_id, days=30)
        
        if len(recent_events) < 10:
            return 0.0
        
        # Split into two periods and compare
        mid_point = len(recent_events) // 2
        first_period = recent_events[:mid_point]
        second_period = recent_events[mid_point:]
        
        first_avg = statistics.mean([event.value for event in first_period])
        second_avg = statistics.mean([event.value for event in second_period])
        
        return (second_avg - first_avg) / max(first_avg, 1)
    
    async def _ml_predict_churn(self, features: Dict[str, float]) -> float:
        """ML-based churn prediction (placeholder)."""
        # Simplified churn prediction logic
        days_inactive = features.get("days_since_last_activity", 0)
        activity_decline = features.get("activity_decline_rate", 0)
        engagement_decline = features.get("engagement_decline_rate", 0)
        
        # Weight factors
        inactivity_factor = min(days_inactive / 30, 1.0)  # Max 1.0 at 30+ days
        decline_factor = max(0, -activity_decline) * 0.5 + max(0, -engagement_decline) * 0.5
        
        churn_probability = min(0.95, inactivity_factor * 0.6 + decline_factor * 0.4)
        
        return round(churn_probability, 3)
    
    async def _get_retention_recommendations(self, risk_level: str) -> List[str]:
        """Get retention recommendations based on risk level."""
        if risk_level == "HIGH":
            return [
                "URGENT: Reach out with personalized engagement",
                "Offer exclusive content opportunities or collaborations",
                "Provide additional platform support and resources",
                "Consider incentives or promotional opportunities"
            ]
        elif risk_level == "MEDIUM":
            return [
                "Schedule regular check-ins and support",
                "Share performance insights and growth tips",
                "Introduce to relevant brand partnership opportunities",
                "Provide content optimization recommendations"
            ]
        else:
            return [
                "Continue current engagement strategies",
                "Share platform updates and new features",
                "Recognize achievements and milestones",
                "Maintain regular communication"
            ]
    
    async def _get_growth_history(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get follower growth history (placeholder - would come from actual data source)."""
        # This would typically come from a database with historical follower counts
        # For now, generate sample data
        base_date = datetime.utcnow() - timedelta(days=90)
        growth_history = []
        
        base_followers = 1000
        for i in range(90):
            date = base_date + timedelta(days=i)
            # Simulate growth with some randomness
            growth_rate = 0.02 + (hash(f"{creator_id}{i}") % 100) / 10000
            base_followers = int(base_followers * (1 + growth_rate))
            
            growth_history.append({
                "date": date.date(),
                "followers": base_followers,
                "daily_growth": base_followers - (growth_history[-1]["followers"] if growth_history else 1000)
            })
        
        return growth_history
    
    async def _calculate_growth_rate(self, growth_data: List[Dict]) -> Dict[str, float]:
        """Calculate various growth rates."""
        if len(growth_data) < 2:
            return {"daily": 0.0, "weekly": 0.0, "monthly": 0.0}
        
        # Daily growth rate (last 7 days average)
        recent_data = growth_data[-7:] if len(growth_data) >= 7 else growth_data
        daily_growth = statistics.mean([day["daily_growth"] for day in recent_data if day["daily_growth"] > 0])
        
        # Weekly growth rate
        if len(growth_data) >= 7:
            week_ago_followers = growth_data[-7]["followers"]
            current_followers = growth_data[-1]["followers"]
            weekly_growth = (current_followers - week_ago_followers) / week_ago_followers * 100
        else:
            weekly_growth = 0.0
        
        # Monthly growth rate
        if len(growth_data) >= 30:
            month_ago_followers = growth_data[-30]["followers"]
            current_followers = growth_data[-1]["followers"]
            monthly_growth = (current_followers - month_ago_followers) / month_ago_followers * 100
        else:
            monthly_growth = 0.0
        
        return {
            "daily": round(daily_growth, 2),
            "weekly": round(weekly_growth, 2),
            "monthly": round(monthly_growth, 2)
        }
    
    async def _calculate_growth_acceleration(self, growth_data: List[Dict]) -> float:
        """Calculate growth acceleration (change in growth rate)."""
        if len(growth_data) < 14:
            return 0.0
        
        # Compare recent growth rate with older growth rate
        recent_growth = statistics.mean([day["daily_growth"] for day in growth_data[-7:]])
        older_growth = statistics.mean([day["daily_growth"] for day in growth_data[-14:-7]])
        
        acceleration = (recent_growth - older_growth) / max(older_growth, 1)
        return round(acceleration, 3)
    
    async def _predict_audience_growth(self, creator_id: str, growth_data: List[Dict]) -> Dict[str, Any]:
        """Predict future audience growth."""
        if len(growth_data) < 7:
            return {"error": "Insufficient data for prediction"}
        
        # Simple linear regression for growth prediction
        recent_growth_rate = statistics.mean([day["daily_growth"] for day in growth_data[-7:]])
        current_followers = growth_data[-1]["followers"]
        
        predictions = {}
        for days in [7, 30, 90, 365]:
            predicted_followers = current_followers + (recent_growth_rate * days)
            predictions[f"{days}_days"] = {
                "predicted_followers": int(predicted_followers),
                "growth_amount": int(predicted_followers - current_followers),
                "confidence": max(0.1, 1.0 - (days / 365) * 0.5)  # Decreasing confidence over time
            }
        
        return predictions
    
    async def _identify_growth_patterns(self, growth_data: List[Dict]) -> Dict[str, Any]:
        """Identify growth patterns and seasonality."""
        if len(growth_data) < 14:
            return {"error": "Insufficient data for pattern analysis"}
        
        daily_growth_values = [day["daily_growth"] for day in growth_data]
        
        # Find growth spikes (values significantly above average)
        avg_growth = statistics.mean(daily_growth_values)
        std_growth = statistics.stdev(daily_growth_values) if len(daily_growth_values) > 1 else 0
        threshold = avg_growth + (2 * std_growth)
        
        growth_spikes = [
            {
                "date": day["date"],
                "growth": day["daily_growth"],
                "significance": day["daily_growth"] / max(avg_growth, 1)
            }
            for day in growth_data
            if day["daily_growth"] > threshold
        ]
        
        # Day of week analysis
        weekday_growth = defaultdict(list)
        for day in growth_data:
            weekday = day["date"].weekday()
            weekday_growth[weekday].append(day["daily_growth"])
        
        weekday_averages = {
            day: statistics.mean(growth_values)
            for day, growth_values in weekday_growth.items()
            if growth_values
        }
        
        best_weekday = max(weekday_averages, key=weekday_averages.get) if weekday_averages else None
        
        return {
            "average_daily_growth": round(avg_growth, 2),
            "growth_volatility": round(std_growth, 2),
            "growth_spikes": growth_spikes[-5:],  # Last 5 spikes
            "best_growth_weekday": best_weekday,
            "weekday_performance": weekday_averages,
            "growth_consistency": round(1 - (std_growth / max(avg_growth, 1)), 3)
        }
    
    async def _calculate_milestone_predictions(self, current_followers: int, growth_rate: Dict[str, float]) -> List[Dict]:
        """Calculate when creator will reach follower milestones."""
        milestones = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        daily_growth = growth_rate.get("daily", 0)
        
        predictions = []
        
        for milestone in milestones:
            if milestone > current_followers and daily_growth > 0:
                days_to_milestone = (milestone - current_followers) / daily_growth
                predicted_date = datetime.utcnow() + timedelta(days=int(days_to_milestone))
                
                predictions.append({
                    "milestone": milestone,
                    "days_to_reach": int(days_to_milestone),
                    "predicted_date": predicted_date.date().isoformat(),
                    "confidence": max(0.1, 1.0 - (days_to_milestone / 365) * 0.3)
                })
        
        return predictions[:3]  # Return next 3 milestones
    
    async def _get_growth_recommendations(self, growth_patterns: Dict[str, Any]) -> List[str]:
        """Get growth optimization recommendations."""
        recommendations = []
        
        if "growth_consistency" in growth_patterns:
            consistency = growth_patterns["growth_consistency"]
            if consistency < 0.5:
                recommendations.append("Focus on consistent posting schedule to improve growth stability")
            elif consistency > 0.8:
                recommendations.append("Excellent growth consistency! Consider scaling successful strategies")
        
        if "best_growth_weekday" in growth_patterns and growth_patterns["best_growth_weekday"] is not None:
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            best_day = weekdays[growth_patterns["best_growth_weekday"]]
            recommendations.append(f"Optimize content publishing for {best_day}s - your best performing day")
        
        if "growth_spikes" in growth_patterns and growth_patterns["growth_spikes"]:
            recommendations.append("Analyze content from growth spike dates to identify successful patterns")
        
        avg_growth = growth_patterns.get("average_daily_growth", 0)
        if avg_growth < 10:
            recommendations.append("Consider collaborations and cross-promotion to accelerate growth")
        elif avg_growth > 100:
            recommendations.append("Exceptional growth! Focus on engagement quality and community building")
        
        return recommendations


# Export the main class
__all__ = ["CreatorEngagementAnalytics", "EngagementEvent", "CreatorProfile", "EngagementPrediction"]