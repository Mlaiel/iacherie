"""Sentiment Analysis Module

Advanced sentiment analysis and emotion detection system for multi-modal content
in the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from pathlib import Path
import json
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, RobertaTokenizer, RobertaForSequenceClassification
)
import cv2
import librosa
from PIL import Image
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Optional sentiment analysis libraries
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    SentimentIntensityAnalyzer = None

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
    emoji = None

from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass


class SentimentLabel(Enum):
    """
Sentiment labels"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionLabel(Enum):
    """Basic emotion labels"""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


class IntensityLevel(Enum):
    """Intensity levels for emotions and sentiments"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class ModalityType(Enum):
    """Types of modalities for analysis"""

    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


@dataclass
class SentimentScore:
    """Sentiment analysis result"""
    positive: float
    negative: float
    neutral: float
    compound: float
    confidence: float
    label: SentimentLabel
    intensity: IntensityLevel
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'positive': self.positive,
            'negative': self.negative,
            'neutral': self.neutral,
            'compound': self.compound,
            'confidence': self.confidence,
            'label': self.label.value,
            'intensity': self.intensity.value
        }


@dataclass
class EmotionScore:
    """
Emotion detection result"""
    emotions: Dict[EmotionLabel, float]
    dominant_emotion: EmotionLabel
    confidence: float
    intensity: IntensityLevel
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'emotions': {k.value: v for k, v in self.emotions.items()},
            'dominant_emotion': self.dominant_emotion.value,
            'confidence': self.confidence,
            'intensity': self.intensity.value
        }


@dataclass
class ToneAnalysisResult:
    """
Tone analysis result"""
    analytical: float
    confident: float
    tentative: float
    joy: float
    fear: float
    sadness: float
    anger: float
    primary_tone: str
    tone_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'analytical': self.analytical,
            'confident': self.confident,
            'tentative': self.tentative,
            'joy': self.joy,
            'fear': self.fear,
            'sadness': self.sadness,
            'anger': self.anger,
            'primary_tone': self.primary_tone,
            'tone_confidence': self.tone_confidence
        }


@dataclass
class SentimentAnalysisResult:
    """
Complete sentiment analysis result"""
    content_id: str
    modality: ModalityType
    sentiment: SentimentScore
    emotions: EmotionScore
    tone: ToneAnalysisResult
    subjectivity: float
    polarity: float
    emotional_arc: List[Tuple[float, float]] = field(default_factory=list)  # (time, emotion_score)
    keywords: List[str] = field(default_factory=list)
    phrases: List[Tuple[str, float]] = field(default_factory=list)  # (phrase, sentiment)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'modality': self.modality.value,
            'sentiment': self.sentiment.to_dict(),
            'emotions': self.emotions.to_dict(),
            'tone': self.tone.to_dict(),
            'subjectivity': self.subjectivity,
            'polarity': self.polarity,
            'emotional_arc': self.emotional_arc,
            'keywords': self.keywords,
            'phrases': self.phrases,
            'metadata': self.metadata,
            'processing_time_ms': self.processing_time_ms,
            'timestamp': self.timestamp.isoformat()
        }


class SentimentAnalyzer(ABC):
    """
Abstract base class for sentiment analyzers"""
    
    def __init__(self, model_name: str = None, device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    def _get_device(self, device: str) -> torch.device:
        """Get appropriate device"""
        if device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(device)
    
    @abstractmethod
    async def load_model(self):
        """Load the sentiment analysis model"""
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, content: Any, content_id: str = None) -> SentimentAnalysisResult:
        """
Analyze sentiment of content"""
        pass
    
    def _determine_intensity(self, score: float) -> IntensityLevel:
        """
Determine intensity level from score"""
        if score < 0.3:
            return IntensityLevel.LOW
        elif score < 0.6:
            return IntensityLevel.MEDIUM
        elif score < 0.8:
            return IntensityLevel.HIGH
        else:
            return IntensityLevel.EXTREME
    
    def _determine_sentiment_label(self, compound_score: float) -> SentimentLabel:
        """
