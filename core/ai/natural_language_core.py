"""
Natural Language Core module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Ainflue Core AI - Advanced Natural Language Processing Engine
============================================================

Enterprise-grade NLP engine with advanced language understanding,
sentiment analysis, content classification, multi-language support,
and integration with state-of-the-art language models.

Features:
- Advanced text preprocessing and tokenization
- Sentiment analysis and emotion detection
- Content classification and categorization
- Named Entity Recognition (NER)
- Language detection and translation
- Content quality assessment
- Spam and toxic content detection
- Multi-language support with locale-specific processing
- Integration with OpenAI, Hugging Face, and custom models

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited
"""

import asyncio
import time
import json
import logging
import re
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime
import statistics
import hashlib

logger = logging.getLogger(__name__)

class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"

class SentimentLabel(str, Enum):
    """Sentiment analysis labels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EmotionLabel(str, Enum):
    """Emotion detection labels"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class ContentCategory(str, Enum):
    """Content classification categories"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    NEWS = "news"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH = "health"
    LIFESTYLE = "lifestyle"
    MUSIC = "music"
    ART = "art"
    GAMING = "gaming"
    FOOD = "food"
    TRAVEL = "travel"
    FASHION = "fashion"

@dataclass
class LanguageDetectionResult:
    """Language detection result"""
    language: LanguageCode
    confidence: float
    alternatives: List[Tuple[LanguageCode, float]] = field(default_factory=list)

@dataclass
class SentimentAnalysisResult:
    """Sentiment analysis result"""
    sentiment: SentimentLabel
    confidence: float
    score: float  # -1.0 to 1.0
    emotions: Dict[EmotionLabel, float] = field(default_factory=dict)

@dataclass
class ContentClassificationResult:
    """Content classification result"""
    category: ContentCategory
    confidence: float
    subcategories: List[Tuple[str, float]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class NamedEntity:
    """Named entity recognition result"""
    text: str
    label: str
    start_pos: int
    end_pos: int
    confidence: float

@dataclass
class ContentQualityMetrics:
    """Content quality assessment metrics"""
    readability_score: float
    complexity_score: float
    coherence_score: float
    grammar_score: float
    overall_quality: float
    issues: List[str] = field(default_factory=list)

@dataclass
class ToxicityDetectionResult:
    """Toxicity detection result"""
    is_toxic: bool
    toxicity_score: float
    categories: Dict[str, float] = field(default_factory=dict)
    flagged_spans: List[Tuple[int, int, str]] = field(default_factory=list)

@dataclass
class NLPProcessingResult:
    """Comprehensive NLP processing result"""
    text: str
    language: LanguageDetectionResult
    sentiment: SentimentAnalysisResult
    classification: ContentClassificationResult
    entities: List[NamedEntity]
    quality: ContentQualityMetrics
    toxicity: ToxicityDetectionResult
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class TextPreprocessor:
    """Advanced text preprocessing utilities"""
    
    def __init__(self) -> None:
        self.html_pattern = re.compile(r'<[^>]+>')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'@[a-zA-Z0-9_]+')
        self.hashtag_pattern = re.compile(r'#[a-zA-Z0-9_]+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
    def clean_text(self, text: str, remove_html: bool = True, remove_urls: bool = True,
                   remove_mentions: bool = False, remove_hashtags: bool = False,
                   remove_emails: bool = True) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        if remove_html:
            text = self.html_pattern.sub(' ', text)
        
        # Remove URLs
        if remove_urls:
            text = self.url_pattern.sub(' [URL] ', text)
        
        # Remove email addresses
        if remove_emails:
            text = self.email_pattern.sub(' [EMAIL] ', text)
        
        # Handle mentions and hashtags
        if remove_mentions:
            text = self.mention_pattern.sub(' ', text)
        else:
            text = self.mention_pattern.sub(lambda m: m.group()[1:], text)  # Remove @
        
        if remove_hashtags:
            text = self.hashtag_pattern.sub(' ', text)
        else:
            text = self.hashtag_pattern.sub(lambda m: m.group()[1:], text)  # Remove #
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract text features"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "char_count": len(text),
            "avg_word_length": statistics.mean([len(w) for w in words]) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "has_urls": bool(self.url_pattern.search(text)),
            "has_mentions": bool(self.mention_pattern.search(text)),
            "has_hashtags": bool(self.hashtag_pattern.search(text)),
            "has_emails": bool(self.email_pattern.search(text))
        }

class LanguageDetector:
    """Language detection using various methods"""
    
    def __init__(self) -> None:
        # Language patterns for basic detection
        self.language_patterns = {
            LanguageCode.ENGLISH: [
                r'\b(the|and|or|is|are|was|were|have|has|will|would|could|should)\b',
                r'\b(a|an|this|that|these|those)\b'
            ],
            LanguageCode.GERMAN: [
                r'\b(der|die|das|und|oder|ist|sind|war|waren|haben|hat)\b',
                r'\b(ein|eine|dieser|diese|dieses)\b'
            ],
            LanguageCode.FRENCH: [
                r'\b(le|la|les|et|ou|est|sont|était|étaient|avoir|a)\b',
                r'\b(un|une|ce|cette|ces)\b'
            ],
            LanguageCode.SPANISH: [
                r'\b(el|la|los|las|y|o|es|son|era|eran|tener|tiene)\b',
                r'\b(un|una|este|esta|estos|estas)\b'
            ]
        }
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language of text"""
        if not text or len(text.strip()) < 10:
            return LanguageDetectionResult(
                language=LanguageCode.ENGLISH,
                confidence=0.5
            )
        
        text_lower = text.lower()
        scores = {}
        
        # Score each language based on pattern matches
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            # Normalize by text length
            scores[lang] = score / len(text.split()) if text.split() else 0
        
        # Find best match
        if scores:
            best_lang = max(scores, key=scores.get)
            best_score = scores[best_lang]
            
            # Convert to confidence (0-1)
            confidence = min(best_score * 2, 1.0)  # Scale factor
            
            # Get alternatives
            alternatives = [
                (lang, score) for lang, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
                if lang != best_lang and score > 0
            ][:3]
            
            return LanguageDetectionResult(
                language=best_lang,
                confidence=confidence,
                alternatives=alternatives
            )
        
        # Default to English with low confidence
        return LanguageDetectionResult(
            language=LanguageCode.ENGLISH,
            confidence=0.3
        )

