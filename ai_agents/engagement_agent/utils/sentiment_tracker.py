"""
Sentiment Tracker - Advanced Sentiment Analysis & Emotional Intelligence System

Industrial-grade sentiment monitoring with real-time emotion tracking,
mood analysis, and psychological insights for audience engagement optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

import numpy as np
import pandas as pd
from textblob import TextBlob
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

from ...ai.core.config import settings
from ...core.managers.database_manager import DatabaseManager
from ...ml.models.emotion_detection import EmotionDetectionModel
from ...ml.models.sentiment_models import AdvancedSentimentAnalyzer
from ...utils.performance_monitor import performance_monitor
from ...utils.cache_manager import CacheManager
from ...utils.statistical_analyzer import StatisticalAnalyzer

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Primary emotion classifications"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    LOVE = "love"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    CONTENTMENT = "contentment"

class SentimentPolarity(Enum):
    """Sentiment polarity levels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    SLIGHTLY_POSITIVE = "slightly_positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class MoodTrend(Enum):
    """Mood trend directions"""
    STRONGLY_IMPROVING = "strongly_improving"
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    STRONGLY_DECLINING = "strongly_declining"
    VOLATILE = "volatile"

@dataclass
class SentimentMetrics:
    """Comprehensive sentiment analysis metrics"""
    text_id: str
    platform: str
    timestamp: datetime
    
    # Core sentiment scores
    polarity: float  # -1.0 to 1.0
    subjectivity: float  # 0.0 to 1.0
    compound_score: float  # -1.0 to 1.0
    
    # Emotion scores
    primary_emotion: EmotionType
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    emotion_confidence: float = 0.0
    
    # Advanced metrics
    sentiment_polarity: SentimentPolarity = SentimentPolarity.NEUTRAL
    emotional_intensity: float = 0.0
    emotional_stability: float = 0.0
    authenticity_score: float = 0.0
    
    # Context information
    context_category: str = "general"
    language: str = "en"
    word_count: int = 0
    
    # Comparative metrics
    audience_sentiment_deviation: float = 0.0
    historical_comparison: float = 0.0

@dataclass
class MoodAnalysis:
    """Mood analysis and trends"""
    subject_id: str  # user_id or content_id
    analysis_period: str
    start_date: datetime
    end_date: datetime
    
    # Mood metrics
    average_sentiment: float
    mood_volatility: float
    dominant_emotion: EmotionType
    mood_trend: MoodTrend
    
    # Trend analysis
    sentiment_trajectory: List[float]
    emotion_evolution: Dict[str, List[float]]
    significant_events: List[Dict[str, Any]]
    
    # Insights
    mood_patterns: Dict[str, Any]
    trigger_analysis: Dict[str, Any]
    recommendations: List[str]

