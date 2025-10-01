#!/usr/bin/env python3
"""
📈 Enterprise Notification Delivery Optimizer - IA Chéries Platform Core
ML-powered timing optimization and adaptive delivery windows

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import pandas as pd
import pytz

class DeliveryChannel(Enum):
    """Delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class DeliveryStrategy(Enum):
    """Delivery optimization strategies"""
    IMMEDIATE = "immediate"
    OPTIMAL_TIME = "optimal_time"
    BATCH_DELIVERY = "batch_delivery"
    ADAPTIVE = "adaptive"
    USER_PREFERENCE = "user_preference"

class DeliveryPriority(Enum):
    """Delivery priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TimeZoneStrategy(Enum):
    """Timezone handling strategies"""
    USER_TIMEZONE = "user_timezone"
    BUSINESS_HOURS = "business_hours"
    GLOBAL_OPTIMAL = "global_optimal"
    FOLLOW_SUN = "follow_sun"

@dataclass
class DeliveryWindow:
    """Optimal delivery time window"""
    start_time: datetime
    end_time: datetime
    confidence_score: float
    expected_engagement: float
    channel_specific: Dict[DeliveryChannel, float]
    timezone: str

@dataclass
class DeliveryOptimization:
    """Delivery optimization result"""
    notification_id: str
    user_id: str
    optimal_time: datetime
    delivery_windows: List[DeliveryWindow]
    strategy_used: DeliveryStrategy
    channel_recommendations: Dict[DeliveryChannel, float]
    confidence_score: float
    estimated_engagement: float
    delay_seconds: int
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class EngagementPrediction:
    """Engagement prediction result"""
    user_id: str
    channel: DeliveryChannel
    delivery_time: datetime
    predicted_engagement: float
    engagement_probability: float
    optimal_score: float
    features_used: Dict[str, Any]
    model_version: str

class NotificationDeliveryOptimizer:
    """Enterprise notification delivery optimizer with ML timing prediction"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # ML models
        self.engagement_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.timing_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Model training status
        self.is_engagement_model_trained = False
        self.is_timing_model_trained = False
        self.model_version = "1.0"
        
        # Timezone support
        self.supported_timezones = pytz.all_timezones
        self.business_hours = {
            'start': 9,  # 9 AM
            'end': 17,   # 5 PM
            'weekdays_only': True
        }
        
        # Channel-specific optimal times (default patterns)
        self.channel_patterns = {
            DeliveryChannel.EMAIL: {
                'optimal_hours': [9, 10, 14, 15],  # Business hours
                'avoid_hours': [0, 1, 2, 3, 4, 5, 22, 23],
                'weekday_boost': 1.2,
                'weekend_penalty': 0.7
            },
            DeliveryChannel.SMS: {
                'optimal_hours': [10, 11, 15, 16, 19, 20],
                'avoid_hours': [0, 1, 2, 3, 4, 5, 6, 22, 23],
                'weekday_boost': 1.0,
                'weekend_penalty': 0.9
            },
            DeliveryChannel.PUSH: {
                'optimal_hours': [8, 12, 18, 19, 20],
                'avoid_hours': [0, 1, 2, 3, 4, 5],
                'weekday_boost': 1.1,
                'weekend_penalty': 0.8
            },
            DeliveryChannel.IN_APP: {
                'optimal_hours': list(range(8, 23)),  # Active hours
                'avoid_hours': [0, 1, 2, 3, 4, 5, 6, 7],
                'weekday_boost': 1.0,
                'weekend_penalty': 1.0
            }
        }
        
        # User behavior cache
        self.user_engagement_patterns: Dict[str, Dict] = {}
        self.global_engagement_stats: Dict = {}
        
        # Performance metrics
        self.metrics = {
            'optimizations_processed': 0,
            'ml_predictions': 0,
            'delivery_delays_applied': 0,
            'engagement_improvements': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'model_accuracy': 0.0,
            'average_engagement_lift': 0.0
        }

    async def initialize(self):
        """Initialize delivery optimizer"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ Delivery optimizer initialized with Redis connection")
            
            # Load existing models
            await self._load_ml_models()
            
            # Load global engagement statistics
            await self._load_global_stats()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize delivery optimizer: {e}")
            raise

    async def optimize_delivery_time(
        self,
        notification_id: str,
        user_id: str,
        content: str,
        channels: List[DeliveryChannel],
        priority: DeliveryPriority = DeliveryPriority.NORMAL,
        strategy: DeliveryStrategy = DeliveryStrategy.ADAPTIVE,
        user_timezone: Optional[str] = None
    ) -> DeliveryOptimization:
        """
        Optimize notification delivery timing
        
        Args:
            notification_id: Unique notification identifier
            user_id: Target user identifier
            content: Notification content for analysis
            channels: Available delivery channels
            priority: Delivery priority level
            strategy: Optimization strategy
            user_timezone: User's timezone
            
        Returns:
            DeliveryOptimization with optimal timing recommendations
        """
        start_time = time.time()
        self.metrics['optimizations_processed'] += 1
        
        try:
            # Get user engagement patterns
            user_patterns = await self._get_user_engagement_patterns(user_id)
            
            # Determine user timezone
            if not user_timezone:
                user_timezone = user_patterns.get('timezone', 'UTC')
            
            # Apply optimization strategy
            if strategy == DeliveryStrategy.IMMEDIATE:
                optimal_time = datetime.utcnow()
                delivery_windows = []
                confidence_score = 1.0
                
            elif strategy == DeliveryStrategy.OPTIMAL_TIME:
                optimal_time, delivery_windows, confidence_score = await self._calculate_optimal_time(
                    user_id, channels, user_timezone, user_patterns
                )
                
            elif strategy == DeliveryStrategy.BATCH_DELIVERY:
                optimal_time, delivery_windows, confidence_score = await self._calculate_batch_delivery_time(
                    user_id, channels, user_timezone, priority
                )
                
            elif strategy == DeliveryStrategy.ADAPTIVE:
                optimal_time, delivery_windows, confidence_score = await self._calculate_adaptive_time(
                    user_id, content, channels, user_timezone, user_patterns, priority
                )
                
            elif strategy == DeliveryStrategy.USER_PREFERENCE:
                optimal_time, delivery_windows, confidence_score = await self._calculate_preference_based_time(
                    user_id, channels, user_timezone, user_patterns
                )
            
            else:
                optimal_time = datetime.utcnow()
                delivery_windows = []
                confidence_score = 0.5
            
            # Calculate channel recommendations
            channel_recommendations = await self._calculate_channel_recommendations(
                user_id, channels, optimal_time, user_patterns
            )
            
            # Estimate engagement improvement
            estimated_engagement = await self._estimate_engagement(
                user_id, optimal_time, channels, content, user_patterns
            )
            
            # Calculate delay
            delay_seconds = max(0, int((optimal_time - datetime.utcnow()).total_seconds()))
            
            # Create optimization result
            optimization = DeliveryOptimization(
                notification_id=notification_id,
                user_id=user_id,
                optimal_time=optimal_time,
                delivery_windows=delivery_windows,
                strategy_used=strategy,
                channel_recommendations=channel_recommendations,
                confidence_score=confidence_score,
                estimated_engagement=estimated_engagement,
                delay_seconds=delay_seconds,
                metadata={
                    'user_timezone': user_timezone,
                    'priority': priority.value,
                    'channels_analyzed': [c.value for c in channels],
                    'processing_time': time.time() - start_time
                },
                created_at=datetime.utcnow()
            )
            
            # Store optimization result
            await self._store_optimization_result(optimization)
            
            # Update delivery metrics
            if delay_seconds > 0:
                self.metrics['delivery_delays_applied'] += 1
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"❌ Delivery optimization failed: {e}")
            
            # Return immediate delivery on failure
            return DeliveryOptimization(
                notification_id=notification_id,
                user_id=user_id,
                optimal_time=datetime.utcnow(),
                delivery_windows=[],
                strategy_used=strategy,
                channel_recommendations={channel: 0.5 for channel in channels},
                confidence_score=0.0,
                estimated_engagement=0.5,
                delay_seconds=0,
                metadata={'error': str(e)},
                created_at=datetime.utcnow()
            )

    async def _calculate_optimal_time(
        self,
        user_id: str,
        channels: List[DeliveryChannel],
        user_timezone: str,
        user_patterns: Dict[str, Any]
    ) -> Tuple[datetime, List[DeliveryWindow], float]:
        """Calculate optimal delivery time using ML models"""
        
        if not self.is_engagement_model_trained:
            # Fallback to rule-based optimization
            return await self._calculate_rule_based_optimal_time(user_id, channels, user_timezone, user_patterns)
        
        try:
            current_time = datetime.utcnow()
            user_tz = pytz.timezone(user_timezone)
            current_local = current_time.replace(tzinfo=pytz.UTC).astimezone(user_tz)
            
            # Generate candidate times (next 24 hours)
            candidate_times = []
            for hour_offset in range(0, 24):
                candidate_time = current_local + timedelta(hours=hour_offset)
                candidate_times.append(candidate_time)
            
            # Predict engagement for each candidate time
            best_time = current_time
            best_score = 0.0
            delivery_windows = []
            
            for candidate_time in candidate_times:
                # Convert back to UTC for processing
                utc_time = candidate_time.astimezone(pytz.UTC).replace(tzinfo=None)
                
                # Calculate engagement score for each channel
                channel_scores = {}
                for channel in channels:
                    engagement_score = await self._predict_engagement(
                        user_id, channel, utc_time, user_patterns
                    )
                    channel_scores[channel] = engagement_score
                
                # Calculate overall score
                overall_score = np.mean(list(channel_scores.values()))
                
                # Create delivery window if score is high enough
                if overall_score > 0.6:  # Threshold for good engagement
                    window = DeliveryWindow(
                        start_time=utc_time,
                        end_time=utc_time + timedelta(hours=1),
                        confidence_score=overall_score,
                        expected_engagement=overall_score,
                        channel_specific=channel_scores,
                        timezone=user_timezone
                    )
                    delivery_windows.append(window)
                
                # Update best time
                if overall_score > best_score:
                    best_score = overall_score
                    best_time = utc_time
            
            # Sort delivery windows by score
            delivery_windows.sort(key=lambda w: w.confidence_score, reverse=True)
            
            return best_time, delivery_windows[:5], best_score  # Top 5 windows
            
        except Exception as e:
            self.logger.error(f"❌ ML optimal time calculation failed: {e}")
            return await self._calculate_rule_based_optimal_time(user_id, channels, user_timezone, user_patterns)

    async def _calculate_rule_based_optimal_time(
        self,
        user_id: str,
        channels: List[DeliveryChannel],
        user_timezone: str,
        user_patterns: Dict[str, Any]
    ) -> Tuple[datetime, List[DeliveryWindow], float]:
        """Fallback rule-based optimal time calculation"""
        
        try:
            user_tz = pytz.timezone(user_timezone)
            current_utc = datetime.utcnow()
            current_local = current_utc.replace(tzinfo=pytz.UTC).astimezone(user_tz)
            
            # Find next optimal time based on channel patterns
            best_times = []
            
            for channel in channels:
                pattern = self.channel_patterns.get(channel, {})
                optimal_hours = pattern.get('optimal_hours', [9, 10, 14, 15])
                
                # Find next optimal hour
                next_optimal_time = None
                for hour_offset in range(0, 48):  # Check next 48 hours
                    candidate_time = current_local + timedelta(hours=hour_offset)
                    
                    if candidate_time.hour in optimal_hours:
                        # Check if it's a weekday (if required)
                        if pattern.get('weekdays_only', False) and candidate_time.weekday() >= 5:
                            continue
                        
                        next_optimal_time = candidate_time.astimezone(pytz.UTC).replace(tzinfo=None)
                        break
                
                if next_optimal_time:
                    best_times.append(next_optimal_time)
            
            # Choose the earliest optimal time
            if best_times:
                optimal_time = min(best_times)
            else:
                # Default to business hours tomorrow
                tomorrow = current_local + timedelta(days=1)
                optimal_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
                optimal_time = optimal_time.astimezone(pytz.UTC).replace(tzinfo=None)
            
            # Create delivery window
            delivery_window = DeliveryWindow(
                start_time=optimal_time,
                end_time=optimal_time + timedelta(hours=2),
                confidence_score=0.7,
                expected_engagement=0.7,
                channel_specific={channel: 0.7 for channel in channels},
                timezone=user_timezone
            )
            
            return optimal_time, [delivery_window], 0.7
            
        except Exception as e:
            self.logger.error(f"❌ Rule-based optimal time calculation failed: {e}")
            return datetime.utcnow(), [], 0.5

    async def _predict_engagement(
        self,
        user_id: str,
        channel: DeliveryChannel,
        delivery_time: datetime,
        user_patterns: Dict[str, Any]
    ) -> float:
        """Predict engagement score for specific time and channel"""
        
        if not self.is_engagement_model_trained:
            return await self._estimate_engagement_rule_based(user_id, channel, delivery_time, user_patterns)
        
        try:
            # Extract features for ML prediction
            features = await self._extract_engagement_features(
                user_id, channel, delivery_time, user_patterns
            )
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict engagement
            engagement_score = self.engagement_predictor.predict(features_scaled)[0]
            
            # Normalize to 0-1 range
            engagement_score = max(0.0, min(1.0, engagement_score))
            
            self.metrics['ml_predictions'] += 1
            
            return engagement_score
            
        except Exception as e:
            self.logger.error(f"❌ ML engagement prediction failed: {e}")
            return await self._estimate_engagement_rule_based(user_id, channel, delivery_time, user_patterns)

    async def _estimate_engagement_rule_based(
        self,
        user_id: str,
        channel: DeliveryChannel,
        delivery_time: datetime,
        user_patterns: Dict[str, Any]
    ) -> float:
        """Rule-based engagement estimation"""
        
        try:
            base_score = 0.5
            
            # Time-based scoring
            hour = delivery_time.hour
            weekday = delivery_time.weekday()
            
            channel_pattern = self.channel_patterns.get(channel, {})
            optimal_hours = channel_pattern.get('optimal_hours', [])
            avoid_hours = channel_pattern.get('avoid_hours', [])
            
            if hour in optimal_hours:
                base_score += 0.3
            elif hour in avoid_hours:
                base_score -= 0.4
            
            # Weekday/weekend adjustment
            if weekday < 5:  # Weekday
                base_score *= channel_pattern.get('weekday_boost', 1.0)
            else:  # Weekend
                base_score *= channel_pattern.get('weekend_penalty', 1.0)
            
            # User-specific patterns
            user_channel_pref = user_patterns.get('channel_preferences', {}).get(channel.value, 0.5)
            base_score = 0.7 * base_score + 0.3 * user_channel_pref
            
            # Historical engagement rate
            historical_rate = user_patterns.get('engagement_rate', 0.5)
            base_score = 0.8 * base_score + 0.2 * historical_rate
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            self.logger.error(f"❌ Rule-based engagement estimation failed: {e}")
            return 0.5

    async def _extract_engagement_features(
        self,
        user_id: str,
        channel: DeliveryChannel,
        delivery_time: datetime,
        user_patterns: Dict[str, Any]
    ) -> List[float]:
        """Extract features for ML engagement prediction"""
        
        features = []
        
        # Time features
        features.append(delivery_time.hour / 24.0)  # Hour of day (normalized)
        features.append(delivery_time.weekday() / 6.0)  # Day of week (normalized)
        features.append(delivery_time.day / 31.0)  # Day of month (normalized)
        
        # Channel features
        channel_encoding = {
            DeliveryChannel.EMAIL: 0.0,
            DeliveryChannel.SMS: 0.25,
            DeliveryChannel.PUSH: 0.5,
            DeliveryChannel.IN_APP: 0.75
        }
        features.append(channel_encoding.get(channel, 0.0))
        
        # User pattern features
        features.append(user_patterns.get('engagement_rate', 0.5))
        features.append(user_patterns.get('activity_score', 0.5))
        features.append(user_patterns.get('channel_preferences', {}).get(channel.value, 0.5))
        features.append(user_patterns.get('frequency_preference', 0.5))
        
        # Global features
        features.append(self.global_engagement_stats.get('average_engagement', 0.5))
        features.append(self.global_engagement_stats.get(f'{channel.value}_avg_engagement', 0.5))
        
        # Time since last notification
        last_notification = user_patterns.get('last_notification_time')
        if last_notification:
            try:
                last_time = datetime.fromisoformat(last_notification)
                hours_since = (delivery_time - last_time).total_seconds() / 3600
                features.append(min(1.0, hours_since / 24.0))  # Normalize to days
            except Exception:
                features.append(0.5)
        else:
            features.append(1.0)  # No previous notifications
        
        return features

    async def _get_user_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement patterns from cache or Redis"""
        
        # Check cache first
        if user_id in self.user_engagement_patterns:
            self.metrics['cache_hits'] += 1
            return self.user_engagement_patterns[user_id]
        
        self.metrics['cache_misses'] += 1
        
        # Load from Redis
        patterns_data = await self.redis_client.get(f"user_patterns:{user_id}")
        
        if patterns_data:
            patterns = json.loads(patterns_data)
            self.user_engagement_patterns[user_id] = patterns
            return patterns
        
        # Default patterns for new users
        default_patterns = {
            'engagement_rate': 0.5,
            'activity_score': 0.5,
            'channel_preferences': {
                'email': 0.6,
                'sms': 0.4,
                'push': 0.7,
                'in_app': 0.8
            },
            'optimal_hours': [9, 10, 14, 15, 19, 20],
            'timezone': 'UTC',
            'frequency_preference': 0.5,
            'last_notification_time': None
        }
        
        self.user_engagement_patterns[user_id] = default_patterns
        await self._save_user_patterns(user_id, default_patterns)
        
        return default_patterns

    async def _save_user_patterns(self, user_id: str, patterns: Dict[str, Any]):
        """Save user engagement patterns to Redis"""
        try:
            await self.redis_client.setex(
                f"user_patterns:{user_id}",
                86400 * 30,  # 30 days
                json.dumps(patterns)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to save user patterns: {e}")

    async def _calculate_channel_recommendations(
        self,
        user_id: str,
        channels: List[DeliveryChannel],
        optimal_time: datetime,
        user_patterns: Dict[str, Any]
    ) -> Dict[DeliveryChannel, float]:
        """Calculate channel recommendation scores"""
        
        recommendations = {}
        
        for channel in channels:
            # Base score from user preferences
            base_score = user_patterns.get('channel_preferences', {}).get(channel.value, 0.5)
            
            # Time-based adjustment
            time_score = await self._calculate_time_channel_score(channel, optimal_time)
            
            # Combine scores
            final_score = 0.6 * base_score + 0.4 * time_score
            
            recommendations[channel] = max(0.0, min(1.0, final_score))
        
        return recommendations

    async def _calculate_time_channel_score(self, channel: DeliveryChannel, delivery_time: datetime) -> float:
        """Calculate channel score based on delivery time"""
        
        pattern = self.channel_patterns.get(channel, {})
        hour = delivery_time.hour
        weekday = delivery_time.weekday()
        
        score = 0.5
        
        # Hour-based scoring
        if hour in pattern.get('optimal_hours', []):
            score += 0.3
        elif hour in pattern.get('avoid_hours', []):
            score -= 0.4
        
        # Weekday/weekend adjustment
        if weekday < 5:  # Weekday
            score *= pattern.get('weekday_boost', 1.0)
        else:  # Weekend
            score *= pattern.get('weekend_penalty', 1.0)
        
        return max(0.0, min(1.0, score))

    async def _estimate_engagement(
        self,
        user_id: str,
        optimal_time: datetime,
        channels: List[DeliveryChannel],
        content: str,
        user_patterns: Dict[str, Any]
    ) -> float:
        """Estimate overall engagement for the optimization"""
        
        channel_engagements = []
        
        for channel in channels:
            engagement = await self._predict_engagement(user_id, channel, optimal_time, user_patterns)
            channel_engagements.append(engagement)
        
        # Return weighted average (favor highest scoring channels)
        if channel_engagements:
            sorted_engagements = sorted(channel_engagements, reverse=True)
            # Weight: 50% best channel, 30% second best, 20% others
            weights = [0.5, 0.3] + [0.2 / max(1, len(sorted_engagements) - 2)] * (len(sorted_engagements) - 2)
            
            weighted_engagement = sum(
                eng * weight for eng, weight in zip(sorted_engagements, weights[:len(sorted_engagements)])
            )
            
            return min(1.0, weighted_engagement)
        
        return 0.5

    async def batch_optimize_delivery(
        self,
        notifications: List[Dict[str, Any]],
        batch_strategy: str = "timezone_grouped"
    ) -> List[DeliveryOptimization]:
        """Optimize delivery for batch of notifications"""
        
        optimizations = []
        
        if batch_strategy == "timezone_grouped":
            # Group by timezone for efficient processing
            timezone_groups = {}
            
            for notification in notifications:
                user_tz = notification.get('user_timezone', 'UTC')
                if user_tz not in timezone_groups:
                    timezone_groups[user_tz] = []
                timezone_groups[user_tz].append(notification)
            
            # Process each timezone group
            for timezone, group_notifications in timezone_groups.items():
                for notification in group_notifications:
                    optimization = await self.optimize_delivery_time(
                        notification_id=notification['notification_id'],
                        user_id=notification['user_id'],
                        content=notification['content'],
                        channels=notification['channels'],
                        priority=DeliveryPriority(notification.get('priority', 'normal')),
                        strategy=DeliveryStrategy.BATCH_DELIVERY,
                        user_timezone=timezone
                    )
                    optimizations.append(optimization)
        
        else:
            # Sequential processing
            for notification in notifications:
                optimization = await self.optimize_delivery_time(
                    notification_id=notification['notification_id'],
                    user_id=notification['user_id'],
                    content=notification['content'],
                    channels=notification['channels'],
                    priority=DeliveryPriority(notification.get('priority', 'normal')),
                    strategy=DeliveryStrategy.ADAPTIVE
                )
                optimizations.append(optimization)
        
        return optimizations

    async def update_engagement_feedback(
        self,
        notification_id: str,
        user_id: str,
        actual_engagement: float,
        delivery_time: datetime,
        channel: DeliveryChannel
    ):
        """Update models with actual engagement feedback"""
        
        try:
            # Get original optimization
            optimization_data = await self.redis_client.get(f"optimization:{notification_id}")
            
            if optimization_data:
                optimization = json.loads(optimization_data)
                
                # Calculate engagement improvement
                estimated = optimization.get('estimated_engagement', 0.5)
                improvement = actual_engagement - estimated
                
                if improvement > 0:
                    self.metrics['engagement_improvements'] += 1
                
                # Update average engagement lift
                current_avg = self.metrics.get('average_engagement_lift', 0.0)
                self.metrics['average_engagement_lift'] = (current_avg * 0.9) + (improvement * 0.1)
                
                # Store feedback for model retraining
                feedback_data = {
                    'notification_id': notification_id,
                    'user_id': user_id,
                    'delivery_time': delivery_time.isoformat(),
                    'channel': channel.value,
                    'actual_engagement': actual_engagement,
                    'estimated_engagement': estimated,
                    'improvement': improvement,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self.redis_client.lpush("engagement_feedback", json.dumps(feedback_data))
                await self.redis_client.ltrim("engagement_feedback", 0, 9999)  # Keep last 10k
                
                # Update user patterns
                await self._update_user_patterns_from_feedback(user_id, channel, actual_engagement, delivery_time)
        
        except Exception as e:
            self.logger.error(f"❌ Failed to update engagement feedback: {e}")

    async def _update_user_patterns_from_feedback(
        self,
        user_id: str,
        channel: DeliveryChannel,
        engagement: float,
        delivery_time: datetime
    ):
        """Update user engagement patterns based on feedback"""
        
        patterns = await self._get_user_engagement_patterns(user_id)
        
        # Update engagement rate (exponential moving average)
        current_rate = patterns.get('engagement_rate', 0.5)
        patterns['engagement_rate'] = 0.9 * current_rate + 0.1 * engagement
        
        # Update channel preference
        channel_prefs = patterns.get('channel_preferences', {})
        current_pref = channel_prefs.get(channel.value, 0.5)
        channel_prefs[channel.value] = 0.9 * current_pref + 0.1 * engagement
        patterns['channel_preferences'] = channel_prefs
        
        # Update optimal hours
        hour = delivery_time.hour
        if engagement > 0.7:  # High engagement
            optimal_hours = patterns.get('optimal_hours', [])
            if hour not in optimal_hours:
                optimal_hours.append(hour)
            patterns['optimal_hours'] = optimal_hours
        
        # Update last notification time
        patterns['last_notification_time'] = delivery_time.isoformat()
        
        # Save updated patterns
        await self._save_user_patterns(user_id, patterns)

    async def train_models_from_feedback(self, min_samples: int = 1000):
        """Train ML models using collected feedback data"""
        
        try:
            # Get feedback data
            feedback_data = await self.redis_client.lrange("engagement_feedback", 0, -1)
            
            if len(feedback_data) < min_samples:
                self.logger.warning(f"⚠️ Insufficient feedback data for training: {len(feedback_data)} < {min_samples}")
                return
            
            # Prepare training data
            X = []
            y = []
            
            for feedback_json in feedback_data:
                try:
                    feedback = json.loads(feedback_json)
                    
                    # Extract features
                    delivery_time = datetime.fromisoformat(feedback['delivery_time'])
                    channel = DeliveryChannel(feedback['channel'])
                    user_patterns = await self._get_user_engagement_patterns(feedback['user_id'])
                    
                    features = await self._extract_engagement_features(
                        feedback['user_id'], channel, delivery_time, user_patterns
                    )
                    
                    X.append(features)
                    y.append(feedback['actual_engagement'])
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to process feedback sample: {e}")
                    continue
            
            if len(X) < min_samples:
                self.logger.warning(f"⚠️ Insufficient valid samples after processing: {len(X)}")
                return
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train engagement predictor
            self.engagement_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.engagement_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            
            self.metrics['model_accuracy'] = 1.0 - mse  # Convert MSE to accuracy-like metric
            self.is_engagement_model_trained = True
            
            # Save trained model
            await self._save_ml_models()
            
            self.logger.info(f"✅ ML models trained successfully with {len(X)} samples, MSE: {mse:.4f}")
            
        except Exception as e:
            self.logger.error(f"❌ Model training failed: {e}")

    async def _store_optimization_result(self, optimization: DeliveryOptimization):
        """Store optimization result in Redis"""
        try:
            optimization_dict = asdict(optimization)
            # Convert datetime objects to ISO strings
            optimization_dict['optimal_time'] = optimization.optimal_time.isoformat()
            optimization_dict['created_at'] = optimization.created_at.isoformat()
            
            # Convert delivery windows
            windows_data = []
            for window in optimization.delivery_windows:
                window_dict = asdict(window)
                window_dict['start_time'] = window.start_time.isoformat()
                window_dict['end_time'] = window.end_time.isoformat()
                windows_data.append(window_dict)
            optimization_dict['delivery_windows'] = windows_data
            
            await self.redis_client.setex(
                f"optimization:{optimization.notification_id}",
                86400 * 7,  # 7 days
                json.dumps(optimization_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to store optimization result: {e}")

    async def _load_global_stats(self):
        """Load global engagement statistics"""
        try:
            stats_data = await self.redis_client.get("global_engagement_stats")
            if stats_data:
                self.global_engagement_stats = json.loads(stats_data)
            else:
                self.global_engagement_stats = {
                    'average_engagement': 0.5,
                    'email_avg_engagement': 0.6,
                    'sms_avg_engagement': 0.7,
                    'push_avg_engagement': 0.4,
                    'in_app_avg_engagement': 0.8
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to load global stats: {e}")

    async def get_delivery_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get delivery optimization analytics"""
        
        analytics = {
            'metrics': self.metrics,
            'model_status': {
                'engagement_model_trained': self.is_engagement_model_trained,
                'timing_model_trained': self.is_timing_model_trained,
                'model_version': self.model_version
            },
            'global_stats': self.global_engagement_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if user_id:
            # Add user-specific analytics
            user_patterns = await self._get_user_engagement_patterns(user_id)
            analytics['user_patterns'] = user_patterns
            
            # Get recent optimizations for user
            recent_optimizations = []
            # This would typically query a database or search Redis keys
            # For now, we'll return empty list
            analytics['recent_optimizations'] = recent_optimizations
        
        return analytics

    async def get_metrics(self) -> Dict[str, Any]:
        """Get delivery optimizer metrics"""
        
        # Calculate additional metrics
        total_optimizations = self.metrics['optimizations_processed']
        delay_rate = (self.metrics['delivery_delays_applied'] / total_optimizations * 100) if total_optimizations > 0 else 0
        improvement_rate = (self.metrics['engagement_improvements'] / total_optimizations * 100) if total_optimizations > 0 else 0
        
        return {
            **self.metrics,
            'delay_rate_percentage': round(delay_rate, 2),
            'improvement_rate_percentage': round(improvement_rate, 2),
            'cached_user_patterns': len(self.user_engagement_patterns),
            'supported_timezones': len(self.supported_timezones),
            'supported_channels': len(DeliveryChannel),
            'ml_model_status': {
                'engagement_model': self.is_engagement_model_trained,
                'timing_model': self.is_timing_model_trained
            }
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("✅ Delivery optimizer cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_delivery_optimizer():
        """Test delivery optimizer functionality"""
        
        # Initialize optimizer
        optimizer = NotificationDeliveryOptimizer()
        await optimizer.initialize()
        
        # Test optimization
        optimization = await optimizer.optimize_delivery_time(
            notification_id="notif_123",
            user_id="user_456",
            content="You have a new message!",
            channels=[DeliveryChannel.EMAIL, DeliveryChannel.PUSH],
            priority=DeliveryPriority.HIGH,
            strategy=DeliveryStrategy.ADAPTIVE,
            user_timezone="America/New_York"
        )
        
        print(f"Optimization result:")
        print(f"- Optimal time: {optimization.optimal_time}")
        print(f"- Strategy: {optimization.strategy_used.value}")
        print(f"- Confidence: {optimization.confidence_score:.2f}")
        print(f"- Estimated engagement: {optimization.estimated_engagement:.2f}")
        print(f"- Delay: {optimization.delay_seconds} seconds")
        print(f"- Channel recommendations: {optimization.channel_recommendations}")
        
        # Test batch optimization
        notifications = [
            {
                'notification_id': f'batch_{i}',
                'user_id': f'user_{i}',
                'content': f'Batch notification {i}',
                'channels': [DeliveryChannel.EMAIL],
                'priority': 'normal',
                'user_timezone': 'UTC'
            }
            for i in range(3)
        ]
        
        batch_optimizations = await optimizer.batch_optimize_delivery(notifications)
        print(f"\nBatch optimization completed: {len(batch_optimizations)} notifications optimized")
        
        # Simulate engagement feedback
        await optimizer.update_engagement_feedback(
            notification_id="notif_123",
            user_id="user_456",
            actual_engagement=0.8,
            delivery_time=optimization.optimal_time,
            channel=DeliveryChannel.EMAIL
        )
        
        # Get analytics
        analytics = await optimizer.get_delivery_analytics("user_456")
        print(f"\nAnalytics: {json.dumps(analytics, indent=2)}")
        
        # Get metrics
        metrics = await optimizer.get_metrics()
        print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
        
        await optimizer.cleanup()
    
    # Run test
    asyncio.run(test_delivery_optimizer())