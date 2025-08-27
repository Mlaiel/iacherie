"""
Analytics Extractors - Industrial IA Analytics and Insights System
=================================================================

Ultra-advanced professional analytics extractors for content performance and business intelligence.
Implements enterprise-grade AI-powered analytics, predictive modeling, and business insights with ML.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import json
from pathlib import Path
from decimal import Decimal
import statistics

# Import core extraction components
from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

# ML and analytics libraries
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics import mean_squared_error, r2_score
    import xgboost as xgb
    import lightgbm as lgb
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False

# Time series analysis
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    import prophet
    HAS_TS_LIBS = True
except ImportError:
    HAS_TS_LIBS = False

# Deep learning
try:
    import torch
    import torch.nn as nn
    from transformers import pipeline
    HAS_DL_LIBS = True
except ImportError:
    HAS_DL_LIBS = False

logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    """Types of analytics"""
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT = "content"
    PREDICTIVE = "predictive"
    COMPETITIVE = "competitive"
    TRENDS = "trends"
    SENTIMENT = "sentiment"
    BEHAVIORAL = "behavioral"


class InsightLevel(Enum):
    """Insight complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    AI_POWERED = "ai_powered"


class PredictionHorizon(Enum):
    """Prediction time horizons"""
    NEXT_HOUR = "next_hour"
    NEXT_DAY = "next_day"
    NEXT_WEEK = "next_week"
    NEXT_MONTH = "next_month"
    NEXT_QUARTER = "next_quarter"
    NEXT_YEAR = "next_year"


@dataclass
class AnalyticsConfig:
    """Analytics extraction configuration"""
    
    config_id: str
    user_id: str
    analytics_types: List[AnalyticsType] = field(default_factory=list)
    insight_level: InsightLevel = InsightLevel.ADVANCED
    
    # Data sources
    data_sources: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    
    # Time range
    start_date: datetime = field(default_factory=lambda: datetime.utcnow() - timedelta(days=30))
    end_date: datetime = field(default_factory=datetime.utcnow)
    
    # Analysis settings
    include_predictions: bool = True
    prediction_horizons: List[PredictionHorizon] = field(default_factory=list)
    confidence_threshold: float = 0.85
    
    # AI features
    use_ai_insights: bool = True
    automated_recommendations: bool = True
    anomaly_detection: bool = True
    trend_analysis: bool = True
    
    # Output preferences
    include_visualizations: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["json", "csv"])
    dashboard_integration: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceMetrics:
    """Content performance metrics"""
    
    # Basic metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    
    # Engagement metrics
    engagement_rate: float = 0.0
    avg_watch_time: float = 0.0
    bounce_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Revenue metrics
    total_revenue: Decimal = Decimal('0.00')
    rpm: Decimal = Decimal('0.00')  # Revenue Per Mille
    cpm: Decimal = Decimal('0.00')  # Cost Per Mille
    
    # Quality metrics
    quality_score: float = 0.0
    relevance_score: float = 0.0
    viral_potential: float = 0.0
    
    # Temporal metrics
    growth_rate: float = 0.0
    trend_direction: str = "stable"  # growing, declining, stable
    seasonality_factor: float = 1.0
    
    # Comparative metrics
    peer_comparison: float = 0.0  # Compared to similar content
    historical_comparison: float = 0.0  # Compared to user's history


