"""Viral Content Predictor - AI-Powered Viral Content Analysis and Prediction

This module predicts content virality using advanced machine learning algorithms,
social signals analysis, and engagement pattern recognition.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
import re
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import math

logger = logging.getLogger(__name__)


class ViralityLevel(Enum):
    """Virality prediction levels"""
    LOW = "low"                    # 0-20% viral potential
    MODERATE = "moderate"          # 21-50% viral potential
    HIGH = "high"                 # 51-80% viral potential
    VIRAL = "viral"               # 81-95% viral potential
    MEGA_VIRAL = "mega_viral"     # 95%+ viral potential


class ContentCategory(Enum):
    """Content categories for viral analysis"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH = "health"
    SPORTS = "sports"
    MUSIC = "music"
    COMEDY = "comedy"
    TRAVEL = "travel"
    FOOD = "food"


class PlatformType(Enum):
    """Platform types for viral content"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"


@dataclass
class ContentFeatures:
    """Content features for viral prediction"""
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    content_type: str = "video"
    duration_seconds: int = 0
    word_count: int = 0
    hashtag_count: int = 0
    mention_count: int = 0
    emoji_count: int = 0
    question_count: int = 0
    exclamation_count: int = 0
    caps_lock_ratio: float = 0.0
    sentiment_score: float = 0.0
    readability_score: float = 0.0
    urgency_score: float = 0.0
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    trending_topics_score: float = 0.0
    timing_score: float = 0.0
    platform_fit_score: float = 0.0
    creator_authority_score: float = 0.0
    audience_size: int = 0
    category: ContentCategory = ContentCategory.ENTERTAINMENT
    platform: PlatformType = PlatformType.TIKTOK


@dataclass
class ViralPrediction:
    """Viral content prediction result"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    viral_score: float = 0.0
    virality_level: ViralityLevel = ViralityLevel.LOW
    platform_scores: Dict[str, float] = field(default_factory=dict)
    prediction_confidence: float = 0.0
    predicted_reach: int = 0
    predicted_engagement_rate: float = 0.0
    predicted_shares: int = 0
    predicted_comments: int = 0
    predicted_likes: int = 0
    viral_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    optimal_posting_time: datetime = field(default_factory=datetime.now)
    trending_window: int = 48  # hours
    peak_engagement_time: int = 6  # hours after posting
    viral_trajectory: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ViralTrend:
    """Viral content trend analysis"""
    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trend_name: str = ""
    trend_score: float = 0.0
    growth_rate: float = 0.0
    platform_distribution: Dict[str, float] = field(default_factory=dict)
    content_types: List[str] = field(default_factory=list)
    demographic_appeal: Dict[str, float] = field(default_factory=dict)
    geographic_hotspots: List[str] = field(default_factory=list)
    related_hashtags: List[str] = field(default_factory=list)
    influencer_participation: List[str] = field(default_factory=list)
    trend_lifecycle_stage: str = "emerging"  # emerging, growing, peak, declining
    estimated_lifespan_days: int = 7
    monetization_potential: float = 0.0


