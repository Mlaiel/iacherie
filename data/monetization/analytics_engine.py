"""Advanced Analytics Engine for Monetization
==========================================

Professional analytics system for revenue tracking and monetization insights.
Provides comprehensive analytics, performance metrics, trend analysis,
and predictive modeling for content creator monetization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import uuid
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis

from .revenue_calculator import Currency, PlatformType


class AnalyticsType(Enum):
    """
Types of analytics"""

    REVENUE = "revenue"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    GROWTH = "growth"
    PREDICTIVE = "predictive"


class MetricType(Enum):
    """Metric types"""

    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    INDEX = "index"
    SCORE = "score"


class TimeGranularity(Enum):
    """Time granularity for analytics"""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class AnalyticsMetric:
    """Individual analytics metric"""
    metric_id: str
    name: str
    value: Union[Decimal, float, int]
    metric_type: MetricType
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class TimeSeriesData:
    """
Time series analytics data"""
    metric_name: str
    time_granularity: TimeGranularity
    data_points: List[Tuple[datetime, float]]
    trend: str  # increasing, decreasing, stable
    growth_rate: float
    seasonality: float


@dataclass
class PerformanceReport:
    """
Performance analytics report"""
    user_id: str
    period_start: datetime
    period_end: datetime
    revenue_metrics: Dict[str, AnalyticsMetric]
    performance_metrics: Dict[str, AnalyticsMetric]
    growth_metrics: Dict[str, AnalyticsMetric]
    benchmark_comparison: Dict[str, float]
    insights: List[str]
    recommendations: List[str]


@dataclass
class PredictiveModel:
    """
