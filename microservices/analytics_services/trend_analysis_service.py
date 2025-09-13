"""
📈 Trend Analysis Service - Market Trend Analysis & Prediction
=============================================================

**Module**: Trend Analysis Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: ML Engineer + DBA + AI Prompt Engineer + Lead Dev IA

Advanced trend analysis service with AI-powered market prediction,
real-time trend monitoring, and intelligent content recommendations.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid
import numpy as np
import re
from collections import defaultdict, deque
import statistics

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TrendAnalysisService")

class TrendDirection(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"

class TrendStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    EXPLOSIVE = "explosive"

class TrendCategory(str, Enum):
    CONTENT = "content"
    HASHTAG = "hashtag"
    KEYWORD = "keyword"
    PLATFORM = "platform"
    INDUSTRY = "industry"
    DEMOGRAPHIC = "demographic"

class TimeFrame(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class TrendMetrics:
    """Trend analysis metrics"""
    trending_topics_count: int
    emerging_trends_count: int
    declining_trends_count: int
    total_data_points: int
    prediction_accuracy: float
    real_time_updates: int
    ai_confidence_score: float

class DataPointModel(BaseModel):
    """Data point for trend analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: float
    source: str
    category: TrendCategory
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TrendModel(BaseModel):
    """Trend model for analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: TrendCategory
    direction: TrendDirection
    strength: TrendStrength
    confidence_score: float = 0.0
    growth_rate: float = 0.0
    current_value: float = 0.0
    peak_value: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_points: List[DataPointModel] = Field(default_factory=list)
    predictions: Dict[str, Any] = Field(default_factory=dict)
    related_trends: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    geographic_data: Dict[str, Any] = Field(default_factory=dict)

class TrendPredictionModel(BaseModel):
    """Trend prediction model"""
    trend_id: str
    timeframe: TimeFrame
    predicted_values: List[Tuple[datetime, float]]
    confidence_intervals: List[Tuple[float, float]]
    accuracy_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    factors: List[str] = Field(default_factory=list)

class TrendAnalysisService:
    """
    📈 Enterprise Trend Analysis Service
    
    **Expertise Applied:**
    - **ML Engineer**: Advanced prediction algorithms and statistical analysis
    - **DBA**: Optimized data storage and retrieval for time-series analysis
    - **AI Prompt Engineer**: Intelligent trend interpretation and insights
    - **Lead Dev IA**: AI-powered trend discovery and recommendation system
    """
    
    def __init__(self):
        self.trends: Dict[str, TrendModel] = {}
        self.data_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.predictions: Dict[str, TrendPredictionModel] = {}
        self.trend_keywords: Dict[str, List[str]] = {}
        self.real_time_processors: Dict[str, Any] = {}
        self.ai_models: Dict[str, Any] = {}
        
        # Initialize trend detection algorithms
        self._initialize_ai_models()
        self._initialize_trend_keywords()
        self._start_real_time_monitoring()
        
        logger.info("📈 Trend Analysis Service initialized")
    
    def _initialize_ai_models(self):
        """Initialize AI models for trend analysis"""
        self.ai_models = {
            "linear_regression": self._linear_trend_model,
            "moving_average": self._moving_average_model,
            "exponential_smoothing": self._exponential_smoothing_model,
            "seasonal_decomposition": self._seasonal_decomposition_model,
            "anomaly_detection": self._anomaly_detection_model,
            "sentiment_analysis": self._sentiment_analysis_model
        }
    
    def _initialize_trend_keywords(self):
        """Initialize trending keywords and hashtags"""
        self.trend_keywords = {
            "content_creation": [
                "viral", "trending", "content", "creator", "influencer",
                "video", "short", "reel", "story", "live", "stream"
            ],
            "technology": [
                "ai", "artificial intelligence", "machine learning", "blockchain",
                "crypto", "metaverse", "vr", "ar", "web3", "nft"
            ],
            "social_media": [
                "instagram", "tiktok", "youtube", "twitter", "linkedin",
                "engagement", "followers", "algorithm", "reach", "impressions"
            ],
            "entertainment": [
                "music", "movies", "gaming", "esports", "streaming",
                "netflix", "spotify", "podcast", "entertainment", "celebrity"
            ],
            "business": [
                "startup", "entrepreneurship", "marketing", "branding",
                "business", "growth", "revenue", "monetization", "commerce"
            ]
        }
    
    def _start_real_time_monitoring(self):
        """Start real-time trend monitoring"""
        # This would typically connect to real data streams
        # For now, we'll simulate with periodic updates
        pass
    
    async def add_data_point(self, data_point: DataPointModel) -> Dict[str, Any]:
        """Add new data point for trend analysis"""
        try:
            # Store data point
            stream_key = f"{data_point.category.value}_{data_point.source}"
            self.data_streams[stream_key].append(data_point)
            
            # Update related trends
            updated_trends = await self._update_trends_with_data_point(data_point)
            
            # Check for new trends
            new_trends = await self._detect_new_trends(data_point)
            
            # Generate real-time insights
            insights = await self._generate_real_time_insights(data_point)
            
            logger.info(f"📊 Data point added: {data_point.source} - {data_point.value}")
            
            return {
                "success": True,
                "data_point_id": data_point.id,
                "updated_trends": updated_trends,
                "new_trends": new_trends,
                "insights": insights,
                "message": "Data point processed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Data point processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data processing failed: {str(e)}")
    
    async def create_trend(self, trend_data: TrendModel) -> Dict[str, Any]:
        """Create new trend for tracking"""
        try:
            # Validate trend data
            if not trend_data.name:
                raise ValueError("Trend name is required")
            
            # Check for existing trend
            existing = next((t for t in self.trends.values() 
                           if t.name.lower() == trend_data.name.lower() and 
                           t.category == trend_data.category), None)
            
            if existing:
                return {
                    "success": True,
                    "trend_id": existing.id,
                    "message": "Trend already exists",
                    "trend": existing.dict()
                }
            
            # Store trend
            self.trends[trend_data.id] = trend_data
            
            # Initialize keywords if not provided
            if not trend_data.keywords:
                trend_data.keywords = await self._extract_trend_keywords(trend_data.name)
            
            # Start monitoring for this trend
            await self._start_trend_monitoring(trend_data.id)
            
            logger.info(f"📈 Trend created: {trend_data.name} (ID: {trend_data.id})")
            
            return {
                "success": True,
                "trend_id": trend_data.id,
                "trend": trend_data.dict(),
                "message": "Trend created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Trend creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Trend creation failed: {str(e)}")
    
    async def analyze_trend(self, trend_id: str, timeframe: TimeFrame = TimeFrame.WEEK) -> Dict[str, Any]:
        """Analyze trend with AI-powered insights"""
        try:
            if trend_id not in self.trends:
                raise ValueError(f"Trend {trend_id} not found")
            
            trend = self.trends[trend_id]
            
            # Get data points for analysis
            data_points = self._get_trend_data_points(trend, timeframe)
            
            if len(data_points) < 2:
                return {
                    "success": False,
                    "message": "Insufficient data for analysis"
                }
            
            # Perform multiple analysis methods
            analyses = {}
            
            # Linear trend analysis
            analyses["linear"] = await self._linear_trend_analysis(data_points)
            
            # Moving average analysis
            analyses["moving_average"] = await self._moving_average_analysis(data_points)
            
            # Volatility analysis
            analyses["volatility"] = await self._volatility_analysis(data_points)
            
            # Momentum analysis
            analyses["momentum"] = await self._momentum_analysis(data_points)
            
            # Seasonal pattern analysis
            analyses["seasonal"] = await self._seasonal_analysis(data_points)
            
            # Anomaly detection
            analyses["anomalies"] = await self._anomaly_detection(data_points)
            
            # Generate overall trend assessment
            assessment = await self._generate_trend_assessment(trend, analyses)
            
            # Update trend with new analysis
            trend.direction = TrendDirection(assessment["direction"])
            trend.strength = TrendStrength(assessment["strength"])
            trend.confidence_score = assessment["confidence"]
            trend.growth_rate = assessment["growth_rate"]
            trend.last_updated = datetime.utcnow()
            
            logger.info(f"📊 Trend analyzed: {trend.name} - {assessment['direction']} {assessment['strength']}")
            
            return {
                "success": True,
                "trend_id": trend_id,
                "trend_name": trend.name,
                "timeframe": timeframe.value,
                "analyses": analyses,
                "assessment": assessment,
                "data_points_analyzed": len(data_points),
                "message": "Trend analysis completed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
    
    async def predict_trend(self, trend_id: str, timeframe: TimeFrame = TimeFrame.WEEK,
                          prediction_days: int = 7) -> Dict[str, Any]:
        """Predict future trend values using AI models"""
        try:
            if trend_id not in self.trends:
                raise ValueError(f"Trend {trend_id} not found")
            
            trend = self.trends[trend_id]
            
            # Get historical data
            data_points = self._get_trend_data_points(trend, timeframe)
            
            if len(data_points) < 5:
                return {
                    "success": False,
                    "message": "Insufficient historical data for prediction"
                }
            
            # Prepare data for prediction
            timestamps = [dp.timestamp for dp in data_points]
            values = [dp.value for dp in data_points]
            
            # Generate predictions using multiple models
            predictions = {}
            
            # Linear prediction
            predictions["linear"] = await self._linear_prediction(timestamps, values, prediction_days)
            
            # Moving average prediction
            predictions["moving_average"] = await self._moving_average_prediction(values, prediction_days)
            
            # Exponential smoothing prediction
            predictions["exponential"] = await self._exponential_smoothing_prediction(values, prediction_days)
            
            # Ensemble prediction (combine multiple models)
            ensemble_prediction = await self._ensemble_prediction(predictions, prediction_days)
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                predictions, ensemble_prediction
            )
            
            # Create prediction model
            prediction_model = TrendPredictionModel(
                trend_id=trend_id,
                timeframe=timeframe,
                predicted_values=ensemble_prediction,
                confidence_intervals=confidence_intervals,
                accuracy_score=await self._calculate_prediction_accuracy(trend_id, predictions),
                factors=await self._identify_prediction_factors(trend)
            )
            
            # Store prediction
            self.predictions[f"{trend_id}_{timeframe.value}"] = prediction_model
            
            # Update trend with predictions
            trend.predictions[timeframe.value] = {
                "ensemble": ensemble_prediction,
                "models": predictions,
                "confidence": confidence_intervals,
                "accuracy": prediction_model.accuracy_score
            }
            
            logger.info(f"🔮 Trend prediction generated: {trend.name} for {prediction_days} days")
            
            return {
                "success": True,
                "trend_id": trend_id,
                "trend_name": trend.name,
                "timeframe": timeframe.value,
                "prediction_days": prediction_days,
                "ensemble_prediction": ensemble_prediction,
                "model_predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "accuracy_score": prediction_model.accuracy_score,
                "prediction_factors": prediction_model.factors,
                "message": "Trend prediction completed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Trend prediction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Trend prediction failed: {str(e)}")
    
    async def get_trending_topics(self, category: Optional[TrendCategory] = None,
                                limit: int = 20) -> Dict[str, Any]:
        """Get currently trending topics with rankings"""
        try:
            # Filter trends by category if specified
            trends_to_analyze = list(self.trends.values())
            if category:
                trends_to_analyze = [t for t in trends_to_analyze if t.category == category]
            
            # Calculate trending score for each trend
            trending_scores = []
            for trend in trends_to_analyze:
                score = await self._calculate_trending_score(trend)
                trending_scores.append({
                    "trend_id": trend.id,
                    "name": trend.name,
                    "category": trend.category.value,
                    "direction": trend.direction.value,
                    "strength": trend.strength.value,
                    "score": score,
                    "growth_rate": trend.growth_rate,
                    "confidence": trend.confidence_score,
                    "keywords": trend.keywords[:5],  # Top 5 keywords
                    "last_updated": trend.last_updated.isoformat()
                })
            
            # Sort by trending score
            trending_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Limit results
            top_trends = trending_scores[:limit]
            
            # Generate insights about trending topics
            insights = await self._generate_trending_insights(top_trends)
            
            return {
                "success": True,
                "category": category.value if category else "all",
                "trending_topics": top_trends,
                "total_trends_analyzed": len(trends_to_analyze),
                "insights": insights,
                "message": "Trending topics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Trending topics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Trending topics failed: {str(e)}")
    
    async def get_trend_recommendations(self, user_interests: List[str],
                                     content_type: str = "general") -> Dict[str, Any]:
        """Get personalized trend recommendations based on user interests"""
        try:
            # Find trends matching user interests
            relevant_trends = []
            
            for trend in self.trends.values():
                relevance_score = await self._calculate_relevance_score(
                    trend, user_interests, content_type
                )
                
                if relevance_score > 0.3:  # Minimum relevance threshold
                    relevant_trends.append({
                        "trend": trend.dict(),
                        "relevance_score": relevance_score,
                        "matching_keywords": list(set(trend.keywords) & set(user_interests)),
                        "opportunity_score": await self._calculate_opportunity_score(trend)
                    })
            
            # Sort by relevance and opportunity
            relevant_trends.sort(
                key=lambda x: x["relevance_score"] * x["opportunity_score"], 
                reverse=True
            )
            
            # Generate content recommendations
            content_recommendations = await self._generate_content_recommendations(
                relevant_trends[:10], user_interests, content_type
            )
            
            # Generate timing recommendations
            timing_recommendations = await self._generate_timing_recommendations(
                relevant_trends[:5]
            )
            
            return {
                "success": True,
                "user_interests": user_interests,
                "content_type": content_type,
                "recommended_trends": relevant_trends[:10],
                "content_recommendations": content_recommendations,
                "timing_recommendations": timing_recommendations,
                "total_relevant_trends": len(relevant_trends),
                "message": "Trend recommendations generated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Trend recommendations failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")
    
    def _get_trend_data_points(self, trend: TrendModel, timeframe: TimeFrame) -> List[DataPointModel]:
        """Get data points for trend within timeframe"""
        cutoff_time = datetime.utcnow()
        
        if timeframe == TimeFrame.HOUR:
            cutoff_time -= timedelta(hours=1)
        elif timeframe == TimeFrame.DAY:
            cutoff_time -= timedelta(days=1)
        elif timeframe == TimeFrame.WEEK:
            cutoff_time -= timedelta(weeks=1)
        elif timeframe == TimeFrame.MONTH:
            cutoff_time -= timedelta(days=30)
        elif timeframe == TimeFrame.QUARTER:
            cutoff_time -= timedelta(days=90)
        elif timeframe == TimeFrame.YEAR:
            cutoff_time -= timedelta(days=365)
        
        return [dp for dp in trend.data_points if dp.timestamp >= cutoff_time]
    
    async def _linear_trend_analysis(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Perform linear trend analysis"""
        if len(data_points) < 2:
            return {"slope": 0, "r_squared": 0, "direction": "stable"}
        
        values = [dp.value for dp in data_points]
        x_values = list(range(len(values)))
        
        # Calculate linear regression
        n = len(values)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate R-squared
        y_pred = [slope * x + (y_mean - slope * x_mean) for x in x_values]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine direction
        if slope > 0.1:
            direction = "rising"
        elif slope < -0.1:
            direction = "falling"
        else:
            direction = "stable"
        
        return {
            "slope": slope,
            "r_squared": r_squared,
            "direction": direction,
            "strength": abs(slope),
            "confidence": r_squared
        }
    
    async def _moving_average_analysis(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Perform moving average analysis"""
        values = [dp.value for dp in data_points]
        
        if len(values) < 5:
            return {"short_ma": 0, "long_ma": 0, "signal": "neutral"}
        
        # Calculate moving averages
        short_period = min(5, len(values) // 3)
        long_period = min(10, len(values) // 2)
        
        short_ma = statistics.mean(values[-short_period:])
        long_ma = statistics.mean(values[-long_period:])
        
        # Generate signal
        if short_ma > long_ma * 1.05:
            signal = "bullish"
        elif short_ma < long_ma * 0.95:
            signal = "bearish"
        else:
            signal = "neutral"
        
        return {
            "short_ma": short_ma,
            "long_ma": long_ma,
            "signal": signal,
            "crossover": short_ma - long_ma,
            "strength": abs(short_ma - long_ma) / long_ma if long_ma != 0 else 0
        }
    
    async def _volatility_analysis(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Analyze trend volatility"""
        values = [dp.value for dp in data_points]
        
        if len(values) < 2:
            return {"volatility": 0, "stability": "unknown"}
        
        # Calculate standard deviation
        volatility = statistics.stdev(values)
        mean_value = statistics.mean(values)
        
        # Calculate coefficient of variation
        cv = volatility / mean_value if mean_value != 0 else 0
        
        # Determine stability
        if cv < 0.1:
            stability = "very_stable"
        elif cv < 0.2:
            stability = "stable"
        elif cv < 0.5:
            stability = "moderate"
        else:
            stability = "volatile"
        
        return {
            "volatility": volatility,
            "coefficient_of_variation": cv,
            "stability": stability,
            "risk_level": min(cv * 100, 100)
        }
    
    async def _momentum_analysis(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Analyze trend momentum"""
        values = [dp.value for dp in data_points]
        
        if len(values) < 3:
            return {"momentum": 0, "acceleration": 0}
        
        # Calculate momentum (rate of change)
        recent_values = values[-5:] if len(values) >= 5 else values
        momentum = (recent_values[-1] - recent_values[0]) / len(recent_values)
        
        # Calculate acceleration (change in momentum)
        if len(values) >= 6:
            prev_period = values[-10:-5] if len(values) >= 10 else values[:-5]
            prev_momentum = (prev_period[-1] - prev_period[0]) / len(prev_period)
            acceleration = momentum - prev_momentum
        else:
            acceleration = 0
        
        return {
            "momentum": momentum,
            "acceleration": acceleration,
            "momentum_strength": abs(momentum),
            "trend_acceleration": "accelerating" if acceleration > 0 else "decelerating" if acceleration < 0 else "steady"
        }
    
    async def _seasonal_analysis(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        # Simplified seasonal analysis
        values = [dp.value for dp in data_points]
        timestamps = [dp.timestamp for dp in data_points]
        
        if len(values) < 7:
            return {"seasonal_pattern": "insufficient_data"}
        
        # Group by hour of day
        hourly_averages = {}
        for i, ts in enumerate(timestamps):
            hour = ts.hour
            if hour not in hourly_averages:
                hourly_averages[hour] = []
            hourly_averages[hour].append(values[i])
        
        # Calculate average for each hour
        hour_stats = {}
        for hour, vals in hourly_averages.items():
            hour_stats[hour] = statistics.mean(vals)
        
        # Find peak hours
        if hour_stats:
            peak_hour = max(hour_stats, key=hour_stats.get)
            low_hour = min(hour_stats, key=hour_stats.get)
        else:
            peak_hour = 12
            low_hour = 3
        
        return {
            "seasonal_pattern": "detected" if len(hour_stats) > 1 else "unclear",
            "peak_hour": peak_hour,
            "low_hour": low_hour,
            "hourly_variation": max(hour_stats.values()) - min(hour_stats.values()) if hour_stats else 0
        }
    
    async def _anomaly_detection(self, data_points: List[DataPointModel]) -> Dict[str, Any]:
        """Detect anomalies in trend data"""
        values = [dp.value for dp in data_points]
        
        if len(values) < 5:
            return {"anomalies": [], "anomaly_count": 0}
        
        # Calculate z-scores
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for i, value in enumerate(values):
            if std_val > 0:
                z_score = abs(value - mean_val) / std_val
                if z_score > 2:  # More than 2 standard deviations
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "z_score": z_score,
                        "timestamp": data_points[i].timestamp.isoformat()
                    })
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "anomaly_rate": len(anomalies) / len(values) * 100
        }
    
    async def _generate_trend_assessment(self, trend: TrendModel, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall trend assessment"""
        # Combine all analyses to determine overall trend
        direction_votes = []
        strength_scores = []
        confidence_scores = []
        
        # Linear analysis contribution
        linear = analyses.get("linear", {})
        if linear.get("direction"):
            direction_votes.append(linear["direction"])
            strength_scores.append(linear.get("strength", 0))
            confidence_scores.append(linear.get("confidence", 0))
        
        # Moving average contribution
        ma = analyses.get("moving_average", {})
        if ma.get("signal") == "bullish":
            direction_votes.append("rising")
        elif ma.get("signal") == "bearish":
            direction_votes.append("falling")
        else:
            direction_votes.append("stable")
        strength_scores.append(ma.get("strength", 0))
        
        # Momentum contribution
        momentum = analyses.get("momentum", {})
        if momentum.get("momentum", 0) > 0:
            direction_votes.append("rising")
        elif momentum.get("momentum", 0) < 0:
            direction_votes.append("falling")
        else:
            direction_votes.append("stable")
        strength_scores.append(momentum.get("momentum_strength", 0))
        
        # Determine final direction
        direction_counts = {"rising": 0, "falling": 0, "stable": 0}
        for vote in direction_votes:
            direction_counts[vote] += 1
        
        final_direction = max(direction_counts, key=direction_counts.get)
        
        # Calculate average strength
        avg_strength = statistics.mean(strength_scores) if strength_scores else 0
        
        # Determine strength category
        if avg_strength > 0.8:
            strength = "explosive"
        elif avg_strength > 0.5:
            strength = "strong"
        elif avg_strength > 0.2:
            strength = "moderate"
        else:
            strength = "weak"
        
        # Calculate confidence
        confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
        
        # Calculate growth rate
        growth_rate = momentum.get("momentum", 0) * 100
        
        return {
            "direction": final_direction,
            "strength": strength,
            "confidence": confidence,
            "growth_rate": growth_rate,
            "volatility": analyses.get("volatility", {}).get("stability", "unknown"),
            "anomaly_rate": analyses.get("anomalies", {}).get("anomaly_rate", 0)
        }
    
    async def _extract_trend_keywords(self, trend_name: str) -> List[str]:
        """Extract relevant keywords for trend"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', trend_name.lower())
        
        # Add related keywords from our knowledge base
        keywords = words.copy()
        for category, category_keywords in self.trend_keywords.items():
            for word in words:
                if word in category_keywords:
                    keywords.extend(category_keywords[:5])  # Add top 5 related keywords
        
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    async def _start_trend_monitoring(self, trend_id: str):
        """Start monitoring for a specific trend"""
        # This would typically set up real-time monitoring
        # For now, we'll just log the start
        logger.info(f"🔍 Started monitoring trend: {trend_id}")
    
    async def _update_trends_with_data_point(self, data_point: DataPointModel) -> List[str]:
        """Update existing trends with new data point"""
        updated_trends = []
        
        # Find trends that match this data point
        for trend_id, trend in self.trends.items():
            if self._data_point_matches_trend(data_point, trend):
                trend.data_points.append(data_point)
                trend.current_value = data_point.value
                trend.peak_value = max(trend.peak_value, data_point.value)
                trend.last_updated = datetime.utcnow()
                updated_trends.append(trend_id)
        
        return updated_trends
    
    def _data_point_matches_trend(self, data_point: DataPointModel, trend: TrendModel) -> bool:
        """Check if data point matches trend criteria"""
        # Match by category
        if data_point.category != trend.category:
            return False
        
        # Match by keywords
        data_text = " ".join([data_point.source] + data_point.tags + list(data_point.metadata.values()))
        data_text = data_text.lower()
        
        for keyword in trend.keywords:
            if keyword.lower() in data_text:
                return True
        
        return False
    
    async def _detect_new_trends(self, data_point: DataPointModel) -> List[Dict[str, Any]]:
        """Detect if data point indicates new emerging trends"""
        # Simplified new trend detection
        new_trends = []
        
        # Check if this is an unusual spike in activity
        if data_point.value > 100:  # Arbitrary threshold
            trend_name = f"Emerging: {data_point.source}"
            
            # Check if trend already exists
            existing = next((t for t in self.trends.values() 
                           if t.name == trend_name), None)
            
            if not existing:
                new_trend = TrendModel(
                    name=trend_name,
                    category=data_point.category,
                    direction=TrendDirection.RISING,
                    strength=TrendStrength.MODERATE,
                    current_value=data_point.value,
                    peak_value=data_point.value,
                    data_points=[data_point],
                    keywords=await self._extract_trend_keywords(data_point.source)
                )
                
                self.trends[new_trend.id] = new_trend
                new_trends.append(new_trend.dict())
        
        return new_trends
    
    async def _generate_real_time_insights(self, data_point: DataPointModel) -> Dict[str, Any]:
        """Generate real-time insights from data point"""
        return {
            "data_velocity": "high" if data_point.value > 50 else "normal",
            "category_activity": data_point.category.value,
            "source_significance": "emerging" if data_point.value > 100 else "normal",
            "timestamp": data_point.timestamp.isoformat()
        }
    
    # Prediction methods (simplified implementations)
    async def _linear_prediction(self, timestamps: List[datetime], values: List[float], days: int) -> List[Tuple[datetime, float]]:
        """Linear trend prediction"""
        if len(values) < 2:
            return []
        
        # Calculate slope
        x_values = list(range(len(values)))
        n = len(values)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Generate predictions
        predictions = []
        last_timestamp = timestamps[-1]
        
        for i in range(1, days + 1):
            future_timestamp = last_timestamp + timedelta(days=i)
            predicted_value = slope * (len(values) + i - 1) + intercept
            predictions.append((future_timestamp, max(0, predicted_value)))
        
        return predictions
    
    async def _moving_average_prediction(self, values: List[float], days: int) -> List[Tuple[datetime, float]]:
        """Moving average based prediction"""
        if len(values) < 3:
            return []
        
        # Use last 5 values for prediction
        recent_values = values[-5:]
        avg_value = statistics.mean(recent_values)
        
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(1, days + 1):
            future_timestamp = base_time + timedelta(days=i)
            # Simple moving average prediction (could be more sophisticated)
            predicted_value = avg_value
            predictions.append((future_timestamp, predicted_value))
        
        return predictions
    
    async def _exponential_smoothing_prediction(self, values: List[float], days: int) -> List[Tuple[datetime, float]]:
        """Exponential smoothing prediction"""
        if len(values) < 2:
            return []
        
        # Simple exponential smoothing
        alpha = 0.3  # Smoothing parameter
        smoothed = values[0]
        
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(1, days + 1):
            future_timestamp = base_time + timedelta(days=i)
            predictions.append((future_timestamp, smoothed))
        
        return predictions
    
    async def _ensemble_prediction(self, predictions: Dict[str, List[Tuple[datetime, float]]], days: int) -> List[Tuple[datetime, float]]:
        """Combine multiple prediction models"""
        if not predictions:
            return []
        
        ensemble = []
        base_time = datetime.utcnow()
        
        for i in range(days):
            future_timestamp = base_time + timedelta(days=i + 1)
            
            # Average predictions from all models
            day_predictions = []
            for model_name, model_predictions in predictions.items():
                if i < len(model_predictions):
                    day_predictions.append(model_predictions[i][1])
            
            if day_predictions:
                avg_prediction = statistics.mean(day_predictions)
                ensemble.append((future_timestamp, avg_prediction))
        
        return ensemble
    
    async def _calculate_confidence_intervals(self, predictions: Dict[str, List], ensemble: List) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for predictions"""
        intervals = []
        
        for i in range(len(ensemble)):
            # Get all model predictions for this day
            day_predictions = []
            for model_predictions in predictions.values():
                if i < len(model_predictions):
                    day_predictions.append(model_predictions[i][1])
            
            if len(day_predictions) > 1:
                std_dev = statistics.stdev(day_predictions)
                mean_pred = ensemble[i][1]
                
                # 95% confidence interval (approximately)
                lower_bound = max(0, mean_pred - 1.96 * std_dev)
                upper_bound = mean_pred + 1.96 * std_dev
                intervals.append((lower_bound, upper_bound))
            else:
                # Single prediction, use wider interval
                pred_value = ensemble[i][1]
                intervals.append((pred_value * 0.8, pred_value * 1.2))
        
        return intervals
    
    async def _calculate_prediction_accuracy(self, trend_id: str, predictions: Dict[str, List]) -> float:
        """Calculate historical prediction accuracy"""
        # Simplified accuracy calculation
        # In a real system, this would compare past predictions with actual outcomes
        return 0.75  # 75% accuracy baseline
    
    async def _identify_prediction_factors(self, trend: TrendModel) -> List[str]:
        """Identify factors influencing the trend prediction"""
        factors = []
        
        # Add category-specific factors
        if trend.category == TrendCategory.CONTENT:
            factors.extend(["algorithm_changes", "seasonal_patterns", "creator_activity"])
        elif trend.category == TrendCategory.HASHTAG:
            factors.extend(["viral_events", "platform_promotion", "community_engagement"])
        elif trend.category == TrendCategory.PLATFORM:
            factors.extend(["feature_updates", "user_adoption", "competitor_activity"])
        
        # Add general factors
        factors.extend(["historical_patterns", "momentum", "volatility"])
        
        return factors[:5]  # Return top 5 factors
    
    async def _calculate_trending_score(self, trend: TrendModel) -> float:
        """Calculate trending score for ranking"""
        score = 0
        
        # Direction impact
        if trend.direction == TrendDirection.RISING:
            score += 100
        elif trend.direction == TrendDirection.FALLING:
            score -= 50
        
        # Strength impact
        if trend.strength == TrendStrength.EXPLOSIVE:
            score += 200
        elif trend.strength == TrendStrength.STRONG:
            score += 100
        elif trend.strength == TrendStrength.MODERATE:
            score += 50
        
        # Confidence impact
        score += trend.confidence_score * 50
        
        # Growth rate impact
        score += trend.growth_rate * 2
        
        # Recency impact
        hours_since_update = (datetime.utcnow() - trend.last_updated).total_seconds() / 3600
        recency_multiplier = max(0.1, 1 - (hours_since_update / 24))  # Decay over 24 hours
        score *= recency_multiplier
        
        return max(0, score)
    
    async def _generate_trending_insights(self, top_trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights about trending topics"""
        if not top_trends:
            return {"summary": "No trending topics available"}
        
        # Category distribution
        category_counts = {}
        for trend in top_trends:
            category = trend["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Top category
        top_category = max(category_counts, key=category_counts.get) if category_counts else "unknown"
        
        # Average growth rate
        growth_rates = [t["growth_rate"] for t in top_trends if t.get("growth_rate")]
        avg_growth = statistics.mean(growth_rates) if growth_rates else 0
        
        return {
            "summary": f"Found {len(top_trends)} trending topics",
            "top_category": top_category,
            "category_distribution": category_counts,
            "average_growth_rate": avg_growth,
            "fastest_growing": top_trends[0]["name"] if top_trends else "None",
            "market_sentiment": "bullish" if avg_growth > 5 else "bearish" if avg_growth < -5 else "neutral"
        }
    
    async def _calculate_relevance_score(self, trend: TrendModel, user_interests: List[str], content_type: str) -> float:
        """Calculate relevance score for trend recommendation"""
        score = 0
        
        # Keyword matching
        matching_keywords = set(trend.keywords) & set([interest.lower() for interest in user_interests])
        score += len(matching_keywords) * 0.2
        
        # Category relevance
        if content_type.lower() in trend.name.lower() or content_type.lower() in str(trend.category.value).lower():
            score += 0.3
        
        # Trend strength
        if trend.strength == TrendStrength.EXPLOSIVE:
            score += 0.4
        elif trend.strength == TrendStrength.STRONG:
            score += 0.3
        elif trend.strength == TrendStrength.MODERATE:
            score += 0.2
        
        # Trend direction
        if trend.direction == TrendDirection.RISING:
            score += 0.3
        
        # Confidence
        score += trend.confidence_score * 0.2
        
        return min(1.0, score)
    
    async def _calculate_opportunity_score(self, trend: TrendModel) -> float:
        """Calculate opportunity score for trend"""
        score = 0
        
        # Early stage trends have higher opportunity
        data_points_count = len(trend.data_points)
        if data_points_count < 10:
            score += 0.4  # Early adopter advantage
        elif data_points_count < 50:
            score += 0.3
        else:
            score += 0.1
        
        # Growth rate
        if trend.growth_rate > 10:
            score += 0.4
        elif trend.growth_rate > 5:
            score += 0.3
        elif trend.growth_rate > 0:
            score += 0.2
        
        # Volatility (moderate volatility indicates opportunity)
        # This would need volatility data from analyses
        score += 0.2  # Simplified
        
        return min(1.0, score)
    
    async def _generate_content_recommendations(self, relevant_trends: List[Dict], user_interests: List[str], content_type: str) -> List[Dict[str, Any]]:
        """Generate content recommendations based on trends"""
        recommendations = []
        
        for trend_data in relevant_trends[:5]:
            trend = trend_data["trend"]
            
            recommendation = {
                "trend_name": trend["name"],
                "content_ideas": [
                    f"Create {content_type} about {trend['name']}",
                    f"Tutorial on {trend['keywords'][0] if trend['keywords'] else 'trending topic'}",
                    f"Your take on the {trend['name']} trend"
                ],
                "suggested_keywords": trend["keywords"][:5],
                "optimal_timing": "next 24-48 hours" if trend["direction"] == "rising" else "monitor for reversal",
                "difficulty": "medium" if trend["strength"] in ["moderate", "strong"] else "high",
                "potential_reach": "high" if trend["strength"] == "explosive" else "medium"
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_timing_recommendations(self, relevant_trends: List[Dict]) -> Dict[str, Any]:
        """Generate timing recommendations for content creation"""
        if not relevant_trends:
            return {"recommendation": "No timing data available"}
        
        # Analyze trend momentum
        rising_trends = [t for t in relevant_trends if t["trend"]["direction"] == "rising"]
        explosive_trends = [t for t in relevant_trends if t["trend"]["strength"] == "explosive"]
        
        if explosive_trends:
            timing = "immediate"
            reason = "Explosive trends detected - act now for maximum impact"
        elif rising_trends:
            timing = "within_24_hours"
            reason = "Rising trends detected - create content while momentum builds"
        else:
            timing = "monitor"
            reason = "No clear rising trends - monitor for opportunities"
        
        return {
            "recommendation": timing,
            "reason": reason,
            "optimal_posting_hours": [9, 12, 15, 18, 21],  # Simplified
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "trend_window": "next 3-7 days"
        }
    
    # Model implementations (simplified)
    def _linear_trend_model(self, data: List[float]) -> Dict[str, Any]:
        """Linear trend model implementation"""
        return {"type": "linear", "data": data}
    
    def _moving_average_model(self, data: List[float]) -> Dict[str, Any]:
        """Moving average model implementation"""
        return {"type": "moving_average", "data": data}
    
    def _exponential_smoothing_model(self, data: List[float]) -> Dict[str, Any]:
        """Exponential smoothing model implementation"""
        return {"type": "exponential_smoothing", "data": data}
    
    def _seasonal_decomposition_model(self, data: List[float]) -> Dict[str, Any]:
        """Seasonal decomposition model implementation"""
        return {"type": "seasonal_decomposition", "data": data}
    
    def _anomaly_detection_model(self, data: List[float]) -> Dict[str, Any]:
        """Anomaly detection model implementation"""
        return {"type": "anomaly_detection", "data": data}
    
    def _sentiment_analysis_model(self, data: List[float]) -> Dict[str, Any]:
        """Sentiment analysis model implementation"""
        return {"type": "sentiment_analysis", "data": data}
    
    async def get_trend_metrics(self) -> Dict[str, Any]:
        """Get trend analysis service metrics"""
        try:
            total_trends = len(self.trends)
            rising_trends = len([t for t in self.trends.values() if t.direction == TrendDirection.RISING])
            falling_trends = len([t for t in self.trends.values() if t.direction == TrendDirection.FALLING])
            
            total_data_points = sum(len(t.data_points) for t in self.trends.values())
            
            # Calculate prediction accuracy (simplified)
            prediction_accuracy = statistics.mean([p.accuracy_score for p in self.predictions.values()]) if self.predictions else 0.75
            
            # Calculate AI confidence score
            ai_confidence = statistics.mean([t.confidence_score for t in self.trends.values()]) if self.trends else 0.5
            
            metrics = TrendMetrics(
                trending_topics_count=total_trends,
                emerging_trends_count=rising_trends,
                declining_trends_count=falling_trends,
                total_data_points=total_data_points,
                prediction_accuracy=prediction_accuracy,
                real_time_updates=total_data_points,  # Simplified
                ai_confidence_score=ai_confidence
            )
            
            return {
                "success": True,
                "metrics": asdict(metrics),
                "active_predictions": len(self.predictions),
                "data_streams": len(self.data_streams),
                "message": "Trend analysis metrics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Metrics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")

# FastAPI Application
app = FastAPI(title="Trend Analysis Service", version="1.0.0")
service = TrendAnalysisService()

@app.post("/data-points/add")
async def add_data_point(data_point: DataPointModel):
    """Add new data point for trend analysis"""
    return await service.add_data_point(data_point)

@app.post("/trends/create")
async def create_trend(trend: TrendModel):
    """Create new trend for tracking"""
    return await service.create_trend(trend)

@app.post("/trends/{trend_id}/analyze")
async def analyze_trend(trend_id: str, timeframe: TimeFrame = TimeFrame.WEEK):
    """Analyze trend with AI-powered insights"""
    return await service.analyze_trend(trend_id, timeframe)

@app.post("/trends/{trend_id}/predict")
async def predict_trend(trend_id: str, timeframe: TimeFrame = TimeFrame.WEEK, prediction_days: int = 7):
    """Predict future trend values"""
    return await service.predict_trend(trend_id, timeframe, prediction_days)

@app.get("/trending")
async def get_trending_topics(category: Optional[TrendCategory] = None, limit: int = 20):
    """Get currently trending topics"""
    return await service.get_trending_topics(category, limit)

@app.post("/recommendations")
async def get_trend_recommendations(user_interests: List[str], content_type: str = "general"):
    """Get personalized trend recommendations"""
    return await service.get_trend_recommendations(user_interests, content_type)

@app.get("/metrics")
async def get_metrics():
    """Get trend analysis service metrics"""
    return await service.get_trend_metrics()

@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "service": "TrendAnalysisService",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("📈 Starting Trend Analysis Service...")
    print("🤖 AI-powered market trend analysis and prediction")
    print("🔮 Real-time trend monitoring and insights")
    print("📊 Advanced statistical modeling and forecasting")
    
    uvicorn.run(app, host="0.0.0.0", port=8089)