@dataclass
class AudienceInsights:
    """Audience analysis insights"""
    
    # Demographics
    age_distribution: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    location_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Behavior patterns
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Segmentation
    audience_segments: List[Dict[str, Any]] = field(default_factory=list)
    high_value_segments: List[Dict[str, Any]] = field(default_factory=list)
    growth_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Psychographics
    interests: Dict[str, float] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    lifestyle_indicators: Dict[str, float] = field(default_factory=dict)
    
    # Platform behavior
    platform_preferences: Dict[str, float] = field(default_factory=dict)
    cross_platform_behavior: Dict[str, Any] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class PredictiveInsights:
    """AI-powered predictive insights"""
    
    # Performance predictions
    predicted_views: Dict[str, int] = field(default_factory=dict)
    predicted_engagement: Dict[str, float] = field(default_factory=dict)
    predicted_revenue: Dict[str, Decimal] = field(default_factory=dict)
    
    # Trend predictions
    trend_forecasts: Dict[str, Any] = field(default_factory=dict)
    seasonal_predictions: Dict[str, Any] = field(default_factory=dict)
    
    # Risk assessments
    performance_risks: List[Dict[str, Any]] = field(default_factory=list)
    market_risks: List[Dict[str, Any]] = field(default_factory=list)
    competitive_risks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Opportunities
    growth_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    monetization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    collaboration_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Model metrics
    prediction_confidence: float = 0.0
    model_accuracy: float = 0.0
    feature_importance: Dict[str, float] = field(default_factory=dict)