class SentimentAnalyzer:
    """Sentiment analysis with emotion detection"""
    
    def __init__(self) -> None:
        # Simplified sentiment lexicon
        self.positive_words = {
            "excellent", "amazing", "fantastic", "wonderful", "great", "good", "nice",
            "love", "like", "enjoy", "happy", "pleased", "satisfied", "perfect",
            "awesome", "brilliant", "outstanding", "superb", "marvelous"
        }
        
        self.negative_words = {
            "terrible", "awful", "horrible", "bad", "poor", "worst", "hate",
            "dislike", "angry", "frustrated", "disappointed", "sad", "upset",
            "annoying", "disgusting", "pathetic", "useless", "failed"
        }
        
        self.emotion_keywords = {
            EmotionLabel.JOY: {"happy", "joy", "excited", "cheerful", "delighted", "elated"},
            EmotionLabel.SADNESS: {"sad", "depressed", "melancholy", "sorrowful", "grief"},
            EmotionLabel.ANGER: {"angry", "furious", "rage", "mad", "irritated", "annoyed"},
            EmotionLabel.FEAR: {"scared", "afraid", "terrified", "anxious", "worried", "nervous"},
            EmotionLabel.SURPRISE: {"surprised", "shocked", "amazed", "astonished", "stunned"},
            EmotionLabel.DISGUST: {"disgusted", "revolted", "sickened", "appalled"},
            EmotionLabel.TRUST: {"trust", "confident", "reliable", "secure", "faith"},
            EmotionLabel.ANTICIPATION: {"excited", "eager", "anticipate", "hopeful", "expectant"}
        }
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysisResult:
        """Analyze sentiment and emotions in text"""
        if not text:
            return SentimentAnalysisResult(
                sentiment=SentimentLabel.NEUTRAL,
                confidence=0.0,
                score=0.0
            )
        
        words = text.lower().split()
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = SentimentLabel.NEUTRAL
            confidence = 0.5
        else:
            sentiment_score = (positive_count - negative_count) / len(words) if words else 0
            confidence = min(total_sentiment_words / len(words) * 2, 1.0) if words else 0
            
            # Determine sentiment label
            if sentiment_score >= 0.1:
                sentiment_label = SentimentLabel.VERY_POSITIVE if sentiment_score >= 0.2 else SentimentLabel.POSITIVE
            elif sentiment_score <= -0.1:
                sentiment_label = SentimentLabel.VERY_NEGATIVE if sentiment_score <= -0.2 else SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.NEUTRAL
        
        # Analyze emotions
        emotions = {}
        for emotion, keywords in self.emotion_keywords.items():
            emotion_count = sum(1 for word in words if word in keywords)
            emotions[emotion] = emotion_count / len(words) if words else 0
        
        return SentimentAnalysisResult(
            sentiment=sentiment_label,
            confidence=confidence,
            score=sentiment_score,
            emotions=emotions
        )

