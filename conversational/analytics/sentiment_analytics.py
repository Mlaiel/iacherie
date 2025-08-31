"""Sentiment Analytics Engine for IA Influencer Agent Platform
Advanced sentiment analysis and emotional intelligence for conversational AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use,
copying, distribution, or reproduction is strictly prohibited and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textblob
from collections import defaultdict
import re
import json


class SentimentDimension(Enum):
    """Dimensions of sentiment analysis."""    POLARITY = "polarity"  # positive/negative
    INTENSITY = "intensity"  # strength of emotion
    EMOTION = "emotion"  # specific emotions
    SUBJECTIVITY = "subjectivity"  # subjective vs objective
    CONFIDENCE = "confidence"  # certainty level
    URGENCY = "urgency"  # urgency level
    SATISFACTION = "satisfaction"  # user satisfaction
    TRUST = "trust"  # trust level


class EmotionType(Enum):
    """Specific emotion types for detailed analysis."""    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    CONFUSION = "confusion"
    SATISFACTION = "satisfaction"


@dataclass
class SentimentScore:
    """Comprehensive sentiment score data structure."""    text_id: str
    text: str
    timestamp: datetime
    polarity_score: float  # -1 to 1
    intensity_score: float  # 0 to 1
    confidence_score: float  # 0 to 1
    subjectivity_score: float  # 0 to 1
    primary_emotion: EmotionType
    emotion_scores: Dict[EmotionType, float]
    sentiment_trend: str
    context_factors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmotionalProfile:
    """User's emotional profile based on conversation history."""    user_id: str
    dominant_emotions: List[EmotionType]
    emotional_stability: float
    sentiment_patterns: Dict[str, float]
    trigger_words: List[str]
    emotional_journey: List[Dict[str, Any]]
    communication_style: str
    empathy_needs: List[str]
    last_updated: datetime