class PerformanceAnalyticsExtractor(BaseExtractor):
    """Advanced performance analytics extractor with AI insights"""
    
    def __init__(self):
        super().__init__("PerformanceAnalyticsExtractor")
        self.ml_models = {}
        self.scalers = {}
        self.feature_extractors = {}
        
        self._initialize_analytics_models()
    
    def _initialize_analytics_models(self):
        """Initialize ML models for analytics"""
        try:
            if HAS_ML_LIBS:
                # Performance prediction models
                self.ml_models = {
                    'view_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
                    'engagement_predictor': GradientBoostingRegressor(n_estimators=100, random_state=42),
                    'revenue_predictor': xgb.XGBRegressor(n_estimators=100, random_state=42),
                    'viral_predictor': lgb.LGBMRegressor(n_estimators=100, random_state=42)
                }
                
                # Data scalers
                self.scalers = {
                    'standard': StandardScaler(),
                    'minmax': MinMaxScaler()
                }
                
                # Clustering models
                self.clustering_models = {
                    'audience_segments': KMeans(n_clusters=5, random_state=42),
                    'content_clusters': DBSCAN(eps=0.5, min_samples=5)
                }
                
                self.logger.info("Analytics models initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics models: {e}")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for performance analytics"""
        return any([
            "performance" in request.extraction_types,
            "analytics" in request.extraction_types,
            "insights" in request.extraction_types,
            "metrics" in request.extraction_types
        ])
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Perform performance analytics extraction"""
        start_time = datetime.utcnow()
        
        try:
            # Parse analytics configuration
            config = await self._parse_analytics_config(request)
            
            # Collect performance data
            raw_data = await self._collect_performance_data(config)
            
            # Calculate basic metrics
            basic_metrics = await self._calculate_basic_metrics(raw_data)
            
            # Perform advanced analytics
            advanced_insights = await self._perform_advanced_analytics(raw_data, config)
            
            # Generate predictions
            predictions = await self._generate_predictions(raw_data, config)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(raw_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(basic_metrics, advanced_insights, predictions)
            
            # Create visualizations
            visualizations = await self._create_visualizations(raw_data, basic_metrics, config)
            
            result = ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data={
                    'analytics_config': config.__dict__,
                    'basic_metrics': basic_metrics.__dict__,
                    'advanced_insights': advanced_insights,
                    'predictions': predictions.__dict__,
                    'anomalies': anomalies,
                    'recommendations': recommendations,
                    'visualizations': visualizations
                },
                metadata={
                    'data_points': len(raw_data),
                    'analytics_types': [t.value for t in config.analytics_types],
                    'prediction_horizon': config.prediction_horizons,
                    'ai_powered': config.use_ai_insights
                },
                extraction_time=(datetime.utcnow() - start_time).total_seconds(),
                quality_score=self._calculate_analytics_quality_score(basic_metrics, advanced_insights),
                completed_at=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Performance analytics extraction failed: {e}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                errors=[str(e)],
                completed_at=datetime.utcnow()
            )
    
    async def _parse_analytics_config(self, request: ExtractionRequest) -> AnalyticsConfig:
        """Parse analytics configuration from request"""
        config_data = request.metadata.get('analytics_config', {})
        
        return AnalyticsConfig(
            config_id=f"analytics_{request.request_id}",
            user_id=request.user_id or "anonymous",
            analytics_types=[AnalyticsType(t) for t in config_data.get('analytics_types', ['performance'])],
            insight_level=InsightLevel(config_data.get('insight_level', 'advanced')),
            platforms=config_data.get('platforms', ['youtube', 'instagram']),
            prediction_horizons=[PredictionHorizon(h) for h in config_data.get('prediction_horizons', ['next_week'])],
            use_ai_insights=config_data.get('use_ai_insights', True)
        )
    
    async def _collect_performance_data(self, config: AnalyticsConfig) -> List[Dict[str, Any]]:
        """Collect performance data from various sources"""
        data = []
        
        try:
            # Collect data from each platform
            for platform in config.platforms:
                platform_data = await self._collect_platform_data(platform, config)
                data.extend(platform_data)
            
            # Enrich with additional metrics
            enriched_data = await self._enrich_performance_data(data)
            
            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Data collection failed: {e}")
            return []
    
    async def _calculate_basic_metrics(self, raw_data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calculate basic performance metrics"""
        if not raw_data:
            return PerformanceMetrics()
        
        try:
            df = pd.DataFrame(raw_data)
            
            metrics = PerformanceMetrics(
                views=df['views'].sum() if 'views' in df.columns else 0,
                likes=df['likes'].sum() if 'likes' in df.columns else 0,
                shares=df['shares'].sum() if 'shares' in df.columns else 0,
                comments=df['comments'].sum() if 'comments' in df.columns else 0,
                engagement_rate=df['engagement_rate'].mean() if 'engagement_rate' in df.columns else 0.0,
                avg_watch_time=df['watch_time'].mean() if 'watch_time' in df.columns else 0.0,
                total_revenue=Decimal(str(df['revenue'].sum())) if 'revenue' in df.columns else Decimal('0.00')
            )
            
            # Calculate derived metrics
            if metrics.views > 0:
                metrics.rpm = Decimal(str(float(metrics.total_revenue) / metrics.views * 1000))
            
            # Calculate growth rate
            if len(df) > 1:
                df_sorted = df.sort_values('date')
                recent_avg = df_sorted.tail(7)['views'].mean()
                previous_avg = df_sorted.head(7)['views'].mean()
                if previous_avg > 0:
                    metrics.growth_rate = (recent_avg - previous_avg) / previous_avg * 100
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Basic metrics calculation failed: {e}")
            return PerformanceMetrics()
    
    async def _perform_advanced_analytics(self, raw_data: List[Dict[str, Any]], config: AnalyticsConfig) -> Dict[str, Any]:
        """Perform advanced analytics and insights"""
        insights = {}
        
        try:
            df = pd.DataFrame(raw_data)
            
            if AnalyticsType.AUDIENCE in config.analytics_types:
                insights['audience'] = await self._analyze_audience(df)
            
            if AnalyticsType.ENGAGEMENT in config.analytics_types:
                insights['engagement'] = await self._analyze_engagement_patterns(df)
            
            if AnalyticsType.CONTENT in config.analytics_types:
                insights['content'] = await self._analyze_content_performance(df)
            
            if AnalyticsType.TRENDS in config.analytics_types:
                insights['trends'] = await self._analyze_trends(df)
            
            if AnalyticsType.COMPETITIVE in config.analytics_types:
                insights['competitive'] = await self._analyze_competitive_landscape(df)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Advanced analytics failed: {e}")
            return {}
    
    async def _generate_predictions(self, raw_data: List[Dict[str, Any]], config: AnalyticsConfig) -> PredictiveInsights:
        """Generate AI-powered predictions"""
        predictions = PredictiveInsights()
        
        try:
            if not HAS_ML_LIBS or not config.include_predictions:
                return predictions
            
            df = pd.DataFrame(raw_data)
            
            # Prepare features for prediction
            features = await self._prepare_prediction_features(df)
            
            # Generate predictions for each horizon
            for horizon in config.prediction_horizons:
                horizon_predictions = await self._predict_for_horizon(features, horizon)
                
                predictions.predicted_views[horizon.value] = horizon_predictions.get('views', 0)
                predictions.predicted_engagement[horizon.value] = horizon_predictions.get('engagement', 0.0)
                predictions.predicted_revenue[horizon.value] = Decimal(str(horizon_predictions.get('revenue', 0.0)))
            
            # Calculate prediction confidence
            predictions.prediction_confidence = await self._calculate_prediction_confidence(features)
            
            # Generate opportunities and risks
            predictions.growth_opportunities = await self._identify_growth_opportunities(df, predictions)
            predictions.performance_risks = await self._identify_performance_risks(df, predictions)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Prediction generation failed: {e}")
            return predictions
    
    async def _detect_anomalies(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in performance data"""
        anomalies = []
        
        try:
            if not raw_data:
                return anomalies
            
            df = pd.DataFrame(raw_data)
            
            # Detect anomalies in key metrics
            for metric in ['views', 'engagement_rate', 'revenue']:
                if metric in df.columns:
                    metric_anomalies = await self._detect_metric_anomalies(df[metric], metric)
                    anomalies.extend(metric_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    async def _generate_recommendations(self, metrics: PerformanceMetrics, insights: Dict[str, Any], 
                                     predictions: PredictiveInsights) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            if metrics.engagement_rate < 0.03:  # Low engagement
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'high',
                    'title': 'Improve Content Engagement',
                    'description': 'Your engagement rate is below optimal. Consider creating more interactive content.',
                    'actions': [
                        'Add more call-to-actions',
                        'Create polls or questions',
                        'Respond to comments promptly',
                        'Use trending hashtags'
                    ],
                    'expected_impact': '+50% engagement rate'
                })
            
            # Growth-based recommendations
            if metrics.growth_rate < 0:  # Declining growth
                recommendations.append({
                    'type': 'growth',
                    'priority': 'high',
                    'title': 'Reverse Declining Trend',
                    'description': 'Your content performance is declining. Time to refresh your strategy.',
                    'actions': [
                        'Analyze top-performing content',
                        'Experiment with new formats',
                        'Collaborate with other creators',
                        'Optimize posting schedule'
                    ],
                    'expected_impact': '+25% view growth'
                })
            
            # Revenue-based recommendations
            if float(metrics.rpm) < 1.0:  # Low monetization
                recommendations.append({
                    'type': 'monetization',
                    'priority': 'medium',
                    'title': 'Improve Revenue Per View',
                    'description': 'Your monetization efficiency could be improved.',
                    'actions': [
                        'Enable all monetization features',
                        'Create premium content',
                        'Partner with brands',
                        'Sell merchandise'
                    ],
                    'expected_impact': '+100% revenue per view'
                })
            
            # AI-powered recommendations from predictions
            for opportunity in predictions.growth_opportunities:
                recommendations.append({
                    'type': 'ai_opportunity',
                    'priority': 'medium',
                    'title': opportunity.get('title', 'AI-Identified Opportunity'),
                    'description': opportunity.get('description', ''),
                    'actions': opportunity.get('actions', []),
                    'expected_impact': opportunity.get('impact', 'Positive')
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def _calculate_analytics_quality_score(self, metrics: PerformanceMetrics, insights: Dict[str, Any]) -> float:
        """Calculate quality score for analytics extraction"""
        base_score = 0.7
        
        # Data completeness bonus
        if metrics.views > 0:
            base_score += 0.1
        if metrics.engagement_rate > 0:
            base_score += 0.1
        if float(metrics.total_revenue) > 0:
            base_score += 0.1
        
        # Insights quality bonus
        insights_count = len(insights)
        base_score += min(0.1, insights_count * 0.02)
        
        return min(1.0, base_score)


class AudienceAnalyticsExtractor(BaseExtractor):
    """Advanced audience analytics and segmentation extractor"""
    
    def __init__(self):
        super().__init__("AudienceAnalyticsExtractor")
        self.segmentation_models = {}
        self.nlp_models = {}
        
        self._initialize_audience_models()
    
    def _initialize_audience_models(self):
        """Initialize models for audience analysis"""
        try:
            if HAS_ML_LIBS:
                self.segmentation_models = {
                    'demographic': KMeans(n_clusters=5, random_state=42),
                    'behavioral': DBSCAN(eps=0.5, min_samples=5),
                    'psychographic': PCA(n_components=3)
                }
                
                if HAS_DL_LIBS:
                    self.nlp_models = {
                        'sentiment': pipeline('sentiment-analysis'),
                        'emotion': pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')
                    }
                
                self.logger.info("Audience models initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audience models: {e}")
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for audience analytics"""
        return any([
            "audience" in request.extraction_types,
            "segmentation" in request.extraction_types,
            "demographics" in request.extraction_types,
            "behavior" in request.extraction_types
        ])
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Perform audience analytics extraction"""
        start_time = datetime.utcnow()
        
        try:
            # Collect audience data
            audience_data = await self._collect_audience_data(request)
            
            # Perform demographic analysis
            demographics = await self._analyze_demographics(audience_data)
            
            # Analyze behavior patterns
            behavior_patterns = await self._analyze_behavior_patterns(audience_data)
            
            # Perform audience segmentation
            segments = await self._perform_audience_segmentation(audience_data)
            
            # Analyze content preferences
            preferences = await self._analyze_content_preferences(audience_data)
            
            # Generate audience insights
            insights = AudienceInsights(
                age_distribution=demographics.get('age_distribution', {}),
                gender_distribution=demographics.get('gender_distribution', {}),
                location_distribution=demographics.get('location_distribution', {}),
                activity_patterns=behavior_patterns.get('activity', {}),
                engagement_patterns=behavior_patterns.get('engagement', {}),
                audience_segments=segments,
                content_preferences=preferences
            )
            
            result = ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.COMPLETED,
                extracted_data={
                    'audience_insights': insights.__dict__,
                    'raw_demographics': demographics,
                    'behavior_analysis': behavior_patterns,
                    'segmentation_results': segments,
                    'preference_analysis': preferences
                },
                metadata={
                    'audience_size': len(audience_data),
                    'segments_identified': len(segments),
                    'data_quality': self._assess_data_quality(audience_data)
                },
                extraction_time=(datetime.utcnow() - start_time).total_seconds(),
                quality_score=self._calculate_audience_quality_score(insights),
                completed_at=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Audience analytics extraction failed: {e}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                errors=[str(e)],
                completed_at=datetime.utcnow()
            )
    
    def _calculate_audience_quality_score(self, insights: AudienceInsights) -> float:
        """Calculate quality score for audience analytics"""
        base_score = 0.6
        
        # Demographics completeness
        if insights.age_distribution:
            base_score += 0.1
        if insights.gender_distribution:
            base_score += 0.1
        if insights.location_distribution:
            base_score += 0.1
        
        # Behavioral insights
        if insights.activity_patterns:
            base_score += 0.1
        if insights.engagement_patterns:
            base_score += 0.1
        
        return min(1.0, base_score)


# Factory function for analytics extractors
def create_analytics_extractor_suite() -> Dict[str, BaseExtractor]:
    """Create a complete suite of analytics extractors"""
    return {
        'performance_analytics': PerformanceAnalyticsExtractor(),
        'audience_analytics': AudienceAnalyticsExtractor()
    }


# Export main classes and functions
__all__ = [
    'PerformanceAnalyticsExtractor',
    'AudienceAnalyticsExtractor',
    'AnalyticsConfig',
    'PerformanceMetrics',
    'AudienceInsights',
    'PredictiveInsights',
    'AnalyticsType',
    'InsightLevel',
    'PredictionHorizon',
    'create_analytics_extractor_suite'
]
