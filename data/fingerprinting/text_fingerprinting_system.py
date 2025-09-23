#!/usr/bin/env python3
"""
Text Fingerprinting System - Ainflue Data Fingerprinting Module
===============================================================
Advanced text fingerprinting system with NLP-powered analysis,
semantic embeddings, linguistic patterns, and specialized text content 
protection for blog/content creators on the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Data Fingerprinting
Version: 1.0 Enterprise Production
"""

import asyncio
import hashlib
import logging
import numpy as np
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import unicodedata

# Core imports for text processing
try:
    import torch
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    import spacy
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.util import ngrams
    import textstat
    from langdetect import detect, LangDetectError
except ImportError as e:
    logging.error(f"Required text dependencies not installed: {e}")

# Ainflue core imports
from .multimodal_fingerprinting_engine import FingerprintResult, FingerprintConfig
from .vector_database_matching import VectorDatabaseManager
from .performance_analytics_engine import PerformanceAnalytics


class TextFingerprintType(Enum):
    """Types of text fingerprints supported."""
    TFIDF_FEATURES = "tfidf_features"
    SEMANTIC_EMBEDDINGS = "semantic_embeddings"
    LINGUISTIC_PATTERNS = "linguistic_patterns"
    STYLOMETRIC_FEATURES = "stylometric_features"
    TOPIC_MODEL = "topic_model"
    N_GRAM_ANALYSIS = "n_gram_analysis"
    READABILITY_METRICS = "readability_metrics"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITIES = "named_entities"
    SYNTACTIC_PATTERNS = "syntactic_patterns"
    LEXICAL_DIVERSITY = "lexical_diversity"
    COMBINED = "combined"


class TextFormat(Enum):
    """Supported text formats."""
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    RTF = "rtf"
    PDF_TEXT = "pdf_text"


class TextLanguage(Enum):
    """Supported languages."""
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    UNKNOWN = "unknown"


@dataclass
class TextMetadata:
    """Text content metadata container."""
    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[TextLanguage] = None
    format: Optional[TextFormat] = None
    encoding: str = "utf-8"
    avg_word_length: Optional[float] = None
    avg_sentence_length: Optional[float] = None
    lexical_diversity: Optional[float] = None
    readability_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    topic_distribution: Optional[Dict[str, float]] = None
    named_entities: Optional[List[str]] = None
    has_urls: bool = False
    has_emails: bool = False
    has_phone_numbers: bool = False
    estimated_reading_time: Optional[float] = None  # in minutes


@dataclass
class TextFingerprint:
    """Text fingerprint data structure."""
    fingerprint_id: str
    fingerprint_type: TextFingerprintType
    data: np.ndarray
    confidence: float
    metadata: TextMetadata
    text_snippet: Optional[str] = None  # First 200 characters for reference
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    file_path: Optional[str] = None
    hash_sha256: Optional[str] = None
    additional_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TextAnalysisConfig:
    """Configuration for text analysis."""
    max_features: int = 10000
    ngram_range: Tuple[int, int] = (1, 3)
    min_df: int = 2
    max_df: float = 0.95
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    spacy_model: str = "en_core_web_sm"
    num_topics: int = 10
    enable_sentiment_analysis: bool = True
    enable_ner: bool = True
    enable_pos_tagging: bool = True
    quality_threshold: float = 0.7
    confidence_threshold: float = 0.8
    max_text_length: int = 100000  # Maximum characters to process
    snippet_length: int = 200


