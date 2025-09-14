"""Semantic Analysis Processor Module
===================================

Deep semantic content analysis engine for the IA Influencer Agent platform.
Provides intelligent content understanding, context analysis, and meaning extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Deep semantic content analysis with AI understanding
- Context and meaning analysis across content types
- Sentiment analysis with emotion detection
- Topic extraction and classification
- Intent detection and purpose analysis
- Semantic search capabilities
- Knowledge graph construction
- Multi-language support and analysis
"""

import asyncio
import logging
import time
import hashlib
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

# NLP and ML libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import torch
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline, BertTokenizer, BertModel
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of semantic analysis"""
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    TOPIC_EXTRACTION = "topic_extraction"
    INTENT_DETECTION = "intent_detection"
    ENTITY_RECOGNITION = "entity_recognition"
    CONTEXT_ANALYSIS = "context_analysis"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    LANGUAGE_DETECTION = "language_detection"
    READABILITY = "readability"
    BIAS_DETECTION = "bias_detection"

class SentimentLabel(Enum):
    """Sentiment classification labels"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class EmotionLabel(Enum):
    """Emotion classification labels"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class IntentLabel(Enum):
    """Intent classification labels"""
    INFORMATIONAL = "informational"
    ENTERTAINMENT = "entertainment"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    NEWS = "news"
    OPINION = "opinion"

@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    overall_sentiment: SentimentLabel
    confidence: float
    polarity_score: float  # -1 to 1
    subjectivity_score: float  # 0 to 1
    emotion_scores: Dict[EmotionLabel, float] = field(default_factory=dict)
    sentence_sentiments: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TopicAnalysis:
    """Topic analysis result"""
    main_topics: List[str]
    topic_scores: Dict[str, float]
    topic_keywords: Dict[str, List[str]]
    topic_coherence: float
    num_topics_detected: int
    topic_distribution: List[float] = field(default_factory=list)

@dataclass
class EntityRecognition:
    """Named entity recognition result"""
    entities: List[Dict[str, Any]]
    entity_types: Dict[str, List[str]]
    entity_relationships: List[Dict[str, Any]] = field(default_factory=list)
    entity_sentiment: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class IntentAnalysis:
    """Intent detection result"""
    primary_intent: IntentLabel
    intent_confidence: float
    intent_scores: Dict[IntentLabel, float]
    intent_keywords: List[str]
    purpose_description: str

@dataclass
class ContextAnalysis:
    """Context analysis result"""
    context_type: str
    domain: str
    formality_level: float  # 0-1, 0=informal, 1=formal
    complexity_level: float  # 0-1, 0=simple, 1=complex
    target_audience: str
    cultural_context: List[str] = field(default_factory=list)
    temporal_context: Optional[str] = None

@dataclass
class SemanticSimilarity:
    """Semantic similarity analysis"""
    similarity_scores: Dict[str, float]
    semantic_clusters: List[List[str]]
    key_concepts: List[str]
    conceptual_relationships: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class LanguageAnalysis:
    """Language detection and analysis"""
    detected_language: str
    language_confidence: float
    dialect_indicators: List[str]
    multilingual_segments: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ReadabilityAnalysis:
    """Readability analysis result"""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float
    coleman_liau_index: float
    readability_level: str  # elementary, middle_school, high_school, college, graduate
    average_sentence_length: float
    average_syllables_per_word: float

@dataclass
class SemanticAnalysisResult:
    """Comprehensive semantic analysis result"""
    analysis_id: str
    content_type: str
    text_content: str
    sentiment_analysis: Optional[SentimentAnalysis] = None
    topic_analysis: Optional[TopicAnalysis] = None
    entity_recognition: Optional[EntityRecognition] = None
    intent_analysis: Optional[IntentAnalysis] = None
    context_analysis: Optional[ContextAnalysis] = None
    semantic_similarity: Optional[SemanticSimilarity] = None
    language_analysis: Optional[LanguageAnalysis] = None
    readability_analysis: Optional[ReadabilityAnalysis] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentUnderstandingEngine:
    """Deep content understanding and semantic analysis engine"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.ContentUnderstandingEngine")
        self.config = config or {}
        
        # Initialize NLP models and resources
        self._initialize_nlp_resources()
        
        # Analysis configuration
        self.analysis_config = {
            'max_topics': self.config.get('max_topics', 10),
            'min_topic_probability': self.config.get('min_topic_probability', 0.1),
            'entity_confidence_threshold': self.config.get('entity_confidence_threshold', 0.7),
            'similarity_threshold': self.config.get('similarity_threshold', 0.8)
        }
    
    def _initialize_nlp_resources(self) -> None:
        """Initialize NLP libraries and download required resources"""
        try:
            if NLTK_AVAILABLE:
                # Download required NLTK data
                nltk_downloads = [
                    'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
                    'maxent_ne_chunker', 'words', 'vader_lexicon'
                ]
                
                for resource in nltk_downloads:
                    try:
                        nltk.data.find(f'tokenizers/{resource}')
                    except LookupError:
                        try:
                            nltk.download(resource, quiet=True)
                        except Exception:
                            pass
                
                # Initialize NLTK components
                self.lemmatizer = WordNetLemmatizer()
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                
                # Get stopwords
                try:
                    self.stop_words = set(stopwords.words('english'))
                except:
                    self.stop_words = set()
                
                self.logger.info("NLTK resources initialized")
            
            if SPACY_AVAILABLE:
                try:
                    # Try to load English model
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.info("spaCy model loaded successfully")
                except OSError:
                    # Model not installed, use basic tokenizer
                    self.nlp = None
                    self.logger.warning("spaCy English model not found")
            
            if TRANSFORMERS_AVAILABLE:
                # Initialize transformer models for advanced analysis
                try:
                    self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
                    self.bert_model = BertModel.from_pretrained('bert-base-uncased')
                    self.sentiment_pipeline = pipeline('sentiment-analysis')
                    self.logger.info("Transformer models initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to load transformer models: {e}")
                    self.bert_tokenizer = None
                    self.bert_model = None
                    self.sentiment_pipeline = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP resources: {str(e)}")
    
    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """
        Perform comprehensive sentiment analysis
        
        Args:
            text: Input text for sentiment analysis
            
        Returns:
            SentimentAnalysis with detailed sentiment information
        """
        try:
            sentiment_result = SentimentAnalysis(
                overall_sentiment=SentimentLabel.NEUTRAL,
                confidence=0.0,
                polarity_score=0.0,
                subjectivity_score=0.0
            )
            
            if NLTK_AVAILABLE and hasattr(self, 'sentiment_analyzer'):
                # VADER sentiment analysis
                scores = self.sentiment_analyzer.polarity_scores(text)
                
                # Determine overall sentiment
                compound_score = scores['compound']
                if compound_score >= 0.5:
                    sentiment_result.overall_sentiment = SentimentLabel.VERY_POSITIVE
                elif compound_score >= 0.1:
                    sentiment_result.overall_sentiment = SentimentLabel.POSITIVE
                elif compound_score <= -0.5:
                    sentiment_result.overall_sentiment = SentimentLabel.VERY_NEGATIVE
                elif compound_score <= -0.1:
                    sentiment_result.overall_sentiment = SentimentLabel.NEGATIVE
                else:
                    sentiment_result.overall_sentiment = SentimentLabel.NEUTRAL
                
                sentiment_result.polarity_score = compound_score
                sentiment_result.confidence = abs(compound_score)
                
                # Analyze sentence-level sentiment
                sentences = sent_tokenize(text)
                for i, sentence in enumerate(sentences):
                    sent_scores = self.sentiment_analyzer.polarity_scores(sentence)
                    sentiment_result.sentence_sentiments.append({
                        'sentence_index': i,
                        'sentence': sentence,
                        'sentiment_scores': sent_scores
                    })
            
            # Advanced sentiment analysis with transformers
            if TRANSFORMERS_AVAILABLE and self.sentiment_pipeline:
                try:
                    transformer_result = self.sentiment_pipeline(text[:512])  # Limit text length
                    if transformer_result:
                        result = transformer_result[0]
                        # Enhance confidence if transformer agrees
                        if result['label'].upper() in ['POSITIVE', 'NEGATIVE']:
                            sentiment_result.confidence = max(sentiment_result.confidence, result['score'])
                except Exception as e:
                    self.logger.debug(f"Transformer sentiment analysis failed: {e}")
            
            # Emotion detection (simplified)
            emotion_scores = await self._detect_emotions(text)
            sentiment_result.emotion_scores = emotion_scores
            
            return sentiment_result
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return SentimentAnalysis(
                overall_sentiment=SentimentLabel.NEUTRAL,
                confidence=0.0,
                polarity_score=0.0,
                subjectivity_score=0.0
            )
    
    async def _detect_emotions(self, text: str) -> Dict[EmotionLabel, float]:
        """Detect emotions in text using keyword-based approach"""
        emotion_keywords = {
            EmotionLabel.JOY: ['happy', 'joy', 'excited', 'pleased', 'delighted', 'cheerful', 'elated'],
            EmotionLabel.SADNESS: ['sad', 'depressed', 'unhappy', 'miserable', 'melancholy', 'sorrowful'],
            EmotionLabel.ANGER: ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'outraged'],
            EmotionLabel.FEAR: ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
            EmotionLabel.SURPRISE: ['surprised', 'amazed', 'astonished', 'shocked', 'stunned'],
            EmotionLabel.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled'],
            EmotionLabel.TRUST: ['trust', 'confident', 'secure', 'reliable', 'dependable'],
            EmotionLabel.ANTICIPATION: ['excited', 'eager', 'hopeful', 'expectant', 'anticipating']
        }
        
        text_lower = text.lower()
        words = word_tokenize(text_lower) if NLTK_AVAILABLE else text_lower.split()
        
        emotion_scores = {}
        total_emotional_words = 0
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in words)
            total_emotional_words += count
            emotion_scores[emotion] = count
        
        # Normalize scores
        if total_emotional_words > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = emotion_scores[emotion] / total_emotional_words
        
        return emotion_scores
    
    async def analyze_topics(self, text: str) -> TopicAnalysis:
        """
        Perform topic analysis and extraction
        
        Args:
            text: Input text for topic analysis
            
        Returns:
            TopicAnalysis with identified topics and keywords
        """
        try:
            if not SKLEARN_AVAILABLE:
                # Fallback to simple keyword extraction
                return await self._simple_topic_extraction(text)
            
            # Preprocess text
            processed_text = await self._preprocess_text_for_topics(text)
            
            if not processed_text.strip():
                return TopicAnalysis(
                    main_topics=[],
                    topic_scores={},
                    topic_keywords={},
                    topic_coherence=0.0,
                    num_topics_detected=0
                )
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            try:
                tfidf_matrix = vectorizer.fit_transform([processed_text])
                feature_names = vectorizer.get_feature_names_out()
            except ValueError:
                # Not enough vocabulary
                return await self._simple_topic_extraction(text)
            
            # Extract top keywords as topics
            tfidf_scores = tfidf_matrix.toarray()[0]
            top_indices = np.argsort(tfidf_scores)[::-1][:self.analysis_config['max_topics']]
            
            main_topics = []
            topic_scores = {}
            topic_keywords = {}
            
            for i, idx in enumerate(top_indices):
                if tfidf_scores[idx] > 0:
                    topic = feature_names[idx]
                    score = float(tfidf_scores[idx])
                    
                    main_topics.append(topic)
                    topic_scores[topic] = score
                    topic_keywords[topic] = [topic]  # Simple approach
            
            # Calculate topic coherence (simplified)
            topic_coherence = np.mean(list(topic_scores.values())) if topic_scores else 0.0
            
            return TopicAnalysis(
                main_topics=main_topics,
                topic_scores=topic_scores,
                topic_keywords=topic_keywords,
                topic_coherence=topic_coherence,
                num_topics_detected=len(main_topics)
            )
            
        except Exception as e:
            self.logger.error(f"Topic analysis failed: {str(e)}")
            return await self._simple_topic_extraction(text)
    
    async def _simple_topic_extraction(self, text: str) -> TopicAnalysis:
        """Simple fallback topic extraction using word frequency"""
        try:
            words = word_tokenize(text.lower()) if NLTK_AVAILABLE else text.lower().split()
            
            # Remove stopwords and short words
            if hasattr(self, 'stop_words'):
                words = [word for word in words if word not in self.stop_words and len(word) > 3]
            else:
                # Basic stopwords
                basic_stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                words = [word for word in words if word not in basic_stopwords and len(word) > 3]
            
            # Count word frequencies
            word_freq = Counter(words)
            top_words = word_freq.most_common(10)
            
            main_topics = [word for word, count in top_words]
            topic_scores = {word: count / len(words) for word, count in top_words}
            topic_keywords = {word: [word] for word, count in top_words}
            
            return TopicAnalysis(
                main_topics=main_topics,
                topic_scores=topic_scores,
                topic_keywords=topic_keywords,
                topic_coherence=0.5,  # Default coherence
                num_topics_detected=len(main_topics)
            )
            
        except Exception as e:
            self.logger.error(f"Simple topic extraction failed: {str(e)}")
            return TopicAnalysis(
                main_topics=[],
                topic_scores={},
                topic_keywords={},
                topic_coherence=0.0,
                num_topics_detected=0
            )
    
    async def _preprocess_text_for_topics(self, text: str) -> str:
        """Preprocess text for topic analysis"""
        try:
            # Basic cleaning
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            if NLTK_AVAILABLE:
                # Tokenize and lemmatize
                words = word_tokenize(text.lower())
                
                # Remove stopwords
                if hasattr(self, 'stop_words'):
                    words = [word for word in words if word not in self.stop_words]
                
                # Lemmatize
                if hasattr(self, 'lemmatizer'):
                    words = [self.lemmatizer.lemmatize(word) for word in words]
                
                return ' '.join(words)
            else:
                return text.lower()
                
        except Exception as e:
            self.logger.error(f"Text preprocessing failed: {str(e)}")
            return text
    
    async def recognize_entities(self, text: str) -> EntityRecognition:
        """
        Perform named entity recognition
        
        Args:
            text: Input text for entity recognition
            
        Returns:
            EntityRecognition with identified entities and relationships
        """
        try:
            entities = []
            entity_types = defaultdict(list)
            
            if SPACY_AVAILABLE and self.nlp:
                # Use spaCy for entity recognition
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    entity_info = {
                        'text': ent.text,
                        'label': ent.label_,
                        'description': spacy.explain(ent.label_),
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': 1.0  # spaCy doesn't provide confidence scores
                    }
                    entities.append(entity_info)
                    entity_types[ent.label_].append(ent.text)
            
            elif NLTK_AVAILABLE:
                # Fallback to NLTK
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity_text = ' '.join([token for token, pos in chunk.leaves()])
                        entity_info = {
                            'text': entity_text,
                            'label': chunk.label(),
                            'description': chunk.label(),
                            'start': 0,  # NLTK doesn't provide character positions easily
                            'end': 0,
                            'confidence': 0.8
                        }
                        entities.append(entity_info)
                        entity_types[chunk.label()].append(entity_text)
            
            # Analyze entity sentiment
            entity_sentiment = {}
            for entity in entities:
                if hasattr(self, 'sentiment_analyzer'):
                    ent_scores = self.sentiment_analyzer.polarity_scores(entity['text'])
                    entity_sentiment[entity['text']] = ent_scores
            
            return EntityRecognition(
                entities=entities,
                entity_types=dict(entity_types),
                entity_sentiment=entity_sentiment
            )
            
        except Exception as e:
            self.logger.error(f"Entity recognition failed: {str(e)}")
            return EntityRecognition(entities=[], entity_types={})
    
    async def detect_intent(self, text: str) -> IntentAnalysis:
        """
        Detect the intent and purpose of the text
        
        Args:
            text: Input text for intent detection
            
        Returns:
            IntentAnalysis with detected intent and confidence
        """
        try:
            # Intent detection using keyword-based approach
            intent_keywords = {
                IntentLabel.INFORMATIONAL: [
                    'information', 'facts', 'data', 'statistics', 'research', 'study',
                    'explain', 'describe', 'what', 'why', 'how', 'when', 'where'
                ],
                IntentLabel.ENTERTAINMENT: [
                    'funny', 'humor', 'joke', 'entertaining', 'fun', 'amusing',
                    'story', 'tale', 'comedy', 'hilarious', 'laugh'
                ],
                IntentLabel.COMMERCIAL: [
                    'buy', 'purchase', 'sale', 'discount', 'offer', 'deal',
                    'price', 'cost', 'payment', 'order', 'shop', 'store'
                ],
                IntentLabel.EDUCATIONAL: [
                    'learn', 'teach', 'education', 'tutorial', 'lesson', 'course',
                    'training', 'instruction', 'guide', 'knowledge', 'skill'
                ],
                IntentLabel.PROMOTIONAL: [
                    'promote', 'advertise', 'marketing', 'brand', 'campaign',
                    'announcement', 'launch', 'introduce', 'feature'
                ],
                IntentLabel.SOCIAL: [
                    'community', 'social', 'share', 'connect', 'network',
                    'friend', 'follow', 'like', 'comment', 'discuss'
                ],
                IntentLabel.NEWS: [
                    'news', 'breaking', 'report', 'update', 'announcement',
                    'event', 'happening', 'current', 'latest', 'today'
                ],
                IntentLabel.OPINION: [
                    'opinion', 'think', 'believe', 'feel', 'view', 'perspective',
                    'review', 'rating', 'recommend', 'suggest', 'advice'
                ]
            }
            
            text_lower = text.lower()
            words = word_tokenize(text_lower) if NLTK_AVAILABLE else text_lower.split()
            
            intent_scores = {}
            total_intent_words = 0
            
            for intent, keywords in intent_keywords.items():
                score = sum(1 for keyword in keywords if keyword in words)
                intent_scores[intent] = score
                total_intent_words += score
            
            # Normalize scores
            if total_intent_words > 0:
                for intent in intent_scores:
                    intent_scores[intent] = intent_scores[intent] / total_intent_words
            
            # Determine primary intent
            if intent_scores:
                primary_intent = max(intent_scores, key=intent_scores.get)
                intent_confidence = intent_scores[primary_intent]
            else:
                primary_intent = IntentLabel.INFORMATIONAL
                intent_confidence = 0.1
            
            # Extract intent keywords
            intent_keywords_found = []
            primary_keywords = intent_keywords.get(primary_intent, [])
            for keyword in primary_keywords:
                if keyword in text_lower:
                    intent_keywords_found.append(keyword)
            
            # Generate purpose description
            purpose_description = self._generate_purpose_description(primary_intent, intent_confidence)
            
            return IntentAnalysis(
                primary_intent=primary_intent,
                intent_confidence=intent_confidence,
                intent_scores=intent_scores,
                intent_keywords=intent_keywords_found,
                purpose_description=purpose_description
            )
            
        except Exception as e:
            self.logger.error(f"Intent detection failed: {str(e)}")
            return IntentAnalysis(
                primary_intent=IntentLabel.INFORMATIONAL,
                intent_confidence=0.0,
                intent_scores={},
                intent_keywords=[],
                purpose_description="Unable to determine intent"
            )
    
    def _generate_purpose_description(self, intent: IntentLabel, confidence: float) -> str:
        """Generate human-readable purpose description"""
        purpose_templates = {
            IntentLabel.INFORMATIONAL: "This content aims to provide information and educate the audience",
            IntentLabel.ENTERTAINMENT: "This content is designed to entertain and amuse the audience",
            IntentLabel.COMMERCIAL: "This content has commercial intent, promoting products or services",
            IntentLabel.EDUCATIONAL: "This content serves an educational purpose, teaching specific skills or knowledge",
            IntentLabel.PROMOTIONAL: "This content promotes a brand, product, or service",
            IntentLabel.SOCIAL: "This content encourages social interaction and community engagement",
            IntentLabel.NEWS: "This content delivers news or current event information",
            IntentLabel.OPINION: "This content expresses opinions, reviews, or personal perspectives"
        }
        
        base_description = purpose_templates.get(intent, "Content purpose unclear")
        
        if confidence > 0.7:
            return f"{base_description} (high confidence)"
        elif confidence > 0.4:
            return f"{base_description} (moderate confidence)"
        else:
            return f"{base_description} (low confidence)"
    
    async def analyze_context(self, text: str) -> ContextAnalysis:
        """
        Analyze context and domain of the text
        
        Args:
            text: Input text for context analysis
            
        Returns:
            ContextAnalysis with context information
        """
        try:
            # Domain detection using keyword matching
            domain_keywords = {
                'technology': ['software', 'computer', 'digital', 'tech', 'AI', 'algorithm', 'programming'],
                'business': ['company', 'business', 'market', 'profit', 'revenue', 'strategy', 'management'],
                'health': ['health', 'medical', 'doctor', 'treatment', 'disease', 'wellness', 'fitness'],
                'entertainment': ['movie', 'music', 'game', 'entertainment', 'celebrity', 'show', 'performance'],
                'education': ['education', 'school', 'university', 'student', 'teacher', 'learning', 'academic'],
                'sports': ['sport', 'game', 'team', 'player', 'competition', 'athlete', 'match'],
                'politics': ['politics', 'government', 'election', 'policy', 'political', 'vote', 'law'],
                'science': ['science', 'research', 'study', 'experiment', 'discovery', 'scientific', 'theory']
            }
            
            text_lower = text.lower()
            domain_scores = {}
            
            for domain, keywords in domain_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                domain_scores[domain] = score
            
            # Determine primary domain
            if domain_scores and max(domain_scores.values()) > 0:
                domain = max(domain_scores, key=domain_scores.get)
            else:
                domain = 'general'
            
            # Analyze formality level
            formality_level = await self._analyze_formality(text)
            
            # Analyze complexity level
            complexity_level = await self._analyze_complexity(text)
            
            # Determine target audience
            target_audience = await self._determine_target_audience(text, formality_level, complexity_level)
            
            return ContextAnalysis(
                context_type='textual',
                domain=domain,
                formality_level=formality_level,
                complexity_level=complexity_level,
                target_audience=target_audience
            )
            
        except Exception as e:
            self.logger.error(f"Context analysis failed: {str(e)}")
            return ContextAnalysis(
                context_type='unknown',
                domain='general',
                formality_level=0.5,
                complexity_level=0.5,
                target_audience='general'
            )
    
    async def _analyze_formality(self, text: str) -> float:
        """Analyze formality level of text"""
        formal_indicators = [
            'therefore', 'furthermore', 'however', 'nevertheless', 'consequently',
            'accordingly', 'subsequently', 'moreover', 'nonetheless'
        ]
        
        informal_indicators = [
            'gonna', 'wanna', 'yeah', 'ok', 'okay', 'cool', 'awesome',
            'like', 'totally', 'really', 'pretty', 'kinda', 'sorta'
        ]
        
        text_lower = text.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text_lower)
        
        if formal_count + informal_count == 0:
            return 0.5  # Neutral
        
        formality_score = formal_count / (formal_count + informal_count)
        return formality_score
    
    async def _analyze_complexity(self, text: str) -> float:
        """Analyze complexity level of text"""
        try:
            words = word_tokenize(text) if NLTK_AVAILABLE else text.split()
            sentences = sent_tokenize(text) if NLTK_AVAILABLE else text.split('.')
            
            if not words or not sentences:
                return 0.5
            
            # Average sentence length
            avg_sentence_length = len(words) / len(sentences)
            
            # Average word length
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Complex word count (words > 6 characters)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_word_ratio = complex_words / len(words) if words else 0
            
            # Combine metrics
            complexity_score = (
                (avg_sentence_length / 20) * 0.4 +  # Normalize by 20 words per sentence
                (avg_word_length / 10) * 0.3 +      # Normalize by 10 characters per word
                complex_word_ratio * 0.3
            )
            
            return min(complexity_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {str(e)}")
            return 0.5
    
    async def _determine_target_audience(self, text: str, formality: float, complexity: float) -> str:
        """Determine target audience based on text characteristics"""
        if complexity > 0.7 and formality > 0.7:
            return 'academic/professional'
        elif complexity > 0.6:
            return 'educated adult'
        elif formality < 0.3:
            return 'casual/young adult'
        elif complexity < 0.3:
            return 'general public'
        else:
            return 'general adult'
    
    async def calculate_semantic_similarity(self, texts: List[str]) -> SemanticSimilarity:
        """
        Calculate semantic similarity between texts
        
        Args:
            texts: List of texts to compare
            
        Returns:
            SemanticSimilarity with similarity scores and relationships
        """
        try:
            if not SKLEARN_AVAILABLE or len(texts) < 2:
                return SemanticSimilarity(
                    similarity_scores={},
                    semantic_clusters=[],
                    key_concepts=[]
                )
            
            # Vectorize texts
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Create similarity scores dictionary
            similarity_scores = {}
            for i in range(len(texts)):
                for j in range(i+1, len(texts)):
                    key = f"text_{i}_text_{j}"
                    similarity_scores[key] = float(similarity_matrix[i][j])
            
            # Identify key concepts
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.mean(axis=0).A1
            top_indices = np.argsort(tfidf_scores)[::-1][:20]
            key_concepts = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            # Simple clustering (group highly similar texts)
            threshold = self.analysis_config['similarity_threshold']
            clusters = []
            used_indices = set()
            
            for i in range(len(texts)):
                if i in used_indices:
                    continue
                
                cluster = [i]
                used_indices.add(i)
                
                for j in range(i+1, len(texts)):
                    if j not in used_indices and similarity_matrix[i][j] > threshold:
                        cluster.append(j)
                        used_indices.add(j)
                
                if len(cluster) > 1:
                    clusters.append([f"text_{idx}" for idx in cluster])
            
            return SemanticSimilarity(
                similarity_scores=similarity_scores,
                semantic_clusters=clusters,
                key_concepts=key_concepts
            )
            
        except Exception as e:
            self.logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return SemanticSimilarity(
                similarity_scores={},
                semantic_clusters=[],
                key_concepts=[]
            )
    
    async def detect_language(self, text: str) -> LanguageAnalysis:
        """
        Detect language and analyze linguistic characteristics
        
        Args:
            text: Input text for language detection
            
        Returns:
            LanguageAnalysis with language information
        """
        try:
            # Simple language detection using character patterns
            # This is a very basic implementation
            
            # English indicators
            english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
            english_score = sum(1 for word in english_words if word in text.lower())
            
            # French indicators  
            french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
            french_score = sum(1 for word in french_words if word in text.lower())
            
            # Spanish indicators
            spanish_words = ['el', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no']
            spanish_score = sum(1 for word in spanish_words if word in text.lower())
            
            # German indicators
            german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
            german_score = sum(1 for word in german_words if word in text.lower())
            
            scores = {
                'english': english_score,
                'french': french_score,
                'spanish': spanish_score,
                'german': german_score
            }
            
            if max(scores.values()) > 0:
                detected_language = max(scores, key=scores.get)
                confidence = scores[detected_language] / sum(scores.values())
            else:
                detected_language = 'unknown'
                confidence = 0.0
            
            return LanguageAnalysis(
                detected_language=detected_language,
                language_confidence=confidence,
                dialect_indicators=[]
            )
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {str(e)}")
            return LanguageAnalysis(
                detected_language='unknown',
                language_confidence=0.0,
                dialect_indicators=[]
            )
    
    async def analyze_readability(self, text: str) -> ReadabilityAnalysis:
        """
        Analyze readability metrics of text
        
        Args:
            text: Input text for readability analysis
            
        Returns:
            ReadabilityAnalysis with readability scores
        """
        try:
            if NLTK_AVAILABLE:
                sentences = sent_tokenize(text)
                words = word_tokenize(text)
            else:
                sentences = text.split('.')
                words = text.split()
            
            if not sentences or not words:
                return ReadabilityAnalysis(
                    flesch_reading_ease=0.0,
                    flesch_kincaid_grade=0.0,
                    automated_readability_index=0.0,
                    coleman_liau_index=0.0,
                    readability_level='unknown',
                    average_sentence_length=0.0,
                    average_syllables_per_word=0.0
                )
            
            # Basic metrics
            num_sentences = len([s for s in sentences if s.strip()])
            num_words = len(words)
            num_syllables = sum(self._count_syllables(word) for word in words)
            
            if num_sentences == 0 or num_words == 0:
                return ReadabilityAnalysis(
                    flesch_reading_ease=0.0,
                    flesch_kincaid_grade=0.0,
                    automated_readability_index=0.0,
                    coleman_liau_index=0.0,
                    readability_level='unknown',
                    average_sentence_length=0.0,
                    average_syllables_per_word=0.0
                )
            
            avg_sentence_length = num_words / num_sentences
            avg_syllables_per_word = num_syllables / num_words
            
            # Flesch Reading Ease
            flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            # Flesch-Kincaid Grade Level
            flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
            
            # Automated Readability Index (simplified)
            characters = sum(len(word) for word in words)
            ari = (4.71 * characters / num_words) + (0.5 * num_words / num_sentences) - 21.43
            
            # Coleman-Liau Index (simplified)
            letters_per_100_words = (characters / num_words) * 100
            sentences_per_100_words = (num_sentences / num_words) * 100
            coleman_liau = 0.0588 * letters_per_100_words - 0.296 * sentences_per_100_words - 15.8
            
            # Determine readability level
            if flesch_reading_ease >= 90:
                readability_level = 'elementary'
            elif flesch_reading_ease >= 80:
                readability_level = 'middle_school'
            elif flesch_reading_ease >= 70:
                readability_level = 'high_school'
            elif flesch_reading_ease >= 60:
                readability_level = 'college'
            else:
                readability_level = 'graduate'
            
            return ReadabilityAnalysis(
                flesch_reading_ease=flesch_reading_ease,
                flesch_kincaid_grade=flesch_kincaid_grade,
                automated_readability_index=ari,
                coleman_liau_index=coleman_liau,
                readability_level=readability_level,
                average_sentence_length=avg_sentence_length,
                average_syllables_per_word=avg_syllables_per_word
            )
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {str(e)}")
            return ReadabilityAnalysis(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                automated_readability_index=0.0,
                coleman_liau_index=0.0,
                readability_level='unknown',
                average_sentence_length=0.0,
                average_syllables_per_word=0.0
            )
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified approach)"""
        word = word.lower().strip(".,!?;:")
        count = 0
        vowels = "aeiouy"
        
        if word == '':
            return 0
        
        if word[0] in vowels:
            count += 1
        
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        
        if word.endswith("e"):
            count -= 1
        
        if count == 0:
            count += 1
        
        return count

class SemanticAnalysisProcessor:
    """
    Deep semantic content analysis processor for the IA Influencer Agent platform
    
    Provides comprehensive semantic understanding, context analysis,
    and meaning extraction using advanced NLP techniques.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.SemanticAnalysisProcessor")
        self.config = config or {}
        
        # Initialize content understanding engine
        self.understanding_engine = ContentUnderstandingEngine(config.get('understanding_engine', {}))
        
        # Analysis statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'content_types_analyzed': set(),
            'languages_detected': set(),
            'total_processing_time': 0.0,
            'analysis_types_performed': defaultdict(int)
        }
        
        self.logger.info("SemanticAnalysisProcessor initialized successfully")
    
    async def analyze_content_semantics(
        self,
        content_data: bytes,
        content_type: str = 'text',
        analysis_types: Optional[List[AnalysisType]] = None,
        language_hint: Optional[str] = None
    ) -> SemanticAnalysisResult:
        """
        Perform comprehensive semantic analysis of content
        
        Args:
            content_data: Raw content bytes
            content_type: Type of content (text, audio, video, image)
            analysis_types: Specific types of analysis to perform
            language_hint: Hint about content language
            
        Returns:
            SemanticAnalysisResult with comprehensive semantic analysis
        """
        try:
            start_time = time.time()
            analysis_id = hashlib.md5(f"{time.time()}_{content_type}".encode()).hexdigest()
            
            self.logger.info(f"Starting semantic analysis: {analysis_id}")
            
            # Extract text content
            if content_type == 'text':
                text_content = content_data.decode('utf-8', errors='ignore')
            else:
                # For non-text content, this would require additional processing
                # For now, return basic analysis
                text_content = "Non-text content analysis not fully implemented"
            
            if not text_content.strip():
                return SemanticAnalysisResult(
                    analysis_id=analysis_id,
                    content_type=content_type,
                    text_content=text_content,
                    processing_time=time.time() - start_time,
                    confidence_score=0.0
                )
            
            # Determine analysis types to perform
            if analysis_types is None:
                analysis_types = [
                    AnalysisType.SENTIMENT,
                    AnalysisType.TOPIC_EXTRACTION,
                    AnalysisType.ENTITY_RECOGNITION,
                    AnalysisType.INTENT_DETECTION,
                    AnalysisType.CONTEXT_ANALYSIS,
                    AnalysisType.LANGUAGE_DETECTION,
                    AnalysisType.READABILITY
                ]
            
            # Perform analyses
            result = SemanticAnalysisResult(
                analysis_id=analysis_id,
                content_type=content_type,
                text_content=text_content
            )
            
            # Sentiment analysis
            if AnalysisType.SENTIMENT in analysis_types:
                result.sentiment_analysis = await self.understanding_engine.analyze_sentiment(text_content)
                self.analysis_stats['analysis_types_performed']['sentiment'] += 1
            
            # Topic analysis
            if AnalysisType.TOPIC_EXTRACTION in analysis_types:
                result.topic_analysis = await self.understanding_engine.analyze_topics(text_content)
                self.analysis_stats['analysis_types_performed']['topic_extraction'] += 1
            
            # Entity recognition
            if AnalysisType.ENTITY_RECOGNITION in analysis_types:
                result.entity_recognition = await self.understanding_engine.recognize_entities(text_content)
                self.analysis_stats['analysis_types_performed']['entity_recognition'] += 1
            
            # Intent detection
            if AnalysisType.INTENT_DETECTION in analysis_types:
                result.intent_analysis = await self.understanding_engine.detect_intent(text_content)
                self.analysis_stats['analysis_types_performed']['intent_detection'] += 1
            
            # Context analysis
            if AnalysisType.CONTEXT_ANALYSIS in analysis_types:
                result.context_analysis = await self.understanding_engine.analyze_context(text_content)
                self.analysis_stats['analysis_types_performed']['context_analysis'] += 1
            
            # Language detection
            if AnalysisType.LANGUAGE_DETECTION in analysis_types:
                result.language_analysis = await self.understanding_engine.detect_language(text_content)
                self.analysis_stats['analysis_types_performed']['language_detection'] += 1
                if result.language_analysis:
                    self.analysis_stats['languages_detected'].add(result.language_analysis.detected_language)
            
            # Readability analysis
            if AnalysisType.READABILITY in analysis_types:
                result.readability_analysis = await self.understanding_engine.analyze_readability(text_content)
                self.analysis_stats['analysis_types_performed']['readability'] += 1
            
            # Calculate overall confidence score
            result.confidence_score = self._calculate_confidence_score(result)
            
            # Set processing time
            result.processing_time = time.time() - start_time
            
            # Update statistics
            self._update_analysis_stats(result, content_type)
            
            self.logger.info(f"Semantic analysis completed: {analysis_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {str(e)}")
            return SemanticAnalysisResult(
                analysis_id=analysis_id if 'analysis_id' in locals() else "",
                content_type=content_type,
                text_content="",
                processing_time=0.0,
                confidence_score=0.0,
                metadata={'error': str(e)}
            )
    
    def _calculate_confidence_score(self, result: SemanticAnalysisResult) -> float:
        """Calculate overall confidence score for the analysis"""
        confidence_scores = []
        
        if result.sentiment_analysis:
            confidence_scores.append(result.sentiment_analysis.confidence)
        
        if result.topic_analysis:
            confidence_scores.append(result.topic_analysis.topic_coherence)
        
        if result.intent_analysis:
            confidence_scores.append(result.intent_analysis.intent_confidence)
        
        if result.language_analysis:
            confidence_scores.append(result.language_analysis.language_confidence)
        
        # Base confidence on available analyses
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        else:
            return 0.5  # Default confidence
    
    def _update_analysis_stats(self, result -> None: SemanticAnalysisResult, content_type -> None: str) -> None:
        """Update analysis statistics"""
        self.analysis_stats['total_analyses'] += 1
        
        if result.confidence_score > 0.3:  # Consider successful if confidence > 30%
            self.analysis_stats['successful_analyses'] += 1
        
        self.analysis_stats['content_types_analyzed'].add(content_type)
        self.analysis_stats['total_processing_time'] += result.processing_time
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        stats = self.analysis_stats.copy()
        stats['content_types_analyzed'] = list(stats['content_types_analyzed'])
        stats['languages_detected'] = list(stats['languages_detected'])
        stats['analysis_types_performed'] = dict(stats['analysis_types_performed'])
        stats['success_rate'] = (
            stats['successful_analyses'] / stats['total_analyses']
            if stats['total_analyses'] > 0 else 0
        )
        stats['average_processing_time'] = (
            stats['total_processing_time'] / stats['total_analyses']
            if stats['total_analyses'] > 0 else 0
        )
        return stats
    
    async def compare_content_semantics(
        self,
        content_list: List[Tuple[bytes, str]]  # List of (content_data, content_type)
    ) -> Dict[str, Any]:
        """
        Compare semantic characteristics across multiple content pieces
        
        Args:
            content_list: List of content data and types to compare
            
        Returns:
            Dictionary with comparative semantic analysis
        """
        try:
            if len(content_list) < 2:
                return {'error': 'At least 2 content pieces required for comparison'}
            
            # Analyze each content piece
            analyses = []
            texts = []
            
            for i, (content_data, content_type) in enumerate(content_list):
                analysis = await self.analyze_content_semantics(content_data, content_type)
                analyses.append(analysis)
                texts.append(analysis.text_content)
            
            # Calculate semantic similarity
            similarity_analysis = await self.understanding_engine.calculate_semantic_similarity(texts)
            
            # Compare sentiment patterns
            sentiment_comparison = self._compare_sentiments(analyses)
            
            # Compare topics
            topic_comparison = self._compare_topics(analyses)
            
            # Compare intents
            intent_comparison = self._compare_intents(analyses)
            
            return {
                'semantic_similarity': similarity_analysis.__dict__,
                'sentiment_comparison': sentiment_comparison,
                'topic_comparison': topic_comparison,
                'intent_comparison': intent_comparison,
                'individual_analyses': [analysis.__dict__ for analysis in analyses]
            }
            
        except Exception as e:
            self.logger.error(f"Content comparison failed: {str(e)}")
            return {'error': str(e)}
    
    def _compare_sentiments(self, analyses: List[SemanticAnalysisResult]) -> Dict[str, Any]:
        """Compare sentiment patterns across analyses"""
        sentiments = []
        confidences = []
        
        for analysis in analyses:
            if analysis.sentiment_analysis:
                sentiments.append(analysis.sentiment_analysis.overall_sentiment.value)
                confidences.append(analysis.sentiment_analysis.confidence)
        
        return {
            'sentiments': sentiments,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'sentiment_consistency': len(set(sentiments)) == 1 if sentiments else False
        }
    
    def _compare_topics(self, analyses: List[SemanticAnalysisResult]) -> Dict[str, Any]:
        """Compare topic patterns across analyses"""
        all_topics = []
        topic_similarities = []
        
        for analysis in analyses:
            if analysis.topic_analysis:
                all_topics.extend(analysis.topic_analysis.main_topics)
        
        # Find common topics
        topic_counts = Counter(all_topics)
        common_topics = [topic for topic, count in topic_counts.items() if count > 1]
        
        return {
            'all_topics': list(set(all_topics)),
            'common_topics': common_topics,
            'topic_diversity': len(set(all_topics)),
            'topic_overlap_ratio': len(common_topics) / len(set(all_topics)) if all_topics else 0
        }
    
    def _compare_intents(self, analyses: List[SemanticAnalysisResult]) -> Dict[str, Any]:
        """Compare intent patterns across analyses"""
        intents = []
        confidences = []
        
        for analysis in analyses:
            if analysis.intent_analysis:
                intents.append(analysis.intent_analysis.primary_intent.value)
                confidences.append(analysis.intent_analysis.intent_confidence)
        
        return {
            'intents': intents,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'intent_consistency': len(set(intents)) == 1 if intents else False,
            'intent_diversity': len(set(intents))
        }
    
    async def process(self, content_data: bytes, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main processing interface for compatibility with other processors
        
        Args:
            content_data: Raw content bytes to process
            config: Processing configuration
            
        Returns:
            Processing result dictionary
        """
        try:
            processing_config = config or {}
            
            # Extract configuration
            content_type = processing_config.get('content_type', 'text')
            analysis_types_str = processing_config.get('analysis_types', [])
            language_hint = processing_config.get('language_hint')
            
            # Convert analysis types to enum
            analysis_types = None
            if analysis_types_str:
                try:
                    analysis_types = [AnalysisType(t) for t in analysis_types_str]
                except ValueError as e:
                    self.logger.warning(f"Invalid analysis type: {e}")
            
            # Perform semantic analysis
            result = await self.analyze_content_semantics(
                content_data=content_data,
                content_type=content_type,
                analysis_types=analysis_types,
                language_hint=language_hint
            )
            
            # Convert result to dictionary for JSON serialization
            result_dict = {
                'success': True,
                'analysis_id': result.analysis_id,
                'content_type': result.content_type,
                'text_content': result.text_content[:500] + '...' if len(result.text_content) > 500 else result.text_content,
                'processing_time': result.processing_time,
                'confidence_score': result.confidence_score,
                'metadata': result.metadata
            }
            
            # Add analysis results
            if result.sentiment_analysis:
                result_dict['sentiment_analysis'] = {
                    'overall_sentiment': result.sentiment_analysis.overall_sentiment.value,
                    'confidence': result.sentiment_analysis.confidence,
                    'polarity_score': result.sentiment_analysis.polarity_score,
                    'emotion_scores': {k.value: v for k, v in result.sentiment_analysis.emotion_scores.items()}
                }
            
            if result.topic_analysis:
                result_dict['topic_analysis'] = {
                    'main_topics': result.topic_analysis.main_topics,
                    'topic_scores': result.topic_analysis.topic_scores,
                    'num_topics_detected': result.topic_analysis.num_topics_detected,
                    'topic_coherence': result.topic_analysis.topic_coherence
                }
            
            if result.entity_recognition:
                result_dict['entity_recognition'] = {
                    'entities': result.entity_recognition.entities,
                    'entity_types': result.entity_recognition.entity_types
                }
            
            if result.intent_analysis:
                result_dict['intent_analysis'] = {
                    'primary_intent': result.intent_analysis.primary_intent.value,
                    'intent_confidence': result.intent_analysis.intent_confidence,
                    'intent_keywords': result.intent_analysis.intent_keywords,
                    'purpose_description': result.intent_analysis.purpose_description
                }
            
            if result.context_analysis:
                result_dict['context_analysis'] = {
                    'domain': result.context_analysis.domain,
                    'formality_level': result.context_analysis.formality_level,
                    'complexity_level': result.context_analysis.complexity_level,
                    'target_audience': result.context_analysis.target_audience
                }
            
            if result.language_analysis:
                result_dict['language_analysis'] = {
                    'detected_language': result.language_analysis.detected_language,
                    'language_confidence': result.language_analysis.language_confidence
                }
            
            if result.readability_analysis:
                result_dict['readability_analysis'] = {
                    'flesch_reading_ease': result.readability_analysis.flesch_reading_ease,
                    'readability_level': result.readability_analysis.readability_level,
                    'average_sentence_length': result.readability_analysis.average_sentence_length
                }
            
            return result_dict
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Export main classes and functions
__all__ = [
    'SemanticAnalysisProcessor',
    'ContentUnderstandingEngine',
    'SemanticAnalysisResult',
    'SentimentAnalysis',
    'TopicAnalysis',
    'EntityRecognition',
    'IntentAnalysis',
    'ContextAnalysis',
    'SemanticSimilarity',
    'LanguageAnalysis',
    'ReadabilityAnalysis',
    'AnalysisType',
    'SentimentLabel',
    'EmotionLabel',
    'IntentLabel'
]