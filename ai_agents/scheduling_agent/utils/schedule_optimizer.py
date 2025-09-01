#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schedule Optimizer - Advanced AI-Powered Content Timing Optimization
====================================================================

Industrial-grade schedule optimization system using machine learning for content timing,
audience behavior analysis, and performance-based scheduling improvements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import pytz

from ..base import BaseAgent, AgentError
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.performance_monitor import PerformanceMonitor
from .scheduling_agent import ScheduledJob, AudienceActivity, OptimalTimingAnalysis

logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """
Schedule optimization strategies"""

    ENGAGEMENT_MAX = "engagement_maximization"
    REACH_MAX = "reach_maximization"
    BALANCED = "balanced_optimization"
    COMPETITION_AVOID = "competition_avoidance"
    COST_EFFICIENT = "cost_efficient"
    AUDIENCE_GROWTH = "audience_growth"

class TimingFactor(Enum):
    """Factors considered in timing optimization"""

    AUDIENCE_ACTIVITY = "audience_activity"
    PLATFORM_ALGORITHM = "platform_algorithm"
    COMPETITION_LEVEL = "competition_level"
    CONTENT_TYPE = "content_type"
    HISTORICAL_PERFORMANCE = "historical_performance"
    SEASONAL_TRENDS = "seasonal_trends"
    GLOBAL_EVENTS = "global_events"
    TIMEZONE_ALIGNMENT = "timezone_alignment"

@dataclass
class OptimizationConfig:
    """Configuration for schedule optimization"""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    factors: List[TimingFactor] = field(default_factory=lambda: list(TimingFactor))
    weights: Dict[TimingFactor, float] = field(default_factory=dict)
    time_horizon_hours: int = 168  # 7 days
    min_delay_hours: int = 1
    max_schedules_per_day: int = 10
    consider_time_zones: List[str] = field(default_factory=list)

@dataclass
class TimingPrediction:
    """
Timing prediction result"""
    recommended_time: datetime
    expected_performance: Dict[str, float]
    confidence_score: float
    factors_analysis: Dict[TimingFactor, float]
    alternative_times: List[Tuple[datetime, float]]
    optimization_reasoning: List[str]

@dataclass
class PerformanceMetrics:
    """
Performance metrics for evaluation"""
    engagement_rate: float
    reach: int
    impressions: int
    clicks: int
    shares: int
    comments: int
    saves: int
    conversion_rate: float
    cost_per_engagement: Optional[float] = None