Predictive analytics model"""
    model_id: str
    model_type: str
    target_metric: str
    features: List[str]
    accuracy_score: float
    last_trained: datetime
    predictions: Dict[str, float]


class AnalyticsEngine:
    """
    Professional analytics engine for IA Influencer Agent monetization.
    
    Provides comprehensive analytics, performance tracking, predictive modeling,
    and data visualization for content creator monetization optimization.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """
        Initialize AnalyticsEngine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """
        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 1800  # 30 minutes
        self.prediction_cache_ttl = 7200  # 2 hours
        self.model_retrain_interval = timedelta(days=7)
        
        # Analytics configuration
        self.revenue_thresholds = {
            'low': Decimal('100.00'),
            'medium': Decimal('500.00'),
            'high': Decimal('2000.00'),
            'premium': Decimal('10000.00')
        }
        
        # Benchmark data (would be updated from industry sources)
        self.industry_benchmarks = {
            'youtube': {
                'average_cpm': 2.50,
                'average_ctr': 0.035,
                'average_engagement': 0.045
            },
            'instagram': {
                'average_cpm': 3.20,
                'average_ctr': 0.042,
                'average_engagement': 0.058
            },
            'tiktok': {
                'average_cpm': 1.80,
                'average_ctr': 0.065,
                'average_engagement': 0.075
            }
        }
        
        # ML models for predictions
        self.prediction_models = {}
        self.scalers = {}
    
    async def calculate_revenue_analytics(self, user_id: str, period_days: int = 30) -> Dict[str, AnalyticsMetric]:
        """
        Calculate comprehensive revenue analytics.
        
        Args:
            user_id: User identifier
            period_days: Analysis period in days
            
        Returns:
            Dictionary of revenue analytics metrics
        """
        try:
            # Check cache first
            cache_key = f"revenue_analytics:{user_id}:{period_days}"
            cached_analytics = await self._get_from_cache(cache_key)
            if cached_analytics:
                return {k: AnalyticsMetric(**v) for k, v in cached_analytics.items()}
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get revenue data
            revenue_data = await self._get_user_revenue_data(user_id, start_date, end_date)
            
            metrics = {}
            
            # Total revenue
            total_revenue = sum(item['amount'] for item in revenue_data)
            metrics['total_revenue'] = AnalyticsMetric(
                metric_id='total_revenue',
                name='Total Revenue',
                value=total_revenue,
                metric_type=MetricType.ABSOLUTE,
                unit='EUR',
                timestamp=datetime.utcnow(),
                metadata={'period_days': period_days}
            )
            
            # Average daily revenue
            avg_daily_revenue = total_revenue / period_days if period_days > 0 else Decimal('0')
            metrics['avg_daily_revenue'] = AnalyticsMetric(
                metric_id='avg_daily_revenue',
                name='Average Daily Revenue',
                value=avg_daily_revenue,
                metric_type=MetricType.ABSOLUTE,
                unit='EUR/day',
                timestamp=datetime.utcnow(),
                metadata={'calculated_from': 'total_revenue'}
            )
            
            # Revenue growth rate
            previous_period_revenue = await self._get_previous_period_revenue(
                user_id, start_date - timedelta(days=period_days), start_date
            )
            growth_rate = 0.0
            if previous_period_revenue > 0:
                growth_rate = ((total_revenue - previous_period_revenue) / previous_period_revenue) * 100
            
            metrics['revenue_growth_rate'] = AnalyticsMetric(
                metric_id='revenue_growth_rate',
                name='Revenue Growth Rate',
                value=growth_rate,
                metric_type=MetricType.PERCENTAGE,
                unit='%',
                timestamp=datetime.utcnow(),
                metadata={'comparison_period': period_days}
            )
            
            # Revenue per platform
            platform_revenue = await self._calculate_platform_revenue(revenue_data)
            for platform, amount in platform_revenue.items():
                metrics[f'revenue_{platform}'] = AnalyticsMetric(
                    metric_id=f'revenue_{platform}',
                    name=f'{platform.title()} Revenue',
                    value=amount,
                    metric_type=MetricType.ABSOLUTE,
                    unit='EUR',
                    timestamp=datetime.utcnow(),
                    metadata={'platform': platform}
                )
            
            # Revenue diversity index (how spread across platforms)
            diversity_index = await self._calculate_revenue_diversity(platform_revenue)
            metrics['revenue_diversity'] = AnalyticsMetric(
                metric_id='revenue_diversity',
                name='Revenue Diversity Index',
                value=diversity_index,
                metric_type=MetricType.INDEX,
                unit='index',
                timestamp=datetime.utcnow(),
                metadata={'range': '0-1, higher is more diverse'}
            )
            
            # Revenue volatility
            volatility = await self._calculate_revenue_volatility(revenue_data)
            metrics['revenue_volatility'] = AnalyticsMetric(
                metric_id='revenue_volatility',
                name='Revenue Volatility',
                value=volatility,
                metric_type=MetricType.PERCENTAGE,
                unit='%',
                timestamp=datetime.utcnow(),
                metadata={'interpretation': 'standard deviation of daily revenue'}
            )
            
            # Cache results
            cache_data = {k: v.__dict__ for k, v in metrics.items()}
            await self._save_to_cache(cache_key, cache_data)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue analytics: {str(e)}")
            return {}
    
    async def generate_performance_report(self, user_id: str, period_days: int = 30) -> PerformanceReport:
        """
        Generate comprehensive performance report.
        
        Args:
            user_id: User identifier
            period_days: Report period in days
            
        Returns:
            Complete performance report
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get revenue analytics
            revenue_metrics = await self.calculate_revenue_analytics(user_id, period_days)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(user_id, period_days)
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(user_id, period_days)
            
            # Compare with benchmarks
            benchmark_comparison = await self._compare_with_benchmarks(user_id, period_days)
            
            # Generate insights
            insights = await self._generate_performance_insights(
                revenue_metrics, performance_metrics, growth_metrics, benchmark_comparison
            )
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(
                user_id, revenue_metrics, performance_metrics
            )
            
            report = PerformanceReport(
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                revenue_metrics=revenue_metrics,
                performance_metrics=performance_metrics,
                growth_metrics=growth_metrics,
                benchmark_comparison=benchmark_comparison,
                insights=insights,
                recommendations=recommendations
            )
            
            # Cache report
            cache_key = f"performance_report:{user_id}:{period_days}"
            await self._save_to_cache(cache_key, report.__dict__, ttl=3600)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return PerformanceReport(
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                revenue_metrics={},
                performance_metrics={},
                growth_metrics={},
                benchmark_comparison={},
                insights=[],
                recommendations=[]
            )
    
    async def create_time_series_analysis(self, user_id: str, metric_name: str,
                                        granularity: TimeGranularity,
                                        period_days: int = 90) -> TimeSeriesData:
        """
        Create time series analysis for specific metric.
        
        Args:
            user_id: User identifier
            metric_name: Name of metric to analyze
            granularity: Time granularity for analysis
            period_days: Analysis period in days
            
        Returns:
            Time series analysis data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get time series data
            raw_data = await self._get_metric_time_series(
                user_id, metric_name, start_date, end_date, granularity
            )
            
            if not raw_data:
                return TimeSeriesData(
                    metric_name=metric_name,
                    time_granularity=granularity,
                    data_points=[],
                    trend='stable',
                    growth_rate=0.0,
                    seasonality=0.0
                )
            
            # Convert to pandas for analysis
            df = pd.DataFrame(raw_data, columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate trend
            trend = await self._calculate_trend(df['value'].values)
            
            # Calculate growth rate
            if len(df) >= 2:
                first_value = df['value'].iloc[0]
                last_value = df['value'].iloc[-1]
                growth_rate = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            else:
                growth_rate = 0.0
            
            # Calculate seasonality
            seasonality = await self._calculate_seasonality(df['value'].values)
            
            # Prepare data points
            data_points = [(row['timestamp'], float(row['value'])) for _, row in df.iterrows()]
            
            return TimeSeriesData(
                metric_name=metric_name,
                time_granularity=granularity,
                data_points=data_points,
                trend=trend,
                growth_rate=growth_rate,
                seasonality=seasonality
            )
            
        except Exception as e:
            self.logger.error(f"Error creating time series analysis: {str(e)}")
            return TimeSeriesData(
                metric_name=metric_name,
                time_granularity=granularity,
                data_points=[],
                trend='stable',
                growth_rate=0.0,
                seasonality=0.0
            )
    
    async def predict_revenue(self, user_id: str, prediction_days: int = 30) -> Dict[str, float]:
        """
        Predict future revenue using ML models.
        
        Args:
            user_id: User identifier
            prediction_days: Number of days to predict
            
        Returns:
            Revenue predictions
        """
        try:
            # Check cache first
            cache_key = f"revenue_prediction:{user_id}:{prediction_days}"
            cached_prediction = await self._get_from_cache(cache_key)
            if cached_prediction:
                return cached_prediction
            
            # Get historical data for training
            historical_data = await self._get_historical_features(user_id, days=90)
            
            if len(historical_data) < 30:  # Need minimum data for prediction
                # Return baseline prediction
                baseline = await self._calculate_baseline_prediction(user_id, prediction_days)
                return {'predicted_revenue': baseline, 'confidence': 0.3}
            
            # Train or load model
            model = await self._get_or_train_revenue_model(user_id, historical_data)
            
            # Generate features for prediction
            prediction_features = await self._generate_prediction_features(user_id, prediction_days)
            
            # Make predictions
            predictions = model.predict(prediction_features)
            
            # Calculate confidence score
            confidence = await self._calculate_prediction_confidence(model, predictions)
            
            result = {
                'predicted_revenue': float(np.sum(predictions)),
                'daily_predictions': [float(p) for p in predictions],
                'confidence': confidence,
                'model_accuracy': getattr(model, 'score_', 0.8)
            }
            
            # Cache predictions
            await self._save_to_cache(cache_key, result, ttl=self.prediction_cache_ttl)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error predicting revenue: {str(e)}")
            return {'predicted_revenue': 0.0, 'confidence': 0.0}
    
    async def create_dashboard_visualization(self, user_id: str) -> Dict[str, Any]:
        """
        Create visualization data for analytics dashboard.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dashboard visualization data
        """
        try:
            visualizations = {}
            
            # Revenue trend chart
            revenue_time_series = await self.create_time_series_analysis(
                user_id, 'revenue', TimeGranularity.DAILY, 30
            )
            
            if revenue_time_series.data_points:
                dates = [point[0].strftime('%Y-%m-%d') for point in revenue_time_series.data_points]
                values = [point[1] for point in revenue_time_series.data_points]
                
                fig_revenue = go.Figure()
                fig_revenue.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name='Daily Revenue',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig_revenue.update_layout(
                    title='Revenue Trend (Last 30 Days)',
                    xaxis_title='Date',
                    yaxis_title='Revenue (EUR)',
                    height=400
                )
                
                visualizations['revenue_trend'] = fig_revenue.to_json()
            
            # Platform revenue pie chart
            revenue_metrics = await self.calculate_revenue_analytics(user_id, 30)
            platform_data = {}
            
            for metric_id, metric in revenue_metrics.items():
                if metric_id.startswith('revenue_') and metric_id != 'total_revenue':
                    platform = metric_id.replace('revenue_', '').title()
                    platform_data[platform] = float(metric.value)
            
            if platform_data:
                fig_platform = go.Figure(data=[go.Pie(
                    labels=list(platform_data.keys()),
                    values=list(platform_data.values()),
                    hole=0.3
                )])
                fig_platform.update_layout(
                    title='Revenue by Platform',
                    height=400
                )
                
                visualizations['platform_breakdown'] = fig_platform.to_json()
            
            # Performance metrics gauge
            performance_metrics = await self._calculate_performance_metrics(user_id, 30)
            
            if 'engagement_rate' in performance_metrics:
                engagement_rate = float(performance_metrics['engagement_rate'].value)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=engagement_rate * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Engagement Rate (%)"},
                    gauge={
                        'axis': {'range': [None, 10]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 2.5], 'color': "lightgray"},
                            {'range': [2.5, 5], 'color': "gray"},
                            {'range': [5, 10], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 7.5
                        }
                    }
                ))
                fig_gauge.update_layout(height=400)
                
                visualizations['engagement_gauge'] = fig_gauge.to_json()
            
            return visualizations
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard visualization: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _get_user_revenue_data(self, user_id: str, start_date: datetime,
                                   end_date: datetime) -> List[Dict]:
        """Get user revenue data for period"""
        # Implementation would query revenue database
        # Placeholder implementation
        revenue_data = []
        
        # Generate sample data
        current_date = start_date
        while current_date <= end_date:
            revenue_data.append({
                'date': current_date,
                'amount': float(np.random.uniform(10, 100)),
                'platform': np.random.choice(['youtube', 'instagram', 'tiktok']),
                'content_id': f"content_{np.random.randint(1, 10)}"
            })
            current_date += timedelta(days=1)
        
        return revenue_data
    
    async def _get_previous_period_revenue(self, user_id: str, start_date: datetime,
                                         end_date: datetime) -> Decimal:
        """Get revenue for previous period"""
        # Implementation would query previous period revenue
        return Decimal('800.00')  # Sample previous revenue
    
    async def _calculate_platform_revenue(self, revenue_data: List[Dict]) -> Dict[str, Decimal]:
        """
Calculate revenue by platform"""
        platform_revenue = {}
        
        for item in revenue_data:
            platform = item['platform']
            amount = Decimal(str(item['amount']))
            platform_revenue[platform] = platform_revenue.get(platform, Decimal('0')) + amount
        
        return platform_revenue
    
    async def _calculate_revenue_diversity(self, platform_revenue: Dict[str, Decimal]) -> float:
        """
Calculate revenue diversity index using Gini coefficient"""
        if not platform_revenue:
            return 0.0
        
        values = [float(v) for v in platform_revenue.values()]
        n = len(values)
        
        if n <= 1:
            return 0.0
        
        # Calculate Gini coefficient
        values.sort()
        cumsum = np.cumsum(values)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        
        # Convert to diversity index (1 - Gini)
        return 1.0 - gini
    
    async def _calculate_revenue_volatility(self, revenue_data: List[Dict]) -> float:
        """
Calculate revenue volatility (standard deviation)"""
        if len(revenue_data) < 2:
            return 0.0
        
        amounts = [item['amount'] for item in revenue_data]
        return float(np.std(amounts))
    
    async def _calculate_trend(self, values: np.ndarray) -> str:
        """
Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    async def _calculate_seasonality(self, values: np.ndarray) -> float:
        """
Calculate seasonality factor"""
        if len(values) < 7:  # Need at least a week of data
            return 0.0
        
        # Simple seasonality: coefficient of variation
        return float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0.0
    
    async def _get_metric_time_series(self, user_id: str, metric_name: str,
                                    start_date: datetime, end_date: datetime,
                                    granularity: TimeGranularity) -> List[Tuple]:
        """
Get time series data for metric"""
        # Implementation would query metric data
        # Placeholder implementation generating sample data
        data = []
        
        if granularity == TimeGranularity.DAILY:
            current_date = start_date
            while current_date <= end_date:
                value = np.random.uniform(50, 150)  # Sample metric value
                data.append((current_date, value))
                current_date += timedelta(days=1)
        
        return data
    
    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """
Get data from cache"""
        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def _save_to_cache(self, key: str, data: Dict, ttl: int = None):
        """
Save data to cache"""
        try:
            ttl = ttl or self.cache_ttl
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache save failed: {str(e)}")
    
    # Additional helper methods would be implemented here for ML models,
    # benchmark comparisons, performance calculations, etc.
