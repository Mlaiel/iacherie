"""Creator Performance Intelligence Predictor
=============================================

Enterprise-grade Creator Performance Intelligence system providing comprehensive
performance prediction, analytics, and optimization for the Ainflue Creator Economy.
Implements sophisticated ML-powered performance forecasting, creator success prediction,
and intelligent optimization recommendations for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

# Optional imports with fallbacks for enterprise deployment
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    # Fallback implementations for minimal deployment
    ML_AVAILABLE = False
    np = type('MockNumpy', (), {
        'array': lambda x: list(x) if hasattr(x, '__iter__') else [x],
        'mean': lambda x: sum(x) / len(x) if x else 0,
        'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0,
        'random': type('MockRandom', (), {'rand': lambda: __import__('random').random()})()
    })()

logger = logging.getLogger(__name__)

class PerformanceMetricType(Enum):
    """Creator performance metric types"""
    ENGAGEMENT_RATE = "engagement_rate"
    FOLLOWER_GROWTH = "follower_growth"
    CONTENT_QUALITY = "content_quality"
    REVENUE_GENERATION = "revenue_generation"
    COLLABORATION_SUCCESS = "collaboration_success"
    AUDIENCE_RETENTION = "audience_retention"
    VIRAL_POTENTIAL = "viral_potential"
    MONETIZATION_EFFICIENCY = "monetization_efficiency"
    CROSS_PLATFORM_REACH = "cross_platform_reach"
    BRAND_PARTNERSHIP_VALUE = "brand_partnership_value"

class PredictionTimeframe(Enum):
    """Prediction timeframe options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class CreatorCategory(Enum):
    """Creator category classification"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    EDUCATOR = "educator"
    GAMER = "gamer"
    LIFESTYLE = "lifestyle"
    TECH_REVIEWER = "tech_reviewer"
    FITNESS = "fitness"

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    creator_id: str
    platform: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorProfile:
    """Creator profile for performance analysis"""
    creator_id: str
    username: str
    category: CreatorCategory
    follower_count: int
    content_count: int
    engagement_history: List[float] = field(default_factory=list)
    revenue_history: List[float] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    tier: str = "bronze"
    join_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformancePrediction:
    """Performance prediction result"""
    creator_id: str
    metric_type: PerformanceMetricType
    predicted_value: float
    confidence_score: float
    timeframe: PredictionTimeframe
    prediction_date: datetime
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class PerformanceAlert:
    """Performance alert configuration"""
    alert_id: str
    creator_id: str
    metric_type: PerformanceMetricType
    threshold_type: str  # "above", "below", "change"
    threshold_value: float
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class CreatorPerformanceIntelligencePredictor:
    """Enterprise Creator Performance Intelligence Predictor
    
    Provides comprehensive performance prediction and analytics for Creator Economy.
    Implements ML-powered forecasting, intelligent optimization, and real-time monitoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Creator Performance Intelligence Predictor
        
        Args:
            config: Configuration dictionary for predictor settings
        """
        self.config = config or {}
        self.performance_data = defaultdict(list)
        self.creator_profiles = {}
        self.prediction_models = {}
        self.alerts = []
        self.performance_cache = {}
        self.prediction_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize ML models if available
        if ML_AVAILABLE:
            self._initialize_ml_models()
        
        # Performance thresholds for different creator tiers
        self.tier_thresholds = {
            "bronze": {"engagement_rate": 0.02, "follower_growth": 0.05},
            "silver": {"engagement_rate": 0.05, "follower_growth": 0.10},
            "gold": {"engagement_rate": 0.08, "follower_growth": 0.15},
            "platinum": {"engagement_rate": 0.12, "follower_growth": 0.20},
            "diamond": {"engagement_rate": 0.15, "follower_growth": 0.25}
        }
        
        logger.info("Creator Performance Intelligence Predictor initialized successfully")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for performance prediction"""
        if not ML_AVAILABLE:
            return
            
        self.prediction_models = {
            PerformanceMetricType.ENGAGEMENT_RATE: RandomForestRegressor(n_estimators=100, random_state=42),
            PerformanceMetricType.FOLLOWER_GROWTH: GradientBoostingRegressor(n_estimators=100, random_state=42),
            PerformanceMetricType.REVENUE_GENERATION: LinearRegression(),
            PerformanceMetricType.CONTENT_QUALITY: RandomForestRegressor(n_estimators=50, random_state=42),
            PerformanceMetricType.VIRAL_POTENTIAL: GradientBoostingRegressor(n_estimators=50, random_state=42)
        }
        
        self.scalers = {
            metric_type: StandardScaler() 
            for metric_type in self.prediction_models.keys()
        }
        
        logger.info("ML models initialized for performance prediction")
    
    async def register_creator(self, profile: CreatorProfile) -> bool:
        """Register a creator profile for performance monitoring
        
        Args:
            profile: Creator profile information
            
        Returns:
            Success status of registration
        """
        try:
            # Validate creator profile
            if not profile.creator_id or not profile.username:
                raise ValueError("Creator ID and username are required")
            
            # Store creator profile
            self.creator_profiles[profile.creator_id] = profile
            
            # Initialize performance data storage
            self.performance_data[profile.creator_id] = []
            
            # Set up default alerts for new creator
            await self._setup_default_alerts(profile.creator_id)
            
            logger.info(f"Creator {profile.username} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator: {str(e)}")
            return False
    
    async def record_performance_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric for analysis
        
        Args:
            metric: Performance metric to record
            
        Returns:
            Success status of recording
        """
        try:
            # Validate metric
            if metric.creator_id not in self.creator_profiles:
                logger.warning(f"Unknown creator ID: {metric.creator_id}")
                return False
            
            # Store metric
            self.performance_data[metric.creator_id].append(metric)
            
            # Update performance cache
            cache_key = f"{metric.creator_id}_{metric.metric_type.value}"
            if cache_key not in self.performance_cache:
                self.performance_cache[cache_key] = deque(maxlen=1000)
            self.performance_cache[cache_key].append(metric)
            
            # Check for alerts
            await self._check_performance_alerts(metric)
            
            # Update creator profile with latest metrics
            await self._update_creator_performance_history(metric)
            
            logger.debug(f"Performance metric recorded for creator {metric.creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {str(e)}")
            return False
    
    async def predict_performance(
        self, 
        creator_id: str, 
        metric_type: PerformanceMetricType,
        timeframe: PredictionTimeframe = PredictionTimeframe.WEEKLY
    ) -> Optional[PerformancePrediction]:
        """Predict future performance for a creator
        
        Args:
            creator_id: Creator identifier
            metric_type: Type of metric to predict
            timeframe: Prediction timeframe
            
        Returns:
            Performance prediction result
        """
        try:
            if creator_id not in self.creator_profiles:
                logger.error(f"Creator not found: {creator_id}")
                return None
            
            # Check prediction cache
            cache_key = f"{creator_id}_{metric_type.value}_{timeframe.value}"
            if cache_key in self.prediction_cache:
                cached_prediction = self.prediction_cache[cache_key]
                # Return cached prediction if less than 1 hour old
                if datetime.now() - cached_prediction.prediction_date < timedelta(hours=1):
                    return cached_prediction
            
            # Get historical data
            historical_data = self._get_historical_performance_data(creator_id, metric_type)
            
            if len(historical_data) < 10:
                # Use statistical prediction for limited data
                prediction = await self._statistical_prediction(creator_id, metric_type, timeframe)
            else:
                # Use ML prediction for sufficient data
                prediction = await self._ml_prediction(creator_id, metric_type, timeframe, historical_data)
            
            # Cache prediction
            if prediction:
                self.prediction_cache[cache_key] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting performance: {str(e)}")
            return None
    
    async def _statistical_prediction(
        self, 
        creator_id: str, 
        metric_type: PerformanceMetricType,
        timeframe: PredictionTimeframe
    ) -> Optional[PerformancePrediction]:
        """Statistical prediction for limited data scenarios"""
        try:
            historical_data = self._get_historical_performance_data(creator_id, metric_type)
            
            if not historical_data:
                # Use tier-based baseline prediction
                creator = self.creator_profiles[creator_id]
                baseline = self.tier_thresholds.get(creator.tier, {}).get(metric_type.value, 0.05)
                
                return PerformancePrediction(
                    creator_id=creator_id,
                    metric_type=metric_type,
                    predicted_value=baseline,
                    confidence_score=0.3,  # Low confidence for baseline
                    timeframe=timeframe,
                    prediction_date=datetime.now(),
                    contributing_factors=["tier_baseline", "limited_data"],
                    recommendations=[
                        "Increase content frequency to improve prediction accuracy",
                        "Engage more with audience to build performance history"
                    ]
                )
            
            # Calculate trend and predict
            values = [data.value for data in historical_data[-10:]]  # Last 10 data points
            mean_value = sum(values) / len(values)
            
            # Simple trend calculation
            if len(values) >= 2:
                trend = (values[-1] - values[0]) / len(values)
                predicted_value = mean_value + trend
            else:
                predicted_value = mean_value
            
            # Ensure positive prediction
            predicted_value = max(0, predicted_value)
            
            return PerformancePrediction(
                creator_id=creator_id,
                metric_type=metric_type,
                predicted_value=predicted_value,
                confidence_score=0.6,
                timeframe=timeframe,
                prediction_date=datetime.now(),
                contributing_factors=["statistical_trend", "historical_average"],
                recommendations=self._generate_recommendations(creator_id, metric_type, predicted_value)
            )
            
        except Exception as e:
            logger.error(f"Error in statistical prediction: {str(e)}")
            return None
    
    async def _ml_prediction(
        self, 
        creator_id: str, 
        metric_type: PerformanceMetricType,
        timeframe: PredictionTimeframe,
        historical_data: List[PerformanceMetric]
    ) -> Optional[PerformancePrediction]:
        """Machine learning-based prediction for sufficient data"""
        if not ML_AVAILABLE:
            return await self._statistical_prediction(creator_id, metric_type, timeframe)
        
        try:
            # Prepare feature matrix
            features, targets = self._prepare_ml_features(historical_data)
            
            if len(features) < 5:
                return await self._statistical_prediction(creator_id, metric_type, timeframe)
            
            # Get or train model
            model = self.prediction_models.get(metric_type)
            if model is None:
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                self.prediction_models[metric_type] = model
            
            # Train model
            scaler = self.scalers.get(metric_type, StandardScaler())
            features_scaled = scaler.fit_transform(features)
            model.fit(features_scaled, targets)
            
            # Make prediction
            latest_features = features[-1:] if features else [[0] * len(features[0])]
            latest_features_scaled = scaler.transform(latest_features)
            predicted_value = model.predict(latest_features_scaled)[0]
            
            # Calculate confidence score
            if len(features) > 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    features_scaled, targets, test_size=0.2, random_state=42
                )
                model.fit(X_train, y_train)
                test_predictions = model.predict(X_test)
                r2 = r2_score(y_test, test_predictions)
                confidence_score = max(0.1, min(0.95, r2))
            else:
                confidence_score = 0.7
            
            return PerformancePrediction(
                creator_id=creator_id,
                metric_type=metric_type,
                predicted_value=max(0, predicted_value),
                confidence_score=confidence_score,
                timeframe=timeframe,
                prediction_date=datetime.now(),
                contributing_factors=["ml_model", "historical_patterns", "feature_analysis"],
                recommendations=self._generate_recommendations(creator_id, metric_type, predicted_value),
                risk_factors=self._identify_risk_factors(creator_id, predicted_value)
            )
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return await self._statistical_prediction(creator_id, metric_type, timeframe)
    
    def _prepare_ml_features(self, historical_data: List[PerformanceMetric]) -> Tuple[List[List[float]], List[float]]:
        """Prepare feature matrix for ML training"""
        features = []
        targets = []
        
        for i in range(len(historical_data) - 1):
            current_metric = historical_data[i]
            next_metric = historical_data[i + 1]
            
            # Create feature vector
            feature_vector = [
                current_metric.value,
                i,  # Time index
                len(historical_data),  # History length
                # Add more features as needed
            ]
            
            features.append(feature_vector)
            targets.append(next_metric.value)
        
        return features, targets
    
    def _generate_recommendations(
        self, 
        creator_id: str, 
        metric_type: PerformanceMetricType, 
        predicted_value: float
    ) -> List[str]:
        """Generate optimization recommendations based on prediction"""
        recommendations = []
        creator = self.creator_profiles.get(creator_id)
        
        if not creator:
            return recommendations
        
        # Tier-based recommendations
        tier_threshold = self.tier_thresholds.get(creator.tier, {}).get(metric_type.value, 0)
        
        if predicted_value < tier_threshold:
            recommendations.extend([
                f"Increase {metric_type.value.replace('_', ' ')} to reach {creator.tier} tier standards",
                "Focus on audience engagement and content quality",
                "Consider collaborating with higher-tier creators"
            ])
        
        # Metric-specific recommendations
        if metric_type == PerformanceMetricType.ENGAGEMENT_RATE:
            recommendations.extend([
                "Post content during peak audience hours",
                "Increase interactive content (polls, Q&A, live streams)",
                "Respond promptly to comments and messages"
            ])
        elif metric_type == PerformanceMetricType.FOLLOWER_GROWTH:
            recommendations.extend([
                "Use trending hashtags and topics",
                "Cross-promote on multiple platforms",
                "Collaborate with creators in similar niches"
            ])
        elif metric_type == PerformanceMetricType.REVENUE_GENERATION:
            recommendations.extend([
                "Diversify monetization strategies",
                "Create premium content offerings",
                "Establish brand partnerships"
            ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _identify_risk_factors(self, creator_id: str, predicted_value: float) -> List[str]:
        """Identify potential risk factors for performance"""
        risk_factors = []
        creator = self.creator_profiles.get(creator_id)
        
        if not creator:
            return risk_factors
        
        # Check for declining performance
        recent_metrics = self._get_recent_performance_data(creator_id, days=7)
        if recent_metrics and len(recent_metrics) >= 2:
            recent_trend = recent_metrics[-1].value - recent_metrics[0].value
            if recent_trend < 0:
                risk_factors.append("Declining performance trend detected")
        
        # Check content frequency
        if creator.content_count < 10:
            risk_factors.append("Low content volume may impact growth")
        
        # Check platform diversity
        if len(creator.platforms) < 2:
            risk_factors.append("Limited platform presence increases risk")
        
        return risk_factors
    
    def _get_historical_performance_data(
        self, 
        creator_id: str, 
        metric_type: PerformanceMetricType,
        days: int = 30
    ) -> List[PerformanceMetric]:
        """Get historical performance data for a creator and metric type"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        all_metrics = self.performance_data.get(creator_id, [])
        filtered_metrics = [
            metric for metric in all_metrics
            if metric.metric_type == metric_type and metric.timestamp >= cutoff_date
        ]
        
        return sorted(filtered_metrics, key=lambda x: x.timestamp)
    
    def _get_recent_performance_data(
        self, 
        creator_id: str, 
        days: int = 7
    ) -> List[PerformanceMetric]:
        """Get recent performance data for trend analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        all_metrics = self.performance_data.get(creator_id, [])
        recent_metrics = [
            metric for metric in all_metrics
            if metric.timestamp >= cutoff_date
        ]
        
        return sorted(recent_metrics, key=lambda x: x.timestamp)
    
    async def _setup_default_alerts(self, creator_id: str):
        """Set up default performance alerts for a new creator"""
        creator = self.creator_profiles.get(creator_id)
        if not creator:
            return
        
        # Default alerts based on tier
        tier_thresholds = self.tier_thresholds.get(creator.tier, {})
        
        for metric_name, threshold in tier_thresholds.items():
            alert = PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                creator_id=creator_id,
                metric_type=PerformanceMetricType(metric_name),
                threshold_type="below",
                threshold_value=threshold * 0.8  # Alert at 80% of tier threshold
            )
            self.alerts.append(alert)
    
    async def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check if a metric triggers any performance alerts"""
        creator_alerts = [
            alert for alert in self.alerts
            if alert.creator_id == metric.creator_id 
            and alert.metric_type == metric.metric_type
            and alert.is_active
        ]
        
        for alert in creator_alerts:
            should_trigger = False
            
            if alert.threshold_type == "below" and metric.value < alert.threshold_value:
                should_trigger = True
            elif alert.threshold_type == "above" and metric.value > alert.threshold_value:
                should_trigger = True
            
            if should_trigger:
                await self._trigger_performance_alert(alert, metric)
    
    async def _trigger_performance_alert(self, alert: PerformanceAlert, metric: PerformanceMetric):
        """Trigger a performance alert"""
        creator = self.creator_profiles.get(alert.creator_id)
        creator_name = creator.username if creator else "Unknown"
        
        logger.warning(
            f"Performance alert triggered for {creator_name}: "
            f"{alert.metric_type.value} is {metric.value:.3f} "
            f"({alert.threshold_type} threshold: {alert.threshold_value:.3f})"
        )
        
        # Here you would implement actual alerting (email, webhook, etc.)
    
    async def _update_creator_performance_history(self, metric: PerformanceMetric):
        """Update creator profile with latest performance metrics"""
        creator = self.creator_profiles.get(metric.creator_id)
        if not creator:
            return
        
        # Update engagement history
        if metric.metric_type == PerformanceMetricType.ENGAGEMENT_RATE:
            creator.engagement_history.append(metric.value)
            # Keep only last 100 values
            creator.engagement_history = creator.engagement_history[-100:]
        
        # Update revenue history
        elif metric.metric_type == PerformanceMetricType.REVENUE_GENERATION:
            creator.revenue_history.append(metric.value)
            creator.revenue_history = creator.revenue_history[-100:]
    
    async def get_creator_performance_summary(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive performance summary for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Performance summary dictionary
        """
        try:
            creator = self.creator_profiles.get(creator_id)
            if not creator:
                return None
            
            # Get recent metrics
            recent_metrics = self._get_recent_performance_data(creator_id, days=30)
            
            # Calculate summary statistics
            summary = {
                "creator_id": creator_id,
                "username": creator.username,
                "category": creator.category.value,
                "tier": creator.tier,
                "follower_count": creator.follower_count,
                "platforms": creator.platforms,
                "metrics_summary": {},
                "performance_trends": {},
                "predictions": {},
                "recommendations": []
            }
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_type[metric.metric_type].append(metric.value)
            
            # Calculate statistics for each metric type
            for metric_type, values in metrics_by_type.items():
                if values:
                    summary["metrics_summary"][metric_type.value] = {
                        "current": values[-1],
                        "average": sum(values) / len(values),
                        "trend": "increasing" if len(values) >= 2 and values[-1] > values[0] else "stable",
                        "data_points": len(values)
                    }
                    
                    # Get prediction for this metric
                    prediction = await self.predict_performance(creator_id, metric_type)
                    if prediction:
                        summary["predictions"][metric_type.value] = {
                            "predicted_value": prediction.predicted_value,
                            "confidence": prediction.confidence_score,
                            "timeframe": prediction.timeframe.value
                        }
            
            # Generate overall recommendations
            summary["recommendations"] = await self._generate_overall_recommendations(creator_id)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {str(e)}")
            return None
    
    async def _generate_overall_recommendations(self, creator_id: str) -> List[str]:
        """Generate overall recommendations for creator performance improvement"""
        recommendations = []
        creator = self.creator_profiles.get(creator_id)
        
        if not creator:
            return recommendations
        
        # Analyze performance across all metrics
        recent_metrics = self._get_recent_performance_data(creator_id, days=30)
        
        if not recent_metrics:
            recommendations.append("Start creating content regularly to build performance history")
            return recommendations
        
        # Tier advancement recommendations
        current_tier_index = ["bronze", "silver", "gold", "platinum", "diamond"].index(creator.tier)
        if current_tier_index < 4:  # Not at highest tier
            next_tier = ["bronze", "silver", "gold", "platinum", "diamond"][current_tier_index + 1]
            recommendations.append(f"Focus on reaching {next_tier} tier requirements")
        
        # Platform diversification
        if len(creator.platforms) < 3:
            recommendations.append("Expand to additional platforms to increase reach")
        
        # Content frequency
        daily_content_rate = len(recent_metrics) / 30
        if daily_content_rate < 0.5:
            recommendations.append("Increase content creation frequency")
        
        # Engagement optimization
        engagement_metrics = [
            m for m in recent_metrics 
            if m.metric_type == PerformanceMetricType.ENGAGEMENT_RATE
        ]
        if engagement_metrics:
            avg_engagement = sum(m.value for m in engagement_metrics) / len(engagement_metrics)
            if avg_engagement < 0.05:
                recommendations.append("Focus on creating more engaging content")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            return {
                "total_creators": len(self.creator_profiles),
                "total_metrics": sum(len(metrics) for metrics in self.performance_data.values()),
                "active_alerts": len([a for a in self.alerts if a.is_active]),
                "cache_size": len(self.performance_cache),
                "prediction_cache_size": len(self.prediction_cache),
                "ml_available": ML_AVAILABLE,
                "models_initialized": len(self.prediction_models),
                "system_uptime": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'CreatorPerformanceIntelligencePredictor',
    'PerformanceMetricType',
    'PredictionTimeframe',
    'CreatorCategory',
    'PerformanceMetric',
    'CreatorProfile',
    'PerformancePrediction',
    'PerformanceAlert'
]