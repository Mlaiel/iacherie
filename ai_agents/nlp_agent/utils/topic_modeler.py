"""
Topic Modeler - Advanced Topic Discovery and Modeling System
============================================================

Advanced AI-powered topic modeling system for discovering latent topics,
themes, and subject matter in text content with high accuracy and interpretability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
from collections import defaultdict, Counter

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Topic modeling will use fallback methods.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation, NMF, TruncatedSVD
    from sklearn.cluster import KMeans
    import scipy.sparse
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Topic modeling capabilities will be limited.")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Using basic text processing.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Topic modeling algorithm types"""
    LDA = "lda"  # Latent Dirichlet Allocation
    NMF = "nmf"  # Non-negative Matrix Factorization
    LSA = "lsa"  # Latent Semantic Analysis
    KMEANS = "kmeans"  # K-Means Clustering
    TRANSFORMER = "transformer"  # Transformer-based

class VectorizerType(Enum):
    """Text vectorization types"""
    TFIDF = "tfidf"
    COUNT = "count"
    TRANSFORMER_EMBEDDINGS = "transformer_embeddings"

@dataclass
class Topic:
    """Individual topic with detailed information"""
    id: int
    name: str
    keywords: List[str]
    keyword_weights: List[float]
    description: str = ""
    coherence_score: float = 0.0
    topic_words: Dict[str, float] = field(default_factory=dict)
    document_assignments: List[int] = field(default_factory=list)
    representative_documents: List[str] = field(default_factory=list)
    related_topics: List[int] = field(default_factory=list)

@dataclass
class DocumentTopic:
    """Document-topic assignment with probabilities"""
    document_index: int
    topic_id: int
    probability: float
    topic_name: str = ""