class TextFingerprintingSystem:
    """
    Advanced Text Fingerprinting System
    
    Provides comprehensive text content fingerprinting with:
    - TF-IDF vectorization and semantic embeddings
    - Stylometric analysis and linguistic patterns
    - Topic modeling and sentiment analysis
    - Named entity recognition and syntactic analysis
    - Multi-language support and encoding detection
    """
    
    def __init__(self, config: Optional[TextAnalysisConfig] = None):
        """Initialize text fingerprinting system."""
        self.config = config or TextAnalysisConfig()
        self.logger = logging.getLogger(__name__)
        
        # Vector database for similarity matching
        self.vector_db = VectorDatabaseManager()
        self.performance_analytics = PerformanceAnalytics()
        
        # NLP models
        self.embedding_model = None
        self.tokenizer = None
        self.sentiment_analyzer = None
        self.nlp = None
        
        # Text processing components
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.config.max_features,
            ngram_range=self.config.ngram_range,
            min_df=self.config.min_df,
            max_df=self.config.max_df,
            stop_words='english'
        )
        self.topic_model = LatentDirichletAllocation(n_components=self.config.num_topics, random_state=42)
        
        # Language tools
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize components
        self._initialize_models()
        self._download_nltk_data()
        
        self.logger.info("TextFingerprintingSystem initialized successfully")
    
    def _initialize_models(self):
        """Initialize NLP models and components."""
        try:
            # Initialize embedding model
            if self.config.embedding_model:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(self.config.embedding_model)
                self.logger.info("Sentence transformer model loaded successfully")
            
            # Initialize sentiment analyzer
            if self.config.enable_sentiment_analysis:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                self.logger.info("Sentiment analyzer loaded successfully")
            
            # Initialize spaCy model
            try:
                self.nlp = spacy.load(self.config.spacy_model)
                self.logger.info("spaCy model loaded successfully")
            except OSError:
                self.logger.warning(f"spaCy model {self.config.spacy_model} not found, NER disabled")
                self.config.enable_ner = False
                self.config.enable_pos_tagging = False
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize some NLP models: {e}")
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk_downloads = [
                'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
                'vader_lexicon', 'omw-1.4'
            ]
            
            for resource in nltk_downloads:
                try:
                    nltk.data.find(f'tokenizers/{resource}')
                except LookupError:
                    try:
                        nltk.download(resource, quiet=True)
                    except Exception:
                        pass
                        
        except Exception as e:
            self.logger.warning(f"Failed to download NLTK data: {e}")
    
    async def process_text_content(
        self,
        text_content: str,
        creator_id: str,
        file_path: Optional[str] = None,
        fingerprint_types: Optional[List[TextFingerprintType]] = None
    ) -> List[TextFingerprint]:
        """
        Process text content and generate multiple fingerprints.
        
        Args:
            text_content: Text content to fingerprint
            creator_id: Creator identifier for protection
            file_path: Optional path to source file
            fingerprint_types: Types of fingerprints to generate
        
        Returns:
            List of generated text fingerprints
        """
        start_time = datetime.utcnow()
        
        try:
            # Limit text length
            if len(text_content) > self.config.max_text_length:
                text_content = text_content[:self.config.max_text_length]
                self.logger.warning(f"Text truncated to {self.config.max_text_length} characters")
            
            # Preprocess text
            cleaned_text = await self._preprocess_text(text_content)
            
            # Extract metadata
            metadata = await self._extract_metadata(text_content, cleaned_text)
            
            # Generate file hash
            file_hash = await self._generate_content_hash(text_content)
            
            # Generate text snippet
            text_snippet = text_content[:self.config.snippet_length]
            
            # Default fingerprint types
            if fingerprint_types is None:
                fingerprint_types = [
                    TextFingerprintType.TFIDF_FEATURES,
                    TextFingerprintType.SEMANTIC_EMBEDDINGS,
                    TextFingerprintType.STYLOMETRIC_FEATURES,
                    TextFingerprintType.LINGUISTIC_PATTERNS,
                    TextFingerprintType.COMBINED
                ]
            
            # Generate fingerprints
            fingerprints = []
            for fp_type in fingerprint_types:
                fingerprint = await self._generate_fingerprint(
                    text_content=text_content,
                    cleaned_text=cleaned_text,
                    fingerprint_type=fp_type,
                    metadata=metadata,
                    text_snippet=text_snippet,
                    file_path=file_path,
                    file_hash=file_hash
                )
                fingerprints.append(fingerprint)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update fingerprints with processing time
            for fp in fingerprints:
                fp.processing_time = processing_time
            
            # Store fingerprints in vector database
            await self._store_fingerprints(fingerprints, creator_id)
            
            # Record analytics
            await self.performance_analytics.record_processing_metrics({
                'operation': 'text_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': processing_time,
                'fingerprint_count': len(fingerprints),
                'text_length': len(text_content),
                'success': True
            })
            
            self.logger.info(
                f"Generated {len(fingerprints)} fingerprints for text "
                f"({len(text_content)} chars) in {processing_time:.2f}s"
            )
            
            return fingerprints
            
        except Exception as e:
            error_msg = f"Failed to process text content: {e}"
            self.logger.error(error_msg)
            
            await self.performance_analytics.record_processing_metrics({
                'operation': 'text_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'fingerprint_count': 0,
                'success': False,
                'error': str(e)
            })
            
            raise
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess text for fingerprinting."""
        try:
            # Normalize unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Basic cleaning
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove control characters
            text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
            
            # Trim
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Text preprocessing failed: {e}")
            return text
    
    async def _extract_metadata(self, original_text: str, cleaned_text: str) -> TextMetadata:
        """Extract comprehensive text metadata."""
        try:
            # Basic statistics
            character_count = len(original_text)
            words = word_tokenize(cleaned_text.lower())
            word_count = len(words)
            sentences = sent_tokenize(cleaned_text)
            sentence_count = len(sentences)
            paragraph_count = len([p for p in original_text.split('\n\n') if p.strip()])
            
            # Language detection
            language = await self._detect_language(cleaned_text)
            
            # Average lengths
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Lexical diversity (Type-Token Ratio)
            unique_words = set(words)
            lexical_diversity = len(unique_words) / len(words) if words else 0
            
            # Readability score
            readability_score = await self._calculate_readability(original_text)
            
            # Sentiment analysis
            sentiment_score = await self._analyze_sentiment(cleaned_text)
            
            # Pattern detection
            has_urls = bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', original_text))
            has_emails = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', original_text))
            has_phone_numbers = bool(re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', original_text))
            
            # Estimated reading time (average 200 words per minute)
            estimated_reading_time = word_count / 200.0
            
            # Named entities
            named_entities = await self._extract_named_entities(cleaned_text)
            
            return TextMetadata(
                character_count=character_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                language=language,
                avg_word_length=avg_word_length,
                avg_sentence_length=avg_sentence_length,
                lexical_diversity=lexical_diversity,
                readability_score=readability_score,
                sentiment_score=sentiment_score,
                named_entities=named_entities,
                has_urls=has_urls,
                has_emails=has_emails,
                has_phone_numbers=has_phone_numbers,
                estimated_reading_time=estimated_reading_time
            )
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return TextMetadata(
                character_count=len(original_text),
                word_count=0,
                sentence_count=0,
                paragraph_count=0
            )
    
    async def _detect_language(self, text: str) -> TextLanguage:
        """Detect text language."""
        try:
            if len(text.strip()) < 10:
                return TextLanguage.UNKNOWN
            
            detected = detect(text)
            
            # Map language codes to enum
            lang_mapping = {
                'en': TextLanguage.ENGLISH,
                'fr': TextLanguage.FRENCH,
                'de': TextLanguage.GERMAN,
                'es': TextLanguage.SPANISH,
                'it': TextLanguage.ITALIAN,
                'pt': TextLanguage.PORTUGUESE,
                'ru': TextLanguage.RUSSIAN,
                'zh-cn': TextLanguage.CHINESE,
                'zh': TextLanguage.CHINESE,
                'ja': TextLanguage.JAPANESE,
                'ko': TextLanguage.KOREAN,
                'ar': TextLanguage.ARABIC
            }
            
            return lang_mapping.get(detected, TextLanguage.UNKNOWN)
            
        except LangDetectError:
            return TextLanguage.UNKNOWN
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return TextLanguage.UNKNOWN
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculate readability score."""
        try:
            # Use Flesch Reading Ease score
            score = textstat.flesch_reading_ease(text)
            # Normalize to 0-1 range
            return max(0.0, min(1.0, score / 100.0))
        except Exception as e:
            self.logger.warning(f"Readability calculation failed: {e}")
            return 0.5
    
    async def _analyze_sentiment(self, text: str) -> Optional[float]:
        """Analyze text sentiment."""
        try:
            if not self.config.enable_sentiment_analysis or self.sentiment_analyzer is None:
                return None
            
            if len(text.strip()) < 10:
                return 0.5  # Neutral
            
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            result = self.sentiment_analyzer(text)
            
            # Convert to single sentiment score (0=negative, 0.5=neutral, 1=positive)
            if isinstance(result, list) and len(result) > 0:
                scores = {item['label'].lower(): item['score'] for item in result[0]}
                
                if 'positive' in scores and 'negative' in scores:
                    return scores.get('positive', 0.5)
                elif 'pos' in scores and 'neg' in scores:
                    return scores.get('pos', 0.5)
            
            return 0.5  # Default neutral
            
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {e}")
            return None
    
    async def _extract_named_entities(self, text: str) -> Optional[List[str]]:
        """Extract named entities from text."""
        try:
            if not self.config.enable_ner or self.nlp is None:
                return None
            
            if len(text.strip()) < 10:
                return []
            
            # Truncate text if too long
            if len(text) > 1000000:  # spaCy limit
                text = text[:1000000]
            
            doc = self.nlp(text)
            entities = [ent.text.strip() for ent in doc.ents if len(ent.text.strip()) > 2]
            
            # Remove duplicates and limit
            unique_entities = list(set(entities))[:50]  # Limit to 50 entities
            
            return unique_entities
            
        except Exception as e:
            self.logger.warning(f"Named entity extraction failed: {e}")
            return None
    
    async def _generate_fingerprint(
        self,
        text_content: str,
        cleaned_text: str,
        fingerprint_type: TextFingerprintType,
        metadata: TextMetadata,
        text_snippet: str,
        file_path: Optional[str],
        file_hash: str
    ) -> TextFingerprint:
        """Generate specific type of text fingerprint."""
        
        try:
            if fingerprint_type == TextFingerprintType.TFIDF_FEATURES:
                data, confidence = await self._generate_tfidf_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.SEMANTIC_EMBEDDINGS:
                data, confidence = await self._generate_semantic_embeddings(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.LINGUISTIC_PATTERNS:
                data, confidence = await self._generate_linguistic_patterns(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.STYLOMETRIC_FEATURES:
                data, confidence = await self._generate_stylometric_features(text_content, cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.TOPIC_MODEL:
                data, confidence = await self._generate_topic_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.N_GRAM_ANALYSIS:
                data, confidence = await self._generate_ngram_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.READABILITY_METRICS:
                data, confidence = await self._generate_readability_features(text_content)
            
            elif fingerprint_type == TextFingerprintType.SENTIMENT_ANALYSIS:
                data, confidence = await self._generate_sentiment_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.NAMED_ENTITIES:
                data, confidence = await self._generate_entity_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.SYNTACTIC_PATTERNS:
                data, confidence = await self._generate_syntactic_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.LEXICAL_DIVERSITY:
                data, confidence = await self._generate_lexical_features(cleaned_text)
            
            elif fingerprint_type == TextFingerprintType.COMBINED:
                data, confidence = await self._generate_combined_fingerprint(text_content, cleaned_text)
            
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(
                file_hash, fingerprint_type.value, data
            )
            
            return TextFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_type=fingerprint_type,
                data=data,
                confidence=confidence,
                metadata=metadata,
                text_snippet=text_snippet,
                file_path=file_path,
                hash_sha256=file_hash
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate {fingerprint_type.value} fingerprint: {e}")
            raise
    
    async def _generate_tfidf_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate TF-IDF based features."""
        try:
            if len(text.strip()) < 10:
                return np.array([]), 0.0
            
            # Tokenize and clean
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and len(word) > 2]
            
            if len(words) < 5:
                return np.array([]), 0.0
            
            # Rejoin for TF-IDF
            processed_text = ' '.join(words)
            
            # Fit or transform TF-IDF
            try:
                tfidf_vector = self.tfidf_vectorizer.fit_transform([processed_text])
            except ValueError:
                # If vocabulary is empty, return empty features
                return np.array([]), 0.0
            
            features = tfidf_vector.toarray().flatten()
            
            # Calculate confidence based on feature sparsity
            non_zero_features = np.count_nonzero(features)
            confidence = min(1.0, non_zero_features / 100.0)  # Scale factor
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"TF-IDF generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_semantic_embeddings(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate semantic embeddings."""
        try:
            if not self.embedding_model or len(text.strip()) < 10:
                return np.array([]), 0.0
            
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode([text])
            features = embeddings[0]
            
            # Calculate confidence based on embedding norm
            embedding_norm = np.linalg.norm(features)
            confidence = min(1.0, embedding_norm / 10.0)  # Normalize
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Semantic embeddings generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_linguistic_patterns(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate linguistic pattern features."""
        try:
            if len(text.strip()) < 10:
                return np.array([]), 0.0
            
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Character-level features
            char_features = []
            
            # Letter frequency
            letters = [c for c in text.lower() if c.isalpha()]
            if letters:
                char_counts = Counter(letters)
                total_chars = len(letters)
                # Top 10 most common letters
                for i, (char, count) in enumerate(char_counts.most_common(10)):
                    char_features.append(count / total_chars)
                
                # Pad to 10 features if needed
                while len(char_features) < 10:
                    char_features.append(0.0)
            else:
                char_features = [0.0] * 10
            
            # Word-level features
            word_features = []
            
            if words:
                # Average word length
                word_features.append(np.mean([len(word) for word in words]))
                
                # Word length distribution
                word_lengths = [len(word) for word in words]
                word_features.extend([
                    np.std(word_lengths),
                    len([w for w in word_lengths if w <= 3]) / len(words),  # Short words ratio
                    len([w for w in word_lengths if w >= 7]) / len(words),  # Long words ratio
                ])
                
                # Function words ratio
                function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                function_word_count = len([w for w in words if w.lower() in function_words])
                word_features.append(function_word_count / len(words))
            else:
                word_features = [0.0] * 5
            
            # Sentence-level features
            sentence_features = []
            
            if sentences:
                sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
                sentence_features.extend([
                    np.mean(sentence_lengths),
                    np.std(sentence_lengths) if len(sentence_lengths) > 1 else 0.0,
                    len([s for s in sentences if s.strip().endswith('?')]) / len(sentences),  # Question ratio
                    len([s for s in sentences if s.strip().endswith('!')]) / len(sentences),  # Exclamation ratio
                ])
            else:
                sentence_features = [0.0] * 4
            
            # Combine all features
            features = np.array(char_features + word_features + sentence_features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Linguistic patterns generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_stylometric_features(self, original_text: str, cleaned_text: str) -> Tuple[np.ndarray, float]:
        """Generate stylometric features for authorship analysis."""
        try:
            if len(cleaned_text.strip()) < 10:
                return np.array([]), 0.0
            
            words = word_tokenize(cleaned_text.lower())
            sentences = sent_tokenize(cleaned_text)
            
            features = []
            
            # Basic statistics
            features.extend([
                len(words),
                len(sentences),
                len(words) / len(sentences) if sentences else 0,  # Words per sentence
                len(set(words)) / len(words) if words else 0,  # Type-token ratio
            ])
            
            # Punctuation features
            punctuation_chars = '.,;:!?'
            for punct in punctuation_chars:
                features.append(original_text.count(punct) / len(original_text) if original_text else 0)
            
            # Word length distribution
            if words:
                word_lengths = [len(word) for word in words]
                features.extend([
                    np.mean(word_lengths),
                    np.std(word_lengths),
                    len([w for w in words if len(w) == 1]) / len(words),  # 1-letter words
                    len([w for w in words if len(w) >= 6]) / len(words),   # Long words
                ])
            else:
                features.extend([0.0] * 4)
            
            # Part-of-speech features (if available)
            if self.config.enable_pos_tagging and self.nlp:
                try:
                    doc = self.nlp(cleaned_text[:10000])  # Limit for performance
                    pos_counts = Counter([token.pos_ for token in doc])
                    total_tokens = len(doc)
                    
                    # Common POS tags
                    pos_tags = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON']
                    for pos in pos_tags:
                        features.append(pos_counts.get(pos, 0) / total_tokens if total_tokens > 0 else 0)
                except Exception:
                    features.extend([0.0] * 5)
            else:
                features.extend([0.0] * 5)
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Stylometric features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_topic_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate topic modeling features."""
        try:
            if len(text.strip()) < 50:
                return np.array([]), 0.0
            
            # Preprocess for topic modeling
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and len(word) > 2]
            
            if len(words) < 10:
                return np.array([]), 0.0
            
            # Remove stopwords
            try:
                stop_words = set(stopwords.words('english'))
                words = [word for word in words if word not in stop_words]
            except Exception:
                pass
            
            if len(words) < 5:
                return np.array([]), 0.0
            
            processed_text = ' '.join(words)
            
            # Transform text for topic modeling
            try:
                tfidf_vector = self.tfidf_vectorizer.fit_transform([processed_text])
                topic_distribution = self.topic_model.fit_transform(tfidf_vector)
                features = topic_distribution.flatten()
            except Exception:
                return np.array([]), 0.0
            
            # Calculate confidence based on topic concentration
            if len(features) > 0:
                topic_entropy = -np.sum(features * np.log(features + 1e-10))
                confidence = min(1.0, topic_entropy / np.log(len(features)))
            else:
                confidence = 0.0
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Topic features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_ngram_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate n-gram based features."""
        try:
            if len(text.strip()) < 10:
                return np.array([]), 0.0
            
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha()]
            
            if len(words) < 3:
                return np.array([]), 0.0
            
            features = []
            
            # Generate n-grams for n=2,3,4
            for n in range(2, 5):
                if len(words) >= n:
                    n_grams = list(ngrams(words, n))
                    n_gram_freq = Counter(n_grams)
                    
                    # Top 10 most common n-grams
                    most_common = n_gram_freq.most_common(10)
                    total_ngrams = len(n_grams)
                    
                    for i, (ngram, count) in enumerate(most_common):
                        features.append(count / total_ngrams)
                    
                    # Pad to 10 features
                    while len(features) % 10 != 0:
                        features.append(0.0)
            
            if not features:
                return np.array([]), 0.0
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"N-gram features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_readability_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate readability-based features."""
        try:
            if len(text.strip()) < 50:
                return np.array([]), 0.0
            
            features = []
            
            # Multiple readability metrics
            try:
                features.extend([
                    textstat.flesch_reading_ease(text) / 100.0,
                    textstat.flesch_kincaid_grade(text) / 20.0,  # Normalize
                    textstat.gunning_fog(text) / 20.0,
                    textstat.automated_readability_index(text) / 20.0,
                    textstat.coleman_liau_index(text) / 20.0,
                    textstat.linsear_write_formula(text) / 20.0,
                    textstat.dale_chall_readability_score(text) / 10.0,
                ])
            except Exception:
                features = [0.5] * 7  # Default values
            
            # Text complexity features
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            if words and sentences:
                features.extend([
                    len(set(words)) / len(words),  # Lexical diversity
                    np.mean([len(word) for word in words]) / 10.0,  # Avg word length
                    len(words) / len(sentences) / 20.0,  # Avg sentence length
                ])
            else:
                features.extend([0.0, 0.0, 0.0])
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Readability features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_sentiment_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate sentiment-based features."""
        try:
            if not self.config.enable_sentiment_analysis or len(text.strip()) < 10:
                return np.array([]), 0.0
            
            features = []
            
            # Overall sentiment
            sentiment_score = await self._analyze_sentiment(text)
            if sentiment_score is not None:
                features.append(sentiment_score)
            else:
                features.append(0.5)
            
            # Sentence-level sentiment analysis
            sentences = sent_tokenize(text)
            sentence_sentiments = []
            
            for sentence in sentences[:10]:  # Limit to first 10 sentences
                sent_score = await self._analyze_sentiment(sentence)
                if sent_score is not None:
                    sentence_sentiments.append(sent_score)
            
            if sentence_sentiments:
                features.extend([
                    np.mean(sentence_sentiments),
                    np.std(sentence_sentiments),
                    len([s for s in sentence_sentiments if s > 0.6]) / len(sentence_sentiments),  # Positive ratio
                    len([s for s in sentence_sentiments if s < 0.4]) / len(sentence_sentiments),  # Negative ratio
                ])
            else:
                features.extend([0.5, 0.0, 0.0, 0.0])
            
            # Emotion keywords
            positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'}
            negative_words = {'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate'}
            
            words = word_tokenize(text.lower())
            if words:
                positive_ratio = len([w for w in words if w in positive_words]) / len(words)
                negative_ratio = len([w for w in words if w in negative_words]) / len(words)
                features.extend([positive_ratio, negative_ratio])
            else:
                features.extend([0.0, 0.0])
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Sentiment features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_entity_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate named entity features."""
        try:
            if not self.config.enable_ner or self.nlp is None or len(text.strip()) < 10:
                return np.array([]), 0.0
            
            # Truncate text for performance
            if len(text) > 100000:
                text = text[:100000]
            
            doc = self.nlp(text)
            
            # Entity type frequencies
            entity_types = ['PERSON', 'ORG', 'GPE', 'MONEY', 'DATE', 'TIME', 'PERCENT']
            features = []
            
            total_entities = len(doc.ents)
            for ent_type in entity_types:
                count = len([ent for ent in doc.ents if ent.label_ == ent_type])
                features.append(count / total_entities if total_entities > 0 else 0.0)
            
            # Entity density
            features.append(total_entities / len(doc) if len(doc) > 0 else 0.0)
            
            # Unique entities ratio
            unique_entities = len(set([ent.text.lower() for ent in doc.ents]))
            features.append(unique_entities / total_entities if total_entities > 0 else 0.0)
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = min(1.0, total_entities / 10.0)  # Based on entity count
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Entity features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_syntactic_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate syntactic pattern features."""
        try:
            if not self.config.enable_pos_tagging or self.nlp is None or len(text.strip()) < 10:
                return np.array([]), 0.0
            
            # Truncate for performance
            if len(text) > 50000:
                text = text[:50000]
            
            doc = self.nlp(text)
            
            features = []
            
            # POS tag frequencies
            pos_tags = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET', 'ADP', 'CONJ']
            pos_counts = Counter([token.pos_ for token in doc])
            total_tokens = len(doc)
            
            for pos in pos_tags:
                features.append(pos_counts.get(pos, 0) / total_tokens if total_tokens > 0 else 0.0)
            
            # Dependency relations
            dep_relations = ['nsubj', 'dobj', 'iobj', 'nmod', 'amod', 'advmod', 'compound']
            dep_counts = Counter([token.dep_ for token in doc])
            
            for dep in dep_relations:
                features.append(dep_counts.get(dep, 0) / total_tokens if total_tokens > 0 else 0.0)
            
            # Sentence structure features
            sentences = [sent for sent in doc.sents]
            if sentences:
                avg_sent_length = np.mean([len(sent) for sent in sentences])
                features.append(avg_sent_length / 20.0)  # Normalize
                
                # Complex sentences ratio (sentences with subordinate clauses)
                complex_sents = len([sent for sent in sentences if any(token.dep_ in ['advcl', 'ccomp', 'xcomp'] for token in sent)])
                features.append(complex_sents / len(sentences))
            else:
                features.extend([0.0, 0.0])
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = min(1.0, total_tokens / 100.0)  # Based on token count
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Syntactic features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_lexical_features(self, text: str) -> Tuple[np.ndarray, float]:
        """Generate lexical diversity features."""
        try:
            if len(text.strip()) < 10:
                return np.array([]), 0.0
            
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha()]
            
            if len(words) < 5:
                return np.array([]), 0.0
            
            features = []
            
            # Type-Token Ratio
            unique_words = set(words)
            ttr = len(unique_words) / len(words)
            features.append(ttr)
            
            # Moving Average Type-Token Ratio (MATTR)
            window_size = min(100, len(words))
            if len(words) >= window_size:
                ttrs = []
                for i in range(len(words) - window_size + 1):
                    window = words[i:i + window_size]
                    window_ttr = len(set(window)) / len(window)
                    ttrs.append(window_ttr)
                mattr = np.mean(ttrs)
                features.append(mattr)
            else:
                features.append(ttr)
            
            # Word frequency distribution
            word_freq = Counter(words)
            
            # Hapax legomena (words that occur only once)
            hapax = len([word for word, count in word_freq.items() if count == 1])
            features.append(hapax / len(unique_words) if unique_words else 0.0)
            
            # Dis legomena (words that occur exactly twice)
            dis = len([word for word, count in word_freq.items() if count == 2])
            features.append(dis / len(unique_words) if unique_words else 0.0)
            
            # Yule's K (vocabulary richness)
            if len(word_freq) > 1:
                freq_counts = Counter(word_freq.values())
                yule_k = 10000 * (sum(freq * (freq_count ** 2) for freq, freq_count in freq_counts.items()) - len(words)) / (len(words) ** 2)
                features.append(yule_k / 1000.0)  # Normalize
            else:
                features.append(0.0)
            
            # Simpson's D (diversity index)
            if len(words) > 1:
                simpson_d = sum((count * (count - 1)) for count in word_freq.values()) / (len(words) * (len(words) - 1))
                features.append(1 - simpson_d)  # Simpson's diversity
            else:
                features.append(0.0)
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = min(1.0, len(unique_words) / 100.0)  # Based on vocabulary size
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Lexical features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_combined_fingerprint(
        self, original_text: str, cleaned_text: str
    ) -> Tuple[np.ndarray, float]:
        """Generate combined fingerprint from multiple features."""
        try:
            features_list = []
            confidences = []
            
            # Generate multiple fingerprints
            fingerprint_types = [
                TextFingerprintType.SEMANTIC_EMBEDDINGS,
                TextFingerprintType.STYLOMETRIC_FEATURES,
                TextFingerprintType.LINGUISTIC_PATTERNS,
                TextFingerprintType.LEXICAL_DIVERSITY
            ]
            
            for fp_type in fingerprint_types:
                try:
                    if fp_type == TextFingerprintType.SEMANTIC_EMBEDDINGS:
                        features, confidence = await self._generate_semantic_embeddings(cleaned_text)
                    elif fp_type == TextFingerprintType.STYLOMETRIC_FEATURES:
                        features, confidence = await self._generate_stylometric_features(original_text, cleaned_text)
                    elif fp_type == TextFingerprintType.LINGUISTIC_PATTERNS:
                        features, confidence = await self._generate_linguistic_patterns(cleaned_text)
                    elif fp_type == TextFingerprintType.LEXICAL_DIVERSITY:
                        features, confidence = await self._generate_lexical_features(cleaned_text)
                    
                    if len(features) > 0:
                        features_list.append(features)
                        confidences.append(confidence)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to generate {fp_type.value} for combined fingerprint: {e}")
            
            # Combine all features
            if features_list:
                combined_features = np.concatenate(features_list)
                combined_confidence = np.mean(confidences)
            else:
                combined_features = np.array([])
                combined_confidence = 0.0
            
            return combined_features, combined_confidence
            
        except Exception as e:
            self.logger.error(f"Combined fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    def _calculate_feature_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence based on feature quality."""
        try:
            if len(features) == 0:
                return 0.0
            
            # Calculate coefficient of variation
            mean_val = np.mean(np.abs(features))
            std_val = np.std(features)
            
            if mean_val == 0:
                return 0.0
            
            cv = std_val / mean_val
            confidence = min(1.0, cv)  # Higher variance = higher confidence
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    async def _generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of text content."""
        try:
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            self.logger.error(f"Content hash generation failed: {e}")
            return ""
    
    def _generate_fingerprint_id(
        self, content_hash: str, fingerprint_type: str, data: np.ndarray
    ) -> str:
        """Generate unique fingerprint identifier."""
        content = f"{content_hash}_{fingerprint_type}_{hash(data.tobytes())}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _store_fingerprints(
        self, fingerprints: List[TextFingerprint], creator_id: str
    ):
        """Store fingerprints in vector database."""
        try:
            for fingerprint in fingerprints:
                await self.vector_db.store_fingerprint(
                    fingerprint_id=fingerprint.fingerprint_id,
                    vector=fingerprint.data,
                    metadata={
                        'type': 'text',
                        'subtype': fingerprint.fingerprint_type.value,
                        'creator_id': creator_id,
                        'confidence': fingerprint.confidence,
                        'character_count': fingerprint.metadata.character_count,
                        'word_count': fingerprint.metadata.word_count,
                        'language': fingerprint.metadata.language.value if fingerprint.metadata.language else None,
                        'text_snippet': fingerprint.text_snippet,
                        'file_path': fingerprint.file_path,
                        'hash': fingerprint.hash_sha256,
                        'created_at': fingerprint.created_at.isoformat()
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to store fingerprints: {e}")
            raise
    
    async def find_similar_texts(
        self,
        fingerprint: TextFingerprint,
        similarity_threshold: float = 0.85,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar text content based on fingerprint."""
        try:
            # Search in vector database
            results = await self.vector_db.search_similar(
                vector=fingerprint.data,
                threshold=similarity_threshold,
                max_results=max_results,
                metadata_filter={'type': 'text', 'subtype': fingerprint.fingerprint_type.value}
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def analyze_text_quality(self, fingerprint: TextFingerprint) -> Dict[str, float]:
        """Analyze text quality metrics."""
        try:
            quality_metrics = {
                'confidence': fingerprint.confidence,
                'length_score': min(1.0, fingerprint.metadata.word_count / 500.0),  # 500 words baseline
                'readability_score': fingerprint.metadata.readability_score or 0.5,
                'lexical_diversity_score': fingerprint.metadata.lexical_diversity or 0.5,
                'language_confidence': 1.0 if fingerprint.metadata.language != TextLanguage.UNKNOWN else 0.5,
                'feature_completeness': 1.0 if len(fingerprint.data) > 0 else 0.0
            }
            
            # Overall quality score
            quality_metrics['overall_quality'] = np.mean(list(quality_metrics.values()))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {'overall_quality': 0.0}


# Factory function for creating text fingerprinting system
def create_text_fingerprinting_system(
    config: Optional[TextAnalysisConfig] = None
) -> TextFingerprintingSystem:
    """Create and initialize text fingerprinting system."""
    return TextFingerprintingSystem(config)


# Export public interface
__all__ = [
    'TextFingerprintingSystem',
    'TextFingerprint',
    'TextFingerprintType',
    'TextFormat',
    'TextLanguage',
    'TextMetadata',
    'TextAnalysisConfig',
    'create_text_fingerprinting_system'
]