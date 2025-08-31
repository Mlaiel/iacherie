"""Semantic Processor - Advanced NLP and Semantic Understanding Engine

Provides comprehensive semantic processing capabilities for content understanding,
sentiment analysis, entity extraction, and contextual analysis. Integrates
state-of-the-art NLP models for deep content comprehension.

Features:
- Multi-language semantic analysis
- Sentiment and emotion detection
- Named entity recognition and linking
- Content categorization and tagging
- Contextual similarity matching
- Intent recognition and extraction

Author: Fahed Mlaiel <mlaiel@live.de>
"""import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime
import json
import re

# NLP Libraries
import spacy
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertModel
)
import torch
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Semantic libraries
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Core Dependencies
from ..adapters.semantic_adapter import SemanticAdapter
from ..processors.language_processor import LanguageProcessor
from ..engines.nlp_engine import NLPEngine
from ..storage.semantic_storage import SemanticStorage


class LanguageCode(Enum):
    """Supported language codes"""    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    AUTO = "auto"


class SemanticTask(Enum):
    """Available semantic processing tasks"""    SENTIMENT_ANALYSIS = "sentiment_analysis"
    EMOTION_DETECTION = "emotion_detection"
    ENTITY_EXTRACTION = "entity_extraction"
    CONTENT_CLASSIFICATION = "content_classification"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    INTENT_RECOGNITION = "intent_recognition"
    TOPIC_MODELING = "topic_modeling"
    KEYWORD_EXTRACTION = "keyword_extraction"


@dataclass
class SentimentResult:
    """Sentiment analysis result"""    overall_sentiment: str  # positive, negative, neutral
    confidence: float
    scores: Dict[str, float]  # detailed sentiment scores
    emotional_tone: Optional[str] = None
    intensity: Optional[float] = None


@dataclass
class EntityResult:
    """Named entity recognition result"""    entities: List[Dict[str, Any]]
    entity_types: List[str]
    entity_links: Dict[str, str]
    confidence_scores: Dict[str, float]


@dataclass
class ClassificationResult:
    """Content classification result"""    primary_category: str
    categories: Dict[str, float]
    confidence: float
    subcategories: Optional[Dict[str, float]] = None


@dataclass
class SimilarityResult:
    """Similarity analysis result"""    similarity_score: float
    semantic_distance: float
    common_themes: List[str]
    distinctive_features: Dict[str, List[str]]


@dataclass
class SemanticAnalysisResult:
    """Comprehensive semantic analysis result"""    analysis_id: str
    input_text: str
    language: LanguageCode
    sentiment: SentimentResult
    entities: EntityResult
    classification: ClassificationResult
    keywords: List[str]
    topics: List[Dict[str, Any]]
    embedding: np.ndarray
    processing_time: float
    confidence_score: float
    metadata: Dict[str, Any]


