"""Sentiment Analyzer
==================

Advanced sentiment and emotion analysis system for content understanding.
Implements multi-language sentiment detection and emotional intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from collections import Counter
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class SentimentPolarity(Enum):
    """Sentiment polarity levels."""    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EmotionType(Enum):
    """Emotion types for classification."""    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    EXCITEMENT = "excitement"
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"

class AnalysisLanguage(Enum):
    """Supported languages for sentiment analysis."""    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    AUTO_DETECT = "auto"

@dataclass
class SentimentScore:
    """Sentiment analysis score result."""    polarity: SentimentPolarity
    confidence: float
    polarity_score: float  # -1 (negative) to 1 (positive)
    subjectivity: float   # 0 (objective) to 1 (subjective)
    
    # Detailed scores
    positive_score: float = 0.0
    negative_score: float = 0.0
    neutral_score: float = 0.0
    
    # Context information
    text_length: int = 0
    language: str = "unknown"
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class EmotionDetection:
    """Emotion detection result."""    primary_emotion: EmotionType
    confidence: float
    emotion_scores: Dict[EmotionType, float] = field(default_factory=dict)
    emotional_intensity: float = 0.0
    emotional_stability: float = 0.0
    
    # Advanced metrics
    emotion_complexity: float = 0.0
    mixed_emotions: List[EmotionType] = field(default_factory=list)
    
    # Context
    language: str = "unknown"
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SentimentAnalysisResult:
    """Complete sentiment analysis result."""    content_id: str
    sentiment_score: SentimentScore
    emotion_detection: EmotionDetection
    
    # Advanced insights
    audience_appeal: float = 0.0
    engagement_potential: float = 0.0
    virality_score: float = 0.0
    brand_safety_score: float = 0.0
    
    # Trending analysis
    trending_keywords: List[str] = field(default_factory=list)
    hashtag_sentiment: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    analysis_method: str = "hybrid"
    total_processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

class SentimentAnalyzer:
    """    Advanced sentiment and emotion analysis system.
    
    Features:
    - Multi-language sentiment analysis
    - Deep emotion detection with 10+ emotion types
    - Brand safety and engagement scoring
    - Trending keyword analysis
    - Real-time and batch processing
    - Cultural and contextual awareness
    """    
    def __init__(
        self,
        enable_gpu: bool = True,
        default_language: AnalysisLanguage = AnalysisLanguage.AUTO_DETECT,
        enable_emotion_detection: bool = True,
        enable_trending_analysis: bool = True
    ):
        """        Initialize sentiment analyzer.
        
        Args:
            enable_gpu: Enable GPU acceleration
            default_language: Default language for analysis
            enable_emotion_detection: Enable emotion detection
            enable_trending_analysis: Enable trending keyword analysis
        """        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.default_language = default_language
        self.enable_emotion_detection = enable_emotion_detection
        self.enable_trending_analysis = enable_trending_analysis
        
        # Analysis statistics
        self.analysis_count = 0
        self.processing_times = []
        self.sentiment_distribution = {}
        self.emotion_distribution = {}
        
        # Language-specific models
        self.sentiment_models = {}
        self.emotion_models = {}
        
        # Initialize models
        self._initialize_models()
        self._load_emotion_lexicons()
        
        logger.info(f"SentimentAnalyzer initialized with GPU: {self.enable_gpu}")
    
    def _initialize_models(self) -> None:
        """Initialize sentiment and emotion analysis models."""        try:
            # Multi-language sentiment model
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.enable_gpu else -1
            )
            
            # Emotion detection model
            if self.enable_emotion_detection:
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=0 if self.enable_gpu else -1
                )
            
            # NLTK sentiment analyzer
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.vader_analyzer = SentimentIntensityAnalyzer()
            except:
                self.vader_analyzer = None
            
            # Language-specific models
            self.language_models = {
                "en": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "fr": "tblard/tf-allocine",
                "de": "oliverguhr/german-sentiment-bert",
                "es": "finiteautomata/beto-sentiment-analysis"
            }
            
            logger.info("Sentiment analysis models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize sentiment models: {e}")
            raise
    
    def _load_emotion_lexicons(self) -> None:
        """Load emotion lexicons and keywords."""        self.emotion_keywords = {
            EmotionType.JOY: [
                'happy', 'joy', 'excited', 'delighted', 'cheerful', 'pleased',
                'glad', 'thrilled', 'elated', 'overjoyed', 'blissful', 'ecstatic'
            ],
            EmotionType.SADNESS: [
                'sad', 'depressed', 'melancholy', 'sorrowful', 'dejected',
                'downhearted', 'gloomy', 'morose', 'despondent', 'grief'
            ],
            EmotionType.ANGER: [
                'angry', 'furious', 'rage', 'mad', 'irritated', 'annoyed',
                'frustrated', 'outraged', 'incensed', 'livid', 'enraged'
            ],
            EmotionType.FEAR: [
                'afraid', 'scared', 'terrified', 'frightened', 'anxious',
                'worried', 'nervous', 'panicked', 'alarmed', 'apprehensive'
            ],
            EmotionType.SURPRISE: [
                'surprised', 'amazed', 'astonished', 'shocked', 'stunned',
                'bewildered', 'astounded', 'flabbergasted', 'dumbfounded'
            ],
            EmotionType.DISGUST: [
                'disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated',
                'appalled', 'horrified', 'grossed', 'offended'
            ],
            EmotionType.LOVE: [
                'love', 'adore', 'cherish', 'affection', 'devoted', 'fond',
                'passionate', 'romantic', 'caring', 'tender', 'heartfelt'
            ],
            EmotionType.EXCITEMENT: [
                'excited', 'thrilled', 'pumped', 'energetic', 'enthusiastic',
                'eager', 'animated', 'exhilarated', 'invigorated'
            ]
        }
        
        # Sentiment modifiers
        self.sentiment_intensifiers = [
            'very', 'extremely', 'really', 'absolutely', 'completely',
            'totally', 'incredibly', 'amazingly', 'exceptionally'
        ]
        
        self.sentiment_diminishers = [
            'slightly', 'somewhat', 'rather', 'fairly', 'quite',
            'relatively', 'moderately', 'little', 'bit'
        ]
        
        self.negation_words = [
            'not', 'no', 'never', 'none', 'nothing', 'nowhere',
            'neither', 'nobody', 'cannot', "can't", "won't", "don't"
        ]
    
    async def analyze_sentiment(
        self,
        content_id: str,
        text_content: str,
        language: Optional[AnalysisLanguage] = None,
        include_emotions: bool = True
    ) -> SentimentAnalysisResult:
        """        Analyze sentiment and emotions in text content.
        
        Args:
            content_id: Unique content identifier
            text_content: Text to analyze
            language: Language for analysis
            include_emotions: Include emotion detection
            
        Returns:
            SentimentAnalysisResult: Complete sentiment analysis
        """        start_time = datetime.now()
        
        try:
            # Detect language if not specified
            detected_lang = language or self._detect_language(text_content)
            
            # Preprocess text
            processed_text = self._preprocess_text(text_content)
            
            # Sentiment analysis
            sentiment_score = await self._analyze_sentiment_score(processed_text, detected_lang)
            
            # Emotion detection
            emotion_detection = None
            if include_emotions and self.enable_emotion_detection:
                emotion_detection = await self._detect_emotions(processed_text, detected_lang)
            else:
                emotion_detection = EmotionDetection(
                    primary_emotion=EmotionType.JOY,
                    confidence=0.0
                )
            
            # Advanced analysis
            audience_appeal = self._calculate_audience_appeal(sentiment_score, emotion_detection)
            engagement_potential = self._calculate_engagement_potential(text_content, sentiment_score)
            virality_score = self._calculate_virality_score(text_content, sentiment_score, emotion_detection)
            brand_safety_score = self._calculate_brand_safety(text_content, sentiment_score)
            
            # Trending analysis
            trending_keywords = []
            hashtag_sentiment = {}
            if self.enable_trending_analysis:
                trending_keywords = self._extract_trending_keywords(text_content)
                hashtag_sentiment = self._analyze_hashtag_sentiment(text_content)
            
            # Calculate total processing time
            total_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(total_time)
            
            # Create result
            result = SentimentAnalysisResult(
                content_id=content_id,
                sentiment_score=sentiment_score,
                emotion_detection=emotion_detection,
                audience_appeal=audience_appeal,
                engagement_potential=engagement_potential,
                virality_score=virality_score,
                brand_safety_score=brand_safety_score,
                trending_keywords=trending_keywords,
                hashtag_sentiment=hashtag_sentiment,
                analysis_method="hybrid_ml",
                total_processing_time=total_time
            )
            
            # Update statistics
            self.analysis_count += 1
            polarity = sentiment_score.polarity.value
            self.sentiment_distribution[polarity] = self.sentiment_distribution.get(polarity, 0) + 1
            
            if emotion_detection:
                emotion = emotion_detection.primary_emotion.value
                self.emotion_distribution[emotion] = self.emotion_distribution.get(emotion, 0) + 1
            
            logger.info(f"Sentiment analyzed for {content_id}: {sentiment_score.polarity.value}")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {content_id}: {e}")
            
            # Return minimal result
            return SentimentAnalysisResult(
                content_id=content_id,
                sentiment_score=SentimentScore(
                    polarity=SentimentPolarity.NEUTRAL,
                    confidence=0.0,
                    polarity_score=0.0,
                    subjectivity=0.0
                ),
                emotion_detection=EmotionDetection(
                    primary_emotion=EmotionType.JOY,
                    confidence=0.0
                ),
                total_processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _analyze_sentiment_score(
        self,
        text: str,
        language: AnalysisLanguage
    ) -> SentimentScore:
        """Analyze sentiment score using multiple models."""        start_time = datetime.now()
        
        try:
            scores = []
            
            # Transformer-based sentiment
            try:
                transformer_result = self.sentiment_pipeline(text)
                if transformer_result:
                    label = transformer_result[0]['label'].lower()
                    score = transformer_result[0]['score']
                    
                    if 'positive' in label:
                        polarity_score = score
                    elif 'negative' in label:
                        polarity_score = -score
                    else:
                        polarity_score = 0.0
                    
                    scores.append(polarity_score)
            except Exception as e:
                logger.debug(f"Transformer sentiment failed: {e}")
            
            # VADER sentiment
            if self.vader_analyzer:
                try:
                    vader_scores = self.vader_analyzer.polarity_scores(text)
                    scores.append(vader_scores['compound'])
                except Exception as e:
                    logger.debug(f"VADER sentiment failed: {e}")
            
            # TextBlob sentiment
            try:
                blob = TextBlob(text)
                scores.append(blob.sentiment.polarity)
                subjectivity = blob.sentiment.subjectivity
            except Exception as e:
                logger.debug(f"TextBlob sentiment failed: {e}")
                subjectivity = 0.5
            
            # Rule-based sentiment
            rule_score = self._rule_based_sentiment(text)
            scores.append(rule_score)
            
            # Combine scores
            if scores:
                polarity_score = np.mean(scores)
                confidence = 1.0 - np.std(scores)  # Higher confidence when models agree
            else:
                polarity_score = 0.0
                confidence = 0.0
            
            # Determine polarity
            if polarity_score > 0.5:
                polarity = SentimentPolarity.VERY_POSITIVE
            elif polarity_score > 0.1:
                polarity = SentimentPolarity.POSITIVE
            elif polarity_score > -0.1:
                polarity = SentimentPolarity.NEUTRAL
            elif polarity_score > -0.5:
                polarity = SentimentPolarity.NEGATIVE
            else:
                polarity = SentimentPolarity.VERY_NEGATIVE
            
            # Calculate detailed scores
            positive_score = max(0, polarity_score)
            negative_score = max(0, -polarity_score)
            neutral_score = 1.0 - abs(polarity_score)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return SentimentScore(
                polarity=polarity,
                confidence=confidence,
                polarity_score=polarity_score,
                subjectivity=subjectivity,
                positive_score=positive_score,
                negative_score=negative_score,
                neutral_score=neutral_score,
                text_length=len(text),
                language=language.value if isinstance(language, AnalysisLanguage) else str(language),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Sentiment score analysis failed: {e}")
            return SentimentScore(
                polarity=SentimentPolarity.NEUTRAL,
                confidence=0.0,
                polarity_score=0.0,
                subjectivity=0.5,
                text_length=len(text),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _detect_emotions(
        self,
        text: str,
        language: AnalysisLanguage
    ) -> EmotionDetection:
        """Detect emotions in text using ML and rule-based approaches."""        start_time = datetime.now()
        
        try:
            emotion_scores = {}
            
            # ML-based emotion detection
            if self.emotion_pipeline:
                try:
                    ml_result = self.emotion_pipeline(text)
                    for result in ml_result:
                        emotion_label = result['label'].lower()
                        emotion_score = result['score']
                        
                        # Map to our emotion types
                        emotion_type = self._map_emotion_label(emotion_label)
                        if emotion_type:
                            emotion_scores[emotion_type] = emotion_score
                except Exception as e:
                    logger.debug(f"ML emotion detection failed: {e}")
            
            # Rule-based emotion detection
            rule_emotions = self._rule_based_emotion_detection(text)
            for emotion, score in rule_emotions.items():
                emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score * 0.3
            
            # Normalize scores
            if emotion_scores:
                max_score = max(emotion_scores.values())
                if max_score > 0:
                    emotion_scores = {k: v / max_score for k, v in emotion_scores.items()}
            
            # Determine primary emotion
            if emotion_scores:
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = emotion_scores[primary_emotion]
            else:
                primary_emotion = EmotionType.JOY
                confidence = 0.0
                emotion_scores = {EmotionType.JOY: 0.0}
            
            # Calculate advanced metrics
            emotional_intensity = self._calculate_emotional_intensity(text, emotion_scores)
            emotional_stability = self._calculate_emotional_stability(emotion_scores)
            emotion_complexity = self._calculate_emotion_complexity(emotion_scores)
            mixed_emotions = self._identify_mixed_emotions(emotion_scores)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmotionDetection(
                primary_emotion=primary_emotion,
                confidence=confidence,
                emotion_scores=emotion_scores,
                emotional_intensity=emotional_intensity,
                emotional_stability=emotional_stability,
                emotion_complexity=emotion_complexity,
                mixed_emotions=mixed_emotions,
                language=language.value if isinstance(language, AnalysisLanguage) else str(language),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return EmotionDetection(
                primary_emotion=EmotionType.JOY,
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle emojis (preserve them as they carry sentiment)
        # For now, keep them as-is
        
        # Handle URLs
        text = re.sub(r'http\S+|www\S+', ' [URL] ', text)
        
        # Handle mentions and hashtags (preserve for analysis)
        # text = re.sub(r'@\w+', ' [MENTION] ', text)
        # text = re.sub(r'#\w+', ' [HASHTAG] ', text)
        
        return text.strip()
    
    def _detect_language(self, text: str) -> AnalysisLanguage:
        """Detect language of text content."""        # Simplified language detection
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        french_words = {'le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec'}
        german_words = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'zu', 'für', 'von', 'mit'}
        
        words = set(text.lower().split())
        
        en_score = len(words & english_words)
        fr_score = len(words & french_words)
        de_score = len(words & german_words)
        
        if en_score >= fr_score and en_score >= de_score:
            return AnalysisLanguage.ENGLISH
        elif fr_score >= de_score:
            return AnalysisLanguage.FRENCH
        else:
            return AnalysisLanguage.GERMAN
    
    def _rule_based_sentiment(self, text: str) -> float:
        """Calculate sentiment using rule-based approach."""        words = text.lower().split()
        
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'brilliant', 'perfect', 'love', 'like', 'enjoy',
            'happy', 'pleased', 'satisfied', 'delighted', 'thrilled'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
            'dislike', 'disappointed', 'frustrated', 'angry', 'sad',
            'upset', 'annoyed', 'boring', 'worst', 'fail', 'sucks'
        }
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Check for intensifiers and diminishers
        intensifier_count = sum(1 for word in words if word in self.sentiment_intensifiers)
        diminisher_count = sum(1 for word in words if word in self.sentiment_diminishers)
        
        # Check for negations
        negation_count = sum(1 for word in words if word in self.negation_words)
        
        # Calculate base sentiment
        if positive_count + negative_count == 0:
            sentiment = 0.0
        else:
            sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        
        # Apply modifiers
        intensity_modifier = 1.0 + (intensifier_count * 0.2) - (diminisher_count * 0.2)
        sentiment *= intensity_modifier
        
        # Apply negation (flip sentiment if odd number of negations)
        if negation_count % 2 == 1:
            sentiment *= -0.5
        
        return np.clip(sentiment, -1.0, 1.0)
    
    def _map_emotion_label(self, label: str) -> Optional[EmotionType]:
        """Map emotion labels from ML models to our emotion types."""        label_mapping = {
            'joy': EmotionType.JOY,
            'happiness': EmotionType.JOY,
            'sadness': EmotionType.SADNESS,
            'anger': EmotionType.ANGER,
            'fear': EmotionType.FEAR,
            'surprise': EmotionType.SURPRISE,
            'disgust': EmotionType.DISGUST,
            'love': EmotionType.LOVE,
            'excitement': EmotionType.EXCITEMENT
        }
        
        return label_mapping.get(label.lower())
    
    def _rule_based_emotion_detection(self, text: str) -> Dict[EmotionType, float]:
        """Detect emotions using rule-based keyword matching."""        words = set(text.lower().split())
        emotion_scores = {}
        
        for emotion_type, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in words)
            if score > 0:
                emotion_scores[emotion_type] = score / len(keywords)
        
        return emotion_scores
    
    def _calculate_emotional_intensity(self, text: str, emotion_scores: Dict[EmotionType, float]) -> float:
        """Calculate overall emotional intensity."""        # Consider exclamation marks, capital letters, repeated characters
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        
        # Repeated characters (like "sooooo")
        repeated_chars = len(re.findall(r'(.)\1{2,}', text.lower()))
        
        # Emotion score intensity
        max_emotion_score = max(emotion_scores.values()) if emotion_scores else 0
        
        intensity_factors = [
            min(1.0, exclamation_count * 0.2),
            min(1.0, question_count * 0.1),
            min(1.0, caps_ratio * 2.0),
            min(1.0, repeated_chars * 0.1),
            max_emotion_score
        ]
        
        return np.mean(intensity_factors)
    
    def _calculate_emotional_stability(self, emotion_scores: Dict[EmotionType, float]) -> float:
        """Calculate emotional stability (consistency of emotions)."""        if not emotion_scores:
            return 1.0
        
        scores = list(emotion_scores.values())
        variance = np.var(scores)
        
        # Lower variance = higher stability
        return max(0.0, 1.0 - variance)
    
    def _calculate_emotion_complexity(self, emotion_scores: Dict[EmotionType, float]) -> float:
        """Calculate emotion complexity (number of significant emotions)."""        significant_emotions = sum(1 for score in emotion_scores.values() if score > 0.3)
        
        # Normalize to 0-1 scale
        return min(1.0, significant_emotions / len(EmotionType))
    
    def _identify_mixed_emotions(
        self,
        emotion_scores: Dict[EmotionType, float],
        threshold: float = 0.4
    ) -> List[EmotionType]:
        """Identify mixed emotions above threshold."""        return [emotion for emotion, score in emotion_scores.items() if score >= threshold]
    
    def _calculate_audience_appeal(
        self,
        sentiment: SentimentScore,
        emotion: EmotionDetection
    ) -> float:
        """Calculate audience appeal score."""        factors = []
        
        # Positive sentiment generally has higher appeal
        if sentiment.polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
            factors.append(0.8)
        elif sentiment.polarity == SentimentPolarity.NEUTRAL:
            factors.append(0.6)
        else:
            factors.append(0.4)
        
        # Certain emotions have higher appeal
        appealing_emotions = [EmotionType.JOY, EmotionType.EXCITEMENT, EmotionType.LOVE, EmotionType.SURPRISE]
        if emotion.primary_emotion in appealing_emotions:
            factors.append(0.9)
        else:
            factors.append(0.6)
        
        # Emotional intensity can increase appeal
        factors.append(emotion.emotional_intensity)
        
        # Confidence factor
        factors.append((sentiment.confidence + emotion.confidence) / 2)
        
        return np.mean(factors)
    
    def _calculate_engagement_potential(self, text: str, sentiment: SentimentScore) -> float:
        """Calculate engagement potential based on content characteristics."""        factors = []
        
        # Text length factor
        text_length = len(text.split())
        if 10 <= text_length <= 100:
            factors.append(0.9)  # Optimal length
        elif text_length < 10:
            factors.append(0.6)  # Too short
        else:
            factors.append(0.7)  # Might be too long
        
        # Sentiment extremes often generate more engagement
        if abs(sentiment.polarity_score) > 0.5:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Questions increase engagement
        question_count = text.count('?')
        factors.append(min(1.0, question_count * 0.3))
        
        # Hashtags and mentions
        hashtag_count = len(re.findall(r'#\w+', text))
        mention_count = len(re.findall(r'@\w+', text))
        social_factor = min(1.0, (hashtag_count + mention_count) * 0.2)
        factors.append(social_factor)
        
        return np.mean(factors)
    
    def _calculate_virality_score(
        self,
        text: str,
        sentiment: SentimentScore,
        emotion: EmotionDetection
    ) -> float:
        """Calculate virality potential score."""        factors = []
        
        # Extreme emotions tend to go viral
        viral_emotions = [EmotionType.ANGER, EmotionType.EXCITEMENT, EmotionType.SURPRISE, EmotionType.JOY]
        if emotion.primary_emotion in viral_emotions:
            factors.append(0.8)
        else:
            factors.append(0.5)
        
        # High emotional intensity
        factors.append(emotion.emotional_intensity)
        
        # Controversial content (mixed emotions)
        if len(emotion.mixed_emotions) > 2:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Strong sentiment (positive or negative)
        if abs(sentiment.polarity_score) > 0.6:
            factors.append(0.8)
        else:
            factors.append(0.4)
        
        # Call-to-action words
        cta_words = ['share', 'retweet', 'like', 'comment', 'tag', 'follow', 'subscribe']
        cta_count = sum(1 for word in cta_words if word in text.lower())
        factors.append(min(1.0, cta_count * 0.3))
        
        return np.mean(factors)
    
    def _calculate_brand_safety(self, text: str, sentiment: SentimentScore) -> float:
        """Calculate brand safety score."""        safety_factors = []
        
        # Positive sentiment is generally brand-safe
        if sentiment.polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
            safety_factors.append(0.9)
        elif sentiment.polarity == SentimentPolarity.NEUTRAL:
            safety_factors.append(0.8)
        else:
            safety_factors.append(0.4)
        
        # Check for unsafe keywords
        unsafe_keywords = [
            'hate', 'violence', 'drugs', 'alcohol', 'gambling', 'adult',
            'controversial', 'political', 'religion', 'death', 'war'
        ]
        
        unsafe_count = sum(1 for keyword in unsafe_keywords if keyword in text.lower())
        safety_factor = max(0.1, 1.0 - unsafe_count * 0.2)
        safety_factors.append(safety_factor)
        
        # Profanity check (simplified)
        profanity_words = ['damn', 'hell', 'crap']  # Add more as needed
        profanity_count = sum(1 for word in profanity_words if word in text.lower())
        profanity_factor = max(0.2, 1.0 - profanity_count * 0.3)
        safety_factors.append(profanity_factor)
        
        return np.mean(safety_factors)
    
    def _extract_trending_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract potentially trending keywords."""        # Remove stop words and extract meaningful keywords
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        # Return most frequent words
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _analyze_hashtag_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of individual hashtags."""        hashtags = re.findall(r'#(\w+)', text.lower())
        hashtag_sentiment = {}
        
        for hashtag in hashtags:
            # Simple sentiment analysis for hashtag
            hashtag_sentiment[f"#{hashtag}"] = self._rule_based_sentiment(hashtag)
        
        return hashtag_sentiment
    
    async def batch_analyze(
        self,
        content_batch: List[Tuple[str, str, Optional[AnalysisLanguage]]]
    ) -> List[SentimentAnalysisResult]:
        """Analyze sentiment for multiple content items in batch."""        tasks = []
        
        for content_id, text_content, language in content_batch:
            task = asyncio.create_task(
                self.analyze_sentiment(content_id, text_content, language)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = [r for r in results if isinstance(r, SentimentAnalysisResult)]
        
        logger.info(f"Batch analyzed sentiment for {len(valid_results)} out of {len(content_batch)} items")
        return valid_results
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get sentiment analysis analytics and performance metrics."""        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "total_analyses": self.analysis_count,
            "average_processing_time": avg_processing_time,
            "sentiment_distribution": self.sentiment_distribution,
            "emotion_distribution": self.emotion_distribution,
            "gpu_enabled": self.enable_gpu,
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""        # Clear statistics
        self.processing_times.clear()
        self.sentiment_distribution.clear()
        self.emotion_distribution.clear()
        
        # Clear GPU memory if using CUDA
        if self.enable_gpu and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("SentimentAnalyzer cleanup completed")
