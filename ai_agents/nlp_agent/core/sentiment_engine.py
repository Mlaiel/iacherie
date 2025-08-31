"""Sentiment Engine - Advanced Sentiment & Emotion Analysis
========================================================

State-of-the-art sentiment analysis engine using transformer models
for comprehensive emotion detection and sentiment classification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np

try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        pipeline, Pipeline
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Sentiment analysis will use fallback methods.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class SentimentLabel(Enum):
    """Sentiment classification labels"""
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"
    MIXED = "mixed"

class EmotionLabel(Enum):
    """Emotion classification labels"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    OPTIMISM = "optimism"
    PESSIMISM = "pessimism"

@dataclass
class SentimentScore:
    """Individual sentiment score"""
    label: str
    score: float
    confidence: float = 0.0

@dataclass
class EmotionScore:
    """Individual emotion score"""
    emotion: str
    score: float
    intensity: str = "low"  # low, medium, high

@dataclass
class SentimentResult:
    """Complete sentiment analysis result"""
    text: str
    overall_sentiment: SentimentLabel
    confidence: float
    sentiment_scores: List[SentimentScore] = field(default_factory=list)
    emotion_scores: List[EmotionScore] = field(default_factory=list)
    dominant_emotion: Optional[str] = None
    polarity: float = 0.0  # -1 to 1
    subjectivity: float = 0.0  # 0 to 1
    intensity: float = 0.0  # 0 to 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class SentimentEngine:
    """
    Advanced sentiment analysis engine using state-of-the-art transformer models
    for comprehensive emotion detection and sentiment classification.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Sentiment Engine"""
        self.config = config or default_config
        self.models = {}
        self.pipelines = {}
        self._model_cache = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment and emotion analysis models"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Using fallback sentiment analysis.")
            return
        
        try:
            # Primary sentiment model
            sentiment_model = self.config.sentiment.model_config.model_name
            logger.info(f"Loading sentiment model: {sentiment_model}")
            
            self.pipelines["sentiment"] = pipeline(
                "sentiment-analysis",
                model=sentiment_model,
                device=self._get_device(),
                return_all_scores=self.config.sentiment.return_all_scores
            )
            
            # Emotion detection model
            if self.config.sentiment.enable_emotion_detection:
                emotion_model = self.config.sentiment.emotion_model
                logger.info(f"Loading emotion model: {emotion_model}")
                
                self.pipelines["emotion"] = pipeline(
                    "text-classification",
                    model=emotion_model,
                    device=self._get_device(),
                    return_all_scores=True
                )
            
            # Additional specialized models
            self._load_specialized_models()
            
            logger.info("Sentiment models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize sentiment models: {e}")
            self._setup_fallback_models()
    
    def _load_specialized_models(self):
        """Load specialized sentiment models for different domains"""
        specialized_models = {
            "twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "financial": "ProsusAI/finbert",
            "multilingual": "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        }
        
        for domain, model_name in specialized_models.items():
            try:
                self.pipelines[f"sentiment_{domain}"] = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=self._get_device(),
                    return_all_scores=True
                )
                logger.info(f"Loaded {domain} sentiment model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load {domain} sentiment model: {e}")
    
    def _setup_fallback_models(self):
        """Setup fallback models when transformers are not available"""
        logger.info("Setting up fallback sentiment analysis")
        
        # Simple rule-based sentiment
        self.positive_words = {
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "enjoy", "happy", "pleased", "satisfied", "perfect",
            "awesome", "brilliant", "outstanding", "superb", "marvelous"
        }
        
        self.negative_words = {
            "bad", "terrible", "awful", "horrible", "disgusting", "hate",
            "dislike", "angry", "sad", "disappointed", "frustrated", "annoying",
            "worst", "pathetic", "useless", "boring", "stupid", "ridiculous"
        }
        
        self.fallback_mode = True
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""
        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    async def analyze_sentiment(
        self,
        text: Union[str, List[str]],
        language: Optional[str] = None,
        domain: Optional[str] = None,
        include_emotions: bool = None
    ) -> Union[SentimentResult, List[SentimentResult]]:
        """
        Analyze sentiment and emotions in text
        
        Args:
            text: Text or list of texts to analyze
            language: Optional language hint
            domain: Optional domain for specialized models
            include_emotions: Whether to include emotion analysis
        
        Returns:
            SentimentResult or list of results
        """
        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        # Set defaults
        if include_emotions is None:
            include_emotions = self.config.sentiment.enable_emotion_detection
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._analyze_single_text(
                    single_text,
                    language=language,
                    domain=domain,
                    include_emotions=include_emotions
                )
                results.append(result)
            
            # Calculate total processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Update processing time for all results
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise
    
    async def _analyze_single_text(
        self,
        text: str,
        language: Optional[str] = None,
        domain: Optional[str] = None,
        include_emotions: bool = True
    ) -> SentimentResult:
        """Analyze sentiment for a single text"""
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = SentimentResult(text=text, overall_sentiment=SentimentLabel.NEUTRAL, confidence=0.0)
        
        try:
            # Choose appropriate model
            model_key = self._select_model(domain, language)
            
            if hasattr(self, 'fallback_mode') and self.fallback_mode:
                # Use fallback analysis
                await self._fallback_sentiment_analysis(text, result)
            else:
                # Use transformer models
                await self._transformer_sentiment_analysis(text, result, model_key)
            
            # Emotion analysis
            if include_emotions and "emotion" in self.pipelines:
                await self._analyze_emotions(text, result)
            
            # Calculate additional metrics
            self._calculate_additional_metrics(text, result)
            
            # Add metadata
            result.metadata = {
                "model_used": model_key,
                "language": language,
                "domain": domain,
                "text_length": len(text),
                "model_version": "2.0"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Single text sentiment analysis failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    def _select_model(self, domain: Optional[str], language: Optional[str]) -> str:
        """Select appropriate model based on domain and language"""
        # Domain-specific models
        if domain and f"sentiment_{domain}" in self.pipelines:
            return f"sentiment_{domain}"
        
        # Language-specific models
        if language and language != "en" and "sentiment_multilingual" in self.pipelines:
            return "sentiment_multilingual"
        
        # Default sentiment model
        return "sentiment"
    
    async def _transformer_sentiment_analysis(
        self,
        text: str,
        result: SentimentResult,
        model_key: str
    ):
        """Perform sentiment analysis using transformer models"""
        try:
            pipeline_obj = self.pipelines.get(model_key, self.pipelines["sentiment"])
            
            # Run inference
            predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                pipeline_obj,
                text
            )
            
            # Process results
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    # Multiple scores returned
                    scores = predictions[0]
                else:
                    # Single prediction
                    scores = predictions
                
                # Convert to SentimentScore objects
                sentiment_scores = []
                max_score = 0.0
                dominant_label = "neutral"
                
                for pred in scores:
                    label = pred["label"].lower()
                    score = pred["score"]
                    
                    # Map labels to standard format
                    label = self._normalize_sentiment_label(label)
                    
                    sentiment_scores.append(SentimentScore(
                        label=label,
                        score=score,
                        confidence=score
                    ))
                    
                    if score > max_score:
                        max_score = score
                        dominant_label = label
                
                result.sentiment_scores = sentiment_scores
                result.overall_sentiment = SentimentLabel(dominant_label)
                result.confidence = max_score
                
                # Calculate polarity (-1 to 1)
                result.polarity = self._calculate_polarity(sentiment_scores)
            
        except Exception as e:
            logger.error(f"Transformer sentiment analysis failed: {e}")
            await self._fallback_sentiment_analysis(text, result)
    
    async def _fallback_sentiment_analysis(self, text: str, result: SentimentResult):
        """Fallback sentiment analysis using rule-based approach"""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        if positive_count > negative_count:
            result.overall_sentiment = SentimentLabel.POSITIVE
            result.confidence = min(positive_count / len(words) * 5, 1.0)
            result.polarity = 0.5
        elif negative_count > positive_count:
            result.overall_sentiment = SentimentLabel.NEGATIVE
            result.confidence = min(negative_count / len(words) * 5, 1.0)
            result.polarity = -0.5
        else:
            result.overall_sentiment = SentimentLabel.NEUTRAL
            result.confidence = 0.5
            result.polarity = 0.0
        
        # Create sentiment scores
        result.sentiment_scores = [
            SentimentScore(
                label=result.overall_sentiment.value,
                score=result.confidence,
                confidence=result.confidence
            )
        ]
    
    async def _analyze_emotions(self, text: str, result: SentimentResult):
        """Analyze emotions in text"""
        try:
            emotion_pipeline = self.pipelines["emotion"]
            
            predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                emotion_pipeline,
                text
            )
            
            if isinstance(predictions, list) and len(predictions) > 0:
                emotion_scores = []
                max_score = 0.0
                dominant_emotion = None
                
                emotions = predictions[0] if isinstance(predictions[0], list) else predictions
                
                for pred in emotions:
                    emotion = pred["label"].lower()
                    score = pred["score"]
                    
                    # Determine intensity
                    if score > 0.7:
                        intensity = "high"
                    elif score > 0.4:
                        intensity = "medium"
                    else:
                        intensity = "low"
                    
                    emotion_scores.append(EmotionScore(
                        emotion=emotion,
                        score=score,
                        intensity=intensity
                    ))
                    
                    if score > max_score:
                        max_score = score
                        dominant_emotion = emotion
                
                result.emotion_scores = emotion_scores
                result.dominant_emotion = dominant_emotion
                
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
    
    def _normalize_sentiment_label(self, label: str) -> str:
        """Normalize sentiment labels to standard format"""
        label = label.lower()
        
        # Map common label variations
        positive_labels = ["positive", "pos", "1", "good", "happy"]
        negative_labels = ["negative", "neg", "0", "bad", "sad"]
        neutral_labels = ["neutral", "neu", "mixed"]
        
        if label in positive_labels:
            return "positive"
        elif label in negative_labels:
            return "negative"
        elif label in neutral_labels:
            return "neutral"
        else:
            return label
    
    def _calculate_polarity(self, sentiment_scores: List[SentimentScore]) -> float:
        """Calculate polarity score from sentiment scores"""
        total_positive = sum(score.score for score in sentiment_scores if score.label == "positive")
        total_negative = sum(score.score for score in sentiment_scores if score.label == "negative")
        
        if total_positive + total_negative == 0:
            return 0.0
        
        return (total_positive - total_negative) / (total_positive + total_negative)
    
    def _calculate_additional_metrics(self, text: str, result: SentimentResult):
        """Calculate additional sentiment metrics"""
        words = text.split()
        
        # Subjectivity (simple heuristic)
        subjective_indicators = [
            "i", "me", "my", "mine", "think", "feel", "believe", "opinion",
            "amazing", "terrible", "love", "hate", "brilliant", "awful"
        ]
        
        subjective_count = sum(
            1 for word in words
            if word.lower() in subjective_indicators
        )
        
        result.subjectivity = min(subjective_count / max(len(words), 1), 1.0)
        
        # Intensity based on punctuation and caps
        intensity_indicators = text.count("!") + text.count("?") * 0.5
        caps_ratio = sum(1 for char in text if char.isupper()) / max(len(text), 1)
        
        result.intensity = min((intensity_indicators * 0.1 + caps_ratio) * 2, 1.0)
    
    async def analyze_sentiment_over_time(
        self,
        texts: List[str],
        timestamps: Optional[List[datetime]] = None
    ) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        if not texts:
            return {"error": "No texts provided"}
        
        results = await self.analyze_sentiment(texts)
        
        # Prepare data for time series analysis
        sentiment_timeline = []
        for i, result in enumerate(results):
            timestamp = timestamps[i] if timestamps and i < len(timestamps) else datetime.now()
            
            sentiment_timeline.append({
                "timestamp": timestamp.isoformat(),
                "sentiment": result.overall_sentiment.value,
                "confidence": result.confidence,
                "polarity": result.polarity,
                "emotions": [
                    {"emotion": emotion.emotion, "score": emotion.score}
                    for emotion in result.emotion_scores[:3]  # Top 3 emotions
                ] if result.emotion_scores else []
            })
        
        # Calculate trend statistics
        polarities = [result.polarity for result in results]
        
        trend_analysis = {
            "timeline": sentiment_timeline,
            "statistics": {
                "total_texts": len(texts),
                "average_polarity": np.mean(polarities) if polarities else 0,
                "polarity_std": np.std(polarities) if polarities else 0,
                "sentiment_distribution": self._get_sentiment_distribution(results),
                "trend_direction": self._calculate_trend_direction(polarities)
            }
        }
        
        return trend_analysis
    
    def _get_sentiment_distribution(self, results: List[SentimentResult]) -> Dict[str, float]:
        """Get distribution of sentiments"""
        total = len(results)
        if total == 0:
            return {}
        
        distribution = {}
        for sentiment in SentimentLabel:
            count = sum(1 for result in results if result.overall_sentiment == sentiment)
            distribution[sentiment.value] = count / total
        
        return distribution
    
    def _calculate_trend_direction(self, polarities: List[float]) -> str:
        """Calculate overall trend direction"""
        if len(polarities) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(polarities))
        slope = np.polyfit(x, polarities, 1)[0]
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"
    
    async def compare_sentiments(
        self,
        text1: str,
        text2: str
    ) -> Dict[str, Any]:
        """Compare sentiments between two texts"""
        results = await self.analyze_sentiment([text1, text2])
        
        result1, result2 = results
        
        comparison = {
            "text1_sentiment": result1.overall_sentiment.value,
            "text2_sentiment": result2.overall_sentiment.value,
            "polarity_difference": abs(result1.polarity - result2.polarity),
            "confidence_difference": abs(result1.confidence - result2.confidence),
            "similarity": 1.0 - abs(result1.polarity - result2.polarity),
            "analysis": {
                "text1": {
                    "sentiment": result1.overall_sentiment.value,
                    "confidence": result1.confidence,
                    "polarity": result1.polarity,
                    "dominant_emotion": result1.dominant_emotion
                },
                "text2": {
                    "sentiment": result2.overall_sentiment.value,
                    "confidence": result2.confidence,
                    "polarity": result2.polarity,
                    "dominant_emotion": result2.dominant_emotion
                }
            }
        }
        
        return comparison
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "models_loaded": list(self.pipelines.keys()),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "device": self._get_device(),
            "fallback_mode": hasattr(self, 'fallback_mode') and self.fallback_mode,
            "emotion_detection_enabled": "emotion" in self.pipelines
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        status = {
            "status": "healthy",
            "models_loaded": len(self.pipelines),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "emotion_detection": "emotion" in self.pipelines
        }
        
        # Test basic functionality
        try:
            if not hasattr(self, 'fallback_mode') or not self.fallback_mode:
                # Quick test with sentiment pipeline
                test_pipeline = self.pipelines.get("sentiment")
                if test_pipeline:
                    test_result = test_pipeline("This is a test.")
                    status["test_result"] = "passed"
                else:
                    status["status"] = "degraded"
                    status["test_result"] = "no_models"
            else:
                status["test_result"] = "fallback_mode"
        except Exception as e:
            status["status"] = "unhealthy"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the sentiment engine"""
        logger.info("Shutting down Sentiment Engine")
        
        # Clear model cache
        self.models.clear()
        self.pipelines.clear()
        self._model_cache.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_sentiment_similarity(result1: SentimentResult, result2: SentimentResult) -> float:
    """Calculate similarity between two sentiment results"""
    polarity_sim = 1.0 - abs(result1.polarity - result2.polarity)
    confidence_sim = 1.0 - abs(result1.confidence - result2.confidence)
    
    # Emotion similarity
    emotion_sim = 0.5  # Default if no emotions
    if result1.emotion_scores and result2.emotion_scores:
        emotion1_dict = {e.emotion: e.score for e in result1.emotion_scores}
        emotion2_dict = {e.emotion: e.score for e in result2.emotion_scores}
        
        common_emotions = set(emotion1_dict.keys()) & set(emotion2_dict.keys())
        if common_emotions:
            emotion_diffs = [
                abs(emotion1_dict[emotion] - emotion2_dict[emotion])
                for emotion in common_emotions
            ]
            emotion_sim = 1.0 - np.mean(emotion_diffs)
    
    return (polarity_sim + confidence_sim + emotion_sim) / 3.0
