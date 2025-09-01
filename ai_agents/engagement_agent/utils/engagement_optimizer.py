"""Engagement Optimizer - Advanced Engagement Analytics & Optimization Engine

Industrial-grade engagement optimization system with ML-powered insights,
A/B testing capabilities, and real-time performance optimization.

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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

from ...ai.core.config import settings
from ...core.managers.database_manager import DatabaseManager
from ...ml.models.time_series_models import TimeSeriesPredictor
from ...ml.models.clustering_models import AudienceSegmentation
from ...utils.statistical_analyzer import StatisticalAnalyzer
from ...utils.performance_monitor import performance_monitor
from ...utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class OptimizationObjective(Enum):
    """
Engagement optimization objectives"""

    MAXIMIZE_REACH = "maximize_reach"
    MAXIMIZE_ENGAGEMENT_RATE = "maximize_engagement_rate" 
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    MAXIMIZE_RETENTION = "maximize_retention"
    MINIMIZE_CHURN = "minimize_churn"
    MAXIMIZE_VIRAL_COEFFICIENT = "maximize_viral_coefficient"
    MAXIMIZE_AUDIENCE_GROWTH = "maximize_audience_growth"

class ExperimentType(Enum):
    """A/B testing experiment types"""

    POSTING_TIME = "posting_time"
    CONTENT_FORMAT = "content_format"
    HASHTAG_STRATEGY = "hashtag_strategy"
    CAPTION_LENGTH = "caption_length"
    CALL_TO_ACTION = "call_to_action"
    VISUAL_STYLE = "visual_style"
    FREQUENCY = "frequency"

@dataclass
class OptimizationRecommendation:
    """Engagement optimization recommendation"""
    objective: OptimizationObjective
    recommendation_type: str
    description: str
    expected_improvement: float
    confidence_score: float
    implementation_effort: str  # low, medium, high
    timeframe_days: int
    success_metrics: List[str]
    action_items: List[str]
    risk_assessment: Dict[str, Any]

@dataclass
class ABTestExperiment:
    """
A/B testing experiment configuration"""
    experiment_id: str
    experiment_type: ExperimentType
    hypothesis: str
    control_group: Dict[str, Any]
    treatment_group: Dict[str, Any]
    success_metric: str
    minimum_sample_size: int
    confidence_level: float
    expected_effect_size: float
    duration_days: int
    status: str  # planned, running, completed, cancelled
    results: Optional[Dict[str, Any]] = None

@dataclass
class InteractionPattern:
    """