Determine sentiment label from compound score"""
        if compound_score >= 0.05:
            return SentimentLabel.POSITIVE
        elif compound_score <= -0.05:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL


class TextSentimentAnalyzer(SentimentAnalyzer):
    """
Advanced text sentiment analyzer"""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest", device: str = "auto"):
        super().__init__(model_name, device)
        self.roberta_pipeline = None
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.nlp = None
        self.lemmatizer = WordNetLemmatizer()
        self.emotion_model = None
        
        # Emotion lexicons
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.intensity_modifiers = self._load_intensity_modifiers()
    
    async def load_model(self):
        """Load text sentiment analysis models"""
        try:
            # Load RoBERTa model for sentiment
            self.roberta_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device.type == "cuda" else -1
            )
            
            # Load emotion analysis model
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if self.device.type == "cuda" else -1
            )
            
            # Load spaCy for advanced NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy model not available")
            
            self.is_loaded = True
            self.logger.info("Text sentiment analyzer loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load text sentiment analyzer: {e}")
            raise
    
    async def analyze_sentiment(self, text: str, content_id: str = None) -> SentimentAnalysisResult:
        """Analyze sentiment of text content"""
        if not self.is_loaded:
            await self.load_model()
        
        start_time = datetime.now()
        content_id = content_id or f"text_{int(start_time.timestamp())}"
        
        try:
            # Preprocess text
            processed_text = await self._preprocess_text(text)
            
            # Basic sentiment analysis with VADER
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Advanced sentiment analysis with RoBERTa
            roberta_result = self.roberta_pipeline(text[:512])  # Limit input length
            roberta_scores = self._parse_roberta_output(roberta_result[0])
            
            # Emotion analysis
            emotion_result = self.emotion_model(text[:512])
            emotion_scores = self._parse_emotion_output(emotion_result)
            
            # Combine sentiment scores
            combined_sentiment = self._combine_sentiment_scores(vader_scores, roberta_scores)
            
            # Tone analysis
            tone_analysis = await self._analyze_tone(text)
            
            # Subjectivity and polarity with TextBlob
            blob = TextBlob(text)
            subjectivity = float(blob.sentiment.subjectivity)
            polarity = float(blob.sentiment.polarity)
            
            # Extract emotional arc for longer texts
            emotional_arc = await self._extract_emotional_arc(text)
            
            # Extract sentiment-bearing keywords and phrases
            keywords = await self._extract_sentiment_keywords(text)
            phrases = await self._extract_sentiment_phrases(text)
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return SentimentAnalysisResult(
                content_id=content_id,
                modality=ModalityType.TEXT,
                sentiment=combined_sentiment,
                emotions=emotion_scores,
                tone=tone_analysis,
                subjectivity=subjectivity,
                polarity=polarity,
                emotional_arc=emotional_arc,
                keywords=keywords,
                phrases=phrases,
                processing_time_ms=processing_time,
                metadata={
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'sentence_count': len(sent_tokenize(text)),
                    'vader_scores': vader_scores,
                    'roberta_confidence': roberta_result[0]['score'] if roberta_result else 0.0
                }
            )
            
        except Exception as e:
            self.logger.error(f"Text sentiment analysis failed: {e}")
            raise
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Handle emojis
        text = self._process_emojis(text)
        
        # Clean text
        text = re.sub(r'http\S+', '[URL]', text)  # Replace URLs
        text = re.sub(r'@\w+', '[MENTION]', text)  # Replace mentions
        text = re.sub(r'#\w+', '[HASHTAG]', text)  # Replace hashtags
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text.strip()
    
    def _process_emojis(self, text: str) -> str:
        """
