"""Distribution Optimization Engine

AI-powered engine for optimizing content distribution strategies and performance.
Uses machine learning to continuously improve distribution effectiveness.

Author: Fahed Mlaiel
Email: mlaiel@live.de
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.config import settings
from ....models.content import ContentModel, ContentType
from ....models.user import UserModel
from ....models.distribution_analytics import DistributionAnalyticsModel
from .platform_manager import PlatformType
from .strategy_engine import StrategyType


logger = logging.getLogger(__name__)


class OptimizationGoal(str, Enum):
    """
Optimization objectives"""

    MAXIMIZE_REACH = "maximize_reach"
    MAXIMIZE_ENGAGEMENT = "maximize_engagement"
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_CONVERSION = "maximize_conversion"
    MINIMIZE_COST = "minimize_cost"
    BALANCED_PERFORMANCE = "balanced_performance"


class OptimizationScope(str, Enum):
    """Scope of optimization"""

    SINGLE_POST = "single_post"
    CONTENT_SERIES = "content_series"
    PLATFORM_STRATEGY = "platform_strategy"
    OVERALL_STRATEGY = "overall_strategy"


@dataclass
class OptimizationFeature:
    """Feature for optimization model"""
    name: str
    value: float
    importance: float
    category: str  # content, timing, platform, audience


@dataclass
class OptimizationResult:
    """
Optimization result with recommendations"""
    goal: OptimizationGoal
    predicted_improvement: float
    confidence_score: float
    recommendations: List[str]
    feature_importance: List[OptimizationFeature]
    optimal_parameters: Dict[str, Any]
    a_b_test_suggestions: List[Dict[str, Any]]


class OptimizationRequest(BaseModel):
    """
