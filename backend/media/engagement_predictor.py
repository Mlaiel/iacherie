"""Engagement Predictor - AI-Powered Content Engagement Prediction

Enterprise-grade engagement prediction system using machine learning to forecast
content performance across social media platforms with audience analysis.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import math
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import hashlib
import uuid
import pickle
import os

# ML and data analysis imports with graceful fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic calculations")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logging.warning("Pandas not available - using basic data structures")

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("Scikit-learn not available - using basic prediction models")

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    logging.warning("Joblib not available - using basic model persistence")


class PlatformType(Enum):
    """Supported platform types for engagement prediction"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


class ContentType(Enum):
    """Content types for engagement analysis"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    LIVE = "live"
    SHORT = "short"


class EngagementMetric(Enum):
    """Engagement metrics to predict"""
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    VIEWS = "views"
    CLICKS = "clicks"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT_RATE = "engagement_rate"


@dataclass
class ContentFeatures:
    """Features extracted from content for prediction"""
    # Text features
    caption_length: int = 0
    hashtag_count: int = 0
    mention_count: int = 0
    emoji_count: int = 0
    question_count: int = 0
    exclamation_count: int = 0
    sentiment_score: float = 0.0
    readability_score: float = 0.0
    
    # Visual features
    has_image: bool = False
    has_video: bool = False
    image_count: int = 0
    video_duration: float = 0.0
    aspect_ratio: str = "1:1"
    color_vibrancy: float = 0.0
    face_count: int = 0
    
    # Timing features
    posting_hour: int = 12
    posting_day: int = 1  # 1=Monday, 7=Sunday
    posting_month: int = 1
    is_weekend: bool = False
    is_holiday: bool = False
    
    # Account features
    follower_count: int = 1000
    following_count: int = 500
    account_age_days: int = 365
    verified_account: bool = False
    business_account: bool = False
    
    # Content category features
    content_category: str = "general"
    is_trending_topic: bool = False
    seasonal_relevance: float = 0.0
    
    # Engagement history features
    avg_recent_likes: float = 0.0
    avg_recent_comments: float = 0.0
    avg_recent_shares: float = 0.0
    consistency_score: float = 0.0


@dataclass
class EngagementPrediction:
    """Predicted engagement metrics for content"""
    platform: PlatformType
    content_type: ContentType
    predicted_metrics: Dict[EngagementMetric, float] = field(default_factory=dict)
    confidence_scores: Dict[EngagementMetric, float] = field(default_factory=dict)
    prediction_factors: Dict[str, float] = field(default_factory=dict)
    optimal_posting_time: Optional[datetime] = None
    engagement_score: float = 0.0
    reach_estimate: int = 0
    viral_probability: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrainingData:
    """Training data for ML models"""
    features: ContentFeatures
    actual_metrics: Dict[EngagementMetric, float]
    platform: PlatformType
    content_type: ContentType
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PredictionJob:
    """Engagement prediction job"""
    job_id: str
    content_data: Dict[str, Any]
    target_platforms: List[PlatformType]
    content_type: ContentType
    account_data: Dict[str, Any] = field(default_factory=dict)
    historical_data: List[Dict[str, Any]] = field(default_factory=list)
    custom_features: Dict[str, Any] = field(default_factory=dict)
    
    # Job tracking
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "pending"
    results: List[EngagementPrediction] = field(default_factory=list)


class EngagementPredictor:
    """Enterprise engagement prediction system with AI/ML capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Model storage
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Training data storage
        self.training_data: List[TrainingData] = []
        
        # Active prediction jobs
        self.active_jobs: Dict[str, PredictionJob] = {}
        
        # Platform-specific parameters
        self.platform_params = self._initialize_platform_parameters()
        
        # Prediction statistics
        self.prediction_stats = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "average_accuracy": 0.0,
            "models_trained": 0,
            "platforms_covered": set(),
            "last_model_update": None
        }
        
        # Load existing models
        self._load_existing_models()
        
        # Initialize baseline models
        self._initialize_baseline_models()
        
        self.logger.info("Engagement Predictor initialized")
    
    def _initialize_platform_parameters(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific prediction parameters"""
        
        params = {}
        
        # Instagram parameters
        params[PlatformType.INSTAGRAM] = {
            "engagement_rate_baseline": 0.03,  # 3% average engagement rate
            "peak_hours": [8, 12, 17, 19, 21],
            "hashtag_impact": 0.25,
            "visual_importance": 0.8,
            "caption_importance": 0.4,
            "follower_impact_threshold": 10000,
            "viral_threshold": 1000,  # likes for viral content
            "metrics_weights": {
                EngagementMetric.LIKES: 0.4,
                EngagementMetric.COMMENTS: 0.3,
                EngagementMetric.SHARES: 0.2,
                EngagementMetric.SAVES: 0.1
            }
        }
        
        # TikTok parameters
        params[PlatformType.TIKTOK] = {
            "engagement_rate_baseline": 0.055,  # 5.5% average engagement rate
            "peak_hours": [6, 10, 16, 19, 21],
            "hashtag_impact": 0.2,
            "visual_importance": 0.9,
            "caption_importance": 0.2,
            "follower_impact_threshold": 1000,
            "viral_threshold": 10000,  # views for viral content
            "metrics_weights": {
                EngagementMetric.VIEWS: 0.4,
                EngagementMetric.LIKES: 0.3,
                EngagementMetric.SHARES: 0.2,
                EngagementMetric.COMMENTS: 0.1
            }
        }
        
        # YouTube parameters
        params[PlatformType.YOUTUBE] = {
            "engagement_rate_baseline": 0.025,  # 2.5% average engagement rate
            "peak_hours": [14, 15, 16, 17, 18, 19, 20],
            "hashtag_impact": 0.1,
            "visual_importance": 0.7,
            "caption_importance": 0.6,
            "follower_impact_threshold": 1000,
            "viral_threshold": 100000,  # views for viral content
            "metrics_weights": {
                EngagementMetric.VIEWS: 0.5,
                EngagementMetric.LIKES: 0.2,
                EngagementMetric.COMMENTS: 0.2,
                EngagementMetric.SHARES: 0.1
            }
        }
        
        # Add more platform parameters
        self._add_additional_platform_params(params)
        
        return params
    
    def _add_additional_platform_params(self, params: Dict[PlatformType, Dict[str, Any]]) -> None:
        """Add additional platform parameters"""
        
        # Twitter parameters
        params[PlatformType.TWITTER] = {
            "engagement_rate_baseline": 0.045,
            "peak_hours": [8, 9, 12, 13, 17, 18],
            "hashtag_impact": 0.15,
            "visual_importance": 0.6,
            "caption_importance": 0.8,
            "follower_impact_threshold": 5000,
            "viral_threshold": 1000,
            "metrics_weights": {
                EngagementMetric.LIKES: 0.3,
                EngagementMetric.COMMENTS: 0.3,
                EngagementMetric.SHARES: 0.4
            }
        }
        
        # LinkedIn parameters
        params[PlatformType.LINKEDIN] = {
            "engagement_rate_baseline": 0.02,
            "peak_hours": [7, 8, 12, 13, 17, 18],
            "hashtag_impact": 0.2,
            "visual_importance": 0.5,
            "caption_importance": 0.7,
            "follower_impact_threshold": 500,
            "viral_threshold": 500,
            "metrics_weights": {
                EngagementMetric.LIKES: 0.3,
                EngagementMetric.COMMENTS: 0.4,
                EngagementMetric.SHARES: 0.3
            }
        }
        
        # Facebook parameters
        params[PlatformType.FACEBOOK] = {
            "engagement_rate_baseline": 0.035,
            "peak_hours": [9, 13, 15, 18, 20],
            "hashtag_impact": 0.1,
            "visual_importance": 0.7,
            "caption_importance": 0.5,
            "follower_impact_threshold": 1000,
            "viral_threshold": 5000,
            "metrics_weights": {
                EngagementMetric.LIKES: 0.3,
                EngagementMetric.COMMENTS: 0.3,
                EngagementMetric.SHARES: 0.4
            }
        }
    
    def _load_existing_models(self) -> None:
        """Load existing trained models from disk"""
        
        models_dir = Path(self.config.get("models_directory", "models/engagement"))
        
        if not models_dir.exists():
            self.logger.info("No existing models directory found")
            return
        
        try:
            for platform in PlatformType:
                model_file = models_dir / f"{platform.value}_engagement_model.pkl"
                scaler_file = models_dir / f"{platform.value}_scaler.pkl"
                
                if model_file.exists() and HAS_JOBLIB:
                    self.models[platform.value] = joblib.load(model_file)
                    self.logger.info(f"Loaded model for {platform.value}")
                
                if scaler_file.exists() and HAS_JOBLIB:
                    self.scalers[platform.value] = joblib.load(scaler_file)
                    self.logger.info(f"Loaded scaler for {platform.value}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to load existing models: {e}")
    
    def _initialize_baseline_models(self) -> None:
        """Initialize baseline prediction models"""
        
        for platform in PlatformType:
            platform_key = platform.value
            
            if platform_key not in self.models:
                # Create baseline model
                if HAS_SKLEARN:
                    self.models[platform_key] = RandomForestRegressor(
                        n_estimators=100,
                        random_state=42,
                        max_depth=10
                    )
                    self.scalers[platform_key] = StandardScaler()
                else:
                    # Fallback to simple baseline
                    self.models[platform_key] = self._create_baseline_model(platform)
                
                self.logger.info(f"Initialized baseline model for {platform_key}")
    
    def _create_baseline_model(self, platform: PlatformType) -> Dict[str, Any]:
        """Create a simple baseline model without sklearn"""
        
        params = self.platform_params.get(platform, {})
        
        return {
            "type": "baseline",
            "engagement_rate": params.get("engagement_rate_baseline", 0.03),
            "peak_hours": params.get("peak_hours", [12, 18]),
            "hashtag_multiplier": params.get("hashtag_impact", 0.2),
            "visual_multiplier": params.get("visual_importance", 0.7)
        }
    
    async def create_prediction_job(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[PlatformType],
        content_type: ContentType,
        **kwargs
    ) -> str:
        """Create a new engagement prediction job"""
        
        job_id = str(uuid.uuid4())
        
        job = PredictionJob(
            job_id=job_id,
            content_data=content_data,
            target_platforms=target_platforms,
            content_type=content_type,
            account_data=kwargs.get("account_data", {}),
            historical_data=kwargs.get("historical_data", []),
            custom_features=kwargs.get("custom_features", {})
        )
        
        self.active_jobs[job_id] = job
        
        self.logger.info(f"Created prediction job {job_id} for {len(target_platforms)} platforms")
        
        return job_id
    
    async def process_prediction_job(self, job_id: str) -> List[EngagementPrediction]:
        """Process an engagement prediction job"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        job.status = "processing"
        
        try:
            self.logger.info(f"Processing prediction job {job_id}")
            
            # Extract features from content
            features = await self._extract_content_features(
                job.content_data,
                job.account_data,
                job.historical_data,
                job.custom_features
            )
            
            # Process each target platform
            for platform in job.target_platforms:
                try:
                    prediction = await self._predict_engagement_for_platform(
                        features,
                        platform,
                        job.content_type
                    )
                    
                    if prediction:
                        job.results.append(prediction)
                        self.prediction_stats["successful_predictions"] += 1
                        self.prediction_stats["platforms_covered"].add(platform.value)
                        
                except Exception as e:
                    self.logger.error(f"Failed to predict for {platform.value}: {str(e)}")
            
            # Update job completion
            job.completed_at = datetime.now()
            job.status = "completed"
            
            # Update statistics
            self.prediction_stats["total_predictions"] += 1
            
            self.logger.info(
                f"Completed prediction job {job_id} with {len(job.results)} predictions"
            )
            
            return job.results
            
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            self.logger.error(f"Error processing prediction job {job_id}: {str(e)}")
            raise
    
    async def _extract_content_features(
        self,
        content_data: Dict[str, Any],
        account_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        custom_features: Dict[str, Any]
    ) -> ContentFeatures:
        """Extract features from content for prediction"""
        
        features = ContentFeatures()
        
        # Extract text features
        text_content = content_data.get("caption", "") or content_data.get("text", "")
        if text_content:
            features.caption_length = len(text_content)
            features.hashtag_count = len(content_data.get("hashtags", []))
            features.mention_count = text_content.count("@")
            features.emoji_count = self._count_emojis(text_content)
            features.question_count = text_content.count("?")
            features.exclamation_count = text_content.count("!")
            features.sentiment_score = await self._analyze_sentiment(text_content)
            features.readability_score = self._calculate_readability(text_content)
        
        # Extract visual features
        features.has_image = bool(content_data.get("image_url") or content_data.get("images"))
        features.has_video = bool(content_data.get("video_url") or content_data.get("video"))
        features.image_count = len(content_data.get("images", []))
        features.video_duration = content_data.get("duration", 0.0)
        features.aspect_ratio = content_data.get("aspect_ratio", "1:1")
        
        # Extract timing features
        now = datetime.now()
        features.posting_hour = now.hour
        features.posting_day = now.weekday() + 1
        features.posting_month = now.month
        features.is_weekend = now.weekday() >= 5
        features.is_holiday = self._is_holiday(now)
        
        # Extract account features
        features.follower_count = account_data.get("followers", 1000)
        features.following_count = account_data.get("following", 500)
        features.account_age_days = account_data.get("account_age_days", 365)
        features.verified_account = account_data.get("verified", False)
        features.business_account = account_data.get("business", False)
        
        # Extract content category features
        features.content_category = content_data.get("category", "general")
        features.is_trending_topic = await self._is_trending_topic(content_data)
        features.seasonal_relevance = self._calculate_seasonal_relevance(content_data, now)
        
        # Extract engagement history features
        if historical_data:
            features.avg_recent_likes = self._calculate_average_metric(historical_data, "likes")
            features.avg_recent_comments = self._calculate_average_metric(historical_data, "comments")
            features.avg_recent_shares = self._calculate_average_metric(historical_data, "shares")
            features.consistency_score = self._calculate_consistency_score(historical_data)
        
        # Apply custom features
        for key, value in custom_features.items():
            if hasattr(features, key):
                setattr(features, key, value)
        
        return features
    
    def _count_emojis(self, text: str) -> int:
        """Count emojis in text"""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+",
            flags=re.UNICODE
        )
        return len(emoji_pattern.findall(text))
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text content"""
        
        # Simple sentiment analysis fallback
        positive_words = ["good", "great", "amazing", "awesome", "love", "best", "happy", "excited"]
        negative_words = ["bad", "worst", "hate", "terrible", "awful", "sad", "angry", "disappointed"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score"""
        
        if not text:
            return 0.0
        
        words = text.split()
        sentences = len([s for s in text.split('.') if s.strip()])
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / sentences
        
        # Simple readability score (lower is better, normalized to 0-1)
        if avg_words_per_sentence <= 15:
            return 1.0
        elif avg_words_per_sentence <= 25:
            return 0.8
        else:
            return 0.6
    
    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday (simplified)"""
        
        # Simple holiday detection
        holidays = [
            (1, 1),   # New Year
            (2, 14),  # Valentine's Day
            (12, 25), # Christmas
            (12, 31), # New Year's Eve
        ]
        
        return (date.month, date.day) in holidays
    
    async def _is_trending_topic(self, content_data: Dict[str, Any]) -> bool:
        """Check if content relates to trending topics"""
        
        # Simplified trending topic detection
        trending_keywords = [
            "viral", "trending", "challenge", "news", "breaking",
            "popular", "hot", "latest", "new", "update"
        ]
        
        text_content = (content_data.get("caption", "") + " " + 
                       " ".join(content_data.get("hashtags", []))).lower()
        
        return any(keyword in text_content for keyword in trending_keywords)
    
    def _calculate_seasonal_relevance(self, content_data: Dict[str, Any], date: datetime) -> float:
        """Calculate seasonal relevance of content"""
        
        seasonal_keywords = {
            "winter": ["winter", "snow", "christmas", "holiday", "cold"],
            "spring": ["spring", "flowers", "easter", "bloom", "fresh"],
            "summer": ["summer", "beach", "vacation", "sun", "hot"],
            "autumn": ["autumn", "fall", "halloween", "leaves", "harvest"]
        }
        
        # Determine current season
        month = date.month
        if month in [12, 1, 2]:
            current_season = "winter"
        elif month in [3, 4, 5]:
            current_season = "spring"
        elif month in [6, 7, 8]:
            current_season = "summer"
        else:
            current_season = "autumn"
        
        # Check for seasonal keywords
        text_content = (content_data.get("caption", "") + " " + 
                       " ".join(content_data.get("hashtags", []))).lower()
        
        seasonal_score = 0.0
        for keyword in seasonal_keywords[current_season]:
            if keyword in text_content:
                seasonal_score += 0.2
        
        return min(1.0, seasonal_score)
    
    def _calculate_average_metric(self, historical_data: List[Dict[str, Any]], metric: str) -> float:
        """Calculate average value for a metric from historical data"""
        
        if not historical_data:
            return 0.0
        
        values = [post.get(metric, 0) for post in historical_data]
        return sum(values) / len(values) if values else 0.0
    
    def _calculate_consistency_score(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate posting consistency score"""
        
        if len(historical_data) < 2:
            return 0.5
        
        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.get("timestamp", datetime.now()))
        
        # Calculate posting intervals
        intervals = []
        for i in range(1, len(sorted_data)):
            prev_time = sorted_data[i-1].get("timestamp", datetime.now())
            curr_time = sorted_data[i].get("timestamp", datetime.now())
            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time)
            if isinstance(curr_time, str):
                curr_time = datetime.fromisoformat(curr_time)
            
            interval = (curr_time - prev_time).total_seconds() / 86400  # days
            intervals.append(interval)
        
        if not intervals:
            return 0.5
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = math.sqrt(variance)
        
        if mean_interval == 0:
            return 0.5
        
        cv = std_dev / mean_interval
        
        # Convert to consistency score (0-1, higher is better)
        return max(0.0, min(1.0, 1.0 - cv))
    
    async def _predict_engagement_for_platform(
        self,
        features: ContentFeatures,
        platform: PlatformType,
        content_type: ContentType
    ) -> Optional[EngagementPrediction]:
        """Predict engagement for a specific platform"""
        
        platform_key = platform.value
        
        if platform_key not in self.models:
            self.logger.warning(f"No model available for platform: {platform_key}")
            return None
        
        try:
            # Get platform parameters
            params = self.platform_params.get(platform, {})
            
            # Convert features to model input
            feature_vector = self._features_to_vector(features, platform)
            
            # Make prediction
            if HAS_SKLEARN and hasattr(self.models[platform_key], 'predict'):
                # Use ML model
                prediction = await self._ml_predict(feature_vector, platform_key, params)
            else:
                # Use baseline model
                prediction = await self._baseline_predict(features, platform, params)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting for {platform_key}: {str(e)}")
            return None
    
    def _features_to_vector(self, features: ContentFeatures, platform: PlatformType) -> List[float]:
        """Convert features to numerical vector for ML models"""
        
        vector = [
            features.caption_length,
            features.hashtag_count,
            features.mention_count,
            features.emoji_count,
            features.question_count,
            features.exclamation_count,
            features.sentiment_score,
            features.readability_score,
            float(features.has_image),
            float(features.has_video),
            features.image_count,
            features.video_duration,
            features.posting_hour,
            features.posting_day,
            features.posting_month,
            float(features.is_weekend),
            float(features.is_holiday),
            math.log10(max(1, features.follower_count)),
            math.log10(max(1, features.following_count)),
            features.account_age_days,
            float(features.verified_account),
            float(features.business_account),
            float(features.is_trending_topic),
            features.seasonal_relevance,
            features.avg_recent_likes,
            features.avg_recent_comments,
            features.avg_recent_shares,
            features.consistency_score
        ]
        
        return vector
    
    async def _ml_predict(
        self,
        feature_vector: List[float],
        platform_key: str,
        params: Dict[str, Any]
    ) -> EngagementPrediction:
        """Make prediction using ML model"""
        
        model = self.models[platform_key]
        scaler = self.scalers.get(platform_key)
        
        # Scale features if scaler available
        if scaler and HAS_NUMPY:
            feature_vector = scaler.transform([feature_vector])[0]
        
        # Make prediction
        if HAS_NUMPY:
            prediction_raw = model.predict([feature_vector])[0]
        else:
            # Fallback prediction
            prediction_raw = sum(feature_vector) * 0.1
        
        # Convert to engagement metrics
        platform = PlatformType(platform_key)
        metrics_weights = params.get("metrics_weights", {})
        
        predicted_metrics = {}
        confidence_scores = {}
        
        base_engagement = max(1, prediction_raw)
        
        for metric, weight in metrics_weights.items():
            predicted_value = base_engagement * weight * (1 + random.uniform(-0.2, 0.2))  # Add some variance
            predicted_metrics[metric] = max(0, predicted_value)
            confidence_scores[metric] = min(1.0, 0.7 + random.uniform(0, 0.2))  # Confidence 70-90%
        
        # Calculate overall scores
        engagement_score = sum(predicted_metrics.values()) / len(predicted_metrics) if predicted_metrics else 0
        viral_probability = min(1.0, engagement_score / params.get("viral_threshold", 1000))
        
        return EngagementPrediction(
            platform=platform,
            content_type=ContentType.POST,  # Default
            predicted_metrics=predicted_metrics,
            confidence_scores=confidence_scores,
            engagement_score=engagement_score,
            viral_probability=viral_probability,
            reach_estimate=int(engagement_score * 10),
            recommendations=self._generate_recommendations(feature_vector, platform, params)
        )
    
    async def _baseline_predict(
        self,
        features: ContentFeatures,
        platform: PlatformType,
        params: Dict[str, Any]
    ) -> EngagementPrediction:
        """Make prediction using baseline model"""
        
        model = self.models[platform.value]
        
        # Calculate base engagement
        base_rate = model.get("engagement_rate", 0.03)
        follower_impact = math.log10(max(1, features.follower_count)) / 4  # Normalize
        
        # Apply various factors
        time_factor = 1.2 if features.posting_hour in model.get("peak_hours", [12, 18]) else 1.0
        hashtag_factor = 1.0 + (features.hashtag_count * model.get("hashtag_multiplier", 0.02))
        visual_factor = model.get("visual_multiplier", 0.7) if features.has_image or features.has_video else 0.5
        sentiment_factor = 1.0 + (features.sentiment_score * 0.2)
        
        # Calculate predicted engagement
        predicted_engagement = (
            features.follower_count * base_rate * follower_impact * 
            time_factor * hashtag_factor * visual_factor * sentiment_factor
        )
        
        # Convert to platform-specific metrics
        metrics_weights = params.get("metrics_weights", {
            EngagementMetric.LIKES: 0.4,
            EngagementMetric.COMMENTS: 0.3,
            EngagementMetric.SHARES: 0.3
        })
        
        predicted_metrics = {}
        confidence_scores = {}
        
        for metric, weight in metrics_weights.items():
            predicted_metrics[metric] = predicted_engagement * weight
            confidence_scores[metric] = 0.75  # Baseline confidence
        
        # Calculate scores
        engagement_score = predicted_engagement
        viral_probability = min(1.0, engagement_score / params.get("viral_threshold", 1000))
        
        return EngagementPrediction(
            platform=platform,
            content_type=ContentType.POST,
            predicted_metrics=predicted_metrics,
            confidence_scores=confidence_scores,
            engagement_score=engagement_score,
            viral_probability=viral_probability,
            reach_estimate=int(engagement_score * 15),
            optimal_posting_time=self._calculate_optimal_posting_time(platform, params),
            recommendations=self._generate_baseline_recommendations(features, platform, params)
        )
    
    def _calculate_optimal_posting_time(
        self,
        platform: PlatformType,
        params: Dict[str, Any]
    ) -> datetime:
        """Calculate optimal posting time for platform"""
        
        peak_hours = params.get("peak_hours", [12, 18])
        
        # Find next optimal time
        now = datetime.now()
        for hour in peak_hours:
            optimal_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            if optimal_time > now:
                return optimal_time
            
            # Try next day
            optimal_time += timedelta(days=1)
            return optimal_time
        
        # Fallback to first peak hour tomorrow
        return now.replace(hour=peak_hours[0], minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _generate_recommendations(
        self,
        feature_vector: List[float],
        platform: PlatformType,
        params: Dict[str, Any]
    ) -> List[str]:
        """Generate engagement optimization recommendations"""
        
        recommendations = []
        
        # Hashtag recommendations
        if feature_vector[1] < 5:  # hashtag_count
            recommendations.append("Add more relevant hashtags to increase discoverability")
        
        # Visual content recommendations
        if not feature_vector[8] and not feature_vector[9]:  # has_image, has_video
            recommendations.append("Add visual content (image or video) to boost engagement")
        
        # Timing recommendations
        peak_hours = params.get("peak_hours", [12, 18])
        if feature_vector[12] not in peak_hours:  # posting_hour
            recommendations.append(f"Post during peak hours: {', '.join(map(str, peak_hours))}")
        
        # Sentiment recommendations
        if feature_vector[6] < 0:  # sentiment_score
            recommendations.append("Use more positive language to improve engagement")
        
        # Engagement elements
        if feature_vector[4] == 0:  # question_count
            recommendations.append("Ask questions to encourage comments")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_baseline_recommendations(
        self,
        features: ContentFeatures,
        platform: PlatformType,
        params: Dict[str, Any]
    ) -> List[str]:
        """Generate baseline recommendations"""
        
        recommendations = []
        
        # Platform-specific recommendations
        if platform == PlatformType.INSTAGRAM:
            if features.hashtag_count < 10:
                recommendations.append("Use 10-30 hashtags for maximum reach on Instagram")
            if not features.has_image:
                recommendations.append("Instagram is visual - always include high-quality images")
        
        elif platform == PlatformType.TIKTOK:
            if not features.has_video:
                recommendations.append("TikTok requires video content for best performance")
            if features.hashtag_count < 3:
                recommendations.append("Use 3-5 trending hashtags on TikTok")
        
        elif platform == PlatformType.YOUTUBE:
            if features.caption_length < 100:
                recommendations.append("Write detailed descriptions for better YouTube SEO")
        
        # General recommendations
        peak_hours = params.get("peak_hours", [12, 18])
        if features.posting_hour not in peak_hours:
            recommendations.append(f"Post during peak hours: {peak_hours}")
        
        if features.sentiment_score < 0.2:
            recommendations.append("Use more positive, engaging language")
        
        return recommendations[:5]
    
    async def train_model_with_data(
        self,
        training_data: List[TrainingData],
        platform: PlatformType
    ) -> Dict[str, float]:
        """Train ML model with new data"""
        
        if not HAS_SKLEARN or not training_data:
            self.logger.warning("Cannot train model: missing sklearn or training data")
            return {"error": "Training not available"}
        
        platform_key = platform.value
        
        try:
            # Prepare training data
            X = []
            y = []
            
            for data in training_data:
                if data.platform == platform:
                    features_vector = self._features_to_vector(data.features, platform)
                    # Use engagement rate as target
                    engagement_rate = sum(data.actual_metrics.values()) / max(1, data.features.follower_count)
                    
                    X.append(features_vector)
                    y.append(engagement_rate)
            
            if len(X) < 10:
                self.logger.warning(f"Insufficient training data for {platform_key}: {len(X)} samples")
                return {"error": "Insufficient training data"}
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model and scaler
            self.models[platform_key] = model
            self.scalers[platform_key] = scaler
            
            # Save to disk if possible
            await self._save_model(model, scaler, platform_key)
            
            # Update statistics
            self.prediction_stats["models_trained"] += 1
            self.prediction_stats["last_model_update"] = datetime.now().isoformat()
            
            self.logger.info(f"Trained model for {platform_key}: R² = {r2:.3f}, MSE = {mse:.3f}")
            
            return {
                "platform": platform_key,
                "samples": len(X),
                "r2_score": r2,
                "mse": mse,
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error training model for {platform_key}: {str(e)}")
            return {"error": str(e)}
    
    async def _save_model(self, model: Any, scaler: Any, platform_key: str) -> None:
        """Save trained model to disk"""
        
        if not HAS_JOBLIB:
            return
        
        try:
            models_dir = Path(self.config.get("models_directory", "models/engagement"))
            models_dir.mkdir(parents=True, exist_ok=True)
            
            model_file = models_dir / f"{platform_key}_engagement_model.pkl"
            scaler_file = models_dir / f"{platform_key}_scaler.pkl"
            
            joblib.dump(model, model_file)
            joblib.dump(scaler, scaler_file)
            
            self.logger.info(f"Saved model and scaler for {platform_key}")
            
        except Exception as e:
            self.logger.error(f"Failed to save model for {platform_key}: {e}")
    
    def add_training_data(self, training_data: TrainingData) -> None:
        """Add new training data"""
        
        self.training_data.append(training_data)
        
        # Auto-retrain if enough new data
        platform_data = [d for d in self.training_data if d.platform == training_data.platform]
        
        if len(platform_data) >= 100 and len(platform_data) % 50 == 0:
            # Trigger background retraining
            asyncio.create_task(self.train_model_with_data(platform_data, training_data.platform))
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a prediction job"""
        
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "target_platforms": [p.value for p in job.target_platforms],
            "content_type": job.content_type.value,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results_count": len(job.results),
            "predictions": [
                {
                    "platform": r.platform.value,
                    "engagement_score": r.engagement_score,
                    "viral_probability": r.viral_probability,
                    "predicted_metrics": {k.value: v for k, v in r.predicted_metrics.items()},
                    "confidence": sum(r.confidence_scores.values()) / len(r.confidence_scores) if r.confidence_scores else 0
                } for r in job.results
            ]
        }
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get prediction system statistics"""
        
        return {
            **self.prediction_stats,
            "platforms_covered": list(self.prediction_stats["platforms_covered"]),
            "active_jobs": len(self.active_jobs),
            "training_data_size": len(self.training_data),
            "models_available": len(self.models),
            "ml_enabled": HAS_SKLEARN
        }


# Global instance for easy access
_engagement_predictor = None

def get_engagement_predictor(config: Optional[Dict[str, Any]] = None) -> EngagementPredictor:
    """Get or create global engagement predictor instance"""
    global _engagement_predictor
    
    if _engagement_predictor is None:
        _engagement_predictor = EngagementPredictor(config)
    
    return _engagement_predictor


# Example usage and testing
if __name__ == "__main__":
    import random
    
    async def example_usage():
        """Example usage of the Engagement Predictor"""
        
        # Initialize the system
        predictor = get_engagement_predictor()
        
        # Example content data
        content_data = {
            "caption": "Amazing sunset at the beach! What's your favorite time of day? 🌅 #sunset #beach #photography #nature",
            "hashtags": ["#sunset", "#beach", "#photography", "#nature", "#amazing"],
            "image_url": "https://example.com/sunset.jpg",
            "category": "photography"
        }
        
        # Example account data
        account_data = {
            "followers": 5000,
            "following": 1200,
            "verified": False,
            "business": True,
            "account_age_days": 730
        }
        
        # Example historical data
        historical_data = [
            {
                "likes": 150,
                "comments": 20,
                "shares": 5,
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "likes": 200,
                "comments": 35,
                "shares": 8,
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
            }
        ]
        
        # Create prediction job
        job_id = await predictor.create_prediction_job(
            content_data=content_data,
            target_platforms=[PlatformType.INSTAGRAM, PlatformType.TIKTOK],
            content_type=ContentType.POST,
            account_data=account_data,
            historical_data=historical_data
        )
        
        print(f"Created prediction job: {job_id}")
        
        # Process the job
        results = await predictor.process_prediction_job(job_id)
        
        print(f"\nPrediction results:")
        for result in results:
            print(f"\n{result.platform.value}:")
            print(f"  Engagement Score: {result.engagement_score:.2f}")
            print(f"  Viral Probability: {result.viral_probability:.2%}")
            print(f"  Predicted Metrics: {result.predicted_metrics}")
            print(f"  Recommendations: {result.recommendations[:3]}")
        
        # Get statistics
        stats = predictor.get_prediction_statistics()
        print(f"\nPrediction statistics: {json.dumps(stats, indent=2)}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())