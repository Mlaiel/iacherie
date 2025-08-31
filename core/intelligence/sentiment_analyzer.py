"""
 Sentiment Analyzer - IA Influencer Agent
=========================================

Advanced sentiment analysis system for understanding audience emotions,
brand perception, and content reception across multiple platforms.

  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
====================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright © 2025 Fahed Mlaiel - All rights reserved
WARNING: Any unauthorized copying, modification, distribution or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
import re

# ML/AI Libraries
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from textblob import TextBlob
import emoji

# NLP Libraries
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Core Dependencies
from ..analytics.audience_analytics import AudienceAnalytics
from ..processors.text_processor import TextProcessor
from ..storage.sentiment_storage import SentimentStorage
from ..cache.redis_cache import RedisCache


class SentimentPolarity(Enum):
    """Sentiment polarity types"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class EmotionType(Enum):
    """Emotion classification types"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"


class ContentSentimentCategory(Enum):
    """Content-specific sentiment categories"""
    ENGAGEMENT_POSITIVE = "engagement_positive"
    ENGAGEMENT_NEGATIVE = "engagement_negative"
    BRAND_POSITIVE = "brand_positive"
    BRAND_NEGATIVE = "brand_negative"
    PRODUCT_POSITIVE = "product_positive"
    PRODUCT_NEGATIVE = "product_negative"
    CREATOR_POSITIVE = "creator_positive"
    CREATOR_NEGATIVE = "creator_negative"


@dataclass
class SentimentScore:
    """Sentiment score data structure"""
    polarity: SentimentPolarity
    confidence: float
    raw_score: float
    emotion_scores: Dict[EmotionType, float]
    subjectivity: float
    intensity: float


@dataclass
class SentimentAnalysis:
    """Comprehensive sentiment analysis result"""
    analysis_id: str
    content_id: str
    platform: str
    overall_sentiment: SentimentScore
    comment_sentiment: SentimentScore
    audience_sentiment: SentimentScore
    brand_sentiment: Optional[SentimentScore]
    trending_emotions: List[EmotionType]
    sentiment_distribution: Dict[SentimentPolarity, float]
    emotion_distribution: Dict[EmotionType, float]
    sentiment_trends: Dict[str, List[float]]  # Time-based sentiment trends
    key_phrases: List[str]
    sentiment_drivers: List[str]
    improvement_suggestions: List[str]
    risk_indicators: List[str]
    opportunity_indicators: List[str]
    demographic_sentiment: Dict[str, SentimentScore]
    platform_comparison: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AudienceInsight:
    """Audience insight from sentiment analysis"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    sentiment_impact: float
    confidence_level: float
    affected_demographics: List[str]
    platforms: List[str]
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