Convert emojis to text sentiment indicators"""
        # Define emoji sentiment mapping
        positive_emojis = ['😊', '😄', '😁', '🙂', '😍', '🥰', '😘', '🤗', '👍', '❤️', '💕', '🎉']
        negative_emojis = ['😢', '😭', '😔', '😞', '😒', '😠', '😡', '🤬', '💔', '😰', '😱', '👎']
        
        for emoji_char in positive_emojis:
            if emoji_char in text:
                text = text.replace(emoji_char, ' [POSITIVE_EMOJI] ')
        
        for emoji_char in negative_emojis:
            if emoji_char in text:
                text = text.replace(emoji_char, ' [NEGATIVE_EMOJI] ')
        
        return text
    
    def _parse_roberta_output(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
Parse RoBERTa model output"""
        label = result['label'].lower()
        score = result['score']
        
        # Map to standard format
        if 'positive' in label or label == 'label_2':
            return {'positive': score, 'negative': 1-score, 'neutral': 0.0}
        elif 'negative' in label or label == 'label_0':
            return {'positive': 1-score, 'negative': score, 'neutral': 0.0}
        else:  # neutral or label_1
            return {'positive': 0.0, 'negative': 0.0, 'neutral': score}
    
    def _parse_emotion_output(self, results: List[Dict[str, Any]]) -> EmotionScore:
        """
Parse emotion model output"""
        emotions = {}
        
        # Map model labels to EmotionLabel enum
        label_mapping = {
            'joy': EmotionLabel.JOY,
            'sadness': EmotionLabel.SADNESS,
            'anger': EmotionLabel.ANGER,
            'fear': EmotionLabel.FEAR,
            'surprise': EmotionLabel.SURPRISE,
            'disgust': EmotionLabel.DISGUST,
            'trust': EmotionLabel.TRUST,
            'anticipation': EmotionLabel.ANTICIPATION
        }
        
        # Initialize all emotions with 0
        for emotion in EmotionLabel:
            emotions[emotion] = 0.0
        
        # Fill in detected emotions
        for result in results:
            label = result['label'].lower()
            score = result['score']
            
            if label in label_mapping:
                emotions[label_mapping[label]] = float(score)
        
        # Find dominant emotion
        dominant_emotion = max(emotions.keys(), key=lambda k: emotions[k])
        confidence = emotions[dominant_emotion]
        intensity = self._determine_intensity(confidence)
        
        return EmotionScore(
            emotions=emotions,
            dominant_emotion=dominant_emotion,
            confidence=confidence,
            intensity=intensity
        )
    
    def _combine_sentiment_scores(
        self,
        vader_scores: Dict[str, float],
        roberta_scores: Dict[str, float]
    ) -> SentimentScore:
        """
Combine VADER and RoBERTa sentiment scores"""
        # Weighted combination
        vader_weight = 0.3
        roberta_weight = 0.7
        
        combined_positive = (vader_scores['pos'] * vader_weight + 
                           roberta_scores['positive'] * roberta_weight)
        combined_negative = (vader_scores['neg'] * vader_weight + 
                           roberta_scores['negative'] * roberta_weight)
        combined_neutral = (vader_scores['neu'] * vader_weight + 
                          roberta_scores['neutral'] * roberta_weight)
        
        compound = vader_scores['compound']
        
        # Calculate confidence as agreement between models
        vader_prediction = 'positive' if vader_scores['compound'] > 0.05 else 'negative' if vader_scores['compound'] < -0.05 else 'neutral'
        roberta_prediction = max(roberta_scores.keys(), key=roberta_scores.get)
        
        confidence = 0.8 if vader_prediction == roberta_prediction else 0.5
        
        label = self._determine_sentiment_label(compound)
        intensity = self._determine_intensity(abs(compound))
        
        return SentimentScore(
            positive=float(combined_positive),
            negative=float(combined_negative),
            neutral=float(combined_neutral),
            compound=float(compound),
            confidence=confidence,
            label=label,
            intensity=intensity
        )
    
    async def _analyze_tone(self, text: str) -> ToneAnalysisResult:
        """
Analyze tone characteristics of text"""
        # Simple tone analysis based on linguistic features
        words = word_tokenize(text.lower())
        
        # Analytical tone indicators
        analytical_words = ['analyze', 'therefore', 'because', 'evidence', 'research', 'study']
        analytical_score = sum(1 for word in analytical_words if word in words) / len(words)
        
        # Confident tone indicators
        confident_words = ['definitely', 'certainly', 'absolutely', 'clearly', 'obviously']
        confident_score = sum(1 for word in confident_words if word in words) / len(words)
        
        # Tentative tone indicators
        tentative_words = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'seems']
        tentative_score = sum(1 for word in tentative_words if word in words) / len(words)
        
        # Emotion-based tones (simplified)
        joy_words = ['happy', 'excited', 'amazing', 'wonderful', 'fantastic']
        joy_score = sum(1 for word in joy_words if word in words) / len(words)
        
        fear_words = ['scared', 'worried', 'anxious', 'nervous', 'afraid']
        fear_score = sum(1 for word in fear_words if word in words) / len(words)
        
        sadness_words = ['sad', 'depressed', 'disappointed', 'upset', 'hurt']
        sadness_score = sum(1 for word in sadness_words if word in words) / len(words)
        
        anger_words = ['angry', 'furious', 'mad', 'irritated', 'annoyed']
        anger_score = sum(1 for word in anger_words if word in words) / len(words)
        
        # Determine primary tone
        tone_scores = {
            'analytical': analytical_score,
            'confident': confident_score,
            'tentative': tentative_score,
            'joy': joy_score,
            'fear': fear_score,
            'sadness': sadness_score,
            'anger': anger_score
        }
        
        primary_tone = max(tone_scores.keys(), key=tone_scores.get)
        tone_confidence = tone_scores[primary_tone]
        
        return ToneAnalysisResult(
            analytical=float(analytical_score),
            confident=float(confident_score),
            tentative=float(tentative_score),
            joy=float(joy_score),
            fear=float(fear_score),
            sadness=float(sadness_score),
            anger=float(anger_score),
            primary_tone=primary_tone,
            tone_confidence=float(tone_confidence)
        )
    
    async def _extract_emotional_arc(self, text: str) -> List[Tuple[float, float]]:
        """
Extract emotional arc for narrative texts"""
        sentences = sent_tokenize(text)
        if len(sentences) < 3:
            return []
        
        emotional_arc = []
        
        for i, sentence in enumerate(sentences):
            # Analyze sentiment of each sentence
            sentence_sentiment = self.vader_analyzer.polarity_scores(sentence)
            time_position = i / len(sentences)
            emotion_score = sentence_sentiment['compound']
            
            emotional_arc.append((float(time_position), float(emotion_score)))
        
        return emotional_arc
    
    async def _extract_sentiment_keywords(self, text: str) -> List[str]:
        """
Extract keywords that contribute to sentiment"""
        keywords = []
        
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract adjectives and adverbs as sentiment keywords
            for token in doc:
                if (token.pos_ in ['ADJ', 'ADV'] and 
                    len(token.text) > 2 and 
                    not token.is_stop):
                    keywords.append(token.lemma_.lower())
        else:
            # Fallback to simple approach
            words = word_tokenize(text.lower())
            sentiment_words = []
            
            for word in words:
                # Check against VADER lexicon
                if word in self.vader_analyzer.lexicon:
                    sentiment_words.append(word)
            
            keywords = sentiment_words
        
        # Remove duplicates and limit
        return list(set(keywords))[:20]
    
    async def _extract_sentiment_phrases(self, text: str) -> List[Tuple[str, float]]:
        """
Extract phrases with their sentiment scores"""
        sentences = sent_tokenize(text)
        phrases = []
        
        for sentence in sentences:
            if len(sentence.split()) > 3:  # Skip very short sentences
                sentiment = self.vader_analyzer.polarity_scores(sentence)
                if abs(sentiment['compound']) > 0.1:  # Only significant sentiment
                    phrases.append((sentence.strip(), float(sentiment['compound'])))
        
        # Sort by absolute sentiment strength
        phrases.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return phrases[:10]  # Return top 10 most emotional phrases
    
    def _load_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """
Load emotion lexicon for keyword-based analysis"""
        # Simplified emotion lexicon
        return {
            'joy': {'happy': 0.8, 'joyful': 0.9, 'excited': 0.7, 'cheerful': 0.6},
            'sadness': {'sad': 0.8, 'depressed': 0.9, 'melancholy': 0.7, 'sorrowful': 0.8},
            'anger': {'angry': 0.8, 'furious': 0.9, 'rage': 0.9, 'mad': 0.7},
            'fear': {'scared': 0.8, 'afraid': 0.7, 'terrified': 0.9, 'anxious': 0.6},
            'surprise': {'surprised': 0.7, 'amazed': 0.8, 'astonished': 0.9, 'shocked': 0.8},
            'disgust': {'disgusting': 0.8, 'revolting': 0.9, 'repulsive': 0.8, 'gross': 0.6}
        }
    
    def _load_intensity_modifiers(self) -> Dict[str, float]:
        """
Load intensity modifiers"""
        return {
            'very': 1.3,
            'extremely': 1.5,
            'incredibly': 1.4,
            'absolutely': 1.4,
            'totally': 1.3,
            'quite': 1.1,
            'rather': 1.1,
            'somewhat': 0.8,
            'slightly': 0.7,
            'barely': 0.5
        }


