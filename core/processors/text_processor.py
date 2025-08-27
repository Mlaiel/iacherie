"""
Text Processor Module - IA-Influencer-Agent Platform

Industrial-grade text processing engine for content creators and influencers.
Handles text analysis, enhancement, conversion, and AI-powered features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""

import asyncio
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import time

# Text processing imports
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.sentiment import SentimentIntensityAnalyzer
    import textstat
    import langdetect
    from textblob import TextBlob
    import spacy
    TEXT_LIBS_AVAILABLE = True
except ImportError:
    TEXT_LIBS_AVAILABLE = False

# AI imports for advanced text analysis
try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModel
    import openai
    AI_LIBS_AVAILABLE = True
except ImportError:
    AI_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextFormat(str, Enum):
    """Supported text formats"""
    PLAIN = "plain"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    RTF = "rtf"
    DOCX = "docx"


class TextQuality(str, Enum):
    """Text quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROFESSIONAL = "professional"


class TextProcessingType(str, Enum):
    """Types of text processing"""
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    CONVERSION = "conversion"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    KEYWORD_EXTRACTION = "keyword_extraction"
    ENTITY_RECOGNITION = "entity_recognition"
    READABILITY_ANALYSIS = "readability_analysis"
    STYLE_ANALYSIS = "style_analysis"
    PLAGIARISM_CHECK = "plagiarism_check"
    SEO_OPTIMIZATION = "seo_optimization"


@dataclass
class TextProcessingConfig:
    """Configuration for text processing"""
    target_format: TextFormat = TextFormat.PLAIN
    target_quality: TextQuality = TextQuality.HIGH
    max_length: int = 1000000  # 1M characters
    enable_ai_analysis: bool = True
    enable_sentiment_analysis: bool = True
    enable_entity_recognition: bool = True
    enable_keyword_extraction: bool = True
    enable_readability_analysis: bool = True
    enable_style_analysis: bool = True
    enable_language_detection: bool = True
    enable_translation: bool = True
    enable_summarization: bool = True
    enable_seo_optimization: bool = True
    enable_plagiarism_check: bool = False
    default_language: str = "en"
    max_summary_length: int = 500
    keyword_count: int = 10
    entity_confidence_threshold: float = 0.8
    sentiment_threshold: float = 0.1


@dataclass
class TextMetadata:
    """Comprehensive text metadata"""
    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[str] = None
    encoding: Optional[str] = None
    reading_time_minutes: Optional[float] = None
    readability_scores: Optional[Dict[str, float]] = None
    complexity_level: Optional[str] = None
    tone: Optional[str] = None
    formality_level: Optional[str] = None
    domain: Optional[str] = None
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    keywords: List[str] = field(default_factory=list)


@dataclass
class SentimentAnalysis:
    """Sentiment analysis results"""
    overall_sentiment: str  # positive, negative, neutral
    confidence: float
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    emotions: Dict[str, float] = field(default_factory=dict)
    sentiment_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class EntityRecognition:
    """Named entity recognition results"""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    entity_types: Dict[str, int] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class KeywordExtraction:
    """Keyword extraction results"""
    keywords: List[str] = field(default_factory=list)
    keyphrases: List[str] = field(default_factory=list)
    keyword_scores: Dict[str, float] = field(default_factory=dict)
    tf_idf_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class ReadabilityAnalysis:
    """Readability analysis results"""
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    smog_index: Optional[float] = None
    automated_readability_index: Optional[float] = None
    coleman_liau_index: Optional[float] = None
    reading_level: Optional[str] = None
    estimated_reading_time: Optional[float] = None


@dataclass
class StyleAnalysis:
    """Writing style analysis results"""
    writing_style: Optional[str] = None
    tone: Optional[str] = None
    formality_level: Optional[str] = None
    complexity_score: Optional[float] = None
    vocabulary_richness: Optional[float] = None
    sentence_variety: Optional[float] = None
    passive_voice_ratio: Optional[float] = None
    average_sentence_length: Optional[float] = None


@dataclass
class TextFeatures:
    """Advanced text features extracted via AI"""
    sentiment_analysis: Optional[SentimentAnalysis] = None
    entity_recognition: Optional[EntityRecognition] = None
    keyword_extraction: Optional[KeywordExtraction] = None
    readability_analysis: Optional[ReadabilityAnalysis] = None
    style_analysis: Optional[StyleAnalysis] = None
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    content_type: Optional[str] = None
    target_audience: Optional[str] = None
    seo_score: Optional[float] = None
    uniqueness_score: Optional[float] = None
    quality_score: Optional[float] = None


@dataclass
class TextAnalysisResult:
    """Result of text analysis"""
    success: bool
    metadata: Optional[TextMetadata] = None
    features: Optional[TextFeatures] = None
    processed_text: Optional[str] = None
    fingerprint: Optional[str] = None
    semantic_hash: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None


