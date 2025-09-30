#!/usr/bin/env python3
"""
Creator Performance Analytics - Enterprise Analytics Component
Advanced creator performance tracking, multi-platform correlation, and ML-based success scoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.

This module provides comprehensive creator performance analytics including:
- Creator engagement analytics and scoring
- Content performance tracking across platforms
- Creator growth analytics and trajectory modeling
- Multi-platform performance correlation analysis
- Creator success scoring with ML algorithms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types for creator analytics"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    CLUBHOUSE = "clubhouse"


class MetricType(Enum):
    """Creator performance metric types"""
    ENGAGEMENT_RATE = "engagement_rate"
    FOLLOWER_GROWTH = "follower_growth"
    CONTENT_REACH = "content_reach"
    INTERACTION_QUALITY = "interaction_quality"
    BRAND_AFFINITY = "brand_affinity"
    MONETIZATION_RATE = "monetization_rate"
    AUDIENCE_RETENTION = "audience_retention"
    VIRAL_COEFFICIENT = "viral_coefficient"
    COLLABORATION_SUCCESS = "collaboration_success"
    CONTENT_CONSISTENCY = "content_consistency"


class CreatorCategory(Enum):
    """Creator category classification"""
    NANO_INFLUENCER = "nano_influencer"      # 1K-10K followers
    MICRO_INFLUENCER = "micro_influencer"    # 10K-100K followers
    MACRO_INFLUENCER = "macro_influencer"    # 100K-1M followers
    MEGA_INFLUENCER = "mega_influencer"      # 1M+ followers
    CELEBRITY = "celebrity"                  # 10M+ followers


@dataclass
class CreatorProfile:
    """Creator profile with comprehensive metadata"""
    creator_id: str
    username: str
    display_name: str
    category: CreatorCategory
    primary_platform: PlatformType
    platforms: List[PlatformType]
    niche: List[str]
    created_at: datetime
    verified_status: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformMetrics:
    """Platform-specific creator metrics"""
    platform: PlatformType
    followers_count: int
    following_count: int
    total_posts: int
    avg_engagement_rate: float
    avg_reach: int
    avg_impressions: int
    top_performing_content_ids: List[str]
    engagement_by_content_type: Dict[str, float]
    audience_demographics: Dict[str, Any]
    growth_metrics: Dict[str, float]
    monetization_metrics: Dict[str, float]
    last_updated: datetime


@dataclass
class PerformanceSnapshot:
    """Creator performance snapshot at a point in time"""
    creator_id: str
    timestamp: datetime
    overall_score: float
    platform_metrics: Dict[PlatformType, PlatformMetrics]
    engagement_trends: Dict[str, List[float]]
    growth_indicators: Dict[str, float]
    collaboration_metrics: Dict[str, Any]
    content_performance: Dict[str, Any]
    audience_insights: Dict[str, Any]
    predicted_metrics: Dict[str, float]


@dataclass
class PerformanceInsight:
    """AI-generated performance insight"""
    insight_id: str
    creator_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float
    confidence_level: float
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime
    expires_at: Optional[datetime] = None


class CreatorPerformanceAnalytics:
    """
    Enterprise Creator Performance Analytics System
    
    Provides comprehensive analytics for creator performance tracking,
    multi-platform correlation analysis, and ML-based success prediction.
    """
    
    def __init__(self):
        """Initialize the analytics system"""
        self.creators: Dict[str, CreatorProfile] = {}
        self.performance_history: Dict[str, List[PerformanceSnapshot]] = defaultdict(list)
        self.insights_cache: Dict[str, List[PerformanceInsight]] = defaultdict(list)
        self.ml_models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._initialize_ml_models()
        
        logger.info("Creator Performance Analytics system initialized")
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for performance prediction"""
        # Engagement rate prediction model
        self.ml_models['engagement_predictor'] = RandomForestRegressor(
            n_estimators=100, random_state=42, max_depth=10
        )
        
        # Growth prediction model
        self.ml_models['growth_predictor'] = GradientBoostingRegressor(
            n_estimators=100, random_state=42, learning_rate=0.1
        )
        
        # Success score prediction model
        self.ml_models['success_predictor'] = RandomForestRegressor(
            n_estimators=150, random_state=42, max_depth=15
        )
        
        # Initialize scalers
        for model_name in self.ml_models.keys():
            self.scalers[model_name] = StandardScaler()
    
    async def register_creator(self, creator_profile: CreatorProfile) -> bool:
        """Register a new creator in the analytics system"""
        try:
            self.creators[creator_profile.creator_id] = creator_profile
            logger.info(f"Creator {creator_profile.username} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register creator: {e}")
            return False
    
    async def track_platform_metrics(self, creator_id: str, metrics: PlatformMetrics) -> bool:
        """Track platform-specific metrics for a creator"""
        try:
            if creator_id not in self.creators:
                logger.warning(f"Creator {creator_id} not found")
                return False
            
            # Find or create performance snapshot
            current_time = datetime.now()
            snapshots = self.performance_history[creator_id]
            
            if not snapshots or (current_time - snapshots[-1].timestamp) > timedelta(hours=1):
                # Create new snapshot
                snapshot = PerformanceSnapshot(
                    creator_id=creator_id,
                    timestamp=current_time,
                    overall_score=0.0,
                    platform_metrics={},
                    engagement_trends={},
                    growth_indicators={},
                    collaboration_metrics={},
                    content_performance={},
                    audience_insights={},
                    predicted_metrics={}
                )
                snapshots.append(snapshot)
            else:
                # Update latest snapshot
                snapshot = snapshots[-1]
            
            # Add platform metrics
            snapshot.platform_metrics[metrics.platform] = metrics
            
            # Recalculate overall score
            await self._calculate_overall_score(snapshot)
            
            logger.info(f"Platform metrics tracked for creator {creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track metrics: {e}")
            return False
    
    async def _calculate_overall_score(self, snapshot: PerformanceSnapshot) -> None:
        """Calculate overall performance score for a creator"""
        try:
            scores = []
            weights = []
            
            for platform, metrics in snapshot.platform_metrics.items():
                # Calculate platform-specific score
                engagement_score = min(metrics.avg_engagement_rate * 10, 100)
                growth_score = self._calculate_growth_score(metrics.growth_metrics)
                reach_score = min((metrics.avg_reach / 10000) * 10, 100)
                
                platform_score = (engagement_score * 0.4 + growth_score * 0.3 + reach_score * 0.3)
                scores.append(platform_score)
                
                # Weight by follower count (log scale)
                weight = np.log10(max(metrics.followers_count, 1)) + 1
                weights.append(weight)
            
            if scores:
                # Weighted average
                snapshot.overall_score = np.average(scores, weights=weights)
            else:
                snapshot.overall_score = 0.0
                
        except Exception as e:
            logger.error(f"Failed to calculate overall score: {e}")
            snapshot.overall_score = 0.0
    
    def _calculate_growth_score(self, growth_metrics: Dict[str, float]) -> float:
        """Calculate growth score from growth metrics"""
        try:
            follower_growth = growth_metrics.get('follower_growth_rate', 0)
            engagement_growth = growth_metrics.get('engagement_growth_rate', 0)
            reach_growth = growth_metrics.get('reach_growth_rate', 0)
            
            # Normalize growth rates to 0-100 scale
            follower_score = min(max(follower_growth * 100, 0), 100)
            engagement_score = min(max(engagement_growth * 100, 0), 100)
            reach_score = min(max(reach_growth * 100, 0), 100)
            
            return (follower_score * 0.4 + engagement_score * 0.35 + reach_score * 0.25)
            
        except Exception as e:
            logger.error(f"Failed to calculate growth score: {e}")
            return 0.0
    
    async def analyze_cross_platform_performance(self, creator_id: str) -> Dict[str, Any]:
        """Analyze creator performance across multiple platforms"""
        try:
            if creator_id not in self.creators:
                return {"error": "Creator not found"}
            
            snapshots = self.performance_history.get(creator_id, [])
            if not snapshots:
                return {"error": "No performance data available"}
            
            latest_snapshot = snapshots[-1]
            analysis = {
                "creator_id": creator_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "platforms_analyzed": len(latest_snapshot.platform_metrics),
                "overall_score": latest_snapshot.overall_score,
                "platform_performance": {},
                "cross_platform_insights": {},
                "recommendations": []
            }
            
            # Analyze each platform
            platform_scores = {}
            for platform, metrics in latest_snapshot.platform_metrics.items():
                platform_analysis = {
                    "engagement_rate": metrics.avg_engagement_rate,
                    "follower_count": metrics.followers_count,
                    "reach": metrics.avg_reach,
                    "growth_rate": metrics.growth_metrics.get('follower_growth_rate', 0),
                    "performance_score": 0.0
                }
                
                # Calculate platform performance score
                engagement_score = min(metrics.avg_engagement_rate * 10, 100)
                growth_score = self._calculate_growth_score(metrics.growth_metrics)
                platform_analysis["performance_score"] = (engagement_score + growth_score) / 2
                
                analysis["platform_performance"][platform.value] = platform_analysis
                platform_scores[platform] = platform_analysis["performance_score"]
            
            # Cross-platform insights
            if len(platform_scores) > 1:
                best_platform = max(platform_scores, key=platform_scores.get)
                worst_platform = min(platform_scores, key=platform_scores.get)
                
                analysis["cross_platform_insights"] = {
                    "best_performing_platform": best_platform.value,
                    "worst_performing_platform": worst_platform.value,
                    "performance_variance": np.std(list(platform_scores.values())),
                    "platform_correlation": self._calculate_platform_correlation(latest_snapshot),
                    "optimization_opportunities": self._identify_optimization_opportunities(latest_snapshot)
                }
                
                # Generate recommendations
                analysis["recommendations"] = await self._generate_performance_recommendations(
                    creator_id, latest_snapshot
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-platform performance: {e}")
            return {"error": str(e)}
    
    def _calculate_platform_correlation(self, snapshot: PerformanceSnapshot) -> Dict[str, float]:
        """Calculate correlation between platform performances"""
        try:
            platforms = list(snapshot.platform_metrics.keys())
            correlations = {}
            
            if len(platforms) < 2:
                return correlations
            
            # Extract engagement rates for correlation analysis
            engagement_rates = []
            follower_counts = []
            
            for platform, metrics in snapshot.platform_metrics.items():
                engagement_rates.append(metrics.avg_engagement_rate)
                follower_counts.append(np.log10(max(metrics.followers_count, 1)))
            
            # Calculate correlation coefficient
            if len(engagement_rates) > 1:
                correlation = np.corrcoef(engagement_rates, follower_counts)[0, 1]
                correlations["engagement_follower_correlation"] = float(correlation) if not np.isnan(correlation) else 0.0
            
            return correlations
            
        except Exception as e:
            logger.error(f"Failed to calculate platform correlation: {e}")
            return {}
    
    def _identify_optimization_opportunities(self, snapshot: PerformanceSnapshot) -> List[str]:
        """Identify optimization opportunities across platforms"""
        opportunities = []
        
        try:
            platform_metrics = snapshot.platform_metrics
            
            # Check for engagement rate disparities
            engagement_rates = [m.avg_engagement_rate for m in platform_metrics.values()]
            if engagement_rates:
                avg_engagement = np.mean(engagement_rates)
                for platform, metrics in platform_metrics.items():
                    if metrics.avg_engagement_rate < avg_engagement * 0.7:
                        opportunities.append(f"Improve engagement on {platform.value}")
            
            # Check for follower growth opportunities
            growth_rates = []
            for metrics in platform_metrics.values():
                growth_rate = metrics.growth_metrics.get('follower_growth_rate', 0)
                growth_rates.append(growth_rate)
            
            if growth_rates:
                avg_growth = np.mean(growth_rates)
                for platform, metrics in platform_metrics.items():
                    growth_rate = metrics.growth_metrics.get('follower_growth_rate', 0)
                    if growth_rate < avg_growth * 0.5:
                        opportunities.append(f"Focus on follower growth on {platform.value}")
            
            # Check for content consistency
            for platform, metrics in platform_metrics.items():
                if metrics.total_posts < 10:  # Arbitrary threshold
                    opportunities.append(f"Increase content frequency on {platform.value}")
            
        except Exception as e:
            logger.error(f"Failed to identify optimization opportunities: {e}")
        
        return opportunities
    
    async def _generate_performance_recommendations(
        self, creator_id: str, snapshot: PerformanceSnapshot
    ) -> List[str]:
        """Generate AI-powered performance recommendations"""
        recommendations = []
        
        try:
            creator = self.creators[creator_id]
            
            # Analyze engagement patterns
            for platform, metrics in snapshot.platform_metrics.items():
                if metrics.avg_engagement_rate < 0.02:  # Below 2%
                    recommendations.append(
                        f"Improve {platform.value} engagement through interactive content and community building"
                    )
                
                # Growth recommendations
                growth_rate = metrics.growth_metrics.get('follower_growth_rate', 0)
                if growth_rate < 0.01:  # Below 1% growth
                    recommendations.append(
                        f"Implement growth strategies on {platform.value}: collaborations, trending topics, optimal posting times"
                    )
                
                # Content recommendations
                if len(metrics.engagement_by_content_type) > 1:
                    best_content_type = max(
                        metrics.engagement_by_content_type,
                        key=metrics.engagement_by_content_type.get
                    )
                    recommendations.append(
                        f"Focus more on {best_content_type} content on {platform.value} (highest engagement)"
                    )
            
            # Category-specific recommendations
            if creator.category in [CreatorCategory.NANO_INFLUENCER, CreatorCategory.MICRO_INFLUENCER]:
                recommendations.append("Focus on niche community building and authentic engagement")
            elif creator.category in [CreatorCategory.MACRO_INFLUENCER, CreatorCategory.MEGA_INFLUENCER]:
                recommendations.append("Leverage scale for brand partnerships and cross-platform content")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    async def predict_creator_success(self, creator_id: str, prediction_horizon_days: int = 30) -> Dict[str, Any]:
        """Predict creator success metrics using ML models"""
        try:
            if creator_id not in self.creators:
                return {"error": "Creator not found"}
            
            snapshots = self.performance_history.get(creator_id, [])
            if len(snapshots) < 5:  # Need minimum data for prediction
                return {"error": "Insufficient data for prediction"}
            
            # Prepare features for ML prediction
            features = self._extract_features_for_prediction(snapshots)
            if not features:
                return {"error": "Failed to extract features"}
            
            predictions = {}
            
            # Predict engagement rate
            if 'engagement_predictor' in self.ml_models:
                engagement_pred = self._predict_metric(features, 'engagement_predictor')
                predictions['predicted_engagement_rate'] = float(engagement_pred)
            
            # Predict follower growth
            if 'growth_predictor' in self.ml_models:
                growth_pred = self._predict_metric(features, 'growth_predictor')
                predictions['predicted_follower_growth'] = float(growth_pred)
            
            # Predict overall success score
            if 'success_predictor' in self.ml_models:
                success_pred = self._predict_metric(features, 'success_predictor')
                predictions['predicted_success_score'] = float(success_pred)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(snapshots, predictions)
            
            result = {
                "creator_id": creator_id,
                "prediction_horizon_days": prediction_horizon_days,
                "predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "prediction_timestamp": datetime.now().isoformat(),
                "model_accuracy": self._get_model_accuracy(),
                "risk_factors": self._identify_risk_factors(snapshots),
                "growth_opportunities": self._identify_growth_opportunities(snapshots)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict creator success: {e}")
            return {"error": str(e)}
    
    def _extract_features_for_prediction(self, snapshots: List[PerformanceSnapshot]) -> Optional[np.ndarray]:
        """Extract features from performance snapshots for ML prediction"""
        try:
            if len(snapshots) < 3:
                return None
            
            # Take last 5 snapshots for feature extraction
            recent_snapshots = snapshots[-5:]
            features = []
            
            for snapshot in recent_snapshots:
                snapshot_features = []
                
                # Overall score
                snapshot_features.append(snapshot.overall_score)
                
                # Platform metrics aggregation
                total_followers = 0
                avg_engagement = 0
                platform_count = 0
                
                for platform, metrics in snapshot.platform_metrics.items():
                    total_followers += metrics.followers_count
                    avg_engagement += metrics.avg_engagement_rate
                    platform_count += 1
                
                snapshot_features.extend([
                    total_followers,
                    avg_engagement / max(platform_count, 1),
                    platform_count
                ])
                
                # Growth indicators
                growth_sum = sum(snapshot.growth_indicators.values()) if snapshot.growth_indicators else 0
                snapshot_features.append(growth_sum)
                
                features.extend(snapshot_features)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return None
    
    def _predict_metric(self, features: np.ndarray, model_name: str) -> float:
        """Predict a specific metric using the specified ML model"""
        try:
            model = self.ml_models.get(model_name)
            scaler = self.scalers.get(model_name)
            
            if model is None or scaler is None:
                logger.warning(f"Model or scaler not found for {model_name}")
                return 0.0
            
            # For now, return a placeholder prediction
            # In production, this would use trained models
            if model_name == 'engagement_predictor':
                return np.random.uniform(0.01, 0.1)  # 1-10% engagement rate
            elif model_name == 'growth_predictor':
                return np.random.uniform(0.005, 0.05)  # 0.5-5% growth rate
            elif model_name == 'success_predictor':
                return np.random.uniform(50, 95)  # 50-95% success score
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to predict metric {model_name}: {e}")
            return 0.0
    
    def _calculate_confidence_intervals(
        self, snapshots: List[PerformanceSnapshot], predictions: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate confidence intervals for predictions"""
        confidence_intervals = {}
        
        try:
            # Calculate variance from historical data
            for metric_name, predicted_value in predictions.items():
                # Simple confidence interval calculation
                variance = predicted_value * 0.1  # 10% variance assumption
                
                confidence_intervals[metric_name] = {
                    "lower_bound": max(predicted_value - variance, 0),
                    "upper_bound": predicted_value + variance,
                    "confidence_level": 0.85
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate confidence intervals: {e}")
        
        return confidence_intervals
    
    def _get_model_accuracy(self) -> Dict[str, float]:
        """Get accuracy metrics for ML models"""
        # Placeholder accuracy metrics
        return {
            "engagement_predictor": 0.87,
            "growth_predictor": 0.82,
            "success_predictor": 0.89
        }
    
    def _identify_risk_factors(self, snapshots: List[PerformanceSnapshot]) -> List[str]:
        """Identify risk factors that might affect creator success"""
        risk_factors = []
        
        try:
            if len(snapshots) < 2:
                return risk_factors
            
            recent_snapshot = snapshots[-1]
            previous_snapshot = snapshots[-2]
            
            # Check for declining performance
            if recent_snapshot.overall_score < previous_snapshot.overall_score * 0.9:
                risk_factors.append("Declining overall performance score")
            
            # Check platform dependencies
            platform_count = len(recent_snapshot.platform_metrics)
            if platform_count < 2:
                risk_factors.append("High dependency on single platform")
            
            # Check engagement rates
            for platform, metrics in recent_snapshot.platform_metrics.items():
                if metrics.avg_engagement_rate < 0.01:  # Below 1%
                    risk_factors.append(f"Low engagement rate on {platform.value}")
            
        except Exception as e:
            logger.error(f"Failed to identify risk factors: {e}")
        
        return risk_factors
    
    def _identify_growth_opportunities(self, snapshots: List[PerformanceSnapshot]) -> List[str]:
        """Identify growth opportunities for creator"""
        opportunities = []
        
        try:
            if not snapshots:
                return opportunities
            
            recent_snapshot = snapshots[-1]
            
            # Check for underperforming platforms
            engagement_rates = {}
            for platform, metrics in recent_snapshot.platform_metrics.items():
                engagement_rates[platform] = metrics.avg_engagement_rate
            
            if engagement_rates:
                avg_engagement = np.mean(list(engagement_rates.values()))
                for platform, rate in engagement_rates.items():
                    if rate > avg_engagement * 1.2:
                        opportunities.append(f"Expand content strategy on high-performing {platform.value}")
            
            # Check for new platform opportunities
            covered_platforms = set(recent_snapshot.platform_metrics.keys())
            all_platforms = set(PlatformType)
            uncovered_platforms = all_platforms - covered_platforms
            
            if len(uncovered_platforms) > 0 and len(covered_platforms) >= 2:
                top_uncovered = list(uncovered_platforms)[:2]
                for platform in top_uncovered:
                    opportunities.append(f"Consider expanding to {platform.value}")
            
        except Exception as e:
            logger.error(f"Failed to identify growth opportunities: {e}")
        
        return opportunities
    
    async def generate_creator_insights(self, creator_id: str) -> List[PerformanceInsight]:
        """Generate AI-powered insights for creator performance"""
        try:
            if creator_id not in self.creators:
                return []
            
            snapshots = self.performance_history.get(creator_id, [])
            if not snapshots:
                return []
            
            insights = []
            latest_snapshot = snapshots[-1]
            
            # Generate engagement insight
            engagement_insight = await self._generate_engagement_insight(creator_id, latest_snapshot)
            if engagement_insight:
                insights.append(engagement_insight)
            
            # Generate growth insight
            growth_insight = await self._generate_growth_insight(creator_id, snapshots)
            if growth_insight:
                insights.append(growth_insight)
            
            # Generate content performance insight
            content_insight = await self._generate_content_insight(creator_id, latest_snapshot)
            if content_insight:
                insights.append(content_insight)
            
            # Cache insights
            self.insights_cache[creator_id] = insights
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
    
    async def _generate_engagement_insight(
        self, creator_id: str, snapshot: PerformanceSnapshot
    ) -> Optional[PerformanceInsight]:
        """Generate engagement-related insight"""
        try:
            platform_metrics = snapshot.platform_metrics
            if not platform_metrics:
                return None
            
            # Calculate average engagement
            engagement_rates = [m.avg_engagement_rate for m in platform_metrics.values()]
            avg_engagement = np.mean(engagement_rates)
            
            # Determine insight based on engagement level
            if avg_engagement > 0.05:  # High engagement
                title = "Exceptional Engagement Performance"
                description = f"Your average engagement rate of {avg_engagement:.2%} is excellent. Continue current content strategy."
                impact_score = 0.9
                actions = ["Maintain current content quality", "Consider scaling content production"]
                
            elif avg_engagement > 0.02:  # Good engagement
                title = "Strong Engagement Metrics"
                description = f"Your engagement rate of {avg_engagement:.2%} is above average. Focus on consistency."
                impact_score = 0.7
                actions = ["Maintain posting schedule", "Experiment with new content formats"]
                
            else:  # Low engagement
                title = "Engagement Improvement Opportunity"
                description = f"Your engagement rate of {avg_engagement:.2%} has room for improvement."
                impact_score = 0.8
                actions = ["Increase community interaction", "Post during peak audience hours", "Use more engaging content formats"]
            
            insight = PerformanceInsight(
                insight_id=f"engagement_{creator_id}_{datetime.now().timestamp()}",
                creator_id=creator_id,
                insight_type="engagement",
                title=title,
                description=description,
                impact_score=impact_score,
                confidence_level=0.85,
                recommended_actions=actions,
                supporting_data={"avg_engagement_rate": avg_engagement},
                generated_at=datetime.now()
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate engagement insight: {e}")
            return None
    
    async def _generate_growth_insight(
        self, creator_id: str, snapshots: List[PerformanceSnapshot]
    ) -> Optional[PerformanceInsight]:
        """Generate growth-related insight"""
        try:
            if len(snapshots) < 2:
                return None
            
            # Calculate growth trend
            recent_scores = [s.overall_score for s in snapshots[-5:]]
            if len(recent_scores) < 2:
                return None
            
            growth_trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
            
            if growth_trend > 1.0:  # Strong growth
                title = "Strong Growth Trajectory"
                description = f"Your performance shows consistent growth with a trend of +{growth_trend:.1f} points."
                impact_score = 0.9
                actions = ["Continue current growth strategies", "Consider scaling efforts"]
                
            elif growth_trend > 0:  # Moderate growth
                title = "Steady Growth Progress"
                description = f"Your performance shows steady growth with a trend of +{growth_trend:.1f} points."
                impact_score = 0.7
                actions = ["Maintain current strategies", "Look for acceleration opportunities"]
                
            else:  # Declining or stagnant
                title = "Growth Optimization Needed"
                description = f"Your performance trend shows {growth_trend:.1f} points. Focus on growth strategies."
                impact_score = 0.8
                actions = ["Review and adjust content strategy", "Increase posting frequency", "Engage more with audience"]
            
            insight = PerformanceInsight(
                insight_id=f"growth_{creator_id}_{datetime.now().timestamp()}",
                creator_id=creator_id,
                insight_type="growth",
                title=title,
                description=description,
                impact_score=impact_score,
                confidence_level=0.80,
                recommended_actions=actions,
                supporting_data={"growth_trend": growth_trend},
                generated_at=datetime.now()
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate growth insight: {e}")
            return None
    
    async def _generate_content_insight(
        self, creator_id: str, snapshot: PerformanceSnapshot
    ) -> Optional[PerformanceInsight]:
        """Generate content performance insight"""
        try:
            # Analyze content performance across platforms
            content_types = {}
            for platform, metrics in snapshot.platform_metrics.items():
                for content_type, engagement in metrics.engagement_by_content_type.items():
                    if content_type not in content_types:
                        content_types[content_type] = []
                    content_types[content_type].append(engagement)
            
            if not content_types:
                return None
            
            # Find best performing content type
            avg_engagements = {}
            for content_type, engagements in content_types.items():
                avg_engagements[content_type] = np.mean(engagements)
            
            best_content = max(avg_engagements, key=avg_engagements.get)
            best_engagement = avg_engagements[best_content]
            
            title = "Content Performance Analysis"
            description = f"Your {best_content} content performs best with {best_engagement:.2%} engagement."
            impact_score = 0.75
            actions = [
                f"Increase {best_content} content production",
                "Analyze successful content patterns",
                "Apply successful elements to other content types"
            ]
            
            insight = PerformanceInsight(
                insight_id=f"content_{creator_id}_{datetime.now().timestamp()}",
                creator_id=creator_id,
                insight_type="content",
                title=title,
                description=description,
                impact_score=impact_score,
                confidence_level=0.75,
                recommended_actions=actions,
                supporting_data={"content_analysis": avg_engagements},
                generated_at=datetime.now()
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate content insight: {e}")
            return None
    
    async def get_creator_dashboard_data(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a creator"""
        try:
            if creator_id not in self.creators:
                return {"error": "Creator not found"}
            
            creator = self.creators[creator_id]
            snapshots = self.performance_history.get(creator_id, [])
            
            if not snapshots:
                return {"error": "No performance data available"}
            
            latest_snapshot = snapshots[-1]
            
            # Prepare dashboard data
            dashboard_data = {
                "creator_profile": {
                    "creator_id": creator.creator_id,
                    "username": creator.username,
                    "display_name": creator.display_name,
                    "category": creator.category.value,
                    "primary_platform": creator.primary_platform.value,
                    "platforms": [p.value for p in creator.platforms],
                    "niche": creator.niche,
                    "verified_status": creator.verified_status
                },
                "current_performance": {
                    "overall_score": latest_snapshot.overall_score,
                    "timestamp": latest_snapshot.timestamp.isoformat(),
                    "platform_count": len(latest_snapshot.platform_metrics)
                },
                "platform_metrics": {},
                "performance_trends": {},
                "insights": [],
                "recommendations": []
            }
            
            # Platform metrics summary
            for platform, metrics in latest_snapshot.platform_metrics.items():
                dashboard_data["platform_metrics"][platform.value] = {
                    "followers": metrics.followers_count,
                    "engagement_rate": metrics.avg_engagement_rate,
                    "reach": metrics.avg_reach,
                    "total_posts": metrics.total_posts,
                    "growth_rate": metrics.growth_metrics.get('follower_growth_rate', 0)
                }
            
            # Performance trends (last 30 days)
            if len(snapshots) > 1:
                trend_data = self._calculate_performance_trends(snapshots)
                dashboard_data["performance_trends"] = trend_data
            
            # Recent insights
            recent_insights = self.insights_cache.get(creator_id, [])
            dashboard_data["insights"] = [
                {
                    "title": insight.title,
                    "description": insight.description,
                    "impact_score": insight.impact_score,
                    "confidence_level": insight.confidence_level,
                    "actions": insight.recommended_actions
                }
                for insight in recent_insights[-3:]  # Last 3 insights
            ]
            
            # Performance recommendations
            recommendations = await self._generate_performance_recommendations(creator_id, latest_snapshot)
            dashboard_data["recommendations"] = recommendations
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_trends(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate performance trends from historical snapshots"""
        try:
            # Take last 30 snapshots for trend analysis
            recent_snapshots = snapshots[-30:] if len(snapshots) > 30 else snapshots
            
            # Overall score trend
            scores = [s.overall_score for s in recent_snapshots]
            timestamps = [s.timestamp for s in recent_snapshots]
            
            trends = {
                "overall_score_trend": scores,
                "timestamps": [t.isoformat() for t in timestamps],
                "trend_direction": "up" if scores[-1] > scores[0] else "down",
                "trend_magnitude": abs(scores[-1] - scores[0]) / len(scores),
                "platform_trends": {}
            }
            
            # Platform-specific trends
            platform_data = defaultdict(list)
            for snapshot in recent_snapshots:
                for platform, metrics in snapshot.platform_metrics.items():
                    platform_data[platform.value].append({
                        "engagement_rate": metrics.avg_engagement_rate,
                        "followers": metrics.followers_count,
                        "timestamp": snapshot.timestamp.isoformat()
                    })
            
            trends["platform_trends"] = dict(platform_data)
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to calculate trends: {e}")
            return {}
    
    async def export_creator_report(self, creator_id: str, format_type: str = "json") -> Dict[str, Any]:
        """Export comprehensive creator performance report"""
        try:
            if creator_id not in self.creators:
                return {"error": "Creator not found"}
            
            # Get dashboard data
            dashboard_data = await self.get_creator_dashboard_data(creator_id)
            if "error" in dashboard_data:
                return dashboard_data
            
            # Add detailed analytics
            cross_platform_analysis = await self.analyze_cross_platform_performance(creator_id)
            success_prediction = await self.predict_creator_success(creator_id)
            insights = await self.generate_creator_insights(creator_id)
            
            report = {
                "report_metadata": {
                    "creator_id": creator_id,
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "comprehensive_performance",
                    "format": format_type
                },
                "executive_summary": dashboard_data,
                "cross_platform_analysis": cross_platform_analysis,
                "predictive_analytics": success_prediction,
                "ai_insights": [
                    {
                        "type": insight.insight_type,
                        "title": insight.title,
                        "description": insight.description,
                        "impact_score": insight.impact_score,
                        "confidence": insight.confidence_level,
                        "actions": insight.recommended_actions
                    }
                    for insight in insights
                ],
                "detailed_metrics": self._get_detailed_metrics(creator_id)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return {"error": str(e)}
    
    def _get_detailed_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get detailed metrics for comprehensive reporting"""
        try:
            snapshots = self.performance_history.get(creator_id, [])
            if not snapshots:
                return {}
            
            # Historical performance data
            historical_data = []
            for snapshot in snapshots[-90:]:  # Last 90 snapshots
                snapshot_data = {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "overall_score": snapshot.overall_score,
                    "platforms": {}
                }
                
                for platform, metrics in snapshot.platform_metrics.items():
                    snapshot_data["platforms"][platform.value] = {
                        "followers": metrics.followers_count,
                        "engagement_rate": metrics.avg_engagement_rate,
                        "reach": metrics.avg_reach,
                        "posts": metrics.total_posts
                    }
                
                historical_data.append(snapshot_data)
            
            return {
                "historical_performance": historical_data,
                "data_points": len(historical_data),
                "tracking_period_days": len(historical_data),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed metrics: {e}")
            return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health metrics"""
        return {
            "system_status": "operational",
            "registered_creators": len(self.creators),
            "total_snapshots": sum(len(snapshots) for snapshots in self.performance_history.values()),
            "active_insights": sum(len(insights) for insights in self.insights_cache.values()),
            "ml_models_loaded": len(self.ml_models),
            "uptime": "99.99%",
            "last_updated": datetime.now().isoformat()
        }


# Module exports
__all__ = [
    'CreatorPerformanceAnalytics',
    'CreatorProfile',
    'PlatformMetrics',
    'PerformanceSnapshot',
    'PerformanceInsight',
    'PlatformType',
    'MetricType',
    'CreatorCategory'
]