"""Engagement Optimizer - Enterprise AI-Powered Multi-Modal Engagement Optimization Engine

Advanced machine learning-driven engagement prediction, content optimization, audience behavior analysis,
sentiment analysis, trending topic detection, and real-time engagement maximization across all social
media platforms with integrated content protection and monetization optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This engagement optimization system and AI algorithms are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization without 
explicit written permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries only.

Expert Development Team Specialties:
- Lead AI Developer & ML Engineer - Advanced ML algorithms and neural network optimization
- Backend Senior Architect - Enterprise-level engagement processing architecture
- Database Administrator (DBA) - Engagement data modeling and performance optimization
- Security & Microservices Expert - Secure engagement tracking and distributed processing
- Audio Processing Specialist - Audio content engagement analysis and optimization
- DevOps & Infrastructure Engineer - Engagement monitoring and scalable infrastructure
- AI Prompt Engineering Expert - Natural language processing and content generation
- Content Protection Specialist - Protected content engagement tracking and optimization
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, classification_report
import nltk
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import re
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class EngagementMetric(Enum):
    """
Comprehensive engagement metrics across all platforms"""
    # Basic Engagement
    LIKES = "likes"
    SHARES = "shares" 
    COMMENTS = "comments"
    VIEWS = "views"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    
    # Advanced Engagement
    SAVES = "saves"
    BOOKMARKS = "bookmarks"
    CLICKS = "clicks"
    PROFILE_VISITS = "profile_visits"
    WEBSITE_CLICKS = "website_clicks"
    EMAIL_CONTACTS = "email_contacts"
    PHONE_CALLS = "phone_calls"
    DIRECTIONS = "directions"
    
    # Video-Specific Metrics
    WATCH_TIME = "watch_time"
    AVERAGE_VIEW_DURATION = "average_view_duration"
    VIEW_RETENTION = "view_retention"
    COMPLETION_RATE = "completion_rate"
    REPLAYS = "replays"
    
    # Story-Specific Metrics
    STORY_EXITS = "story_exits"
    STORY_REPLIES = "story_replies"
    STORY_TAPS_FORWARD = "story_taps_forward"
    STORY_TAPS_BACK = "story_taps_back"
    
    # E-commerce Metrics
    PRODUCT_CLICKS = "product_clicks"
    ADD_TO_CART = "add_to_cart"
    PURCHASES = "purchases"
    REVENUE = "revenue"
    
    # Community Metrics
    MENTIONS = "mentions"
    HASHTAG_USES = "hashtag_uses"
    USER_GENERATED_CONTENT = "user_generated_content"
    BRAND_MENTIONS = "brand_mentions"
    
    # Engagement Quality
    SENTIMENT_SCORE = "sentiment_score"
    ENGAGEMENT_RATE = "engagement_rate"
    VIRAL_COEFFICIENT = "viral_coefficient"
    AUDIENCE_QUALITY_SCORE = "audience_quality_score"

class OptimizationStrategy(Enum):
    """AI optimization strategies for different objectives"""

    MAXIMIZE_ENGAGEMENT = "maximize_engagement"
    MAXIMIZE_REACH = "maximize_reach"
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    MAXIMIZE_REVENUE = "maximize_revenue"
    MAXIMIZE_BRAND_AWARENESS = "maximize_brand_awareness"
    MAXIMIZE_AUDIENCE_GROWTH = "maximize_audience_growth"
    MAXIMIZE_RETENTION = "maximize_retention"
    MAXIMIZE_VIRAL_POTENTIAL = "maximize_viral_potential"
    MINIMIZE_NEGATIVE_SENTIMENT = "minimize_negative_sentiment"
    BALANCE_ALL_METRICS = "balance_all_metrics"

class ContentOptimizationType(Enum):
    """Types of content optimization techniques"""

    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    CAPTION_OPTIMIZATION = "caption_optimization"
    TIMING_OPTIMIZATION = "timing_optimization"
    VISUAL_OPTIMIZATION = "visual_optimization"
    AUDIO_OPTIMIZATION = "audio_optimization"
    TRENDING_INTEGRATION = "trending_integration"
    AUDIENCE_TARGETING = "audience_targeting"
    PLATFORM_ADAPTATION = "platform_adaptation"
    SENTIMENT_ENHANCEMENT = "sentiment_enhancement"
    CALL_TO_ACTION_OPTIMIZATION = "call_to_action_optimization"

class MLModelType(Enum):
    """Machine learning models for engagement prediction"""

    GRADIENT_BOOSTING = "gradient_boosting"
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"
    TRANSFORMER = "transformer"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    DEEP_LEARNING = "deep_learning"
    VIEWS = "views"
    CLICKS = "clicks"
    SAVES = "saves"
    REACH = "reach"
    IMPRESSIONS = "impressions"

class OptimizationTarget(Enum):
    """Optimization targets"""

    ENGAGEMENT_RATE = "engagement_rate"
    REACH_MAXIMIZATION = "reach_maximization"
    CONVERSION_RATE = "conversion_rate"
    BRAND_AWARENESS = "brand_awareness"
    CLICK_THROUGH_RATE = "click_through_rate"
    VIRAL_POTENTIAL = "viral_potential"

class ContentCategory(Enum):
    """Content categories for optimization"""

    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"
    NEWS = "news"
    PERSONAL = "personal"
    BEHIND_SCENES = "behind_scenes"
    USER_GENERATED = "user_generated"
    TRENDING = "trending"

@dataclass
class EngagementData:
    """Historical engagement data point"""
    content_id: str
    platform: str
    timestamp: datetime
    metrics: Dict[EngagementMetric, int]
    content_features: Dict[str, Any]
    audience_features: Dict[str, Any]
    engagement_rate: float
    reach_rate: float
    virality_score: float = 0.0

@dataclass
class OptimizationRecommendation:
    """