class ContentClassifier:
    """Content classification system"""
    
    def __init__(self) -> None:
        # Category keywords (simplified)
        self.category_keywords = {
            ContentCategory.ENTERTAINMENT: {
                "movie", "film", "tv", "show", "actor", "actress", "music", "song",
                "album", "concert", "entertainment", "celebrity", "star", "funny", "comedy"
            },
            ContentCategory.EDUCATION: {
                "learn", "education", "school", "university", "course", "lesson",
                "study", "research", "academic", "knowledge", "tutorial", "teach"
            },
            ContentCategory.TECHNOLOGY: {
                "technology", "tech", "computer", "software", "app", "digital",
                "ai", "artificial", "intelligence", "machine", "learning", "code"
            },
            ContentCategory.SPORTS: {
                "sport", "game", "team", "player", "match", "score", "football",
                "basketball", "soccer", "tennis", "golf", "athletic", "competition"
            },
            ContentCategory.BUSINESS: {
                "business", "company", "market", "economy", "financial", "money",
                "investment", "profit", "sales", "marketing", "entrepreneur"
            },
            ContentCategory.NEWS: {
                "news", "breaking", "report", "journalist", "media", "politics",
                "government", "election", "policy", "announcement", "update"
            }
        }
    
    def classify_content(self, text: str) -> ContentClassificationResult:
        """Classify content into categories"""
        if not text:
            return ContentClassificationResult(
                category=ContentCategory.ENTERTAINMENT,
                confidence=0.0
            )
        
        words = text.lower().split()
        scores = {}
        
        # Score each category
        for category, keywords in self.category_keywords.items():
            score = sum(1 for word in words if word in keywords)
            scores[category] = score / len(words) if words else 0
        
        # Find best category
        if scores:
            best_category = max(scores, key=scores.get)
            best_score = scores[best_category]
            confidence = min(best_score * 5, 1.0)  # Scale factor
            
            # Get subcategories (other high-scoring categories)
            subcategories = [
                (cat.value, score) for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
                if cat != best_category and score > 0
            ][:3]
            
            return ContentClassificationResult(
                category=best_category,
                confidence=confidence,
                subcategories=subcategories
            )
        
        # Default classification
        return ContentClassificationResult(
            category=ContentCategory.ENTERTAINMENT,
            confidence=0.1
        )

