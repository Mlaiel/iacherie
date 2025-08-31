"""NLP Engine - Advanced Natural Language Processing and Analysis

Industrial-grade NLP engine providing comprehensive language processing, 
semantic analysis, and intelligent text understanding for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VaderAnalyzer
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModel
)
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Ensure NLTK resources are available
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """NLP analysis types"""    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    INTENT = "intent"
    TOPIC = "topic"
    ENTITY = "entity"
    SEMANTIC = "semantic"
    SYNTAX = "syntax"
    COHERENCE = "coherence"

class SentimentPolarity(Enum):
    """Sentiment polarity levels"""    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EmotionType(Enum):
    """Basic emotion types"""    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

@dataclass
class SentimentResult:
    """Sentiment analysis result"""    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    confidence: float  # 0 to 1
    label: SentimentPolarity
    emotions: Dict[str, float]
    detailed_scores: Dict[str, float]

@dataclass
class EntityResult:
    """Named entity recognition result"""    text: str
    label: str
    start: int
    end: int
    confidence: float
    description: str

@dataclass
class TopicResult:
    """Topic modeling result"""    topic_id: int
    keywords: List[str]
    coherence_score: float
    probability: float

@dataclass
class SemanticResult:
    """Semantic analysis result"""    embeddings: np.ndarray
    similarity_scores: Dict[str, float]
    semantic_concepts: List[str]
    coherence_score: float

class NLPEngine:
    """    Advanced NLP processing engine with comprehensive language analysis capabilities
    """    
    def __init__(self):
        self.sentiment_analyzers = {}
        self.emotion_analyzer = None
        self.sentence_transformer = None
        self.nlp_models = {}
        
        # Initialize NLP components
        self._init_sentiment_analyzers()
        self._init_emotion_analyzer()
        self._init_language_models()
        self._init_semantic_models()
        
        # Analysis caches for performance
        self.analysis_cache = {}
        self.embedding_cache = {}
        
        # Statistics tracking
        self.analysis_stats = {
            "total_analyses": 0,
            "sentiment_analyses": 0,
            "emotion_analyses": 0,
            "entity_extractions": 0,
            "topic_modelings": 0,
            "average_processing_time": 0.0
        }
        
        logger.info("NLPEngine initialized with advanced analysis capabilities")
    
    def _init_sentiment_analyzers(self):
        """Initialize multiple sentiment analysis models"""        try:
            # VADER sentiment analyzer (rule-based)
            self.sentiment_analyzers['vader'] = VaderAnalyzer()
            
            # TextBlob sentiment analyzer
            self.sentiment_analyzers['textblob'] = TextBlob
            
            # NLTK VADER
            self.sentiment_analyzers['nltk_vader'] = SentimentIntensityAnalyzer()
            
            # Transformer-based sentiment analyzer
            self.sentiment_analyzers['roberta'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Sentiment analyzers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzers: {e}")
    
    def _init_emotion_analyzer(self):
        """Initialize emotion analysis model"""        try:
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Emotion analyzer initialized successfully")
            
        except Exception as e:
            logger.warning(f"Emotion analyzer initialization failed: {e}")
            self.emotion_analyzer = None
    
    def _init_language_models(self):
        """Initialize spaCy language models"""        try:
            # Load multiple language models
            language_models = {
                'en': 'en_core_web_sm',
                'fr': 'fr_core_news_sm',
                'de': 'de_core_news_sm',
                'es': 'es_core_news_sm',
                'it': 'it_core_news_sm'
            }
            
            for lang, model_name in language_models.items():
                try:
                    self.nlp_models[lang] = spacy.load(model_name)
                except OSError:
                    logger.warning(f"SpaCy model {model_name} not found for {lang}")
                    # Use English as fallback
                    if lang != 'en':
                        self.nlp_models[lang] = spacy.load('en_core_web_sm')
            
            logger.info(f"Language models loaded: {list(self.nlp_models.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading language models: {e}")
    
    def _init_semantic_models(self):
        """Initialize semantic analysis models"""        try:
            # Sentence transformer for embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            logger.info("Semantic models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing semantic models: {e}")
    
    async def analyze_sentiment(
        self,
        text: str,
        analyzer: str = "ensemble",
        language: str = "en"
    ) -> SentimentResult:
        """        Comprehensive sentiment analysis with multiple models
        
        Args:
            text: Input text for sentiment analysis
            analyzer: Specific analyzer to use or 'ensemble' for combined
            language: Language of the text
            
        Returns:
            SentimentResult: Comprehensive sentiment analysis results
        """        start_time = time.time()
        
        try:
            if analyzer == "ensemble":
                # Use ensemble of all available analyzers
                sentiment_scores = {}
                
                # VADER analysis
                if 'vader' in self.sentiment_analyzers:
                    vader_scores = self.sentiment_analyzers['vader'].polarity_scores(text)
                    sentiment_scores['vader'] = {
                        'compound': vader_scores['compound'],
                        'positive': vader_scores['pos'],
                        'neutral': vader_scores['neu'],
                        'negative': vader_scores['neg']
                    }
                
                # TextBlob analysis
                if 'textblob' in self.sentiment_analyzers:
                    blob = TextBlob(text)
                    sentiment_scores['textblob'] = {
                        'polarity': blob.sentiment.polarity,
                        'subjectivity': blob.sentiment.subjectivity
                    }
                
                # RoBERTa analysis
                if 'roberta' in self.sentiment_analyzers:
                    roberta_result = self.sentiment_analyzers['roberta'](text[:512])
                    if roberta_result:
                        label = roberta_result[0]['label'].lower()
                        score = roberta_result[0]['score']
                        
                        sentiment_scores['roberta'] = {
                            'label': label,
                            'score': score
                        }
                
                # Combine scores using ensemble method
                polarity, subjectivity, confidence = await self._ensemble_sentiment_scores(sentiment_scores)
                
            else:
                # Use specific analyzer
                polarity, subjectivity, confidence = await self._single_analyzer_sentiment(text, analyzer)
            
            # Determine sentiment label
            label = await self._determine_sentiment_label(polarity)
            
            # Extract emotions if emotion analyzer is available
            emotions = await self._analyze_emotions(text)
            
            processing_time = time.time() - start_time
            
            result = SentimentResult(
                polarity=polarity,
                subjectivity=subjectivity,
                confidence=confidence,
                label=label,
                emotions=emotions,
                detailed_scores=sentiment_scores if analyzer == "ensemble" else {}
            )
            
            # Update statistics
            self.analysis_stats["sentiment_analyses"] += 1
            self.analysis_stats["total_analyses"] += 1
            self._update_processing_time(processing_time)
            
            logger.debug(f"Sentiment analysis completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            # Return neutral sentiment as fallback
            return SentimentResult(
                polarity=0.0,
                subjectivity=0.5,
                confidence=0.0,
                label=SentimentPolarity.NEUTRAL,
                emotions={},
                detailed_scores={}
            )
    
    async def extract_entities(
        self,
        text: str,
        language: str = "en",
        confidence_threshold: float = 0.5
    ) -> List[EntityResult]:
        """        Extract named entities from text
        
        Args:
            text: Input text for entity extraction
            language: Language of the text
            confidence_threshold: Minimum confidence for entity inclusion
            
        Returns:
            List of EntityResult objects
        """        start_time = time.time()
        
        try:
            # Get appropriate language model
            nlp = self.nlp_models.get(language, self.nlp_models.get('en'))
            if not nlp:
                logger.error(f"No NLP model available for language: {language}")
                return []
            
            # Process text with spaCy
            doc = nlp(text)
            
            entities = []
            for ent in doc.ents:
                # Calculate confidence (spaCy doesn't provide this directly)
                confidence = 0.9  # Default confidence for spaCy entities
                
                if confidence >= confidence_threshold:
                    entity_result = EntityResult(
                        text=ent.text,
                        label=ent.label_,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=confidence,
                        description=spacy.explain(ent.label_) or "Unknown entity type"
                    )
                    entities.append(entity_result)
            
            # Also try NLTK's named entity recognition
            try:
                nltk_entities = await self._extract_nltk_entities(text)
                entities.extend(nltk_entities)
            except Exception as e:
                logger.warning(f"NLTK entity extraction failed: {e}")
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.analysis_stats["entity_extractions"] += 1
            self.analysis_stats["total_analyses"] += 1
            self._update_processing_time(processing_time)
            
            logger.debug(f"Entity extraction completed: {len(entities)} entities found")
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def extract_topics(
        self,
        texts: List[str],
        num_topics: int = 5,
        method: str = "lda"
    ) -> List[TopicResult]:
        """        Extract topics from multiple texts using topic modeling
        
        Args:
            texts: List of texts for topic modeling
            num_topics: Number of topics to extract
            method: Topic modeling method ('lda' or 'kmeans')
            
        Returns:
            List of TopicResult objects
        """        start_time = time.time()
        
        try:
            if not texts or len(texts) < 2:
                logger.warning("Insufficient texts for topic modeling")
                return []
            
            # Vectorize texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            if method == "lda":
                topics = await self._extract_topics_lda(tfidf_matrix, feature_names, num_topics)
            elif method == "kmeans":
                topics = await self._extract_topics_kmeans(tfidf_matrix, feature_names, num_topics)
            else:
                topics = await self._extract_topics_lda(tfidf_matrix, feature_names, num_topics)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.analysis_stats["topic_modelings"] += 1
            self.analysis_stats["total_analyses"] += 1
            self._update_processing_time(processing_time)
            
            logger.debug(f"Topic modeling completed: {len(topics)} topics extracted")
            return topics
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
    
    async def analyze_semantics(
        self,
        text: str,
        reference_texts: Optional[List[str]] = None
    ) -> SemanticResult:
        """        Comprehensive semantic analysis of text
        
        Args:
            text: Input text for semantic analysis
            reference_texts: Optional reference texts for comparison
            
        Returns:
            SemanticResult: Comprehensive semantic analysis results
        """        start_time = time.time()
        
        try:
            # Generate embeddings
            embeddings = self.sentence_transformer.encode([text])
            text_embedding = embeddings[0]
            
            # Calculate similarity scores with reference texts
            similarity_scores = {}
            if reference_texts:
                ref_embeddings = self.sentence_transformer.encode(reference_texts)
                similarities = cosine_similarity([text_embedding], ref_embeddings)[0]
                
                for i, ref_text in enumerate(reference_texts):
                    similarity_scores[f"ref_{i}"] = float(similarities[i])
            
            # Extract semantic concepts (simplified)
            semantic_concepts = await self._extract_semantic_concepts(text)
            
            # Calculate coherence score
            coherence_score = await self._calculate_coherence(text)
            
            result = SemanticResult(
                embeddings=text_embedding,
                similarity_scores=similarity_scores,
                semantic_concepts=semantic_concepts,
                coherence_score=coherence_score
            )
            
            processing_time = time.time() - start_time
            self._update_processing_time(processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")
            return SemanticResult(
                embeddings=np.array([]),
                similarity_scores={},
                semantic_concepts=[],
                coherence_score=0.0
            )
    
    async def _ensemble_sentiment_scores(self, scores: Dict[str, Dict]) -> Tuple[float, float, float]:
        """Combine sentiment scores from multiple analyzers"""        try:
            polarities = []
            subjectivities = []
            confidences = []
            
            # Extract polarity scores
            if 'vader' in scores:
                polarities.append(scores['vader']['compound'])
                confidences.append(abs(scores['vader']['compound']))
            
            if 'textblob' in scores:
                polarities.append(scores['textblob']['polarity'])
                subjectivities.append(scores['textblob']['subjectivity'])
            
            if 'roberta' in scores:
                roberta_score = scores['roberta']['score']
                if scores['roberta']['label'] == 'negative':
                    polarities.append(-roberta_score)
                elif scores['roberta']['label'] == 'positive':
                    polarities.append(roberta_score)
                else:  # neutral
                    polarities.append(0.0)
                confidences.append(roberta_score)
            
            # Calculate ensemble scores
            avg_polarity = np.mean(polarities) if polarities else 0.0
            avg_subjectivity = np.mean(subjectivities) if subjectivities else 0.5
            avg_confidence = np.mean(confidences) if confidences else 0.5
            
            return avg_polarity, avg_subjectivity, avg_confidence
            
        except Exception as e:
            logger.warning(f"Ensemble scoring failed: {e}")
            return 0.0, 0.5, 0.0
    
    async def _single_analyzer_sentiment(self, text: str, analyzer: str) -> Tuple[float, float, float]:
        """Get sentiment from single analyzer"""        if analyzer == 'vader' and analyzer in self.sentiment_analyzers:
            scores = self.sentiment_analyzers['vader'].polarity_scores(text)
            return scores['compound'], 0.5, abs(scores['compound'])
        
        elif analyzer == 'textblob':
            blob = TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity, 0.8
        
        else:
            # Default fallback
            return 0.0, 0.5, 0.0
    
    async def _determine_sentiment_label(self, polarity: float) -> SentimentPolarity:
        """Determine sentiment label based on polarity score"""        if polarity >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif polarity >= 0.2:
            return SentimentPolarity.POSITIVE
        elif polarity >= -0.2:
            return SentimentPolarity.NEUTRAL
        elif polarity >= -0.6:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.VERY_NEGATIVE
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Extract emotional content from text"""        try:
            if not self.emotion_analyzer:
                return {}
            
            # Get emotion predictions
            emotions = self.emotion_analyzer(text[:512])  # Limit text length
            
            emotion_scores = {}
            if emotions:
                for emotion in emotions:
                    emotion_scores[emotion['label'].lower()] = emotion['score']
            
            return emotion_scores
            
        except Exception as e:
            logger.warning(f"Emotion analysis failed: {e}")
            return {}
    
    async def _extract_nltk_entities(self, text: str) -> List[EntityResult]:
        """Extract entities using NLTK"""        try:
            # Tokenize and tag
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Named entity chunking
            chunks = ne_chunk(pos_tags)
            
            entities = []
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    # Find position in original text
                    start_pos = text.find(entity_text)
                    end_pos = start_pos + len(entity_text)
                    
                    if start_pos != -1:
                        entity = EntityResult(
                            text=entity_text,
                            label=chunk.label(),
                            start=start_pos,
                            end=end_pos,
                            confidence=0.7,  # Default confidence for NLTK
                            description=f"NLTK {chunk.label()} entity"
                        )
                        entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.warning(f"NLTK entity extraction failed: {e}")
            return []
    
    async def _extract_topics_lda(self, tfidf_matrix, feature_names, num_topics) -> List[TopicResult]:
        """Extract topics using Latent Dirichlet Allocation"""        try:
            lda = LatentDirichletAllocation(
                n_components=num_topics,
                random_state=42,
                max_iter=10
            )
            lda.fit(tfidf_matrix)
            
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                # Get top words for this topic
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                
                # Calculate topic coherence (simplified)
                coherence_score = float(np.mean(topic[top_words_idx]))
                
                topic_result = TopicResult(
                    topic_id=topic_idx,
                    keywords=top_words,
                    coherence_score=coherence_score,
                    probability=1.0 / num_topics  # Equal probability assumption
                )
                topics.append(topic_result)
            
            return topics
            
        except Exception as e:
            logger.error(f"LDA topic extraction failed: {e}")
            return []
    
    async def _extract_topics_kmeans(self, tfidf_matrix, feature_names, num_topics) -> List[TopicResult]:
        """Extract topics using K-means clustering"""        try:
            kmeans = KMeans(n_clusters=num_topics, random_state=42, n_init=10)
            kmeans.fit(tfidf_matrix)
            
            topics = []
            for cluster_idx in range(num_topics):
                # Get cluster center
                cluster_center = kmeans.cluster_centers_[cluster_idx]
                
                # Get top features for this cluster
                top_indices = cluster_center.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                
                coherence_score = float(np.mean(cluster_center[top_indices]))
                
                topic_result = TopicResult(
                    topic_id=cluster_idx,
                    keywords=top_words,
                    coherence_score=coherence_score,
                    probability=1.0 / num_topics
                )
                topics.append(topic_result)
            
            return topics
            
        except Exception as e:
            logger.error(f"K-means topic extraction failed: {e}")
            return []
    
    async def _extract_semantic_concepts(self, text: str) -> List[str]:
        """Extract semantic concepts from text"""        try:
            # Simple concept extraction using TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top concepts
            top_indices = scores.argsort()[-10:][::-1]
            concepts = [feature_names[i] for i in top_indices if scores[i] > 0]
            
            return concepts
            
        except Exception as e:
            logger.warning(f"Concept extraction failed: {e}")
            return []
    
    async def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence score"""        try:
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return 1.0
            
            # Generate sentence embeddings
            sentence_embeddings = self.sentence_transformer.encode(sentences)
            
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(sentences) - 1):
                similarity = cosine_similarity(
                    [sentence_embeddings[i]], 
                    [sentence_embeddings[i + 1]]
                )[0][0]
                similarities.append(similarity)
            
            # Return average coherence
            return float(np.mean(similarities))
            
        except Exception as e:
            logger.warning(f"Coherence calculation failed: {e}")
            return 0.5
    
    def _update_processing_time(self, processing_time: float):
        """Update average processing time"""        total_time = (
            self.analysis_stats["average_processing_time"] * 
            (self.analysis_stats["total_analyses"] - 1) +
            processing_time
        )
        self.analysis_stats["average_processing_time"] = total_time / self.analysis_stats["total_analyses"]
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""        return {
            **self.analysis_stats,
            "models_loaded": len(self.nlp_models),
            "analyzers_available": len(self.sentiment_analyzers)
        }


class SentimentAnalyzer:
    """    Specialized sentiment analysis component with advanced features
    """    
    def __init__(self):
        self.nlp_engine = NLPEngine()
        self.sentiment_history = []
        
        # Sentiment tracking and trends
        self.sentiment_trends = {
            "daily_average": 0.0,
            "weekly_average": 0.0,
            "trend_direction": "stable"
        }
        
        logger.info("SentimentAnalyzer initialized")
    
    async def analyze_sentiment_with_context(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        track_trends: bool = True
    ) -> Dict[str, Any]:
        """        Analyze sentiment with contextual information and trend tracking
        
        Args:
            text: Text to analyze
            context: Contextual information (author, platform, etc.)
            track_trends: Whether to track sentiment trends
            
        Returns:
            Dict containing detailed sentiment analysis with context
        """        try:
            # Basic sentiment analysis
            sentiment_result = await self.nlp_engine.analyze_sentiment(text)
            
            # Add contextual analysis
            contextual_score = sentiment_result.polarity
            if context:
                contextual_score = await self._adjust_for_context(sentiment_result, context)
            
            # Track trends if enabled
            if track_trends:
                self._track_sentiment_trend(sentiment_result.polarity)
            
            result = {
                'basic_sentiment': {
                    'polarity': sentiment_result.polarity,
                    'subjectivity': sentiment_result.subjectivity,
                    'confidence': sentiment_result.confidence,
                    'label': sentiment_result.label.value
                },
                'contextual_sentiment': {
                    'adjusted_polarity': contextual_score,
                    'context_factors': context or {}
                },
                'emotions': sentiment_result.emotions,
                'trends': self.sentiment_trends if track_trends else {},
                'metadata': {
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'analysis_timestamp': time.time()
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Contextual sentiment analysis failed: {e}")
            return {'error': str(e)}
    
    async def _adjust_for_context(self, sentiment_result: SentimentResult, context: Dict[str, Any]) -> float:
        """Adjust sentiment score based on context"""        adjusted_score = sentiment_result.polarity
        
        # Adjust based on platform
        if 'platform' in context:
            platform = context['platform'].lower()
            if platform in ['twitter', 'facebook']:
                # Social media tends to be more polarized
                adjusted_score *= 1.1
            elif platform in ['linkedin', 'medium']:
                # Professional platforms tend to be more neutral
                adjusted_score *= 0.9
        
        # Adjust based on content type
        if 'content_type' in context:
            content_type = context['content_type'].lower()
            if content_type == 'review':
                # Reviews tend to be more extreme
                adjusted_score *= 1.2
            elif content_type == 'news':
                # News tends to be more objective
                adjusted_score *= 0.8
        
        return max(-1.0, min(1.0, adjusted_score))
    
    def _track_sentiment_trend(self, sentiment_score: float):
        """Track sentiment trends over time"""        self.sentiment_history.append({
            'score': sentiment_score,
            'timestamp': time.time()
        })
        
        # Keep only recent history (last 100 analyses)
        if len(self.sentiment_history) > 100:
            self.sentiment_history = self.sentiment_history[-100:]
        
        # Calculate trends
        if len(self.sentiment_history) >= 10:
            recent_scores = [entry['score'] for entry in self.sentiment_history[-10:]]
            older_scores = [entry['score'] for entry in self.sentiment_history[-20:-10]] if len(self.sentiment_history) >= 20 else recent_scores
            
            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)
            
            self.sentiment_trends['daily_average'] = recent_avg
            self.sentiment_trends['weekly_average'] = np.mean([entry['score'] for entry in self.sentiment_history])
            
            # Determine trend direction
            if recent_avg > older_avg + 0.1:
                self.sentiment_trends['trend_direction'] = 'improving'
            elif recent_avg < older_avg - 0.1:
                self.sentiment_trends['trend_direction'] = 'declining'
            else:
                self.sentiment_trends['trend_direction'] = 'stable'
