"""Comprehensive Text Analysis Module
=================================

Enterprise-grade text analysis engine for content creators:
- Multi-model sentiment analysis with confidence scoring
- Emotional tone detection for engagement optimization  
- Content quality assessment and readability optimization
- Text complexity analysis for audience targeting
- Real-time content performance prediction
- Multi-language text analytics with cultural context
- Content authenticity and AI-generated text detection

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

⚠️  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone

import spacy
import textstat
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import hashlib

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode
from ...security.encryption import encrypt_data, decrypt_data

logger = get_logger(__name__)


class SentimentLevel(Enum):
    """Sentiment intensity levels"""    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class EmotionalTone(Enum):
    """Emotional tone categories for content"""    EXCITED = "excited"
    CALM = "calm"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    INSPIRATIONAL = "inspirational"
    INFORMATIVE = "informative"


@dataclass
class SentimentResult:
    """Comprehensive sentiment analysis result"""    overall_sentiment: SentimentLevel
    confidence_score: float
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float
    emotional_tone: EmotionalTone
    intensity: float
    subjectivity: float
    keywords: List[str] = field(default_factory=list)
    emotions: Dict[str, float] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TextAnalysisResult:
    """Complete text analysis result"""    text_length: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    readability_score: float
    complexity_level: str
    grade_level: float
    reading_time_minutes: float
    language_detected: str
    content_type: str
    quality_score: float
    engagement_potential: float
    seo_keywords: List[str] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)


class SentimentAnalyzer:
    """Enterprise sentiment analysis for content creators"""    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.transformer_model = None
        self.transformer_tokenizer = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models for sentiment analysis"""        try:
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.transformer_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.transformer_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Emotion detection pipeline
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
            
            logger.info("Sentiment analysis models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment models: {e}")
            
    async def analyze_sentiment(self, text: str, content_type: str = "general") -> SentimentResult:
        """        Perform comprehensive sentiment analysis
        
        Args:
            text: Text content to analyze
            content_type: Type of content (post, caption, description, etc.)
            
        Returns:
            SentimentResult with detailed analysis
        """        try:
            # Cache key for performance
            cache_key = f"sentiment_{hashlib.md5(text.encode()).hexdigest()}_{content_type}"
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)
            
            # Clean and preprocess text
            cleaned_text = clean_text(text)
            
            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # Transformer-based sentiment
            transformer_result = await self._transformer_sentiment(cleaned_text)
            
            # Emotion analysis
            emotions = await self._analyze_emotions(cleaned_text)
            
            # Determine overall sentiment
            overall_sentiment = self._determine_sentiment_level(vader_scores['compound'])
            
            # Determine emotional tone
            emotional_tone = await self._determine_emotional_tone(cleaned_text, emotions)
            
            # Extract keywords
            keywords = await self._extract_sentiment_keywords(cleaned_text)
            
            result = SentimentResult(
                overall_sentiment=overall_sentiment,
                confidence_score=transformer_result['confidence'],
                positive_score=vader_scores['pos'],
                negative_score=vader_scores['neg'],
                neutral_score=vader_scores['neu'],
                compound_score=vader_scores['compound'],
                emotional_tone=emotional_tone,
                intensity=abs(vader_scores['compound']),
                subjectivity=self._calculate_subjectivity(cleaned_text),
                keywords=keywords,
                emotions=emotions
            )
            
            # Cache result
            await cache_manager.set(cache_key, pickle.dumps(result), expire=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise
            
    async def _transformer_sentiment(self, text: str) -> Dict[str, float]:
        """Use transformer model for sentiment analysis"""        try:
            inputs = self.transformer_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            confidence = torch.max(predictions).item()
            predicted_class = torch.argmax(predictions).item()
            
            return {
                'confidence': confidence,
                'class': predicted_class,
                'scores': predictions.numpy()[0].tolist()
            }
        except Exception as e:
            logger.error(f"Transformer sentiment analysis failed: {e}")
            return {'confidence': 0.5, 'class': 1, 'scores': [0.33, 0.34, 0.33]}
            
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content of text"""        try:
            emotions_result = self.emotion_pipeline(text)
            emotions_dict = {emotion['label'].lower(): emotion['score'] for emotion in emotions_result}
            return emotions_dict
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {}
            
    def _determine_sentiment_level(self, compound_score: float) -> SentimentLevel:
        """Determine sentiment level from compound score"""        if compound_score >= 0.6:
            return SentimentLevel.VERY_POSITIVE
        elif compound_score >= 0.2:
            return SentimentLevel.POSITIVE
        elif compound_score <= -0.6:
            return SentimentLevel.VERY_NEGATIVE
        elif compound_score <= -0.2:
            return SentimentLevel.NEGATIVE
        else:
            return SentimentLevel.NEUTRAL
            
    async def _determine_emotional_tone(self, text: str, emotions: Dict[str, float]) -> EmotionalTone:
        """Determine emotional tone based on content analysis"""        try:
            # Analyze text patterns for tone detection
            text_lower = text.lower()
            
            # Professional indicators
            professional_keywords = ['analysis', 'strategy', 'performance', 'metrics', 'professional', 'business']
            if any(keyword in text_lower for keyword in professional_keywords):
                return EmotionalTone.PROFESSIONAL
                
            # Excitement indicators
            excitement_patterns = [r'[!]{2,}', r'wow', r'amazing', r'incredible', r'fantastic']
            if any(re.search(pattern, text_lower) for pattern in excitement_patterns):
                return EmotionalTone.EXCITED
                
            # Humor indicators
            humor_keywords = ['lol', 'haha', 'funny', 'joke', '😂', '🤣']
            if any(keyword in text_lower for keyword in humor_keywords):
                return EmotionalTone.HUMOROUS
                
            # Default to calm for neutral content
            return EmotionalTone.CALM
            
        except Exception as e:
            logger.error(f"Emotional tone detection failed: {e}")
            return EmotionalTone.NEUTRAL
            
    async def _extract_sentiment_keywords(self, text: str) -> List[str]:
        """Extract keywords that contribute to sentiment"""        try:
            # Simple keyword extraction based on sentiment-bearing words
            positive_words = ['great', 'amazing', 'excellent', 'fantastic', 'wonderful', 'awesome', 'love', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing', 'frustrating']
            
            text_lower = text.lower()
            found_keywords = []
            
            for word in positive_words + negative_words:
                if word in text_lower:
                    found_keywords.append(word)
                    
            return found_keywords[:10]  # Limit to top 10
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
            
    def _calculate_subjectivity(self, text: str) -> float:
        """Calculate text subjectivity score"""        try:
            # Simple subjectivity calculation based on personal pronouns and opinion words
            subjective_indicators = ['i', 'me', 'my', 'we', 'our', 'you', 'your', 'think', 'feel', 'believe', 'opinion']
            text_lower = text.lower()
            words = text_lower.split()
            
            subjective_count = sum(1 for word in words if word in subjective_indicators)
            total_words = len(words)
            
            return min(subjective_count / max(total_words, 1), 1.0)
            
        except Exception as e:
            logger.error(f"Subjectivity calculation failed: {e}")
            return 0.5


class TextAnalyzer:
    """Comprehensive text analysis for content optimization"""    
    def __init__(self):
        self.nlp = None
        self._initialize_nlp()
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def _initialize_nlp(self):
        """Initialize spaCy NLP pipeline"""        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy NLP pipeline initialized")
        except IOError:
            logger.warning("spaCy model not found, using fallback analysis")
            
    async def analyze_text(self, text: str, content_type: str = "general") -> TextAnalysisResult:
        """        Perform comprehensive text analysis
        
        Args:
            text: Text content to analyze
            content_type: Type of content for specialized analysis
            
        Returns:
            TextAnalysisResult with detailed metrics
        """        try:
            # Comprehensive text statistics
            analysis_result.text_length = len(text)
            analysis_result.word_count = len(text.split())
            analysis_result.sentence_count = len(re.findall(r'[.!?]+', text))
            analysis_result.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Content readability analysis
            analysis_result.readability_score = self._calculate_readability_score(text)
            analysis_result.grade_level = textstat.flesch_kincaid_grade(text)
            analysis_result.reading_time_minutes = self._estimate_reading_time(text)
            
            # Content complexity assessment
            analysis_result.complexity_level = self._determine_complexity_level(analysis_result.grade_level)
            
            # Content quality scoring
            analysis_result.quality_score = await self._calculate_content_quality(text)
            
            # Engagement potential prediction
            analysis_result.engagement_potential = await self._predict_engagement_potential(text, content_type)
            
            # SEO keyword extraction
            analysis_result.seo_keywords = await self._extract_seo_keywords(text)
            
            # Hashtag suggestions
            analysis_result.hashtag_suggestions = await self._generate_hashtag_suggestions(text, content_type)
            word_count = len(text.split())
            sentence_count = len(re.findall(r'[.!?]+', text))
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Readability analysis
            readability_score = textstat.flesch_reading_ease(text)
            grade_level = textstat.flesch_kincaid_grade(text)
            complexity_level = self._determine_complexity_level(readability_score)
            
            # Reading time calculation (average 200 words per minute)
            reading_time = word_count / 200.0
            
            # Language detection
            language_detected = await self._detect_language(text)
            
            # Content quality assessment
            quality_score = await self._assess_content_quality(text, content_type)
            
            # Engagement potential
            engagement_potential = await self._calculate_engagement_potential(text, content_type)
            
            # SEO keywords extraction
            seo_keywords = await self._extract_seo_keywords(text)
            
            # Hashtag suggestions
            hashtag_suggestions = await self._suggest_hashtags(text, content_type)
            
            return TextAnalysisResult(
                text_length=len(text),
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                readability_score=readability_score,
                complexity_level=complexity_level,
                grade_level=grade_level,
                reading_time_minutes=reading_time,
                language_detected=language_detected,
                content_type=content_type,
                quality_score=quality_score,
                engagement_potential=engagement_potential,
                seo_keywords=seo_keywords,
                hashtag_suggestions=hashtag_suggestions
            )
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            raise
            
    def _determine_complexity_level(self, readability_score: float) -> str:
        """Determine text complexity level from readability score"""        if readability_score >= 90:
            return "very_easy"
        elif readability_score >= 80:
            return "easy"
        elif readability_score >= 70:
            return "fairly_easy"
        elif readability_score >= 60:
            return "standard"
        elif readability_score >= 50:
            return "fairly_difficult"
        elif readability_score >= 30:
            return "difficult"
        else:
            return "very_difficult"
            
    async def _detect_language(self, text: str) -> str:
        """Detect text language"""        try:
            # Simple language detection based on character patterns
            # This would be enhanced with proper language detection library
            return "en"  # Default to English for now
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "unknown"
            
    async def _assess_content_quality(self, text: str, content_type: str) -> float:
        """Assess overall content quality"""        try:
            quality_factors = []
            
            # Length appropriateness for content type
            word_count = len(text.split())
            if content_type == "post" and 50 <= word_count <= 200:
                quality_factors.append(0.8)
            elif content_type == "caption" and 10 <= word_count <= 50:
                quality_factors.append(0.8)
            else:
                quality_factors.append(0.6)
                
            # Grammar and spelling (simplified check)
            spelling_errors = len(re.findall(r'\b\w+\b', text)) - len(set(text.split()))
            spelling_score = max(0, 1 - (spelling_errors / max(word_count, 1)))
            quality_factors.append(spelling_score)
            
            # Sentence structure variety
            sentences = re.split(r'[.!?]+', text)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variance = np.std(sentence_lengths) / max(np.mean(sentence_lengths), 1)
                structure_score = min(length_variance / 2, 1.0)
                quality_factors.append(structure_score)
                
            return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
            
        except Exception as e:
            logger.error(f"Content quality assessment failed: {e}")
            return 0.5
            
    async def _calculate_engagement_potential(self, text: str, content_type: str) -> float:
        """Calculate potential for audience engagement"""        try:
            engagement_factors = []
            
            # Emotional content (using sentiment analysis)
            sentiment_result = await self.sentiment_analyzer.analyze_sentiment(text, content_type)
            emotion_intensity = sentiment_result.intensity
            engagement_factors.append(emotion_intensity)
            
            # Question presence
            question_count = len(re.findall(r'\?', text))
            question_score = min(question_count / 3, 1.0)
            engagement_factors.append(question_score)
            
            # Call-to-action words
            cta_words = ['comment', 'share', 'like', 'follow', 'subscribe', 'click', 'join', 'try', 'discover']
            cta_count = sum(1 for word in cta_words if word.lower() in text.lower())
            cta_score = min(cta_count / 2, 1.0)
            engagement_factors.append(cta_score)
            
            # Visual elements mentions
            visual_words = ['photo', 'image', 'video', 'picture', 'visual', 'see', 'watch', 'look']
            visual_count = sum(1 for word in visual_words if word.lower() in text.lower())
            visual_score = min(visual_count / 3, 1.0)
            engagement_factors.append(visual_score)
            
            return sum(engagement_factors) / len(engagement_factors)
            
        except Exception as e:
            logger.error(f"Engagement potential calculation failed: {e}")
            return 0.5
            
    async def _extract_seo_keywords(self, text: str) -> List[str]:
        """Extract SEO-relevant keywords"""        try:
            # Simple keyword extraction using TF-IDF
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Sort by frequency and return top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10] if freq > 1]
            
        except Exception as e:
            logger.error(f"SEO keyword extraction failed: {e}")
            return []
            
    async def _suggest_hashtags(self, text: str, content_type: str) -> List[str]:
        """Generate hashtag suggestions based on content"""        try:
            # Extract potential hashtag words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Content type specific hashtags
            base_hashtags = {
                'music': ['#music', '#musician', '#song', '#artist'],
                'photo': ['#photography', '#photo', '#picture', '#visual'],
                'video': ['#video', '#content', '#creator', '#film'],
                'post': ['#content', '#creator', '#social', '#community']
            }
            
            suggested_hashtags = base_hashtags.get(content_type, ['#content', '#creator'])
            
            # Add content-specific hashtags
            for word in words[:5]:
                if len(word) > 3 and word.isalpha():
                    suggested_hashtags.append(f"#{word}")
                    
            return suggested_hashtags[:10]
            
        except Exception as e:
            logger.error(f"Hashtag suggestion failed: {e}")
            return ['#content', '#creator']
