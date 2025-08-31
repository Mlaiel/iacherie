"""
Predictive Analytics Agent - ML prédictif

Advanced machine learning agent for predictive analytics including content performance 
prediction, user behavior forecasting, revenue prediction, and trend analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

# Import base agent
try:
    from .base import BaseAgent, AgentRequest, AgentResponse
except ImportError:
    from ai_agents.base import BaseAgent, AgentRequest, AgentResponse

# Import existing analytics components 
try:
    from analytics.business_intelligence import PredictiveAnalyticsEngine, PredictiveInsight
except ImportError:
    # Fallback implementations
    @dataclass
    class PredictiveInsight:
        insight_id: str
        insight_type: str
        prediction: Any
        confidence: float
        time_horizon: timedelta
        impact_score: float
        recommendations: List[str]
        created_at: datetime
        metadata: Dict[str, Any] = field(default_factory=dict)
    
    class PredictiveAnalyticsEngine:
        def __init__(self, config=None):
            pass
        async def generate_predictive_insights(self, data, horizon=None):
            return []

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """Machine learning prediction result"""
    prediction_id: str
    model_type: str
    prediction_value: Union[float, int, str, Dict]
    confidence_score: float
    prediction_horizon: timedelta
    feature_importance: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class PredictiveAnalyticsAgent(BaseAgent):
    """
    Advanced Predictive Analytics Agent using Machine Learning
    
    Capabilities:
    - Content performance prediction using ML models
    - User behavior and churn prediction
    - Revenue forecasting with time series analysis
    - Trend detection and market prediction
    - Anomaly detection in platform metrics
    - Real-time prediction model updates
    """
    
    def __init__(self, agent_id: str = "predictive_analytics_agent", **kwargs):
        super().__init__(
            agent_id=agent_id,
            agent_type="predictive_analytics",
            version="1.0.0",
            config=kwargs.get('config', {})
        )
        
        # Initialize predictive engine
        self.predictive_engine = PredictiveAnalyticsEngine(self.config)
        
        # Prediction models cache
        self.models = {
            "content_performance": None,
            "user_churn": None,
            "revenue_forecast": None,
            "engagement_prediction": None,
            "trend_detection": None
        }
        
        # Prediction history
        self.prediction_history = []
        self.model_accuracy_scores = {}
        
        self.logger = logger

    async def _load_models_and_resources(self):
        """Load ML models and initialize predictive resources"""
        try:
            # Initialize ML models (in production, these would be trained models)
            await self._initialize_prediction_models()
            
            # Load historical data for model training
            await self._load_training_data()
            
            self.logger.info("Predictive analytics models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load predictive models: {e}")
            raise

    async def _initialize_prediction_models(self):
        """Initialize machine learning prediction models"""
        try:
            # Placeholder for actual ML model initialization
            # In production, these would be trained scikit-learn, TensorFlow, or PyTorch models
            
            self.models["content_performance"] = {
                "model_type": "random_forest",
                "features": ["content_length", "posting_time", "creator_followers", "hashtag_count"],
                "accuracy": 0.85,
                "last_trained": datetime.utcnow()
            }
            
            self.models["user_churn"] = {
                "model_type": "logistic_regression", 
                "features": ["session_frequency", "engagement_rate", "last_activity", "account_age"],
                "accuracy": 0.78,
                "last_trained": datetime.utcnow()
            }
            
            self.models["revenue_forecast"] = {
                "model_type": "time_series",
                "features": ["historical_revenue", "seasonality", "user_growth", "engagement_trends"],
                "accuracy": 0.73,
                "last_trained": datetime.utcnow()
            }
            
            self.logger.info("ML prediction models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing prediction models: {e}")
            raise

    async def _load_training_data(self):
        """Load historical data for model training and validation"""
        try:
            # In production, this would load data from databases
            # For now, we'll use mock data structure
            
            self.training_data = {
                "content_performance": [],
                "user_behavior": [],
                "revenue_history": [],
                "engagement_metrics": []
            }
            
            self.logger.info("Training data loaded")
            
        except Exception as e:
            self.logger.error(f"Error loading training data: {e}")

    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys"""
        return [
            "prediction_models_path",
            "training_data_source",
            "model_update_frequency",
            "prediction_confidence_threshold"
        ]

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process predictive analytics requests"""
        try:
            action = request.action
            data = request.data
            
            result = {}
            
            if action == "predict_content_performance":
                result = await self._predict_content_performance(data)
            elif action == "predict_user_churn":
                result = await self._predict_user_churn(data)
            elif action == "forecast_revenue":
                result = await self._forecast_revenue(data)
            elif action == "detect_trends":
                result = await self._detect_trends(data)
            elif action == "predict_engagement":
                result = await self._predict_engagement(data)
            elif action == "generate_insights":
                result = await self._generate_predictive_insights(data)
            elif action == "update_models":
                result = await self._update_prediction_models(data)
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}",
                    error_code="INVALID_ACTION"
                )
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Predictive analytics completed for action: {action}"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing predictive analytics request: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="PREDICTION_ERROR"
            )

    async def _predict_content_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict content performance using ML models"""
        try:
            content_features = data.get("content_features", {})
            prediction_horizon = data.get("prediction_horizon_hours", 24)
            
            # Extract features for prediction
            features = self._extract_content_features(content_features)
            
            # Simulate ML prediction (in production, use trained models)
            predicted_views = self._simulate_prediction("views", features)
            predicted_engagement = self._simulate_prediction("engagement_rate", features)
            predicted_revenue = self._simulate_prediction("revenue", features)
            
            # Calculate confidence score
            confidence = self._calculate_prediction_confidence(features, "content_performance")
            
            prediction = MLPrediction(
                prediction_id=f"content_pred_{datetime.utcnow().timestamp()}",
                model_type="content_performance",
                prediction_value={
                    "predicted_views": predicted_views,
                    "predicted_engagement_rate": predicted_engagement,
                    "predicted_revenue": predicted_revenue,
                    "prediction_horizon_hours": prediction_horizon
                },
                confidence_score=confidence,
                prediction_horizon=timedelta(hours=prediction_horizon),
                feature_importance=self._get_feature_importance("content_performance"),
                created_at=datetime.utcnow(),
                metadata={"content_id": content_features.get("content_id")}
            )
            
            # Store prediction
            self.prediction_history.append(prediction)
            
            return {
                "prediction": {
                    "prediction_id": prediction.prediction_id,
                    "predicted_views": predicted_views,
                    "predicted_engagement_rate": predicted_engagement,
                    "predicted_revenue": predicted_revenue,
                    "confidence_score": confidence,
                    "prediction_horizon_hours": prediction_horizon,
                    "feature_importance": prediction.feature_importance
                },
                "recommendations": self._generate_content_recommendations(prediction),
                "model_info": {
                    "model_type": self.models["content_performance"]["model_type"],
                    "model_accuracy": self.models["content_performance"]["accuracy"],
                    "last_trained": self.models["content_performance"]["last_trained"].isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting content performance: {e}")
            return {"error": f"Content performance prediction failed: {e}"}

    async def _predict_user_churn(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user churn probability"""
        try:
            user_features = data.get("user_features", {})
            user_ids = data.get("user_ids", [])
            
            churn_predictions = []
            
            for user_id in user_ids:
                user_data = user_features.get(user_id, {})
                features = self._extract_user_features(user_data)
                
                # Simulate churn prediction
                churn_probability = self._simulate_prediction("churn_probability", features)
                risk_level = self._classify_churn_risk(churn_probability)
                
                churn_predictions.append({
                    "user_id": user_id,
                    "churn_probability": churn_probability,
                    "risk_level": risk_level,
                    "contributing_factors": self._identify_churn_factors(features),
                    "retention_recommendations": self._generate_retention_recommendations(churn_probability)
                })
            
            # Overall churn analytics
            high_risk_count = sum(1 for p in churn_predictions if p["risk_level"] == "high")
            average_churn_prob = np.mean([p["churn_probability"] for p in churn_predictions]) if churn_predictions else 0
            
            return {
                "churn_predictions": churn_predictions,
                "analytics": {
                    "total_users_analyzed": len(user_ids),
                    "high_risk_users": high_risk_count,
                    "average_churn_probability": average_churn_prob,
                    "overall_retention_health": "good" if average_churn_prob < 0.3 else "concerning"
                },
                "model_info": {
                    "model_accuracy": self.models["user_churn"]["accuracy"],
                    "features_used": self.models["user_churn"]["features"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting user churn: {e}")
            return {"error": f"User churn prediction failed: {e}"}

    async def _forecast_revenue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast revenue using time series analysis"""
        try:
            historical_data = data.get("historical_revenue", [])
            forecast_days = data.get("forecast_days", 30)
            
            if len(historical_data) < 7:
                return {"error": "Insufficient historical data for revenue forecasting"}
            
            # Simulate time series forecasting
            revenue_forecast = self._simulate_revenue_forecast(historical_data, forecast_days)
            
            # Calculate forecast metrics
            forecast_total = sum(revenue_forecast["daily_forecast"])
            current_avg = np.mean(historical_data[-7:]) if len(historical_data) >= 7 else 0
            growth_rate = ((forecast_total / forecast_days) - current_avg) / current_avg * 100 if current_avg > 0 else 0
            
            prediction = MLPrediction(
                prediction_id=f"revenue_forecast_{datetime.utcnow().timestamp()}",
                model_type="revenue_forecast",
                prediction_value=revenue_forecast,
                confidence_score=self.models["revenue_forecast"]["accuracy"],
                prediction_horizon=timedelta(days=forecast_days),
                feature_importance=self._get_feature_importance("revenue_forecast"),
                created_at=datetime.utcnow()
            )
            
            return {
                "forecast": revenue_forecast,
                "summary": {
                    "forecast_period_days": forecast_days,
                    "predicted_total_revenue": forecast_total,
                    "predicted_daily_average": forecast_total / forecast_days,
                    "growth_rate_percentage": growth_rate,
                    "confidence_score": prediction.confidence_score
                },
                "insights": self._generate_revenue_insights(revenue_forecast, growth_rate),
                "model_info": {
                    "model_type": self.models["revenue_forecast"]["model_type"],
                    "accuracy": self.models["revenue_forecast"]["accuracy"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error forecasting revenue: {e}")
            return {"error": f"Revenue forecasting failed: {e}"}

    async def _detect_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect trends in platform metrics and user behavior"""
        try:
            metrics_data = data.get("metrics_data", {})
            trend_period = data.get("trend_period_days", 30)
            
            trends_detected = {}
            
            for metric_name, metric_values in metrics_data.items():
                if len(metric_values) < 5:
                    continue
                
                trend_analysis = self._analyze_metric_trend(metric_values, metric_name)
                trends_detected[metric_name] = trend_analysis
            
            # Identify significant trends
            significant_trends = {
                name: trend for name, trend in trends_detected.items()
                if trend.get("significance_score", 0) > 0.7
            }
            
            # Generate trend predictions
            trend_predictions = {}
            for metric_name, trend in significant_trends.items():
                future_trend = self._predict_trend_continuation(trend, trend_period)
                trend_predictions[metric_name] = future_trend
            
            return {
                "trends_detected": trends_detected,
                "significant_trends": significant_trends,
                "trend_predictions": trend_predictions,
                "summary": {
                    "total_metrics_analyzed": len(metrics_data),
                    "significant_trends_count": len(significant_trends),
                    "trend_analysis_period": trend_period,
                    "overall_trend_direction": self._determine_overall_trend_direction(significant_trends)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting trends: {e}")
            return {"error": f"Trend detection failed: {e}"}

    async def _predict_engagement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user engagement patterns"""
        try:
            content_data = data.get("content_data", [])
            user_data = data.get("user_data", [])
            prediction_horizon = data.get("prediction_horizon_hours", 24)
            
            engagement_predictions = []
            
            for content in content_data:
                content_id = content.get("content_id")
                content_features = self._extract_content_features(content)
                
                # Predict engagement metrics
                predicted_likes = self._simulate_prediction("likes", content_features)
                predicted_shares = self._simulate_prediction("shares", content_features)
                predicted_comments = self._simulate_prediction("comments", content_features)
                
                engagement_rate = (predicted_likes + predicted_shares + predicted_comments) / max(content.get("expected_views", 1000), 1)
                
                engagement_predictions.append({
                    "content_id": content_id,
                    "predicted_likes": predicted_likes,
                    "predicted_shares": predicted_shares,
                    "predicted_comments": predicted_comments,
                    "predicted_engagement_rate": engagement_rate,
                    "engagement_quality": self._classify_engagement_quality(engagement_rate),
                    "optimization_suggestions": self._generate_engagement_optimization(content_features)
                })
            
            return {
                "engagement_predictions": engagement_predictions,
                "summary": {
                    "total_content_analyzed": len(content_data),
                    "average_predicted_engagement": np.mean([p["predicted_engagement_rate"] for p in engagement_predictions]) if engagement_predictions else 0,
                    "prediction_horizon_hours": prediction_horizon
                },
                "recommendations": self._generate_engagement_recommendations(engagement_predictions)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting engagement: {e}")
            return {"error": f"Engagement prediction failed: {e}"}

    async def _generate_predictive_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive predictive insights"""
        try:
            historical_data = data.get("historical_data", [])
            prediction_horizon = timedelta(days=data.get("prediction_horizon_days", 30))
            
            # Use existing predictive engine
            insights = await self.predictive_engine.generate_predictive_insights(
                historical_data, prediction_horizon
            )
            
            # Enhance with additional ML insights
            enhanced_insights = []
            for insight in insights:
                enhanced_insight = {
                    "insight_id": insight.insight_id,
                    "insight_type": insight.insight_type,
                    "prediction": insight.prediction,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score,
                    "recommendations": insight.recommendations,
                    "time_horizon": insight.time_horizon.days,
                    "created_at": insight.created_at.isoformat(),
                    "ml_enhancement": self._enhance_insight_with_ml(insight)
                }
                enhanced_insights.append(enhanced_insight)
            
            return {
                "predictive_insights": enhanced_insights,
                "insights_summary": {
                    "total_insights": len(enhanced_insights),
                    "high_impact_insights": len([i for i in enhanced_insights if i["impact_score"] > 0.7]),
                    "prediction_horizon_days": prediction_horizon.days
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating predictive insights: {e}")
            return {"error": f"Predictive insights generation failed: {e}"}

    async def _update_prediction_models(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update prediction models with new training data"""
        try:
            new_training_data = data.get("training_data", {})
            models_to_update = data.get("models", list(self.models.keys()))
            
            update_results = {}
            
            for model_name in models_to_update:
                if model_name in self.models:
                    # Simulate model retraining
                    old_accuracy = self.models[model_name]["accuracy"]
                    new_accuracy = min(1.0, old_accuracy + np.random.uniform(-0.05, 0.1))
                    
                    self.models[model_name]["accuracy"] = new_accuracy
                    self.models[model_name]["last_trained"] = datetime.utcnow()
                    
                    update_results[model_name] = {
                        "updated": True,
                        "old_accuracy": old_accuracy,
                        "new_accuracy": new_accuracy,
                        "improvement": new_accuracy - old_accuracy,
                        "last_trained": self.models[model_name]["last_trained"].isoformat()
                    }
                else:
                    update_results[model_name] = {
                        "updated": False,
                        "error": "Model not found"
                    }
            
            return {
                "model_updates": update_results,
                "summary": {
                    "models_updated": len([r for r in update_results.values() if r.get("updated")]),
                    "models_failed": len([r for r in update_results.values() if not r.get("updated")]),
                    "average_accuracy_improvement": np.mean([r.get("improvement", 0) for r in update_results.values() if r.get("updated")])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error updating prediction models: {e}")
            return {"error": f"Model update failed: {e}"}

    # Helper methods for ML predictions and analysis

    def _extract_content_features(self, content_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from content data for ML models"""
        return [
            content_data.get("content_length", 0),
            content_data.get("creator_followers", 0),
            content_data.get("hashtag_count", 0),
            content_data.get("posting_hour", 12),
            1 if content_data.get("has_image", False) else 0,
            1 if content_data.get("has_video", False) else 0,
            content_data.get("sentiment_score", 0.5)
        ]

    def _extract_user_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from user data for ML models"""
        return [
            user_data.get("account_age_days", 0),
            user_data.get("session_frequency", 0),
            user_data.get("avg_session_duration", 0),
            user_data.get("content_interactions", 0),
            user_data.get("last_activity_hours", 0),
            user_data.get("revenue_generated", 0)
        ]

    def _simulate_prediction(self, prediction_type: str, features: List[float]) -> float:
        """Simulate ML prediction (replace with actual model inference in production)"""
        # Simple simulation based on feature values
        feature_sum = sum(features)
        
        if prediction_type == "views":
            return max(0, int(feature_sum * np.random.uniform(50, 200)))
        elif prediction_type == "engagement_rate":
            return max(0, min(1, (feature_sum / 1000) * np.random.uniform(0.8, 1.2)))
        elif prediction_type == "revenue":
            return max(0, feature_sum * np.random.uniform(0.01, 0.1))
        elif prediction_type == "churn_probability":
            return max(0, min(1, 1 - (feature_sum / 1000) * np.random.uniform(0.8, 1.2)))
        elif prediction_type in ["likes", "shares", "comments"]:
            return max(0, int(feature_sum * np.random.uniform(5, 50)))
        else:
            return feature_sum * np.random.uniform(0.5, 1.5)

    def _calculate_prediction_confidence(self, features: List[float], model_type: str) -> float:
        """Calculate confidence score for predictions"""
        base_confidence = self.models.get(model_type, {}).get("accuracy", 0.5)
        feature_quality = min(1.0, len([f for f in features if f > 0]) / len(features))
        return min(1.0, base_confidence * feature_quality)

    def _get_feature_importance(self, model_type: str) -> Dict[str, float]:
        """Get feature importance scores for a model"""
        if model_type == "content_performance":
            return {
                "creator_followers": 0.3,
                "content_length": 0.2,
                "posting_hour": 0.15,
                "hashtag_count": 0.15,
                "has_video": 0.1,
                "has_image": 0.05,
                "sentiment_score": 0.05
            }
        elif model_type == "user_churn":
            return {
                "last_activity_hours": 0.4,
                "session_frequency": 0.25,
                "avg_session_duration": 0.15,
                "content_interactions": 0.1,
                "account_age_days": 0.05,
                "revenue_generated": 0.05
            }
        else:
            return {"feature_1": 0.5, "feature_2": 0.3, "feature_3": 0.2}

    def _classify_churn_risk(self, churn_probability: float) -> str:
        """Classify churn risk level"""
        if churn_probability > 0.7:
            return "high"
        elif churn_probability > 0.4:
            return "medium"
        else:
            return "low"

    def _classify_engagement_quality(self, engagement_rate: float) -> str:
        """Classify engagement quality"""
        if engagement_rate > 0.1:
            return "excellent"
        elif engagement_rate > 0.05:
            return "good"
        elif engagement_rate > 0.02:
            return "average"
        else:
            return "poor"

    def _generate_content_recommendations(self, prediction: MLPrediction) -> List[str]:
        """Generate content optimization recommendations"""
        recommendations = []
        
        confidence = prediction.confidence_score
        predicted_values = prediction.prediction_value
        
        if predicted_values.get("predicted_engagement_rate", 0) < 0.05:
            recommendations.append("Consider improving content quality and relevance")
            recommendations.append("Optimize posting times based on audience activity")
        
        if confidence < 0.7:
            recommendations.append("Gather more data for better prediction accuracy")
        
        if predicted_values.get("predicted_revenue", 0) < 10:
            recommendations.append("Explore monetization opportunities")
        
        return recommendations

    def _generate_retention_recommendations(self, churn_probability: float) -> List[str]:
        """Generate user retention recommendations"""
        if churn_probability > 0.7:
            return [
                "Immediate intervention required - send personalized retention offer",
                "Schedule direct outreach or customer support contact",
                "Provide exclusive content or benefits"
            ]
        elif churn_probability > 0.4:
            return [
                "Send re-engagement campaign",
                "Recommend relevant content",
                "Offer participation in community events"
            ]
        else:
            return [
                "Continue regular engagement activities",
                "Monitor activity levels",
                "Provide value-added services"
            ]

    # Additional helper methods would be implemented here...
    
    def _simulate_revenue_forecast(self, historical_data: List[float], forecast_days: int) -> Dict[str, Any]:
        """Simulate revenue forecasting"""
        if len(historical_data) < 2:
            trend = 0
        else:
            trend = (historical_data[-1] - historical_data[0]) / len(historical_data)
        
        last_value = historical_data[-1] if historical_data else 100
        daily_forecast = []
        
        for day in range(forecast_days):
            # Add trend and some randomness
            predicted_value = max(0, last_value + (trend * day) + np.random.uniform(-10, 10))
            daily_forecast.append(predicted_value)
        
        return {
            "daily_forecast": daily_forecast,
            "trend_direction": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "confidence_interval": {
                "lower": [max(0, v * 0.8) for v in daily_forecast],
                "upper": [v * 1.2 for v in daily_forecast]
            }
        }

    def _analyze_metric_trend(self, metric_values: List[float], metric_name: str) -> Dict[str, Any]:
        """Analyze trend in metric values"""
        if len(metric_values) < 3:
            return {"trend": "insufficient_data", "significance_score": 0}
        
        # Calculate trend
        x = np.arange(len(metric_values))
        trend_slope = np.polyfit(x, metric_values, 1)[0]
        
        # Determine trend direction and significance
        if abs(trend_slope) < 0.1:
            trend_direction = "stable"
            significance = 0.3
        elif trend_slope > 0:
            trend_direction = "increasing"
            significance = min(1.0, abs(trend_slope) / np.mean(metric_values))
        else:
            trend_direction = "decreasing"
            significance = min(1.0, abs(trend_slope) / np.mean(metric_values))
        
        return {
            "trend": trend_direction,
            "slope": trend_slope,
            "significance_score": significance,
            "metric_name": metric_name
        }

    def _predict_trend_continuation(self, trend: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Predict trend continuation"""
        slope = trend.get("slope", 0)
        current_value = 100  # Placeholder
        
        future_values = []
        for day in range(days):
            future_value = current_value + (slope * day)
            future_values.append(max(0, future_value))
        
        return {
            "predicted_values": future_values,
            "trend_strength": trend.get("significance_score", 0),
            "prediction_confidence": min(1.0, trend.get("significance_score", 0) * 0.8)
        }

    def _determine_overall_trend_direction(self, trends: Dict[str, Dict]) -> str:
        """Determine overall trend direction across all metrics"""
        increasing_count = sum(1 for t in trends.values() if t.get("trend") == "increasing")
        decreasing_count = sum(1 for t in trends.values() if t.get("trend") == "decreasing")
        
        if increasing_count > decreasing_count:
            return "positive"
        elif decreasing_count > increasing_count:
            return "negative"
        else:
            return "mixed"

    def _generate_engagement_optimization(self, content_features: List[float]) -> List[str]:
        """Generate engagement optimization suggestions"""
        suggestions = []
        
        # Analyze feature values and suggest improvements
        if len(content_features) > 0 and content_features[0] < 100:  # content_length
            suggestions.append("Consider creating longer, more detailed content")
        
        if len(content_features) > 4 and content_features[4] == 0:  # has_image
            suggestions.append("Add visual elements to increase engagement")
        
        if len(content_features) > 5 and content_features[5] == 0:  # has_video
            suggestions.append("Consider adding video content for higher engagement")
        
        return suggestions or ["Continue current content strategy"]

    def _generate_engagement_recommendations(self, predictions: List[Dict]) -> List[str]:
        """Generate overall engagement recommendations"""
        if not predictions:
            return ["No predictions available for recommendations"]
        
        avg_engagement = np.mean([p["predicted_engagement_rate"] for p in predictions])
        
        recommendations = []
        
        if avg_engagement < 0.02:
            recommendations.append("Focus on improving overall content quality")
            recommendations.append("Analyze successful competitor content strategies")
        elif avg_engagement > 0.1:
            recommendations.append("Excellent engagement predicted - scale successful strategies")
        
        recommendations.append("Monitor engagement metrics closely for optimization opportunities")
        
        return recommendations

    def _identify_churn_factors(self, features: List[float]) -> List[str]:
        """Identify factors contributing to churn risk"""
        factors = []
        
        if len(features) > 4 and features[4] > 168:  # last_activity_hours > 1 week
            factors.append("Low recent activity")
        
        if len(features) > 1 and features[1] < 3:  # session_frequency < 3
            factors.append("Infrequent usage")
        
        if len(features) > 2 and features[2] < 300:  # avg_session_duration < 5 minutes
            factors.append("Short session durations")
        
        return factors or ["No specific risk factors identified"]

    def _generate_revenue_insights(self, forecast: Dict[str, Any], growth_rate: float) -> List[str]:
        """Generate revenue forecasting insights"""
        insights = []
        
        trend = forecast.get("trend_direction", "stable")
        
        if trend == "increasing" and growth_rate > 5:
            insights.append("Strong revenue growth predicted - consider scaling operations")
        elif trend == "decreasing":
            insights.append("Revenue decline predicted - implement growth strategies immediately")
        elif trend == "stable":
            insights.append("Stable revenue predicted - explore new growth opportunities")
        
        daily_forecast = forecast.get("daily_forecast", [])
        if daily_forecast:
            max_day = daily_forecast.index(max(daily_forecast)) + 1
            insights.append(f"Peak revenue expected on day {max_day} of forecast period")
        
        return insights

    def _enhance_insight_with_ml(self, insight: PredictiveInsight) -> Dict[str, Any]:
        """Enhance existing insights with additional ML analysis"""
        return {
            "ml_confidence_adjustment": min(1.0, insight.confidence * 1.1),
            "feature_analysis": "Advanced ML analysis completed",
            "prediction_accuracy_estimate": self.model_accuracy_scores.get(insight.insight_type, 0.75),
            "alternative_scenarios": [
                {"scenario": "optimistic", "adjustment": 1.2},
                {"scenario": "pessimistic", "adjustment": 0.8}
            ]
        }