class SentimentTracker:
    """
    Advanced Sentiment Analysis & Tracking System
    
    Industrial-grade sentiment monitoring with multi-model analysis,
    real-time tracking, and predictive mood analytics.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager(namespace="sentiment_tracker")
        self.emotion_detector = EmotionDetectionModel()
        self.advanced_sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # AI Models
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.bert_sentiment_model = None
        
        # Tracking data
        self.sentiment_history: Dict[str, List[SentimentMetrics]] = {}
        self.mood_profiles: Dict[str, MoodAnalysis] = {}
        
        # Performance metrics
        self.model_performance: Dict[str, Any] = {}
        
        logger.info("Sentiment Tracker initialized")

    async def initialize(self) -> bool:
        """Initialize sentiment tracker with AI models"""
        try:
            # Load sentiment analysis models
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Load emotion detection model
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Load advanced models
            await self.emotion_detector.load_model()
            await self.advanced_sentiment_analyzer.load_model()
            
            # Initialize BERT model for advanced analysis
            model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.bert_sentiment_model = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                return_all_scores=True
            )
            
            # Load historical data
            await self._load_historical_sentiment_data()
            
            logger.info("Sentiment Tracker successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentiment Tracker: {str(e)}")
            return False

    @performance_monitor.track_execution_time
    async def analyze_sentiment(self,
                              text: str,
                              context: Optional[Dict[str, Any]] = None) -> SentimentMetrics:
        """
        Comprehensive sentiment analysis of text
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            SentimentMetrics: Comprehensive sentiment analysis
        """
        try:
            # Basic preprocessing
            clean_text = await self._preprocess_text(text)
            
            if not clean_text or len(clean_text.strip()) < 3:
                return self._create_neutral_sentiment_metrics(text, context)
            
            # Multi-model sentiment analysis
            textblob_analysis = await self._analyze_with_textblob(clean_text)
            roberta_analysis = await self._analyze_with_roberta(clean_text)
            bert_analysis = await self._analyze_with_bert(clean_text)
            advanced_analysis = await self.advanced_sentiment_analyzer.analyze(clean_text)
            
            # Emotion detection
            emotion_analysis = await self._detect_emotions(clean_text)
            
            # Calculate ensemble sentiment scores
            ensemble_scores = await self._calculate_ensemble_scores(
                textblob_analysis, roberta_analysis, bert_analysis, advanced_analysis
            )
            
            # Determine primary emotion and confidence
            primary_emotion, emotion_confidence = await self._determine_primary_emotion(
                emotion_analysis
            )
            
            # Calculate advanced metrics
            emotional_intensity = await self._calculate_emotional_intensity(emotion_analysis)
            authenticity_score = await self._calculate_authenticity_score(clean_text, ensemble_scores)
            
            # Create sentiment metrics
            sentiment_metrics = SentimentMetrics(
                text_id=context.get('text_id', f"text_{datetime.utcnow().timestamp()}") if context else f"text_{datetime.utcnow().timestamp()}",
                platform=context.get('platform', 'unknown') if context else 'unknown',
                timestamp=datetime.utcnow(),
                polarity=ensemble_scores['polarity'],
                subjectivity=textblob_analysis['subjectivity'],
                compound_score=ensemble_scores['compound'],
                primary_emotion=primary_emotion,
                emotion_scores=emotion_analysis,
                emotion_confidence=emotion_confidence,
                sentiment_polarity=self._classify_sentiment_polarity(ensemble_scores['polarity']),
                emotional_intensity=emotional_intensity,
                authenticity_score=authenticity_score,
                context_category=context.get('category', 'general') if context else 'general',
                language=await self._detect_language(text),
                word_count=len(clean_text.split())
            )
            
            # Calculate comparative metrics if historical data exists
            await self._calculate_comparative_metrics(sentiment_metrics, context)
            
            # Store in history
            subject_id = context.get('subject_id', 'unknown') if context else 'unknown'
            if subject_id not in self.sentiment_history:
                self.sentiment_history[subject_id] = []
            self.sentiment_history[subject_id].append(sentiment_metrics)
            
            # Cache results
            await self.cache_manager.set(
                f"sentiment_analysis_{sentiment_metrics.text_id}",
                sentiment_metrics,
                ttl=3600
            )
            
            logger.info(f"Sentiment analysis completed: {sentiment_metrics.sentiment_polarity.value}")
            return sentiment_metrics
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return self._create_neutral_sentiment_metrics(text, context)

    async def track_mood_over_time(self,
                                 subject_id: str,
                                 timeframe_days: int = 30) -> MoodAnalysis:
        """
        Track mood changes and trends over time
        
        Args:
            subject_id: Subject identifier (user, content, etc.)
            timeframe_days: Analysis timeframe in days
            
        Returns:
            MoodAnalysis: Comprehensive mood analysis
        """
        try:
            # Get sentiment history for subject
            sentiment_data = self.sentiment_history.get(subject_id, [])
            
            if not sentiment_data:
                raise ProcessingError(f"No sentiment data found for subject {subject_id}")
            
            # Filter by timeframe
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            filtered_data = [
                s for s in sentiment_data 
                if s.timestamp >= start_date
            ]
            
            if len(filtered_data) < 2:
                raise ProcessingError(f"Insufficient sentiment data for mood analysis")
            
            # Calculate mood metrics
            sentiment_scores = [s.compound_score for s in filtered_data]
            average_sentiment = statistics.mean(sentiment_scores)
            mood_volatility = statistics.stdev(sentiment_scores) if len(sentiment_scores) > 1 else 0
            
            # Determine dominant emotion
            emotion_counts = {}
            for sentiment in filtered_data:
                emotion = sentiment.primary_emotion.value
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            dominant_emotion = EmotionType(max(emotion_counts, key=emotion_counts.get))
            
            # Calculate mood trend
            mood_trend = await self._calculate_mood_trend(sentiment_scores)
            
            # Analyze emotion evolution
            emotion_evolution = await self._analyze_emotion_evolution(filtered_data)
            
            # Identify significant events
            significant_events = await self._identify_significant_mood_events(filtered_data)
            
            # Generate mood patterns
            mood_patterns = await self._analyze_mood_patterns(filtered_data)
            
            # Analyze triggers
            trigger_analysis = await self._analyze_mood_triggers(filtered_data)
            
            # Generate recommendations
            recommendations = await self._generate_mood_recommendations(
                average_sentiment, mood_volatility, mood_trend, significant_events
            )
            
            mood_analysis = MoodAnalysis(
                subject_id=subject_id,
                analysis_period=f"{timeframe_days} days",
                start_date=start_date,
                end_date=datetime.utcnow(),
                average_sentiment=average_sentiment,
                mood_volatility=mood_volatility,
                dominant_emotion=dominant_emotion,
                mood_trend=mood_trend,
                sentiment_trajectory=sentiment_scores,
                emotion_evolution=emotion_evolution,
                significant_events=significant_events,
                mood_patterns=mood_patterns,
                trigger_analysis=trigger_analysis,
                recommendations=recommendations
            )
            
            # Store mood analysis
            self.mood_profiles[subject_id] = mood_analysis
            
            # Cache results
            await self.cache_manager.set(
                f"mood_analysis_{subject_id}_{timeframe_days}d",
                mood_analysis,
                ttl=1800  # 30 minutes cache
            )
            
            logger.info(f"Mood analysis completed for {subject_id}: {mood_trend.value}")
            return mood_analysis
            
        except Exception as e:
            logger.error(f"Failed to track mood over time: {str(e)}")
            raise ProcessingError(f"Mood tracking failed: {str(e)}")

    async def analyze_audience_sentiment_trends(self,
                                              audience_data: List[Dict[str, Any]],
                                              grouping: str = "daily") -> Dict[str, Any]:
        """
        Analyze sentiment trends across audience interactions
        
        Args:
            audience_data: List of audience interactions with text content
            grouping: Time grouping ('hourly', 'daily', 'weekly')
            
        Returns:
            Dict: Comprehensive audience sentiment analysis
        """
        try:
            # Analyze sentiment for each interaction
            sentiment_analyses = []
            
            for interaction in audience_data:
                if 'text' in interaction and interaction['text']:
                    sentiment = await self.analyze_sentiment(
                        interaction['text'],
                        context={
                            'text_id': interaction.get('id', ''),
                            'platform': interaction.get('platform', ''),
                            'user_id': interaction.get('user_id', ''),
                            'timestamp': interaction.get('timestamp', datetime.utcnow())
                        }
                    )
                    sentiment_analyses.append(sentiment)
            
            if not sentiment_analyses:
                return {'error': 'No sentiment data to analyze'}
            
            # Group by time period
            grouped_data = await self._group_sentiment_by_time(sentiment_analyses, grouping)
            
            # Calculate trend metrics
            trend_analysis = await self._calculate_sentiment_trends(grouped_data)
            
            # Analyze emotion distribution
            emotion_distribution = await self._analyze_emotion_distribution(sentiment_analyses)
            
            # Identify sentiment peaks and valleys
            sentiment_extremes = await self._identify_sentiment_extremes(grouped_data)
            
            # Calculate audience engagement correlation
            engagement_correlation = await self._calculate_sentiment_engagement_correlation(
                audience_data, sentiment_analyses
            )
            
            # Generate insights and recommendations
            insights = await self._generate_audience_sentiment_insights(
                trend_analysis, emotion_distribution, sentiment_extremes, engagement_correlation
            )
            
            result = {
                'analysis_summary': {
                    'total_interactions': len(sentiment_analyses),
                    'average_sentiment': statistics.mean([s.compound_score for s in sentiment_analyses]),
                    'sentiment_volatility': statistics.stdev([s.compound_score for s in sentiment_analyses]) if len(sentiment_analyses) > 1 else 0,
                    'dominant_emotion': max(emotion_distribution, key=emotion_distribution.get),
                    'analysis_period': f"{len(grouped_data)} {grouping} periods"
                },
                'trend_analysis': trend_analysis,
                'grouped_data': grouped_data,
                'emotion_distribution': emotion_distribution,
                'sentiment_extremes': sentiment_extremes,
                'engagement_correlation': engagement_correlation,
                'insights': insights,
                'recommendations': await self._generate_audience_sentiment_recommendations(insights)
            }
            
            logger.info(f"Audience sentiment analysis completed: {len(sentiment_analyses)} interactions analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze audience sentiment trends: {str(e)}")
            raise ProcessingError(f"Audience sentiment analysis failed: {str(e)}")

    # Private helper methods
    
    async def _analyze_with_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis failed: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.0}

    async def _analyze_with_roberta(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using RoBERTa model"""
        try:
            results = self.sentiment_pipeline(text)
            
            # Convert to polarity score
            polarity = 0.0
            for result in results:
                if result['label'] == 'LABEL_2':  # Positive
                    polarity += result['score']
                elif result['label'] == 'LABEL_0':  # Negative
                    polarity -= result['score']
                # LABEL_1 is neutral, contributes 0
            
            return {
                'polarity': polarity,
                'confidence': max([r['score'] for r in results]),
                'detailed_scores': {r['label']: r['score'] for r in results}
            }
            
        except Exception as e:
            logger.error(f"RoBERTa analysis failed: {str(e)}")
            return {'polarity': 0.0, 'confidence': 0.0, 'detailed_scores': {}}

    async def _analyze_with_bert(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using BERT model"""
        try:
            results = self.bert_sentiment_model(text)
            
            # Extract polarity from BERT results
            polarity = 0.0
            confidence = 0.0
            
            for result in results:
                if result['label'] in ['POSITIVE', '5 stars', '4 stars']:
                    polarity += result['score']
                elif result['label'] in ['NEGATIVE', '1 star', '2 stars']:
                    polarity -= result['score']
                
                confidence = max(confidence, result['score'])
            
            return {
                'polarity': polarity,
                'confidence': confidence,
                'detailed_scores': {r['label']: r['score'] for r in results}
            }
            
        except Exception as e:
            logger.error(f"BERT analysis failed: {str(e)}")
            return {'polarity': 0.0, 'confidence': 0.0, 'detailed_scores': {}}

    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text using emotion classification model"""
        try:
            results = self.emotion_pipeline(text)
            
            emotion_scores = {}
            for result in results:
                emotion_scores[result['label']] = result['score']
            
            # Map to our emotion types
            mapped_emotions = {}
            emotion_mapping = {
                'joy': EmotionType.JOY.value,
                'sadness': EmotionType.SADNESS.value,
                'anger': EmotionType.ANGER.value,
                'fear': EmotionType.FEAR.value,
                'surprise': EmotionType.SURPRISE.value,
                'disgust': EmotionType.DISGUST.value,
                'love': EmotionType.LOVE.value,
            }
            
            for detected_emotion, score in emotion_scores.items():
                mapped_emotion = emotion_mapping.get(detected_emotion.lower(), detected_emotion)
                mapped_emotions[mapped_emotion] = score
            
            return mapped_emotions
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {str(e)}")
            return {}

    async def _calculate_ensemble_scores(self, *analyses) -> Dict[str, float]:
        """Calculate ensemble sentiment scores from multiple models"""
        try:
            polarities = []
            confidences = []
            
            for analysis in analyses:
                if analysis and 'polarity' in analysis:
                    polarities.append(analysis['polarity'])
                if analysis and 'confidence' in analysis:
                    confidences.append(analysis['confidence'])
            
            if not polarities:
                return {'polarity': 0.0, 'compound': 0.0, 'confidence': 0.0}
            
            # Weighted average based on confidence scores
            if confidences and len(confidences) == len(polarities):
                weighted_polarity = sum(p * c for p, c in zip(polarities, confidences)) / sum(confidences)
            else:
                weighted_polarity = statistics.mean(polarities)
            
            # Calculate compound score (normalized)
            compound_score = max(-1.0, min(1.0, weighted_polarity))
            
            return {
                'polarity': weighted_polarity,
                'compound': compound_score,
                'confidence': statistics.mean(confidences) if confidences else 0.5
            }
            
        except Exception as e:
            logger.error(f"Ensemble calculation failed: {str(e)}")
            return {'polarity': 0.0, 'compound': 0.0, 'confidence': 0.0}

    def _classify_sentiment_polarity(self, polarity_score: float) -> SentimentPolarity:
        """Classify sentiment polarity based on score"""
        if polarity_score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif polarity_score >= 0.3:
            return SentimentPolarity.POSITIVE
        elif polarity_score >= 0.1:
            return SentimentPolarity.SLIGHTLY_POSITIVE
        elif polarity_score >= -0.1:
            return SentimentPolarity.NEUTRAL
        elif polarity_score >= -0.3:
            return SentimentPolarity.SLIGHTLY_NEGATIVE
        elif polarity_score >= -0.6:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.VERY_NEGATIVE

    async def _determine_primary_emotion(self, 
                                       emotion_scores: Dict[str, float]) -> Tuple[EmotionType, float]:
        """Determine primary emotion and confidence"""
        try:
            if not emotion_scores:
                return EmotionType.TRUST, 0.0
            
            primary_emotion_name = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary_emotion_name]
            
            # Try to map to EmotionType
            try:
                primary_emotion = EmotionType(primary_emotion_name)
            except ValueError:
                # If not directly mappable, use a default
                primary_emotion = EmotionType.TRUST
            
            return primary_emotion, confidence
            
        except Exception as e:
            logger.error(f"Failed to determine primary emotion: {str(e)}")
            return EmotionType.TRUST, 0.0

    async def _calculate_mood_trend(self, sentiment_scores: List[float]) -> MoodTrend:
        """Calculate mood trend from sentiment score sequence"""
        try:
            if len(sentiment_scores) < 2:
                return MoodTrend.STABLE
            
            # Calculate trend using linear regression
            x = np.arange(len(sentiment_scores))
            y = np.array(sentiment_scores)
            
            # Calculate slope
            slope = np.polyfit(x, y, 1)[0]
            
            # Calculate volatility
            volatility = np.std(sentiment_scores)
            
            # Classify trend
            if volatility > 0.3:  # High volatility threshold
                return MoodTrend.VOLATILE
            elif slope > 0.1:
                return MoodTrend.STRONGLY_IMPROVING if slope > 0.2 else MoodTrend.IMPROVING
            elif slope < -0.1:
                return MoodTrend.STRONGLY_DECLINING if slope < -0.2 else MoodTrend.DECLINING
            else:
                return MoodTrend.STABLE
                
        except Exception as e:
            logger.error(f"Failed to calculate mood trend: {str(e)}")
            return MoodTrend.STABLE

    def _create_neutral_sentiment_metrics(self, 
                                        text: str, 
                                        context: Optional[Dict[str, Any]]) -> SentimentMetrics:
        """Create neutral sentiment metrics as fallback"""
        return SentimentMetrics(
            text_id=context.get('text_id', f"text_{datetime.utcnow().timestamp()}") if context else f"text_{datetime.utcnow().timestamp()}",
            platform=context.get('platform', 'unknown') if context else 'unknown',
            timestamp=datetime.utcnow(),
            polarity=0.0,
            subjectivity=0.0,
            compound_score=0.0,
            primary_emotion=EmotionType.TRUST,
            emotion_scores={},
            emotion_confidence=0.0,
            sentiment_polarity=SentimentPolarity.NEUTRAL,
            emotional_intensity=0.0,
            authenticity_score=0.5,
            context_category=context.get('category', 'general') if context else 'general',
            language='en',
            word_count=len(text.split()) if text else 0
        )