class SentimentAnalytics:
    """    Enterprise-grade sentiment analytics engine for comprehensive
    emotional intelligence and sentiment tracking in conversations.
    """    
    def __init__(self, db_session: AsyncSession, model_cache_dir: str = "./models"):
        self.db_session = db_session
        self.model_cache_dir = model_cache_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize sentiment analysis models
        self.sentiment_models = {}
        self.emotion_classifier = None
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Emotional intelligence components
        self.emotional_profiles = {}
        self.sentiment_history = defaultdict(list)
        self.trigger_patterns = {}
        
        # Analysis configurations
        self.sentiment_thresholds = {
            'very_positive': 0.6,
            'positive': 0.2,
            'neutral': -0.2,
            'negative': -0.6,
            'very_negative': -1.0
        }
        
        self.emotion_weights = {
            EmotionType.JOY: 1.0,
            EmotionType.SATISFACTION: 0.9,
            EmotionType.TRUST: 0.8,
            EmotionType.EXCITEMENT: 0.7,
            EmotionType.ANTICIPATION: 0.6,
            EmotionType.SURPRISE: 0.5,
            EmotionType.CONFUSION: -0.3,
            EmotionType.FRUSTRATION: -0.6,
            EmotionType.ANGER: -0.8,
            EmotionType.SADNESS: -0.7,
            EmotionType.FEAR: -0.9,
            EmotionType.DISGUST: -0.8
        }
    
    async def initialize_sentiment_models(self):
        """Initialize sentiment analysis and emotion detection models."""        try:
            self.logger.info("Initializing sentiment analytics models")
            
            # Initialize sentiment analysis pipeline
            self.sentiment_models['roberta'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Initialize emotion classification
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Initialize additional sentiment models
            self.sentiment_models['finbert'] = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert"
            )
            
            self.logger.info("Sentiment analytics models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing sentiment models: {str(e)}")
            raise
    
    async def analyze_text_sentiment(self, text: str, context: Optional[Dict[str, Any]] = None) -> SentimentScore:
        """Perform comprehensive sentiment analysis on text."""        try:
            text_id = f"text_{int(datetime.utcnow().timestamp())}"
            
            # Multi-model sentiment analysis
            roberta_sentiment = await self._analyze_with_roberta(text)
            vader_sentiment = self._analyze_with_vader(text)
            textblob_sentiment = self._analyze_with_textblob(text)
            
            # Emotion classification
            emotions = await self._classify_emotions(text)
            
            # Combine sentiment scores
            combined_polarity = self._combine_sentiment_scores(
                roberta_sentiment['polarity'],
                vader_sentiment['polarity'],
                textblob_sentiment['polarity']
            )
            
            # Calculate intensity and confidence
            intensity = self._calculate_sentiment_intensity(roberta_sentiment, vader_sentiment)
            confidence = self._calculate_confidence_score(roberta_sentiment, vader_sentiment, textblob_sentiment)
            
            # Determine primary emotion
            primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            
            # Analyze context factors
            context_factors = self._analyze_context_factors(text, context)
            
            # Determine sentiment trend
            sentiment_trend = self._determine_sentiment_trend(combined_polarity, intensity)
            
            sentiment_score = SentimentScore(
                text_id=text_id,
                text=text,
                timestamp=datetime.utcnow(),
                polarity_score=combined_polarity,
                intensity_score=intensity,
                confidence_score=confidence,
                subjectivity_score=textblob_sentiment['subjectivity'],
                primary_emotion=primary_emotion,
                emotion_scores=emotions,
                sentiment_trend=sentiment_trend,
                context_factors=context_factors,
                metadata={
                    'raw_scores': {
                        'roberta': roberta_sentiment,
                        'vader': vader_sentiment,
                        'textblob': textblob_sentiment
                    },
                    'context': context
                }
            )
            
            return sentiment_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing text sentiment: {str(e)}")
            raise
    
    async def analyze_conversation_sentiment_flow(self, conversation_turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment flow throughout a conversation."""        try:
            sentiment_timeline = []
            user_sentiment_scores = []
            ai_response_effectiveness = []
            
            for i, turn in enumerate(conversation_turns):
                # Analyze turn sentiment
                sentiment = await self.analyze_text_sentiment(
                    turn['message'], 
                    context={'turn_number': i, 'speaker': turn['speaker']}
                )
                
                sentiment_timeline.append({
                    'turn_number': i,
                    'speaker': turn['speaker'],
                    'polarity': sentiment.polarity_score,
                    'intensity': sentiment.intensity_score,
                    'primary_emotion': sentiment.primary_emotion.value,
                    'timestamp': turn.get('timestamp', datetime.utcnow())
                })
                
                if turn['speaker'] == 'user':
                    user_sentiment_scores.append(sentiment.polarity_score)
                    
                    # Analyze AI response effectiveness (if next turn is AI)
                    if i + 1 < len(conversation_turns) and conversation_turns[i + 1]['speaker'] == 'ai':
                        effectiveness = await self._analyze_response_effectiveness(
                            turn, conversation_turns[i + 1], sentiment
                        )
                        ai_response_effectiveness.append(effectiveness)
            
            # Calculate conversation-level metrics
            sentiment_progression = self._calculate_sentiment_progression(user_sentiment_scores)
            emotional_journey = self._map_emotional_journey(sentiment_timeline)
            conversation_mood = self._determine_conversation_mood(sentiment_timeline)
            
            return {
                'conversation_id': conversation_turns[0].get('conversation_id', 'unknown'),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'sentiment_timeline': sentiment_timeline,
                'sentiment_progression': sentiment_progression,
                'emotional_journey': emotional_journey,
                'conversation_mood': conversation_mood,
                'ai_response_effectiveness': {
                    'average_effectiveness': np.mean(ai_response_effectiveness) if ai_response_effectiveness else 0,
                    'effectiveness_scores': ai_response_effectiveness
                },
                'sentiment_metrics': {
                    'initial_sentiment': user_sentiment_scores[0] if user_sentiment_scores else 0,
                    'final_sentiment': user_sentiment_scores[-1] if user_sentiment_scores else 0,
                    'sentiment_improvement': (user_sentiment_scores[-1] - user_sentiment_scores[0]) if len(user_sentiment_scores) > 1 else 0,
                    'sentiment_volatility': np.std(user_sentiment_scores) if user_sentiment_scores else 0,
                    'average_sentiment': np.mean(user_sentiment_scores) if user_sentiment_scores else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing conversation sentiment flow: {str(e)}")
            return {}
    
    async def build_user_emotional_profile(self, user_id: str) -> EmotionalProfile:
        """Build comprehensive emotional profile for a user."""        try:
            # Get user's conversation history
            user_conversations = await self._get_user_conversations(user_id)
            
            # Analyze all user messages
            all_sentiments = []
            emotion_frequencies = defaultdict(int)
            trigger_words = []
            
            for conversation in user_conversations:
                for turn in conversation['turns']:
                    if turn['speaker'] == 'user':
                        sentiment = await self.analyze_text_sentiment(turn['message'])
                        all_sentiments.append(sentiment)
                        
                        # Count emotions
                        emotion_frequencies[sentiment.primary_emotion] += 1
                        
                        # Collect potential trigger words
                        if sentiment.polarity_score < -0.5:  # Strong negative sentiment
                            triggers = self._extract_trigger_words(turn['message'])
                            trigger_words.extend(triggers)
            
            # Calculate emotional stability
            sentiment_scores = [s.polarity_score for s in all_sentiments]
            emotional_stability = 1 - np.std(sentiment_scores) if sentiment_scores else 0
            
            # Identify dominant emotions
            dominant_emotions = sorted(
                emotion_frequencies.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            dominant_emotions = [emotion for emotion, _ in dominant_emotions]
            
            # Analyze sentiment patterns
            sentiment_patterns = self._analyze_user_sentiment_patterns(all_sentiments)
            
            # Map emotional journey
            emotional_journey = self._create_emotional_journey_map(all_sentiments)
            
            # Determine communication style
            communication_style = self._determine_communication_style(all_sentiments)
            
            # Identify empathy needs
            empathy_needs = self._identify_empathy_needs(all_sentiments, dominant_emotions)
            
            profile = EmotionalProfile(
                user_id=user_id,
                dominant_emotions=dominant_emotions,
                emotional_stability=emotional_stability,
                sentiment_patterns=sentiment_patterns,
                trigger_words=list(set(trigger_words)),
                emotional_journey=emotional_journey,
                communication_style=communication_style,
                empathy_needs=empathy_needs,
                last_updated=datetime.utcnow()
            )
            
            # Cache the profile
            self.emotional_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error building emotional profile: {str(e)}")
            raise
    
    async def generate_emotional_intelligence_insights(self, time_period: int = 30) -> Dict[str, Any]:
        """Generate insights about emotional intelligence and sentiment patterns."""        try:
            # Get sentiment data for the period
            sentiment_data = await self._get_sentiment_data_by_period(time_period)
            
            # Analyze overall sentiment trends
            sentiment_trends = self._analyze_overall_sentiment_trends(sentiment_data)
            
            # Identify emotional patterns
            emotional_patterns = self._identify_emotional_patterns(sentiment_data)
            
            # Analyze AI emotional intelligence performance
            ai_ei_performance = await self._analyze_ai_emotional_intelligence(sentiment_data)
            
            # Identify improvement opportunities
            improvement_opportunities = self._identify_ei_improvements(sentiment_data, ai_ei_performance)
            
            # Generate emotional intelligence recommendations
            ei_recommendations = await self._generate_ei_recommendations(improvement_opportunities)
            
            return {
                'analysis_period_days': time_period,
                'total_interactions': len(sentiment_data),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'sentiment_trends': sentiment_trends,
                'emotional_patterns': emotional_patterns,
                'ai_emotional_intelligence': ai_ei_performance,
                'improvement_opportunities': improvement_opportunities,
                'recommendations': ei_recommendations,
                'emotional_health_score': self._calculate_emotional_health_score(sentiment_trends),
                'empathy_effectiveness': await self._measure_empathy_effectiveness(sentiment_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating EI insights: {str(e)}")
            return {}
    
    async def predict_user_emotional_state(self, user_id: str, recent_messages: List[str]) -> Dict[str, Any]:
        """Predict user's current emotional state based on recent interactions."""        try:
            # Get user's emotional profile
            if user_id not in self.emotional_profiles:
                await self.build_user_emotional_profile(user_id)
            
            user_profile = self.emotional_profiles.get(user_id)
            
            # Analyze recent messages
            recent_sentiments = []
            for message in recent_messages:
                sentiment = await self.analyze_text_sentiment(message)
                recent_sentiments.append(sentiment)
            
            # Predict emotional state based on patterns
            predicted_state = self._predict_emotional_state(user_profile, recent_sentiments)
            
            # Calculate confidence in prediction
            prediction_confidence = self._calculate_prediction_confidence(user_profile, recent_sentiments)
            
            # Generate intervention recommendations
            interventions = self._recommend_emotional_interventions(predicted_state, user_profile)
            
            return {
                'user_id': user_id,
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'predicted_emotional_state': predicted_state,
                'prediction_confidence': prediction_confidence,
                'current_sentiment_trend': self._analyze_recent_sentiment_trend(recent_sentiments),
                'emotional_triggers_detected': self._detect_emotional_triggers(recent_messages, user_profile),
                'recommended_interventions': interventions,
                'support_level_needed': self._assess_support_needs(predicted_state),
                'conversation_approach': self._recommend_conversation_approach(predicted_state, user_profile)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting emotional state: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _analyze_with_roberta(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using RoBERTa model."""        try:
            results = self.sentiment_models['roberta'](text)
            
            # Convert to polarity score
            polarity = 0.0
            for result in results:
                if result['label'] == 'LABEL_2':  # Positive
                    polarity += result['score']
                elif result['label'] == 'LABEL_0':  # Negative
                    polarity -= result['score']
            
            return {
                'polarity': polarity,
                'confidence': max(r['score'] for r in results),
                'raw_results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error with RoBERTa analysis: {str(e)}")
            return {'polarity': 0.0, 'confidence': 0.0, 'raw_results': []}
    
    def _analyze_with_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER."""        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'polarity': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
            
        except Exception as e:
            self.logger.error(f"Error with VADER analysis: {str(e)}")
            return {'polarity': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob."""        try:
            blob = textblob.TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
            
        except Exception as e:
            self.logger.error(f"Error with TextBlob analysis: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.5}
    
    async def _classify_emotions(self, text: str) -> Dict[EmotionType, float]:
        """Classify emotions in text."""        try:
            emotion_results = self.emotion_classifier(text)
            
            emotion_mapping = {
                'joy': EmotionType.JOY,
                'sadness': EmotionType.SADNESS,
                'anger': EmotionType.ANGER,
                'fear': EmotionType.FEAR,
                'surprise': EmotionType.SURPRISE,
                'disgust': EmotionType.DISGUST
            }
            
            emotions = {}
            for result in emotion_results:
                emotion_label = result['label'].lower()
                if emotion_label in emotion_mapping:
                    emotions[emotion_mapping[emotion_label]] = result['score']
            
            return emotions
            
        except Exception as e:
            self.logger.error(f"Error classifying emotions: {str(e)}")
            return {EmotionType.JOY: 0.0}
    
    def _combine_sentiment_scores(self, roberta_score: float, vader_score: float, textblob_score: float) -> float:
        """Combine sentiment scores from different models."""        # Weighted average with RoBERTa having highest weight
        weights = {'roberta': 0.5, 'vader': 0.3, 'textblob': 0.2}
        
        combined = (
            roberta_score * weights['roberta'] +
            vader_score * weights['vader'] +
            textblob_score * weights['textblob']
        )
        
        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, combined))
    
    def _calculate_sentiment_intensity(self, roberta_result: Dict, vader_result: Dict) -> float:
        """Calculate sentiment intensity based on model confidence and scores."""        # Use confidence from RoBERTa and absolute values from VADER
        roberta_intensity = roberta_result.get('confidence', 0)
        vader_intensity = abs(vader_result.get('polarity', 0))
        
        return (roberta_intensity + vader_intensity) / 2
    
    def _determine_sentiment_trend(self, polarity: float, intensity: float) -> str:
        """Determine sentiment trend based on polarity and intensity."""        if polarity > 0.2 and intensity > 0.6:
            return "strongly_positive"
        elif polarity > 0.2:
            return "positive"
        elif polarity < -0.2 and intensity > 0.6:
            return "strongly_negative"
        elif polarity < -0.2:
            return "negative"
        else:
            return "neutral"
