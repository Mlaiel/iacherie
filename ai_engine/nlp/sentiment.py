"""Specialized Sentiment Analysis Module for IA Influencer Agent Platform

Advanced sentiment analysis specifically designed for social media content,
influencer marketing, and audience engagement optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import json
from abc import ABC, abstractmethod
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class SentimentScore:
    """Sentiment score structure"""    positive: float
    negative: float
    neutral: float
    compound: float  # Overall sentiment score (-1 to 1)
    confidence: float
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    intensity: str = "moderate"  # low, moderate, high, extreme

@dataclass
class EmotionAnalysis:
    """Detailed emotion analysis"""    primary_emotion: str
    secondary_emotions: List[str]
    emotion_intensity: float
    emotional_stability: float  # How consistent the emotion is throughout
    emotional_complexity: int  # Number of different emotions detected
    emotion_progression: List[Dict[str, Any]] = field(default_factory=list)  # How emotions change

@dataclass
class EngagementSentiment:
    """Engagement-focused sentiment analysis"""    engagement_potential: float  # 0-1 score for likely engagement
    virality_score: float  # Potential for viral spread
    controversy_level: float  # How controversial the content is
    call_to_action_strength: float  # Strength of CTA sentiment
    authenticity_score: float  # How authentic the sentiment feels
    brand_safety_score: float  # Safety for brand association

@dataclass
class SentimentAnalysisResult:
    """Complete sentiment analysis result"""    request_id: str
    original_text: str
    sentiment: SentimentScore
    emotions: EmotionAnalysis
    engagement: EngagementSentiment
    platform_optimization: Dict[str, Any]
    audience_reactions: Dict[str, float]  # Predicted audience reactions
    content_recommendations: List[str]
    sentiment_keywords: List[str]
    mood_indicators: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class AdvancedSentimentAnalyzer:
    """    Advanced sentiment analyzer for influencer content
    
    Features:
    - Multi-dimensional sentiment analysis
    - Platform-specific optimization
    - Audience-targeted sentiment prediction
    - Engagement potential scoring
    - Brand safety assessment
    - Real-time sentiment monitoring
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.sentiment_models = self._initialize_sentiment_models()
        self.platform_patterns = self._load_platform_patterns()
        self.audience_profiles = self._load_audience_profiles()
        self.brand_safety_rules = self._load_brand_safety_rules()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""        return {
            'enable_emotion_analysis': True,
            'enable_engagement_prediction': True,
            'enable_brand_safety': True,
            'confidence_threshold': 0.7,
            'multi_language_support': True,
            'real_time_monitoring': True,
            'cache_results': True,
            'detailed_analysis': True
        }
    
    def _load_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Load comprehensive emotion lexicon"""        return {
            # Basic emotions with intensity scores
            'joy': {
                'happy': 0.8, 'excited': 0.9, 'thrilled': 0.95, 'elated': 0.9,
                'cheerful': 0.7, 'delighted': 0.85, 'ecstatic': 0.95, 'joyful': 0.8,
                'euphoric': 1.0, 'blissful': 0.9, 'content': 0.6, 'pleased': 0.7,
                '😊': 0.8, '😁': 0.9, '🤩': 0.95, '🥳': 0.9, '❤️': 0.8
            },
            'sadness': {
                'sad': 0.8, 'depressed': 0.9, 'miserable': 0.95, 'devastated': 1.0,
                'heartbroken': 0.95, 'disappointed': 0.7, 'melancholy': 0.8,
                'despondent': 0.9, 'grief': 0.95, 'sorrow': 0.85, 'gloom': 0.8,
                '😢': 0.8, '😭': 0.9, '💔': 0.9, '😞': 0.7
            },
            'anger': {
                'angry': 0.8, 'furious': 0.95, 'rage': 1.0, 'mad': 0.8,
                'irritated': 0.6, 'annoyed': 0.5, 'outraged': 0.95, 'livid': 0.9,
                'enraged': 0.95, 'irate': 0.85, 'aggravated': 0.7, 'frustrated': 0.7,
                '😠': 0.8, '😡': 0.9, '🤬': 0.95
            },
            'fear': {
                'afraid': 0.8, 'scared': 0.8, 'terrified': 0.95, 'anxious': 0.7,
                'worried': 0.6, 'nervous': 0.6, 'panicked': 0.9, 'frightened': 0.85,
                'alarmed': 0.8, 'concerned': 0.5, 'apprehensive': 0.7,
                '😨': 0.8, '😰': 0.7, '😱': 0.9
            },
            'surprise': {
                'surprised': 0.7, 'amazed': 0.8, 'astonished': 0.9, 'shocked': 0.8,
                'stunned': 0.85, 'bewildered': 0.7, 'dumbfounded': 0.8,
                'flabbergasted': 0.9, 'astounded': 0.85,
                '😲': 0.8, '😮': 0.7, '🤯': 0.9
            },
            'disgust': {
                'disgusted': 0.8, 'revolted': 0.9, 'repulsed': 0.85, 'sickened': 0.8,
                'nauseated': 0.8, 'appalled': 0.85, 'horrified': 0.9,
                '🤢': 0.8, '🤮': 0.9, '😷': 0.7
            },
            'trust': {
                'trust': 0.8, 'confident': 0.8, 'secure': 0.7, 'certain': 0.7,
                'assured': 0.75, 'reliable': 0.8, 'dependable': 0.8, 'faithful': 0.85,
                'loyal': 0.8, 'honest': 0.8, 'genuine': 0.75
            },
            'anticipation': {
                'excited': 0.8, 'eager': 0.8, 'hopeful': 0.7, 'optimistic': 0.7,
                'expectant': 0.7, 'enthusiastic': 0.85, 'keen': 0.75, 'impatient': 0.6,
                'looking forward': 0.8
            }
        }
    
    def _initialize_sentiment_models(self) -> Dict[str, Any]:
        """Initialize sentiment analysis models"""        return {
            'base_model': 'bert-sentiment',  # Would use actual BERT model
            'social_media_model': 'roberta-sentiment-social',  # Specialized for social media
            'influencer_model': 'custom-influencer-sentiment',  # Custom trained
            'multilingual_model': 'xlm-sentiment',  # For multiple languages
            'engagement_model': 'engagement-predictor',  # For engagement prediction
            'brand_safety_model': 'brand-safety-classifier'  # For brand safety
        }
    
    def _load_platform_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific sentiment patterns"""        return {
            'instagram': {
                'positive_indicators': ['✨', '💫', '🌟', '💖', '🔥', 'goals', 'vibes', 'mood'],
                'engagement_boosters': ['story time', 'swipe up', 'link in bio', 'dm me'],
                'authenticity_markers': ['real talk', 'no filter', 'behind the scenes', 'honest'],
                'typical_sentiment_range': (0.3, 0.8),  # Generally positive platform
                'optimal_emotion_mix': {'joy': 0.4, 'excitement': 0.3, 'trust': 0.3}
            },
            'twitter': {
                'positive_indicators': ['👏', '🙌', '💯', '🔥', 'thread', 'this'],
                'engagement_boosters': ['retweet', 'rt', 'thread', 'your thoughts?'],
                'controversy_markers': ['unpopular opinion', 'hot take', 'controversial'],
                'typical_sentiment_range': (-0.2, 0.6),  # More varied sentiment
                'optimal_emotion_mix': {'surprise': 0.3, 'trust': 0.4, 'anticipation': 0.3}
            },
            'linkedin': {
                'positive_indicators': ['proud', 'grateful', 'honored', 'excited', 'professional'],
                'engagement_boosters': ['thoughts?', 'agree?', 'experience', 'insights'],
                'professional_markers': ['career', 'growth', 'leadership', 'industry'],
                'typical_sentiment_range': (0.2, 0.7),  # Professional positive
                'optimal_emotion_mix': {'trust': 0.5, 'anticipation': 0.3, 'joy': 0.2}
            },
            'tiktok': {
                'positive_indicators': ['💀', '😭', 'not me', 'pov', 'viral', 'trend'],
                'engagement_boosters': ['duet this', 'stitch', 'comment', 'part 2'],
                'trend_markers': ['trend', 'viral', 'for you page', 'fyp'],
                'typical_sentiment_range': (-0.1, 0.9),  # High energy, varied
                'optimal_emotion_mix': {'surprise': 0.4, 'joy': 0.4, 'anticipation': 0.2}
            },
            'youtube': {
                'positive_indicators': ['subscribe', 'like', 'notification bell', 'comment'],
                'engagement_boosters': ['subscribe', 'bell icon', 'comment below', 'like'],
                'retention_markers': ['watch until end', 'stay tuned', 'coming up'],
                'typical_sentiment_range': (0.1, 0.8),  # Generally positive
                'optimal_emotion_mix': {'anticipation': 0.4, 'joy': 0.3, 'surprise': 0.3}
            }
        }
    
    def _load_audience_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load audience sentiment preferences"""        return {
            'gen_z': {
                'preferred_emotions': ['excitement', 'surprise', 'humor'],
                'engagement_triggers': ['authentic', 'relatable', 'chaotic'],
                'sentiment_sensitivity': 0.8,  # High sensitivity to sentiment
                'authenticity_importance': 0.9
            },
            'millennials': {
                'preferred_emotions': ['nostalgia', 'hope', 'determination'],
                'engagement_triggers': ['authentic', 'meaningful', 'progress'],
                'sentiment_sensitivity': 0.7,
                'authenticity_importance': 0.8
            },
            'gen_x': {
                'preferred_emotions': ['trust', 'respect', 'achievement'],
                'engagement_triggers': ['professional', 'family', 'experience'],
                'sentiment_sensitivity': 0.6,
                'authenticity_importance': 0.7
            },
            'boomers': {
                'preferred_emotions': ['trust', 'security', 'tradition'],
                'engagement_triggers': ['family', 'values', 'experience'],
                'sentiment_sensitivity': 0.5,
                'authenticity_importance': 0.9
            }
        }
    
    def _load_brand_safety_rules(self) -> Dict[str, Any]:
        """Load brand safety rules and thresholds"""        return {
            'safe_sentiment_range': (0.2, 0.8),  # Safe sentiment range
            'max_controversy_level': 0.3,  # Maximum acceptable controversy
            'min_authenticity_score': 0.6,  # Minimum authenticity requirement
            'blocked_emotions': ['hate', 'disgust', 'extreme_anger'],
            'warning_keywords': [
                'controversial', 'hate', 'discrimination', 'violence',
                'politics', 'religion', 'adult content'
            ],
            'safe_emotions': ['joy', 'trust', 'anticipation', 'surprise'],
            'brand_friendly_sentiments': ['positive', 'neutral', 'inspiring', 'educational']
        }
    
    async def analyze_sentiment(self, text: str, platform: str = "general", 
                              target_audience: str = "general", 
                              content_type: str = "post") -> SentimentAnalysisResult:
        """Comprehensive sentiment analysis"""        request_id = self._generate_request_id(text, platform)
        
        try:
            # Core sentiment analysis
            sentiment_score = await self._analyze_core_sentiment(text)
            
            # Emotion analysis
            emotion_analysis = await self._analyze_emotions(text)
            
            # Engagement sentiment analysis
            engagement_sentiment = await self._analyze_engagement_sentiment(
                text, platform, target_audience
            )
            
            # Platform-specific optimization
            platform_optimization = await self._optimize_for_platform(
                text, platform, sentiment_score, emotion_analysis
            )
            
            # Predict audience reactions
            audience_reactions = await self._predict_audience_reactions(
                text, sentiment_score, emotion_analysis, target_audience
            )
            
            # Generate content recommendations
            recommendations = await self._generate_sentiment_recommendations(
                sentiment_score, emotion_analysis, engagement_sentiment, platform
            )
            
            # Extract sentiment keywords
            sentiment_keywords = await self._extract_sentiment_keywords(text)
            
            # Identify mood indicators
            mood_indicators = await self._identify_mood_indicators(text)
            
            result = SentimentAnalysisResult(
                request_id=request_id,
                original_text=text,
                sentiment=sentiment_score,
                emotions=emotion_analysis,
                engagement=engagement_sentiment,
                platform_optimization=platform_optimization,
                audience_reactions=audience_reactions,
                content_recommendations=recommendations,
                sentiment_keywords=sentiment_keywords,
                mood_indicators=mood_indicators
            )
            
            logger.info(f"Sentiment analysis completed: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {request_id}: {str(e)}")
            raise
    
    async def batch_analyze_sentiment(self, texts: List[str], platform: str = "general") -> List[SentimentAnalysisResult]:
        """Batch sentiment analysis"""        tasks = [self.analyze_sentiment(text, platform) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch sentiment analysis error: {str(result)}")
                # Create error result
                error_result = SentimentAnalysisResult(
                    request_id="error",
                    original_text="",
                    sentiment=SentimentScore(0.0, 0.0, 1.0, 0.0, 0.0),
                    emotions=EmotionAnalysis("neutral", [], 0.0, 0.0, 0),
                    engagement=EngagementSentiment(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                    platform_optimization={},
                    audience_reactions={},
                    content_recommendations=[],
                    sentiment_keywords=[],
                    mood_indicators=[]
                )
                valid_results.append(error_result)
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _analyze_core_sentiment(self, text: str) -> SentimentScore:
        """Analyze core sentiment using multiple approaches"""        
        # Lexicon-based sentiment analysis
        lexicon_sentiment = await self._lexicon_based_sentiment(text)
        
        # Pattern-based sentiment analysis
        pattern_sentiment = await self._pattern_based_sentiment(text)
        
        # ML model-based sentiment (simulated)
        model_sentiment = await self._model_based_sentiment(text)
        
        # Combine different approaches
        combined_positive = (lexicon_sentiment['positive'] + pattern_sentiment['positive'] + model_sentiment['positive']) / 3
        combined_negative = (lexicon_sentiment['negative'] + pattern_sentiment['negative'] + model_sentiment['negative']) / 3
        combined_neutral = (lexicon_sentiment['neutral'] + pattern_sentiment['neutral'] + model_sentiment['neutral']) / 3
        
        # Calculate compound score
        compound = combined_positive - combined_negative
        
        # Calculate confidence based on agreement between methods
        confidence = self._calculate_sentiment_confidence(lexicon_sentiment, pattern_sentiment, model_sentiment)
        
        # Determine intensity
        intensity = self._determine_intensity(abs(compound))
        
        # Extract emotion scores
        emotion_scores = await self._extract_emotion_scores(text)
        
        return SentimentScore(
            positive=combined_positive,
            negative=combined_negative,
            neutral=combined_neutral,
            compound=compound,
            confidence=confidence,
            emotion_scores=emotion_scores,
            intensity=intensity
        )
    
    async def _lexicon_based_sentiment(self, text: str) -> Dict[str, float]:
        """Lexicon-based sentiment analysis"""        words = text.lower().split()
        total_sentiment = 0.0
        sentiment_words = 0
        
        positive_score = 0.0
        negative_score = 0.0
        
        for word in words:
            # Check in emotion lexicon
            for emotion, word_scores in self.emotion_lexicon.items():
                if word in word_scores:
                    score = word_scores[word]
                    sentiment_words += 1
                    
                    if emotion in ['joy', 'trust', 'anticipation']:
                        positive_score += score
                    elif emotion in ['sadness', 'anger', 'fear', 'disgust']:
                        negative_score += score
        
        # Normalize scores
        if sentiment_words > 0:
            positive_score /= sentiment_words
            negative_score /= sentiment_words
        
        neutral_score = 1.0 - positive_score - negative_score
        neutral_score = max(0.0, neutral_score)
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score
        }
    
    async def _pattern_based_sentiment(self, text: str) -> Dict[str, float]:
        """Pattern-based sentiment analysis"""        
        # Positive patterns
        positive_patterns = [
            r'\b(love|amazing|awesome|fantastic|incredible|perfect|excellent)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'😊|😁|🤩|🥳|❤️|💖|✨|🔥|💯',  # Positive emojis
            r'\b(yes|absolutely|definitely|totally)\b'
        ]
        
        # Negative patterns
        negative_patterns = [
            r'\b(hate|terrible|awful|horrible|disgusting|worst)\b',
            r'\b(no|never|nothing|nobody|nowhere)\b',
            r'😢|😭|😠|😡|💔|😞|🤬',  # Negative emojis
            r'\b(disappointed|frustrated|angry|sad)\b'
        ]
        
        # Neutral patterns
        neutral_patterns = [
            r'\b(okay|fine|alright|maybe|perhaps)\b',
            r'\b(the|and|is|are|was|were)\b'  # Common neutral words
        ]
        
        positive_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in positive_patterns)
        negative_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in negative_patterns)
        neutral_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in neutral_patterns)
        
        total_matches = positive_matches + negative_matches + neutral_matches
        
        if total_matches == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_matches / total_matches,
            'negative': negative_matches / total_matches,
            'neutral': neutral_matches / total_matches
        }
    
    async def _model_based_sentiment(self, text: str) -> Dict[str, float]:
        """ML model-based sentiment analysis (simulated)"""        # In practice, this would use actual ML models like BERT, RoBERTa, etc.
        
        # Simplified model simulation based on text characteristics
        text_length = len(text)
        word_count = len(text.split())
        
        # Base sentiment based on length and structure
        if text_length < 50:
            # Short text tends to be more neutral or slightly positive
            base_positive = 0.4
            base_negative = 0.2
            base_neutral = 0.4
        elif text_length > 200:
            # Longer text tends to be more complex sentiment
            base_positive = 0.35
            base_negative = 0.35
            base_neutral = 0.3
        else:
            # Medium text
            base_positive = 0.45
            base_negative = 0.25
            base_neutral = 0.3
        
        # Adjust based on punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        if exclamation_count > 0:
            base_positive += min(0.2, exclamation_count * 0.05)
            base_neutral -= min(0.15, exclamation_count * 0.03)
        
        if question_count > 0:
            base_neutral += min(0.1, question_count * 0.02)
            base_positive -= min(0.05, question_count * 0.01)
        
        # Normalize to sum to 1
        total = base_positive + base_negative + base_neutral
        
        return {
            'positive': base_positive / total,
            'negative': base_negative / total,
            'neutral': base_neutral / total
        }
    
    def _calculate_sentiment_confidence(self, lexicon: Dict[str, float], 
                                      pattern: Dict[str, float], 
                                      model: Dict[str, float]) -> float:
        """Calculate confidence based on agreement between methods"""        
        # Calculate variance for each sentiment dimension
        positive_variance = np.var([lexicon['positive'], pattern['positive'], model['positive']])
        negative_variance = np.var([lexicon['negative'], pattern['negative'], model['negative']])
        neutral_variance = np.var([lexicon['neutral'], pattern['neutral'], model['neutral']])
        
        # Average variance
        avg_variance = (positive_variance + negative_variance + neutral_variance) / 3
        
        # Convert variance to confidence (lower variance = higher confidence)
        confidence = max(0.0, 1.0 - (avg_variance * 10))
        
        return min(1.0, confidence)
    
    def _determine_intensity(self, compound_abs: float) -> str:
        """Determine sentiment intensity"""        if compound_abs >= 0.8:
            return "extreme"
        elif compound_abs >= 0.6:
            return "high"
        elif compound_abs >= 0.3:
            return "moderate"
        else:
            return "low"
    
    async def _extract_emotion_scores(self, text: str) -> Dict[str, float]:
        """Extract detailed emotion scores"""        emotion_scores = {}
        words = text.lower().split()
        
        for emotion, word_scores in self.emotion_lexicon.items():
            total_score = 0.0
            word_count = 0
            
            for word in words:
                if word in word_scores:
                    total_score += word_scores[word]
                    word_count += 1
            
            if word_count > 0:
                emotion_scores[emotion] = total_score / word_count
            else:
                emotion_scores[emotion] = 0.0
        
        return emotion_scores
    
    async def _analyze_emotions(self, text: str) -> EmotionAnalysis:
        """Detailed emotion analysis"""        
        # Get emotion scores
        emotion_scores = await self._extract_emotion_scores(text)
        
        # Find primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else "neutral"
        
        # Find secondary emotions (emotions with score > 0.3)
        secondary_emotions = [
            emotion for emotion, score in emotion_scores.items()
            if score > 0.3 and emotion != primary_emotion
        ]
        secondary_emotions.sort(key=lambda x: emotion_scores[x], reverse=True)
        secondary_emotions = secondary_emotions[:3]  # Top 3 secondary emotions
        
        # Calculate emotion intensity
        emotion_intensity = emotion_scores.get(primary_emotion, 0.0)
        
        # Calculate emotional stability (consistency)
        emotion_values = list(emotion_scores.values())
        emotional_stability = 1.0 - (np.std(emotion_values) if emotion_values else 0.0)
        
        # Calculate emotional complexity
        emotional_complexity = sum(1 for score in emotion_scores.values() if score > 0.2)
        
        # Analyze emotion progression (for longer texts)
        emotion_progression = await self._analyze_emotion_progression(text)
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            emotion_intensity=emotion_intensity,
            emotional_stability=emotional_stability,
            emotional_complexity=emotional_complexity,
            emotion_progression=emotion_progression
        )
    
    async def _analyze_emotion_progression(self, text: str) -> List[Dict[str, Any]]:
        """Analyze how emotions change throughout the text"""        sentences = text.split('.')
        if len(sentences) < 3:
            return []  # Not enough content for progression analysis
        
        progression = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence_emotions = await self._extract_emotion_scores(sentence)
                primary_emotion = max(sentence_emotions, key=sentence_emotions.get) if sentence_emotions else "neutral"
                
                progression.append({
                    'position': i,
                    'sentence': sentence.strip(),
                    'primary_emotion': primary_emotion,
                    'emotion_intensity': sentence_emotions.get(primary_emotion, 0.0),
                    'emotions': sentence_emotions
                })
        
        return progression
    
    async def _analyze_engagement_sentiment(self, text: str, platform: str, target_audience: str) -> EngagementSentiment:
        """Analyze engagement-focused sentiment"""        
        # Calculate engagement potential
        engagement_potential = await self._calculate_engagement_potential(text, platform)
        
        # Calculate virality score
        virality_score = await self._calculate_virality_score(text, platform)
        
        # Calculate controversy level
        controversy_level = await self._calculate_controversy_level(text)
        
        # Calculate call-to-action strength
        cta_strength = await self._calculate_cta_strength(text, platform)
        
        # Calculate authenticity score
        authenticity_score = await self._calculate_authenticity_score(text, target_audience)
        
        # Calculate brand safety score
        brand_safety_score = await self._calculate_brand_safety_score(text)
        
        return EngagementSentiment(
            engagement_potential=engagement_potential,
            virality_score=virality_score,
            controversy_level=controversy_level,
            call_to_action_strength=cta_strength,
            authenticity_score=authenticity_score,
            brand_safety_score=brand_safety_score
        )
    
    async def _calculate_engagement_potential(self, text: str, platform: str) -> float:
        """Calculate potential for audience engagement"""        score = 0.0
        
        # Platform-specific engagement indicators
        platform_patterns = self.platform_patterns.get(platform, {})
        engagement_boosters = platform_patterns.get('engagement_boosters', [])
        
        for booster in engagement_boosters:
            if booster.lower() in text.lower():
                score += 0.2
        
        # Question indicators (encourage responses)
        if '?' in text:
            score += 0.15 * text.count('?')
        
        # Emotional engagement indicators
        emotion_scores = await self._extract_emotion_scores(text)
        high_engagement_emotions = ['surprise', 'joy', 'anticipation']
        
        for emotion in high_engagement_emotions:
            score += emotion_scores.get(emotion, 0.0) * 0.3
        
        # Personal pronouns (relatability)
        personal_pronouns = ['you', 'your', 'we', 'us', 'our']
        for pronoun in personal_pronouns:
            score += text.lower().count(pronoun) * 0.05
        
        return min(1.0, score)
    
    async def _calculate_virality_score(self, text: str, platform: str) -> float:
        """Calculate potential for viral spread"""        score = 0.0
        
        # Platform-specific viral indicators
        platform_patterns = self.platform_patterns.get(platform, {})
        
        if platform == 'tiktok':
            viral_words = ['trend', 'viral', 'fyp', 'for you', 'pov', 'not me']
            for word in viral_words:
                if word in text.lower():
                    score += 0.2
        elif platform == 'twitter':
            viral_words = ['thread', 'this', 'everyone needs to see', 'retweet']
            for word in viral_words:
                if word in text.lower():
                    score += 0.15
        
        # Strong emotional content
        emotion_scores = await self._extract_emotion_scores(text)
        intense_emotions = ['surprise', 'anger', 'joy']
        
        for emotion in intense_emotions:
            if emotion_scores.get(emotion, 0.0) > 0.7:
                score += 0.25
        
        # Shocking or controversial elements
        controversial_keywords = ['shocking', 'unbelievable', 'you won\'t believe', 'mind-blowing']
        for keyword in controversial_keywords:
            if keyword in text.lower():
                score += 0.2
        
        return min(1.0, score)
    
    async def _calculate_controversy_level(self, text: str) -> float:
        """Calculate controversy level"""        controversy_score = 0.0
        
        # Controversial keywords
        controversial_words = [
            'controversial', 'unpopular opinion', 'hot take', 'debate',
            'argue', 'disagree', 'wrong', 'stupid', 'ridiculous'
        ]
        
        for word in controversial_words:
            if word in text.lower():
                controversy_score += 0.2
        
        # Strong negative emotions
        emotion_scores = await self._extract_emotion_scores(text)
        controversial_emotions = ['anger', 'disgust']
        
        for emotion in controversial_emotions:
            controversy_score += emotion_scores.get(emotion, 0.0) * 0.3
        
        # Extreme language
        extreme_words = ['always', 'never', 'everyone', 'nobody', 'completely', 'totally']
        for word in extreme_words:
            controversy_score += text.lower().count(word) * 0.05
        
        return min(1.0, controversy_score)
    
    async def _calculate_cta_strength(self, text: str, platform: str) -> float:
        """Calculate call-to-action strength"""        cta_score = 0.0
        
        # Direct CTAs
        direct_ctas = [
            'click', 'buy', 'shop', 'subscribe', 'follow', 'like', 'share',
            'comment', 'dm', 'message', 'check out', 'visit', 'download'
        ]
        
        for cta in direct_ctas:
            cta_score += text.lower().count(cta) * 0.15
        
        # Urgency indicators
        urgency_words = ['now', 'today', 'limited', 'hurry', 'quick', 'fast']
        for word in urgency_words:
            cta_score += text.lower().count(word) * 0.1
        
        # Platform-specific CTAs
        platform_patterns = self.platform_patterns.get(platform, {})
        platform_ctas = platform_patterns.get('engagement_boosters', [])
        
        for cta in platform_ctas:
            if cta.lower() in text.lower():
                cta_score += 0.2
        
        return min(1.0, cta_score)
    
    async def _calculate_authenticity_score(self, text: str, target_audience: str) -> float:
        """Calculate authenticity score"""        authenticity_score = 0.8  # Start with high base score
        
        # Authentic language indicators
        authentic_phrases = [
            'real talk', 'honestly', 'to be honest', 'personally', 'in my experience',
            'no filter', 'authentic', 'genuine', 'from the heart'
        ]
        
        for phrase in authentic_phrases:
            if phrase in text.lower():
                authenticity_score += 0.1
        
        # Personal pronouns and experiences
        personal_indicators = ['i', 'me', 'my', 'mine', 'myself']
        personal_count = sum(text.lower().count(word) for word in personal_indicators)
        authenticity_score += min(0.2, personal_count * 0.02)
        
        # Overly promotional language (reduces authenticity)
        promotional_words = [
            'amazing deal', 'incredible offer', 'limited time', 'act now',
            'don\'t miss out', 'exclusive', 'special promotion'
        ]
        
        for word in promotional_words:
            if word in text.lower():
                authenticity_score -= 0.15
        
        # Perfect grammar/no imperfections (might seem less authentic)
        if not re.search(r'[.]{2,}|!+|\?+|[\w\']{15,}', text):
            authenticity_score -= 0.1  # Slightly reduce for overly perfect text
        
        return max(0.0, min(1.0, authenticity_score))
    
    async def _calculate_brand_safety_score(self, text: str) -> float:
        """Calculate brand safety score"""        safety_score = 1.0  # Start with perfect safety
        
        # Check for unsafe content
        unsafe_keywords = self.brand_safety_rules['warning_keywords']
        
        for keyword in unsafe_keywords:
            if keyword in text.lower():
                safety_score -= 0.2
        
        # Check sentiment range
        safe_range = self.brand_safety_rules['safe_sentiment_range']
        sentiment = await self._analyze_core_sentiment(text)
        
        if not (safe_range[0] <= sentiment.compound <= safe_range[1]):
            safety_score -= 0.3
        
        # Check for blocked emotions
        blocked_emotions = self.brand_safety_rules['blocked_emotions']
        emotion_scores = await self._extract_emotion_scores(text)
        
        for emotion in blocked_emotions:
            if emotion_scores.get(emotion, 0.0) > 0.5:
                safety_score -= 0.4
        
        return max(0.0, safety_score)
    
    async def _optimize_for_platform(self, text: str, platform: str, sentiment: SentimentScore, emotions: EmotionAnalysis) -> Dict[str, Any]:
        """Generate platform-specific optimization suggestions"""        
        platform_info = self.platform_patterns.get(platform, {})
        optimization = {
            'platform': platform,
            'current_sentiment_fit': 0.0,
            'suggestions': [],
            'optimal_adjustments': [],
            'emoji_recommendations': [],
            'hashtag_suggestions': []
        }
        
        # Check sentiment fit for platform
        typical_range = platform_info.get('typical_sentiment_range', (-1, 1))
        if typical_range[0] <= sentiment.compound <= typical_range[1]:
            optimization['current_sentiment_fit'] = 0.8
        else:
            optimization['current_sentiment_fit'] = 0.3
            optimization['suggestions'].append(
                f"Adjust sentiment to better fit {platform} typical range: {typical_range}"
            )
        
        # Check emotion mix
        optimal_emotions = platform_info.get('optimal_emotion_mix', {})
        current_emotions = emotions.emotion_progression
        
        for emotion, target_ratio in optimal_emotions.items():
            current_ratio = sentiment.emotion_scores.get(emotion, 0.0)
            if current_ratio < target_ratio * 0.7:
                optimization['optimal_adjustments'].append(
                    f"Increase {emotion} emotion (current: {current_ratio:.2f}, optimal: {target_ratio:.2f})"
                )
        
        # Platform-specific emoji recommendations
        if platform == 'instagram':
            optimization['emoji_recommendations'] = ['✨', '💫', '🌟', '💖', '🔥']
        elif platform == 'twitter':
            optimization['emoji_recommendations'] = ['👏', '🙌', '💯', '🔥']
        elif platform == 'linkedin':
            optimization['emoji_recommendations'] = ['💼', '📈', '🎯', '💡']
        
        return optimization
    
    async def _predict_audience_reactions(self, text: str, sentiment: SentimentScore, 
                                        emotions: EmotionAnalysis, target_audience: str) -> Dict[str, float]:
        """Predict how different audience segments will react"""        
        audience_profile = self.audience_profiles.get(target_audience, {})
        
        reactions = {
            'engagement_likelihood': 0.0,
            'positive_response': 0.0,
            'share_likelihood': 0.0,
            'comment_likelihood': 0.0,
            'save_likelihood': 0.0
        }
        
        # Base engagement from sentiment
        reactions['engagement_likelihood'] = min(1.0, abs(sentiment.compound) + 0.3)
        
        # Positive response based on sentiment and audience preferences
        preferred_emotions = audience_profile.get('preferred_emotions', [])
        emotion_match = sum(
            sentiment.emotion_scores.get(emotion, 0.0) 
            for emotion in preferred_emotions
        ) / len(preferred_emotions) if preferred_emotions else 0.5
        
        reactions['positive_response'] = (sentiment.positive + emotion_match) / 2
        
        # Share likelihood based on emotion intensity and virality factors
        if emotions.emotion_intensity > 0.7:
            reactions['share_likelihood'] = 0.8
        elif emotions.emotion_intensity > 0.5:
            reactions['share_likelihood'] = 0.6
        else:
            reactions['share_likelihood'] = 0.3
        
        # Comment likelihood based on questions and controversial content
        if '?' in text:
            reactions['comment_likelihood'] = 0.7
        elif emotions.primary_emotion in ['surprise', 'anger']:
            reactions['comment_likelihood'] = 0.6
        else:
            reactions['comment_likelihood'] = 0.4
        
        # Save likelihood based on value and usefulness
        educational_keywords = ['tip', 'how to', 'guide', 'tutorial', 'learn']
        if any(keyword in text.lower() for keyword in educational_keywords):
            reactions['save_likelihood'] = 0.8
        else:
            reactions['save_likelihood'] = 0.3
        
        return reactions
    
    async def _generate_sentiment_recommendations(self, sentiment: SentimentScore, 
                                                emotions: EmotionAnalysis, 
                                                engagement: EngagementSentiment,
                                                platform: str) -> List[str]:
        """Generate recommendations to improve sentiment and engagement"""        recommendations = []
        
        # Sentiment optimization
        if sentiment.compound < 0.2:
            recommendations.append("Consider adding more positive elements to improve overall sentiment")
        
        if sentiment.confidence < 0.7:
            recommendations.append("Add clearer emotional indicators to improve sentiment clarity")
        
        # Emotion optimization
        if emotions.emotional_complexity < 2:
            recommendations.append("Add more emotional depth with varied emotional expressions")
        
        if emotions.emotion_intensity < 0.5:
            recommendations.append("Increase emotional intensity to boost engagement")
        
        # Engagement optimization
        if engagement.engagement_potential < 0.6:
            recommendations.append("Add questions or calls-to-action to increase engagement")
        
        if engagement.authenticity_score < 0.7:
            recommendations.append("Use more personal language to increase authenticity")
        
        # Brand safety
        if engagement.brand_safety_score < 0.8:
            recommendations.append("Review content for brand safety concerns")
        
        # Platform-specific recommendations
        platform_info = self.platform_patterns.get(platform, {})
        positive_indicators = platform_info.get('positive_indicators', [])
        
        if not any(indicator in sentiment.emotion_scores for indicator in positive_indicators):
            recommendations.append(f"Consider adding {platform}-specific positive indicators")
        
        return recommendations
    
    async def _extract_sentiment_keywords(self, text: str) -> List[str]:
        """Extract keywords that carry sentiment"""        words = text.lower().split()
        sentiment_keywords = []
        
        for word in words:
            # Check if word exists in emotion lexicon
            for emotion_words in self.emotion_lexicon.values():
                if word in emotion_words:
                    sentiment_keywords.append(word)
                    break
        
        # Add emoji sentiment indicators
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
        emojis = re.findall(emoji_pattern, text)
        sentiment_keywords.extend(emojis)
        
        return list(set(sentiment_keywords))  # Remove duplicates
    
    async def _identify_mood_indicators(self, text: str) -> List[str]:
        """Identify indicators of overall mood"""        mood_indicators = []
        
        # Exclamation patterns (excitement/enthusiasm)
        if re.search(r'[!]{2,}', text):
            mood_indicators.append('high_excitement')
        elif '!' in text:
            mood_indicators.append('enthusiasm')
        
        # Question patterns (curiosity/uncertainty)
        if '?' in text:
            mood_indicators.append('curiosity')
        
        # Capitalization patterns (emphasis/shouting)
        if re.search(r'[A-Z]{3,}', text):
            mood_indicators.append('emphasis')
        
        # Ellipsis patterns (hesitation/contemplation)
        if '...' in text:
            mood_indicators.append('contemplation')
        
        # Length patterns
        if len(text) > 300:
            mood_indicators.append('detailed')
        elif len(text) < 50:
            mood_indicators.append('concise')
        
        # Repetition patterns (emphasis)
        words = text.lower().split()
        word_counts = Counter(words)
        repeated_words = [word for word, count in word_counts.items() if count > 2]
        if repeated_words:
            mood_indicators.append('repetitive_emphasis')
        
        return mood_indicators
    
    def _generate_request_id(self, text: str, platform: str) -> str:
        """Generate unique request ID"""        import hashlib
        id_string = f"{text[:100]}{platform}{datetime.utcnow().isoformat()}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]

# Utility functions for quick sentiment analysis
async def quick_sentiment_analysis(text: str, platform: str = "general") -> Dict[str, Any]:
    """Quick sentiment analysis function"""    analyzer = AdvancedSentimentAnalyzer()
    result = await analyzer.analyze_sentiment(text, platform)
    
    return {
        'sentiment': result.sentiment.compound,
        'primary_emotion': result.emotions.primary_emotion,
        'engagement_potential': result.engagement.engagement_potential,
        'brand_safety': result.engagement.brand_safety_score,
        'recommendations': result.content_recommendations[:3]  # Top 3 recommendations
    }

async def sentiment_monitoring(texts: List[str], platform: str = "general") -> Dict[str, Any]:
    """Monitor sentiment across multiple pieces of content"""    analyzer = AdvancedSentimentAnalyzer()
    results = await analyzer.batch_analyze_sentiment(texts, platform)
    
    # Aggregate statistics
    sentiment_scores = [r.sentiment.compound for r in results]
    engagement_scores = [r.engagement.engagement_potential for r in results]
    safety_scores = [r.engagement.brand_safety_score for r in results]
    
    return {
        'total_content_pieces': len(results),
        'average_sentiment': np.mean(sentiment_scores) if sentiment_scores else 0.0,
        'sentiment_range': (min(sentiment_scores), max(sentiment_scores)) if sentiment_scores else (0, 0),
        'average_engagement_potential': np.mean(engagement_scores) if engagement_scores else 0.0,
        'average_brand_safety': np.mean(safety_scores) if safety_scores else 0.0,
        'content_needing_attention': len([s for s in safety_scores if s < 0.7]),
        'high_engagement_content': len([e for e in engagement_scores if e > 0.7]),
        'detailed_results': results
    }