class ViralContentPredictor:
    """Advanced viral content prediction and analysis system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Viral Content Predictor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.predictions: Dict[str, ViralPrediction] = {}
        self.content_features: Dict[str, ContentFeatures] = {}
        self.viral_trends: Dict[str, ViralTrend] = {}
        self.model_cache: Dict[str, Any] = {}
        
        # ML Models
        self.viral_classifier = RandomForestRegressor(n_estimators=100, random_state=42)
        self.engagement_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.trend_analyzer = RandomForestRegressor(n_estimators=50, random_state=42)
        
        # Text processing
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        
        # Configuration parameters
        self.min_viral_score = self.config.get('min_viral_score', 0.6)
        self.prediction_confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.trending_topics_weight = self.config.get('trending_weight', 0.3)
        self.platform_weights = self.config.get('platform_weights', {
            'tiktok': 1.2,
            'instagram': 1.1,
            'youtube': 1.0,
            'twitter': 0.9,
            'facebook': 0.8
        })
        
        # Initialize models with synthetic data
        asyncio.create_task(self._initialize_models())
    
    async def predict_viral_potential(
        self,
        content_data: Dict[str, Any],
        target_platforms: Optional[List[PlatformType]] = None,
        optimization_mode: bool = True
    ) -> ViralPrediction:
        """Predict viral potential for content
        
        Args:
            content_data: Content information and features
            target_platforms: Platforms to analyze
            optimization_mode: Whether to include optimization suggestions
            
        Returns:
            Comprehensive viral prediction
        """
        try:
            logger.info(f"Predicting viral potential for content: {content_data.get('title', 'Unknown')}")
            
            # Extract content features
            features = await self._extract_content_features(content_data)
            
            # Generate base viral prediction
            base_prediction = await self._generate_base_prediction(features)
            
            # Analyze platform-specific potential
            platform_scores = await self._analyze_platform_potential(
                features, target_platforms or [PlatformType.TIKTOK, PlatformType.INSTAGRAM]
            )
            
            # Calculate timing optimization
            optimal_timing = await self._optimize_posting_timing(features)
            
            # Analyze viral factors and risks
            viral_factors, risk_factors = await self._analyze_viral_factors(features)
            
            # Generate optimization suggestions
            optimization_suggestions = []
            if optimization_mode:
                optimization_suggestions = await self._generate_optimization_suggestions(
                    features, base_prediction
                )
            
            # Create prediction object
            prediction = ViralPrediction(
                content_id=features.content_id,
                viral_score=base_prediction['viral_score'],
                virality_level=await self._classify_virality_level(base_prediction['viral_score']),
                platform_scores=platform_scores,
                prediction_confidence=base_prediction['confidence'],
                predicted_reach=await self._predict_reach(features, base_prediction['viral_score']),
                predicted_engagement_rate=await self._predict_engagement_rate(features),
                predicted_shares=await self._predict_shares(features, base_prediction['viral_score']),
                predicted_comments=await self._predict_comments(features, base_prediction['viral_score']),
                predicted_likes=await self._predict_likes(features, base_prediction['viral_score']),
                viral_factors=viral_factors,
                risk_factors=risk_factors,
                optimization_suggestions=optimization_suggestions,
                optimal_posting_time=optimal_timing['optimal_time'],
                trending_window=optimal_timing['trending_window'],
                peak_engagement_time=optimal_timing['peak_time'],
                viral_trajectory=await self._predict_viral_trajectory(features, base_prediction['viral_score'])
            )
            
            # Store prediction
            self.predictions[prediction.prediction_id] = prediction
            self.content_features[features.content_id] = features
            
            logger.info(f"Viral prediction completed. Score: {prediction.viral_score:.2f}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting viral potential: {str(e)}")
            # Return default prediction
            return ViralPrediction(
                content_id=content_data.get('id', 'unknown'),
                viral_score=0.1,
                virality_level=ViralityLevel.LOW,
                prediction_confidence=0.0
            )
    
    async def analyze_viral_trends(
        self,
        platforms: Optional[List[PlatformType]] = None,
        time_range_days: int = 7
    ) -> List[ViralTrend]:
        """Analyze current viral trends
        
        Args:
            platforms: Platforms to analyze
            time_range_days: Time range for trend analysis
            
        Returns:
            List of viral trends
        """
        try:
            logger.info("Analyzing viral trends")
            
            platforms = platforms or list(PlatformType)
            trends = []
            
            # Generate trending topics
            trending_topics = await self._discover_trending_topics(platforms, time_range_days)
            
            for topic_data in trending_topics:
                trend = ViralTrend(
                    trend_name=topic_data['name'],
                    trend_score=topic_data['score'],
                    growth_rate=topic_data['growth_rate'],
                    platform_distribution=topic_data['platform_distribution'],
                    content_types=topic_data['content_types'],
                    demographic_appeal=topic_data['demographics'],
                    geographic_hotspots=topic_data['geographic_hotspots'],
                    related_hashtags=topic_data['hashtags'],
                    influencer_participation=topic_data['influencers'],
                    trend_lifecycle_stage=await self._determine_lifecycle_stage(topic_data),
                    estimated_lifespan_days=await self._estimate_trend_lifespan(topic_data),
                    monetization_potential=await self._calculate_monetization_potential(topic_data)
                )
                
                trends.append(trend)
                self.viral_trends[trend.trend_id] = trend
            
            # Sort by trend score
            trends.sort(key=lambda x: x.trend_score, reverse=True)
            
            logger.info(f"Identified {len(trends)} viral trends")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing viral trends: {str(e)}")
            return []
    
    async def optimize_content_for_virality(
        self,
        content_data: Dict[str, Any],
        target_viral_score: float = 0.8,
        target_platform: PlatformType = PlatformType.TIKTOK
    ) -> Dict[str, Any]:
        """Optimize content for maximum viral potential
        
        Args:
            content_data: Original content data
            target_viral_score: Target viral score to achieve
            target_platform: Primary target platform
            
        Returns:
            Optimization recommendations and improved content suggestions
        """
        try:
            logger.info(f"Optimizing content for virality (target: {target_viral_score})")
            
            # Get current prediction
            current_prediction = await self.predict_viral_potential(content_data, [target_platform])
            
            # Generate optimization strategies
            optimizations = {
                'current_score': current_prediction.viral_score,
                'target_score': target_viral_score,
                'improvement_needed': target_viral_score - current_prediction.viral_score,
                'title_optimizations': await self._optimize_title(content_data, target_platform),
                'content_optimizations': await self._optimize_content_structure(content_data, target_platform),
                'hashtag_optimizations': await self._optimize_hashtags(content_data, target_platform),
                'timing_optimizations': await self._optimize_timing_strategy(content_data, target_platform),
                'platform_specific_tips': await self._get_platform_specific_tips(target_platform),
                'trend_integration': await self._suggest_trend_integration(content_data),
                'engagement_hooks': await self._generate_engagement_hooks(content_data, target_platform),
                'visual_suggestions': await self._suggest_visual_optimizations(content_data, target_platform),
                'predicted_improvement': await self._estimate_optimization_impact(
                    current_prediction, target_viral_score
                )
            }
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing content for virality: {str(e)}")
            return {}
    
    async def _extract_content_features(self, content_data: Dict[str, Any]) -> ContentFeatures:
        """Extract features from content data"""
        try:
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            
            features = ContentFeatures(
                content_id=content_data.get('id', str(uuid.uuid4())),
                title=title,
                description=description,
                content_type=content_data.get('type', 'video'),
                duration_seconds=content_data.get('duration', 30),
                word_count=len((title + ' ' + description).split()),
                hashtag_count=len(re.findall(r'#\w+', title + ' ' + description)),
                mention_count=len(re.findall(r'@\w+', title + ' ' + description)),
                emoji_count=await self._count_emojis(title + ' ' + description),
                question_count=title.count('?') + description.count('?'),
                exclamation_count=title.count('!') + description.count('!'),
                caps_lock_ratio=await self._calculate_caps_ratio(title + ' ' + description),
                sentiment_score=await self._analyze_sentiment(title + ' ' + description),
                readability_score=await self._calculate_readability(title + ' ' + description),
                urgency_score=await self._calculate_urgency(title + ' ' + description),
                emotion_scores=await self._analyze_emotions(title + ' ' + description),
                trending_topics_score=await self._calculate_trending_alignment(title + ' ' + description),
                timing_score=await self._calculate_timing_score(content_data),
                platform_fit_score=await self._calculate_platform_fit(content_data),
                creator_authority_score=content_data.get('creator_authority', 0.5),
                audience_size=content_data.get('follower_count', 1000),
                category=ContentCategory(content_data.get('category', 'entertainment')),
                platform=PlatformType(content_data.get('platform', 'tiktok'))
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting content features: {str(e)}")
            return ContentFeatures()
    
    async def _generate_base_prediction(self, features: ContentFeatures) -> Dict[str, float]:
        """Generate base viral prediction using ML models"""
        try:
            # Create feature vector
            feature_vector = await self._create_feature_vector(features)
            
            # Use trained model or fallback to heuristic scoring
            if hasattr(self.viral_classifier, 'predict'):
                try:
                    viral_score = self.viral_classifier.predict([feature_vector])[0]
                    viral_score = max(0.0, min(1.0, viral_score))  # Clamp to [0, 1]
                except:
                    viral_score = await self._heuristic_viral_score(features)
            else:
                viral_score = await self._heuristic_viral_score(features)
            
            # Calculate confidence based on feature quality
            confidence = await self._calculate_prediction_confidence(features, viral_score)
            
            return {
                'viral_score': viral_score,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error generating base prediction: {str(e)}")
            return {'viral_score': 0.1, 'confidence': 0.0}
    
    async def _heuristic_viral_score(self, features: ContentFeatures) -> float:
        """Calculate viral score using heuristic approach"""
        try:
            score = 0.0
            
            # Content quality factors
            if features.hashtag_count > 0:
                score += min(features.hashtag_count / 10, 0.15)
            
            if features.emotion_scores.get('excitement', 0) > 0.7:
                score += 0.2
            
            if features.urgency_score > 0.6:
                score += 0.15
            
            if features.sentiment_score > 0.3:
                score += 0.1
            
            # Platform-specific bonuses
            if features.platform == PlatformType.TIKTOK:
                if 15 <= features.duration_seconds <= 60:
                    score += 0.1
                if features.emotion_scores.get('humor', 0) > 0.6:
                    score += 0.15
            
            # Trending alignment
            score += features.trending_topics_score * 0.2
            
            # Creator authority
            score += features.creator_authority_score * 0.1
            
            # Audience size factor (logarithmic)
            if features.audience_size > 0:
                audience_factor = min(math.log10(features.audience_size) / 6, 0.1)
                score += audience_factor
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating heuristic viral score: {str(e)}")
            return 0.1
    
    async def _analyze_platform_potential(
        self,
        features: ContentFeatures,
        platforms: List[PlatformType]
    ) -> Dict[str, float]:
        """Analyze viral potential for each platform"""
        try:
            platform_scores = {}
            
            for platform in platforms:
                base_score = await self._heuristic_viral_score(features)
                
                # Platform-specific adjustments
                if platform == PlatformType.TIKTOK:
                    # Short-form video preference
                    if features.duration_seconds <= 60:
                        base_score *= 1.2
                    # Trend alignment is crucial
                    base_score += features.trending_topics_score * 0.3
                    
                elif platform == PlatformType.INSTAGRAM:
                    # Visual content preference
                    if features.content_type in ['image', 'video']:
                        base_score *= 1.1
                    # Hashtag optimization
                    if 5 <= features.hashtag_count <= 15:
                        base_score *= 1.15
                        
                elif platform == PlatformType.YOUTUBE:
                    # Longer content tolerance
                    if features.duration_seconds > 60:
                        base_score *= 1.1
                    # Educational content bonus
                    if features.category == ContentCategory.EDUCATION:
                        base_score *= 1.2
                        
                elif platform == PlatformType.TWITTER:
                    # Brevity bonus
                    if features.word_count <= 280:
                        base_score *= 1.1
                    # News and trending topics
                    if features.category == ContentCategory.NEWS:
                        base_score *= 1.15
                
                # Apply platform weight
                platform_weight = self.platform_weights.get(platform.value, 1.0)
                platform_scores[platform.value] = min(base_score * platform_weight, 1.0)
            
            return platform_scores
            
        except Exception as e:
            logger.error(f"Error analyzing platform potential: {str(e)}")
            return {}
    
    async def _optimize_posting_timing(self, features: ContentFeatures) -> Dict[str, Any]:
        """Optimize posting timing for maximum viral potential"""
        try:
            # Platform-specific optimal times
            optimal_times = {
                PlatformType.TIKTOK: {'hour': 19, 'day_offset': 0},  # 7 PM today
                PlatformType.INSTAGRAM: {'hour': 20, 'day_offset': 0},  # 8 PM today
                PlatformType.YOUTUBE: {'hour': 15, 'day_offset': 1},  # 3 PM tomorrow
                PlatformType.TWITTER: {'hour': 12, 'day_offset': 0},  # 12 PM today
                PlatformType.FACEBOOK: {'hour': 21, 'day_offset': 0}  # 9 PM today
            }
            
            platform_time = optimal_times.get(features.platform, {'hour': 18, 'day_offset': 0})
            
            # Calculate optimal posting time
            now = datetime.now()
            optimal_time = now.replace(
                hour=platform_time['hour'],
                minute=0,
                second=0,
                microsecond=0
            ) + timedelta(days=platform_time['day_offset'])
            
            # If time has passed today, schedule for tomorrow
            if optimal_time <= now:
                optimal_time += timedelta(days=1)
            
            return {
                'optimal_time': optimal_time,
                'trending_window': 48,  # hours
                'peak_time': 6  # hours after posting
            }
            
        except Exception as e:
            logger.error(f"Error optimizing posting timing: {str(e)}")
            return {
                'optimal_time': datetime.now() + timedelta(hours=2),
                'trending_window': 24,
                'peak_time': 4
            }
    
    async def _analyze_viral_factors(self, features: ContentFeatures) -> Tuple[List[str], List[str]]:
        """Analyze viral factors and risk factors"""
        try:
            viral_factors = []
            risk_factors = []
            
            # Viral factors
            if features.emotion_scores.get('excitement', 0) > 0.7:
                viral_factors.append("High excitement level")
            
            if features.trending_topics_score > 0.6:
                viral_factors.append("Strong trend alignment")
            
            if features.urgency_score > 0.6:
                viral_factors.append("High urgency/FOMO factor")
            
            if features.hashtag_count >= 5:
                viral_factors.append("Good hashtag coverage")
            
            if features.creator_authority_score > 0.7:
                viral_factors.append("High creator authority")
            
            if features.sentiment_score > 0.5:
                viral_factors.append("Positive sentiment")
            
            # Risk factors
            if features.word_count > 50 and features.platform in [PlatformType.TIKTOK, PlatformType.INSTAGRAM]:
                risk_factors.append("Text too long for platform")
            
            if features.hashtag_count > 20:
                risk_factors.append("Too many hashtags (spam risk)")
            
            if features.sentiment_score < -0.3:
                risk_factors.append("Negative sentiment")
            
            if features.trending_topics_score < 0.2:
                risk_factors.append("Low trend relevance")
            
            if features.readability_score < 0.4:
                risk_factors.append("Poor readability")
            
            return viral_factors, risk_factors
            
        except Exception as e:
            logger.error(f"Error analyzing viral factors: {str(e)}")
            return [], []
    
    async def _generate_optimization_suggestions(
        self,
        features: ContentFeatures,
        prediction: Dict[str, float]
    ) -> List[str]:
        """Generate optimization suggestions for better viral potential"""
        try:
            suggestions = []
            
            # Title optimization
            if len(features.title) < 10:
                suggestions.append("Create a more descriptive and engaging title")
            
            if features.question_count == 0:
                suggestions.append("Add a compelling question to increase engagement")
            
            # Hashtag optimization
            if features.hashtag_count < 3:
                suggestions.append("Add more relevant hashtags (aim for 5-10)")
            elif features.hashtag_count > 15:
                suggestions.append("Reduce hashtag count to avoid spam perception")
            
            # Emotion optimization
            if features.emotion_scores.get('excitement', 0) < 0.5:
                suggestions.append("Increase excitement factor with energetic language")
            
            # Platform-specific suggestions
            if features.platform == PlatformType.TIKTOK:
                if features.duration_seconds > 60:
                    suggestions.append("Keep video under 60 seconds for better TikTok performance")
                suggestions.append("Use trending sounds and effects")
                
            elif features.platform == PlatformType.INSTAGRAM:
                suggestions.append("Use high-quality visuals")
                suggestions.append("Post during optimal engagement hours (7-9 PM)")
                
            elif features.platform == PlatformType.YOUTUBE:
                suggestions.append("Create compelling thumbnail")
                suggestions.append("Add clear call-to-action")
            
            # Trending alignment
            if features.trending_topics_score < 0.4:
                suggestions.append("Align content with current trending topics")
            
            # Urgency factor
            if features.urgency_score < 0.3:
                suggestions.append("Add time-sensitive elements or FOMO triggers")
            
            return suggestions[:8]  # Return top 8 suggestions
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {str(e)}")
            return ["Improve content quality and engagement factors"]
    
    # Helper methods for feature extraction
    async def _count_emojis(self, text: str) -> int:
        """Count emojis in text"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE
        )
        return len(emoji_pattern.findall(text))
    
    async def _calculate_caps_ratio(self, text: str) -> float:
        """Calculate ratio of capital letters"""
        if not text:
            return 0.0
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0.0
        return sum(1 for c in letters if c.isupper()) / len(letters)
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment (simplified implementation)"""
        positive_words = ['amazing', 'awesome', 'great', 'love', 'best', 'perfect', 'incredible']
        negative_words = ['hate', 'terrible', 'worst', 'awful', 'bad', 'horrible']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified)"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = len(re.split(r'[.!?]+', text))
        
        # Simple readability score (lower is better, normalize to 0-1)
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = len(words) / sentences
        complexity = (avg_word_length * 0.4) + (avg_sentence_length * 0.6)
        
        # Normalize (assume complexity 1-20, invert so higher is better)
        readability = max(0, min(1, 1 - (complexity - 1) / 19))
        return readability
    
    async def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency score"""
        urgency_words = [
            'now', 'today', 'urgent', 'limited', 'hurry', 'fast', 'quick',
            'immediately', 'asap', 'deadline', 'expires', 'last chance'
        ]
        
        text_lower = text.lower()
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        
        # Also check for exclamation marks and caps
        exclamation_factor = min(text.count('!') / 10, 0.3)
        caps_factor = await self._calculate_caps_ratio(text) * 0.2
        
        urgency_score = min(urgency_count / 5, 0.5) + exclamation_factor + caps_factor
        return min(urgency_score, 1.0)
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content (simplified)"""
        emotions = {
            'excitement': ['amazing', 'wow', 'incredible', 'awesome', 'fantastic'],
            'humor': ['funny', 'lol', 'hilarious', 'joke', 'laugh'],
            'surprise': ['shocking', 'unbelievable', 'surprising', 'unexpected'],
            'curiosity': ['secret', 'mystery', 'discover', 'reveal', 'unknown']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, words in emotions.items():
            score = sum(1 for word in words if word in text_lower)
            emotion_scores[emotion] = min(score / 3, 1.0)  # Normalize
        
        return emotion_scores
    
    async def _calculate_trending_alignment(self, text: str) -> float:
        """Calculate alignment with trending topics"""
        trending_keywords = [
            'ai', 'viral', 'trending', 'challenge', 'hack', 'tip',
            'secret', 'exposed', 'revealed', 'truth', '2025'
        ]
        
        text_lower = text.lower()
        trend_count = sum(1 for keyword in trending_keywords if keyword in text_lower)
        
        return min(trend_count / 5, 1.0)
    
    async def _calculate_timing_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate timing score based on posting schedule"""
        # Simplified - in production would analyze optimal posting times
        return 0.7
    
    async def _calculate_platform_fit(self, content_data: Dict[str, Any]) -> float:
        """Calculate how well content fits the platform"""
        # Simplified platform fit calculation
        return 0.8
    
    async def _create_feature_vector(self, features: ContentFeatures) -> List[float]:
        """Create feature vector for ML models"""
        return [
            features.word_count / 100,  # Normalized
            features.hashtag_count / 20,
            features.mention_count / 10,
            features.emoji_count / 10,
            features.question_count / 5,
            features.exclamation_count / 5,
            features.caps_lock_ratio,
            features.sentiment_score,
            features.readability_score,
            features.urgency_score,
            features.emotion_scores.get('excitement', 0),
            features.emotion_scores.get('humor', 0),
            features.trending_topics_score,
            features.timing_score,
            features.platform_fit_score,
            features.creator_authority_score,
            min(math.log10(features.audience_size + 1) / 6, 1.0)  # Normalized log
        ]
    
    async def _calculate_prediction_confidence(self, features: ContentFeatures, viral_score: float) -> float:
        """Calculate confidence in prediction"""
        confidence_factors = [
            features.creator_authority_score,
            features.platform_fit_score,
            min(features.audience_size / 10000, 1.0),
            features.trending_topics_score
        ]
        
        base_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Adjust based on viral score (extreme scores are less confident)
        score_confidence = 1 - abs(viral_score - 0.5) * 0.5
        
        return (base_confidence + score_confidence) / 2
    
    async def _classify_virality_level(self, viral_score: float) -> ViralityLevel:
        """Classify virality level based on score"""
        if viral_score >= 0.95:
            return ViralityLevel.MEGA_VIRAL
        elif viral_score >= 0.8:
            return ViralityLevel.VIRAL
        elif viral_score >= 0.5:
            return ViralityLevel.HIGH
        elif viral_score >= 0.2:
            return ViralityLevel.MODERATE
        else:
            return ViralityLevel.LOW
    
    # Prediction helper methods
    async def _predict_reach(self, features: ContentFeatures, viral_score: float) -> int:
        """Predict content reach"""
        base_reach = features.audience_size * 2  # Base reach is 2x follower count
        viral_multiplier = 1 + (viral_score * 50)  # Up to 50x for viral content
        return int(base_reach * viral_multiplier)
    
    async def _predict_engagement_rate(self, features: ContentFeatures) -> float:
        """Predict engagement rate"""
        base_rate = 0.03  # 3% base engagement rate
        
        # Adjust based on platform
        platform_multipliers = {
            PlatformType.TIKTOK: 1.5,
            PlatformType.INSTAGRAM: 1.2,
            PlatformType.YOUTUBE: 1.0,
            PlatformType.TWITTER: 0.8,
            PlatformType.FACEBOOK: 0.6
        }
        
        multiplier = platform_multipliers.get(features.platform, 1.0)
        
        # Adjust based on content quality
        quality_factor = (
            features.sentiment_score * 0.3 +
            features.emotion_scores.get('excitement', 0) * 0.4 +
            features.trending_topics_score * 0.3
        )
        
        engagement_rate = base_rate * multiplier * (1 + quality_factor)
        return min(engagement_rate, 0.2)  # Cap at 20%
    
    async def _predict_shares(self, features: ContentFeatures, viral_score: float) -> int:
        """Predict number of shares"""
        predicted_reach = await self._predict_reach(features, viral_score)
        share_rate = 0.001 + (viral_score * 0.05)  # 0.1% to 5.1% share rate
        return int(predicted_reach * share_rate)
    
    async def _predict_comments(self, features: ContentFeatures, viral_score: float) -> int:
        """Predict number of comments"""
        predicted_reach = await self._predict_reach(features, viral_score)
        comment_rate = 0.005 + (viral_score * 0.02)  # 0.5% to 2.5% comment rate
        return int(predicted_reach * comment_rate)
    
    async def _predict_likes(self, features: ContentFeatures, viral_score: float) -> int:
        """Predict number of likes"""
        predicted_reach = await self._predict_reach(features, viral_score)
        engagement_rate = await self._predict_engagement_rate(features)
        return int(predicted_reach * engagement_rate)
    
    async def _predict_viral_trajectory(self, features: ContentFeatures, viral_score: float) -> Dict[str, float]:
        """Predict viral trajectory over time"""
        trajectory = {}
        
        # Hour-by-hour prediction for first 48 hours
        peak_hour = 6  # Peak at 6 hours
        
        for hour in range(48):
            if hour <= peak_hour:
                # Growing phase
                progress = hour / peak_hour
                viral_factor = viral_score * progress
            else:
                # Decline phase
                decay_rate = 0.9
                hours_past_peak = hour - peak_hour
                viral_factor = viral_score * (decay_rate ** hours_past_peak)
            
            trajectory[f"hour_{hour}"] = min(viral_factor, viral_score)
        
        return trajectory
    
    # Trend analysis methods
    async def _discover_trending_topics(self, platforms: List[PlatformType], time_range_days: int) -> List[Dict[str, Any]]:
        """Discover trending topics across platforms"""
        # Simulated trending topics
        trending_topics = [
            {
                'name': 'AI Technology 2025',
                'score': 0.9,
                'growth_rate': 0.15,
                'platform_distribution': {'tiktok': 0.4, 'instagram': 0.3, 'youtube': 0.3},
                'content_types': ['educational', 'demo', 'prediction'],
                'demographics': {'18-24': 0.4, '25-34': 0.4, '35-44': 0.2},
                'geographic_hotspots': ['US', 'UK', 'CA'],
                'hashtags': ['#AI2025', '#TechTrends', '#FutureTech'],
                'influencers': ['@techguru', '@aiexpert', '@futurist']
            },
            {
                'name': 'Sustainability Challenge',
                'score': 0.8,
                'growth_rate': 0.12,
                'platform_distribution': {'instagram': 0.5, 'tiktok': 0.3, 'youtube': 0.2},
                'content_types': ['lifestyle', 'tutorial', 'challenge'],
                'demographics': {'18-24': 0.5, '25-34': 0.3, '35-44': 0.2},
                'geographic_hotspots': ['US', 'DE', 'AU'],
                'hashtags': ['#SustainableLife', '#EcoChallenge', '#GreenLiving'],
                'influencers': ['@ecoliving', '@sustainableguru', '@greentips']
            },
            {
                'name': 'Fitness Transformation',
                'score': 0.75,
                'growth_rate': 0.08,
                'platform_distribution': {'instagram': 0.4, 'tiktok': 0.4, 'youtube': 0.2},
                'content_types': ['transformation', 'workout', 'motivation'],
                'demographics': {'18-24': 0.3, '25-34': 0.5, '35-44': 0.2},
                'geographic_hotspots': ['US', 'UK', 'AU'],
                'hashtags': ['#FitnessTransformation', '#WorkoutMotivation', '#HealthyLife'],
                'influencers': ['@fitnessguru', '@workoutqueen', '@healthylifestyle']
            }
        ]
        
        return trending_topics
    
    async def _determine_lifecycle_stage(self, topic_data: Dict[str, Any]) -> str:
        """Determine trend lifecycle stage"""
        growth_rate = topic_data['growth_rate']
        
        if growth_rate > 0.1:
            return "growing"
        elif growth_rate > 0.05:
            return "peak"
        elif growth_rate > 0:
            return "declining"
        else:
            return "emerging"
    
    async def _estimate_trend_lifespan(self, topic_data: Dict[str, Any]) -> int:
        """Estimate trend lifespan in days"""
        growth_rate = topic_data['growth_rate']
        
        if growth_rate > 0.15:
            return 3  # Very fast trends die quickly
        elif growth_rate > 0.1:
            return 7  # Standard viral trend
        elif growth_rate > 0.05:
            return 14  # Longer lasting trends
        else:
            return 30  # Slow-growing, longer-lasting trends
    
    async def _calculate_monetization_potential(self, topic_data: Dict[str, Any]) -> float:
        """Calculate monetization potential for trend"""
        # Factors: audience size, engagement level, commercial appeal
        demographics = topic_data['demographics']
        
        # Higher value demographics (25-44 age group)
        valuable_demo_percentage = demographics.get('25-34', 0) + demographics.get('35-44', 0)
        
        # Platform commercial potential
        platform_dist = topic_data['platform_distribution']
        commercial_potential = (
            platform_dist.get('youtube', 0) * 1.0 +
            platform_dist.get('instagram', 0) * 0.8 +
            platform_dist.get('tiktok', 0) * 0.6
        )
        
        monetization_score = (valuable_demo_percentage * 0.6) + (commercial_potential * 0.4)
        return min(monetization_score, 1.0)
    
    # Optimization methods
    async def _optimize_title(self, content_data: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Optimize title for platform"""
        current_title = content_data.get('title', '')
        
        suggestions = {
            'current_title': current_title,
            'optimized_titles': [],
            'improvements': []
        }
        
        # Generate optimized titles based on platform
        if platform == PlatformType.TIKTOK:
            suggestions['optimized_titles'] = [
                f"You Won't Believe What Happened! {current_title}",
                f"This {current_title} Change Everything 🤯",
                f"POV: {current_title} Goes Viral"
            ]
            suggestions['improvements'] = [
                "Add emotional hooks",
                "Use trending expressions",
                "Include emojis"
            ]
        
        return suggestions
    
    async def _optimize_content_structure(self, content_data: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Optimize content structure for platform"""
        return {
            'hook_suggestions': [
                "Start with surprising statement",
                "Ask engaging question",
                "Use pattern interrupt"
            ],
            'structure_tips': [
                "Front-load value",
                "Use clear progression",
                "End with call-to-action"
            ]
        }
    
    async def _optimize_hashtags(self, content_data: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Optimize hashtags for platform"""
        trending_hashtags = await self._get_trending_hashtags(platform)
        
        return {
            'trending_hashtags': trending_hashtags,
            'strategy': 'Mix of trending and niche hashtags',
            'optimal_count': self._get_optimal_hashtag_count(platform)
        }
    
    async def _optimize_timing_strategy(self, content_data: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Optimize timing strategy"""
        return {
            'optimal_days': ['Monday', 'Wednesday', 'Friday'],
            'optimal_hours': [18, 19, 20],
            'timezone_considerations': 'Target audience timezone',
            'frequency_recommendations': 'Daily for TikTok, 3-4x/week for others'
        }
    
    async def _get_platform_specific_tips(self, platform: PlatformType) -> List[str]:
        """Get platform-specific optimization tips"""
        tips = {
            PlatformType.TIKTOK: [
                "Use trending sounds and effects",
                "Keep videos 15-60 seconds",
                "Start with hook in first 3 seconds",
                "Use vertical video format",
                "Post consistently daily"
            ],
            PlatformType.INSTAGRAM: [
                "Use high-quality visuals",
                "Mix feed posts and stories",
                "Engage with comments quickly",
                "Use Instagram Reels for reach",
                "Optimize bio and highlights"
            ],
            PlatformType.YOUTUBE: [
                "Create compelling thumbnails",
                "Use SEO-optimized titles",
                "Add timestamps and chapters",
                "Encourage subscriptions",
                "Use end screens effectively"
            ]
        }
        
        return tips.get(platform, ["Focus on high-quality content"])
    
    async def _suggest_trend_integration(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest trend integration strategies"""
        return {
            'current_trends': ['AI technology', 'sustainability', 'wellness'],
            'integration_methods': [
                "Reference trends in content",
                "Use trending hashtags",
                "Collaborate with trend creators"
            ],
            'timing_advice': "Jump on trends early but not too early"
        }
    
    async def _generate_engagement_hooks(self, content_data: Dict[str, Any], platform: PlatformType) -> List[str]:
        """Generate engagement hooks"""
        hooks = [
            "Wait for it...",
            "You won't believe what happens next",
            "This changed everything",
            "Nobody talks about this but...",
            "The secret that everyone should know"
        ]
        
        return hooks[:5]
    
    async def _suggest_visual_optimizations(self, content_data: Dict[str, Any], platform: PlatformType) -> Dict[str, Any]:
        """Suggest visual optimizations"""
        return {
            'aspect_ratio': '9:16 for TikTok/Instagram, 16:9 for YouTube',
            'thumbnail_tips': ['Bright colors', 'Clear text', 'Expressive faces'],
            'visual_elements': ['Captions', 'Graphics', 'Transitions'],
            'lighting_tips': ['Natural light preferred', 'Avoid harsh shadows']
        }
    
    async def _estimate_optimization_impact(self, current_prediction: ViralPrediction, target_score: float) -> Dict[str, Any]:
        """Estimate impact of optimizations"""
        current_score = current_prediction.viral_score
        improvement_potential = target_score - current_score
        
        return {
            'estimated_score_increase': improvement_potential,
            'estimated_reach_increase': f"{improvement_potential * 100:.0f}%",
            'optimization_difficulty': 'medium' if improvement_potential < 0.3 else 'high',
            'time_to_implement': '1-2 hours' if improvement_potential < 0.2 else '4-6 hours'
        }
    
    # Helper methods
    async def _get_trending_hashtags(self, platform: PlatformType) -> List[str]:
        """Get trending hashtags for platform"""
        trending_hashtags = {
            PlatformType.TIKTOK: ['#fyp', '#viral', '#trending', '#foryou', '#tiktok'],
            PlatformType.INSTAGRAM: ['#instagram', '#instagood', '#photooftheday', '#love', '#fashion'],
            PlatformType.YOUTUBE: ['#youtube', '#viral', '#trending', '#subscribe', '#like']
        }
        
        return trending_hashtags.get(platform, ['#trending', '#viral'])
    
    def _get_optimal_hashtag_count(self, platform: PlatformType) -> int:
        """Get optimal hashtag count for platform"""
        optimal_counts = {
            PlatformType.TIKTOK: 5,
            PlatformType.INSTAGRAM: 10,
            PlatformType.YOUTUBE: 3,
            PlatformType.TWITTER: 2,
            PlatformType.FACEBOOK: 2
        }
        
        return optimal_counts.get(platform, 5)
    
    async def _initialize_models(self):
        """Initialize ML models with synthetic training data"""
        try:
            # Generate synthetic training data
            X, y = await self._generate_training_data()
            
            if len(X) > 10:  # Ensure we have enough data
                # Train viral classifier
                self.viral_classifier.fit(X, y)
                
                # Train engagement predictor
                engagement_y = [score * 0.1 + np.random.normal(0, 0.02) for score in y]
                self.engagement_predictor.fit(X, engagement_y)
                
                logger.info("ML models initialized successfully")
            else:
                logger.warning("Insufficient training data for ML models")
                
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
    
    async def _generate_training_data(self) -> Tuple[List[List[float]], List[float]]:
        """Generate synthetic training data for ML models"""
        X, y = [], []
        
        # Generate 100 synthetic content examples
        for _ in range(100):
            features = [
                np.random.uniform(0, 100),  # word_count
                np.random.uniform(0, 20),   # hashtag_count
                np.random.uniform(0, 10),   # mention_count
                np.random.uniform(0, 10),   # emoji_count
                np.random.uniform(0, 5),    # question_count
                np.random.uniform(0, 5),    # exclamation_count
                np.random.uniform(0, 1),    # caps_lock_ratio
                np.random.uniform(-1, 1),   # sentiment_score
                np.random.uniform(0, 1),    # readability_score
                np.random.uniform(0, 1),    # urgency_score
                np.random.uniform(0, 1),    # excitement
                np.random.uniform(0, 1),    # humor
                np.random.uniform(0, 1),    # trending_alignment
                np.random.uniform(0, 1),    # timing_score
                np.random.uniform(0, 1),    # platform_fit
                np.random.uniform(0, 1),    # creator_authority
                np.random.uniform(0, 1)     # audience_size (normalized)
            ]
            
            # Generate viral score based on features (synthetic relationship)
            viral_score = (
                features[6] * 0.1 +   # sentiment
                features[9] * 0.2 +   # urgency
                features[10] * 0.2 +  # excitement
                features[12] * 0.3 +  # trending
                features[15] * 0.2    # creator authority
            ) + np.random.normal(0, 0.1)
            
            viral_score = max(0, min(1, viral_score))
            
            X.append(features)
            y.append(viral_score)
        
        return X, y
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """Get summary of all predictions"""
        try:
            if not self.predictions:
                return {"total_predictions": 0}
            
            viral_scores = [p.viral_score for p in self.predictions.values()]
            virality_levels = [p.virality_level.value for p in self.predictions.values()]
            
            return {
                "total_predictions": len(self.predictions),
                "average_viral_score": statistics.mean(viral_scores),
                "highest_viral_score": max(viral_scores),
                "virality_distribution": dict(Counter(virality_levels)),
                "high_potential_content": len([s for s in viral_scores if s >= 0.7]),
                "total_predicted_reach": sum(p.predicted_reach for p in self.predictions.values())
            }
            
        except Exception as e:
            logger.error(f"Error generating prediction summary: {str(e)}")
            return {"error": str(e)}


# Example usage
async def main():
    """Example usage of Viral Content Predictor"""
    try:
        # Initialize predictor
        config = {
            'min_viral_score': 0.6,
            'confidence_threshold': 0.7,
            'trending_weight': 0.3
        }
        
        predictor = ViralContentPredictor(config)
        
        # Example content data
        content_data = {
            'id': 'content_001',
            'title': 'Amazing AI Tool That Changes Everything!',
            'description': 'This new AI technology will revolutionize how we work. You need to see this! #AI #Technology #Viral',
            'type': 'video',
            'duration': 45,
            'category': 'technology',
            'platform': 'tiktok',
            'creator_authority': 0.8,
            'follower_count': 50000
        }
        
        print(f"🤖 Predicting viral potential for: {content_data['title']}")
        
        # Predict viral potential
        prediction = await predictor.predict_viral_potential(
            content_data=content_data,
            target_platforms=[PlatformType.TIKTOK, PlatformType.INSTAGRAM],
            optimization_mode=True
        )
        
        # Print results
        print(f"\n📊 Viral Prediction Results:")
        print(f"   Viral Score: {prediction.viral_score:.2f}")
        print(f"   Virality Level: {prediction.virality_level.value}")
        print(f"   Confidence: {prediction.prediction_confidence:.2f}")
        print(f"   Predicted Reach: {prediction.predicted_reach:,}")
        print(f"   Predicted Engagement Rate: {prediction.predicted_engagement_rate:.1%}")
        print(f"   Predicted Likes: {prediction.predicted_likes:,}")
        print(f"   Predicted Shares: {prediction.predicted_shares:,}")
        
        # Show platform scores
        print(f"\n🎯 Platform Scores:")
        for platform, score in prediction.platform_scores.items():
            print(f"   {platform}: {score:.2f}")
        
        # Show viral factors
        print(f"\n✅ Viral Factors:")
        for factor in prediction.viral_factors:
            print(f"   • {factor}")
        
        # Show optimization suggestions
        print(f"\n💡 Optimization Suggestions:")
        for suggestion in prediction.optimization_suggestions[:5]:
            print(f"   • {suggestion}")
        
        # Analyze viral trends
        print(f"\n📈 Analyzing viral trends...")
        trends = await predictor.analyze_viral_trends(
            platforms=[PlatformType.TIKTOK, PlatformType.INSTAGRAM],
            time_range_days=7
        )
        
        print(f"\n🔥 Top Viral Trends:")
        for i, trend in enumerate(trends[:3]):
            print(f"\n{i+1}. {trend.trend_name}")
            print(f"   Trend Score: {trend.trend_score:.2f}")
            print(f"   Growth Rate: {trend.growth_rate:.1%}")
            print(f"   Lifecycle Stage: {trend.trend_lifecycle_stage}")
            print(f"   Hashtags: {', '.join(trend.related_hashtags[:3])}")
        
        # Optimize content for virality
        print(f"\n🚀 Optimizing content for virality...")
        optimizations = await predictor.optimize_content_for_virality(
            content_data=content_data,
            target_viral_score=0.9,
            target_platform=PlatformType.TIKTOK
        )
        
        print(f"\n⚡ Optimization Results:")
        print(f"   Current Score: {optimizations.get('current_score', 0):.2f}")
        print(f"   Target Score: {optimizations.get('target_score', 0):.2f}")
        print(f"   Improvement Needed: {optimizations.get('improvement_needed', 0):.2f}")
        
        # Show title optimizations
        title_opts = optimizations.get('title_optimizations', {})
        if 'optimized_titles' in title_opts:
            print(f"\n📝 Optimized Titles:")
            for title in title_opts['optimized_titles'][:2]:
                print(f"   • {title}")
        
        # Get summary
        summary = predictor.get_prediction_summary()
        print(f"\n📊 Summary:")
        print(f"   Total Predictions: {summary['total_predictions']}")
        print(f"   Average Viral Score: {summary.get('average_viral_score', 0):.2f}")
        print(f"   High Potential Content: {summary.get('high_potential_content', 0)}")
        
        print("\n✅ Viral Content Prediction completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())