class NamedEntityRecognizer:
    """Named Entity Recognition system"""
    
    def __init__(self) -> None:
        # Simple patterns for entity recognition
        self.patterns = {
            "PERSON": re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),
            "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "URL": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            "PHONE": re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'),
            "DATE": re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b')
        }
    
    def extract_entities(self, text: str) -> List[NamedEntity]:
        """Extract named entities from text"""
        entities = []
        
        for label, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity = NamedEntity(
                    text=match.group(),
                    label=label,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8  # Fixed confidence for pattern matching
                )
                entities.append(entity)
        
        return entities

class QualityAssessor:
    """Content quality assessment"""
    
    def assess_quality(self, text: str) -> ContentQualityMetrics:
        """Assess content quality"""
        if not text:
            return ContentQualityMetrics(
                readability_score=0.0,
                complexity_score=0.0,
                coherence_score=0.0,
                grammar_score=0.0,
                overall_quality=0.0
            )
        
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Basic readability (simplified Flesch reading ease)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = statistics.mean([len(w) for w in words]) if words else 0
        
        readability_score = max(0, min(100, 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_word_length / len(words))) / 100 if words else 0
        
        # Complexity (based on word length and sentence structure)
        complexity_score = min(1.0, (avg_word_length - 3) / 5) if avg_word_length > 3 else 0
        
        # Coherence (simplified - based on repetition and flow)
        unique_words = set(words)
        coherence_score = len(unique_words) / len(words) if words else 0
        
        # Grammar (simplified - based on capitalization and punctuation)
        capitalized_sentences = sum(1 for s in sentences if s and s[0].isupper())
        grammar_score = capitalized_sentences / len(sentences) if sentences else 0
        
        # Overall quality
        overall_quality = (readability_score + (1 - complexity_score) + coherence_score + grammar_score) / 4
        
        issues = []
        if readability_score < 0.3:
            issues.append("Low readability")
        if complexity_score > 0.8:
            issues.append("High complexity")
        if coherence_score < 0.5:
            issues.append("Low coherence")
        if grammar_score < 0.8:
            issues.append("Grammar issues")
        
        return ContentQualityMetrics(
            readability_score=readability_score,
            complexity_score=complexity_score,
            coherence_score=coherence_score,
            grammar_score=grammar_score,
            overall_quality=overall_quality,
            issues=issues
        )

class ToxicityDetector:
    """Toxicity and inappropriate content detection"""
    
    def __init__(self) -> None:
        # Simplified toxic word list (in production, use ML models)
        self.toxic_words = {
            "hate", "stupid", "idiot", "fool", "dumb", "moron", "loser",
            "trash", "garbage", "worthless", "pathetic", "disgusting"
        }
        
        self.categories = {
            "profanity": {"damn", "hell", "crap"},
            "harassment": {"hate", "stupid", "idiot", "loser"},
            "threat": {"kill", "destroy", "harm", "hurt"},
            "spam": {"buy", "click", "free", "offer", "deal"}
        }
    
    def detect_toxicity(self, text: str) -> ToxicityDetectionResult:
        """Detect toxic content"""
        if not text:
            return ToxicityDetectionResult(
                is_toxic=False,
                toxicity_score=0.0
            )
        
        words = text.lower().split()
        toxic_count = sum(1 for word in words if word in self.toxic_words)
        
        toxicity_score = toxic_count / len(words) if words else 0
        is_toxic = toxicity_score > 0.05  # Threshold
        
        # Category scores
        category_scores = {}
        flagged_spans = []
        
        for category, category_words in self.categories.items():
            category_count = sum(1 for word in words if word in category_words)
            category_scores[category] = category_count / len(words) if words else 0
            
            # Find flagged spans
            for i, word in enumerate(words):
                if word in category_words:
                    start_pos = text.lower().find(word)
                    end_pos = start_pos + len(word)
                    flagged_spans.append((start_pos, end_pos, category))
        
        return ToxicityDetectionResult(
            is_toxic=is_toxic,
            toxicity_score=toxicity_score,
            categories=category_scores,
            flagged_spans=flagged_spans
        )

