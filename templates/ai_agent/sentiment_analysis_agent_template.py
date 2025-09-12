"""{{agent_name}} Sentiment Analysis Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import re

import torch
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, RobertaTokenizer, RobertaForSequenceClassification
)
from textblob import TextBlob
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import SentimentModelManager
from nlp.preprocessing import TextPreprocessor, LanguageDetector
from nlp.emotion_detection import EmotionClassifier
from nlp.aspect_sentiment import AspectBasedSentimentAnalyzer
from core.config import get_settings
from utils.exceptions import SentimentException
from monitoring.sentiment_metrics import SentimentMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class SentimentPolarity(Enum):
    """Sentiment polarity levels"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class EmotionType(Enum):
    """Emotion types"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    EXCITEMENT = "excitement"
    ANXIETY = "anxiety"
    TRUST = "trust"


class SentimentAnalysisType(Enum):
    """Types of sentiment analysis"""
    DOCUMENT_LEVEL = "document_level"
    SENTENCE_LEVEL = "sentence_level"
    ASPECT_BASED = "aspect_based"
    EMOTION_DETECTION = "emotion_detection"
    MULTI_LABEL = "multi_label"
    COMPARATIVE = "comparative"
    TEMPORAL = "temporal"


class SentimentRequest(BaseModel):
    """Sentiment analysis request model"""
    text: Union[str, List[str]]
    analysis_type: SentimentAnalysisType = SentimentAnalysisType.DOCUMENT_LEVEL
    language: Optional[str] = None
    aspects: Optional[List[str]] = None
    include_emotions: bool = True
    include_confidence: bool = True
    include_explanations: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('text')
    def validate_text(cls, v):
        if isinstance(v, str):
            if len(v.strip()) == 0:
                raise ValueError('Text cannot be empty')
            if len(v) > 10000:
                raise ValueError('Text too long (max 10,000 characters)')
        elif isinstance(v, list):
            if len(v) == 0:
                raise ValueError('Text list cannot be empty')
            for text in v:
                if len(text.strip()) == 0:
                    raise ValueError('Text items cannot be empty')
        return v


class SentimentScore(BaseModel):
    """Sentiment score model"""
    polarity: SentimentPolarity
    confidence: float = Field(ge=0.0, le=1.0)
    positive_score: float = Field(ge=0.0, le=1.0)
    negative_score: float = Field(ge=0.0, le=1.0)
    neutral_score: float = Field(ge=0.0, le=1.0)
    compound_score: float = Field(ge=-1.0, le=1.0)


class EmotionScore(BaseModel):
    """Emotion score model"""
    emotion: EmotionType
    confidence: float = Field(ge=0.0, le=1.0)
    intensity: float = Field(ge=0.0, le=1.0)


class AspectSentiment(BaseModel):
    """Aspect-based sentiment model"""
    aspect: str
    sentiment: SentimentScore
    context: str
    span: Tuple[int, int]


class SentimentResult(BaseModel):
    """Sentiment analysis result model"""
    text: str
    sentiment: SentimentScore
    emotions: List[EmotionScore] = Field(default_factory=list)
    aspects: List[AspectSentiment] = Field(default_factory=list)
    language: Optional[str] = None
    analysis_time: float
    explanations: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SentimentConfig(BaseModel):
    """Sentiment analysis configuration"""
    primary_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    aspect_model: str = "yangheng/deberta-v3-base-absa-v1.1"
    language_detection: bool = True
    multi_model_ensemble: bool = True
    enable_preprocessing: bool = True
    cache_results: bool = True
    confidence_threshold: float = 0.5
    max_batch_size: int = 32


class {{agent_class_name}}(BaseAIAgent):
    """
    Advanced sentiment analysis agent for Ainflue platform.
    
    Features:
    - Multi-level sentiment analysis (document, sentence, aspect)
    - Emotion detection and classification
    - Multi-language support
    - Real-time and batch processing
    - Confidence scoring and explanations
    - Temporal sentiment tracking
    - Social media optimization
    - Performance monitoring
    """
    
    def __init__(
        self,
        name: str = "{{agent_name}}",
        config: Optional[SentimentConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or SentimentConfig()
        
        # Initialize components
        self.model_manager = SentimentModelManager()
        self.text_preprocessor = TextPreprocessor()
        self.language_detector = LanguageDetector()
        self.emotion_classifier = EmotionClassifier()
        self.aspect_analyzer = AspectBasedSentimentAnalyzer()
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize metrics collector
        self.metrics = SentimentMetricsCollector()
        
        # Load models and NLP tools
        self._load_models()
        self._load_nlp_tools()
        
        logger.info(f"Sentiment analysis agent '{name}' initialized successfully")

    def _load_models(self) -> None:
        """Load and initialize sentiment analysis models"""
        try:
            # Load primary sentiment model
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                self.config.primary_model
            )
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                self.config.primary_model
            )
            
            # Load emotion detection model
            self.emotion_tokenizer = AutoTokenizer.from_pretrained(
                self.config.emotion_model
            )
            self.emotion_model = AutoModelForSequenceClassification.from_pretrained(
                self.config.emotion_model
            )
            
            # Initialize pipelines
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.config.primary_model,
                device=0 if torch.cuda.is_available() else -1,
                return_all_scores=True
            )
            
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=self.config.emotion_model,
                device=0 if torch.cuda.is_available() else -1,
                return_all_scores=True
            )
            
            # Load additional models for ensemble
            if self.config.multi_model_ensemble:
                self.ensemble_pipelines = [
                    pipeline(
                        "sentiment-analysis",
                        model="nlptown/bert-base-multilingual-uncased-sentiment",
                        device=0 if torch.cuda.is_available() else -1
                    ),
                    pipeline(
                        "sentiment-analysis", 
                        model="distilbert-base-uncased-finetuned-sst-2-english",
                        device=0 if torch.cuda.is_available() else -1
                    )
                ]
            
            logger.info("All sentiment models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading sentiment models: {str(e)}")
            raise SentimentException(f"Model loading failed: {str(e)}")

    def _load_nlp_tools(self) -> None:
        """Load NLP tools for preprocessing"""
        try:
            # Load spaCy model for advanced NLP processing
            self.nlp = spacy.load("en_core_web_sm")
            
            logger.info("NLP tools loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}")
            self.nlp = None

    async def analyze_sentiment(
        self,
        request: SentimentRequest
    ) -> Union[SentimentResult, List[SentimentResult]]:
        """
        Analyze sentiment of text or list of texts.
        
        Args:
            request: Sentiment analysis request
            
        Returns:
            SentimentResult or list of results
        """
        start_time = datetime.utcnow()
        
        try:
            if isinstance(request.text, str):
                result = await self._analyze_single_text(request, start_time)
                return result
            else:
                results = await self._analyze_batch_text(request, start_time)
                return results
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            raise SentimentException(f"Analysis failed: {str(e)}")

    async def _analyze_single_text(
        self,
        request: SentimentRequest,
        start_time: datetime
    ) -> SentimentResult:
        """Analyze sentiment for single text"""
        text = request.text
        
        # Detect language if needed
        language = None
        if self.config.language_detection:
            language = await self._detect_language(text)
        
        # Preprocess text
        if self.config.enable_preprocessing:
            processed_text = await self._preprocess_text(text, language)
        else:
            processed_text = text
        
        # Perform sentiment analysis based on type
        if request.analysis_type == SentimentAnalysisType.DOCUMENT_LEVEL:
            sentiment = await self._analyze_document_sentiment(processed_text)
        elif request.analysis_type == SentimentAnalysisType.SENTENCE_LEVEL:
            sentiment = await self._analyze_sentence_sentiment(processed_text)
        elif request.analysis_type == SentimentAnalysisType.ASPECT_BASED:
            sentiment = await self._analyze_aspect_sentiment(
                processed_text, request.aspects or []
            )
        else:
            sentiment = await self._analyze_document_sentiment(processed_text)
        
        # Detect emotions if requested
        emotions = []
        if request.include_emotions:
            emotions = await self._detect_emotions(processed_text)
        
        # Analyze aspects if specified
        aspects = []
        if request.analysis_type == SentimentAnalysisType.ASPECT_BASED and request.aspects:
            aspects = await self._analyze_aspects(processed_text, request.aspects)
        
        # Generate explanations if requested
        explanations = None
        if request.include_explanations:
            explanations = await self._generate_explanations(
                processed_text, sentiment, emotions
            )
        
        # Calculate analysis time
        analysis_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create result
        result = SentimentResult(
            text=text,
            sentiment=sentiment,
            emotions=emotions,
            aspects=aspects,
            language=language,
            analysis_time=analysis_time,
            explanations=explanations,
            metadata={
                "processed_text": processed_text,
                "analysis_type": request.analysis_type.value,
                "model_used": self.config.primary_model
            }
        )
        
        # Record metrics
        await self.metrics.record_analysis(request, result)
        
        return result

    async def _analyze_batch_text(
        self,
        request: SentimentRequest,
        start_time: datetime
    ) -> List[SentimentResult]:
        """Analyze sentiment for batch of texts"""
        texts = request.text
        results = []
        
        # Process in batches
        batch_size = min(self.config.max_batch_size, len(texts))
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Create individual requests
            batch_requests = [
                SentimentRequest(
                    text=text,
                    analysis_type=request.analysis_type,
                    language=request.language,
                    aspects=request.aspects,
                    include_emotions=request.include_emotions,
                    include_confidence=request.include_confidence,
                    include_explanations=request.include_explanations
                )
                for text in batch
            ]
            
            # Process batch
            batch_results = await asyncio.gather(*[
                self._analyze_single_text(req, start_time)
                for req in batch_requests
            ])
            
            results.extend(batch_results)
        
        return results

    async def _analyze_document_sentiment(self, text: str) -> SentimentScore:
        """Analyze document-level sentiment"""
        try:
            # Use primary model
            primary_result = self.sentiment_pipeline(text)
            
            # Use VADER for additional insights
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Ensemble if enabled
            if self.config.multi_model_ensemble:
                ensemble_results = []
                for pipeline in self.ensemble_pipelines:
                    try:
                        result = pipeline(text)
                        ensemble_results.append(result)
                    except Exception:
                        continue
                
                # Combine results
                sentiment_score = self._combine_sentiment_scores(
                    primary_result, vader_scores, ensemble_results
                )
            else:
                sentiment_score = self._convert_to_sentiment_score(
                    primary_result, vader_scores
                )
            
            return sentiment_score
            
        except Exception as e:
            logger.error(f"Document sentiment analysis failed: {str(e)}")
            raise SentimentException(f"Document analysis failed: {str(e)}")

    async def _analyze_sentence_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentence-level sentiment"""
        try:
            if self.nlp:
                # Use spaCy for sentence segmentation
                doc = self.nlp(text)
                sentences = [sent.text.strip() for sent in doc.sents]
            else:
                # Fallback: simple sentence splitting
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if s.strip()]
            
            # Analyze each sentence
            sentence_sentiments = []
            for sentence in sentences:
                if len(sentence) > 10:  # Skip very short sentences
                    sent_result = self.sentiment_pipeline(sentence)
                    sentence_sentiments.append(sent_result)
            
            # Aggregate sentence sentiments
            if sentence_sentiments:
                aggregated_sentiment = self._aggregate_sentence_sentiments(
                    sentence_sentiments
                )
            else:
                # Fallback to document-level analysis
                aggregated_sentiment = await self._analyze_document_sentiment(text)
            
            return aggregated_sentiment
            
        except Exception as e:
            logger.error(f"Sentence sentiment analysis failed: {str(e)}")
            raise SentimentException(f"Sentence analysis failed: {str(e)}")

    async def _detect_emotions(self, text: str) -> List[EmotionScore]:
        """Detect emotions in text"""
        try:
            emotion_results = self.emotion_pipeline(text)
            
            emotions = []
            for emotion_data in emotion_results:
                if emotion_data['score'] >= self.config.confidence_threshold:
                    # Map emotion labels to EmotionType
                    emotion_type = self._map_emotion_label(emotion_data['label'])
                    if emotion_type:
                        emotion_score = EmotionScore(
                            emotion=emotion_type,
                            confidence=emotion_data['score'],
                            intensity=emotion_data['score']  # Using confidence as intensity
                        )
                        emotions.append(emotion_score)
            
            # Sort by confidence
            emotions.sort(key=lambda x: x.confidence, reverse=True)
            
            return emotions[:5]  # Return top 5 emotions
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {str(e)}")
            return []

    async def _analyze_aspects(
        self,
        text: str,
        aspects: List[str]
    ) -> List[AspectSentiment]:
        """Analyze sentiment for specific aspects"""
        try:
            aspect_sentiments = []
            
            for aspect in aspects:
                # Find aspect mentions in text
                aspect_mentions = self._find_aspect_mentions(text, aspect)
                
                for mention, span, context in aspect_mentions:
                    # Analyze sentiment for the context
                    context_sentiment = await self._analyze_document_sentiment(context)
                    
                    aspect_sentiment = AspectSentiment(
                        aspect=aspect,
                        sentiment=context_sentiment,
                        context=context,
                        span=span
                    )
                    aspect_sentiments.append(aspect_sentiment)
            
            return aspect_sentiments
            
        except Exception as e:
            logger.error(f"Aspect sentiment analysis failed: {str(e)}")
            return []

    def _find_aspect_mentions(
        self,
        text: str,
        aspect: str
    ) -> List[Tuple[str, Tuple[int, int], str]]:
        """Find mentions of an aspect in text"""
        mentions = []
        
        # Simple keyword matching (can be enhanced with NER)
        aspect_lower = aspect.lower()
        text_lower = text.lower()
        
        start = 0
        while True:
            pos = text_lower.find(aspect_lower, start)
            if pos == -1:
                break
            
            # Extract context around the mention
            context_start = max(0, pos - 50)
            context_end = min(len(text), pos + len(aspect) + 50)
            context = text[context_start:context_end]
            
            mention = text[pos:pos + len(aspect)]
            span = (pos, pos + len(aspect))
            
            mentions.append((mention, span, context))
            start = pos + 1
        
        return mentions

    async def _detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        try:
            return self.language_detector.detect(text)
        except Exception:
            return None

    async def _preprocess_text(self, text: str, language: Optional[str]) -> str:
        """Preprocess text for analysis"""
        try:
            return self.text_preprocessor.preprocess(text, language)
        except Exception:
            return text

    def _convert_to_sentiment_score(
        self,
        primary_result: List[Dict],
        vader_scores: Dict[str, float]
    ) -> SentimentScore:
        """Convert model outputs to SentimentScore"""
        # Extract scores from primary model
        scores = {item['label'].lower(): item['score'] for item in primary_result}
        
        # Map to our polarity system
        positive_score = scores.get('positive', scores.get('pos', 0.0))
        negative_score = scores.get('negative', scores.get('neg', 0.0))
        neutral_score = scores.get('neutral', 1.0 - positive_score - negative_score)
        
        # Determine polarity
        if positive_score > negative_score and positive_score > neutral_score:
            if positive_score > 0.8:
                polarity = SentimentPolarity.VERY_POSITIVE
            else:
                polarity = SentimentPolarity.POSITIVE
        elif negative_score > positive_score and negative_score > neutral_score:
            if negative_score > 0.8:
                polarity = SentimentPolarity.VERY_NEGATIVE
            else:
                polarity = SentimentPolarity.NEGATIVE
        else:
            polarity = SentimentPolarity.NEUTRAL
        
        # Confidence is the highest score
        confidence = max(positive_score, negative_score, neutral_score)
        
        return SentimentScore(
            polarity=polarity,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score,
            compound_score=vader_scores.get('compound', 0.0)
        )

    def _combine_sentiment_scores(
        self,
        primary_result: List[Dict],
        vader_scores: Dict[str, float],
        ensemble_results: List[List[Dict]]
    ) -> SentimentScore:
        """Combine multiple sentiment analysis results"""
        # Start with primary result
        primary_score = self._convert_to_sentiment_score(primary_result, vader_scores)
        
        if not ensemble_results:
            return primary_score
        
        # Aggregate ensemble scores
        total_positive = primary_score.positive_score
        total_negative = primary_score.negative_score
        total_neutral = primary_score.neutral_score
        count = 1
        
        for ensemble_result in ensemble_results:
            scores = {item['label'].lower(): item['score'] for item in ensemble_result}
            total_positive += scores.get('positive', scores.get('pos', 0.0))
            total_negative += scores.get('negative', scores.get('neg', 0.0))
            total_neutral += scores.get('neutral', 1.0 - total_positive - total_negative)
            count += 1
        
        # Average the scores
        avg_positive = total_positive / count
        avg_negative = total_negative / count
        avg_neutral = total_neutral / count
        
        # Determine final polarity
        if avg_positive > avg_negative and avg_positive > avg_neutral:
            if avg_positive > 0.8:
                polarity = SentimentPolarity.VERY_POSITIVE
            else:
                polarity = SentimentPolarity.POSITIVE
        elif avg_negative > avg_positive and avg_negative > avg_neutral:
            if avg_negative > 0.8:
                polarity = SentimentPolarity.VERY_NEGATIVE
            else:
                polarity = SentimentPolarity.NEGATIVE
        else:
            polarity = SentimentPolarity.NEUTRAL
        
        confidence = max(avg_positive, avg_negative, avg_neutral)
        
        return SentimentScore(
            polarity=polarity,
            confidence=confidence,
            positive_score=avg_positive,
            negative_score=avg_negative,
            neutral_score=avg_neutral,
            compound_score=vader_scores.get('compound', 0.0)
        )

    def _aggregate_sentence_sentiments(
        self,
        sentence_sentiments: List[List[Dict]]
    ) -> SentimentScore:
        """Aggregate sentence-level sentiments"""
        total_positive = 0.0
        total_negative = 0.0
        total_neutral = 0.0
        
        for sent_result in sentence_sentiments:
            scores = {item['label'].lower(): item['score'] for item in sent_result}
            total_positive += scores.get('positive', scores.get('pos', 0.0))
            total_negative += scores.get('negative', scores.get('neg', 0.0))
            total_neutral += scores.get('neutral', 1.0 - total_positive - total_negative)
        
        count = len(sentence_sentiments)
        avg_positive = total_positive / count
        avg_negative = total_negative / count
        avg_neutral = total_neutral / count
        
        # Determine polarity
        if avg_positive > avg_negative and avg_positive > avg_neutral:
            if avg_positive > 0.8:
                polarity = SentimentPolarity.VERY_POSITIVE
            else:
                polarity = SentimentPolarity.POSITIVE
        elif avg_negative > avg_positive and avg_negative > avg_neutral:
            if avg_negative > 0.8:
                polarity = SentimentPolarity.VERY_NEGATIVE
            else:
                polarity = SentimentPolarity.NEGATIVE
        else:
            polarity = SentimentPolarity.NEUTRAL
        
        confidence = max(avg_positive, avg_negative, avg_neutral)
        
        return SentimentScore(
            polarity=polarity,
            confidence=confidence,
            positive_score=avg_positive,
            negative_score=avg_negative,
            neutral_score=avg_neutral,
            compound_score=0.0  # Could calculate compound score from aggregated values
        )

    def _map_emotion_label(self, label: str) -> Optional[EmotionType]:
        """Map emotion label to EmotionType"""
        label_mapping = {
            'joy': EmotionType.JOY,
            'happiness': EmotionType.JOY,
            'sadness': EmotionType.SADNESS,
            'anger': EmotionType.ANGER,
            'fear': EmotionType.FEAR,
            'surprise': EmotionType.SURPRISE,
            'disgust': EmotionType.DISGUST,
            'love': EmotionType.LOVE,
            'excitement': EmotionType.EXCITEMENT,
            'anxiety': EmotionType.ANXIETY,
            'trust': EmotionType.TRUST
        }
        
        return label_mapping.get(label.lower())

    async def _generate_explanations(
        self,
        text: str,
        sentiment: SentimentScore,
        emotions: List[EmotionScore]
    ) -> Dict[str, Any]:
        """Generate explanations for sentiment analysis results"""
        try:
            explanations = {
                "sentiment_reasoning": self._explain_sentiment(text, sentiment),
                "emotion_reasoning": self._explain_emotions(text, emotions),
                "key_phrases": self._extract_key_phrases(text),
                "sentiment_indicators": self._find_sentiment_indicators(text)
            }
            
            return explanations
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            return {}

    def _explain_sentiment(self, text: str, sentiment: SentimentScore) -> str:
        """Explain sentiment analysis result"""
        if sentiment.polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
            return f"The text expresses positive sentiment with {sentiment.confidence:.2f} confidence. " \
                   f"Positive indicators dominate the content."
        elif sentiment.polarity in [SentimentPolarity.NEGATIVE, SentimentPolarity.VERY_NEGATIVE]:
            return f"The text expresses negative sentiment with {sentiment.confidence:.2f} confidence. " \
                   f"Negative indicators are prominent in the content."
        else:
            return f"The text maintains neutral sentiment with {sentiment.confidence:.2f} confidence. " \
                   f"The content is balanced or lacks strong emotional indicators."

    def _explain_emotions(self, text: str, emotions: List[EmotionScore]) -> str:
        """Explain emotion detection results"""
        if not emotions:
            return "No strong emotions detected in the text."
        
        top_emotion = emotions[0]
        return f"Primary emotion detected is {top_emotion.emotion.value} " \
               f"with {top_emotion.confidence:.2f} confidence and " \
               f"{top_emotion.intensity:.2f} intensity."

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases that influence sentiment"""
        # Simplified implementation - could use more sophisticated NLP
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'worst']
        
        text_lower = text.lower()
        key_phrases = []
        
        for word in positive_words:
            if word in text_lower:
                key_phrases.append(f"+{word}")
        
        for word in negative_words:
            if word in text_lower:
                key_phrases.append(f"-{word}")
        
        return key_phrases

    def _find_sentiment_indicators(self, text: str) -> Dict[str, List[str]]:
        """Find specific sentiment indicators in text"""
        # Simplified implementation
        return {
            "positive_indicators": self._extract_key_phrases(text),
            "negative_indicators": [],
            "neutral_indicators": []
        }

    async def analyze_temporal_sentiment(
        self,
        texts: List[str],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """Analyze sentiment changes over time"""
        if len(texts) != len(timestamps):
            raise ValueError("Texts and timestamps must have the same length")
        
        results = []
        
        for text, timestamp in zip(texts, timestamps):
            request = SentimentRequest(text=text)
            result = await self.analyze_sentiment(request)
            
            results.append({
                "timestamp": timestamp,
                "sentiment": result.sentiment,
                "emotions": result.emotions
            })
        
        # Calculate trends
        temporal_analysis = {
            "results": results,
            "trends": self._calculate_sentiment_trends(results),
            "statistics": self._calculate_temporal_statistics(results)
        }
        
        return temporal_analysis

    def _calculate_sentiment_trends(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate sentiment trends over time"""
        if len(results) < 2:
            return {"trend": "insufficient_data"}
        
        # Extract sentiment scores over time
        scores = [r["sentiment"].compound_score for r in results]
        
        # Calculate trend direction
        if scores[-1] > scores[0]:
            trend_direction = "improving"
        elif scores[-1] < scores[0]:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        # Calculate volatility
        volatility = np.std(scores) if len(scores) > 1 else 0.0
        
        return {
            "trend": trend_direction,
            "volatility": float(volatility),
            "score_change": scores[-1] - scores[0],
            "average_score": np.mean(scores)
        }

    def _calculate_temporal_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate temporal sentiment statistics"""
        if not results:
            return {}
        
        compound_scores = [r["sentiment"].compound_score for r in results]
        positive_scores = [r["sentiment"].positive_score for r in results]
        negative_scores = [r["sentiment"].negative_score for r in results]
        
        return {
            "compound_stats": {
                "mean": float(np.mean(compound_scores)),
                "std": float(np.std(compound_scores)),
                "min": float(np.min(compound_scores)),
                "max": float(np.max(compound_scores))
            },
            "positive_stats": {
                "mean": float(np.mean(positive_scores)),
                "std": float(np.std(positive_scores))
            },
            "negative_stats": {
                "mean": float(np.mean(negative_scores)),
                "std": float(np.std(negative_scores))
            }
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "analysis_types": [t.value for t in SentimentAnalysisType],
            "sentiment_polarities": [p.value for p in SentimentPolarity],
            "emotion_types": [e.value for e in EmotionType],
            "supports_multilingual": self.config.language_detection,
            "supports_batch": True,
            "supports_streaming": False,
            "supports_temporal": True,
            "models": {
                "primary": self.config.primary_model,
                "emotion": self.config.emotion_model,
                "aspect": self.config.aspect_model
            }
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get sentiment analysis metrics"""
        return self.metrics.get_summary()