class TextProcessor:
    """
    📝 ENTERPRISE TEXT PROCESSOR
    
    Industrial-grade text processing engine with advanced AI capabilities
    for content creators, writers, and influencers.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[TextProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or TextProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.TextProcessor")
        
        # Initialize AI models
        self._sentiment_analyzer = None
        self._ner_model = None
        self._summarizer = None
        self._translator = None
        self._nlp_model = None
        self._initialized = False
        
        if not TEXT_LIBS_AVAILABLE:
            self.logger.warning("Text processing libraries not available")
        
        if not AI_LIBS_AVAILABLE:
            self.logger.warning("AI libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the text processor"""
        try:
            if TEXT_LIBS_AVAILABLE:
                # Download required NLTK data
                try:
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    nltk.download('vader_lexicon', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                    nltk.download('wordnet', quiet=True)
                except:
                    self.logger.warning("Failed to download NLTK data")
                
                # Initialize NLTK sentiment analyzer
                try:
                    self._sentiment_analyzer = SentimentIntensityAnalyzer()
                except:
                    self.logger.warning("Failed to initialize NLTK sentiment analyzer")
                
                # Initialize spaCy model
                try:
                    self._nlp_model = spacy.load("en_core_web_sm")
                except:
                    self.logger.warning("spaCy model not available. Install with: python -m spacy download en_core_web_sm")
            
            if AI_LIBS_AVAILABLE and self.config.enable_ai_analysis:
                # Initialize NER model
                if self.config.enable_entity_recognition:
                    try:
                        self._ner_model = pipeline(
                            "ner",
                            model="dbmdz/bert-large-cased-finetuned-conll03-english",
                            aggregation_strategy="simple"
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not load NER model: {e}")
                
                # Initialize summarization model
                if self.config.enable_summarization:
                    try:
                        self._summarizer = pipeline(
                            "summarization",
                            model="facebook/bart-large-cnn",
                            max_length=self.config.max_summary_length,
                            min_length=50
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not load summarization model: {e}")
                
                # Initialize translation model
                if self.config.enable_translation:
                    try:
                        self._translator = pipeline(
                            "translation",
                            model="Helsinki-NLP/opus-mt-en-de"  # Example: English to German
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not load translation model: {e}")
            
            self._initialized = True
            self.logger.info("✅ Text processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize text processor: {e}")
            return False
    
    async def process(
        self,
        content: Union[str, bytes, BinaryIO],
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process text content with comprehensive analysis
        
        Args:
            content: Text content (string, bytes, or file object)
            options: Processing options
            metadata: Additional metadata
            
        Returns:
            Processing result dictionary
        """
        start_time = time.time()
        options = options or {}
        metadata = metadata or {}
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Load text
            text = await self._load_text(content)
            
            if not text:
                return {
                    "success": False,
                    "error_message": "Failed to load text content",
                    "processing_time": time.time() - start_time
                }
            
            # Extract metadata
            text_metadata = await self._extract_metadata(text)
            
            # Validate text
            validation_result = await self._validate_text(text_metadata)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error_message": validation_result["reason"],
                    "processing_time": time.time() - start_time
                }
            
            # Text enhancement
            enhanced_text = text
            if options.get("enhance", True):
                enhanced_text = await self._enhance_text(text)
            
            # Feature extraction
            features = None
            if self.config.enable_ai_analysis:
                features = await self._extract_features(enhanced_text)
            
            # Generate fingerprints
            fingerprint = await self._generate_fingerprint(enhanced_text)
            semantic_hash = await self._generate_semantic_hash(enhanced_text)
            
            # Generate tags
            tags = await self._generate_tags(
                metadata=text_metadata,
                features=features,
                text=enhanced_text
            )
            
            # Format conversion if requested
            processed_content = None
            if options.get("convert_format"):
                target_format = TextFormat(options.get("target_format", self.config.target_format))
                processed_content = await self._convert_format(enhanced_text, target_format, options)
            
            # Create analysis result
            analysis_result = TextAnalysisResult(
                success=True,
                metadata=text_metadata,
                features=features,
                processed_text=processed_content or enhanced_text,
                fingerprint=fingerprint,
                semantic_hash=semantic_hash,
                tags=tags,
                processing_time=time.time() - start_time
            )
            
            return {
                "success": True,
                "processed_content": processed_content,
                "analysis_result": analysis_result.__dict__,
                "metadata": text_metadata.__dict__,
                "quality_metrics": {
                    "quality_score": features.quality_score if features else None,
                    "uniqueness_score": features.uniqueness_score if features else None,
                    "seo_score": features.seo_score if features else None
                },
                "tags": tags,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _load_text(self, content: Union[str, bytes, BinaryIO]) -> Optional[str]:
        """Load text data from various input types"""
        try:
            if isinstance(content, str):
                return content
            elif isinstance(content, bytes):
                # Try to decode bytes
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return content.decode('latin-1')
                    except UnicodeDecodeError:
                        return content.decode('utf-8', errors='ignore')
            else:
                # File object
                content_bytes = content.read()
                if isinstance(content_bytes, str):
                    return content_bytes
                else:
                    return content_bytes.decode('utf-8', errors='ignore')
            
        except Exception as e:
            self.logger.error(f"Failed to load text: {e}")
            return None
    
    async def _extract_metadata(self, text: str) -> TextMetadata:
        """Extract comprehensive text metadata"""
        try:
            # Basic counts
            character_count = len(text)
            word_count = len(text.split())
            
            # Sentence count
            if TEXT_LIBS_AVAILABLE:
                try:
                    sentences = sent_tokenize(text)
                    sentence_count = len(sentences)
                except:
                    sentence_count = len([s for s in text.split('.') if s.strip()])
            else:
                sentence_count = len([s for s in text.split('.') if s.strip()])
            
            # Paragraph count
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Language detection
            language = None
            if self.config.enable_language_detection:
                try:
                    language = langdetect.detect(text)
                except:
                    language = self.config.default_language
            
            # Reading time estimation (average 200 words per minute)
            reading_time_minutes = word_count / 200.0
            
            # Readability scores
            readability_scores = None
            complexity_level = None
            if TEXT_LIBS_AVAILABLE and self.config.enable_readability_analysis:
                readability_scores = await self._calculate_readability_scores(text)
                complexity_level = await self._determine_complexity_level(readability_scores)
            
            # Basic tone analysis
            tone = None
            formality_level = None
            if self.config.enable_style_analysis:
                tone = await self._analyze_basic_tone(text)
                formality_level = await self._analyze_formality(text)
            
            # Extract keywords (basic)
            keywords = await self._extract_basic_keywords(text)
            
            return TextMetadata(
                character_count=character_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                language=language,
                encoding="utf-8",
                reading_time_minutes=reading_time_minutes,
                readability_scores=readability_scores,
                complexity_level=complexity_level,
                tone=tone,
                formality_level=formality_level,
                keywords=keywords,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract text metadata: {e}")
            return TextMetadata(
                character_count=len(text),
                word_count=len(text.split()),
                sentence_count=0,
                paragraph_count=0
            )
    
    async def _validate_text(self, metadata: TextMetadata) -> Dict[str, Any]:
        """Validate text against configuration constraints"""
        if metadata.character_count > self.config.max_length:
            return {
                "valid": False,
                "reason": f"Text length ({metadata.character_count}) exceeds maximum ({self.config.max_length})"
            }
        
        if metadata.character_count == 0:
            return {
                "valid": False,
                "reason": "Empty text content"
            }
        
        return {"valid": True}
    
    async def _enhance_text(self, text: str) -> str:
        """Enhance text quality through various techniques"""
        try:
            enhanced = text
            
            # Basic text cleaning
            # Remove excessive whitespace
            enhanced = re.sub(r'\s+', ' ', enhanced)
            
            # Fix common punctuation issues
            enhanced = re.sub(r'\s+([,.!?;:])', r'\1', enhanced)
            enhanced = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', enhanced)
            
            # Fix quotes
            enhanced = re.sub(r'"([^"]*)"', r'"\1"', enhanced)
            enhanced = re.sub(r"'([^']*)'", r"'\1'", enhanced)
            
            # Remove trailing whitespace
            enhanced = enhanced.strip()
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Text enhancement failed: {e}")
            return text
    
    async def _extract_features(self, text: str) -> TextFeatures:
        """Extract advanced text features using NLP and AI"""
        try:
            features = TextFeatures()
            
            # Sentiment analysis
            if self.config.enable_sentiment_analysis:
                features.sentiment_analysis = await self._analyze_sentiment(text)
            
            # Entity recognition
            if self.config.enable_entity_recognition:
                features.entity_recognition = await self._recognize_entities(text)
            
            # Keyword extraction
            if self.config.enable_keyword_extraction:
                features.keyword_extraction = await self._extract_keywords(text)
            
            # Readability analysis
            if self.config.enable_readability_analysis:
                features.readability_analysis = await self._analyze_readability(text)
            
            # Style analysis
            if self.config.enable_style_analysis:
                features.style_analysis = await self._analyze_style(text)
            
            # Summarization
            if self.config.enable_summarization and self._summarizer:
                features.summary = await self._generate_summary(text)
            
            # Topic extraction
            features.topics = await self._extract_topics(text)
            
            # Content type classification
            features.content_type = await self._classify_content_type(text)
            
            # Target audience analysis
            features.target_audience = await self._analyze_target_audience(text)
            
            # SEO analysis
            if self.config.enable_seo_optimization:
                features.seo_score = await self._calculate_seo_score(text)
            
            # Quality assessment
            features.quality_score = await self._calculate_quality_score(text, features)
            features.uniqueness_score = await self._calculate_uniqueness_score(text)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return TextFeatures()
    
    async def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment of the text"""
        try:
            sentiment_analysis = SentimentAnalysis(
                overall_sentiment="neutral",
                confidence=0.0,
                polarity=0.0,
                subjectivity=0.0
            )
            
            # NLTK VADER sentiment
            if self._sentiment_analyzer:
                scores = self._sentiment_analyzer.polarity_scores(text)
                
                # Determine overall sentiment
                if scores['compound'] >= self.config.sentiment_threshold:
                    sentiment_analysis.overall_sentiment = "positive"
                elif scores['compound'] <= -self.config.sentiment_threshold:
                    sentiment_analysis.overall_sentiment = "negative"
                else:
                    sentiment_analysis.overall_sentiment = "neutral"
                
                sentiment_analysis.confidence = abs(scores['compound'])
                sentiment_analysis.polarity = scores['compound']
                sentiment_analysis.sentiment_distribution = {
                    "positive": scores['pos'],
                    "negative": scores['neg'],
                    "neutral": scores['neu']
                }
            
            # TextBlob sentiment (alternative/additional)
            if TEXT_LIBS_AVAILABLE:
                try:
                    blob = TextBlob(text)
                    sentiment_analysis.subjectivity = blob.sentiment.subjectivity
                    
                    # Use TextBlob polarity as additional signal
                    if not sentiment_analysis.polarity:
                        sentiment_analysis.polarity = blob.sentiment.polarity
                except:
                    pass
            
            # Emotion analysis (simplified)
            sentiment_analysis.emotions = await self._analyze_emotions(text)
            
            return sentiment_analysis
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return SentimentAnalysis(
                overall_sentiment="neutral",
                confidence=0.0,
                polarity=0.0,
                subjectivity=0.0
            )
    
    async def _recognize_entities(self, text: str) -> EntityRecognition:
        """Recognize named entities in the text"""
        try:
            entity_recognition = EntityRecognition()
            
            # spaCy NER
            if self._nlp_model:
                doc = self._nlp_model(text)
                
                for ent in doc.ents:
                    if ent.label_ not in entity_recognition.entity_types:
                        entity_recognition.entity_types[ent.label_] = 0
                    entity_recognition.entity_types[ent.label_] += 1
                    
                    entity_recognition.entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 1.0  # spaCy doesn't provide confidence scores
                    })
            
            # Transformers NER (if available and text not too long)
            elif self._ner_model and len(text) < 10000:
                try:
                    results = self._ner_model(text)
                    
                    for result in results:
                        if result['score'] >= self.config.entity_confidence_threshold:
                            entity_type = result['entity_group']
                            
                            if entity_type not in entity_recognition.entity_types:
                                entity_recognition.entity_types[entity_type] = 0
                            entity_recognition.entity_types[entity_type] += 1
                            
                            entity_recognition.entities.append({
                                "text": result['word'],
                                "label": entity_type,
                                "start": result['start'],
                                "end": result['end'],
                                "confidence": result['score']
                            })
                            
                            entity_recognition.confidence_scores[result['word']] = result['score']
                except Exception as e:
                    self.logger.warning(f"Transformers NER failed: {e}")
            
            return entity_recognition
            
        except Exception as e:
            self.logger.error(f"Entity recognition failed: {e}")
            return EntityRecognition()
    
    async def _extract_keywords(self, text: str) -> KeywordExtraction:
        """Extract keywords and keyphrases from the text"""
        try:
            keyword_extraction = KeywordExtraction()
            
            if not TEXT_LIBS_AVAILABLE:
                return keyword_extraction
            
            # Basic keyword extraction using frequency and stopwords
            words = word_tokenize(text.lower())
            
            # Remove stopwords and punctuation
            try:
                stop_words = set(stopwords.words('english'))
            except:
                stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            
            # Filter words
            filtered_words = [
                word for word in words 
                if word.isalpha() and len(word) > 2 and word not in stop_words
            ]
            
            # Calculate word frequencies
            from collections import Counter
            word_freq = Counter(filtered_words)
            
            # Get top keywords
            top_keywords = [word for word, freq in word_freq.most_common(self.config.keyword_count)]
            keyword_extraction.keywords = top_keywords
            
            # Create keyword scores
            max_freq = max(word_freq.values()) if word_freq else 1
            keyword_extraction.keyword_scores = {
                word: freq / max_freq for word, freq in word_freq.items()
            }
            
            # Extract keyphrases (simple bigrams and trigrams)
            if self._nlp_model:
                doc = self._nlp_model(text)
                keyphrases = []
                
                # Extract noun phrases
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) >= 2 and len(chunk.text) > 5:
                        keyphrases.append(chunk.text.lower())
                
                # Get most frequent keyphrases
                keyphrase_freq = Counter(keyphrases)
                keyword_extraction.keyphrases = [
                    phrase for phrase, freq in keyphrase_freq.most_common(5)
                ]
            
            return keyword_extraction
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return KeywordExtraction()
    
    async def _analyze_readability(self, text: str) -> ReadabilityAnalysis:
        """Analyze readability of the text"""
        try:
            readability = ReadabilityAnalysis()
            
            if not TEXT_LIBS_AVAILABLE:
                return readability
            
            # Calculate various readability metrics
            try:
                readability.flesch_reading_ease = textstat.flesch_reading_ease(text)
                readability.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
                readability.gunning_fog = textstat.gunning_fog(text)
                readability.smog_index = textstat.smog_index(text)
                readability.automated_readability_index = textstat.automated_readability_index(text)
                readability.coleman_liau_index = textstat.coleman_liau_index(text)
                
                # Determine reading level
                grade_level = readability.flesch_kincaid_grade
                if grade_level <= 6:
                    readability.reading_level = "elementary"
                elif grade_level <= 9:
                    readability.reading_level = "middle_school"
                elif grade_level <= 12:
                    readability.reading_level = "high_school"
                elif grade_level <= 16:
                    readability.reading_level = "college"
                else:
                    readability.reading_level = "graduate"
                
                # Estimate reading time
                word_count = len(text.split())
                readability.estimated_reading_time = word_count / 200.0  # 200 WPM average
                
            except Exception as e:
                self.logger.warning(f"Some readability metrics failed: {e}")
            
            return readability
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {e}")
            return ReadabilityAnalysis()
    
    async def _analyze_style(self, text: str) -> StyleAnalysis:
        """Analyze writing style of the text"""
        try:
            style_analysis = StyleAnalysis()
            
            if not TEXT_LIBS_AVAILABLE:
                return style_analysis
            
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Average sentence length
            if sentences:
                style_analysis.average_sentence_length = len(words) / len(sentences)
            
            # Sentence variety (coefficient of variation of sentence lengths)
            sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
            if sentence_lengths:
                import numpy as np
                style_analysis.sentence_variety = np.std(sentence_lengths) / np.mean(sentence_lengths)
            
            # Vocabulary richness (type-token ratio)
            unique_words = set(word.lower() for word in words if word.isalpha())
            alpha_words = [word for word in words if word.isalpha()]
            if alpha_words:
                style_analysis.vocabulary_richness = len(unique_words) / len(alpha_words)
            
            # Passive voice detection (simplified)
            passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
            passive_count = sum(1 for word in words if word.lower() in passive_indicators)
            style_analysis.passive_voice_ratio = passive_count / len(words) if words else 0
            
            # Determine writing style
            style_analysis.writing_style = await self._classify_writing_style(text, style_analysis)
            
            # Tone analysis
            style_analysis.tone = await self._analyze_advanced_tone(text)
            
            # Formality level
            style_analysis.formality_level = await self._analyze_formality(text)
            
            # Complexity score
            style_analysis.complexity_score = await self._calculate_complexity_score(style_analysis)
            
            return style_analysis
            
        except Exception as e:
            self.logger.error(f"Style analysis failed: {e}")
            return StyleAnalysis()
    
    async def _calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """Calculate various readability scores"""
        try:
            scores = {}
            if TEXT_LIBS_AVAILABLE:
                scores['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
                scores['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
                scores['gunning_fog'] = textstat.gunning_fog(text)
                scores['smog_index'] = textstat.smog_index(text)
            return scores
        except:
            return {}
    
    async def _determine_complexity_level(self, readability_scores: Optional[Dict[str, float]]) -> str:
        """Determine complexity level based on readability scores"""
        if not readability_scores or 'flesch_kincaid_grade' not in readability_scores:
            return "medium"
        
        grade = readability_scores['flesch_kincaid_grade']
        if grade <= 6:
            return "simple"
        elif grade <= 9:
            return "medium"
        elif grade <= 12:
            return "complex"
        else:
            return "very_complex"
    
    async def _analyze_basic_tone(self, text: str) -> str:
        """Analyze basic tone of the text"""
        # Simplified tone analysis based on word patterns
        formal_indicators = ['therefore', 'furthermore', 'however', 'nevertheless', 'consequently']
        casual_indicators = ['like', 'you know', 'kinda', 'gonna', 'wanna']
        
        text_lower = text.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        casual_count = sum(1 for indicator in casual_indicators if indicator in text_lower)
        
        if formal_count > casual_count:
            return "formal"
        elif casual_count > formal_count:
            return "casual"
        else:
            return "neutral"
    
    async def _analyze_formality(self, text: str) -> str:
        """Analyze formality level of the text"""
        # Simplified formality analysis
        contractions = ["n't", "'re", "'ve", "'ll", "'d", "'m", "'s"]
        formal_words = ["therefore", "furthermore", "consequently", "nevertheless", "moreover"]
        
        contraction_count = sum(text.count(contraction) for contraction in contractions)
        formal_word_count = sum(1 for word in formal_words if word in text.lower())
        
        words = text.split()
        if not words:
            return "neutral"
        
        contraction_ratio = contraction_count / len(words)
        formal_ratio = formal_word_count / len(words)
        
        if formal_ratio > 0.02:
            return "formal"
        elif contraction_ratio > 0.05:
            return "informal"
        else:
            return "neutral"
    
    async def _extract_basic_keywords(self, text: str) -> List[str]:
        """Extract basic keywords from text"""
        try:
            if not TEXT_LIBS_AVAILABLE:
                # Simple keyword extraction without NLTK
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                from collections import Counter
                word_freq = Counter(words)
                return [word for word, freq in word_freq.most_common(5)]
            
            words = word_tokenize(text.lower())
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            
            filtered_words = [word for word in words if word.isalpha() and len(word) > 2 and word not in stop_words]
            
            from collections import Counter
            word_freq = Counter(filtered_words)
            return [word for word, freq in word_freq.most_common(5)]
            
        except:
            return []
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in the text (simplified)"""
        # Simplified emotion analysis based on keyword matching
        emotion_keywords = {
            'joy': ['happy', 'joyful', 'excited', 'pleased', 'delighted', 'cheerful'],
            'sadness': ['sad', 'unhappy', 'depressed', 'melancholy', 'sorrowful'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated'],
            'fear': ['afraid', 'scared', 'frightened', 'anxious', 'worried'],
            'surprise': ['surprised', 'amazed', 'shocked', 'astonished'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'nauseated']
        }
        
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = count / len(text.split()) if text.split() else 0
        
        return emotions
    
    async def _generate_summary(self, text: str) -> Optional[str]:
        """Generate summary of the text"""
        try:
            if not self._summarizer:
                return None
            
            # Only summarize if text is long enough
            if len(text.split()) < 100:
                return None
            
            # Truncate text if too long for model
            max_length = 1024  # Typical model limit
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self._summarizer(text, max_length=self.config.max_summary_length, min_length=50)
            
            if result and len(result) > 0:
                return result[0]['summary_text']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return None
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from the text (simplified)"""
        try:
            # Simplified topic extraction using keyword frequency
            keywords = await self._extract_basic_keywords(text)
            
            # Group keywords into potential topics
            topics = []
            
            # Technology topics
            tech_words = ['technology', 'digital', 'computer', 'software', 'internet', 'ai', 'artificial', 'intelligence']
            if any(word in text.lower() for word in tech_words):
                topics.append('technology')
            
            # Business topics
            business_words = ['business', 'company', 'market', 'profit', 'revenue', 'strategy', 'management']
            if any(word in text.lower() for word in business_words):
                topics.append('business')
            
            # Health topics
            health_words = ['health', 'medical', 'doctor', 'patient', 'treatment', 'medicine', 'wellness']
            if any(word in text.lower() for word in health_words):
                topics.append('health')
            
            # Education topics
            education_words = ['education', 'school', 'student', 'teacher', 'learning', 'knowledge', 'study']
            if any(word in text.lower() for word in education_words):
                topics.append('education')
            
            # Add most frequent keywords as topics if no specific topics found
            if not topics:
                topics = keywords[:3]
            
            return topics
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return []
    
    async def _classify_content_type(self, text: str) -> str:
        """Classify the type of content"""
        text_lower = text.lower()
        
        # News article indicators
        if any(indicator in text_lower for indicator in ['breaking', 'reported', 'according to', 'sources say']):
            return 'news'
        
        # Blog post indicators
        if any(indicator in text_lower for indicator in ['i think', 'in my opinion', 'personally', 'my experience']):
            return 'blog'
        
        # Academic paper indicators
        if any(indicator in text_lower for indicator in ['abstract', 'methodology', 'conclusion', 'references']):
            return 'academic'
        
        # Social media indicators
        if any(indicator in text_lower for indicator in ['#', '@', 'like', 'share', 'follow']):
            return 'social_media'
        
        # Marketing content indicators
        if any(indicator in text_lower for indicator in ['buy now', 'limited time', 'special offer', 'discount']):
            return 'marketing'
        
        return 'general'
    
    async def _analyze_target_audience(self, text: str) -> str:
        """Analyze target audience of the text"""
        readability_scores = await self._calculate_readability_scores(text)
        
        if readability_scores and 'flesch_kincaid_grade' in readability_scores:
            grade = readability_scores['flesch_kincaid_grade']
            
            if grade <= 6:
                return 'children'
            elif grade <= 9:
                return 'young_adults'
            elif grade <= 12:
                return 'general_public'
            elif grade <= 16:
                return 'educated_adults'
            else:
                return 'experts'
        
        return 'general_public'
    
    async def _calculate_seo_score(self, text: str) -> float:
        """Calculate SEO score of the text"""
        try:
            score = 0.0
            
            # Word count (optimal 300-2000 words)
            word_count = len(text.split())
            if 300 <= word_count <= 2000:
                score += 0.2
            elif word_count >= 100:
                score += 0.1
            
            # Sentence length (optimal 15-20 words)
            if TEXT_LIBS_AVAILABLE:
                sentences = sent_tokenize(text)
                if sentences:
                    avg_sentence_length = word_count / len(sentences)
                    if 15 <= avg_sentence_length <= 20:
                        score += 0.15
                    elif 10 <= avg_sentence_length <= 25:
                        score += 0.1
            
            # Paragraph structure
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) >= 3:
                score += 0.1
            
            # Readability
            readability_scores = await self._calculate_readability_scores(text)
            if readability_scores and 'flesch_reading_ease' in readability_scores:
                ease = readability_scores['flesch_reading_ease']
                if 60 <= ease <= 80:  # Good readability
                    score += 0.2
                elif 40 <= ease <= 90:
                    score += 0.1
            
            # Keyword density (simplified)
            keywords = await self._extract_basic_keywords(text)
            if keywords:
                main_keyword = keywords[0]
                keyword_count = text.lower().count(main_keyword)
                keyword_density = keyword_count / word_count
                if 0.01 <= keyword_density <= 0.03:  # Optimal density 1-3%
                    score += 0.15
                elif keyword_density <= 0.05:
                    score += 0.1
            
            # Structure indicators (headers, lists)
            if any(indicator in text for indicator in ['#', '*', '-', '1.', '2.']):
                score += 0.1
            
            # Link indicators
            if 'http' in text or 'www' in text:
                score += 0.05
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"SEO score calculation failed: {e}")
            return 0.5
    
    async def _calculate_quality_score(self, text: str, features: TextFeatures) -> float:
        """Calculate overall text quality score"""
        try:
            score = 0.0
            
            # Grammar and spelling (simplified check)
            if TEXT_LIBS_AVAILABLE:
                try:
                    blob = TextBlob(text)
                    corrected = str(blob.correct())
                    grammar_score = 1.0 - (len(text) - len(corrected)) / len(text)
                    score += grammar_score * 0.25
                except:
                    score += 0.2  # Default if correction fails
            else:
                score += 0.2
            
            # Readability
            if features and features.readability_analysis and features.readability_analysis.flesch_reading_ease:
                ease = features.readability_analysis.flesch_reading_ease
                if 60 <= ease <= 80:
                    score += 0.25
                elif 40 <= ease <= 90:
                    score += 0.15
                else:
                    score += 0.1
            else:
                score += 0.15
            
            # Content structure
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) >= 2:
                score += 0.15
            
            # Vocabulary richness
            if features and features.style_analysis and features.style_analysis.vocabulary_richness:
                richness = features.style_analysis.vocabulary_richness
                if richness >= 0.7:
                    score += 0.2
                elif richness >= 0.5:
                    score += 0.15
                else:
                    score += 0.1
            else:
                score += 0.1
            
            # Coherence (simplified - based on keyword consistency)
            keywords = await self._extract_basic_keywords(text)
            if len(keywords) >= 3:
                score += 0.15
            else:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return 0.5
    
    async def _calculate_uniqueness_score(self, text: str) -> float:
        """Calculate uniqueness score (simplified)"""
        try:
            # In production, this would check against a database of known content
            # For now, use text characteristics as proxy for uniqueness
            
            unique_words = set(word.lower() for word in text.split() if word.isalpha())
            total_words = len([word for word in text.split() if word.isalpha()])
            
            if total_words == 0:
                return 0.0
            
            # Vocabulary diversity as proxy for uniqueness
            diversity = len(unique_words) / total_words
            
            # Sentence structure variety
            if TEXT_LIBS_AVAILABLE:
                sentences = sent_tokenize(text)
                sentence_lengths = [len(sentence.split()) for sentence in sentences]
                if sentence_lengths:
                    import numpy as np
                    length_variety = np.std(sentence_lengths) / np.mean(sentence_lengths)
                    uniqueness_score = (diversity * 0.7) + (min(1.0, length_variety) * 0.3)
                else:
                    uniqueness_score = diversity
            else:
                uniqueness_score = diversity
            
            return min(1.0, uniqueness_score)
            
        except Exception as e:
            self.logger.error(f"Uniqueness score calculation failed: {e}")
            return 0.5
    
    async def _classify_writing_style(self, text: str, style_analysis: StyleAnalysis) -> str:
        """Classify the writing style"""
        try:
            # Academic style
            if (style_analysis.average_sentence_length and style_analysis.average_sentence_length > 20 and
                style_analysis.vocabulary_richness and style_analysis.vocabulary_richness > 0.7):
                return "academic"
            
            # Conversational style
            if (style_analysis.average_sentence_length and style_analysis.average_sentence_length < 15 and
                any(word in text.lower() for word in ['you', 'i', 'we', 'let\'s'])):
                return "conversational"
            
            # Journalistic style
            if (style_analysis.average_sentence_length and 15 <= style_analysis.average_sentence_length <= 20 and
                any(indicator in text.lower() for indicator in ['according to', 'reported', 'sources'])):
                return "journalistic"
            
            # Creative writing
            if (style_analysis.vocabulary_richness and style_analysis.vocabulary_richness > 0.6 and
                style_analysis.sentence_variety and style_analysis.sentence_variety > 0.3):
                return "creative"
            
            # Technical writing
            if any(indicator in text.lower() for indicator in ['therefore', 'furthermore', 'however', 'thus']):
                return "technical"
            
            return "general"
            
        except Exception as e:
            self.logger.error(f"Writing style classification failed: {e}")
            return "general"
    
    async def _analyze_advanced_tone(self, text: str) -> str:
        """Analyze advanced tone of the text"""
        # More sophisticated tone analysis
        
        # Positive tone indicators
        positive_words = ['excellent', 'amazing', 'wonderful', 'great', 'fantastic', 'love', 'enjoy']
        positive_count = sum(1 for word in positive_words if word in text.lower())
        
        # Negative tone indicators
        negative_words = ['terrible', 'awful', 'hate', 'disgusting', 'horrible', 'worst', 'fail']
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        # Professional tone indicators
        professional_words = ['professional', 'expertise', 'experience', 'qualified', 'competent']
        professional_count = sum(1 for word in professional_words if word in text.lower())
        
        # Urgent tone indicators
        urgent_words = ['urgent', 'immediately', 'asap', 'critical', 'emergency', 'now']
        urgent_count = sum(1 for word in urgent_words if word in text.lower())
        
        # Determine dominant tone
        scores = {
            'positive': positive_count,
            'negative': negative_count,
            'professional': professional_count,
            'urgent': urgent_count
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'neutral'
        
        return max(scores.keys(), key=scores.get)
    
    async def _calculate_complexity_score(self, style_analysis: StyleAnalysis) -> float:
        """Calculate complexity score from style analysis"""
        try:
            score = 0.0
            
            # Sentence length complexity
            if style_analysis.average_sentence_length:
                if style_analysis.average_sentence_length > 25:
                    score += 0.4
                elif style_analysis.average_sentence_length > 15:
                    score += 0.3
                else:
                    score += 0.1
            
            # Vocabulary richness
            if style_analysis.vocabulary_richness:
                score += style_analysis.vocabulary_richness * 0.3
            
            # Sentence variety
            if style_analysis.sentence_variety:
                score += style_analysis.sentence_variety * 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            self.logger.error(f"Complexity score calculation failed: {e}")
            return 0.5
    
    async def _generate_fingerprint(self, text: str) -> str:
        """Generate text fingerprint for content identification"""
        try:
            # Create a normalized version of the text
            normalized = re.sub(r'\s+', ' ', text.lower().strip())
            
            # Generate hash
            fingerprint = hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            return ""
    
    async def _generate_semantic_hash(self, text: str) -> str:
        """Generate semantic hash based on content meaning"""
        try:
            # Simplified semantic hashing using keywords
            keywords = await self._extract_basic_keywords(text)
            
            # Sort keywords for consistency
            sorted_keywords = sorted(keywords)
            
            # Create hash from keywords
            keyword_string = ' '.join(sorted_keywords)
            semantic_hash = hashlib.md5(keyword_string.encode('utf-8')).hexdigest()[:16]
            
            return semantic_hash
            
        except Exception as e:
            self.logger.error(f"Semantic hash generation failed: {e}")
            return ""
    
    async def _generate_tags(
        self,
        metadata: TextMetadata,
        features: Optional[TextFeatures],
        text: str
    ) -> List[str]:
        """Generate relevant tags for the text content"""
        tags = []
        
        try:
            # Language tag
            if metadata.language:
                tags.append(f"lang-{metadata.language}")
            
            # Length tags
            if metadata.word_count < 100:
                tags.append("short")
            elif metadata.word_count > 1000:
                tags.append("long")
            
            # Complexity tags
            if metadata.complexity_level:
                tags.append(f"complexity-{metadata.complexity_level}")
            
            # Reading level tags
            if features and features.readability_analysis and features.readability_analysis.reading_level:
                tags.append(f"reading-{features.readability_analysis.reading_level}")
            
            # Content type tags
            if features and features.content_type:
                tags.append(features.content_type)
            
            # Sentiment tags
            if features and features.sentiment_analysis:
                tags.append(f"sentiment-{features.sentiment_analysis.overall_sentiment}")
            
            # Style tags
            if features and features.style_analysis:
                if features.style_analysis.writing_style:
                    tags.append(f"style-{features.style_analysis.writing_style}")
                if features.style_analysis.tone:
                    tags.append(f"tone-{features.style_analysis.tone}")
                if features.style_analysis.formality_level:
                    tags.append(f"formality-{features.style_analysis.formality_level}")
            
            # Topic tags
            if features and features.topics:
                tags.extend([f"topic-{topic}" for topic in features.topics])
            
            # Quality tags
            if features and features.quality_score:
                if features.quality_score > 0.8:
                    tags.append("high-quality")
                elif features.quality_score < 0.5:
                    tags.append("needs-improvement")
            
            # Entity tags
            if features and features.entity_recognition and features.entity_recognition.entity_types:
                for entity_type in features.entity_recognition.entity_types.keys():
                    tags.append(f"entity-{entity_type.lower()}")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Tag generation failed: {e}")
            return []
    
    async def _convert_format(
        self,
        text: str,
        target_format: TextFormat,
        options: Dict[str, Any]
    ) -> str:
        """Convert text to target format"""
        try:
            if target_format == TextFormat.PLAIN:
                # Strip HTML tags if present
                import re
                cleaned = re.sub(r'<[^>]+>', '', text)
                return cleaned.strip()
            
            elif target_format == TextFormat.HTML:
                # Convert plain text to HTML
                paragraphs = text.split('\n\n')
                html_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
                return '\n'.join(html_paragraphs)
            
            elif target_format == TextFormat.MARKDOWN:
                # Convert to Markdown (basic)
                lines = text.split('\n')
                markdown_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        markdown_lines.append('')
                    # Simple heuristic for headers
                    elif line.isupper() and len(line) < 50:
                        markdown_lines.append(f"# {line}")
                    elif line.endswith(':') and len(line) < 50:
                        markdown_lines.append(f"## {line}")
                    else:
                        markdown_lines.append(line)
                
                return '\n'.join(markdown_lines)
            
            elif target_format == TextFormat.JSON:
                # Convert to JSON structure
                import json
                data = {
                    "text": text,
                    "metadata": {
                        "word_count": len(text.split()),
                        "character_count": len(text),
                        "generated_at": datetime.now().isoformat()
                    }
                }
                return json.dumps(data, indent=2)
            
            else:
                # Default: return as-is
                return text
                
        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            return text
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the text processor"""
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "text_libs_available": TEXT_LIBS_AVAILABLE,
            "ai_libs_available": AI_LIBS_AVAILABLE,
            "sentiment_analyzer_loaded": self._sentiment_analyzer is not None,
            "ner_model_loaded": self._ner_model is not None,
            "summarizer_loaded": self._summarizer is not None,
            "translator_loaded": self._translator is not None,
            "nlp_model_loaded": self._nlp_model is not None,
            "config": self.config.__dict__
        }


async def create_text_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> TextProcessor:
    """
    Factory function to create and initialize a text processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized TextProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = TextProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in TextProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = TextProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