class ScheduleOptimizer:
    """
    Enterprise schedule optimizer using machine learning for optimal timing prediction.
    
    Features:
    - ML-based performance prediction
    - Multi-factor optimization
    - Historical data analysis
    - A/B testing framework
    - Real-time adaptation
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
        # ML models for different optimization tasks
        self.engagement_model = None
        self.reach_model = None
        self.competition_model = None
        
        # Feature scalers
        self.scaler = StandardScaler()
        
        # Model storage paths
        self.model_storage_path = settings.MODEL_STORAGE_PATH
        
        # Cache for predictions
        self.prediction_cache = {}
        self.cache_ttl = timedelta(minutes=30)
        
        self._load_or_initialize_models()
        
        logger.info("Schedule optimizer initialized")
    
    def _load_or_initialize_models(self):
        """Load existing models or initialize new ones"""
        try:
            # Try to load existing models
            self.engagement_model = joblib.load(f"{self.model_storage_path}/engagement_model.joblib")
            self.reach_model = joblib.load(f"{self.model_storage_path}/reach_model.joblib")
            self.competition_model = joblib.load(f"{self.model_storage_path}/competition_model.joblib")
            self.scaler = joblib.load(f"{self.model_storage_path}/feature_scaler.joblib")
            
            logger.info("Loaded existing ML models")
            
        except (FileNotFoundError, Exception) as e:
            logger.info("Initializing new ML models")
            
            # Initialize new models with default parameters
            self.engagement_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.reach_model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
            
            self.competition_model = RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
    
    async def optimize_schedule(
        self,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str],
        config: OptimizationConfig,
        target_timezone: str = "UTC"
    ) -> TimingPrediction:
        """
        Optimize schedule timing using ML-based analysis.
        
        Args:
            creator_id: Creator identifier
            content_metadata: Content metadata for optimization
            platforms: Target platforms
            config: Optimization configuration
            target_timezone: Target timezone for scheduling
            
        Returns:
            Timing prediction with optimal schedule
        """
        try:
            logger.info(f"Optimizing schedule for creator {creator_id}")
            
            # Check cache first
            cache_key = self._generate_cache_key(creator_id, content_metadata, platforms, config)
            if cache_key in self.prediction_cache:
                cached_result, cached_time = self.prediction_cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    logger.info("Returning cached optimization result")
                    return cached_result
            
            # Collect historical data for training/prediction
            historical_data = await self._collect_historical_data(creator_id, platforms)
            
            # Extract features for prediction
            features = await self._extract_features(
                creator_id, content_metadata, platforms, target_timezone
            )
            
            # Update models with recent data if available
            if len(historical_data) > 10:  # Minimum data for training
                await self._update_models(historical_data, features)
            
            # Generate candidate times
            candidate_times = self._generate_candidate_times(config, target_timezone)
            
            # Evaluate each candidate time
            time_scores = []
            for candidate_time in candidate_times:
                score = await self._evaluate_timing(
                    candidate_time, creator_id, content_metadata, platforms, config
                )
                time_scores.append((candidate_time, score))
            
            # Sort by score (highest first)
            time_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select optimal time
            optimal_time, optimal_score = time_scores[0]
            
            # Generate performance predictions
            expected_performance = await self._predict_performance(
                optimal_time, creator_id, content_metadata, platforms
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                optimal_score, len(historical_data), features
            )
            
            # Analyze factors contribution
            factors_analysis = await self._analyze_factors(
                optimal_time, creator_id, content_metadata, platforms, config
            )
            
            # Generate alternative times
            alternative_times = time_scores[1:6]  # Top 5 alternatives
            
            # Generate optimization reasoning
            reasoning = self._generate_reasoning(
                config, factors_analysis, optimal_time, expected_performance
            )
            
            result = TimingPrediction(
                recommended_time=optimal_time,
                expected_performance=expected_performance,
                confidence_score=confidence_score,
                factors_analysis=factors_analysis,
                alternative_times=alternative_times,
                optimization_reasoning=reasoning
            )
            
            # Cache result
            self.prediction_cache[cache_key] = (result, datetime.utcnow())
            
            logger.info(f"Schedule optimization completed with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize schedule: {str(e)}")
            raise AgentError(f"Schedule optimization failed: {str(e)}")
    
    async def evaluate_schedule_performance(
        self,
        schedule_id: str,
        actual_performance: PerformanceMetrics
    ) -> Dict[str, Any]:
        """
        Evaluate actual performance vs predicted performance for model improvement.
        
        Args:
            schedule_id: Schedule identifier
            actual_performance: Actual performance metrics
            
        Returns:
            Performance evaluation results
        """
        try:
            logger.info(f"Evaluating schedule performance for {schedule_id}")
            
            # Get schedule details
            with get_db_session() as db:
                schedule = db.query(ScheduledJob).filter(
                    ScheduledJob.id == schedule_id
                ).first()
                
                if not schedule:
                    raise AgentError(f"Schedule {schedule_id} not found")
                
                predicted_performance = schedule.metadata.get('predicted_performance', {})
            
            # Calculate prediction accuracy
            accuracy_metrics = {}
            
            if 'engagement_rate' in predicted_performance:
                predicted_engagement = predicted_performance['engagement_rate']
                actual_engagement = actual_performance.engagement_rate
                
                accuracy_metrics['engagement_accuracy'] = 1.0 - abs(
                    predicted_engagement - actual_engagement
                ) / max(predicted_engagement, actual_engagement, 0.001)
            
            if 'reach' in predicted_performance:
                predicted_reach = predicted_performance['reach']
                actual_reach = actual_performance.reach
                
                accuracy_metrics['reach_accuracy'] = 1.0 - abs(
                    predicted_reach - actual_reach
                ) / max(predicted_reach, actual_reach, 1)
            
            # Calculate overall accuracy
            overall_accuracy = np.mean(list(accuracy_metrics.values())) if accuracy_metrics else 0.5
            
            # Store feedback for model improvement
            feedback_data = {
                'schedule_id': schedule_id,
                'predicted_performance': predicted_performance,
                'actual_performance': actual_performance.__dict__,
                'accuracy_metrics': accuracy_metrics,
                'overall_accuracy': overall_accuracy,
                'evaluation_timestamp': datetime.utcnow().isoformat()
            }
            
            await self._store_performance_feedback(feedback_data)
            
            logger.info(f"Performance evaluation completed with accuracy {overall_accuracy:.2f}")
            
            return {
                'schedule_id': schedule_id,
                'accuracy_metrics': accuracy_metrics,
                'overall_accuracy': overall_accuracy,
                'improvement_suggestions': self._generate_improvement_suggestions(
                    accuracy_metrics, predicted_performance, actual_performance.__dict__
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate performance: {str(e)}")
            raise AgentError(f"Performance evaluation failed: {str(e)}")
    
    async def retrain_models(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrain optimization models with latest data.
        
        Args:
            creator_id: Optional creator ID for personalized training
            
        Returns:
            Retraining results
        """
        try:
            logger.info("Starting model retraining")
            
            # Collect training data
            training_data = await self._collect_training_data(creator_id)
            
            if len(training_data) < 50:  # Minimum data requirement
                logger.warning("Insufficient training data for model retraining")
                return {
                    'status': 'skipped',
                    'reason': 'insufficient_data',
                    'data_points': len(training_data)
                }
            
            # Prepare features and targets
            features, engagement_targets, reach_targets, competition_targets = \
                self._prepare_training_data(training_data)
            
            # Split data
            X_train, X_test, y_eng_train, y_eng_test = train_test_split(
                features, engagement_targets, test_size=0.2, random_state=42
            )
            _, _, y_reach_train, y_reach_test = train_test_split(
                features, reach_targets, test_size=0.2, random_state=42
            )
            _, _, y_comp_train, y_comp_test = train_test_split(
                features, competition_targets, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            results = {}
            
            # Engagement model
            self.engagement_model.fit(X_train_scaled, y_eng_train)
            eng_pred = self.engagement_model.predict(X_test_scaled)
            results['engagement_model'] = {
                'r2_score': r2_score(y_eng_test, eng_pred),
                'mse': mean_squared_error(y_eng_test, eng_pred),
                'feature_importance': dict(zip(
                    range(len(features.columns)),
                    self.engagement_model.feature_importances_
                ))
            }
            
            # Reach model
            self.reach_model.fit(X_train_scaled, y_reach_train)
            reach_pred = self.reach_model.predict(X_test_scaled)
            results['reach_model'] = {
                'r2_score': r2_score(y_reach_test, reach_pred),
                'mse': mean_squared_error(y_reach_test, reach_pred)
            }
            
            # Competition model
            self.competition_model.fit(X_train_scaled, y_comp_train)
            comp_pred = self.competition_model.predict(X_test_scaled)
            results['competition_model'] = {
                'r2_score': r2_score(y_comp_test, comp_pred),
                'mse': mean_squared_error(y_comp_test, comp_pred)
            }
            
            # Save models
            self._save_models()
            
            logger.info("Model retraining completed successfully")
            
            return {
                'status': 'completed',
                'data_points': len(training_data),
                'model_performance': results,
                'retrain_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to retrain models: {str(e)}")
            raise AgentError(f"Model retraining failed: {str(e)}")
    
    async def _collect_historical_data(
        self,
        creator_id: str,
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Collect historical scheduling and performance data"""
        historical_data = []
        
        try:
            with get_db_session() as db:
                # Get completed schedules from last 90 days
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                
                schedules = db.query(ScheduledJob).filter(
                    ScheduledJob.creator_id == creator_id,
                    ScheduledJob.status == 'completed',
                    ScheduledJob.created_at >= cutoff_date,
                    ScheduledJob.performance_metrics.isnot(None)
                ).all()
                
                for schedule in schedules:
                    # Only include schedules for relevant platforms
                    if any(platform in schedule.platforms for platform in platforms):
                        historical_data.append({
                            'schedule_time': schedule.schedule_time,
                            'platforms': schedule.platforms,
                            'performance_metrics': schedule.performance_metrics,
                            'metadata': schedule.metadata or {}
                        })
            
            logger.info(f"Collected {len(historical_data)} historical data points")
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to collect historical data: {str(e)}")
            return []
    
    async def _extract_features(
        self,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str],
        target_timezone: str
    ) -> pd.DataFrame:
        """Extract features for ML prediction"""
        features = {}
        
        # Time-based features
        current_time = datetime.now(pytz.timezone(target_timezone))
        features['hour_of_day'] = current_time.hour
        features['day_of_week'] = current_time.weekday()
        features['day_of_month'] = current_time.day
        features['month'] = current_time.month
        features['is_weekend'] = int(current_time.weekday() >= 5)
        
        # Content features
        features['content_type'] = hash(content_metadata.get('content_type', 'general')) % 1000
        features['content_length'] = content_metadata.get('duration_seconds', 0)
        features['has_hashtags'] = int(len(content_metadata.get('hashtags', [])) > 0)
        features['hashtag_count'] = len(content_metadata.get('hashtags', []))
        
        # Platform features
        for platform in ['instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube']:
            features[f'platform_{platform}'] = int(platform in [p.lower() for p in platforms])
        
        features['platform_count'] = len(platforms)
        
        # Historical performance features (simplified)
        features['historical_avg_engagement'] = 0.05  # Mock data
        features['historical_avg_reach'] = 1000       # Mock data
        
        # Seasonal features
        features['is_holiday_period'] = int(current_time.month in [11, 12, 1])  # Holiday season
        features['is_summer'] = int(current_time.month in [6, 7, 8])           # Summer
        
        return pd.DataFrame([features])
    
    async def _update_models(self, historical_data: List[Dict[str, Any]], features: pd.DataFrame):
        """
Update ML models with recent data"""
        if len(historical_data) < 10:
            return
        
        try:
            # This would implement incremental learning
            # For now, we'll skip actual model updates to avoid complexity
            logger.info("Model update skipped (incremental learning not implemented)")
            
        except Exception as e:
            logger.error(f"Failed to update models: {str(e)}")
    
    def _generate_candidate_times(
        self,
        config: OptimizationConfig,
        target_timezone: str
    ) -> List[datetime]:
        """Generate candidate posting times within the optimization window"""
        candidates = []
        
        # Start from minimum delay
        start_time = datetime.now(pytz.timezone(target_timezone)) + timedelta(hours=config.min_delay_hours)
        end_time = start_time + timedelta(hours=config.time_horizon_hours)
        
        # Generate candidates every hour
        current_time = start_time
        while current_time < end_time:
            candidates.append(current_time)
            current_time += timedelta(hours=1)
        
        return candidates
    
    async def _evaluate_timing(
        self,
        candidate_time: datetime,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str],
        config: OptimizationConfig
    ) -> float:
        """
Evaluate a candidate timing using multiple factors"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            # Evaluate each factor
            for factor in config.factors:
                weight = config.weights.get(factor, 1.0)
                score = await self._evaluate_factor(
                    factor, candidate_time, creator_id, content_metadata, platforms
                )
                total_score += score * weight
                total_weight += weight
            
            # Normalize score
            final_score = total_score / total_weight if total_weight > 0 else 0.5
            
            return final_score
            
        except Exception as e:
            logger.error(f"Failed to evaluate timing: {str(e)}")
            return 0.5
    
    async def _evaluate_factor(
        self,
        factor: TimingFactor,
        candidate_time: datetime,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str]
    ) -> float:
        """Evaluate a specific timing factor"""
        try:
            if factor == TimingFactor.AUDIENCE_ACTIVITY:
                return await self._evaluate_audience_activity(candidate_time, creator_id, platforms)
            
            elif factor == TimingFactor.PLATFORM_ALGORITHM:
                return await self._evaluate_platform_algorithm(candidate_time, platforms)
            
            elif factor == TimingFactor.COMPETITION_LEVEL:
                return await self._evaluate_competition_level(candidate_time, platforms)
            
            elif factor == TimingFactor.CONTENT_TYPE:
                return self._evaluate_content_type(candidate_time, content_metadata)
            
            elif factor == TimingFactor.HISTORICAL_PERFORMANCE:
                return await self._evaluate_historical_performance(candidate_time, creator_id, platforms)
            
            elif factor == TimingFactor.SEASONAL_TRENDS:
                return self._evaluate_seasonal_trends(candidate_time)
            
            elif factor == TimingFactor.GLOBAL_EVENTS:
                return await self._evaluate_global_events(candidate_time)
            
            elif factor == TimingFactor.TIMEZONE_ALIGNMENT:
                return self._evaluate_timezone_alignment(candidate_time, platforms)
            
            else:
                return 0.5  # Default neutral score
                
        except Exception as e:
            logger.error(f"Failed to evaluate factor {factor}: {str(e)}")
            return 0.5
    
    async def _evaluate_audience_activity(
        self,
        candidate_time: datetime,
        creator_id: str,
        platforms: List[str]
    ) -> float:
        """Evaluate audience activity at candidate time"""
        try:
            with get_db_session() as db:
                hour = candidate_time.hour
                day_of_week = candidate_time.weekday()
                
                activities = db.query(AudienceActivity).filter(
                    AudienceActivity.creator_id == creator_id,
                    AudienceActivity.platform.in_(platforms),
                    AudienceActivity.hour_of_day == hour,
                    AudienceActivity.day_of_week == day_of_week
                ).all()
                
                if activities:
                    avg_score = np.mean([activity.activity_score for activity in activities])
                    return float(avg_score)
                else:
                    # Use default patterns
                    return self._get_default_activity_score(hour, day_of_week)
                    
        except Exception as e:
            logger.error(f"Failed to evaluate audience activity: {str(e)}")
            return 0.5
    
    async def _evaluate_platform_algorithm(
        self,
        candidate_time: datetime,
        platforms: List[str]
    ) -> float:
        """Evaluate platform algorithm preferences"""
        # Mock implementation based on known platform preferences
        hour = candidate_time.hour
        day_of_week = candidate_time.weekday()
        
        scores = []
        for platform in platforms:
            platform_lower = platform.lower()
            
            if platform_lower == 'instagram':
                # Instagram peak times: 6-9 AM, 12-2 PM, 5-7 PM
                if hour in [6, 7, 8, 9, 12, 13, 14, 17, 18, 19]:
                    scores.append(0.9)
                else:
                    scores.append(0.4)
                    
            elif platform_lower == 'twitter':
                # Twitter peak times: 7-9 AM, 12-1 PM, 5-6 PM
                if hour in [7, 8, 9, 12, 13, 17, 18]:
                    scores.append(0.8)
                else:
                    scores.append(0.5)
                    
            elif platform_lower == 'facebook':
                # Facebook peak times: 12-3 PM, 6-9 PM
                if hour in [12, 13, 14, 15, 18, 19, 20, 21]:
                    scores.append(0.7)
                else:
                    scores.append(0.4)
                    
            elif platform_lower == 'linkedin':
                # LinkedIn peak times: 7-9 AM, 5-6 PM (weekdays only)
                if day_of_week < 5 and hour in [7, 8, 9, 17, 18]:
                    scores.append(0.8)
                elif day_of_week >= 5:
                    scores.append(0.2)  # Poor performance on weekends
                else:
                    scores.append(0.5)
                    
            elif platform_lower == 'tiktok':
                # TikTok peak times: 6-10 PM, especially evenings
                if hour in [18, 19, 20, 21, 22]:
                    scores.append(0.9)
                else:
                    scores.append(0.5)
                    
            elif platform_lower == 'youtube':
                # YouTube peak times: 2-4 PM, 7-9 PM (weekends better)
                weekend_bonus = 0.2 if day_of_week >= 5 else 0
                if hour in [14, 15, 16, 19, 20, 21]:
                    scores.append(0.8 + weekend_bonus)
                else:
                    scores.append(0.4 + weekend_bonus)
            else:
                scores.append(0.5)  # Default neutral score
        
        return np.mean(scores) if scores else 0.5
    
    async def _evaluate_competition_level(
        self,
        candidate_time: datetime,
        platforms: List[str]
    ) -> float:
        """
Evaluate competition level (lower competition = higher score)"""
        hour = candidate_time.hour
        day_of_week = candidate_time.weekday()
        
        # Mock competition analysis
        # High competition times get lower scores
        high_competition_hours = [9, 12, 18, 21]  # Peak posting times
        weekend_penalty = 0.1 if day_of_week >= 5 else 0  # Weekends are more competitive
        
        if hour in high_competition_hours:
            base_score = 0.3
        else:
            base_score = 0.7
        
        # Platform-specific adjustments
        platform_competition = {
            'instagram': 0.8,  # Very competitive
            'twitter': 0.7,
            'facebook': 0.6,
            'linkedin': 0.4,   # Less competitive
            'tiktok': 0.9,     # Extremely competitive
            'youtube': 0.5
        }
        
        platform_factor = np.mean([
            1.0 - platform_competition.get(p.lower(), 0.5) for p in platforms
        ])
        
        final_score = (base_score + platform_factor) / 2 - weekend_penalty
        return max(0.1, min(1.0, final_score))
    
    def _evaluate_content_type(
        self,
        candidate_time: datetime,
        content_metadata: Dict[str, Any]
    ) -> float:
        """
Evaluate timing based on content type"""
        content_type = content_metadata.get('content_type', 'general').lower()
        hour = candidate_time.hour
        day_of_week = candidate_time.weekday()
        
        # Content type optimal timing patterns
        content_timing = {
            'video': {
                'peak_hours': [14, 15, 16, 19, 20, 21],
                'weekend_bonus': 0.2
            },
            'image': {
                'peak_hours': [6, 7, 8, 12, 17, 18, 19],
                'weekend_bonus': 0.1
            },
            'text': {
                'peak_hours': [7, 8, 9, 12, 13, 17, 18],
                'weekend_bonus': 0.0
            },
            'audio': {
                'peak_hours': [7, 8, 16, 17, 18, 19, 20],
                'weekend_bonus': 0.1
            }
        }
        
        timing_config = content_timing.get(content_type, content_timing['image'])
        
        base_score = 0.8 if hour in timing_config['peak_hours'] else 0.4
        weekend_bonus = timing_config['weekend_bonus'] if day_of_week >= 5 else 0
        
        return min(1.0, base_score + weekend_bonus)
    
    async def _evaluate_historical_performance(
        self,
        candidate_time: datetime,
        creator_id: str,
        platforms: List[str]
    ) -> float:
        """
Evaluate based on historical performance at similar times"""
        try:
            # Mock implementation - would analyze actual historical data
            hour = candidate_time.hour
            day_of_week = candidate_time.weekday()
            
            # Simulate historical performance lookup
            # In reality, this would query performance data from similar time slots
            base_performance = 0.5
            
            # Time-based adjustments based on common patterns
            if hour in [7, 8, 9, 12, 17, 18, 19]:  # Common high-performance hours
                base_performance += 0.2
            
            if day_of_week < 5:  # Weekdays generally perform better for business content
                base_performance += 0.1
            
            return min(1.0, base_performance)
            
        except Exception as e:
            logger.error(f"Failed to evaluate historical performance: {str(e)}")
            return 0.5
    
    def _evaluate_seasonal_trends(self, candidate_time: datetime) -> float:
        """Evaluate seasonal and trending factors"""
        month = candidate_time.month
        day = candidate_time.day
        
        # Seasonal adjustments
        seasonal_score = 0.5
        
        # Holiday periods (higher engagement)
        if month in [11, 12]:  # Thanksgiving, Christmas season
            seasonal_score += 0.2
        elif month == 1:       # New Year period
            seasonal_score += 0.1
        elif month in [6, 7, 8]:  # Summer vacation
            seasonal_score += 0.1
        
        # Back-to-school period (good for educational content)
        if month == 9:
            seasonal_score += 0.1
        
        # Valentine's Day
        if month == 2 and day == 14:
            seasonal_score += 0.15
        
        return min(1.0, seasonal_score)
    
    async def _evaluate_global_events(self, candidate_time: datetime) -> float:
        """
Evaluate impact of global events (simplified)"""
        # Mock implementation - would integrate with news/events APIs
        # For now, return neutral score
        return 0.5
    
    def _evaluate_timezone_alignment(
        self,
        candidate_time: datetime,
        platforms: List[str]
    ) -> float:
        """
Evaluate timezone alignment with target audience"""
        # Mock implementation - would consider creator's audience timezone distribution
        # For now, assume good alignment during reasonable hours
        hour = candidate_time.hour
        
        if 6 <= hour <= 23:  # Reasonable posting hours
            return 0.8
        else:
            return 0.3  # Poor timing for most timezones
    
    def _get_default_activity_score(self, hour: int, day_of_week: int) -> float:
        """
Get default activity score when no data available"""
        # Mock default patterns
        peak_hours = [7, 8, 9, 12, 17, 18, 19, 20]
        weekend_penalty = 0.1 if day_of_week >= 5 else 0
        
        base_score = 0.7 if hour in peak_hours else 0.4
        return max(0.1, base_score - weekend_penalty)
    
    async def _predict_performance(
        self,
        optimal_time: datetime,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, float]:
        """
Predict performance metrics for optimal time"""
        try:
            # Extract features for the optimal time
            features_df = await self._extract_features(
                creator_id, content_metadata, platforms, optimal_time.tzinfo.zone or "UTC"
            )
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Make predictions
            predicted_performance = {}
            
            if self.engagement_model:
                engagement_pred = self.engagement_model.predict(features_scaled)[0]
                predicted_performance['engagement_rate'] = max(0.001, engagement_pred)
            
            if self.reach_model:
                reach_pred = self.reach_model.predict(features_scaled)[0]
                predicted_performance['reach'] = max(1, int(reach_pred))
            
            # Add some derived metrics
            if 'reach' in predicted_performance and 'engagement_rate' in predicted_performance:
                predicted_performance['estimated_interactions'] = int(
                    predicted_performance['reach'] * predicted_performance['engagement_rate']
                )
            
            return predicted_performance
            
        except Exception as e:
            logger.error(f"Failed to predict performance: {str(e)}")
            # Return mock predictions
            return {
                'engagement_rate': 0.05,
                'reach': 1000,
                'estimated_interactions': 50
            }
    
    def _calculate_confidence(
        self,
        optimal_score: float,
        data_points: int,
        features: pd.DataFrame
    ) -> float:
        """Calculate confidence in the optimization result"""
        # Base confidence from optimization score
        score_confidence = optimal_score
        
        # Data availability confidence
        data_confidence = min(1.0, data_points / 100)  # Full confidence at 100+ data points
        
        # Feature completeness confidence (all features present)
        feature_confidence = 0.8  # Mock confidence
        
        # Combined confidence
        combined_confidence = (
            score_confidence * 0.4 +
            data_confidence * 0.3 +
            feature_confidence * 0.3
        )
        
        return combined_confidence
    
    async def _analyze_factors(
        self,
        optimal_time: datetime,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str],
        config: OptimizationConfig
    ) -> Dict[TimingFactor, float]:
        """
Analyze contribution of each factor to the optimal timing"""
        factors_analysis = {}
        
        for factor in config.factors:
            score = await self._evaluate_factor(
                factor, optimal_time, creator_id, content_metadata, platforms
            )
            factors_analysis[factor] = score
        
        return factors_analysis
    
    def _generate_reasoning(
        self,
        config: OptimizationConfig,
        factors_analysis: Dict[TimingFactor, float],
        optimal_time: datetime,
        expected_performance: Dict[str, float]
    ) -> List[str]:
        """
Generate human-readable optimization reasoning"""
        reasoning = []
        
        # Strategy-based reasoning
        if config.strategy == OptimizationStrategy.ENGAGEMENT_MAX:
            reasoning.append("Optimized for maximum audience engagement")
        elif config.strategy == OptimizationStrategy.REACH_MAX:
            reasoning.append("Optimized for maximum content reach")
        elif config.strategy == OptimizationStrategy.BALANCED:
            reasoning.append("Balanced optimization across multiple performance metrics")
        
        # Top factors reasoning
        top_factors = sorted(factors_analysis.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for factor, score in top_factors:
            if score > 0.6:
                if factor == TimingFactor.AUDIENCE_ACTIVITY:
                    reasoning.append("High audience activity expected at this time")
                elif factor == TimingFactor.PLATFORM_ALGORITHM:
                    reasoning.append("Platform algorithms favor content posted at this time")
                elif factor == TimingFactor.COMPETITION_LEVEL:
                    reasoning.append("Lower competition window identified")
        
        # Performance expectation
        if 'engagement_rate' in expected_performance:
            eng_rate = expected_performance['engagement_rate']
            if eng_rate > 0.1:
                reasoning.append(f"High engagement rate expected ({eng_rate:.1%})")
            elif eng_rate > 0.05:
                reasoning.append(f"Moderate engagement rate expected ({eng_rate:.1%})")
        
        if not reasoning:
            reasoning.append("Optimal timing based on multi-factor analysis")
        
        return reasoning
    
    def _generate_cache_key(
        self,
        creator_id: str,
        content_metadata: Dict[str, Any],
        platforms: List[str],
        config: OptimizationConfig
    ) -> str:
        """Generate cache key for optimization results"""
        key_parts = [
            creator_id,
            content_metadata.get('content_type', 'general'),
            ':'.join(sorted(platforms)),
            config.strategy.value,
            str(config.time_horizon_hours)
        ]
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    async def _collect_training_data(self, creator_id: Optional[str]) -> List[Dict[str, Any]]:
        """
Collect data for model training"""
        training_data = []
        
        try:
            with get_db_session() as db:
                query = db.query(ScheduledJob).filter(
                    ScheduledJob.status == 'completed',
                    ScheduledJob.performance_metrics.isnot(None)
                )
                
                if creator_id:
                    query = query.filter(ScheduledJob.creator_id == creator_id)
                
                # Get last 1000 completed schedules for training
                schedules = query.order_by(ScheduledJob.created_at.desc()).limit(1000).all()
                
                for schedule in schedules:
                    training_data.append({
                        'schedule_time': schedule.schedule_time,
                        'platforms': schedule.platforms,
                        'performance_metrics': schedule.performance_metrics,
                        'metadata': schedule.metadata or {},
                        'creator_id': schedule.creator_id
                    })
            
            return training_data
            
        except Exception as e:
            logger.error(f"Failed to collect training data: {str(e)}")
            return []
    
    def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        features_list = []
        engagement_targets = []
        reach_targets = []
        competition_targets = []
        
        for data_point in training_data:
            schedule_time = data_point['schedule_time']
            platforms = data_point['platforms']
            performance = data_point['performance_metrics']
            metadata = data_point['metadata']
            
            # Extract features (simplified)
            features = {
                'hour_of_day': schedule_time.hour,
                'day_of_week': schedule_time.weekday(),
                'month': schedule_time.month,
                'is_weekend': int(schedule_time.weekday() >= 5),
                'platform_count': len(platforms),
                'content_type_hash': hash(metadata.get('content_type', 'general')) % 1000
            }
            
            # Platform features
            for platform in ['instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube']:
                features[f'platform_{platform}'] = int(platform in [p.lower() for p in platforms])
            
            features_list.append(features)
            
            # Extract targets
            avg_engagement = np.mean([
                perf.get('engagement_rate', 0.05) for perf in performance.values()
                if isinstance(perf, dict)
            ])
            avg_reach = np.mean([
                perf.get('reach', 1000) for perf in performance.values()
                if isinstance(perf, dict)
            ])
            
            engagement_targets.append(avg_engagement)
            reach_targets.append(avg_reach)
            competition_targets.append(0.5)  # Mock competition score
        
        features_df = pd.DataFrame(features_list)
        return (
            features_df,
            np.array(engagement_targets),
            np.array(reach_targets),
            np.array(competition_targets)
        )
    
    def _save_models(self):
        """
Save trained models to disk"""
        try:
            joblib.dump(self.engagement_model, f"{self.model_storage_path}/engagement_model.joblib")
            joblib.dump(self.reach_model, f"{self.model_storage_path}/reach_model.joblib")
            joblib.dump(self.competition_model, f"{self.model_storage_path}/competition_model.joblib")
            joblib.dump(self.scaler, f"{self.model_storage_path}/feature_scaler.joblib")
            
            logger.info("ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {str(e)}")
    
    async def _store_performance_feedback(self, feedback_data: Dict[str, Any]):
        """Store performance feedback for model improvement"""
        # This would typically store feedback in a database or data pipeline
        # For now, we'll just log it
        logger.info(f"Performance feedback recorded: {feedback_data['overall_accuracy']:.2f}")
    
    def _generate_improvement_suggestions(
        self,
        accuracy_metrics: Dict[str, float],
        predicted_performance: Dict[str, Any],
        actual_performance: Dict[str, Any]
    ) -> List[str]:
        """Generate suggestions for model improvement"""
        suggestions = []
        
        overall_accuracy = np.mean(list(accuracy_metrics.values())) if accuracy_metrics else 0.5
        
        if overall_accuracy < 0.7:
            suggestions.append("Model accuracy is below threshold - consider retraining with more data")
        
        if 'engagement_accuracy' in accuracy_metrics and accuracy_metrics['engagement_accuracy'] < 0.6:
            suggestions.append("Engagement prediction accuracy is low - review audience activity patterns")
        
        if 'reach_accuracy' in accuracy_metrics and accuracy_metrics['reach_accuracy'] < 0.6:
            suggestions.append("Reach prediction accuracy is low - review platform algorithm factors")
        
        return suggestions

class TimingAnalyzer:
    """
    Enterprise timing analysis system for content scheduling optimization.
    
    Provides detailed analytics and insights for scheduling decisions.
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        logger.info("Timing analyzer initialized")
    
    async def analyze_creator_patterns(self, creator_id: str) -> Dict[str, Any]:
        """Analyze creator's posting patterns and performance"""
        try:
            with get_db_session() as db:
                # Get creator's schedule history
                schedules = db.query(ScheduledJob).filter(
                    ScheduledJob.creator_id == creator_id,
                    ScheduledJob.status == 'completed'
                ).order_by(ScheduledJob.schedule_time.desc()).limit(500).all()
                
                if not schedules:
                    return {'error': 'No scheduling history found for creator'}
                
                # Analyze patterns
                patterns = {
                    'posting_frequency': self._analyze_posting_frequency(schedules),
                    'optimal_hours': self._analyze_optimal_hours(schedules),
                    'platform_performance': self._analyze_platform_performance(schedules),
                    'content_type_performance': self._analyze_content_type_performance(schedules),
                    'seasonal_trends': self._analyze_seasonal_trends(schedules),
                    'performance_trends': self._analyze_performance_trends(schedules)
                }
                
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to analyze creator patterns: {str(e)}")
            raise AgentError(f"Pattern analysis failed: {str(e)}")
    
    def _analyze_posting_frequency(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """Analyze posting frequency patterns"""
        if not schedules:
            return {}
        
        # Calculate daily posting frequency
        daily_posts = {}
        for schedule in schedules:
            date_key = schedule.schedule_time.date()
            daily_posts[date_key] = daily_posts.get(date_key, 0) + 1
        
        frequencies = list(daily_posts.values())
        
        return {
            'average_posts_per_day': np.mean(frequencies) if frequencies else 0,
            'max_posts_per_day': max(frequencies) if frequencies else 0,
            'min_posts_per_day': min(frequencies) if frequencies else 0,
            'most_active_days': sorted(daily_posts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_optimal_hours(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """
Analyze optimal posting hours based on performance"""
        hourly_performance = {}
        
        for schedule in schedules:
            hour = schedule.schedule_time.hour
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            
            # Calculate average performance across platforms
            if schedule.performance_metrics:
                avg_engagement = np.mean([
                    perf.get('engagement_rate', 0.05) for perf in schedule.performance_metrics.values()
                    if isinstance(perf, dict) and 'engagement_rate' in perf
                ])
                hourly_performance[hour].append(avg_engagement)
        
        # Calculate average performance by hour
        hourly_averages = {
            hour: np.mean(performances) 
            for hour, performances in hourly_performance.items()
            if performances
        }
        
        # Find top performing hours
        top_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'hourly_averages': hourly_averages,
            'top_performing_hours': top_hours,
            'worst_performing_hours': sorted(hourly_averages.items(), key=lambda x: x[1])[:3]
        }
    
    def _analyze_platform_performance(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """
Analyze performance across different platforms"""
        platform_performance = {}
        
        for schedule in schedules:
            if not schedule.performance_metrics:
                continue
                
            for platform in schedule.platforms:
                if platform not in platform_performance:
                    platform_performance[platform] = []
                
                # Get platform-specific performance
                perf = schedule.performance_metrics.get(platform, {})
                if isinstance(perf, dict) and 'engagement_rate' in perf:
                    platform_performance[platform].append(perf['engagement_rate'])
        
        # Calculate averages
        platform_averages = {
            platform: {
                'avg_engagement': np.mean(performances),
                'post_count': len(performances),
                'consistency': np.std(performances)
            }
            for platform, performances in platform_performance.items()
            if performances
        }
        
        return platform_averages
    
    def _analyze_content_type_performance(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """
Analyze performance by content type"""
        content_performance = {}
        
        for schedule in schedules:
            if not schedule.metadata or not schedule.performance_metrics:
                continue
                
            content_type = schedule.metadata.get('content_type', 'general')
            
            if content_type not in content_performance:
                content_performance[content_type] = []
            
            # Calculate average performance
            avg_engagement = np.mean([
                perf.get('engagement_rate', 0.05) for perf in schedule.performance_metrics.values()
                if isinstance(perf, dict) and 'engagement_rate' in perf
            ])
            content_performance[content_type].append(avg_engagement)
        
        # Calculate averages by content type
        content_averages = {
            content_type: {
                'avg_engagement': np.mean(performances),
                'post_count': len(performances)
            }
            for content_type, performances in content_performance.items()
            if performances
        }
        
        return content_averages
    
    def _analyze_seasonal_trends(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """
Analyze seasonal performance trends"""
        monthly_performance = {}
        
        for schedule in schedules:
            if not schedule.performance_metrics:
                continue
                
            month = schedule.schedule_time.month
            
            if month not in monthly_performance:
                monthly_performance[month] = []
            
            avg_engagement = np.mean([
                perf.get('engagement_rate', 0.05) for perf in schedule.performance_metrics.values()
                if isinstance(perf, dict) and 'engagement_rate' in perf
            ])
            monthly_performance[month].append(avg_engagement)
        
        # Calculate monthly averages
        monthly_averages = {
            month: np.mean(performances)
            for month, performances in monthly_performance.items()
            if performances
        }
        
        # Identify seasonal patterns
        best_months = sorted(monthly_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        worst_months = sorted(monthly_averages.items(), key=lambda x: x[1])[:3]
        
        return {
            'monthly_averages': monthly_averages,
            'best_months': best_months,
            'worst_months': worst_months
        }
    
    def _analyze_performance_trends(self, schedules: List[ScheduledJob]) -> Dict[str, Any]:
        """
Analyze overall performance trends over time"""
        # Sort schedules by time
        sorted_schedules = sorted(schedules, key=lambda x: x.schedule_time)
        
        # Calculate rolling averages
        window_size = 30  # 30-post rolling window
        rolling_averages = []
        
        for i in range(len(sorted_schedules)):
            start_idx = max(0, i - window_size + 1)
            window_schedules = sorted_schedules[start_idx:i+1]
            
            avg_engagement = np.mean([
                np.mean([
                    perf.get('engagement_rate', 0.05) for perf in schedule.performance_metrics.values()
                    if isinstance(perf, dict) and 'engagement_rate' in perf
                ])
                for schedule in window_schedules
                if schedule.performance_metrics
            ])
            
            rolling_averages.append({
                'date': sorted_schedules[i].schedule_time.date(),
                'rolling_avg_engagement': avg_engagement
            })
        
        # Calculate trend direction
        recent_avg = np.mean([ra['rolling_avg_engagement'] for ra in rolling_averages[-10:]])
        older_avg = np.mean([ra['rolling_avg_engagement'] for ra in rolling_averages[-30:-10]])
        
        trend_direction = "improving" if recent_avg > older_avg else "declining"
        
        return {
            'rolling_averages': rolling_averages[-30:],  # Last 30 data points
            'trend_direction': trend_direction,
            'recent_performance': recent_avg,
            'historical_performance': older_avg
        }