User interaction pattern analysis"""
    user_id: str
    platform: str
    interaction_type: str
    frequency: int
    timing_pattern: List[int]  # Hours of day
    content_preferences: Dict[str, float]
    engagement_value: float
    loyalty_score: float
    churn_probability: float

class EngagementOptimizer:
    """
    Advanced Engagement Optimization Engine
    
    Machine learning-powered engagement optimization with A/B testing,
    predictive analytics, and automated recommendation generation.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager(namespace="engagement_optimizer")
        self.time_series_predictor = TimeSeriesPredictor()
        self.audience_segmentation = AudienceSegmentation()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # ML models
        self.engagement_predictor = None
        self.churn_predictor = None
        self.viral_predictor = None
        
        # Optimization state
        self.active_experiments: Dict[str, ABTestExperiment] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        self.model_performance_metrics: Dict[str, Any] = {}
        
        logger.info("Engagement Optimizer initialized")

    async def initialize(self) -> bool:
        """Initialize optimizer with ML models and historical data"""
        try:
            # Load and train ML models
            await self._initialize_ml_models()
            
            # Load active experiments
            await self._load_active_experiments()
            
            # Load optimization history
            await self._load_optimization_history()
            
            logger.info("Engagement Optimizer successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Optimizer: {str(e)}")
            return False

    @performance_monitor.track_execution_time
    async def optimize_engagement_strategy(self,
                                         creator_id: str,
                                         platform: str,
                                         objective: OptimizationObjective,
                                         historical_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
        Generate optimized engagement strategy recommendations
        
        Args:
            creator_id: Creator identifier
            platform: Target platform
            objective: Optimization objective
            historical_data: Historical engagement data
            
        Returns:
            List[OptimizationRecommendation]: Prioritized recommendations
        """
        try:
            # Analyze current performance patterns
            performance_analysis = await self._analyze_performance_patterns(
                historical_data, objective
            )
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(
                creator_id, platform, performance_analysis
            )
            
            # Generate ML-powered recommendations
            ml_recommendations = await self._generate_ml_recommendations(
                creator_id, platform, objective, historical_data
            )
            
            # Perform statistical significance testing
            stat_recommendations = await self._generate_statistical_recommendations(
                historical_data, objective
            )
            
            # Combine and prioritize recommendations
            all_recommendations = ml_recommendations + stat_recommendations
            prioritized_recommendations = await self._prioritize_recommendations(
                all_recommendations, objective, creator_id
            )
            
            # Validate recommendations with business logic
            validated_recommendations = await self._validate_recommendations(
                prioritized_recommendations, creator_id, platform
            )
            
            # Store optimization results
            await self._store_optimization_results(
                creator_id, platform, objective, validated_recommendations
            )
            
            logger.info(f"Generated {len(validated_recommendations)} optimization recommendations")
            return validated_recommendations
            
        except Exception as e:
            logger.error(f"Failed to optimize engagement strategy: {str(e)}")
            raise ProcessingError(f"Optimization failed: {str(e)}")

    async def run_ab_test_experiment(self,
                                   experiment_config: ABTestExperiment) -> Dict[str, Any]:
        """
        Run A/B testing experiment for engagement optimization
        
        Args:
            experiment_config: Experiment configuration
            
        Returns:
            Dict: Experiment results and analysis
        """
        try:
            # Validate experiment configuration
            validation_result = await self._validate_experiment_config(experiment_config)
            if not validation_result['valid']:
                raise ValidationError(f"Invalid experiment config: {validation_result['error']}")
            
            # Calculate required sample size
            sample_size = await self._calculate_required_sample_size(
                experiment_config.expected_effect_size,
                experiment_config.confidence_level
            )
            experiment_config.minimum_sample_size = sample_size
            
            # Initialize experiment tracking
            experiment_config.status = "running"
            self.active_experiments[experiment_config.experiment_id] = experiment_config
            
            # Monitor experiment progress
            monitoring_task = asyncio.create_task(
                self._monitor_experiment_progress(experiment_config.experiment_id)
            )
            
            # Wait for experiment completion or timeout
            completion_result = await asyncio.wait_for(
                monitoring_task,
                timeout=experiment_config.duration_days * 24 * 3600  # Convert to seconds
            )
            
            # Analyze experiment results
            results = await self._analyze_experiment_results(experiment_config.experiment_id)
            
            # Update experiment status
            experiment_config.results = results
            experiment_config.status = "completed"
            
            logger.info(f"A/B test experiment {experiment_config.experiment_id} completed")
            return results
            
        except asyncio.TimeoutError:
            logger.warning(f"Experiment {experiment_config.experiment_id} timed out")
            experiment_config.status = "cancelled"
            return {"status": "timeout", "partial_results": await self._get_partial_results(experiment_config.experiment_id)}
            
        except Exception as e:
            logger.error(f"A/B test experiment failed: {str(e)}")
            experiment_config.status = "cancelled"
            raise ProcessingError(f"Experiment failed: {str(e)}")

    async def predict_engagement_performance(self,
                                           content_features: Dict[str, Any],
                                           platform: str,
                                           posting_time: datetime) -> Dict[str, Any]:
        """
        Predict engagement performance for content before posting
        
        Args:
            content_features: Content characteristics
            platform: Target platform
            posting_time: Planned posting time
            
        Returns:
            Dict: Predicted engagement metrics
        """
        try:
            # Prepare feature vector
            feature_vector = await self._prepare_feature_vector(
                content_features, platform, posting_time
            )
            
            # Predict with ensemble of models
            predictions = {}
            
            # Engagement rate prediction
            if self.engagement_predictor:
                engagement_pred = await self.engagement_predictor.predict(feature_vector)
                predictions['engagement_rate'] = engagement_pred[0]
            
            # Reach prediction
            reach_pred = await self._predict_reach(feature_vector, platform)
            predictions['predicted_reach'] = reach_pred
            
            # Viral coefficient prediction
            if self.viral_predictor:
                viral_pred = await self.viral_predictor.predict(feature_vector)
                predictions['viral_coefficient'] = viral_pred[0]
            
            # Time-series based predictions
            time_series_pred = await self.time_series_predictor.predict_engagement(
                feature_vector, hours_ahead=24
            )
            predictions['hourly_engagement'] = time_series_pred
            
            # Confidence intervals
            predictions['confidence_intervals'] = await self._calculate_prediction_confidence(
                feature_vector, predictions
            )
            
            # Performance comparison with historical content
            performance_comparison = await self._compare_with_historical_performance(
                content_features, platform, predictions
            )
            predictions['performance_comparison'] = performance_comparison
            
            # Risk assessment
            risk_assessment = await self._assess_content_risks(
                content_features, predictions
            )
            predictions['risk_assessment'] = risk_assessment
            
            logger.info("Engagement performance prediction completed")
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict engagement performance: {str(e)}")
            raise ProcessingError(f"Prediction failed: {str(e)}")

    async def analyze_audience_segments(self,
                                      creator_id: str,
                                      platform: str) -> Dict[str, Any]:
        """
        Perform advanced audience segmentation analysis
        
        Args:
            creator_id: Creator identifier
            platform: Target platform
            
        Returns:
            Dict: Audience segmentation insights
        """
        try:
            # Fetch audience interaction data
            audience_data = await self._fetch_audience_interaction_data(
                creator_id, platform
            )
            
            # Perform clustering-based segmentation
            segments = await self.audience_segmentation.segment_audience(audience_data)
            
            # Analyze segment characteristics
            segment_analysis = {}
            for segment_id, segment_data in segments.items():
                analysis = await self._analyze_segment_characteristics(segment_data)
                segment_analysis[segment_id] = analysis
            
            # Generate segment-specific strategies
            segment_strategies = {}
            for segment_id, analysis in segment_analysis.items():
                strategy = await self._generate_segment_strategy(analysis)
                segment_strategies[segment_id] = strategy
            
            # Calculate segment value and priority
            segment_priorities = await self._calculate_segment_priorities(
                segment_analysis, creator_id
            )
            
            # Generate cross-segment insights
            cross_segment_insights = await self._generate_cross_segment_insights(
                segment_analysis
            )
            
            result = {
                'segments': segment_analysis,
                'strategies': segment_strategies,
                'priorities': segment_priorities,
                'cross_segment_insights': cross_segment_insights,
                'total_segments': len(segments),
                'segmentation_quality_score': await self._evaluate_segmentation_quality(segments)
            }
            
            # Cache results for performance
            await self.cache_manager.set(
                f"audience_segments_{creator_id}_{platform}",
                result,
                ttl=7200  # 2 hours cache
            )
            
            logger.info(f"Audience segmentation completed: {len(segments)} segments identified")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze audience segments: {str(e)}")
            raise ProcessingError(f"Audience segmentation failed: {str(e)}")

    # Private helper methods
    
    async def _initialize_ml_models(self) -> None:
        """Initialize and train ML models for optimization"""
        try:
            # Load historical data for training
            training_data = await self._fetch_training_data()
            
            if len(training_data) < 100:  # Minimum data requirement
                logger.warning("Insufficient training data, using pre-trained models")
                await self._load_pretrained_models()
                return
            
            # Prepare training features
            X, y_engagement, y_churn, y_viral = await self._prepare_training_data(training_data)
            
            # Train engagement predictor
            self.engagement_predictor = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_engagement, test_size=0.2, random_state=42
            )
            
            self.engagement_predictor.fit(X_train, y_train)
            engagement_score = self.engagement_predictor.score(X_test, y_test)
            
            # Train churn predictor
            self.churn_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            self.churn_predictor.fit(X_train, y_churn[:len(X_train)])
            
            # Train viral coefficient predictor
            self.viral_predictor = GradientBoostingRegressor(
                n_estimators=80,
                learning_rate=0.15,
                max_depth=5,
                random_state=42
            )
            self.viral_predictor.fit(X_train, y_viral[:len(X_train)])
            
            # Store model performance metrics
            self.model_performance_metrics = {
                'engagement_r2_score': engagement_score,
                'training_data_size': len(training_data),
                'last_trained': datetime.utcnow().isoformat(),
                'feature_importance': self.engagement_predictor.feature_importances_.tolist()
            }
            
            logger.info(f"ML models trained successfully. Engagement R² score: {engagement_score:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {str(e)}")
            await self._load_pretrained_models()

    async def _analyze_performance_patterns(self,
                                          historical_data: Dict[str, Any],
                                          objective: OptimizationObjective) -> Dict[str, Any]:
        """Analyze historical performance patterns"""
        try:
            df = pd.DataFrame(historical_data['metrics'])
            
            # Time-based analysis
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['day_of_month'] = pd.to_datetime(df['timestamp']).dt.day
            
            patterns = {
                'best_posting_hours': df.groupby('hour')['engagement_rate'].mean().nlargest(5).to_dict(),
                'best_days_of_week': df.groupby('day_of_week')['engagement_rate'].mean().nlargest(3).to_dict(),
                'engagement_trends': self._calculate_engagement_trends(df),
                'seasonal_patterns': self._identify_seasonal_patterns(df),
                'content_type_performance': df.groupby('content_type')['engagement_rate'].mean().to_dict(),
                'hashtag_effectiveness': self._analyze_hashtag_performance(df),
                'audience_growth_correlation': self._analyze_growth_correlation(df)
            }
            
            # Statistical significance testing
            patterns['statistical_significance'] = await self._test_pattern_significance(df)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze performance patterns: {str(e)}")
            return {}

    async def _generate_ml_recommendations(self,
                                         creator_id: str,
                                         platform: str,
                                         objective: OptimizationObjective,
                                         historical_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate ML-powered optimization recommendations"""
        recommendations = []
        
        try:
            if self.engagement_predictor is None:
                return recommendations
            
            # Feature importance analysis
            feature_importance = self.engagement_predictor.feature_importances_
            important_features = np.argsort(feature_importance)[-5:]  # Top 5 features
            
            # Generate recommendations based on feature importance
            for feature_idx in important_features:
                feature_name = self._get_feature_name(feature_idx)
                importance_score = feature_importance[feature_idx]
                
                if importance_score > 0.1:  # Threshold for significant features
                    recommendation = await self._create_feature_based_recommendation(
                        feature_name, importance_score, objective, historical_data
                    )
                    if recommendation:
                        recommendations.append(recommendation)
            
            # Prediction-based recommendations
            prediction_recommendations = await self._generate_prediction_based_recommendations(
                creator_id, platform, objective
            )
            recommendations.extend(prediction_recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate ML recommendations: {str(e)}")
            return recommendations

    def _calculate_engagement_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate engagement trends over time"""
        try:
            df_sorted = df.sort_values('timestamp')
            df_sorted['moving_avg'] = df_sorted['engagement_rate'].rolling(window=7).mean()
            
            # Calculate trend direction
            recent_trend = np.polyfit(range(len(df_sorted[-30:])), 
                                    df_sorted['engagement_rate'].tail(30), 1)[0]
            
            return {
                'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing',
                'trend_strength': abs(recent_trend),
                'volatility': df_sorted['engagement_rate'].std(),
                'average_engagement': df_sorted['engagement_rate'].mean(),
                'peak_performance': df_sorted['engagement_rate'].max(),
                'consistency_score': 1 - (df_sorted['engagement_rate'].std() / df_sorted['engagement_rate'].mean())
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement trends: {str(e)}")
            return {}

    def _identify_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify seasonal engagement patterns"""
        try:
            df['month'] = pd.to_datetime(df['timestamp']).dt.month
            monthly_avg = df.groupby('month')['engagement_rate'].mean()
            
            # Identify peak and low seasons
            peak_months = monthly_avg.nlargest(3).index.tolist()
            low_months = monthly_avg.nsmallest(3).index.tolist()
            
            return {
                'peak_months': peak_months,
                'low_months': low_months,
                'seasonal_variation': monthly_avg.std(),
                'monthly_averages': monthly_avg.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to identify seasonal patterns: {str(e)}")
            return {}


class InteractionAnalyzer:
    """
    Advanced User Interaction Analysis System
    
    Analyzes user interaction patterns, behavior sequences, and engagement quality
    to provide deep insights into audience behavior and preferences.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager(namespace="interaction_analyzer")
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # Interaction tracking
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
        self.behavior_sequences: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("Interaction Analyzer initialized")

    async def analyze_user_interactions(self,
                                      creator_id: str,
                                      platform: str,
                                      timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Analyze user interaction patterns and behaviors
        
        Args:
            creator_id: Creator identifier
            platform: Target platform
            timeframe_days: Analysis timeframe in days
            
        Returns:
            Dict: Comprehensive interaction analysis
        """
        try:
            # Fetch interaction data
            interaction_data = await self._fetch_interaction_data(
                creator_id, platform, timeframe_days
            )
            
            # Analyze interaction patterns
            patterns = await self._analyze_interaction_patterns(interaction_data)
            
            # Identify high-value users
            high_value_users = await self._identify_high_value_users(interaction_data)
            
            # Analyze engagement sequences
            sequences = await self._analyze_engagement_sequences(interaction_data)
            
            # Calculate interaction quality metrics
            quality_metrics = await self._calculate_interaction_quality(interaction_data)
            
            # Generate behavioral insights
            behavioral_insights = await self._generate_behavioral_insights(
                patterns, sequences, quality_metrics
            )
            
            result = {
                'interaction_patterns': patterns,
                'high_value_users': high_value_users,
                'engagement_sequences': sequences,
                'quality_metrics': quality_metrics,
                'behavioral_insights': behavioral_insights,
                'analysis_period': f"{timeframe_days} days",
                'total_interactions': len(interaction_data)
            }
            
            # Cache results
            await self.cache_manager.set(
                f"interaction_analysis_{creator_id}_{platform}",
                result,
                ttl=3600
            )
            
            logger.info(f"Interaction analysis completed for {creator_id} on {platform}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze user interactions: {str(e)}")
            raise ProcessingError(f"Interaction analysis failed: {str(e)}")

    async def predict_user_churn(self,
                               user_interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict user churn probability based on interaction patterns
        
        Args:
            user_interactions: Historical user interactions
            
        Returns:
            Dict: Churn prediction and risk factors
        """
        try:
            # Extract churn features
            features = await self._extract_churn_features(user_interactions)
            
            # Calculate engagement decline indicators
            decline_indicators = await self._calculate_decline_indicators(user_interactions)
            
            # Assess interaction quality trends
            quality_trends = await self._assess_interaction_quality_trends(user_interactions)
            
            # Calculate churn probability
            churn_probability = await self._calculate_churn_probability(
                features, decline_indicators, quality_trends
            )
            
            # Identify churn risk factors
            risk_factors = await self._identify_churn_risk_factors(
                features, decline_indicators
            )
            
            # Generate retention recommendations
            retention_recommendations = await self._generate_retention_recommendations(
                churn_probability, risk_factors
            )
            
            return {
                'churn_probability': churn_probability,
                'risk_level': self._categorize_risk_level(churn_probability),
                'risk_factors': risk_factors,
                'retention_recommendations': retention_recommendations,
                'decline_indicators': decline_indicators,
                'quality_trends': quality_trends
            }
            
        except Exception as e:
            logger.error(f"Failed to predict user churn: {str(e)}")
            raise ProcessingError(f"Churn prediction failed: {str(e)}")

    # Private helper methods for interaction analysis
    
    async def _analyze_interaction_patterns(self, 
                                          interaction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        try:
            df = pd.DataFrame(interaction_data)
            
            if df.empty:
                return {}
            
            # Time-based patterns
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            
            patterns = {
                'interaction_frequency': len(df),
                'active_hours': df.groupby('hour').size().nlargest(5).to_dict(),
                'active_days': df.groupby('day_of_week').size().nlargest(3).to_dict(),
                'interaction_types': df['interaction_type'].value_counts().to_dict(),
                'average_session_length': self._calculate_average_session_length(df),
                'interaction_intensity': self._calculate_interaction_intensity(df),
                'engagement_consistency': self._calculate_engagement_consistency(df)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze interaction patterns: {str(e)}")
            return {}

    def _calculate_average_session_length(self, df: pd.DataFrame) -> float:
        """Calculate average user session length"""
        try:
            df_sorted = df.sort_values(['user_id', 'timestamp'])
            session_lengths = []
            
            for user_id in df['user_id'].unique():
                user_data = df_sorted[df_sorted['user_id'] == user_id]
                if len(user_data) > 1:
                    time_diffs = pd.to_datetime(user_data['timestamp']).diff().dt.total_seconds()
                    session_breaks = time_diffs > 1800  # 30 minutes gap = session break
                    
                    if session_breaks.sum() > 0:
                        sessions = []
                        current_session = []
                        
                        for i, is_break in enumerate(session_breaks):
                            if is_break and current_session:
                                sessions.append(current_session)
                                current_session = [i]
                            else:
                                current_session.append(i)
                        
                        if current_session:
                            sessions.append(current_session)
                        
                        for session in sessions:
                            if len(session) > 1:
                                session_start = pd.to_datetime(user_data.iloc[session[0]]['timestamp'])
                                session_end = pd.to_datetime(user_data.iloc[session[-1]]['timestamp'])
                                session_length = (session_end - session_start).total_seconds()
                                session_lengths.append(session_length)
            
            return statistics.mean(session_lengths) if session_lengths else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate session length: {str(e)}")
            return 0.0

    def _calculate_interaction_intensity(self, df: pd.DataFrame) -> float:
        """Calculate interaction intensity score"""
        try:
            # Weight different interaction types
            interaction_weights = {
                'like': 1.0,
                'comment': 3.0,
                'share': 2.5,
                'save': 2.0,
                'follow': 5.0,
                'message': 4.0
            }
            
            total_weighted_score = 0
            total_interactions = len(df)
            
            for _, row in df.iterrows():
                interaction_type = row.get('interaction_type', 'like')
                weight = interaction_weights.get(interaction_type, 1.0)
                total_weighted_score += weight
            
            return total_weighted_score / total_interactions if total_interactions > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate interaction intensity: {str(e)}")
            return 0.0

    def _categorize_risk_level(self, churn_probability: float) -> str:
        """Categorize churn risk level"""
        if churn_probability >= 0.8:
            return "critical"
        elif churn_probability >= 0.6:
            return "high"
        elif churn_probability >= 0.4:
            return "medium"
        elif churn_probability >= 0.2:
            return "low"
        else:
            return "minimal"