class SentimentAnalyzer:
    """
    Advanced sentiment analysis engine for creators
    
    Provides comprehensive sentiment analysis including:
    - Multi-modal sentiment detection (text, emoji, context)
    - Emotion classification and intensity analysis
    - Brand sentiment monitoring and tracking
    - Audience demographic sentiment analysis
    - Cross-platform sentiment comparison
    - Sentiment trend prediction and alerts
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize sentiment analyzer"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.audience_analytics = AudienceAnalytics(config.get('audience_analytics', {}))
        self.text_processor = TextProcessor(config.get('text_processing', {}))
        self.sentiment_storage = SentimentStorage(config.get('storage', {}))
        self.cache = RedisCache(config.get('redis', {}))
        
        # ML Models
        self.sentiment_model = None
        self.emotion_model = None
        self.brand_sentiment_model = None
        self.nltk_analyzer = None
        
        # Processing parameters
        self.min_text_length = config.get('min_text_length', 10)
        self.sentiment_threshold = config.get('sentiment_threshold', 0.6)
        self.batch_size = config.get('batch_size', 32)
        self.supported_languages = config.get('supported_languages', ['en', 'es', 'fr', 'de'])
        
        # Sentiment weights by source
        self.source_weights = config.get('source_weights', {
            'comments': 0.4,
            'captions': 0.3,
            'reviews': 0.2,
            'mentions': 0.1
        })
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models"""



        try:
            # Ensure NLTK data is available
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon')
                nltk.download('punkt')
                nltk.download('stopwords')
            
            # NLTK VADER sentiment analyzer
            self.nltk_analyzer = SentimentIntensityAnalyzer()
            
            # Transformer-based sentiment model
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Emotion classification model
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Brand sentiment model (specialized for brand mentions)
            self.brand_sentiment_model = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Custom neural network for multi-modal sentiment
            class MultiModalSentimentNet(nn.Module):
                def __init__(self, text_dim: int = 768, emoji_dim: int = 50, context_dim: int = 20):
                    super().__init__()
                    self.text_encoder = nn.Linear(text_dim, 256)
                    self.emoji_encoder = nn.Linear(emoji_dim, 64)
                    self.context_encoder = nn.Linear(context_dim, 32)
                    
                    self.fusion = nn.Sequential(
                        nn.Linear(256 + 64 + 32, 128),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(128, 64),
                        nn.ReLU(),
                        nn.Linear(64, 5)  # 5 sentiment classes
                    )
                    
                    self.softmax = nn.Softmax(dim=1)
                
                def forward(self, text_features, emoji_features, context_features):
                    text_out = torch.relu(self.text_encoder(text_features))
                    emoji_out = torch.relu(self.emoji_encoder(emoji_features))
                    context_out = torch.relu(self.context_encoder(context_features))
                    
                    combined = torch.cat([text_out, emoji_out, context_out], dim=1)
                    sentiment_logits = self.fusion(combined)
                    
                    return self.softmax(sentiment_logits)
            
            self.multimodal_sentiment_net = MultiModalSentimentNet()
            
            # TF-IDF vectorizer for key phrase extraction
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            self.logger.info("Sentiment analysis models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing sentiment models: {e}")
            raise
    
    async def analyze_content_sentiment(
        self,
        content_data: Dict[str, Any],
        include_comments: bool = True,
        include_audience_analysis: bool = True,
        platforms: List[str] = None
    ) -> SentimentAnalysis:
        """
        Perform comprehensive sentiment analysis on content
        
        Args:
            content_data: Content data including text, comments, engagement
            include_comments: Whether to analyze comment sentiment
            include_audience_analysis: Whether to perform audience sentiment analysis
            platforms: Specific platforms to analyze
            
        Returns:
            Comprehensive sentiment analysis result
        """



        try:
            content_id = content_data.get('content_id', 'unknown')
            platform = content_data.get('platform', 'unknown')
            
            self.logger.info(f"Analyzing sentiment for content {content_id} on {platform}")
            
            # Extract text content
            text_content = self._extract_text_content(content_data)
            
            # Analyze overall content sentiment
            overall_sentiment = await self._analyze_text_sentiment(text_content)
            
            # Analyze comment sentiment if requested
            comment_sentiment = None
            if include_comments and content_data.get('comments'):
                comment_sentiment = await self._analyze_comments_sentiment(
                    content_data['comments']
                )
            
            # Analyze audience sentiment if requested
            audience_sentiment = None
            if include_audience_analysis:
                audience_sentiment = await self._analyze_audience_sentiment(
                    content_id, platform
                )
            
            # Analyze brand sentiment if brand mentions detected
            brand_sentiment = None
            if self._has_brand_mentions(text_content):
                brand_sentiment = await self._analyze_brand_sentiment(text_content)
            
            # Extract trending emotions
            trending_emotions = await self._extract_trending_emotions(
                text_content, content_data.get('comments', [])
            )
            
            # Calculate sentiment distribution
            sentiment_distribution = await self._calculate_sentiment_distribution(
                overall_sentiment, comment_sentiment, audience_sentiment
            )
            
            # Calculate emotion distribution
            emotion_distribution = await self._calculate_emotion_distribution(
                text_content, content_data.get('comments', [])
            )
            
            # Analyze sentiment trends over time
            sentiment_trends = await self._analyze_sentiment_trends(content_id, platform)
            
            # Extract key phrases and sentiment drivers
            key_phrases = await self._extract_key_phrases(text_content)
            sentiment_drivers = await self._identify_sentiment_drivers(
                text_content, overall_sentiment
            )
            
            # Generate insights and recommendations
            improvement_suggestions = await self._generate_improvement_suggestions(
                overall_sentiment, comment_sentiment, sentiment_drivers
            )
            
            risk_indicators = await self._identify_risk_indicators(
                overall_sentiment, comment_sentiment, sentiment_trends
            )
            
            opportunity_indicators = await self._identify_opportunity_indicators(
                overall_sentiment, trending_emotions, sentiment_trends
            )
            
            # Demographic sentiment analysis
            demographic_sentiment = {}
            if include_audience_analysis and content_data.get('audience_demographics'):
                demographic_sentiment = await self._analyze_demographic_sentiment(
                    content_data['audience_demographics'], content_data.get('comments', [])
                )
            
            # Cross-platform sentiment comparison
            platform_comparison = {}
            if platforms:
                platform_comparison = await self._compare_platform_sentiment(
                    content_id, platforms
                )
            
            analysis = SentimentAnalysis(
                analysis_id=self._generate_id(),
                content_id=content_id,
                platform=platform,
                overall_sentiment=overall_sentiment,
                comment_sentiment=comment_sentiment or self._create_neutral_sentiment(),
                audience_sentiment=audience_sentiment or self._create_neutral_sentiment(),
                brand_sentiment=brand_sentiment,
                trending_emotions=trending_emotions,
                sentiment_distribution=sentiment_distribution,
                emotion_distribution=emotion_distribution,
                sentiment_trends=sentiment_trends,
                key_phrases=key_phrases,
                sentiment_drivers=sentiment_drivers,
                improvement_suggestions=improvement_suggestions,
                risk_indicators=risk_indicators,
                opportunity_indicators=opportunity_indicators,
                demographic_sentiment=demographic_sentiment,
                platform_comparison=platform_comparison
            )
            
            # Cache analysis result
            cache_key = f"sentiment_analysis:{content_id}:{platform}"
            await self.cache.set(cache_key, analysis.__dict__, ttl=3600)
            
            # Store in permanent storage
            await self.sentiment_storage.store_analysis(analysis)
            
            self.logger.info(f"Sentiment analysis completed for {content_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content sentiment: {e}")
            return self._create_fallback_analysis(content_data)
    
    async def _analyze_text_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment of text content"""



        try:
            if not text or len(text.strip()) < self.min_text_length:
                return self._create_neutral_sentiment()
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Multiple sentiment analysis approaches
            sentiment_scores = []
            
            # 1. VADER sentiment analysis
            vader_scores = self.nltk_analyzer.polarity_scores(cleaned_text)
            sentiment_scores.append({
                'positive': vader_scores['pos'],
                'neutral': vader_scores['neu'],
                'negative': vader_scores['neg'],
                'compound': vader_scores['compound']
            })
            
            # 2. Transformer-based sentiment analysis
            if len(cleaned_text) <= 512:  # Model token limit
                transformer_result = self.sentiment_model(cleaned_text)
                transformer_score = self._process_transformer_sentiment(transformer_result[0])
                sentiment_scores.append(transformer_score)
            
            # 3. TextBlob sentiment analysis
            blob = TextBlob(cleaned_text)
            textblob_score = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
            sentiment_scores.append(self._convert_textblob_sentiment(textblob_score))
            
            # 4. Emoji sentiment analysis
            emoji_sentiment = self._analyze_emoji_sentiment(text)
            if emoji_sentiment:
                sentiment_scores.append(emoji_sentiment)
            
            # Ensemble sentiment calculation
            final_sentiment = self._ensemble_sentiment_scores(sentiment_scores)
            
            # Emotion analysis
            emotion_scores = await self._analyze_text_emotions(cleaned_text)
            
            # Create sentiment score object
            sentiment_score = SentimentScore(
                polarity=self._determine_polarity(final_sentiment['compound']),
                confidence=final_sentiment.get('confidence', 0.7),
                raw_score=final_sentiment['compound'],
                emotion_scores=emotion_scores,
                subjectivity=textblob_score['subjectivity'],
                intensity=abs(final_sentiment['compound'])
            )
            
            return sentiment_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing text sentiment: {e}")
            return self._create_neutral_sentiment()
    
    async def _analyze_comments_sentiment(self, comments: List[Dict[str, Any]]) -> SentimentScore:
        """Analyze sentiment of comments"""



        try:
            if not comments:
                return self._create_neutral_sentiment()
            
            comment_sentiments = []
            total_weight = 0
            
            for comment in comments:
                comment_text = comment.get('text', '')
                comment_likes = comment.get('likes', 1)
                comment_weight = min(comment_likes, 100)  # Cap weight to prevent outliers
                
                if len(comment_text.strip()) >= self.min_text_length:
                    comment_sentiment = await self._analyze_text_sentiment(comment_text)
                    comment_sentiments.append({
                        'sentiment': comment_sentiment,
                        'weight': comment_weight
                    })
                    total_weight += comment_weight
            
            if not comment_sentiments:
                return self._create_neutral_sentiment()
            
            # Calculate weighted average sentiment
            weighted_compound = sum(
                cs['sentiment'].raw_score * cs['weight'] for cs in comment_sentiments
            ) / total_weight
            
            weighted_subjectivity = sum(
                cs['sentiment'].subjectivity * cs['weight'] for cs in comment_sentiments
            ) / total_weight
            
            # Aggregate emotion scores
            aggregated_emotions = {}
            for emotion_type in EmotionType:
                emotion_sum = sum(
                    cs['sentiment'].emotion_scores.get(emotion_type, 0.0) * cs['weight']
                    for cs in comment_sentiments
                )
                aggregated_emotions[emotion_type] = emotion_sum / total_weight
            
            # Calculate confidence based on consistency
            sentiment_variance = np.var([cs['sentiment'].raw_score for cs in comment_sentiments])
            confidence = max(0.3, 1.0 - sentiment_variance)
            
            return SentimentScore(
                polarity=self._determine_polarity(weighted_compound),
                confidence=confidence,
                raw_score=weighted_compound,
                emotion_scores=aggregated_emotions,
                subjectivity=weighted_subjectivity,
                intensity=abs(weighted_compound)
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing comments sentiment: {e}")
            return self._create_neutral_sentiment()
    
    async def _analyze_audience_sentiment(self, content_id: str, platform: str) -> SentimentScore:
        """Analyze general audience sentiment towards creator"""



        try:
            # Get audience engagement data
            audience_data = await self.audience_analytics.get_audience_sentiment_data(
                content_id, platform, timeframe='7d'
            )
            
            if not audience_data:
                return self._create_neutral_sentiment()
            
            # Analyze engagement patterns for sentiment indicators
            positive_indicators = audience_data.get('positive_engagement', 0)
            negative_indicators = audience_data.get('negative_engagement', 0)
            neutral_indicators = audience_data.get('neutral_engagement', 0)
            
            total_engagement = positive_indicators + negative_indicators + neutral_indicators
            
            if total_engagement == 0:
                return self._create_neutral_sentiment()
            
            # Calculate sentiment score based on engagement patterns
            positive_ratio = positive_indicators / total_engagement
            negative_ratio = negative_indicators / total_engagement
            
            # Compound score calculation
            compound_score = (positive_ratio - negative_ratio)
            
            # Determine emotion distribution from engagement types
            emotion_scores = {
                EmotionType.JOY: positive_ratio * 0.6,
                EmotionType.TRUST: positive_ratio * 0.4,
                EmotionType.ANGER: negative_ratio * 0.5,
                EmotionType.SADNESS: negative_ratio * 0.3,
                EmotionType.SURPRISE: audience_data.get('surprise_engagement', 0) / max(total_engagement, 1),
                EmotionType.ANTICIPATION: audience_data.get('anticipation_engagement', 0) / max(total_engagement, 1),
                EmotionType.FEAR: negative_ratio * 0.2,
                EmotionType.DISGUST: negative_ratio * 0.0
            }
            
            return SentimentScore(
                polarity=self._determine_polarity(compound_score),
                confidence=min(total_engagement / 1000, 0.9),  # Higher engagement = higher confidence
                raw_score=compound_score,
                emotion_scores=emotion_scores,
                subjectivity=0.5,  # Audience sentiment is moderately subjective
                intensity=abs(compound_score)
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience sentiment: {e}")
            return self._create_neutral_sentiment()
    
    async def _analyze_brand_sentiment(self, text: str) -> SentimentScore:
        """Analyze brand-specific sentiment"""



        try:
            # Extract brand mentions
            brand_mentions = self._extract_brand_mentions(text)
            
            if not brand_mentions:
                return None
            
            brand_sentiment_scores = []
            
            for brand_mention in brand_mentions:
                # Extract context around brand mention
                brand_context = self._extract_brand_context(text, brand_mention)
                
                # Analyze sentiment of brand context
                if len(brand_context) >= self.min_text_length:
                    brand_result = self.brand_sentiment_model(brand_context[:512])
                    brand_score = self._process_brand_sentiment_result(brand_result[0])
                    brand_sentiment_scores.append(brand_score)
            
            if not brand_sentiment_scores:
                return None
            
            # Average brand sentiment scores
            avg_compound = np.mean([score['compound'] for score in brand_sentiment_scores])
            avg_confidence = np.mean([score['confidence'] for score in brand_sentiment_scores])
            avg_subjectivity = np.mean([score.get('subjectivity', 0.5) for score in brand_sentiment_scores])
            
            return SentimentScore(
                polarity=self._determine_polarity(avg_compound),
                confidence=avg_confidence,
                raw_score=avg_compound,
                emotion_scores={emotion: 0.0 for emotion in EmotionType},  # Brand sentiment focuses on polarity
                subjectivity=avg_subjectivity,
                intensity=abs(avg_compound)
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing brand sentiment: {e}")
            return None
    
    async def _analyze_text_emotions(self, text: str) -> Dict[EmotionType, float]:
        """Analyze emotions in text"""



        try:
            if len(text.strip()) < self.min_text_length:
                return {emotion: 0.0 for emotion in EmotionType}
            
            # Use emotion classification model
            emotion_results = self.emotion_model(text[:512])  # Truncate for model
            
            # Map model outputs to our emotion types
            emotion_mapping = {
                'joy': EmotionType.JOY,
                'sadness': EmotionType.SADNESS,
                'anger': EmotionType.ANGER,
                'fear': EmotionType.FEAR,
                'surprise': EmotionType.SURPRISE,
                'disgust': EmotionType.DISGUST,
                'love': EmotionType.JOY,  # Map love to joy
                'optimism': EmotionType.ANTICIPATION,
                'pessimism': EmotionType.SADNESS,
                'trust': EmotionType.TRUST
            }
            
            emotion_scores = {emotion: 0.0 for emotion in EmotionType}
            
            for result in emotion_results:
                emotion_label = result['label'].lower()
                if emotion_label in emotion_mapping:
                    emotion_type = emotion_mapping[emotion_label]
                    emotion_scores[emotion_type] = result['score']
            
            return emotion_scores
            
        except Exception as e:
            self.logger.error(f"Error analyzing text emotions: {e}")
            return {emotion: 0.0 for emotion in EmotionType}
    
    def _extract_text_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content from content data"""
        text_parts = []
        
        # Caption/description
        if content_data.get('caption'):
            text_parts.append(content_data['caption'])
        
        if content_data.get('description'):
            text_parts.append(content_data['description'])
        
        # Hashtags as text
        if content_data.get('hashtags'):
            hashtag_text = ' '.join(f"#{tag}" for tag in content_data['hashtags'])
            text_parts.append(hashtag_text)
        
        # Any other text fields
        if content_data.get('title'):
            text_parts.append(content_data['title'])
        
        return ' '.join(text_parts)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize mentions and hashtags for better processing
        text = re.sub(r'@\w+', ' @USER ', text)
        text = re.sub(r'#(\w+)', r' #\1 ', text)
        
        # Preserve emojis but add spaces around them
        text = re.sub(r'([^\w\s])', r' \1 ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        return text.strip()
    
    def _process_transformer_sentiment(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Process transformer model sentiment result"""
        label = result['label'].upper()
        score = result['score']
        
        if 'POSITIVE' in label:
            return {
                'positive': score,
                'negative': 1 - score,
                'neutral': 0.0,
                'compound': score,
                'confidence': score
            }
        elif 'NEGATIVE' in label:
            return {
                'positive': 1 - score,
                'negative': score,
                'neutral': 0.0,
                'compound': -score,
                'confidence': score
            }
        else:  # NEUTRAL
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': score,
                'compound': 0.0,
                'confidence': score
            }
    
    def _convert_textblob_sentiment(self, textblob_result: Dict[str, float]) -> Dict[str, float]:
        """Convert TextBlob sentiment to standard format"""
        polarity = textblob_result['polarity']
        
        if polarity > 0:
            positive = polarity
            negative = 0
        elif polarity < 0:
            positive = 0
            negative = abs(polarity)
        else:
            positive = 0
            negative = 0
        
        return {
            'positive': positive,
            'negative': negative,
            'neutral': 1 - positive - negative,
            'compound': polarity,
            'confidence': 0.7  # TextBlob has moderate confidence
        }
    
    def _analyze_emoji_sentiment(self, text: str) -> Optional[Dict[str, float]]:
        """Analyze sentiment based on emojis"""



        try:
            # Extract emojis from text
            emojis = [char for char in text if char in emoji.EMOJI_DATA]
            
            if not emojis:
                return None
            
            # Simple emoji sentiment mapping
            positive_emojis = ['', '', '', '', '', '', '🥰', '', '🤗', '', '', '', '', '', '', '', '']
            negative_emojis = ['', '', '', '', '', '', '', '', '', '🤬', '', '', '', '']
            
            positive_count = sum(1 for e in emojis if e in positive_emojis)
            negative_count = sum(1 for e in emojis if e in negative_emojis)
            total_emojis = len(emojis)
            
            if total_emojis == 0:
                return None
            
            positive_ratio = positive_count / total_emojis
            negative_ratio = negative_count / total_emojis
            neutral_ratio = 1 - positive_ratio - negative_ratio
            
            compound = positive_ratio - negative_ratio
            
            return {
                'positive': positive_ratio,
                'negative': negative_ratio,
                'neutral': neutral_ratio,
                'compound': compound,
                'confidence': min(total_emojis / 5, 0.8)  # More emojis = higher confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing emoji sentiment: {e}")
            return None
    
    def _ensemble_sentiment_scores(self, sentiment_scores: List[Dict[str, float]]) -> Dict[str, float]:
        """Combine multiple sentiment scores using ensemble method"""
        if not sentiment_scores:
            return {'compound': 0.0, 'confidence': 0.0}
        
        # Weight different methods
        method_weights = [0.3, 0.4, 0.2, 0.1]  # VADER, Transformer, TextBlob, Emoji
        
        weighted_compound = 0.0
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for i, scores in enumerate(sentiment_scores):
            weight = method_weights[i] if i < len(method_weights) else 0.1
            confidence = scores.get('confidence', 0.5)
            
            weighted_compound += scores['compound'] * weight * confidence
            weighted_confidence += confidence * weight
            total_weight += weight * confidence
        
        if total_weight == 0:
            return {'compound': 0.0, 'confidence': 0.0}
        
        final_compound = weighted_compound / total_weight
        final_confidence = weighted_confidence / sum(method_weights[:len(sentiment_scores)])
        
        return {
            'compound': final_compound,
            'confidence': final_confidence
        }
    
    def _determine_polarity(self, compound_score: float) -> SentimentPolarity:
        """Determine sentiment polarity from compound score"""
        if compound_score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif compound_score >= 0.2:
            return SentimentPolarity.POSITIVE
        elif compound_score <= -0.6:
            return SentimentPolarity.VERY_NEGATIVE
        elif compound_score <= -0.2:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.NEUTRAL
    
    def _create_neutral_sentiment(self) -> SentimentScore:
        """Create neutral sentiment score"""



        return SentimentScore(
            polarity=SentimentPolarity.NEUTRAL,
            confidence=0.5,
            raw_score=0.0,
            emotion_scores={emotion: 0.0 for emotion in EmotionType},
            subjectivity=0.5,
            intensity=0.0
        )
    
    def _has_brand_mentions(self, text: str) -> bool:
        """Check if text contains brand mentions"""
        # Simple brand mention detection
        brand_patterns = [
            r'@\w+',  # Mentions
            r'#\w*brand\w*',  # Brand hashtags
            r'\b(brand|company|product|service)\b'  # Brand-related words
        ]
        
        for pattern in brand_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_brand_mentions(self, text: str) -> List[str]:
        """Extract brand mentions from text"""
        mentions = []
        
        # Extract @ mentions
        at_mentions = re.findall(r'@(\w+)', text)
        mentions.extend(at_mentions)
        
        # Extract brand-related hashtags
        brand_hashtags = re.findall(r'#(\w*brand\w*)', text, re.IGNORECASE)
        mentions.extend(brand_hashtags)
        
        return list(set(mentions))  # Remove duplicates
    
    def _extract_brand_context(self, text: str, brand_mention: str) -> str:
        """Extract context around brand mention"""
        # Find the brand mention in text
        pattern = re.compile(re.escape(brand_mention), re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return ""
        
        # Extract context (50 characters before and after)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        
        return text[start:end]
    
    def _process_brand_sentiment_result(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Process brand sentiment model result"""
        # This would depend on the specific model used
        # For now, use a simplified approach
        label = result.get('label', 'NEUTRAL')
        score = result.get('score', 0.5)
        
        if 'POSITIVE' in label.upper() or '4' in label or '5' in label:
            compound = score
        elif 'NEGATIVE' in label.upper() or '1' in label or '2' in label:
            compound = -score
        else:
            compound = 0.0
        
        return {
            'compound': compound,
            'confidence': score,
            'subjectivity': 0.7  # Brand sentiment is usually more subjective
        }
    
    def _create_fallback_analysis(self, content_data: Dict[str, Any]) -> SentimentAnalysis:
        """Create fallback analysis when main analysis fails"""



        return SentimentAnalysis(
            analysis_id=self._generate_id(),
            content_id=content_data.get('content_id', 'unknown'),
            platform=content_data.get('platform', 'unknown'),
            overall_sentiment=self._create_neutral_sentiment(),
            comment_sentiment=self._create_neutral_sentiment(),
            audience_sentiment=self._create_neutral_sentiment(),
            brand_sentiment=None,
            trending_emotions=[],
            sentiment_distribution={polarity: 0.2 for polarity in SentimentPolarity},
            emotion_distribution={emotion: 0.125 for emotion in EmotionType},
            sentiment_trends={},
            key_phrases=[],
            sentiment_drivers=[],
            improvement_suggestions=["Unable to analyze sentiment due to technical error"],
            risk_indicators=["Sentiment analysis failed"],
            opportunity_indicators=[],
            demographic_sentiment={},
            platform_comparison={}
        )
    
    def _generate_id(self) -> str:
        """Generate unique ID"""



        return hashlib.md5(f"{datetime.now().isoformat()}{hash(self)}".encode()).hexdigest()[:12]


class AudienceInsightEngine:
    """
    Advanced audience insight engine using sentiment analysis
    
    Generates actionable insights about audience behavior,
    preferences, and engagement patterns based on sentiment data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize audience insight engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.sentiment_analyzer = SentimentAnalyzer(config)
    
    async def generate_audience_insights(
        self,
        creator_id: str,
        timeframe: str = "30d",
        platforms: List[str] = None
    ) -> List[AudienceInsight]:
        """
        Generate audience insights based on sentiment analysis
        
        Args:
            creator_id: Creator ID for analysis
            timeframe: Analysis timeframe
            platforms: Platforms to analyze
            
        Returns:
            List of audience insights
        """



        try:
            self.logger.info(f"Generating audience insights for creator {creator_id}")
            
            # This would implement comprehensive audience insight generation
            # For now, return mock insights
            
            insights = [
                AudienceInsight(
                    insight_id=self._generate_id(),
                    insight_type="sentiment_trend",
                    title="Positive Sentiment Trend",
                    description="Audience sentiment has improved by 15% over the last month",
                    sentiment_impact=0.15,
                    confidence_level=0.8,
                    affected_demographics=["18-25", "female"],
                    platforms=platforms or ["instagram"],
                    recommendations=["Continue current content strategy", "Increase posting frequency"],
                    supporting_data={"sentiment_change": 0.15, "sample_size": 1000}
                )
            ]
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating audience insights: {e}")
            return []
    
    def _generate_id(self) -> str:
        """Generate unique ID"""



        return hashlib.md5(f"{datetime.now().isoformat()}{hash(self)}".encode()).hexdigest()[:12]