@dataclass
class TopicModelResult:
    """Complete topic modeling result"""
    texts: List[str]
    topics: List[Topic] = field(default_factory=list)
    document_topics: List[List[DocumentTopic]] = field(default_factory=list)
    model_type: str = ""
    num_topics: int = 0
    coherence_score: float = 0.0
    perplexity: float = 0.0
    topic_diversity: float = 0.0
    dominant_topics: List[int] = field(default_factory=list)
    topic_distribution: Dict[int, float] = field(default_factory=dict)
    vocabulary_size: int = 0
    preprocessing_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class TopicModeler:
    """
    Advanced AI-powered topic modeling system for discovering latent topics
    and themes in text content with comprehensive analysis capabilities.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Topic Modeler"""
        self.config = config or default_config
        self.models = {}
        self.vectorizers = {}
        self.pipelines = {}
        self.stop_words = self._load_stop_words()
        self.lemmatizer = None
        
        if NLTK_AVAILABLE:
            try:
                self.lemmatizer = WordNetLemmatizer()
            except:
                logger.warning("WordNet lemmatizer not available")
        
        self._initialize_models()
    
    def _load_stop_words(self) -> set:
        """Load stop words for text preprocessing"""
        stop_words = set()
        
        try:
            if NLTK_AVAILABLE:
                stop_words.update(stopwords.words('english'))
        except:
            pass
        
        # Add common stop words
        common_stops = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
            'would', 'there', 'we', 'him', 'been', 'has', 'her', 'his', 'how',
            'man', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did',
            'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        stop_words.update(common_stops)
        
        return stop_words
    
    def _initialize_models(self):
        """Initialize topic modeling components"""
        try:
            # Initialize scikit-learn models if available
            if SKLEARN_AVAILABLE:
                # Vectorizers
                self.vectorizers["tfidf"] = TfidfVectorizer(
                    max_features=10000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95
                )
                
                self.vectorizers["count"] = CountVectorizer(
                    max_features=10000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95
                )
                
                # Topic models
                self.models["lda"] = LatentDirichletAllocation(
                    n_components=10,
                    random_state=42,
                    learning_method='batch',
                    max_iter=25
                )
                
                self.models["nmf"] = NMF(
                    n_components=10,
                    random_state=42,
                    init='random',
                    solver='cd'
                )
                
                self.models["lsa"] = TruncatedSVD(
                    n_components=10,
                    random_state=42
                )
                
                self.models["kmeans"] = KMeans(
                    n_clusters=10,
                    random_state=42,
                    n_init=10
                )
                
                logger.info("Scikit-learn models initialized")
            
            # Initialize transformer models if available
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Sentence embeddings for topic modeling
                    self.pipelines["embeddings"] = pipeline(
                        "feature-extraction",
                        model="sentence-transformers/all-MiniLM-L6-v2",
                        device=self._get_device()
                    )
                    
                    logger.info("Transformer models initialized")
                except Exception as e:
                    logger.warning(f"Failed to load transformer models: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize topic modeling components: {e}")
            self._setup_fallback_methods()
    
    def _setup_fallback_methods(self):
        """Setup fallback methods for topic modeling"""
        logger.info("Setting up topic modeling fallback methods")
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
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts for topic modeling"""
        processed_texts = []
        
        for text in texts:
            if not isinstance(text, str):
                continue
            
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Tokenize
            if NLTK_AVAILABLE:
                try:
                    tokens = word_tokenize(text)
                except:
                    tokens = text.split()
            else:
                tokens = text.split()
            
            # Remove stop words
            tokens = [token for token in tokens if token not in self.stop_words]
            
            # Lemmatize
            if self.lemmatizer:
                try:
                    tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
                except:
                    pass
            
            # Filter short tokens
            tokens = [token for token in tokens if len(token) > 2]
            
            processed_text = ' '.join(tokens)
            if processed_text.strip():
                processed_texts.append(processed_text)
        
        return processed_texts
    
    async def discover_topics(
        self,
        texts: List[str],
        num_topics: int = 10,
        model_type: ModelType = ModelType.LDA,
        vectorizer_type: VectorizerType = VectorizerType.TFIDF,
        preprocess_texts: bool = True,
        min_topic_size: int = 2
    ) -> TopicModelResult:
        """
        Discover topics in a collection of texts
        
        Args:
            texts: List of texts to analyze
            num_topics: Number of topics to discover
            model_type: Type of topic modeling algorithm
            vectorizer_type: Type of text vectorization
            preprocess_texts: Whether to preprocess texts
            min_topic_size: Minimum size for topic clusters
        
        Returns:
            TopicModelResult with discovered topics
        """
        start_time = asyncio.get_event_loop().time()
        
        if not texts or not isinstance(texts, list):
            raise ValueError("Input must be a non-empty list of texts")
        
        result = TopicModelResult(
            texts=texts,
            model_type=model_type.value,
            num_topics=num_topics
        )
        
        try:
            # Preprocess texts if requested
            processed_texts = texts
            if preprocess_texts:
                processed_texts = self._preprocess_texts(texts)
            
            result.preprocessing_info = {
                "original_count": len(texts),
                "processed_count": len(processed_texts),
                "preprocessing_enabled": preprocess_texts
            }
            
            if not processed_texts:
                logger.warning("No texts remaining after preprocessing")
                return result
            
            # Choose modeling approach
            if model_type == ModelType.TRANSFORMER and TRANSFORMERS_AVAILABLE:
                await self._discover_with_transformers(processed_texts, num_topics, result)
            elif SKLEARN_AVAILABLE:
                await self._discover_with_sklearn(
                    processed_texts, num_topics, model_type, vectorizer_type, result
                )
            else:
                await self._discover_with_fallback(processed_texts, num_topics, result)
            
            # Post-process results
            await self._post_process_results(result, min_topic_size)
            
            # Calculate processing time
            result.processing_time = asyncio.get_event_loop().time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Topic discovery failed: {e}")
            result.metadata["error"] = str(e)
            result.processing_time = asyncio.get_event_loop().time() - start_time
            return result
    
    async def _discover_with_sklearn(
        self,
        texts: List[str],
        num_topics: int,
        model_type: ModelType,
        vectorizer_type: VectorizerType,
        result: TopicModelResult
    ):
        """Discover topics using scikit-learn models"""
        try:
            # Get vectorizer
            if vectorizer_type == VectorizerType.TFIDF:
                vectorizer = self.vectorizers["tfidf"]
            else:
                vectorizer = self.vectorizers["count"]
            
            # Create document-term matrix
            vectorizer.set_params(max_features=min(10000, len(texts) * 100))
            doc_term_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            result.vocabulary_size = len(feature_names)
            
            # Get topic model
            if model_type == ModelType.LDA:
                model = self.models["lda"]
            elif model_type == ModelType.NMF:
                model = self.models["nmf"]
            elif model_type == ModelType.LSA:
                model = self.models["lsa"]
            else:  # KMEANS
                model = self.models["kmeans"]
            
            # Set number of topics/clusters
            model.set_params(n_components=num_topics)
            if hasattr(model, 'n_clusters'):
                model.set_params(n_clusters=num_topics)
            
            # Fit model
            if model_type == ModelType.KMEANS:
                # For K-means, we need dense vectors
                if scipy.sparse.issparse(doc_term_matrix):
                    doc_term_matrix_dense = doc_term_matrix.toarray()
                else:
                    doc_term_matrix_dense = doc_term_matrix
                
                model.fit(doc_term_matrix_dense)
                topic_word_matrix = model.cluster_centers_
            else:
                model.fit(doc_term_matrix)
                topic_word_matrix = model.components_
            
            # Extract topics
            await self._extract_sklearn_topics(
                topic_word_matrix, feature_names, model, doc_term_matrix, result
            )
            
            # Calculate document-topic assignments
            await self._calculate_document_topics(model, doc_term_matrix, result)
            
        except Exception as e:
            logger.error(f"Sklearn topic discovery failed: {e}")
            raise
    
    async def _discover_with_transformers(
        self,
        texts: List[str],
        num_topics: int,
        result: TopicModelResult
    ):
        """Discover topics using transformer models"""
        try:
            # Get embeddings for all texts
            embeddings_pipeline = self.pipelines.get("embeddings")
            if not embeddings_pipeline:
                raise Exception("Embeddings pipeline not available")
            
            # Generate embeddings
            embeddings = []
            batch_size = 32
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: embeddings_pipeline(batch_texts)
                )
                
                # Average pooling for sentence embeddings
                for emb in batch_embeddings:
                    avg_embedding = np.mean(emb, axis=0)
                    embeddings.append(avg_embedding)
            
            embeddings_matrix = np.array(embeddings)
            
            # Use K-means clustering on embeddings
            if SKLEARN_AVAILABLE:
                kmeans = KMeans(n_clusters=num_topics, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(embeddings_matrix)
                
                # Create topics from clusters
                await self._extract_transformer_topics(
                    texts, embeddings_matrix, cluster_labels, kmeans, result
                )
        
        except Exception as e:
            logger.error(f"Transformer topic discovery failed: {e}")
            raise
    
    async def _discover_with_fallback(
        self,
        texts: List[str],
        num_topics: int,
        result: TopicModelResult
    ):
        """Discover topics using fallback methods"""
        try:
            # Simple keyword-based topic discovery
            all_words = []
            for text in texts:
                words = text.split()
                all_words.extend(words)
            
            # Get most common words
            word_counts = Counter(all_words)
            common_words = word_counts.most_common(num_topics * 5)
            
            # Create simple topics based on word co-occurrence
            topics = []
            words_per_topic = max(1, len(common_words) // num_topics)
            
            for i in range(num_topics):
                start_idx = i * words_per_topic
                end_idx = min(start_idx + words_per_topic, len(common_words))
                
                if start_idx < len(common_words):
                    topic_words = common_words[start_idx:end_idx]
                    keywords = [word for word, count in topic_words]
                    weights = [count / sum(word_counts.values()) for word, count in topic_words]
                    
                    topic = Topic(
                        id=i,
                        name=f"Topic {i + 1}",
                        keywords=keywords[:10],  # Top 10 keywords
                        keyword_weights=weights[:10],
                        description=f"Topic containing: {', '.join(keywords[:5])}",
                        coherence_score=0.5  # Default score for fallback
                    )
                    
                    topics.append(topic)
            
            result.topics = topics
            result.model_type = "fallback"
            
        except Exception as e:
            logger.error(f"Fallback topic discovery failed: {e}")
            raise
    
    async def _extract_sklearn_topics(
        self,
        topic_word_matrix: np.ndarray,
        feature_names: np.ndarray,
        model,
        doc_term_matrix,
        result: TopicModelResult
    ):
        """Extract topics from sklearn model results"""
        topics = []
        
        for topic_idx, topic_weights in enumerate(topic_word_matrix):
            # Get top words for this topic
            top_word_indices = topic_weights.argsort()[-20:][::-1]  # Top 20 words
            keywords = [feature_names[idx] for idx in top_word_indices]
            keyword_weights = [topic_weights[idx] for idx in top_word_indices]
            
            # Normalize weights
            if max(keyword_weights) > 0:
                keyword_weights = [w / max(keyword_weights) for w in keyword_weights]
            
            # Create topic word dictionary
            topic_words = dict(zip(keywords, keyword_weights))
            
            topic = Topic(
                id=topic_idx,
                name=f"Topic {topic_idx + 1}: {', '.join(keywords[:3])}",
                keywords=keywords[:10],
                keyword_weights=keyword_weights[:10],
                description=f"Topic focusing on: {', '.join(keywords[:5])}",
                topic_words=topic_words,
                coherence_score=self._calculate_topic_coherence(keywords[:10])
            )
            
            topics.append(topic)
        
        result.topics = topics
    
    async def _extract_transformer_topics(
        self,
        texts: List[str],
        embeddings_matrix: np.ndarray,
        cluster_labels: np.ndarray,
        kmeans_model,
        result: TopicModelResult
    ):
        """Extract topics from transformer-based clustering"""
        topics = []
        unique_labels = np.unique(cluster_labels)
        
        for cluster_id in unique_labels:
            # Get documents in this cluster
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_texts = [texts[idx] for idx in cluster_indices]
            
            # Extract keywords from cluster texts
            all_words = []
            for text in cluster_texts:
                words = text.split()
                all_words.extend([word for word in words if word not in self.stop_words])
            
            word_counts = Counter(all_words)
            top_words = word_counts.most_common(20)
            
            keywords = [word for word, count in top_words]
            keyword_weights = [count / len(all_words) for word, count in top_words]
            
            topic = Topic(
                id=int(cluster_id),
                name=f"Topic {cluster_id + 1}: {', '.join(keywords[:3])}",
                keywords=keywords[:10],
                keyword_weights=keyword_weights[:10],
                description=f"Cluster topic containing: {', '.join(keywords[:5])}",
                coherence_score=self._calculate_topic_coherence(keywords[:10]),
                document_assignments=cluster_indices.tolist(),
                representative_documents=cluster_texts[:3]  # First 3 as representatives
            )
            
            topics.append(topic)
        
        result.topics = topics
    
    async def _calculate_document_topics(
        self,
        model,
        doc_term_matrix,
        result: TopicModelResult
    ):
        """Calculate document-topic assignments"""
        document_topics = []
        
        try:
            if hasattr(model, 'transform'):
                # For LDA, NMF, LSA
                doc_topic_matrix = model.transform(doc_term_matrix)
            elif hasattr(model, 'predict'):
                # For K-means
                if scipy.sparse.issparse(doc_term_matrix):
                    doc_term_matrix_dense = doc_term_matrix.toarray()
                else:
                    doc_term_matrix_dense = doc_term_matrix
                
                cluster_labels = model.predict(doc_term_matrix_dense)
                # Convert to probability-like format
                doc_topic_matrix = np.zeros((len(cluster_labels), len(result.topics)))
                for i, label in enumerate(cluster_labels):
                    doc_topic_matrix[i, label] = 1.0
            else:
                return
            
            # Create document-topic assignments
            for doc_idx, topic_probs in enumerate(doc_topic_matrix):
                doc_topics = []
                
                # Get topic assignments for this document
                for topic_idx, prob in enumerate(topic_probs):
                    if prob > 0.01:  # Only include topics with reasonable probability
                        doc_topic = DocumentTopic(
                            document_index=doc_idx,
                            topic_id=topic_idx,
                            probability=float(prob),
                            topic_name=result.topics[topic_idx].name if topic_idx < len(result.topics) else f"Topic {topic_idx + 1}"
                        )
                        doc_topics.append(doc_topic)
                
                # Sort by probability
                doc_topics.sort(key=lambda x: x.probability, reverse=True)
                document_topics.append(doc_topics)
            
            result.document_topics = document_topics
            
        except Exception as e:
            logger.error(f"Document-topic calculation failed: {e}")
    
    def _calculate_topic_coherence(self, keywords: List[str]) -> float:
        """Calculate topic coherence score (simplified implementation)"""
        if len(keywords) < 2:
            return 0.0
        
        # Simple coherence based on word co-occurrence patterns
        # This is a simplified version - in practice, you'd use more sophisticated methods
        coherence_score = 1.0 / (len(keywords) * 0.1 + 1)  # Inversely related to keyword count
        
        return min(coherence_score, 1.0)
    
    async def _post_process_results(self, result: TopicModelResult, min_topic_size: int):
        """Post-process topic modeling results"""
        try:
            # Filter topics by size
            if min_topic_size > 0:
                filtered_topics = [
                    topic for topic in result.topics
                    if len(topic.document_assignments) >= min_topic_size
                ]
                result.topics = filtered_topics
                result.num_topics = len(filtered_topics)
            
            # Calculate overall statistics
            if result.topics:
                result.coherence_score = np.mean([topic.coherence_score for topic in result.topics])
                
                # Find dominant topics
                topic_doc_counts = {
                    topic.id: len(topic.document_assignments) 
                    for topic in result.topics
                }
                
                sorted_topics = sorted(
                    topic_doc_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                result.dominant_topics = [topic_id for topic_id, count in sorted_topics[:5]]
                result.topic_distribution = {
                    topic_id: count / len(result.texts)
                    for topic_id, count in topic_doc_counts.items()
                }
            
            # Add metadata
            result.metadata = {
                "total_documents": len(result.texts),
                "vocabulary_size": result.vocabulary_size,
                "topics_generated": len(result.topics),
                "avg_coherence": result.coherence_score,
                "sklearn_available": SKLEARN_AVAILABLE,
                "transformers_available": TRANSFORMERS_AVAILABLE
            }
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
    
    async def get_topic_keywords(self, topic_id: int, result: TopicModelResult) -> List[str]:
        """Get keywords for a specific topic"""
        for topic in result.topics:
            if topic.id == topic_id:
                return topic.keywords
        return []
    
    async def get_documents_by_topic(
        self,
        topic_id: int,
        result: TopicModelResult,
        min_probability: float = 0.1
    ) -> List[Tuple[int, str, float]]:
        """Get documents assigned to a specific topic"""
        documents = []
        
        for doc_idx, doc_topics in enumerate(result.document_topics):
            for doc_topic in doc_topics:
                if (doc_topic.topic_id == topic_id and 
                    doc_topic.probability >= min_probability):
                    documents.append((
                        doc_idx,
                        result.texts[doc_idx],
                        doc_topic.probability
                    ))
                    break
        
        # Sort by probability
        documents.sort(key=lambda x: x[2], reverse=True)
        return documents
    
    async def find_similar_topics(
        self,
        result: TopicModelResult,
        similarity_threshold: float = 0.3
    ) -> List[Tuple[int, int, float]]:
        """Find similar topics based on keyword overlap"""
        similar_pairs = []
        
        for i, topic1 in enumerate(result.topics):
            for j, topic2 in enumerate(result.topics[i+1:], i+1):
                # Calculate keyword overlap
                keywords1 = set(topic1.keywords)
                keywords2 = set(topic2.keywords)
                
                overlap = len(keywords1 & keywords2)
                union = len(keywords1 | keywords2)
                
                if union > 0:
                    similarity = overlap / union
                    if similarity >= similarity_threshold:
                        similar_pairs.append((topic1.id, topic2.id, similarity))
        
        return similar_pairs
    
    async def evolve_topics_over_time(
        self,
        text_batches: List[List[str]],
        num_topics: int = 10
    ) -> List[TopicModelResult]:
        """Track topic evolution over time periods"""
        results = []
        
        for i, batch in enumerate(text_batches):
            if batch:
                result = await self.discover_topics(
                    batch,
                    num_topics=num_topics
                )
                result.metadata["time_period"] = i
                results.append(result)
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        status = {
            "status": "healthy",
            "sklearn_available": SKLEARN_AVAILABLE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "nltk_available": NLTK_AVAILABLE,
            "models_loaded": len(self.models),
            "vectorizers_loaded": len(self.vectorizers)
        }
        
        # Test basic functionality
        try:
            test_texts = [
                "This is about machine learning and AI",
                "Sports and football are great activities",
                "Cooking and recipes for delicious food"
            ]
            
            test_result = asyncio.run(self.discover_topics(test_texts, num_topics=2))
            status["test_result"] = "passed"
            status["test_topics_found"] = len(test_result.topics)
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the topic modeler"""
        logger.info("Shutting down Topic Modeler")
        
        # Clear models
        self.models.clear()
        self.vectorizers.clear()
        self.pipelines.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_topic_similarity(topic1: Topic, topic2: Topic) -> float:
    """Calculate similarity between two topics"""
    keywords1 = set(topic1.keywords)
    keywords2 = set(topic2.keywords)
    
    if not keywords1 and not keywords2:
        return 1.0
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    return intersection / union if union > 0 else 0.0

def merge_topic_results(results: List[TopicModelResult]) -> TopicModelResult:
    """Merge multiple topic modeling results"""
    if not results:
        return TopicModelResult(texts=[])
    
    merged_texts = []
    merged_topics = []
    topic_id_offset = 0
    
    for result in results:
        merged_texts.extend(result.texts)
        
        # Adjust topic IDs to avoid conflicts
        for topic in result.topics:
            adjusted_topic = Topic(
                id=topic.id + topic_id_offset,
                name=topic.name,
                keywords=topic.keywords,
                keyword_weights=topic.keyword_weights,
                description=topic.description,
                coherence_score=topic.coherence_score,
                topic_words=topic.topic_words,
                document_assignments=[
                    doc_idx + len(merged_texts) - len(result.texts)
                    for doc_idx in topic.document_assignments
                ]
            )
            merged_topics.append(adjusted_topic)
        
        topic_id_offset += len(result.topics)
    
    merged_result = TopicModelResult(
        texts=merged_texts,
        topics=merged_topics,
        num_topics=len(merged_topics)
    )
    
    return merged_result