Optimization request model"""
    user_id: int
    content_id: Optional[int] = None
    goal: OptimizationGoal
    scope: OptimizationScope
    platforms: Optional[List[PlatformType]] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    current_strategy: Optional[Dict[str, Any]] = None
    optimization_horizon: int = 30  # days


class DistributionOptimizer:
    """
    AI-powered distribution optimization engine
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.models = self._initialize_models()
        self.feature_extractors = self._initialize_feature_extractors()
        self.optimization_strategies = self._initialize_optimization_strategies()
        
    def _initialize_models(self) -> Dict[str, Any]:
        """
Initialize ML models for optimization"""
        models = {}
        
        try:
            # Load pre-trained models
            models["reach_predictor"] = joblib.load("models/reach_optimization.pkl")
            models["engagement_predictor"] = joblib.load("models/engagement_optimization.pkl")
            models["revenue_predictor"] = joblib.load("models/revenue_optimization.pkl")
            models["conversion_predictor"] = joblib.load("models/conversion_optimization.pkl")
            
            # Load feature scalers
            models["feature_scaler"] = joblib.load("models/optimization_scaler.pkl")
            models["label_encoder"] = joblib.load("models/optimization_encoder.pkl")
            
        except FileNotFoundError:
            logger.warning("Pre-trained optimization models not found, creating new ones")
            models = self._create_default_models()
        
        return models
    
    def _create_default_models(self) -> Dict[str, Any]:
        """Create default optimization models"""
        return {
            "reach_predictor": GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.1, max_depth=6
            ),
            "engagement_predictor": RandomForestRegressor(
                n_estimators=100, max_depth=8
            ),
            "revenue_predictor": GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.1, max_depth=6
            ),
            "conversion_predictor": RandomForestRegressor(
                n_estimators=100, max_depth=6
            ),
            "feature_scaler": StandardScaler(),
            "label_encoder": LabelEncoder()
        }
    
    def _initialize_feature_extractors(self) -> Dict[str, callable]:
        """Initialize feature extraction functions"""
        return {
            "content_features": self._extract_content_features,
            "timing_features": self._extract_timing_features,
            "platform_features": self._extract_platform_features,
            "audience_features": self._extract_audience_features,
            "historical_features": self._extract_historical_features,
            "competitive_features": self._extract_competitive_features
        }
    
    def _initialize_optimization_strategies(self) -> Dict[OptimizationGoal, callable]:
        """Initialize optimization strategies for different goals"""
        return {
            OptimizationGoal.MAXIMIZE_REACH: self._optimize_for_reach,
            OptimizationGoal.MAXIMIZE_ENGAGEMENT: self._optimize_for_engagement,
            OptimizationGoal.MAXIMIZE_REVENUE: self._optimize_for_revenue,
            OptimizationGoal.MAXIMIZE_CONVERSION: self._optimize_for_conversion,
            OptimizationGoal.MINIMIZE_COST: self._optimize_for_cost,
            OptimizationGoal.BALANCED_PERFORMANCE: self._optimize_for_balance
        }
    
    async def optimize_distribution(
        self, request: OptimizationRequest
    ) -> OptimizationResult:
        """
        Optimize distribution strategy based on request parameters
        
        Args:
            request: Optimization request with goals and constraints
            
        Returns:
            Optimization result with recommendations
        """
        try:
            # Validate request
            await self._validate_optimization_request(request)
            
            # Extract features for optimization
            features = await self._extract_optimization_features(request)
            
            # Get historical performance data
            historical_data = await self._get_historical_performance(request)
            
            # Train/update models if needed
            if len(historical_data) > 50:  # Minimum data for training
                await self._update_models(historical_data)
            
            # Apply optimization strategy
            optimization_strategy = self.optimization_strategies[request.goal]
            optimization_result = await optimization_strategy(request, features, historical_data)
            
            # Generate A/B test suggestions
            ab_test_suggestions = await self._generate_ab_test_suggestions(
                request, optimization_result
            )
            optimization_result.a_b_test_suggestions = ab_test_suggestions
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Distribution optimization failed: {e}")
            raise
    
    async def _validate_optimization_request(self, request: OptimizationRequest) -> None:
        """Validate optimization request"""
        # Check user exists
        user = self.db.query(UserModel).filter(UserModel.id == request.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check content exists if specified
        if request.content_id:
            content = self.db.query(ContentModel).filter(
                ContentModel.id == request.content_id,
                ContentModel.user_id == request.user_id
            ).first()
            if not content:
                raise ValueError("Content not found or access denied")
        
        # Validate optimization horizon
        if request.optimization_horizon < 1 or request.optimization_horizon > 365:
            raise ValueError("Optimization horizon must be between 1 and 365 days")
    
    async def _extract_optimization_features(
        self, request: OptimizationRequest
    ) -> Dict[str, List[OptimizationFeature]]:
        """Extract features for optimization"""
        all_features = {}
        
        for feature_type, extractor in self.feature_extractors.items():
            features = await extractor(request)
            all_features[feature_type] = features
        
        return all_features
    
    async def _extract_content_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """
Extract content-related features"""
        features = []
        
        if request.content_id:
            content = self.db.query(ContentModel).filter(
                ContentModel.id == request.content_id
            ).first()
            
            if content:
                # Content type
                content_type_score = {
                    ContentType.VIDEO: 0.8,
                    ContentType.AUDIO: 0.7,
                    ContentType.IMAGE: 0.6,
                    ContentType.TEXT: 0.5
                }.get(content.content_type, 0.5)
                
                features.append(OptimizationFeature(
                    name="content_type_score",
                    value=content_type_score,
                    importance=0.3,
                    category="content"
                ))
                
                # Title length
                title_length = len(content.title) if content.title else 0
                title_score = min(1.0, title_length / 100)  # Optimal around 100 chars
                
                features.append(OptimizationFeature(
                    name="title_optimization",
                    value=title_score,
                    importance=0.2,
                    category="content"
                ))
                
                # Description quality
                desc_length = len(content.description) if content.description else 0
                desc_score = min(1.0, desc_length / 500)  # Optimal around 500 chars
                
                features.append(OptimizationFeature(
                    name="description_quality",
                    value=desc_score,
                    importance=0.15,
                    category="content"
                ))
                
                # Hashtag count
                hashtag_count = len(content.hashtags) if content.hashtags else 0
                hashtag_score = min(1.0, hashtag_count / 15)  # Optimal around 15 hashtags
                
                features.append(OptimizationFeature(
                    name="hashtag_optimization",
                    value=hashtag_score,
                    importance=0.1,
                    category="content"
                ))
                
                # Content quality (from metadata)
                quality_score = 0.5  # Default
                if content.metadata:
                    if content.metadata.get("resolution"):
                        if "1080p" in str(content.metadata["resolution"]):
                            quality_score = 0.8
                        elif "4K" in str(content.metadata["resolution"]):
                            quality_score = 1.0
                    
                    if content.metadata.get("duration"):
                        duration = content.metadata["duration"]
                        if isinstance(duration, (int, float)):
                            # Optimal duration varies by content type
                            optimal_durations = {
                                ContentType.VIDEO: 300,  # 5 minutes
                                ContentType.AUDIO: 1200,  # 20 minutes
                                ContentType.IMAGE: 0,
                                ContentType.TEXT: 0
                            }
                            optimal = optimal_durations.get(content.content_type, 300)
                            if optimal > 0:
                                duration_score = 1.0 - min(1.0, abs(duration - optimal) / optimal)
                                quality_score = max(quality_score, duration_score)
                
                features.append(OptimizationFeature(
                    name="content_quality",
                    value=quality_score,
                    importance=0.25,
                    category="content"
                ))
        
        return features
    
    async def _extract_timing_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """Extract timing-related features"""
        features = []
        
        now = datetime.utcnow()
        
        # Hour of day (0-23)
        hour_score = self._calculate_hour_score(now.hour)
        features.append(OptimizationFeature(
            name="posting_hour_optimization",
            value=hour_score,
            importance=0.2,
            category="timing"
        ))
        
        # Day of week (0-6, Monday=0)
        day_score = self._calculate_day_score(now.weekday())
        features.append(OptimizationFeature(
            name="posting_day_optimization",
            value=day_score,
            importance=0.15,
            category="timing"
        ))
        
        # Month seasonality
        month_score = self._calculate_month_score(now.month)
        features.append(OptimizationFeature(
            name="seasonal_optimization",
            value=month_score,
            importance=0.1,
            category="timing"
        ))
        
        # Posting frequency (recent activity)
        recent_posts = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == request.user_id,
            DistributionAnalyticsModel.created_at >= now - timedelta(days=7)
        ).count()
        
        frequency_score = min(1.0, recent_posts / 14)  # Optimal ~2 posts per day
        features.append(OptimizationFeature(
            name="posting_frequency",
            value=frequency_score,
            importance=0.1,
            category="timing"
        ))
        
        return features
    
    def _calculate_hour_score(self, hour: int) -> float:
        """Calculate optimization score for hour of day"""
        # Peak hours: 9-11 AM, 2-4 PM, 7-9 PM
        peak_hours = [9, 10, 11, 14, 15, 16, 19, 20, 21]
        if hour in peak_hours:
            return 1.0
        elif hour in [8, 12, 13, 17, 18, 22]:
            return 0.7
        elif hour in [7, 23, 0]:
            return 0.3
        else:
            return 0.1  # Late night/early morning
    
    def _calculate_day_score(self, weekday: int) -> float:
        """
Calculate optimization score for day of week"""
        # Tuesday-Thursday are typically best, weekends vary by platform
        scores = {
            0: 0.7,  # Monday
            1: 1.0,  # Tuesday
            2: 1.0,  # Wednesday
            3: 1.0,  # Thursday
            4: 0.8,  # Friday
            5: 0.6,  # Saturday
            6: 0.5   # Sunday
        }
        return scores.get(weekday, 0.5)
    
    def _calculate_month_score(self, month: int) -> float:
        """
Calculate optimization score for month (seasonality)"""
        # Higher engagement typically in fall/winter
        scores = {
            1: 0.9,  # January
            2: 0.8,  # February
            3: 0.7,  # March
            4: 0.7,  # April
            5: 0.6,  # May
            6: 0.5,  # June
            7: 0.5,  # July
            8: 0.6,  # August
            9: 0.8,  # September
            10: 0.9, # October
            11: 1.0, # November
            12: 0.9  # December
        }
        return scores.get(month, 0.7)
    
    async def _extract_platform_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """
Extract platform-related features"""
        features = []
        
        if request.platforms:
            # Platform diversity score
            platform_count = len(request.platforms)
            diversity_score = min(1.0, platform_count / 6)  # Optimal ~6 platforms
            
            features.append(OptimizationFeature(
                name="platform_diversity",
                value=diversity_score,
                importance=0.2,
                category="platform"
            ))
            
            # Platform synergy score (how well platforms work together)
            synergy_score = self._calculate_platform_synergy(request.platforms)
            features.append(OptimizationFeature(
                name="platform_synergy",
                value=synergy_score,
                importance=0.15,
                category="platform"
            ))
            
            # High-performing platform presence
            high_perf_platforms = [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.TIKTOK]
            high_perf_count = len([p for p in request.platforms if p in high_perf_platforms])
            high_perf_score = high_perf_count / len(high_perf_platforms)
            
            features.append(OptimizationFeature(
                name="high_performance_platforms",
                value=high_perf_score,
                importance=0.25,
                category="platform"
            ))
        
        return features
    
    def _calculate_platform_synergy(self, platforms: List[PlatformType]) -> float:
        """Calculate how well platforms work together"""
        synergy_matrix = {
            # Platforms that work well together
            (PlatformType.YOUTUBE, PlatformType.INSTAGRAM): 0.9,
            (PlatformType.TIKTOK, PlatformType.INSTAGRAM): 0.8,
            (PlatformType.TWITTER, PlatformType.LINKEDIN): 0.7,
            (PlatformType.SPOTIFY, PlatformType.YOUTUBE): 0.9,
            (PlatformType.YOUTUBE, PlatformType.TIKTOK): 0.8,
        }
        
        if len(platforms) < 2:
            return 0.5
        
        total_synergy = 0
        pair_count = 0
        
        for i, platform1 in enumerate(platforms):
            for platform2 in platforms[i+1:]:
                synergy = synergy_matrix.get((platform1, platform2), 0.5)
                if synergy == 0.5:  # Try reverse order
                    synergy = synergy_matrix.get((platform2, platform1), 0.5)
                
                total_synergy += synergy
                pair_count += 1
        
        return total_synergy / pair_count if pair_count > 0 else 0.5
    
    async def _extract_audience_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """
Extract audience-related features"""
        features = []
        
        # Get user's historical audience data
        recent_analytics = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == request.user_id,
            DistributionAnalyticsModel.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if recent_analytics:
            # Audience engagement score
            total_reach = sum(
                record.metrics.get("reach", 0) if record.metrics else 0
                for record in recent_analytics
            )
            total_engagement = sum(
                record.metrics.get("engagement", 0) if record.metrics else 0
                for record in recent_analytics
            )
            
            engagement_rate = total_engagement / total_reach if total_reach > 0 else 0
            engagement_score = min(1.0, engagement_rate * 20)  # Scale to 0-1
            
            features.append(OptimizationFeature(
                name="audience_engagement_quality",
                value=engagement_score,
                importance=0.3,
                category="audience"
            ))
            
            # Audience growth rate
            if len(recent_analytics) > 7:
                early_period = recent_analytics[:len(recent_analytics)//2]
                late_period = recent_analytics[len(recent_analytics)//2:]
                
                early_avg_reach = np.mean([
                    record.metrics.get("reach", 0) if record.metrics else 0
                    for record in early_period
                ])
                late_avg_reach = np.mean([
                    record.metrics.get("reach", 0) if record.metrics else 0
                    for record in late_period
                ])
                
                growth_rate = (late_avg_reach - early_avg_reach) / early_avg_reach if early_avg_reach > 0 else 0
                growth_score = min(1.0, max(0.0, (growth_rate + 0.5)))  # Normalize around 0
                
                features.append(OptimizationFeature(
                    name="audience_growth_trend",
                    value=growth_score,
                    importance=0.2,
                    category="audience"
                ))
        
        return features
    
    async def _extract_historical_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """Extract historical performance features"""
        features = []
        
        # Get historical performance data
        historical_data = await self._get_historical_performance(request)
        
        if len(historical_data) > 5:
            # Performance consistency
            reaches = [record.metrics.get("reach", 0) if record.metrics else 0 for record in historical_data]
            if reaches:
                consistency_score = 1.0 - (np.std(reaches) / np.mean(reaches)) if np.mean(reaches) > 0 else 0.5
                consistency_score = max(0.0, min(1.0, consistency_score))
                
                features.append(OptimizationFeature(
                    name="performance_consistency",
                    value=consistency_score,
                    importance=0.15,
                    category="historical"
                ))
            
            # Best performing content type
            content_performance = {}
            for record in historical_data:
                if record.content_id:
                    content = self.db.query(ContentModel).filter(
                        ContentModel.id == record.content_id
                    ).first()
                    if content:
                        content_type = content.content_type.value
                        reach = record.metrics.get("reach", 0) if record.metrics else 0
                        
                        if content_type not in content_performance:
                            content_performance[content_type] = []
                        content_performance[content_type].append(reach)
            
            if content_performance:
                avg_performance = {
                    content_type: np.mean(reaches)
                    for content_type, reaches in content_performance.items()
                }
                
                best_type = max(avg_performance.items(), key=lambda x: x[1])
                best_performance_score = min(1.0, best_type[1] / 10000)  # Normalize
                
                features.append(OptimizationFeature(
                    name="best_content_type_performance",
                    value=best_performance_score,
                    importance=0.2,
                    category="historical"
                ))
        
        return features
    
    async def _extract_competitive_features(
        self, request: OptimizationRequest
    ) -> List[OptimizationFeature]:
        """Extract competitive landscape features"""
        # This would integrate with competitive analysis tools
        # For now, using estimated features
        
        features = [
            OptimizationFeature(
                name="market_saturation",
                value=0.6,  # Estimated market saturation
                importance=0.1,
                category="competitive"
            ),
            OptimizationFeature(
                name="trending_opportunity",
                value=0.7,  # Estimated trending opportunity
                importance=0.15,
                category="competitive"
            )
        ]
        
        return features
    
    async def _get_historical_performance(
        self, request: OptimizationRequest
    ) -> List[DistributionAnalyticsModel]:
        """Get historical performance data for analysis"""
        lookback_days = min(request.optimization_horizon * 3, 180)  # Max 6 months
        start_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        query = self.db.query(DistributionAnalyticsModel).filter(
            DistributionAnalyticsModel.user_id == request.user_id,
            DistributionAnalyticsModel.created_at >= start_date,
            DistributionAnalyticsModel.success == True
        )
        
        if request.platforms:
            platform_values = [p.value for p in request.platforms]
            query = query.filter(
                DistributionAnalyticsModel.platform.in_(platform_values)
            )
        
        return query.all()
    
    async def _update_models(
        self, historical_data: List[DistributionAnalyticsModel]
    ) -> None:
        """
Update ML models with recent data"""
        try:
            # Prepare training data
            X, y_reach, y_engagement, y_revenue = self._prepare_training_data(historical_data)
            
            if len(X) < 20:  # Minimum samples for training
                return
            
            # Split data
            X_train, X_test, y_reach_train, y_reach_test = train_test_split(
                X, y_reach, test_size=0.2, random_state=42
            )
            
            # Update reach predictor
            self.models["reach_predictor"].fit(X_train, y_reach_train)
            reach_score = self.models["reach_predictor"].score(X_test, y_reach_test)
            logger.info(f"Reach predictor R² score: {reach_score:.3f}")
            
            # Update engagement predictor
            if len(y_engagement) > 0:
                _, _, y_eng_train, y_eng_test = train_test_split(
                    X, y_engagement, test_size=0.2, random_state=42
                )
                self.models["engagement_predictor"].fit(X_train, y_eng_train)
                eng_score = self.models["engagement_predictor"].score(X_test, y_eng_test)
                logger.info(f"Engagement predictor R² score: {eng_score:.3f}")
            
            # Update revenue predictor
            if len(y_revenue) > 0 and sum(y_revenue) > 0:
                _, _, y_rev_train, y_rev_test = train_test_split(
                    X, y_revenue, test_size=0.2, random_state=42
                )
                self.models["revenue_predictor"].fit(X_train, y_rev_train)
                rev_score = self.models["revenue_predictor"].score(X_test, y_rev_test)
                logger.info(f"Revenue predictor R² score: {rev_score:.3f}")
            
            # Save updated models
            await self._save_models()
            
        except Exception as e:
            logger.error(f"Model update failed: {e}")
    
    def _prepare_training_data(
        self, historical_data: List[DistributionAnalyticsModel]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from historical analytics"""

        X = []
        y_reach = []
        y_engagement = []
        y_revenue = []
        
        for record in historical_data:
            # Extract features for this record
            features = self._extract_record_features(record)
            
            if features is not None:
                X.append(features)
                
                # Extract targets
                metrics = record.metrics or {}
                y_reach.append(metrics.get("reach", 0))
                y_engagement.append(metrics.get("engagement", 0))
                y_revenue.append(metrics.get("revenue", 0.0))
        
        return (
            np.array(X),
            np.array(y_reach),
            np.array(y_engagement),
            np.array(y_revenue)
        )
    
    def _extract_record_features(self, record: DistributionAnalyticsModel) -> Optional[List[float]]:
        """Extract feature vector from analytics record"""
        try:
            features = []
            
            # Platform encoding
            platform_encodings = {
                "youtube": [1, 0, 0, 0, 0, 0],
                "instagram": [0, 1, 0, 0, 0, 0],
                "tiktok": [0, 0, 1, 0, 0, 0],
                "twitter": [0, 0, 0, 1, 0, 0],
                "spotify": [0, 0, 0, 0, 1, 0],
                "linkedin": [0, 0, 0, 0, 0, 1]
            }
            
            platform_encoding = platform_encodings.get(record.platform, [0, 0, 0, 0, 0, 0])
            features.extend(platform_encoding)
            
            # Time features
            created_at = record.created_at
            features.extend([
                created_at.hour / 24.0,  # Hour of day (normalized)
                created_at.weekday() / 6.0,  # Day of week (normalized)
                created_at.month / 12.0,  # Month (normalized)
            ])
            
            # Content features (if available)
            if record.content_id:
                content = self.db.query(ContentModel).filter(
                    ContentModel.id == record.content_id
                ).first()
                
                if content:
                    # Content type encoding
                    content_type_encodings = {
                        ContentType.VIDEO: [1, 0, 0, 0],
                        ContentType.AUDIO: [0, 1, 0, 0],
                        ContentType.IMAGE: [0, 0, 1, 0],
                        ContentType.TEXT: [0, 0, 0, 1]
                    }
                    
                    content_encoding = content_type_encodings.get(
                        content.content_type, [0, 0, 0, 0]
                    )
                    features.extend(content_encoding)
                    
                    # Title and description lengths (normalized)
                    title_length = len(content.title) / 200.0 if content.title else 0
                    desc_length = len(content.description) / 1000.0 if content.description else 0
                    hashtag_count = len(content.hashtags) / 30.0 if content.hashtags else 0
                    
                    features.extend([title_length, desc_length, hashtag_count])
                else:
                    # Default content features
                    features.extend([0, 0, 0, 0, 0, 0, 0])
            else:
                # Default content features
                features.extend([0, 0, 0, 0, 0, 0, 0])
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed for record {record.id}: {e}")
            return None
    
    async def _save_models(self) -> None:
        """Save trained models to disk"""
        try:
            joblib.dump(self.models["reach_predictor"], "models/reach_optimization.pkl")
            joblib.dump(self.models["engagement_predictor"], "models/engagement_optimization.pkl")
            joblib.dump(self.models["revenue_predictor"], "models/revenue_optimization.pkl")
            joblib.dump(self.models["conversion_predictor"], "models/conversion_optimization.pkl")
            joblib.dump(self.models["feature_scaler"], "models/optimization_scaler.pkl")
            joblib.dump(self.models["label_encoder"], "models/optimization_encoder.pkl")
            
            logger.info("Optimization models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    # Optimization strategy implementations
    async def _optimize_for_reach(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for maximum reach"""
        
        # Calculate current baseline
        baseline_reach = self._calculate_baseline_reach(historical_data)
        
        # Feature importance for reach optimization
        reach_important_features = [
            "platform_diversity", "posting_hour_optimization", "content_quality",
            "high_performance_platforms", "audience_engagement_quality"
        ]
        
        # Generate recommendations
        recommendations = []
        feature_importance = []
        
        # Analyze features for optimization opportunities
        all_features = []
        for feature_list in features.values():
            all_features.extend(feature_list)
        
        for feature in all_features:
            if feature.name in reach_important_features:
                feature_importance.append(feature)
                
                if feature.value < 0.7:  # Room for improvement
                    if feature.name == "platform_diversity":
                        recommendations.append(
                            f"Expand to more platforms to increase reach diversity (current score: {feature.value:.2f})"
                        )
                    elif feature.name == "posting_hour_optimization":
                        recommendations.append(
                            f"Optimize posting times for peak audience hours (current score: {feature.value:.2f})"
                        )
                    elif feature.name == "content_quality":
                        recommendations.append(
                            f"Improve content quality with better resolution/production (current score: {feature.value:.2f})"
                        )
        
        # Predict improvement
        predicted_improvement = self._predict_reach_improvement(features, baseline_reach)
        confidence_score = self._calculate_confidence(historical_data, len(recommendations))
        
        optimal_parameters = {
            "recommended_platforms": 4,  # Optimal platform count for reach
            "posting_frequency": 2,  # Posts per day
            "content_types": ["video", "image"],  # Best for reach
            "optimal_times": [9, 14, 19]  # Peak hours
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]  # Will be populated later
        )
    
    async def _optimize_for_engagement(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for maximum engagement"""
        
        baseline_engagement = self._calculate_baseline_engagement(historical_data)
        
        engagement_important_features = [
            "content_quality", "hashtag_optimization", "audience_engagement_quality",
            "posting_hour_optimization", "platform_synergy"
        ]
        
        recommendations = []
        feature_importance = []
        
        all_features = []
        for feature_list in features.values():
            all_features.extend(feature_list)
        
        for feature in all_features:
            if feature.name in engagement_important_features:
                feature_importance.append(feature)
                
                if feature.value < 0.8:
                    if feature.name == "hashtag_optimization":
                        recommendations.append(
                            f"Optimize hashtag strategy for better discoverability (current score: {feature.value:.2f})"
                        )
                    elif feature.name == "content_quality":
                        recommendations.append(
                            f"Focus on high-quality, engaging content formats (current score: {feature.value:.2f})"
                        )
                    elif feature.name == "platform_synergy":
                        recommendations.append(
                            f"Choose platforms that work well together (current score: {feature.value:.2f})"
                        )
        
        predicted_improvement = self._predict_engagement_improvement(features, baseline_engagement)
        confidence_score = self._calculate_confidence(historical_data, len(recommendations))
        
        optimal_parameters = {
            "recommended_platforms": 3,  # Focus on fewer platforms for engagement
            "posting_frequency": 1.5,  # Slightly less frequent but higher quality
            "content_types": ["video", "interactive"],
            "engagement_tactics": ["questions", "polls", "behind_scenes"]
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]
        )
    
    async def _optimize_for_revenue(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for maximum revenue"""
        
        baseline_revenue = self._calculate_baseline_revenue(historical_data)
        
        revenue_important_features = [
            "content_quality", "platform_diversity", "audience_engagement_quality",
            "performance_consistency", "high_performance_platforms"
        ]
        
        recommendations = [
            "Focus on monetizable platforms like YouTube and Spotify",
            "Create longer-form content for better ad revenue",
            "Build consistent posting schedule to grow subscriber base",
            "Optimize for high-value demographics"
        ]
        
        feature_importance = []
        all_features = []
        for feature_list in features.values():
            all_features.extend(feature_list)
        
        for feature in all_features:
            if feature.name in revenue_important_features:
                feature_importance.append(feature)
        
        predicted_improvement = self._predict_revenue_improvement(features, baseline_revenue)
        confidence_score = self._calculate_confidence(historical_data, len(recommendations))
        
        optimal_parameters = {
            "monetization_platforms": ["youtube", "spotify", "instagram"],
            "content_length": "long_form",  # Better for monetization
            "audience_targeting": "high_value_demographics",
            "revenue_streams": ["ads", "sponsorships", "merchandise"]
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]
        )
    
    async def _optimize_for_conversion(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for conversion rates"""
        
        baseline_conversion = self._calculate_baseline_conversion(historical_data)
        
        recommendations = [
            "Include clear call-to-action in all posts",
            "Use compelling thumbnails and titles",
            "Target specific audience segments",
            "A/B test different messaging approaches"
        ]
        
        feature_importance = []
        predicted_improvement = baseline_conversion * 0.15  # 15% improvement estimate
        confidence_score = 0.7
        
        optimal_parameters = {
            "cta_placement": "early_and_end",
            "targeting": "lookalike_audiences",
            "content_format": "short_video_with_hook"
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]
        )
    
    async def _optimize_for_cost(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for cost efficiency"""
        
        recommendations = [
            "Focus on organic reach strategies",
            "Use free platform features effectively",
            "Optimize posting times to reduce promoted post needs",
            "Leverage user-generated content"
        ]
        
        feature_importance = []
        predicted_improvement = 0.25  # 25% cost reduction estimate
        confidence_score = 0.8
        
        optimal_parameters = {
            "budget_allocation": "organic_first",
            "content_strategy": "user_generated",
            "platform_selection": "high_organic_reach"
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]
        )
    
    async def _optimize_for_balance(
        self,
        request: OptimizationRequest,
        features: Dict[str, List[OptimizationFeature]],
        historical_data: List[DistributionAnalyticsModel]
    ) -> OptimizationResult:
        """Optimize for balanced performance across all metrics"""
        
        recommendations = [
            "Balance reach and engagement with strategic platform mix",
            "Maintain consistent posting schedule across platforms",
            "Diversify content types to maximize different metrics",
            "Monitor and adjust strategy based on performance data"
        ]
        
        feature_importance = []
        predicted_improvement = 0.12  # 12% balanced improvement
        confidence_score = 0.75
        
        optimal_parameters = {
            "platform_mix": "balanced_portfolio",
            "content_strategy": "diversified",
            "optimization_approach": "multi_objective"
        }
        
        return OptimizationResult(
            goal=request.goal,
            predicted_improvement=predicted_improvement,
            confidence_score=confidence_score,
            recommendations=recommendations,
            feature_importance=feature_importance,
            optimal_parameters=optimal_parameters,
            a_b_test_suggestions=[]
        )
    
    # Helper methods for calculations
    def _calculate_baseline_reach(self, historical_data: List[DistributionAnalyticsModel]) -> float:
        """Calculate baseline reach from historical data"""
        if not historical_data:
            return 1000.0  # Default baseline
        
        reaches = [
            record.metrics.get("reach", 0) if record.metrics else 0
            for record in historical_data[-10:]  # Last 10 posts
        ]
        
        return np.mean(reaches) if reaches else 1000.0
    
    def _calculate_baseline_engagement(self, historical_data: List[DistributionAnalyticsModel]) -> float:
        """Calculate baseline engagement from historical data"""
        if not historical_data:
            return 50.0  # Default baseline
        
        engagements = [
            record.metrics.get("engagement", 0) if record.metrics else 0
            for record in historical_data[-10:]
        ]
        
        return np.mean(engagements) if engagements else 50.0
    
    def _calculate_baseline_revenue(self, historical_data: List[DistributionAnalyticsModel]) -> float:
        """Calculate baseline revenue from historical data"""
        if not historical_data:
            return 10.0  # Default baseline
        
        revenues = [
            record.metrics.get("revenue", 0.0) if record.metrics else 0.0
            for record in historical_data[-10:]
        ]
        
        return np.mean(revenues) if revenues else 10.0
    
    def _calculate_baseline_conversion(self, historical_data: List[DistributionAnalyticsModel]) -> float:
        """Calculate baseline conversion from historical data"""
        if not historical_data:
            return 0.02  # Default 2% conversion
        
        total_clicks = sum(
            record.metrics.get("clicks", 0) if record.metrics else 0
            for record in historical_data[-10:]
        )
        total_reach = sum(
            record.metrics.get("reach", 0) if record.metrics else 0
            for record in historical_data[-10:]
        )
        
        return total_clicks / total_reach if total_reach > 0 else 0.02
    
    def _predict_reach_improvement(
        self, features: Dict[str, List[OptimizationFeature]], baseline: float
    ) -> float:
        """Predict reach improvement based on features"""
        # Simplified prediction based on feature scores
        improvement_factors = []
        
        for feature_list in features.values():
            for feature in feature_list:
                if feature.name in ["platform_diversity", "content_quality", "posting_hour_optimization"]:
                    # Room for improvement is inverse of current score
                    improvement_potential = (1.0 - feature.value) * feature.importance
                    improvement_factors.append(improvement_potential)
        
        total_improvement = sum(improvement_factors)
        predicted_improvement = baseline * total_improvement * 0.5  # Conservative estimate
        
        return predicted_improvement
    
    def _predict_engagement_improvement(
        self, features: Dict[str, List[OptimizationFeature]], baseline: float
    ) -> float:
        """Predict engagement improvement based on features"""
        improvement_factors = []
        
        for feature_list in features.values():
            for feature in feature_list:
                if feature.name in ["content_quality", "hashtag_optimization", "audience_engagement_quality"]:
                    improvement_potential = (1.0 - feature.value) * feature.importance
                    improvement_factors.append(improvement_potential)
        
        total_improvement = sum(improvement_factors)
        predicted_improvement = baseline * total_improvement * 0.4
        
        return predicted_improvement
    
    def _predict_revenue_improvement(
        self, features: Dict[str, List[OptimizationFeature]], baseline: float
    ) -> float:
        """Predict revenue improvement based on features"""
        # Revenue optimization typically has higher potential
        improvement_factors = []
        
        for feature_list in features.values():
            for feature in feature_list:
                if feature.name in ["content_quality", "platform_diversity", "high_performance_platforms"]:
                    improvement_potential = (1.0 - feature.value) * feature.importance
                    improvement_factors.append(improvement_potential)
        
        total_improvement = sum(improvement_factors)
        predicted_improvement = baseline * total_improvement * 0.8  # Higher potential for revenue
        
        return predicted_improvement
    
    def _calculate_confidence(
        self, historical_data: List[DistributionAnalyticsModel], recommendation_count: int
    ) -> float:
        """Calculate confidence score for optimization"""
        # Base confidence on data availability and recommendation specificity
        data_confidence = min(1.0, len(historical_data) / 50)  # More data = higher confidence
        recommendation_confidence = min(1.0, recommendation_count / 5)  # More specific recommendations
        
        return (data_confidence + recommendation_confidence) / 2
    
    async def _generate_ab_test_suggestions(
        self, request: OptimizationRequest, optimization_result: OptimizationResult
    ) -> List[Dict[str, Any]]:
        """
Generate A/B test suggestions based on optimization results"""
        suggestions = []
        
        # Test different posting times
        suggestions.append({
            "test_name": "Optimal Posting Time",
            "description": "Test posting at peak vs. off-peak hours",
            "variant_a": "Post during identified peak hours",
            "variant_b": "Post during current schedule",
            "metric_to_measure": "engagement_rate",
            "duration_days": 14,
            "expected_lift": "15-25%"
        })
        
        # Test content formats
        if "content_quality" in [f.name for f in optimization_result.feature_importance]:
            suggestions.append({
                "test_name": "Content Format Optimization",
                "description": "Test high-quality vs. standard content production",
                "variant_a": "High-production quality content",
                "variant_b": "Standard quality content",
                "metric_to_measure": "reach",
                "duration_days": 21,
                "expected_lift": "20-30%"
            })
        
        # Test platform mix
        if len(request.platforms or []) > 2:
            suggestions.append({
                "test_name": "Platform Strategy",
                "description": "Test focused vs. diversified platform approach",
                "variant_a": "Focus on top 2 performing platforms",
                "variant_b": "Distribute across all platforms",
                "metric_to_measure": "total_reach",
                "duration_days": 30,
                "expected_lift": "10-20%"
            })
        
        return suggestions