class MoodAnalyzer:
    """
    Advanced Mood Analysis & Psychological Insights System
    
    Specialized system for deep mood analysis, psychological pattern recognition,
    and emotional intelligence insights for content creators and their audiences.
    """
    
    def __init__(self):
        self.sentiment_tracker = SentimentTracker()
        self.cache_manager = CacheManager(namespace="mood_analyzer")
        
        # Psychological analysis models
        self.mood_predictor = None
        self.personality_analyzer = None
        
        # Analysis data
        self.psychological_profiles: Dict[str, Any] = {}
        self.mood_patterns: Dict[str, Any] = {}
        
        logger.info("Mood Analyzer initialized")

    async def analyze_psychological_profile(self,
                                          subject_id: str,
                                          interaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze psychological profile based on interaction patterns
        
        Args:
            subject_id: Subject identifier
            interaction_history: Historical interaction data with text content
            
        Returns:
            Dict: Comprehensive psychological profile analysis
        """
        try:
            # Analyze sentiment patterns
            sentiment_patterns = await self._analyze_sentiment_patterns(interaction_history)
            
            # Analyze communication style
            communication_style = await self._analyze_communication_style(interaction_history)
            
            # Analyze emotional stability
            emotional_stability = await self._analyze_emotional_stability(interaction_history)
            
            # Analyze social engagement patterns
            social_patterns = await self._analyze_social_engagement_patterns(interaction_history)
            
            # Generate personality insights
            personality_insights = await self._generate_personality_insights(
                sentiment_patterns, communication_style, emotional_stability, social_patterns
            )
            
            # Calculate psychological metrics
            psychological_metrics = await self._calculate_psychological_metrics(
                sentiment_patterns, emotional_stability, social_patterns
            )
            
            # Generate recommendations
            recommendations = await self._generate_psychological_recommendations(
                personality_insights, psychological_metrics
            )
            
            profile = {
                'subject_id': subject_id,
                'analysis_date': datetime.utcnow(),
                'data_points': len(interaction_history),
                'sentiment_patterns': sentiment_patterns,
                'communication_style': communication_style,
                'emotional_stability': emotional_stability,
                'social_patterns': social_patterns,
                'personality_insights': personality_insights,
                'psychological_metrics': psychological_metrics,
                'recommendations': recommendations,
                'confidence_score': await self._calculate_profile_confidence(
                    len(interaction_history), psychological_metrics
                )
            }
            
            # Store profile
            self.psychological_profiles[subject_id] = profile
            
            # Cache results
            await self.cache_manager.set(
                f"psychological_profile_{subject_id}",
                profile,
                ttl=7200  # 2 hours cache
            )
            
            logger.info(f"Psychological profile analysis completed for {subject_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to analyze psychological profile: {str(e)}")
            raise ProcessingError(f"Psychological profile analysis failed: {str(e)}")

    async def predict_mood_changes(self,
                                 subject_id: str,
                                 prediction_horizon_hours: int = 24) -> Dict[str, Any]:
        """
        Predict mood changes and emotional states
        
        Args:
            subject_id: Subject identifier
            prediction_horizon_hours: Hours to predict ahead
            
        Returns:
            Dict: Mood prediction analysis
        """
        try:
            # Get recent mood history
            recent_mood_data = await self._get_recent_mood_data(subject_id, hours=168)  # 1 week
            
            if len(recent_mood_data) < 10:
                raise ProcessingError(f"Insufficient mood data for prediction")
            
            # Extract features for prediction
            features = await self._extract_mood_prediction_features(recent_mood_data)
            
            # Generate mood predictions
            hourly_predictions = []
            
            for hour in range(1, prediction_horizon_hours + 1):
                prediction = await self._predict_mood_at_hour(features, hour)
                hourly_predictions.append({
                    'hour': hour,
                    'predicted_sentiment': prediction['sentiment'],
                    'predicted_emotion': prediction['emotion'],
                    'confidence': prediction['confidence'],
                    'risk_factors': prediction['risk_factors']
                })
            
            # Identify significant mood change periods
            mood_change_periods = await self._identify_mood_change_periods(hourly_predictions)
            
            # Generate intervention recommendations
            interventions = await self._generate_mood_interventions(
                hourly_predictions, mood_change_periods
            )
            
            # Calculate prediction reliability
            reliability_score = await self._calculate_prediction_reliability(
                recent_mood_data, features
            )
            
            result = {
                'subject_id': subject_id,
                'prediction_horizon': f"{prediction_horizon_hours} hours",
                'prediction_timestamp': datetime.utcnow(),
                'hourly_predictions': hourly_predictions,
                'mood_change_periods': mood_change_periods,
                'intervention_recommendations': interventions,
                'reliability_score': reliability_score,
                'confidence_intervals': await self._calculate_confidence_intervals(
                    hourly_predictions
                ),
                'risk_assessment': await self._assess_mood_risks(hourly_predictions)
            }
            
            # Cache predictions
            await self.cache_manager.set(
                f"mood_predictions_{subject_id}_{prediction_horizon_hours}h",
                result,
                ttl=3600  # 1 hour cache
            )
            
            logger.info(f"Mood prediction completed for {subject_id}: {prediction_horizon_hours}h horizon")
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict mood changes: {str(e)}")
            raise ProcessingError(f"Mood prediction failed: {str(e)}")

    # Private helper methods
    
    async def _analyze_sentiment_patterns(self, 
                                        interaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment patterns from interaction history"""
        try:
            sentiments = []
            
            for interaction in interaction_history:
                if 'text' in interaction and interaction['text']:
                    sentiment = await self.sentiment_tracker.analyze_sentiment(
                        interaction['text']
                    )
                    sentiments.append(sentiment)
            
            if not sentiments:
                return {}
            
            sentiment_scores = [s.compound_score for s in sentiments]
            
            patterns = {
                'average_sentiment': statistics.mean(sentiment_scores),
                'sentiment_volatility': statistics.stdev(sentiment_scores) if len(sentiment_scores) > 1 else 0,
                'positive_ratio': sum(1 for s in sentiment_scores if s > 0.1) / len(sentiment_scores),
                'negative_ratio': sum(1 for s in sentiment_scores if s < -0.1) / len(sentiment_scores),
                'neutral_ratio': sum(1 for s in sentiment_scores if -0.1 <= s <= 0.1) / len(sentiment_scores),
                'extreme_sentiment_frequency': sum(1 for s in sentiment_scores if abs(s) > 0.7) / len(sentiment_scores),
                'sentiment_consistency': 1 - (statistics.stdev(sentiment_scores) if len(sentiment_scores) > 1 else 0),
                'emotional_range': max(sentiment_scores) - min(sentiment_scores),
                'recent_trend': await self._calculate_recent_sentiment_trend(sentiment_scores[-10:] if len(sentiment_scores) >= 10 else sentiment_scores)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment patterns: {str(e)}")
            return {}

    async def _calculate_recent_sentiment_trend(self, recent_scores: List[float]) -> str:
        """Calculate recent sentiment trend direction"""
        if len(recent_scores) < 2:
            return "stable"
        
        # Calculate trend using simple linear regression
        x = np.arange(len(recent_scores))
        y = np.array(recent_scores)
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"
