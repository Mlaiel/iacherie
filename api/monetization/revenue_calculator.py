"""
Advanced revenue calculation engine with AI-powered estimation algorithms.

This module implements sophisticated revenue calculation models including:
- Multi-platform revenue aggregation
- AI-powered revenue prediction and forecasting  
- Dynamic pricing optimization algorithms
- Creator performance analytics and insights
- Real-time revenue tracking and reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Revenue Optimization Specialist: AI-Powered Financial Modeling
- Data Science Engineer: Predictive Analytics & Machine Learning
- Business Intelligence Analyst: Creator Economy & Market Analysis
- Financial Systems Architect: Payment Processing & Revenue Management

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

from ..core.config import get_database
from ..core.exceptions import MonetizationException, CalculationException


class RevenueCalculationMethod(Enum):
    """Revenue calculation methodologies."""
    REAL_TIME = "real_time"
    PREDICTIVE = "predictive"
    HISTORICAL_AVERAGE = "historical_average"
    MACHINE_LEARNING = "machine_learning"
    HYBRID_MODEL = "hybrid_model"
    DYNAMIC_PRICING = "dynamic_pricing"


class PlatformMetric(Enum):
    """Platform-specific revenue metrics."""
    SPOTIFY_STREAMS = "spotify_streams"
    YOUTUBE_VIEWS = "youtube_views"
    INSTAGRAM_ENGAGEMENT = "instagram_engagement"
    TIKTOK_VIEWS = "tiktok_views"
    TWITCH_SUBS = "twitch_subscribers"
    PATREON_SUPPORTERS = "patreon_supporters"
    BANDCAMP_SALES = "bandcamp_sales"
    SOUNDCLOUD_PLAYS = "soundcloud_plays"


@dataclass
class PlatformRevenueData:
    """Platform-specific revenue and engagement data."""
    platform: str
    metric_type: PlatformMetric
    raw_value: Union[int, float]
    revenue_per_unit: Decimal
    total_revenue: Decimal
    currency: str
    time_period: Tuple[datetime, datetime]
    engagement_rate: float = 0.0
    growth_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueProjection:
    """Revenue forecast and projection data."""
    creator_id: str
    projection_period: Tuple[datetime, datetime]
    conservative_estimate: Decimal
    optimistic_estimate: Decimal
    most_likely_estimate: Decimal
    confidence_score: float
    key_factors: List[str]
    methodology: RevenueCalculationMethod
    platform_breakdown: Dict[str, Decimal]
    risk_factors: List[str] = field(default_factory=list)
    growth_opportunities: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorPerformanceMetrics:
    """Comprehensive creator performance analytics."""
    creator_id: str
    total_followers: int
    engagement_rate: float
    content_frequency: float
    platform_diversity: int
    revenue_consistency: float
    growth_velocity: float
    market_position: str
    performance_score: float
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)


class AdvancedRevenueCalculator:
    """
    AI-powered revenue calculation and forecasting engine.
    
    Provides sophisticated revenue estimation, prediction, and optimization
    capabilities using machine learning algorithms and multi-platform data analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("monetization.revenue_calculator")
        self.db = get_database()
        
        # ML model settings
        self.model_cache = {}
        self.scaler_cache = {}
        self.feature_importance = {}
        
        # Revenue calculation settings
        self.calculation_accuracy = self.config.get("calculation_accuracy", 0.95)
        self.prediction_horizon_days = self.config.get("prediction_horizon_days", 90)
        self.min_data_points = self.config.get("min_data_points", 30)
        
        # Platform revenue rates (updated dynamically)
        self.platform_rates = {
            PlatformMetric.SPOTIFY_STREAMS: Decimal("0.003"),
            PlatformMetric.YOUTUBE_VIEWS: Decimal("0.002"),
            PlatformMetric.INSTAGRAM_ENGAGEMENT: Decimal("0.05"),
            PlatformMetric.TIKTOK_VIEWS: Decimal("0.001"),
            PlatformMetric.TWITCH_SUBS: Decimal("2.50"),
            PlatformMetric.PATREON_SUPPORTERS: Decimal("5.00"),
            PlatformMetric.BANDCAMP_SALES: Decimal("0.90"),
            PlatformMetric.SOUNDCLOUD_PLAYS: Decimal("0.001")
        }
        
        # Thread pool for parallel calculations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize ML models
        self._initialize_ml_models()
        
        self.logger.info("AdvancedRevenueCalculator initialized successfully")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for revenue prediction."""
        try:
            # Revenue prediction models
            self.models = {
                "revenue_forecast": GradientBoostingRegressor(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                ),
                "growth_prediction": RandomForestRegressor(
                    n_estimators=150,
                    max_depth=8,
                    random_state=42
                ),
                "performance_scoring": LinearRegression()
            }
            
            # Initialize scalers
            self.scalers = {
                "feature_scaler": StandardScaler(),
                "target_scaler": StandardScaler()
            }
            
            self.logger.info("ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"ML model initialization failed: {e}")
            raise CalculationException(f"Model initialization error: {e}")
    
    async def calculate_real_time_revenue(
        self,
        creator_id: str,
        platforms: Optional[List[str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, PlatformRevenueData]:
        """
        Calculate real-time revenue across specified platforms.
        
        Args:
            creator_id: Unique creator identifier
            platforms: List of platforms to calculate revenue for
            time_range: Time period for revenue calculation
            
        Returns:
            Dictionary of platform revenue data
        """
        try:
            self.logger.info(f"Calculating real-time revenue for creator: {creator_id}")
            
            # Set default time range if not provided
            if not time_range:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                time_range = (start_date, end_date)
            
            # Get platform data
            platform_data = await self._fetch_platform_data(
                creator_id, platforms, time_range
            )
            
            # Calculate revenue for each platform
            revenue_data = {}
            for platform, data in platform_data.items():
                platform_revenue = await self._calculate_platform_revenue(
                    platform, data, time_range
                )
                revenue_data[platform] = platform_revenue
            
            # Store calculation results
            await self._store_revenue_calculation(creator_id, revenue_data)
            
            self.logger.info(f"Real-time revenue calculated for {len(revenue_data)} platforms")
            
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Real-time revenue calculation failed: {e}")
            raise CalculationException(f"Revenue calculation error: {e}")
    
    async def _fetch_platform_data(
        self,
        creator_id: str,
        platforms: Optional[List[str]],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch data from various platforms."""
        try:
            query = """
            SELECT platform, metric_type, value, engagement_rate, created_at
            FROM creator_platform_metrics 
            WHERE creator_id = $1 AND created_at BETWEEN $2 AND $3
            """
            
            if platforms:
                platform_filter = " AND platform = ANY($4)"
                query += platform_filter
                results = await self.db.fetch(query, creator_id, time_range[0], time_range[1], platforms)
            else:
                results = await self.db.fetch(query, creator_id, time_range[0], time_range[1])
            
            # Organize data by platform
            platform_data = {}
            for row in results:
                platform = row["platform"]
                if platform not in platform_data:
                    platform_data[platform] = []
                
                platform_data[platform].append({
                    "metric_type": row["metric_type"],
                    "value": row["value"],
                    "engagement_rate": row["engagement_rate"],
                    "timestamp": row["created_at"]
                })
            
            return platform_data
            
        except Exception as e:
            self.logger.error(f"Platform data fetch failed: {e}")
            return {}
    
    async def _calculate_platform_revenue(
        self,
        platform: str,
        data: List[Dict[str, Any]],
        time_range: Tuple[datetime, datetime]
    ) -> PlatformRevenueData:
        """Calculate revenue for specific platform."""
        try:
            # Determine primary metric for platform
            metric_mapping = {
                "spotify": PlatformMetric.SPOTIFY_STREAMS,
                "youtube": PlatformMetric.YOUTUBE_VIEWS,
                "instagram": PlatformMetric.INSTAGRAM_ENGAGEMENT,
                "tiktok": PlatformMetric.TIKTOK_VIEWS,
                "twitch": PlatformMetric.TWITCH_SUBS,
                "patreon": PlatformMetric.PATREON_SUPPORTERS,
                "bandcamp": PlatformMetric.BANDCAMP_SALES,
                "soundcloud": PlatformMetric.SOUNDCLOUD_PLAYS
            }
            
            platform_metric = metric_mapping.get(platform.lower(), PlatformMetric.SPOTIFY_STREAMS)
            
            # Aggregate metrics
            total_value = sum(item["value"] for item in data)
            avg_engagement = np.mean([item["engagement_rate"] for item in data]) if data else 0.0
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(platform, data, time_range)
            
            # Get revenue rate for platform
            revenue_per_unit = self.platform_rates.get(platform_metric, Decimal("0.001"))
            
            # Apply dynamic pricing factors
            revenue_per_unit = await self._apply_dynamic_factors(
                platform, revenue_per_unit, avg_engagement, growth_rate
            )
            
            # Calculate total revenue
            total_revenue = Decimal(str(total_value)) * revenue_per_unit
            
            return PlatformRevenueData(
                platform=platform,
                metric_type=platform_metric,
                raw_value=total_value,
                revenue_per_unit=revenue_per_unit,
                total_revenue=total_revenue,
                currency="USD",
                time_period=time_range,
                engagement_rate=avg_engagement,
                growth_rate=growth_rate,
                metadata={"data_points": len(data)}
            )
            
        except Exception as e:
            self.logger.error(f"Platform revenue calculation failed: {e}")
            raise CalculationException(f"Platform calculation error: {e}")
    
    async def _calculate_growth_rate(
        self,
        platform: str,
        data: List[Dict[str, Any]],
        time_range: Tuple[datetime, datetime]
    ) -> float:
        """Calculate growth rate for platform metrics."""
        if len(data) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: x["timestamp"])
        
        # Calculate period growth
        start_period = sorted_data[:len(sorted_data)//3]
        end_period = sorted_data[-len(sorted_data)//3:]
        
        start_avg = np.mean([item["value"] for item in start_period])
        end_avg = np.mean([item["value"] for item in end_period])
        
        if start_avg == 0:
            return 0.0
        
        growth_rate = (end_avg - start_avg) / start_avg
        return min(max(growth_rate, -1.0), 5.0)  # Cap between -100% and +500%
    
    async def _apply_dynamic_factors(
        self,
        platform: str,
        base_rate: Decimal,
        engagement_rate: float,
        growth_rate: float
    ) -> Decimal:
        """Apply dynamic factors to revenue calculations."""
        multiplier = Decimal("1.0")
        
        # Engagement bonus
        if engagement_rate > 0.05:  # 5% engagement
            multiplier *= Decimal("1.2")  # 20% bonus
        elif engagement_rate > 0.03:  # 3% engagement
            multiplier *= Decimal("1.1")  # 10% bonus
        
        # Growth bonus
        if growth_rate > 0.2:  # 20% growth
            multiplier *= Decimal("1.3")  # 30% bonus
        elif growth_rate > 0.1:  # 10% growth
            multiplier *= Decimal("1.15")  # 15% bonus
        
        # Platform-specific adjustments
        platform_adjustments = {
            "spotify": Decimal("1.1"),    # Music streaming premium
            "youtube": Decimal("1.0"),    # Base rate
            "instagram": Decimal("1.2"),  # High engagement value
            "tiktok": Decimal("0.9"),     # Lower monetization
            "patreon": Decimal("1.5")     # Direct fan support premium
        }
        
        platform_factor = platform_adjustments.get(platform.lower(), Decimal("1.0"))
        multiplier *= platform_factor
        
        return base_rate * multiplier
    
    async def generate_revenue_projection(
        self,
        creator_id: str,
        projection_days: int = 90
    ) -> RevenueProjection:
        """
        Generate AI-powered revenue projections for creator.
        
        Args:
            creator_id: Unique creator identifier
            projection_days: Number of days to project forward
            
        Returns:
            Comprehensive revenue projection with confidence scores
        """
        try:
            self.logger.info(f"Generating revenue projection for creator: {creator_id}")
            
            # Get historical data for ML training
            historical_data = await self._fetch_historical_revenue_data(creator_id)
            
            # Prepare features for ML model
            features = await self._prepare_projection_features(creator_id, historical_data)
            
            # Train or get cached ML model
            model = await self._get_or_train_projection_model(creator_id, features)
            
            # Generate predictions
            projection_end = datetime.utcnow() + timedelta(days=projection_days)
            projection_period = (datetime.utcnow(), projection_end)
            
            # Calculate different scenarios
            conservative = await self._calculate_conservative_projection(model, features)
            optimistic = await self._calculate_optimistic_projection(model, features)
            most_likely = await self._calculate_most_likely_projection(model, features)
            
            # Calculate confidence score
            confidence = await self._calculate_projection_confidence(model, features)
            
            # Identify key factors and risks
            key_factors = await self._identify_key_factors(model, features)
            risk_factors = await self._identify_risk_factors(creator_id, features)
            growth_opportunities = await self._identify_growth_opportunities(creator_id, features)
            
            # Generate platform breakdown
            platform_breakdown = await self._generate_platform_breakdown(
                creator_id, most_likely, projection_days
            )
            
            projection = RevenueProjection(
                creator_id=creator_id,
                projection_period=projection_period,
                conservative_estimate=conservative,
                optimistic_estimate=optimistic,
                most_likely_estimate=most_likely,
                confidence_score=confidence,
                key_factors=key_factors,
                methodology=RevenueCalculationMethod.MACHINE_LEARNING,
                platform_breakdown=platform_breakdown,
                risk_factors=risk_factors,
                growth_opportunities=growth_opportunities
            )
            
            # Store projection
            await self._store_revenue_projection(projection)
            
            self.logger.info(f"Revenue projection generated with {confidence:.2%} confidence")
            
            return projection
            
        except Exception as e:
            self.logger.error(f"Revenue projection generation failed: {e}")
            raise CalculationException(f"Projection generation error: {e}")
    
    async def _fetch_historical_revenue_data(
        self,
        creator_id: str,
        days: int = 180
    ) -> pd.DataFrame:
        """Fetch historical revenue data for ML training."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = """
            SELECT 
                platform,
                revenue_amount,
                metric_value,
                engagement_rate,
                created_at::date as date,
                EXTRACT(dow FROM created_at) as day_of_week,
                EXTRACT(day FROM created_at) as day_of_month
            FROM revenue_tracking rt
            JOIN creator_platform_metrics cpm ON rt.content_id = cpm.content_id
            WHERE rt.user_id = (SELECT id FROM users WHERE creator_id = $1)
            AND rt.created_at BETWEEN $2 AND $3
            ORDER BY rt.created_at
            """
            
            results = await self.db.fetch(query, creator_id, start_date, end_date)
            
            # Convert to pandas DataFrame
            df = pd.DataFrame([dict(row) for row in results])
            
            if df.empty:
                self.logger.warning(f"No historical data found for creator: {creator_id}")
                return pd.DataFrame()
            
            # Add calculated features
            df["revenue_per_engagement"] = df["revenue_amount"] / (df["engagement_rate"] + 0.001)
            df["revenue_per_metric"] = df["revenue_amount"] / (df["metric_value"] + 1)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Historical data fetch failed: {e}")
            return pd.DataFrame()
    
    async def _prepare_projection_features(
        self,
        creator_id: str,
        historical_data: pd.DataFrame
    ) -> np.ndarray:
        """Prepare feature matrix for ML projection models."""
        try:
            if historical_data.empty:
                # Return default features if no historical data
                return np.array([[1000, 0.03, 0.1, 1, 0, 0, 1]])
            
            # Calculate statistical features
            revenue_mean = historical_data["revenue_amount"].mean()
            revenue_std = historical_data["revenue_amount"].std()
            revenue_trend = self._calculate_trend(historical_data["revenue_amount"])
            
            engagement_mean = historical_data["engagement_rate"].mean()
            engagement_trend = self._calculate_trend(historical_data["engagement_rate"])
            
            platform_count = historical_data["platform"].nunique()
            
            # Seasonal features
            day_of_week_performance = historical_data.groupby("day_of_week")["revenue_amount"].mean().max()
            monthly_seasonality = historical_data.groupby("day_of_month")["revenue_amount"].std()
            
            # Create feature vector
            features = np.array([[
                revenue_mean,
                revenue_std,
                revenue_trend,
                engagement_mean,
                engagement_trend,
                platform_count,
                day_of_week_performance,
                monthly_seasonality.mean(),
                len(historical_data)  # Data points available
            ]])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature preparation failed: {e}")
            # Return default feature vector
            return np.array([[1000, 100, 0.05, 0.03, 0.01, 2, 150, 50, 30]])
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend coefficient for time series data."""
        if len(series) < 2:
            return 0.0
        
        x = np.arange(len(series))
        coeffs = np.polyfit(x, series.values, 1)
        return float(coeffs[0])  # Slope coefficient
    
    async def _get_or_train_projection_model(
        self,
        creator_id: str,
        features: np.ndarray
    ) -> GradientBoostingRegressor:
        """Get cached or train new projection model."""
        model_key = f"projection_{creator_id}"
        
        if model_key in self.model_cache:
            return self.model_cache[model_key]
        
        # Train new model (in production, this would use more sophisticated training)
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # For this example, we'll create synthetic training data
        # In production, this would use actual historical data
        X_train, y_train = await self._generate_training_data(creator_id, features)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Cache model and scaler
        self.model_cache[model_key] = model
        self.scaler_cache[model_key] = scaler
        
        return model
    
    async def _generate_training_data(
        self,
        creator_id: str,
        features: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate training data for model fitting."""
        # This is a simplified example - in production, use actual historical data
        base_features = features[0]
        
        # Generate variations around base features
        n_samples = 100
        X_train = []
        y_train = []
        
        for _ in range(n_samples):
            # Add noise to features
            feature_variation = base_features * (1 + np.random.normal(0, 0.1, len(base_features)))
            
            # Calculate synthetic target (revenue)
            revenue = (
                feature_variation[0] * 0.7 +  # Base revenue weight
                feature_variation[3] * 10000 +  # Engagement rate weight
                feature_variation[5] * 500 +    # Platform count weight
                np.random.normal(0, feature_variation[0] * 0.1)  # Noise
            )
            
            X_train.append(feature_variation)
            y_train.append(max(revenue, 0))  # Ensure non-negative
        
        return np.array(X_train), np.array(y_train)
    
    async def _calculate_conservative_projection(
        self,
        model: GradientBoostingRegressor,
        features: np.ndarray
    ) -> Decimal:
        """Calculate conservative revenue projection (5th percentile)."""
        try:
            model_key = f"projection_model"
            scaler = self.scaler_cache.get(model_key, StandardScaler().fit(features))
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            
            # Apply conservative factor (80% of prediction)
            conservative = prediction * 0.8
            
            return Decimal(str(max(conservative, 0))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
        except Exception as e:
            self.logger.error(f"Conservative projection calculation failed: {e}")
            return Decimal('100.00')  # Fallback value
    
    async def _calculate_optimistic_projection(
        self,
        model: GradientBoostingRegressor,
        features: np.ndarray
    ) -> Decimal:
        """Calculate optimistic revenue projection (95th percentile)."""
        try:
            model_key = f"projection_model"
            scaler = self.scaler_cache.get(model_key, StandardScaler().fit(features))
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            
            # Apply optimistic factor (150% of prediction)
            optimistic = prediction * 1.5
            
            return Decimal(str(optimistic)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
        except Exception as e:
            self.logger.error(f"Optimistic projection calculation failed: {e}")
            return Decimal('1000.00')  # Fallback value
    
    async def _calculate_most_likely_projection(
        self,
        model: GradientBoostingRegressor,
        features: np.ndarray
    ) -> Decimal:
        """Calculate most likely revenue projection (median)."""
        try:
            model_key = f"projection_model"
            scaler = self.scaler_cache.get(model_key, StandardScaler().fit(features))
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            
            return Decimal(str(prediction)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
        except Exception as e:
            self.logger.error(f"Most likely projection calculation failed: {e}")
            return Decimal('500.00')  # Fallback value
    
    async def _calculate_projection_confidence(
        self,
        model: GradientBoostingRegressor,
        features: np.ndarray
    ) -> float:
        """Calculate confidence score for projection."""
        try:
            # Base confidence on feature quality and model performance
            feature_quality = min(1.0, features[0][8] / 100)  # Data points / 100
            
            # Model confidence (simplified)
            model_confidence = 0.8  # This would be based on actual model validation
            
            # Combined confidence
            confidence = (feature_quality * 0.6) + (model_confidence * 0.4)
            
            return min(max(confidence, 0.1), 0.95)  # Between 10% and 95%
            
        except Exception as e:
            self.logger.error(f"Confidence calculation failed: {e}")
            return 0.7  # Default confidence
    
    async def _identify_key_factors(
        self,
        model: GradientBoostingRegressor,
        features: np.ndarray
    ) -> List[str]:
        """Identify key factors driving revenue projections."""
        try:
            # Feature importance from model
            importance = model.feature_importances_
            
            feature_names = [
                "Average Revenue",
                "Revenue Volatility", 
                "Revenue Trend",
                "Engagement Rate",
                "Engagement Trend",
                "Platform Diversity",
                "Day-of-Week Performance",
                "Monthly Seasonality",
                "Data History Length"
            ]
            
            # Get top 3 most important features
            top_indices = np.argsort(importance)[-3:][::-1]
            key_factors = [feature_names[i] for i in top_indices]
            
            return key_factors
            
        except Exception as e:
            self.logger.error(f"Key factor identification failed: {e}")
            return ["Engagement Rate", "Platform Diversity", "Content Consistency"]
    
    async def _identify_risk_factors(
        self,
        creator_id: str,
        features: np.ndarray
    ) -> List[str]:
        """Identify potential risk factors for revenue."""
        risks = []
        
        try:
            # Check feature values for risk indicators
            if features[0][1] > features[0][0] * 0.5:  # High volatility
                risks.append("High revenue volatility")
            
            if features[0][2] < 0:  # Negative trend
                risks.append("Declining revenue trend")
            
            if features[0][4] < 0:  # Declining engagement
                risks.append("Decreasing engagement rate")
            
            if features[0][5] < 2:  # Low platform diversity
                risks.append("Platform dependency risk")
            
            if features[0][8] < 30:  # Limited data history
                risks.append("Limited historical data")
            
            # Platform-specific risks
            platform_risks = await self._assess_platform_risks(creator_id)
            risks.extend(platform_risks)
            
            return risks[:5]  # Return top 5 risks
            
        except Exception as e:
            self.logger.error(f"Risk factor identification failed: {e}")
            return ["Market volatility", "Platform algorithm changes"]
    
    async def _identify_growth_opportunities(
        self,
        creator_id: str,
        features: np.ndarray
    ) -> List[str]:
        """Identify growth opportunities for creator."""
        opportunities = []
        
        try:
            # Feature-based opportunities
            if features[0][5] < 4:  # Can expand to more platforms
                opportunities.append("Expand to additional platforms")
            
            if features[0][3] < 0.05:  # Low engagement rate
                opportunities.append("Improve audience engagement strategies")
            
            if features[0][2] > 0.1:  # Strong positive trend
                opportunities.append("Capitalize on current growth momentum")
            
            # Content-based opportunities
            content_opportunities = await self._assess_content_opportunities(creator_id)
            opportunities.extend(content_opportunities)
            
            return opportunities[:5]  # Return top 5 opportunities
            
        except Exception as e:
            self.logger.error(f"Growth opportunity identification failed: {e}")
            return ["Diversify content types", "Collaborate with other creators"]
    
    async def _assess_platform_risks(self, creator_id: str) -> List[str]:
        """Assess platform-specific risks."""
        risks = []
        
        # This would analyze platform-specific data
        # For now, return common risks
        risks.extend([
            "Algorithm changes affecting reach",
            "Platform policy modifications",
            "Increased competition in niche"
        ])
        
        return risks
    
    async def _assess_content_opportunities(self, creator_id: str) -> List[str]:
        """Assess content-based growth opportunities."""
        opportunities = []
        
        # This would analyze content performance data
        # For now, return common opportunities
        opportunities.extend([
            "Develop premium content tiers",
            "Launch merchandise store",
            "Offer exclusive subscriber content"
        ])
        
        return opportunities
    
    async def _generate_platform_breakdown(
        self,
        creator_id: str,
        total_projection: Decimal,
        projection_days: int
    ) -> Dict[str, Decimal]:
        """Generate platform-specific revenue breakdown."""
        try:
            # Get current platform distribution
            current_data = await self.calculate_real_time_revenue(creator_id)
            
            if not current_data:
                # Default distribution if no current data
                return {
                    "spotify": total_projection * Decimal("0.4"),
                    "youtube": total_projection * Decimal("0.3"),
                    "instagram": total_projection * Decimal("0.2"),
                    "other": total_projection * Decimal("0.1")
                }
            
            # Calculate proportional breakdown
            total_current = sum(data.total_revenue for data in current_data.values())
            
            if total_current == 0:
                return {"total": total_projection}
            
            breakdown = {}
            for platform, data in current_data.items():
                proportion = data.total_revenue / total_current
                breakdown[platform] = total_projection * proportion
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Platform breakdown generation failed: {e}")
            return {"total": total_projection}
    
    async def _store_revenue_calculation(
        self,
        creator_id: str,
        revenue_data: Dict[str, PlatformRevenueData]
    ):
        """Store revenue calculation results in database."""
        try:
            for platform, data in revenue_data.items():
                query = """
                INSERT INTO revenue_calculations (
                    creator_id, platform, metric_type, raw_value,
                    revenue_per_unit, total_revenue, currency,
                    time_period_start, time_period_end, engagement_rate,
                    growth_rate, metadata, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """
                
                await self.db.execute(
                    query,
                    creator_id,
                    data.platform,
                    data.metric_type.value,
                    data.raw_value,
                    data.revenue_per_unit,
                    data.total_revenue,
                    data.currency,
                    data.time_period[0],
                    data.time_period[1],
                    data.engagement_rate,
                    data.growth_rate,
                    json.dumps(data.metadata),
                    datetime.utcnow()
                )
            
        except Exception as e:
            self.logger.error(f"Revenue calculation storage failed: {e}")
    
    async def _store_revenue_projection(self, projection: RevenueProjection):
        """Store revenue projection in database."""
        try:
            query = """
            INSERT INTO revenue_projections (
                creator_id, projection_start, projection_end,
                conservative_estimate, optimistic_estimate, most_likely_estimate,
                confidence_score, methodology, key_factors, risk_factors,
                growth_opportunities, platform_breakdown, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """
            
            await self.db.execute(
                query,
                projection.creator_id,
                projection.projection_period[0],
                projection.projection_period[1],
                projection.conservative_estimate,
                projection.optimistic_estimate,
                projection.most_likely_estimate,
                projection.confidence_score,
                projection.methodology.value,
                json.dumps(projection.key_factors),
                json.dumps(projection.risk_factors),
                json.dumps(projection.growth_opportunities),
                json.dumps({k: str(v) for k, v in projection.platform_breakdown.items()}),
                projection.calculated_at
            )
            
        except Exception as e:
            self.logger.error(f"Revenue projection storage failed: {e}")
    
    async def analyze_creator_performance(
        self,
        creator_id: str
    ) -> CreatorPerformanceMetrics:
        """
        Comprehensive creator performance analysis.
        
        Args:
            creator_id: Unique creator identifier
            
        Returns:
            Detailed performance metrics and recommendations
        """
        try:
            self.logger.info(f"Analyzing performance for creator: {creator_id}")
            
            # Get creator statistics
            stats = await self._get_creator_statistics(creator_id)
            
            # Calculate performance metrics
            engagement_rate = await self._calculate_overall_engagement(creator_id)
            content_frequency = await self._calculate_content_frequency(creator_id)
            platform_diversity = await self._calculate_platform_diversity(creator_id)
            revenue_consistency = await self._calculate_revenue_consistency(creator_id)
            growth_velocity = await self._calculate_growth_velocity(creator_id)
            
            # Determine market position
            market_position = await self._assess_market_position(creator_id, stats)
            
            # Calculate overall performance score
            performance_score = await self._calculate_performance_score(
                engagement_rate, content_frequency, platform_diversity,
                revenue_consistency, growth_velocity
            )
            
            # Identify strengths and improvement areas
            strengths = await self._identify_strengths(creator_id, stats)
            improvement_areas = await self._identify_improvement_areas(creator_id, stats)
            
            # Benchmark against industry
            benchmark_comparison = await self._benchmark_against_industry(creator_id, stats)
            
            performance = CreatorPerformanceMetrics(
                creator_id=creator_id,
                total_followers=stats.get("total_followers", 0),
                engagement_rate=engagement_rate,
                content_frequency=content_frequency,
                platform_diversity=platform_diversity,
                revenue_consistency=revenue_consistency,
                growth_velocity=growth_velocity,
                market_position=market_position,
                performance_score=performance_score,
                strengths=strengths,
                improvement_areas=improvement_areas,
                benchmark_comparison=benchmark_comparison
            )
            
            # Store performance analysis
            await self._store_performance_analysis(performance)
            
            self.logger.info(f"Performance analysis completed with score: {performance_score:.2f}")
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Creator performance analysis failed: {e}")
            raise CalculationException(f"Performance analysis error: {e}")
    
    async def _get_creator_statistics(self, creator_id: str) -> Dict[str, Any]:
        """Get basic creator statistics from database."""
        try:
            query = """
            SELECT 
                COUNT(DISTINCT platform) as platform_count,
                SUM(followers) as total_followers,
                AVG(engagement_rate) as avg_engagement,
                COUNT(*) as total_posts
            FROM creator_platform_metrics 
            WHERE creator_id = $1 
            AND created_at >= NOW() - INTERVAL '90 days'
            """
            
            result = await self.db.fetchrow(query, creator_id)
            
            return {
                "platform_count": result["platform_count"] or 0,
                "total_followers": result["total_followers"] or 0,
                "avg_engagement": float(result["avg_engagement"] or 0),
                "total_posts": result["total_posts"] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Creator statistics fetch failed: {e}")
            return {}
    
    async def _calculate_overall_engagement(self, creator_id: str) -> float:
        """Calculate overall engagement rate across platforms."""
        try:
            query = """
            SELECT AVG(engagement_rate) as avg_engagement
            FROM creator_platform_metrics 
            WHERE creator_id = $1 
            AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            result = await self.db.fetchrow(query, creator_id)
            return float(result["avg_engagement"] or 0)
            
        except Exception as e:
            self.logger.error(f"Engagement calculation failed: {e}")
            return 0.0
    
    async def _calculate_content_frequency(self, creator_id: str) -> float:
        """Calculate content posting frequency."""
        try:
            query = """
            SELECT COUNT(*) as post_count
            FROM creator_platform_metrics 
            WHERE creator_id = $1 
            AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            result = await self.db.fetchrow(query, creator_id)
            post_count = result["post_count"] or 0
            
            # Posts per day over last 30 days
            return post_count / 30.0
            
        except Exception as e:
            self.logger.error(f"Content frequency calculation failed: {e}")
            return 0.0
    
    async def _calculate_platform_diversity(self, creator_id: str) -> int:
        """Calculate number of active platforms."""
        try:
            query = """
            SELECT COUNT(DISTINCT platform) as platform_count
            FROM creator_platform_metrics 
            WHERE creator_id = $1 
            AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            result = await self.db.fetchrow(query, creator_id)
            return result["platform_count"] or 0
            
        except Exception as e:
            self.logger.error(f"Platform diversity calculation failed: {e}")
            return 0
    
    async def _calculate_revenue_consistency(self, creator_id: str) -> float:
        """Calculate revenue consistency score."""
        try:
            query = """
            SELECT revenue_amount, created_at
            FROM revenue_tracking 
            WHERE user_id = (SELECT id FROM users WHERE creator_id = $1)
            AND created_at >= NOW() - INTERVAL '90 days'
            ORDER BY created_at
            """
            
            results = await self.db.fetch(query, creator_id)
            
            if not results:
                return 0.0
            
            revenues = [float(row["revenue_amount"]) for row in results]
            
            if len(revenues) < 2:
                return 0.0
            
            # Calculate coefficient of variation (lower is more consistent)
            mean_revenue = np.mean(revenues)
            std_revenue = np.std(revenues)
            
            if mean_revenue == 0:
                return 0.0
            
            cv = std_revenue / mean_revenue
            
            # Convert to consistency score (higher is better)
            consistency = max(0, 1 - cv)
            
            return min(consistency, 1.0)
            
        except Exception as e:
            self.logger.error(f"Revenue consistency calculation failed: {e}")
            return 0.0
    
    async def _calculate_growth_velocity(self, creator_id: str) -> float:
        """Calculate growth velocity across metrics."""
        try:
            query = """
            SELECT 
                DATE_TRUNC('week', created_at) as week,
                AVG(followers) as avg_followers,
                AVG(engagement_rate) as avg_engagement
            FROM creator_platform_metrics 
            WHERE creator_id = $1 
            AND created_at >= NOW() - INTERVAL '12 weeks'
            GROUP BY DATE_TRUNC('week', created_at)
            ORDER BY week
            """
            
            results = await self.db.fetch(query, creator_id)
            
            if len(results) < 2:
                return 0.0
            
            # Calculate follower growth velocity
            followers = [float(row["avg_followers"]) for row in results]
            engagement = [float(row["avg_engagement"]) for row in results]
            
            # Calculate trends
            weeks = np.arange(len(followers))
            follower_trend = np.polyfit(weeks, followers, 1)[0] if len(followers) > 1 else 0
            engagement_trend = np.polyfit(weeks, engagement, 1)[0] if len(engagement) > 1 else 0
            
            # Normalize and combine
            follower_velocity = follower_trend / (np.mean(followers) + 1) if np.mean(followers) > 0 else 0
            engagement_velocity = engagement_trend / (np.mean(engagement) + 0.01) if np.mean(engagement) > 0 else 0
            
            # Combined growth velocity
            growth_velocity = (follower_velocity * 0.6) + (engagement_velocity * 0.4)
            
            return min(max(growth_velocity, -1.0), 1.0)  # Clamp between -1 and 1
            
        except Exception as e:
            self.logger.error(f"Growth velocity calculation failed: {e}")
            return 0.0
    
    async def _assess_market_position(self, creator_id: str, stats: Dict[str, Any]) -> str:
        """Assess creator's market position."""
        total_followers = stats.get("total_followers", 0)
        avg_engagement = stats.get("avg_engagement", 0)
        platform_count = stats.get("platform_count", 0)
        
        # Simple position assessment
        if total_followers > 100000 and avg_engagement > 0.05 and platform_count >= 3:
            return "Leading"
        elif total_followers > 50000 and avg_engagement > 0.03 and platform_count >= 2:
            return "Established"
        elif total_followers > 10000 and avg_engagement > 0.02:
            return "Growing"
        elif total_followers > 1000:
            return "Emerging"
        else:
            return "Starting"
    
    async def _calculate_performance_score(
        self,
        engagement_rate: float,
        content_frequency: float,
        platform_diversity: int,
        revenue_consistency: float,
        growth_velocity: float
    ) -> float:
        """Calculate overall performance score."""
        # Normalize metrics to 0-1 scale
        engagement_score = min(engagement_rate / 0.1, 1.0)  # 10% engagement = perfect
        frequency_score = min(content_frequency / 2.0, 1.0)  # 2 posts/day = perfect
        diversity_score = min(platform_diversity / 5.0, 1.0)  # 5 platforms = perfect
        consistency_score = revenue_consistency  # Already 0-1
        growth_score = (growth_velocity + 1) / 2  # Convert -1,1 to 0,1
        
        # Weighted performance score
        performance_score = (
            engagement_score * 0.3 +
            frequency_score * 0.2 +
            diversity_score * 0.15 +
            consistency_score * 0.2 +
            growth_score * 0.15
        )
        
        return round(performance_score * 100, 2)  # Convert to 0-100 scale
    
    async def _identify_strengths(self, creator_id: str, stats: Dict[str, Any]) -> List[str]:
        """Identify creator strengths."""
        strengths = []
        
        if stats.get("avg_engagement", 0) > 0.05:
            strengths.append("High audience engagement")
        
        if stats.get("platform_count", 0) >= 3:
            strengths.append("Strong multi-platform presence")
        
        if stats.get("total_followers", 0) > 50000:
            strengths.append("Large follower base")
        
        # Additional analysis could be added here
        
        return strengths
    
    async def _identify_improvement_areas(self, creator_id: str, stats: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement."""
        improvements = []
        
        if stats.get("avg_engagement", 0) < 0.02:
            improvements.append("Increase audience engagement")
        
        if stats.get("platform_count", 0) < 2:
            improvements.append("Expand to additional platforms")
        
        if stats.get("total_posts", 0) < 30:  # Less than 1 post per day
            improvements.append("Increase content frequency")
        
        return improvements
    
    async def _benchmark_against_industry(
        self,
        creator_id: str,
        stats: Dict[str, Any]
    ) -> Dict[str, float]:
        """Benchmark creator against industry averages."""
        # Industry benchmarks (simplified examples)
        industry_benchmarks = {
            "engagement_rate": 0.03,
            "platform_diversity": 2.5,
            "content_frequency": 1.2,
            "follower_growth": 0.05
        }
        
        creator_metrics = {
            "engagement_rate": stats.get("avg_engagement", 0),
            "platform_diversity": stats.get("platform_count", 0),
            "content_frequency": stats.get("total_posts", 0) / 30,
            "follower_growth": 0.02  # Would be calculated from actual data
        }
        
        comparison = {}
        for metric, benchmark in industry_benchmarks.items():
            creator_value = creator_metrics.get(metric, 0)
            if benchmark > 0:
                comparison[metric] = creator_value / benchmark
            else:
                comparison[metric] = 0.0
        
        return comparison
    
    async def _store_performance_analysis(self, performance: CreatorPerformanceMetrics):
        """Store performance analysis in database."""
        try:
            query = """
            INSERT INTO creator_performance_analysis (
                creator_id, total_followers, engagement_rate, content_frequency,
                platform_diversity, revenue_consistency, growth_velocity,
                market_position, performance_score, strengths, improvement_areas,
                benchmark_comparison, analyzed_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """
            
            await self.db.execute(
                query,
                performance.creator_id,
                performance.total_followers,
                performance.engagement_rate,
                performance.content_frequency,
                performance.platform_diversity,
                performance.revenue_consistency,
                performance.growth_velocity,
                performance.market_position,
                performance.performance_score,
                json.dumps(performance.strengths),
                json.dumps(performance.improvement_areas),
                json.dumps(performance.benchmark_comparison),
                datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Performance analysis storage failed: {e}")
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=False)
        except Exception:
            pass


# Factory function for easy instantiation
def create_revenue_calculator(config: Optional[Dict[str, Any]] = None) -> AdvancedRevenueCalculator:
    """Create and return configured revenue calculator instance."""
    return AdvancedRevenueCalculator(config)