class SemanticProcessor:
    """    Advanced semantic processing engine for comprehensive text understanding
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize semantic processor
        
        Args:
            config: Configuration dictionary
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize models and components
        self._initialize_models()
        self._initialize_processors()
        self._initialize_storage()
        
        # Processing cache and performance tracking
        self.analysis_cache = {}
        self.performance_metrics = {
            "total_analyses": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "accuracy_scores": {}
        }
        
        # Language detection and processing
        self.supported_languages = [lang.value for lang in LanguageCode if lang != LanguageCode.AUTO]
    
    def _initialize_models(self) -> None:
        """Initialize NLP and semantic models"""        try:
            # Download required NLTK data
            try:
                nltk.download('vader_lexicon', quiet=True)
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            except:
                pass
            
            # Initialize spaCy models for different languages
            self.nlp_models = {}
            language_models = {
                'en': 'en_core_web_sm',
                'de': 'de_core_news_sm', 
                'fr': 'fr_core_news_sm',
                'es': 'es_core_news_sm'
            }
            
            for lang, model_name in language_models.items():
                try:
                    self.nlp_models[lang] = spacy.load(model_name)
                except OSError:
                    self.logger.warning(f"SpaCy model {model_name} not found, using English model")
                    self.nlp_models[lang] = spacy.load('en_core_web_sm')
            
            # Initialize transformers models
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize sentence transformer for embeddings
            self.sentence_transformer = SentenceTransformer(
                'sentence-transformers/all-MiniLM-L6-v2'
            )
            
            # Initialize BERT for contextual understanding
            self.bert_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = AutoModel.from_pretrained('bert-base-uncased')
            
            # Initialize classification models
            self.classification_models = {
                'content_type': pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=0 if torch.cuda.is_available() else -1
                )
            }
            
            # Initialize TF-IDF for keyword extraction
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            # Initialize NLTK sentiment analyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # Initialize FAISS index for similarity search
            self.embedding_dimension = 384  # MiniLM embedding dimension
            self.similarity_index = faiss.IndexFlatIP(self.embedding_dimension)
            self.indexed_texts = []
            
            self.logger.info("Semantic models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize semantic models: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize semantic processors"""        self.semantic_adapter = SemanticAdapter(self.config)
        self.language_processor = LanguageProcessor(self.config)
        self.nlp_engine = NLPEngine(self.config)
    
    def _initialize_storage(self) -> None:
        """Initialize semantic storage"""        self.semantic_storage = SemanticStorage(self.config)
    
    async def analyze_text(
        self,
        text: str,
        language: LanguageCode = LanguageCode.AUTO,
        tasks: Optional[List[SemanticTask]] = None
    ) -> SemanticAnalysisResult:
        """        Perform comprehensive semantic analysis on text
        
        Args:
            text: Input text to analyze
            language: Language code (auto-detect if not specified)
            tasks: Specific tasks to perform (all if not specified)
            
        Returns:
            SemanticAnalysisResult: Comprehensive analysis results
        """        start_time = datetime.now()
        analysis_id = self._generate_analysis_id(text)
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(text, language, tasks)
            if cache_key in self.analysis_cache:
                self.logger.info(f"Cache hit for analysis: {analysis_id}")
                return self.analysis_cache[cache_key]
            
            # Detect language if auto
            if language == LanguageCode.AUTO:
                language = await self._detect_language(text)
            
            # Perform all requested analyses
            if tasks is None:
                tasks = list(SemanticTask)
            
            # Sentiment analysis
            sentiment_result = await self._analyze_sentiment(text, language)
            
            # Entity extraction
            entity_result = await self._extract_entities(text, language)
            
            # Content classification
            classification_result = await self._classify_content(text, language)
            
            # Keyword extraction
            keywords = await self._extract_keywords(text, language)
            
            # Topic modeling
            topics = await self._extract_topics(text, language)
            
            # Generate embeddings
            embedding = await self._generate_embeddings(text)
            
            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(
                sentiment_result, entity_result, classification_result
            )
            
            # Create result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = SemanticAnalysisResult(
                analysis_id=analysis_id,
                input_text=text,
                language=language,
                sentiment=sentiment_result,
                entities=entity_result,
                classification=classification_result,
                keywords=keywords,
                topics=topics,
                embedding=embedding,
                processing_time=processing_time,
                confidence_score=confidence_score,
                metadata={
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "sentence_count": len([s for s in text.split('.') if s.strip()]),
                    "tasks_performed": [task.value for task in tasks]
                }
            )
            
            # Cache result
            self.analysis_cache[cache_key] = result
            
            # Update performance metrics
            self._update_performance_metrics(processing_time)
            
            self.logger.info(f"Semantic analysis {analysis_id} completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed for {analysis_id}: {e}")
            raise
    
    async def _detect_language(self, text: str) -> LanguageCode:
        """Detect text language"""        try:
            # Use langdetect or simple heuristics
            from langdetect import detect
            detected = detect(text)
            
            # Map to supported languages
            language_mapping = {
                'en': LanguageCode.ENGLISH,
                'fr': LanguageCode.FRENCH,
                'de': LanguageCode.GERMAN,
                'es': LanguageCode.SPANISH,
                'it': LanguageCode.ITALIAN,
                'pt': LanguageCode.PORTUGUESE
            }
            
            return language_mapping.get(detected, LanguageCode.ENGLISH)
            
        except Exception:
            # Fallback to English if detection fails
            return LanguageCode.ENGLISH
    
    async def _analyze_sentiment(self, text: str, language: LanguageCode) -> SentimentResult:
        """Analyze sentiment and emotional tone"""        try:
            # VADER sentiment analysis (works well for social media text)
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Transformer-based sentiment analysis
            transformer_result = self.sentiment_model(text)[0]
            
            # Emotion detection
            emotion_result = self.emotion_model(text)[0]
            
            # Combine results
            if transformer_result['label'] == 'LABEL_2':  # Positive
                overall_sentiment = 'positive'
                confidence = transformer_result['score']
            elif transformer_result['label'] == 'LABEL_0':  # Negative
                overall_sentiment = 'negative'
                confidence = transformer_result['score']
            else:  # Neutral
                overall_sentiment = 'neutral'
                confidence = transformer_result['score']
            
            # Calculate intensity
            intensity = max(abs(vader_scores['compound']), transformer_result['score'])
            
            return SentimentResult(
                overall_sentiment=overall_sentiment,
                confidence=confidence,
                scores={
                    'positive': vader_scores['pos'],
                    'negative': vader_scores['neg'],
                    'neutral': vader_scores['neu'],
                    'compound': vader_scores['compound'],
                    'transformer_score': transformer_result['score']
                },
                emotional_tone=emotion_result['label'],
                intensity=intensity
            )
            
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {e}")
            return SentimentResult(
                overall_sentiment='neutral',
                confidence=0.5,
                scores={'positive': 0.33, 'negative': 0.33, 'neutral': 0.34, 'compound': 0.0}
            )
    
    async def _extract_entities(self, text: str, language: LanguageCode) -> EntityResult:
        """Extract named entities and their relationships"""        try:
            # Get appropriate spaCy model
            nlp_model = self.nlp_models.get(language.value, self.nlp_models['en'])
            
            # Process text
            doc = nlp_model(text)
            
            # Extract entities
            entities = []
            entity_types = set()
            confidence_scores = {}
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_)
                }
                entities.append(entity_info)
                entity_types.add(ent.label_)
                confidence_scores[ent.text] = 0.8  # spaCy doesn't provide confidence scores directly
            
            # Entity linking (simplified)
            entity_links = {}
            for entity in entities:
                if entity['label'] in ['PERSON', 'ORG', 'GPE']:
                    # This would typically connect to a knowledge base
                    entity_links[entity['text']] = f"wiki:{entity['text'].replace(' ', '_')}"
            
            return EntityResult(
                entities=entities,
                entity_types=list(entity_types),
                entity_links=entity_links,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            self.logger.warning(f"Entity extraction failed: {e}")
            return EntityResult(
                entities=[],
                entity_types=[],
                entity_links={},
                confidence_scores={}
            )
    
    async def _classify_content(self, text: str, language: LanguageCode) -> ClassificationResult:
        """Classify content into categories"""        try:
            # Define content categories
            content_categories = [
                "entertainment", "music", "education", "technology", "business",
                "sports", "news", "lifestyle", "travel", "food", "fashion",
                "gaming", "art", "science", "politics", "health"
            ]
            
            # Use zero-shot classification
            classification_result = self.classification_models['content_type'](
                text, content_categories
            )
            
            # Extract results
            primary_category = classification_result['labels'][0]
            categories = dict(zip(
                classification_result['labels'],
                classification_result['scores']
            ))
            confidence = classification_result['scores'][0]
            
            # Add subcategories for specific domains
            subcategories = {}
            if primary_category == "music":
                music_subcategories = ["pop", "rock", "hip-hop", "electronic", "classical", "jazz"]
                subresult = self.classification_models['content_type'](text, music_subcategories)
                subcategories = dict(zip(subresult['labels'], subresult['scores']))
            
            return ClassificationResult(
                primary_category=primary_category,
                categories=categories,
                confidence=confidence,
                subcategories=subcategories if subcategories else None
            )
            
        except Exception as e:
            self.logger.warning(f"Content classification failed: {e}")
            return ClassificationResult(
                primary_category="general",
                categories={"general": 1.0},
                confidence=0.5
            )
    
    async def _extract_keywords(self, text: str, language: LanguageCode) -> List[str]:
        """Extract important keywords and phrases"""        try:
            # Get spaCy model
            nlp_model = self.nlp_models.get(language.value, self.nlp_models['en'])
            doc = nlp_model(text)
            
            # Extract keywords using various methods
            keywords = set()
            
            # Method 1: Named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT']:
                    keywords.add(ent.text.lower())
            
            # Method 2: Important nouns and adjectives
            for token in doc:
                if (token.pos_ in ['NOUN', 'ADJ', 'PROPN'] and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2):
                    keywords.add(token.lemma_.lower())
            
            # Method 3: TF-IDF (if we have a corpus)
            try:
                # This would work better with a larger corpus
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                tfidf_scores = tfidf_matrix.toarray()[0]
                
                # Get top TF-IDF terms
                top_indices = tfidf_scores.argsort()[-10:][::-1]
                for idx in top_indices:
                    if tfidf_scores[idx] > 0:
                        keywords.add(feature_names[idx])
            except:
                pass
            
            # Sort keywords by importance (simplified)
            keyword_list = list(keywords)
            return keyword_list[:20]  # Return top 20 keywords
            
        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    async def _extract_topics(self, text: str, language: LanguageCode) -> List[Dict[str, Any]]:
        """Extract topics from text"""        try:
            # Simple topic extraction based on entities and keywords
            nlp_model = self.nlp_models.get(language.value, self.nlp_models['en'])
            doc = nlp_model(text)
            
            topics = []
            
            # Extract topics from entities
            entity_topics = {}
            for ent in doc.ents:
                topic_category = self._map_entity_to_topic(ent.label_)
                if topic_category not in entity_topics:
                    entity_topics[topic_category] = []
                entity_topics[topic_category].append(ent.text)
            
            # Create topic objects
            for category, entities in entity_topics.items():
                if entities:
                    topics.append({
                        'topic': category,
                        'confidence': 0.8,
                        'keywords': entities[:5],  # Top 5 entities
                        'description': f"Topic related to {category}"
                    })
            
            # Add general content topic based on classification
            if not topics:
                topics.append({
                    'topic': 'general_content',
                    'confidence': 0.6,
                    'keywords': await self._extract_keywords(text, language),
                    'description': 'General content topic'
                })
            
            return topics[:5]  # Return top 5 topics
            
        except Exception as e:
            self.logger.warning(f"Topic extraction failed: {e}")
            return []
    
    def _map_entity_to_topic(self, entity_label: str) -> str:
        """Map entity labels to topic categories"""        entity_topic_mapping = {
            'PERSON': 'people',
            'ORG': 'organizations',
            'GPE': 'locations',
            'PRODUCT': 'products',
            'EVENT': 'events',
            'MONEY': 'finance',
            'DATE': 'temporal',
            'TIME': 'temporal'
        }
        return entity_topic_mapping.get(entity_label, 'general')
    
    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate semantic embeddings for text"""        try:
            # Use sentence transformer for embeddings
            embedding = self.sentence_transformer.encode(text)
            return embedding
            
        except Exception as e:
            self.logger.warning(f"Embedding generation failed: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dimension)
    
    def _calculate_overall_confidence(
        self,
        sentiment_result: SentimentResult,
        entity_result: EntityResult,
        classification_result: ClassificationResult
    ) -> float:
        """Calculate overall confidence score for analysis"""        confidences = [
            sentiment_result.confidence,
            classification_result.confidence,
            0.8 if entity_result.entities else 0.5  # Entity extraction confidence
        ]
        
        return np.mean(confidences)
    
    async def calculate_similarity(
        self,
        text1: str,
        text2: str,
        method: str = "semantic"
    ) -> SimilarityResult:
        """        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            method: Similarity method ("semantic", "lexical", "combined")
            
        Returns:
            SimilarityResult: Similarity analysis result
        """        try:
            if method == "semantic":
                # Semantic similarity using embeddings
                embedding1 = await self._generate_embeddings(text1)
                embedding2 = await self._generate_embeddings(text2)
                
                # Cosine similarity
                similarity_score = float(np.dot(embedding1, embedding2) / 
                                       (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
                
                semantic_distance = 1.0 - similarity_score
                
            elif method == "lexical":
                # Lexical similarity using TF-IDF
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
                similarity_matrix = cosine_similarity(tfidf_matrix)
                similarity_score = float(similarity_matrix[0, 1])
                semantic_distance = 1.0 - similarity_score
                
            else:  # combined
                # Combine semantic and lexical similarity
                semantic_sim = await self.calculate_similarity(text1, text2, "semantic")
                lexical_sim = await self.calculate_similarity(text1, text2, "lexical")
                
                similarity_score = (semantic_sim.similarity_score + lexical_sim.similarity_score) / 2
                semantic_distance = 1.0 - similarity_score
            
            # Extract common themes
            common_themes = await self._find_common_themes(text1, text2)
            
            # Find distinctive features
            distinctive_features = await self._find_distinctive_features(text1, text2)
            
            return SimilarityResult(
                similarity_score=similarity_score,
                semantic_distance=semantic_distance,
                common_themes=common_themes,
                distinctive_features=distinctive_features
            )
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return SimilarityResult(
                similarity_score=0.0,
                semantic_distance=1.0,
                common_themes=[],
                distinctive_features={"text1": [], "text2": []}
            )
    
    async def _find_common_themes(self, text1: str, text2: str) -> List[str]:
        """Find common themes between two texts"""        try:
            # Analyze both texts
            analysis1 = await self.analyze_text(text1)
            analysis2 = await self.analyze_text(text2)
            
            # Find common keywords
            keywords1 = set(analysis1.keywords)
            keywords2 = set(analysis2.keywords)
            common_keywords = keywords1.intersection(keywords2)
            
            # Find common entities
            entities1 = {ent['text'].lower() for ent in analysis1.entities.entities}
            entities2 = {ent['text'].lower() for ent in analysis2.entities.entities}
            common_entities = entities1.intersection(entities2)
            
            # Find common topics
            topics1 = {topic['topic'] for topic in analysis1.topics}
            topics2 = {topic['topic'] for topic in analysis2.topics}
            common_topics = topics1.intersection(topics2)
            
            # Combine all common themes
            common_themes = list(common_keywords) + list(common_entities) + list(common_topics)
            return common_themes[:10]  # Return top 10 common themes
            
        except Exception as e:
            self.logger.warning(f"Common themes extraction failed: {e}")
            return []
    
    async def _find_distinctive_features(self, text1: str, text2: str) -> Dict[str, List[str]]:
        """Find distinctive features of each text"""        try:
            # Analyze both texts
            analysis1 = await self.analyze_text(text1)
            analysis2 = await self.analyze_text(text2)
            
            # Find unique keywords
            keywords1 = set(analysis1.keywords)
            keywords2 = set(analysis2.keywords)
            
            unique_keywords1 = keywords1 - keywords2
            unique_keywords2 = keywords2 - keywords1
            
            # Find unique entities
            entities1 = {ent['text'] for ent in analysis1.entities.entities}
            entities2 = {ent['text'] for ent in analysis2.entities.entities}
            
            unique_entities1 = entities1 - entities2
            unique_entities2 = entities2 - entities1
            
            return {
                "text1": list(unique_keywords1)[:5] + list(unique_entities1)[:3],
                "text2": list(unique_keywords2)[:5] + list(unique_entities2)[:3]
            }
            
        except Exception as e:
            self.logger.warning(f"Distinctive features extraction failed: {e}")
            return {"text1": [], "text2": []}
    
    async def search_similar_content(
        self,
        query_text: str,
        content_database: List[str],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """        Search for similar content in a database
        
        Args:
            query_text: Query text to find similar content for
            content_database: Database of content to search
            top_k: Number of top results to return
            
        Returns:
            List of (content, similarity_score) tuples
        """        try:
            # Generate query embedding
            query_embedding = await self._generate_embeddings(query_text)
            
            # Generate embeddings for all content
            content_embeddings = []
            for content in content_database:
                embedding = await self._generate_embeddings(content)
                content_embeddings.append(embedding)
            
            # Calculate similarities
            similarities = []
            for i, content_embedding in enumerate(content_embeddings):
                similarity = float(np.dot(query_embedding, content_embedding) / 
                                 (np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding)))
                similarities.append((content_database[i], similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            self.logger.error(f"Similar content search failed: {e}")
            return []
    
    async def extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract user intent from text"""        try:
            # Define intent categories
            intent_categories = [
                "create_content", "analyze_performance", "monetize_content",
                "protect_content", "collaborate", "optimize_content",
                "get_recommendations", "ask_question", "report_issue"
            ]
            
            # Use zero-shot classification for intent
            intent_result = self.classification_models['content_type'](
                text, intent_categories
            )
            
            # Extract confidence and intent
            primary_intent = intent_result['labels'][0]
            confidence = intent_result['scores'][0]
            
            # Extract entities that might be parameters
            entity_analysis = await self._extract_entities(text, LanguageCode.AUTO)
            parameters = {}
            
            for entity in entity_analysis.entities:
                if entity['label'] in ['PRODUCT', 'MONEY', 'DATE', 'TIME']:
                    parameters[entity['label'].lower()] = entity['text']
            
            return {
                'intent': primary_intent,
                'confidence': confidence,
                'parameters': parameters,
                'all_intents': dict(zip(intent_result['labels'], intent_result['scores']))
            }
            
        except Exception as e:
            self.logger.warning(f"Intent extraction failed: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'all_intents': {}
            }
    
    def _generate_analysis_id(self, text: str) -> str:
        """Generate unique analysis ID"""        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        timestamp = str(datetime.now().timestamp())
        return f"sem_{text_hash[:8]}_{timestamp[-6:]}"
    
    def _generate_cache_key(
        self,
        text: str,
        language: LanguageCode,
        tasks: Optional[List[SemanticTask]]
    ) -> str:
        """Generate cache key for analysis"""        text_hash = str(hash(text))
        tasks_str = "_".join(sorted([task.value for task in tasks or []]))
        return f"{text_hash}_{language.value}_{tasks_str}"
    
    def _update_performance_metrics(self, processing_time: float) -> None:
        """Update performance tracking metrics"""        self.performance_metrics["total_analyses"] += 1
        total = self.performance_metrics["total_analyses"]
        current_avg = self.performance_metrics["average_processing_time"]
        
        # Update running average
        self.performance_metrics["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Update cache hit rate
        cache_hits = len(self.analysis_cache)
        self.performance_metrics["cache_hit_rate"] = cache_hits / total
    
    async def batch_analyze(
        self,
        texts: List[str],
        language: LanguageCode = LanguageCode.AUTO,
        tasks: Optional[List[SemanticTask]] = None
    ) -> List[SemanticAnalysisResult]:
        """Analyze multiple texts in batch"""        results = []
        
        for text in texts:
            try:
                result = await self.analyze_text(text, language, tasks)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch analysis failed for text: {e}")
                continue
        
        return results
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""        return self.performance_metrics.copy()
    
    async def clear_cache(self) -> None:
        """Clear analysis cache"""        self.analysis_cache.clear()
        self.logger.info("Semantic analysis cache cleared")
    
    async def update_similarity_index(self, new_content: List[str]) -> None:
        """Update similarity search index with new content"""        try:
            for content in new_content:
                embedding = await self._generate_embeddings(content)
                self.similarity_index.add(embedding.reshape(1, -1))
                self.indexed_texts.append(content)
            
            self.logger.info(f"Updated similarity index with {len(new_content)} new items")
            
        except Exception as e:
            self.logger.error(f"Failed to update similarity index: {e}")
    
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""        return self.supported_languages