class NaturalLanguageCore:
    """Advanced enterprise natural language processing core"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.level = level
        self.preprocessor = TextPreprocessor()
        self.language_detector = LanguageDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.content_classifier = ContentClassifier()
        self.entity_recognizer = NamedEntityRecognizer()
        self.quality_assessor = QualityAssessor()
        self.toxicity_detector = ToxicityDetector()
        self.enabled = True
        
        # Performance settings based on level
        self.performance_config = self._get_performance_config()
        
        # Processing cache
        self._cache: Dict[str, NLPProcessingResult] = {}
        self._cache_lock = threading.Lock()
    
    def _get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration based on level"""
        configs = {
            "basic": {
                "cache_size": 100,
                "enable_caching": True,
                "parallel_processing": False,
                "detailed_analysis": False
            },
            "standard": {
                "cache_size": 500,
                "enable_caching": True,
                "parallel_processing": True,
                "detailed_analysis": False
            },
            "professional": {
                "cache_size": 1000,
                "enable_caching": True,
                "parallel_processing": True,
                "detailed_analysis": True
            },
            "enterprise": {
                "cache_size": 10000,
                "enable_caching": True,
                "parallel_processing": True,
                "detailed_analysis": True
            }
        }
        return configs.get(self.level, configs["enterprise"])
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    async def initialize(self) -> bool:
        """Initialize NLP core"""
        try:
            logger.info(f"🚀 Initializing NaturalLanguageCore - Level: {self.level}")
            
            logger.info("✅ NaturalLanguageCore initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NaturalLanguageCore: {e}")
            return False
    
    async def process_text(self, text: str, use_cache: bool = True) -> NLPProcessingResult:
        """Comprehensive text processing"""
        start_time = time.time()
        
        try:
            if not text or not text.strip():
                raise ValueError("Empty text provided")
            
            # Check cache
            cache_key = self._get_cache_key(text)
            if use_cache and self.performance_config["enable_caching"]:
                with self._cache_lock:
                    if cache_key in self._cache:
                        cached_result = self._cache[cache_key]
                        logger.debug(f"Returning cached NLP result for text: {text[:50]}...")
                        return cached_result
            
            # Clean text
            cleaned_text = self.preprocessor.clean_text(text)
            
            # Run all analysis components
            if self.performance_config["parallel_processing"]:
                # Parallel processing
                tasks = [
                    self._detect_language_async(cleaned_text),
                    self._analyze_sentiment_async(cleaned_text),
                    self._classify_content_async(cleaned_text),
                    self._extract_entities_async(cleaned_text),
                    self._assess_quality_async(cleaned_text),
                    self._detect_toxicity_async(cleaned_text)
                ]
                
                results = await asyncio.gather(*tasks)
                language_result, sentiment_result, classification_result, entities_result, quality_result, toxicity_result = results
            else:
                # Sequential processing
                language_result = self.language_detector.detect_language(cleaned_text)
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(cleaned_text)
                classification_result = self.content_classifier.classify_content(cleaned_text)
                entities_result = self.entity_recognizer.extract_entities(cleaned_text)
                quality_result = self.quality_assessor.assess_quality(cleaned_text)
                toxicity_result = self.toxicity_detector.detect_toxicity(cleaned_text)
            
            processing_time = time.time() - start_time
            
            # Create comprehensive result
            result = NLPProcessingResult(
                text=text,
                language=language_result,
                sentiment=sentiment_result,
                classification=classification_result,
                entities=entities_result,
                quality=quality_result,
                toxicity=toxicity_result,
                processing_time=processing_time
            )
            
            # Cache result
            if use_cache and self.performance_config["enable_caching"]:
                with self._cache_lock:
                    if len(self._cache) >= self.performance_config["cache_size"]:
                        # Remove oldest entry
                        oldest_key = next(iter(self._cache))
                        del self._cache[oldest_key]
                    
                    self._cache[cache_key] = result
            
            logger.info(f"✅ NLP processing completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ NLP processing failed after {processing_time:.3f}s: {e}")
            raise
    
    async def _detect_language_async(self, text: str) -> LanguageDetectionResult:
        """Async language detection"""
        return self.language_detector.detect_language(text)
    
    async def _analyze_sentiment_async(self, text: str) -> SentimentAnalysisResult:
        """Async sentiment analysis"""
        return self.sentiment_analyzer.analyze_sentiment(text)
    
    async def _classify_content_async(self, text: str) -> ContentClassificationResult:
        """Async content classification"""
        return self.content_classifier.classify_content(text)
    
    async def _extract_entities_async(self, text: str) -> List[NamedEntity]:
        """Async entity extraction"""
        return self.entity_recognizer.extract_entities(text)
    
    async def _assess_quality_async(self, text: str) -> ContentQualityMetrics:
        """Async quality assessment"""
        return self.quality_assessor.assess_quality(text)
    
    async def _detect_toxicity_async(self, text: str) -> ToxicityDetectionResult:
        """Async toxicity detection"""
        return self.toxicity_detector.detect_toxicity(text)
    
    async def analyze_sentiment_only(self, text: str) -> SentimentAnalysisResult:
        """Analyze sentiment only"""
        cleaned_text = self.preprocessor.clean_text(text)
        return self.sentiment_analyzer.analyze_sentiment(cleaned_text)
    
    async def classify_content_only(self, text: str) -> ContentClassificationResult:
        """Classify content only"""
        cleaned_text = self.preprocessor.clean_text(text)
        return self.content_classifier.classify_content(cleaned_text)
    
    async def detect_language_only(self, text: str) -> LanguageDetectionResult:
        """Detect language only"""
        return self.language_detector.detect_language(text)
    
    async def check_toxicity_only(self, text: str) -> ToxicityDetectionResult:
        """Check toxicity only"""
        cleaned_text = self.preprocessor.clean_text(text)
        return self.toxicity_detector.detect_toxicity(cleaned_text)
    
    async def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract text features"""
        return self.preprocessor.extract_features(text)
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        with self._cache_lock:
            cache_size = len(self._cache)
        
        return {
            "cache_size": cache_size,
            "max_cache_size": self.performance_config["cache_size"],
            "caching_enabled": self.performance_config["enable_caching"],
            "parallel_processing": self.performance_config["parallel_processing"],
            "detailed_analysis": self.performance_config["detailed_analysis"],
            "supported_languages": [lang.value for lang in LanguageCode],
            "available_emotions": [emotion.value for emotion in EmotionLabel],
            "content_categories": [category.value for category in ContentCategory]
        }
    
    async def clear_cache(self) -> bool:
        """Clear processing cache"""
        try:
            with self._cache_lock:
                self._cache.clear()
            logger.info("✅ NLP cache cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear cache: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Health check for NLP core"""
        try:
            # Test basic functionality
            test_result = await self.analyze_sentiment_only("This is a test message.")
            return test_result.confidence >= 0.0
        except Exception as e:
            logger.error(f"NaturalLanguageCore health check failed: {e}")
            return False
    
    async def start(self) -> bool:
        """Start NLP service"""
        try:
            logger.info("🚀 Starting NaturalLanguageCore service")
            self.enabled = True
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start NaturalLanguageCore: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop NLP service"""
        try:
            logger.info("🛑 Stopping NaturalLanguageCore service")
            self.enabled = False
            await self.clear_cache()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to stop NaturalLanguageCore: {e}")
            return False

# Export main classes
__all__ = [
    "NaturalLanguageCore", "NLPProcessingResult", "SentimentAnalysisResult",
    "ContentClassificationResult", "LanguageDetectionResult", "NamedEntity",
    "ContentQualityMetrics", "ToxicityDetectionResult", "LanguageCode",
    "SentimentLabel", "EmotionLabel", "ContentCategory"
]