class MultiModalSentimentAnalyzer:
    """
Multi-modal sentiment analyzer for combined text, audio, and visual content"""
    
    def __init__(self, device: str = "auto"):
        self.device = device
        self.text_analyzer = TextSentimentAnalyzer(device=device)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_loaded = False
        
        # Fusion weights for different modalities
        self.fusion_weights = {
            'text': 0.5,
            'audio': 0.3,
            'visual': 0.2
        }
    
    async def load_models(self):
        """Load all modal-specific analyzers"""
        try:
            await self.text_analyzer.load_model()
            # Additional modal analyzers would be loaded here
            
            self.is_loaded = True
            self.logger.info("Multi-modal sentiment analyzer loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load multi-modal analyzer: {e}")
            raise
    
    async def analyze_multimodal_content(
        self,
        content: Dict[str, Any],
        content_id: str = None
    ) -> SentimentAnalysisResult:
        """Analyze sentiment across multiple modalities"""
        if not self.is_loaded:
            await self.load_models()
        
        start_time = datetime.now()
        content_id = content_id or f"multimodal_{int(start_time.timestamp())}"
        
        modal_results = {}
        
        # Analyze text content if available
        if 'text' in content:
            text_result = await self.text_analyzer.analyze_sentiment(
                content['text'], f"{content_id}_text"
            )
            modal_results['text'] = text_result
        
        # Analyze audio content if available
        if 'audio' in content:
            audio_result = await self._analyze_audio_sentiment(
                content['audio'], f"{content_id}_audio"
            )
            modal_results['audio'] = audio_result
        
        # Analyze visual content if available
        if 'image' in content or 'video' in content:
            visual_result = await self._analyze_visual_sentiment(
                content.get('image') or content.get('video'), 
                f"{content_id}_visual"
            )
            modal_results['visual'] = visual_result
        
        # Fuse results from different modalities
        fused_result = await self._fuse_modal_results(modal_results, content_id)
        
        # Processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        fused_result.processing_time_ms = processing_time
        
        return fused_result
    
    async def _analyze_audio_sentiment(self, audio_path: str, content_id: str) -> SentimentAnalysisResult:
        """Analyze sentiment from audio content"""
        # Placeholder for audio sentiment analysis
        # This would involve:
        # 1. Speech-to-text conversion
        # 2. Prosodic feature extraction (pitch, tone, pace)
        # 3. Emotional speech recognition
        
        # For now, return neutral result
        return SentimentAnalysisResult(
            content_id=content_id,
            modality=ModalityType.AUDIO,
            sentiment=SentimentScore(0.33, 0.33, 0.34, 0.0, 0.5, SentimentLabel.NEUTRAL, IntensityLevel.LOW),
            emotions=EmotionScore({e: 0.125 for e in EmotionLabel}, EmotionLabel.JOY, 0.5, IntensityLevel.LOW),
            tone=ToneAnalysisResult(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'neutral', 0.5),
            subjectivity=0.5,
            polarity=0.0
        )
    
    async def _analyze_visual_sentiment(self, image_path: str, content_id: str) -> SentimentAnalysisResult:
        """
Analyze sentiment from visual content"""
        # Placeholder for visual sentiment analysis
        # This would involve:
        # 1. Facial expression recognition
        # 2. Scene emotion detection
        # 3. Color psychology analysis
        # 4. Composition mood analysis
        
        # For now, return neutral result
        return SentimentAnalysisResult(
            content_id=content_id,
            modality=ModalityType.IMAGE,
            sentiment=SentimentScore(0.33, 0.33, 0.34, 0.0, 0.5, SentimentLabel.NEUTRAL, IntensityLevel.LOW),
            emotions=EmotionScore({e: 0.125 for e in EmotionLabel}, EmotionLabel.JOY, 0.5, IntensityLevel.LOW),
            tone=ToneAnalysisResult(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'neutral', 0.5),
            subjectivity=0.5,
            polarity=0.0
        )
    
    async def _fuse_modal_results(
        self,
        modal_results: Dict[str, SentimentAnalysisResult],
        content_id: str
    ) -> SentimentAnalysisResult:
        """
Fuse results from different modalities"""
        if not modal_results:
            raise ValueError("No modal results to fuse")
        
        # Weighted fusion of sentiment scores
        fused_positive = 0.0
        fused_negative = 0.0
        fused_neutral = 0.0
        fused_compound = 0.0
        total_weight = 0.0
        
        # Fused emotions
        fused_emotions = {emotion: 0.0 for emotion in EmotionLabel}
        
        # Fused tone
        fused_tone_scores = {
            'analytical': 0.0,
            'confident': 0.0,
            'tentative': 0.0,
            'joy': 0.0,
            'fear': 0.0,
            'sadness': 0.0,
            'anger': 0.0
        }
        
        fused_subjectivity = 0.0
        fused_polarity = 0.0
        
        # Combine results
        for modality, result in modal_results.items():
            weight = self.fusion_weights.get(modality, 1.0)
            
            # Sentiment fusion
            fused_positive += result.sentiment.positive * weight
            fused_negative += result.sentiment.negative * weight
            fused_neutral += result.sentiment.neutral * weight
            fused_compound += result.sentiment.compound * weight
            
            # Emotion fusion
            for emotion, score in result.emotions.emotions.items():
                fused_emotions[emotion] += score * weight
            
            # Tone fusion
            tone_dict = result.tone.to_dict()
            for tone_type, score in tone_dict.items():
                if tone_type in fused_tone_scores:
                    fused_tone_scores[tone_type] += score * weight
            
            # Other metrics
            fused_subjectivity += result.subjectivity * weight
            fused_polarity += result.polarity * weight
            
            total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            fused_positive /= total_weight
            fused_negative /= total_weight
            fused_neutral /= total_weight
            fused_compound /= total_weight
            fused_subjectivity /= total_weight
            fused_polarity /= total_weight
            
            for emotion in fused_emotions:
                fused_emotions[emotion] /= total_weight
            
            for tone_type in fused_tone_scores:
                fused_tone_scores[tone_type] /= total_weight
        
        # Create fused sentiment score
        fused_sentiment = SentimentScore(
            positive=fused_positive,
            negative=fused_negative,
            neutral=fused_neutral,
            compound=fused_compound,
            confidence=0.8,  # High confidence for multimodal
            label=self.text_analyzer._determine_sentiment_label(fused_compound),
            intensity=self.text_analyzer._determine_intensity(abs(fused_compound))
        )
        
        # Create fused emotion score
        dominant_emotion = max(fused_emotions.keys(), key=fused_emotions.get)
        emotion_confidence = fused_emotions[dominant_emotion]
        
        fused_emotion_score = EmotionScore(
            emotions=fused_emotions,
            dominant_emotion=dominant_emotion,
            confidence=emotion_confidence,
            intensity=self.text_analyzer._determine_intensity(emotion_confidence)
        )
        
        # Create fused tone analysis
        primary_tone = max(fused_tone_scores.keys(), key=fused_tone_scores.get)
        
        fused_tone_analysis = ToneAnalysisResult(
            analytical=fused_tone_scores['analytical'],
            confident=fused_tone_scores['confident'],
            tentative=fused_tone_scores['tentative'],
            joy=fused_tone_scores['joy'],
            fear=fused_tone_scores['fear'],
            sadness=fused_tone_scores['sadness'],
            anger=fused_tone_scores['anger'],
            primary_tone=primary_tone,
            tone_confidence=fused_tone_scores[primary_tone]
        )
        
        # Combine keywords and phrases from all modalities
        all_keywords = []
        all_phrases = []
        
        for result in modal_results.values():
            all_keywords.extend(result.keywords)
            all_phrases.extend(result.phrases)
        
        # Remove duplicates
        unique_keywords = list(set(all_keywords))
        unique_phrases = list(set(all_phrases))
        
        return SentimentAnalysisResult(
            content_id=content_id,
            modality=ModalityType.MULTIMODAL,
            sentiment=fused_sentiment,
            emotions=fused_emotion_score,
            tone=fused_tone_analysis,
            subjectivity=fused_subjectivity,
            polarity=fused_polarity,
            keywords=unique_keywords[:20],
            phrases=unique_phrases[:10],
            metadata={
                'modalities_used': list(modal_results.keys()),
                'fusion_weights': self.fusion_weights,
                'modal_confidences': {k: v.sentiment.confidence for k, v in modal_results.items()}
            }
        )
    
    def update_fusion_weights(self, new_weights: Dict[str, float]):
        """Update fusion weights for different modalities"""
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights
            new_weights = {k: v / total_weight for k, v in new_weights.items()}
        
        self.fusion_weights.update(new_weights)
        self.logger.info(f"Updated fusion weights: {self.fusion_weights}")


