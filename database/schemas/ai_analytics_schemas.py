"""AI Analytics and Machine Learning Schemas

Comprehensive Pydantic schemas for AI analytics, machine learning models,
and intelligent insights in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import PositiveInt, PositiveFloat


class AnalyticsTypeEnum(str, Enum):
    """Types of analytics"""    CONTENT_PERFORMANCE = "content_performance"
    AUDIENCE_INSIGHTS = "audience_insights"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    REVENUE_ANALYTICS = "revenue_analytics"
    TREND_ANALYSIS = "trend_analysis"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    MARKET_INTELLIGENCE = "market_intelligence"
    USER_BEHAVIOR = "user_behavior"
    PLATFORM_PERFORMANCE = "platform_performance"
    COLLABORATION_METRICS = "collaboration_metrics"


class ModelTypeEnum(str, Enum):
    """Types of ML models"""    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NATURAL_LANGUAGE = "natural_language"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"


class ModelStatusEnum(str, Enum):
    """ML model status"""    TRAINING = "training"
    VALIDATION = "validation"
    TESTING = "testing"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    ARCHIVED = "archived"
    EXPERIMENTAL = "experimental"


class DataQualityEnum(str, Enum):
    """Data quality levels"""    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INSUFFICIENT = "insufficient"


class InsightTypeEnum(str, Enum):
    """Types of AI insights"""    OPTIMIZATION_SUGGESTION = "optimization_suggestion"
    TREND_PREDICTION = "trend_prediction"
    ANOMALY_ALERT = "anomaly_alert"
    RECOMMENDATION = "recommendation"
    RISK_ASSESSMENT = "risk_assessment"
    OPPORTUNITY_IDENTIFICATION = "opportunity_identification"
    PERFORMANCE_FORECAST = "performance_forecast"
    MARKET_SIGNAL = "market_signal"
    USER_BEHAVIOR_PATTERN = "user_behavior_pattern"
    CONTENT_STRATEGY = "content_strategy"


class MetricAggregationSchema(BaseModel):
    """Schema for metric aggregation"""    metric_name: str = Field(..., description="Name of the metric")
    aggregation_type: str = Field(..., description="Type of aggregation (sum, avg, max, min, count)")
    value: Union[int, float, Decimal] = Field(..., description="Aggregated value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    percentage_change: Optional[float] = Field(None, description="Percentage change from previous period")
    trend_direction: Optional[str] = Field(None, description="Trend direction (up, down, stable)")
    confidence_interval: Optional[Dict[str, float]] = Field(None, description="Confidence interval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "total_streams",
                "aggregation_type": "sum",
                "value": 125000,
                "unit": "streams",
                "percentage_change": 15.5,
                "trend_direction": "up"
            }
        }


class TimeSeriesDataSchema(BaseModel):
    """Schema for time series data points"""    timestamp: datetime = Field(..., description="Data point timestamp")
    value: Union[int, float, Decimal] = Field(..., description="Metric value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    anomaly_score: Optional[float] = Field(None, description="Anomaly detection score")
    prediction: Optional[Union[int, float, Decimal]] = Field(None, description="Predicted value")
    confidence: Optional[float] = Field(None, description="Prediction confidence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-08-24T12:00:00Z",
                "value": 1250,
                "anomaly_score": 0.05,
                "prediction": 1300,
                "confidence": 0.85
            }
        }


class AudienceSegmentSchema(BaseModel):
    """Schema for audience segmentation"""    segment_id: str = Field(..., description="Unique segment identifier")
    segment_name: str = Field(..., description="Segment name")
    segment_description: str = Field(..., description="Segment description")
    
    # Demographics
    age_range: Optional[Dict[str, int]] = Field(None, description="Age range distribution")
    gender_distribution: Optional[Dict[str, float]] = Field(None, description="Gender distribution")
    geographic_distribution: Optional[Dict[str, float]] = Field(None, description="Geographic distribution")
    language_distribution: Optional[Dict[str, float]] = Field(None, description="Language distribution")
    
    # Behavioral characteristics
    engagement_level: str = Field(..., description="Engagement level (high, medium, low)")
    listening_habits: Optional[Dict[str, Any]] = Field(None, description="Listening behavior patterns")
    platform_preferences: Optional[Dict[str, float]] = Field(None, description="Platform usage preferences")
    content_preferences: Optional[Dict[str, float]] = Field(None, description="Content type preferences")
    
    # Size and growth
    segment_size: int = Field(..., description="Number of users in segment")
    growth_rate: Optional[float] = Field(None, description="Segment growth rate")
    
    # Value metrics
    average_lifetime_value: Optional[Decimal] = Field(None, description="Average CLV")
    conversion_rate: Optional[float] = Field(None, description="Conversion rate")
    retention_rate: Optional[float] = Field(None, description="Retention rate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment_id": "SEG-001",
                "segment_name": "Electronic Music Enthusiasts",
                "engagement_level": "high",
                "segment_size": 15000,
                "growth_rate": 8.5,
                "average_lifetime_value": "45.00"
            }
        }


class MLModelPerformanceSchema(BaseModel):
    """Schema for ML model performance metrics"""    model_id: str = Field(..., description="Model identifier")
    evaluation_date: datetime = Field(..., description="Evaluation date")
    
    # Classification metrics
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Model accuracy")
    precision: Optional[float] = Field(None, ge=0, le=1, description="Model precision")
    recall: Optional[float] = Field(None, ge=0, le=1, description="Model recall")
    f1_score: Optional[float] = Field(None, ge=0, le=1, description="F1 score")
    auc_roc: Optional[float] = Field(None, ge=0, le=1, description="AUC-ROC score")
    
    # Regression metrics
    mse: Optional[float] = Field(None, description="Mean squared error")
    rmse: Optional[float] = Field(None, description="Root mean squared error")
    mae: Optional[float] = Field(None, description="Mean absolute error")
    r_squared: Optional[float] = Field(None, description="R-squared score")
    
    # General metrics
    training_time: Optional[float] = Field(None, description="Training time in seconds")
    inference_time: Optional[float] = Field(None, description="Average inference time in ms")
    model_size_mb: Optional[float] = Field(None, description="Model size in MB")
    data_quality_score: Optional[float] = Field(None, description="Training data quality score")
    
    # Business metrics
    prediction_accuracy: Optional[float] = Field(None, description="Real-world prediction accuracy")
    business_impact: Optional[Decimal] = Field(None, description="Measured business impact")
    user_satisfaction: Optional[float] = Field(None, description="User satisfaction with predictions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "recommendation_v2.1",
                "accuracy": 0.89,
                "precision": 0.91,
                "recall": 0.87,
                "f1_score": 0.89,
                "training_time": 3600.0,
                "inference_time": 15.5
            }
        }


class PredictiveInsightSchema(BaseModel):
    """Schema for predictive insights and forecasts"""    insight_id: str = Field(..., description="Unique insight identifier")
    insight_type: InsightTypeEnum = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    
    # Prediction details
    predicted_value: Union[int, float, Decimal, str] = Field(..., description="Predicted value")
    prediction_confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    time_horizon: str = Field(..., description="Time horizon for prediction")
    
    # Supporting data
    historical_data: Optional[List[TimeSeriesDataSchema]] = Field(None, description="Historical data points")
    contributing_factors: List[str] = Field(..., description="Factors contributing to prediction")
    risk_factors: Optional[List[str]] = Field(None, description="Risk factors")
    
    # Actionable recommendations
    recommended_actions: List[str] = Field(..., description="Recommended actions")
    potential_impact: Optional[str] = Field(None, description="Potential impact if actions taken")
    urgency_level: str = Field(..., description="Urgency level (low, medium, high, critical)")
    
    # Validation and tracking
    model_used: str = Field(..., description="ML model used for prediction")
    generated_at: datetime = Field(..., description="Insight generation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Insight expiration")
    validated: Optional[bool] = Field(None, description="Whether insight was validated")
    validation_score: Optional[float] = Field(None, description="Validation accuracy score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "insight_id": "INS-2024-001234",
                "insight_type": "trend_prediction",
                "title": "Rising Interest in Lo-Fi Hip Hop",
                "predicted_value": "25% increase",
                "prediction_confidence": 0.87,
                "time_horizon": "next_3_months",
                "urgency_level": "medium"
            }
        }


class ContentAnalyticsSchema(BaseModel):
    """Schema for content performance analytics"""    content_id: PositiveInt = Field(..., description="Content ID")
    analytics_period: str = Field(..., description="Analytics time period")
    
    # Engagement metrics
    total_views: int = Field(0, description="Total views")
    unique_views: int = Field(0, description="Unique views")
    total_streams: int = Field(0, description="Total streams")
    total_downloads: int = Field(0, description="Total downloads")
    likes: int = Field(0, description="Number of likes")
    shares: int = Field(0, description="Number of shares")
    comments: int = Field(0, description="Number of comments")
    saves: int = Field(0, description="Number of saves/bookmarks")
    
    # Engagement quality
    average_watch_time: Optional[float] = Field(None, description="Average watch time in seconds")
    completion_rate: Optional[float] = Field(None, description="Completion rate percentage")
    engagement_rate: float = Field(0.0, description="Overall engagement rate")
    virality_score: Optional[float] = Field(None, description="Virality score")
    
    # Audience insights
    audience_segments: List[AudienceSegmentSchema] = Field([], description="Audience segments")
    top_countries: Optional[Dict[str, int]] = Field(None, description="Top countries by views")
    age_demographics: Optional[Dict[str, float]] = Field(None, description="Age distribution")
    device_breakdown: Optional[Dict[str, float]] = Field(None, description="Device usage breakdown")
    
    # Performance trends
    performance_trend: List[TimeSeriesDataSchema] = Field([], description="Performance over time")
    growth_metrics: Optional[Dict[str, float]] = Field(None, description="Growth metrics")
    seasonal_patterns: Optional[Dict[str, Any]] = Field(None, description="Seasonal patterns")
    
    # Comparative analysis
    category_ranking: Optional[int] = Field(None, description="Ranking within category")
    percentile_score: Optional[float] = Field(None, description="Percentile score vs similar content")
    competitor_comparison: Optional[Dict[str, Any]] = Field(None, description="Competitor comparison")
    
    # Predictive insights
    predicted_performance: Optional[PredictiveInsightSchema] = Field(None, description="Performance predictions")
    optimization_suggestions: List[str] = Field([], description="Optimization suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": 12345,
                "analytics_period": "last_30_days",
                "total_views": 125000,
                "total_streams": 98000,
                "engagement_rate": 6.8,
                "completion_rate": 0.75,
                "category_ranking": 15,
                "percentile_score": 0.92
            }
        }


class MarketIntelligenceSchema(BaseModel):
    """Schema for market intelligence and industry insights"""    market_segment: str = Field(..., description="Market segment")
    analysis_date: datetime = Field(..., description="Analysis date")
    
    # Market size and growth
    market_size: Optional[Decimal] = Field(None, description="Market size estimate")
    growth_rate: Optional[float] = Field(None, description="Market growth rate")
    market_maturity: Optional[str] = Field(None, description="Market maturity level")
    
    # Trend analysis
    emerging_trends: List[str] = Field(..., description="Emerging trends")
    declining_trends: List[str] = Field(..., description="Declining trends")
    trend_momentum: Dict[str, float] = Field(..., description="Trend momentum scores")
    
    # Competitive landscape
    key_players: List[Dict[str, Any]] = Field(..., description="Key market players")
    market_concentration: Optional[float] = Field(None, description="Market concentration index")
    competitive_intensity: Optional[float] = Field(None, description="Competitive intensity score")
    
    # Consumer behavior
    consumer_preferences: Dict[str, float] = Field(..., description="Consumer preferences")
    spending_patterns: Optional[Dict[str, Any]] = Field(None, description="Spending patterns")
    adoption_rates: Optional[Dict[str, float]] = Field(None, description="Technology adoption rates")
    
    # Opportunities and threats
    growth_opportunities: List[str] = Field(..., description="Identified growth opportunities")
    market_threats: List[str] = Field(..., description="Market threats")
    regulatory_changes: Optional[List[str]] = Field(None, description="Regulatory changes")
    
    # Forecasts
    revenue_forecast: Optional[List[Dict]] = Field(None, description="Revenue forecasts")
    user_growth_forecast: Optional[List[Dict]] = Field(None, description="User growth forecasts")
    technology_predictions: Optional[List[str]] = Field(None, description="Technology predictions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "market_segment": "electronic_music_streaming",
                "growth_rate": 12.5,
                "emerging_trends": ["AI-generated music", "spatial audio", "live streaming"],
                "competitive_intensity": 0.78,
                "growth_opportunities": ["emerging markets", "podcast integration"]
            }
        }


class AIModelManagementSchema(BaseModel):
    """Schema for AI model management and deployment"""    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Model name")
    model_type: ModelTypeEnum = Field(..., description="Type of ML model")
    model_version: str = Field(..., description="Model version")
    
    # Model details
    description: str = Field(..., description="Model description")
    use_case: str = Field(..., description="Primary use case")
    target_metrics: List[str] = Field(..., description="Target performance metrics")
    
    # Training information
    training_dataset_size: Optional[int] = Field(None, description="Training dataset size")
    training_features: List[str] = Field(..., description="Training features")
    hyperparameters: Dict[str, Any] = Field(..., description="Model hyperparameters")
    training_duration: Optional[float] = Field(None, description="Training duration in hours")
    
    # Performance and status
    status: ModelStatusEnum = Field(..., description="Current model status")
    performance_metrics: MLModelPerformanceSchema = Field(..., description="Performance metrics")
    deployment_date: Optional[datetime] = Field(None, description="Deployment date")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    # Infrastructure
    compute_requirements: Dict[str, Any] = Field(..., description="Compute requirements")
    storage_requirements: Optional[Dict[str, Any]] = Field(None, description="Storage requirements")
    api_endpoint: Optional[str] = Field(None, description="Model API endpoint")
    
    # Monitoring and maintenance
    monitoring_enabled: bool = Field(True, description="Monitoring enabled")
    auto_retraining: bool = Field(False, description="Automatic retraining enabled")
    drift_detection: bool = Field(True, description="Data drift detection enabled")
    performance_threshold: Optional[float] = Field(None, description="Performance threshold for alerts")
    
    # Documentation and governance
    documentation_url: Optional[str] = Field(None, description="Model documentation URL")
    responsible_team: str = Field(..., description="Team responsible for model")
    compliance_requirements: Optional[List[str]] = Field(None, description="Compliance requirements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "recommendation_engine_v2.1",
                "model_name": "Content Recommendation Engine",
                "model_type": "recommendation",
                "model_version": "2.1.0",
                "status": "deployed",
                "use_case": "personalized_content_recommendations",
                "responsible_team": "ML_Engineering"
            }
        }


class RecommendationSchema(BaseModel):
    """Schema for AI-generated recommendations"""    recommendation_id: str = Field(..., description="Unique recommendation ID")
    user_id: PositiveInt = Field(..., description="Target user ID")
    recommendation_type: str = Field(..., description="Type of recommendation")
    
    # Recommendation content
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    recommended_items: List[Dict[str, Any]] = Field(..., description="Recommended items")
    
    # Scoring and ranking
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    ranking_position: int = Field(..., description="Position in recommendation list")
    
    # Context and reasoning
    reasoning: Optional[str] = Field(None, description="Reasoning behind recommendation")
    context_factors: List[str] = Field(..., description="Contextual factors considered")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences used")
    
    # Performance tracking
    generated_at: datetime = Field(..., description="Generation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Recommendation expiration")
    viewed: bool = Field(False, description="Whether recommendation was viewed")
    clicked: bool = Field(False, description="Whether recommendation was clicked")
    conversion: bool = Field(False, description="Whether recommendation led to conversion")
    
    # Feedback
    user_feedback: Optional[str] = Field(None, description="User feedback")
    feedback_score: Optional[int] = Field(None, ge=1, le=5, description="User rating")
    implicit_feedback: Optional[Dict[str, Any]] = Field(None, description="Implicit feedback signals")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation_id": "REC-2024-001234",
                "user_id": 123,
                "recommendation_type": "content_discovery",
                "title": "New Electronic Tracks You Might Like",
                "relevance_score": 0.89,
                "confidence_score": 0.84,
                "ranking_position": 1,
                "viewed": True,
                "clicked": False
            }
        }


# Export schemas
__all__ = [
    # Enums
    "AnalyticsTypeEnum",
    "ModelTypeEnum",
    "ModelStatusEnum",
    "DataQualityEnum",
    "InsightTypeEnum",
    
    # Complex schemas
    "MetricAggregationSchema",
    "TimeSeriesDataSchema",
    "AudienceSegmentSchema",
    "MLModelPerformanceSchema",
    "PredictiveInsightSchema",
    "ContentAnalyticsSchema",
    "MarketIntelligenceSchema",
    "AIModelManagementSchema",
    "RecommendationSchema"
]