Content optimization recommendation"""
    aspect: str  # hashtags, timing, content_type, etc.
    current_value: Any
    recommended_value: Any
    expected_improvement: float
    confidence: float
    reasoning: str
    priority: int  # 1=high, 5=low

@dataclass
class ContentAnalysis:
    """
Comprehensive content analysis"""
    content_id: str
    platform: str
    predicted_engagement: Dict[EngagementMetric, float]
    optimization_score: float
    recommendations: List[OptimizationRecommendation]
    audience_fit: float
    viral_potential: float
    optimal_posting_time: datetime
    suggested_hashtags: List[str]
    content_improvements: List[str]
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

class ContentFeatureExtractor:
    """
Extract features from content for ML analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.tokenizer = None
        self.text_classifier = None
        self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """
Initialize NLP models for content analysis"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {str(e)}")
    
    def extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text content"""
        features = {}
        
        if not text:
            return features
        
        # Basic text statistics
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(text.split('.'))
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        
        # Hashtag and mention analysis
        hashtags = re.findall(r'#\w+', text)
        mentions = re.findall(r'@\w+', text)
        
        features['hashtag_count'] = len(hashtags)
        features['mention_count'] = len(mentions)
        features['has_hashtags'] = len(hashtags) > 0
        features['has_mentions'] = len(mentions) > 0
        
        # URL and emoji detection
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        emojis = re.findall(r'[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff]', text)
        
        features['url_count'] = len(urls)
        features['emoji_count'] = len(emojis)
        features['has_urls'] = len(urls) > 0
        features['has_emojis'] = len(emojis) > 0
        
        # Sentiment analysis
        try:
            if self.sentiment_analyzer:
                sentiment_scores = self.sentiment_analyzer(text[:512])  # Limit for model
                if sentiment_scores and sentiment_scores[0]:
                    for score_data in sentiment_scores[0]:
                        features[f'sentiment_{score_data["label"].lower()}'] = score_data["score"]
            
            # TextBlob sentiment as backup
            blob = TextBlob(text)
            features['polarity'] = blob.sentiment.polarity
            features['subjectivity'] = blob.sentiment.subjectivity
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {str(e)}")
            features['polarity'] = 0.0
            features['subjectivity'] = 0.0
        
        # Language complexity
        try:
            words = text.lower().split()
            unique_words = set(words)
            features['vocabulary_diversity'] = len(unique_words) / len(words) if words else 0
            features['avg_syllables'] = self._estimate_syllables(text)
            features['readability_score'] = self._calculate_readability(text)
        except:
            features['vocabulary_diversity'] = 0
            features['avg_syllables'] = 0
            features['readability_score'] = 0
        
        # Question and exclamation detection
        features['question_count'] = text.count('?')
        features['exclamation_count'] = text.count('!')
        features['has_questions'] = '?' in text
        features['has_exclamations'] = '!' in text
        
        return features
    
    def _estimate_syllables(self, text: str) -> float:
        """Estimate average syllables per word"""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0
        
        total_syllables = 0
        for word in words:
            syllables = max(1, len(re.findall(r'[aeiouy]+', word)))
            total_syllables += syllables
        
        return total_syllables / len(words)
    
    def _calculate_readability(self, text: str) -> float:
        """
Calculate readability score (simplified Flesch score)"""
        sentences = len(text.split('.'))
        words = len(text.split())
        syllables = sum(max(1, len(re.findall(r'[aeiouy]+', word.lower()))) 
                       for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0
        
        # Simplified Flesch Reading Ease score
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))
    
    def extract_media_features(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract features from media content"""
        features = {}
        
        media_types = media_data.get('types', [])
        media_count = media_data.get('count', 0)
        
        features['media_count'] = media_count
        features['has_media'] = media_count > 0
        features['has_video'] = 'video' in media_types
        features['has_image'] = 'image' in media_types
        features['has_audio'] = 'audio' in media_types
        features['media_type_diversity'] = len(set(media_types))
        
        # Video-specific features
        if 'video' in media_types:
            features['video_duration'] = media_data.get('video_duration', 0)
            features['video_quality'] = media_data.get('video_quality', 'standard')
            features['has_sound'] = media_data.get('has_sound', True)
        
        # Image-specific features
        if 'image' in media_types:
            features['image_count'] = media_data.get('image_count', 0)
            features['image_quality'] = media_data.get('image_quality', 'standard')
            features['has_filters'] = media_data.get('has_filters', False)
        
        return features
    
    def extract_timing_features(self, timestamp: datetime) -> Dict[str, Any]:
        """
Extract timing-related features"""
        features = {}
        
        features['hour'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        features['day_of_month'] = timestamp.day
        features['month'] = timestamp.month
        features['quarter'] = (timestamp.month - 1) // 3 + 1
        features['is_weekend'] = timestamp.weekday() >= 5
        features['is_morning'] = 6 <= timestamp.hour < 12
        features['is_afternoon'] = 12 <= timestamp.hour < 18
        features['is_evening'] = 18 <= timestamp.hour < 22
        features['is_night'] = timestamp.hour >= 22 or timestamp.hour < 6
        
        # Business hours
        features['is_business_hours'] = 9 <= timestamp.hour <= 17
        features['is_prime_time'] = 19 <= timestamp.hour <= 22
        
        return features

class EngagementPredictor:
    """
ML model for predicting engagement metrics"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_columns: Dict[str, List[str]] = {}
        self.training_history: List[Dict[str, Any]] = []
        
    def train_engagement_model(self, training_data: List[EngagementData], 
                             target_metric: EngagementMetric) -> bool:
        """
Train ML model to predict engagement metrics"""
        try:
            if len(training_data) < 100:
                logger.warning(f"Insufficient data for training {target_metric.value} model")
                return False
            
            # Prepare training data
            df = self._prepare_training_dataframe(training_data, target_metric)
            
            if df.empty:
                return False
            
            # Features and target
            feature_cols = [col for col in df.columns if col not in ['target', 'content_id', 'platform']]
            X = df[feature_cols]
            y = df['target']
            
            # Handle missing values
            X = X.fillna(0)
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Store model and metadata
            model_key = target_metric.value
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            self.feature_columns[model_key] = feature_cols
            
            # Log training results
            training_result = {
                'metric': target_metric.value,
                'train_score': train_score,
                'test_score': test_score,
                'mae': mae,
                'data_points': len(training_data),
                'features': len(feature_cols),
                'trained_at': datetime.utcnow().isoformat()
            }
            self.training_history.append(training_result)
            
            logger.info(f"Trained {target_metric.value} model - Test Score: {test_score:.3f}, MAE: {mae:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train {target_metric.value} model: {str(e)}")
            return False
    
    def _prepare_training_dataframe(self, training_data: List[EngagementData], 
                                  target_metric: EngagementMetric) -> pd.DataFrame:
        """Prepare DataFrame for model training"""
        records = []
        
        for data in training_data:
            record = {
                'content_id': data.content_id,
                'platform': data.platform,
                'target': data.metrics.get(target_metric, 0)
            }
            
            # Add all features
            record.update(data.content_features)
            record.update(data.audience_features)
            
            # Add derived features
            record['engagement_rate'] = data.engagement_rate
            record['reach_rate'] = data.reach_rate
            record['virality_score'] = data.virality_score
            
            records.append(record)
        
        df = pd.DataFrame(records)
        
        # Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in ['content_id', 'platform']:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
        
        return df
    
    def predict_engagement(self, content_features: Dict[str, Any], 
                         metrics: List[EngagementMetric]) -> Dict[EngagementMetric, float]:
        """
Predict engagement for given content features"""
        predictions = {}
        
        for metric in metrics:
            model_key = metric.value
            
            if model_key not in self.models:
                predictions[metric] = 0.0
                continue
            
            try:
                model = self.models[model_key]
                scaler = self.scalers[model_key]
                feature_cols = self.feature_columns[model_key]
                
                # Prepare features
                feature_values = []
                for col in feature_cols:
                    value = content_features.get(col, 0)
                    if isinstance(value, str):
                        # Handle categorical values (simple hash-based encoding)
                        value = hash(value) % 1000
                    feature_values.append(float(value))
                
                # Scale and predict
                X = np.array([feature_values])
                X_scaled = scaler.transform(X)
                prediction = model.predict(X_scaled)[0]
                
                predictions[metric] = max(0, prediction)  # Ensure non-negative
                
            except Exception as e:
                logger.error(f"Prediction failed for {metric.value}: {str(e)}")
                predictions[metric] = 0.0
        
        return predictions

class HashtagOptimizer:
    """Optimize hashtags for maximum engagement"""
    
    def __init__(self):
        self.hashtag_performance: Dict[str, Dict[str, float]] = {}
        self.trending_hashtags: Dict[str, List[str]] = {}
        self.hashtag_combinations: Dict[str, Dict[str, float]] = {}
    
    def analyze_hashtag_performance(self, engagement_data: List[EngagementData]):
        """
Analyze hashtag performance across historical data"""
        platform_stats = {}
        
        for data in engagement_data:
            platform = data.platform
            if platform not in platform_stats:
                platform_stats[platform] = {}
            
            hashtags = data.content_features.get('hashtags', [])
            total_engagement = sum(data.metrics.values())
            
            for hashtag in hashtags:
                if hashtag not in platform_stats[platform]:
                    platform_stats[platform][hashtag] = {
                        'total_engagement': 0,
                        'post_count': 0,
                        'avg_engagement': 0
                    }
                
                platform_stats[platform][hashtag]['total_engagement'] += total_engagement
                platform_stats[platform][hashtag]['post_count'] += 1
        
        # Calculate average performance
        for platform, hashtags in platform_stats.items():
            for hashtag, stats in hashtags.items():
                if stats['post_count'] > 0:
                    stats['avg_engagement'] = stats['total_engagement'] / stats['post_count']
        
        self.hashtag_performance = platform_stats
    
    def get_optimal_hashtags(self, platform: str, content_category: ContentCategory,
                           current_hashtags: List[str], count: int = 10) -> List[str]:
        """
Get optimal hashtags for given content"""
        if platform not in self.hashtag_performance:
            return current_hashtags[:count]
        
        platform_hashtags = self.hashtag_performance[platform]
        
        # Score hashtags
        hashtag_scores = {}
        for hashtag, stats in platform_hashtags.items():
            if stats['post_count'] >= 5:  # Minimum posts for reliability
                score = stats['avg_engagement']
                
                # Boost score for category relevance
                if self._is_relevant_to_category(hashtag, content_category):
                    score *= 1.2
                
                # Penalize overused hashtags
                if stats['post_count'] > 1000:
                    score *= 0.8
                
                hashtag_scores[hashtag] = score
        
        # Sort by score and select top hashtags
        sorted_hashtags = sorted(hashtag_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Combine with current hashtags
        optimal_hashtags = current_hashtags.copy()
        
        for hashtag, score in sorted_hashtags:
            if hashtag not in optimal_hashtags and len(optimal_hashtags) < count:
                optimal_hashtags.append(hashtag)
        
        return optimal_hashtags[:count]
    
    def _is_relevant_to_category(self, hashtag: str, category: ContentCategory) -> bool:
        """
Check if hashtag is relevant to content category"""
        category_keywords = {
            ContentCategory.EDUCATIONAL: ['learn', 'tip', 'how', 'guide', 'tutorial', 'knowledge'],
            ContentCategory.ENTERTAINMENT: ['fun', 'funny', 'comedy', 'entertainment', 'viral'],
            ContentCategory.PROMOTIONAL: ['sale', 'offer', 'deal', 'discount', 'promotion'],
            ContentCategory.NEWS: ['news', 'breaking', 'update', 'latest', 'today'],
            ContentCategory.PERSONAL: ['life', 'personal', 'story', 'experience', 'journey'],
            ContentCategory.TRENDING: ['trending', 'viral', 'popular', 'hot', 'buzz']
        }
        
        keywords = category_keywords.get(category, [])
        hashtag_lower = hashtag.lower()
        
        return any(keyword in hashtag_lower for keyword in keywords)
    
    def suggest_hashtag_combinations(self, platform: str, base_hashtags: List[str],
                                   max_combinations: int = 5) -> List[List[str]]:
        """
Suggest effective hashtag combinations"""
        if platform not in self.hashtag_performance:
            return [base_hashtags]
        
        # Find hashtags that perform well together
        platform_hashtags = list(self.hashtag_performance[platform].keys())
        high_performing = [h for h, stats in self.hashtag_performance[platform].items()
                          if stats['avg_engagement'] > statistics.median([s['avg_engagement'] 
                                                                         for s in self.hashtag_performance[platform].values()])]
        
        combinations = []
        
        # Base combination
        combinations.append(base_hashtags)
        
        # Add high-performing hashtags
        for i in range(min(max_combinations - 1, len(high_performing))):
            combo = base_hashtags.copy()
            combo.extend(high_performing[i:i+3])  # Add 3 high-performing hashtags
            combinations.append(combo[:20])  # Limit total hashtags
        
        return combinations

class EngagementOptimizer:
    """
    Advanced AI-Powered Engagement Optimization Engine
    Combines ML predictions, content analysis, and strategic recommendations for maximum engagement
    """
    
    def __init__(self):
        self.feature_extractor = ContentFeatureExtractor()
        self.engagement_predictor = EngagementPredictor()
        self.hashtag_optimizer = HashtagOptimizer()
        self.historical_data: List[EngagementData] = []
        self.optimization_cache: Dict[str, ContentAnalysis] = {}
        self.platform_benchmarks: Dict[str, Dict[str, float]] = {}
        
    async def initialize(self, historical_data: List[EngagementData] = None):
        """
Initialize optimizer with historical data"""
        if historical_data:
            self.historical_data = historical_data
            await self._train_models()
            self._calculate_benchmarks()
            logger.info(f"Engagement optimizer initialized with {len(historical_data)} data points")
    
    async def _train_models(self):
        """Train all ML models with historical data"""
        if len(self.historical_data) < 100:
            logger.warning("Insufficient data for model training")
            return
        
        # Train engagement prediction models
        metrics_to_train = [
            EngagementMetric.LIKES,
            EngagementMetric.SHARES,
            EngagementMetric.COMMENTS,
            EngagementMetric.VIEWS
        ]
        
        for metric in metrics_to_train:
            await asyncio.to_thread(
                self.engagement_predictor.train_engagement_model,
                self.historical_data,
                metric
            )
        
        # Analyze hashtag performance
        await asyncio.to_thread(
            self.hashtag_optimizer.analyze_hashtag_performance,
            self.historical_data
        )
    
    def _calculate_benchmarks(self):
        """Calculate platform-specific performance benchmarks"""
        platform_data = {}
        
        for data in self.historical_data:
            platform = data.platform
            if platform not in platform_data:
                platform_data[platform] = {
                    'engagement_rates': [],
                    'reach_rates': [],
                    'virality_scores': []
                }
            
            platform_data[platform]['engagement_rates'].append(data.engagement_rate)
            platform_data[platform]['reach_rates'].append(data.reach_rate)
            platform_data[platform]['virality_scores'].append(data.virality_score)
        
        # Calculate benchmarks
        for platform, data in platform_data.items():
            self.platform_benchmarks[platform] = {
                'avg_engagement_rate': np.mean(data['engagement_rates']),
                'median_engagement_rate': np.median(data['engagement_rates']),
                'top_quartile_engagement': np.percentile(data['engagement_rates'], 75),
                'avg_reach_rate': np.mean(data['reach_rates']),
                'avg_virality_score': np.mean(data['virality_scores'])
            }
    
    async def analyze_content(self, content_id: str, platform: str, text: str,
                            media_data: Dict[str, Any] = None,
                            current_hashtags: List[str] = None,
                            target_audience: Dict[str, Any] = None) -> ContentAnalysis:
        """
Comprehensive content analysis and optimization"""
        
        # Extract content features
        text_features = self.feature_extractor.extract_text_features(text)
        media_features = self.feature_extractor.extract_media_features(media_data or {})
        timing_features = self.feature_extractor.extract_timing_features(datetime.utcnow())
        
        # Combine all features
        all_features = {**text_features, **media_features, **timing_features}
        if target_audience:
            all_features.update(target_audience)
        
        # Predict engagement
        metrics_to_predict = [
            EngagementMetric.LIKES,
            EngagementMetric.SHARES,
            EngagementMetric.COMMENTS,
            EngagementMetric.VIEWS
        ]
        
        predicted_engagement = self.engagement_predictor.predict_engagement(
            all_features, metrics_to_predict
        )
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            predicted_engagement, platform
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            all_features, predicted_engagement, platform, text, 
            current_hashtags or [], media_data or {}
        )
        
        # Calculate audience fit
        audience_fit = self._calculate_audience_fit(all_features, target_audience or {})
        
        # Calculate viral potential
        viral_potential = self._calculate_viral_potential(predicted_engagement, all_features)
        
        # Suggest optimal posting time
        optimal_time = self._suggest_optimal_time(platform, all_features)
        
        # Optimize hashtags
        suggested_hashtags = self.hashtag_optimizer.get_optimal_hashtags(
            platform, ContentCategory.GENERAL, current_hashtags or [], count=15
        )
        
        # Generate content improvements
        content_improvements = await self._suggest_content_improvements(
            text, all_features, predicted_engagement
        )
        
        analysis = ContentAnalysis(
            content_id=content_id,
            platform=platform,
            predicted_engagement=predicted_engagement,
            optimization_score=optimization_score,
            recommendations=recommendations,
            audience_fit=audience_fit,
            viral_potential=viral_potential,
            optimal_posting_time=optimal_time,
            suggested_hashtags=suggested_hashtags,
            content_improvements=content_improvements
        )
        
        # Cache analysis
        self.optimization_cache[content_id] = analysis
        
        return analysis
    
    def _calculate_optimization_score(self, predicted_engagement: Dict[EngagementMetric, float],
                                    platform: str) -> float:
        """
Calculate overall optimization score (0-100)"""
        if platform not in self.platform_benchmarks:
            return 50.0  # Default score
        
        benchmarks = self.platform_benchmarks[platform]
        
        # Calculate weighted engagement score
        total_predicted = sum(predicted_engagement.values())
        
        # Compare against benchmark
        avg_benchmark = benchmarks.get('avg_engagement_rate', 0.05) * 10000  # Scale up
        
        if avg_benchmark > 0:
            score = min(100, (total_predicted / avg_benchmark) * 50)
        else:
            score = 50.0
        
        return max(0, score)
    
    async def _generate_recommendations(self, features: Dict[str, Any], 
                                      predictions: Dict[EngagementMetric, float],
                                      platform: str, text: str, hashtags: List[str],
                                      media_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
Generate optimization recommendations"""
        recommendations = []
        
        # Text length optimization
        current_length = len(text)
        optimal_length = self._get_optimal_text_length(platform)
        
        if abs(current_length - optimal_length) > 50:
            recommendations.append(OptimizationRecommendation(
                aspect="text_length",
                current_value=current_length,
                recommended_value=optimal_length,
                expected_improvement=0.15,
                confidence=0.8,
                reasoning=f"Optimal text length for {platform} is around {optimal_length} characters",
                priority=2
            ))
        
        # Hashtag optimization
        if len(hashtags) < self._get_optimal_hashtag_count(platform):
            recommendations.append(OptimizationRecommendation(
                aspect="hashtags",
                current_value=len(hashtags),
                recommended_value=self._get_optimal_hashtag_count(platform),
                expected_improvement=0.25,
                confidence=0.9,
                reasoning=f"Add more relevant hashtags to increase discoverability",
                priority=1
            ))
        
        # Sentiment optimization
        polarity = features.get('polarity', 0)
        if polarity < 0.1:
            recommendations.append(OptimizationRecommendation(
                aspect="sentiment",
                current_value=f"Neutral/Negative ({polarity:.2f})",
                recommended_value="Positive (>0.3)",
                expected_improvement=0.20,
                confidence=0.7,
                reasoning="More positive content tends to get higher engagement",
                priority=2
            ))
        
        # Media recommendations
        if not media_data.get('types'):
            recommendations.append(OptimizationRecommendation(
                aspect="media",
                current_value="Text only",
                recommended_value="Add visual media",
                expected_improvement=0.40,
                confidence=0.9,
                reasoning="Posts with media get significantly higher engagement",
                priority=1
            ))
        
        # Timing recommendations
        current_hour = datetime.utcnow().hour
        optimal_hours = self._get_optimal_hours(platform)
        
        if current_hour not in optimal_hours:
            recommendations.append(OptimizationRecommendation(
                aspect="timing",
                current_value=f"{current_hour:02d}:00",
                recommended_value=f"{optimal_hours[0]:02d}:00-{optimal_hours[-1]:02d}:00",
                expected_improvement=0.18,
                confidence=0.75,
                reasoning="Post during peak engagement hours for better reach",
                priority=2
            ))
        
        return sorted(recommendations, key=lambda x: x.priority)
    
    def _get_optimal_text_length(self, platform: str) -> int:
        """Get optimal text length for platform"""
        optimal_lengths = {
            'twitter': 100,
            'instagram': 150,
            'facebook': 200,
            'linkedin': 300,
            'tiktok': 100
        }
        return optimal_lengths.get(platform.lower(), 150)
    
    def _get_optimal_hashtag_count(self, platform: str) -> int:
        """
Get optimal hashtag count for platform"""
        optimal_counts = {
            'twitter': 2,
            'instagram': 11,
            'facebook': 3,
            'linkedin': 5,
            'tiktok': 5
        }
        return optimal_counts.get(platform.lower(), 5)
    
    def _get_optimal_hours(self, platform: str) -> List[int]:
        """
Get optimal posting hours for platform"""
        optimal_hours = {
            'instagram': [11, 12, 13, 17, 18, 19],
            'facebook': [9, 10, 15, 20, 21],
            'twitter': [8, 9, 12, 17, 18],
            'linkedin': [7, 8, 9, 17, 18],
            'tiktok': [18, 19, 20, 21]
        }
        return optimal_hours.get(platform.lower(), [12, 18, 20])
    
    def _calculate_audience_fit(self, features: Dict[str, Any], 
                              target_audience: Dict[str, Any]) -> float:
        """
Calculate how well content fits target audience"""
        if not target_audience:
            return 0.7  # Default fit
        
        fit_score = 0.5  # Base score
        
        # Age group fit
        if 'age_group' in target_audience:
            content_complexity = features.get('readability_score', 50)
            age_group = target_audience['age_group']
            
            if age_group == 'young' and content_complexity < 60:
                fit_score += 0.2
            elif age_group == 'adult' and 40 <= content_complexity <= 70:
                fit_score += 0.2
            elif age_group == 'senior' and content_complexity > 60:
                fit_score += 0.2
        
        # Interest fit
        if 'interests' in target_audience:
            text_features = features.get('text_length', 0)
            interests = target_audience['interests']
            
            # Simple keyword matching (would be more sophisticated in practice)
            if 'technology' in interests and features.get('vocabulary_diversity', 0) > 0.7:
                fit_score += 0.1
            if 'entertainment' in interests and features.get('emoji_count', 0) > 0:
                fit_score += 0.1
        
        return min(1.0, fit_score)
    
    def _calculate_viral_potential(self, predictions: Dict[EngagementMetric, float],
                                 features: Dict[str, Any]) -> float:
        """
Calculate viral potential score"""
        viral_score = 0.0
        
        # High share prediction indicates viral potential
        shares = predictions.get(EngagementMetric.SHARES, 0)
        if shares > 100:
            viral_score += 0.3
        
        # Emotional content has higher viral potential
        polarity = abs(features.get('polarity', 0))
        if polarity > 0.5:
            viral_score += 0.2
        
        # Questions and exclamations increase engagement
        if features.get('has_questions', False):
            viral_score += 0.1
        if features.get('has_exclamations', False):
            viral_score += 0.1
        
        # Visual content has higher viral potential
        if features.get('has_media', False):
            viral_score += 0.2
        
        # Trending topics boost viral potential
        if features.get('hashtag_count', 0) > 5:
            viral_score += 0.1
        
        return min(1.0, viral_score)
    
    def _suggest_optimal_time(self, platform: str, features: Dict[str, Any]) -> datetime:
        """
Suggest optimal posting time"""
        now = datetime.utcnow()
        optimal_hours = self._get_optimal_hours(platform)
        
        # Find next optimal hour
        next_optimal = None
        for hour in optimal_hours:
            test_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if test_time > now:
                next_optimal = test_time
                break
        
        # If no optimal time today, use tomorrow's first optimal hour
        if not next_optimal:
            tomorrow = now + timedelta(days=1)
            next_optimal = tomorrow.replace(
                hour=optimal_hours[0], minute=0, second=0, microsecond=0
            )
        
        return next_optimal
    
    async def _suggest_content_improvements(self, text: str, features: Dict[str, Any],
                                          predictions: Dict[EngagementMetric, float]) -> List[str]:
        """
Suggest specific content improvements"""
        improvements = []
        
        # Text improvements
        if features.get('word_count', 0) < 10:
            improvements.append("Add more descriptive content to provide context")
        
        if features.get('hashtag_count', 0) == 0:
            improvements.append("Add relevant hashtags to increase discoverability")
        
        if not features.get('has_emojis', False):
            improvements.append("Consider adding emojis to make content more engaging")
        
        if features.get('polarity', 0) < 0:
            improvements.append("Consider using more positive language")
        
        if not features.get('has_questions', False) and not features.get('has_exclamations', False):
            improvements.append("Add a question or call-to-action to encourage interaction")
        
        if features.get('readability_score', 50) < 30:
            improvements.append("Simplify language for better readability")
        
        # Media improvements
        if not features.get('has_media', False):
            improvements.append("Add images or videos to increase visual appeal")
        
        return improvements[:5]  # Limit to top 5 improvements
    
    def add_engagement_data(self, data: EngagementData):
        """Add new engagement data for continuous learning"""
        self.historical_data.append(data)
        
        # Limit data size to prevent memory issues
        if len(self.historical_data) > 10000:
            self.historical_data = self.historical_data[-8000:]
        
        # Retrain models periodically
        if len(self.historical_data) % 100 == 0:
            asyncio.create_task(self._train_models())
    
    def get_optimization_insights(self, platform: str = None) -> Dict[str, Any]:
        """
Get insights about optimization performance"""
        insights = {
            'total_analyses': len(self.optimization_cache),
            'model_performance': self.engagement_predictor.training_history,
            'platform_benchmarks': self.platform_benchmarks
        }
        
        if platform and platform in self.platform_benchmarks:
            insights['platform_specific'] = self.platform_benchmarks[platform]
        
        # Analyze recent recommendations
        recent_analyses = [a for a in self.optimization_cache.values() 
                          if a.analyzed_at > datetime.utcnow() - timedelta(days=7)]
        
        if recent_analyses:
            avg_score = np.mean([a.optimization_score for a in recent_analyses])
            avg_viral_potential = np.mean([a.viral_potential for a in recent_analyses])
            
            insights['recent_performance'] = {
                'avg_optimization_score': avg_score,
                'avg_viral_potential': avg_viral_potential,
                'total_recent_analyses': len(recent_analyses)
            }
        
        return insights