# Utility classes for specialized analysis
class EmotionDetector(TextSentimentAnalyzer):
    """Specialized emotion detector"""
    
    def __init__(self, device: str = "auto"):
        super().__init__("j-hartmann/emotion-english-distilroberta-base", device)
    
    async def detect_emotions_only(self, text: str) -> EmotionScore:
        """Detect only emotions, optimized for speed"""
        if not self.is_loaded:
            await self.load_model()
        
        emotion_result = self.emotion_model(text[:512])
        return self._parse_emotion_output(emotion_result)


class ToneAnalyzer(TextSentimentAnalyzer):
    """
Specialized tone analyzer"""
    
    def __init__(self, device: str = "auto"):
        super().__init__(device=device)
    
    async def analyze_tone_only(self, text: str) -> ToneAnalysisResult:
        """Analyze only tone characteristics"""
        return await self._analyze_tone(text)


# Export main classes
__all__ = [
    'SentimentAnalyzer',
    'TextSentimentAnalyzer',
    'MultiModalSentimentAnalyzer',
    'EmotionDetector',
    'ToneAnalyzer',
    'SentimentAnalysisResult',
    'SentimentScore',
    'EmotionScore',
    'ToneAnalysisResult',
    'SentimentLabel',
    'EmotionLabel',
    'IntensityLevel',
    'ModalityType'
]
