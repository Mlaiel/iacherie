"""Conversation Memory Indexing Systems - Multi-Dimensional Indexing

Advanced indexing systems for conversation memory including topic indexing,
semantic indexing, content-type indexing, and temporal indexing for optimal
conversation search and retrieval performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING: Unauthorized use strictly prohibited ⚠️
Contact: mlaiel@live.de
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
import json
import re

# NLP and ML libraries
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Internal imports
from backend.utils.cache import CacheManager
from backend.utils.metrics import MetricsCollector

from .models import (
    ConversationRecord,
    ContentType,
    ConversationStatus
)

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")


class IndexingInterface(ABC):
    """Abstract interface for indexing systems"""    
    @abstractmethod
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """Index a conversation"""        pass
    
    @abstractmethod
    async def search_index(self, query: Dict[str, Any]) -> List[str]:
        """Search the index"""        pass
    
    @abstractmethod
    async def update_index(self, conversation_id: str, conversation: ConversationRecord) -> bool:
        """Update index for a conversation"""        pass
    
    @abstractmethod
    async def remove_from_index(self, conversation_id: str) -> bool:
        """Remove conversation from index"""        pass


class ConversationIndexer:
    """    Main conversation indexer orchestrating all indexing strategies
    
    Coordinates multiple indexing approaches for comprehensive
    conversation search and retrieval capabilities.
    """    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector("conversation_indexer")
        
        # Individual indexers
        self.topic_indexer = TopicIndexer()
        self.semantic_indexer = SemanticIndexer()
        self.content_indexer = ContentIndexer()
        self.temporal_indexer = TemporalIndexer()
        
        # Processing components
        self.text_processor = TextProcessor()
        
        logger.info("ConversationIndexer initialized")
    
    async def initialize(self):
        """Initialize all indexing components"""        try:
            await asyncio.gather(
                self.topic_indexer.initialize(),
                self.semantic_indexer.initialize(),
                self.content_indexer.initialize(),
                self.temporal_indexer.initialize(),
                self.text_processor.initialize()
            )
            
            logger.info("ConversationIndexer components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ConversationIndexer: {e}")
            raise
    
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """        Index conversation across all indexing dimensions
        
        Args:
            conversation: ConversationRecord to index
            
        Returns:
            Success status
        """        try:
            # Extract and process text content
            text_content = self._extract_conversation_text(conversation)
            processed_text = await self.text_processor.process_text(text_content)
            
            # Index across all dimensions in parallel
            indexing_tasks = [
                self.topic_indexer.index_conversation(conversation),
                self.semantic_indexer.index_conversation(conversation),
                self.content_indexer.index_conversation(conversation),
                self.temporal_indexer.index_conversation(conversation)
            ]
            
            results = await asyncio.gather(*indexing_tasks, return_exceptions=True)
            
            # Check if all indexing succeeded
            success_count = sum(1 for result in results if result is True)
            overall_success = success_count >= 3  # Allow one failure
            
            if overall_success:
                self.metrics.increment("conversations_indexed")
                
                # Update unified index cache
                await self._update_unified_index(conversation, processed_text)
                
            else:
                self.metrics.increment("indexing_failures")
                logger.warning(f"Indexing partially failed for conversation {conversation.conversation_id}")
            
            return overall_success
            
        except Exception as e:
            logger.error(f"Failed to index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("indexing_errors")
            return False
    
    async def search_unified_index(
        self,
        query: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """        Search across all index dimensions
        
        Args:
            query: Search query parameters
            
        Returns:
            Results from all indexing dimensions
        """        try:
            # Search all indexes in parallel
            search_tasks = [
                self.topic_indexer.search_index(query),
                self.semantic_indexer.search_index(query),
                self.content_indexer.search_index(query),
                self.temporal_indexer.search_index(query)
            ]
            
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Organize results by index type
            unified_results = {
                "topic_results": results[0] if not isinstance(results[0], Exception) else [],
                "semantic_results": results[1] if not isinstance(results[1], Exception) else [],
                "content_results": results[2] if not isinstance(results[2], Exception) else [],
                "temporal_results": results[3] if not isinstance(results[3], Exception) else []
            }
            
            self.metrics.increment("unified_searches")
            return unified_results
            
        except Exception as e:
            logger.error(f"Failed to search unified index: {e}")
            self.metrics.increment("unified_search_errors")
            return {}
    
    async def reindex_conversations(
        self,
        conversation_ids: List[str],
        batch_size: int = 50
    ) -> int:
        """        Reindex multiple conversations in batches
        
        Args:
            conversation_ids: List of conversation IDs to reindex
            batch_size: Number of conversations per batch
            
        Returns:
            Number of successfully reindexed conversations
        """        try:
            reindexed_count = 0
            
            # Process in batches
            for i in range(0, len(conversation_ids), batch_size):
                batch_ids = conversation_ids[i:i + batch_size]
                
                # Get conversations (would need access to storage)
                # This is simplified - in practice would get from storage
                batch_conversations = []  # Would populate from storage
                
                # Index batch
                indexing_tasks = [
                    self.index_conversation(conv)
                    for conv in batch_conversations
                ]
                
                if indexing_tasks:
                    batch_results = await asyncio.gather(*indexing_tasks, return_exceptions=True)
                    batch_success = sum(1 for result in batch_results if result is True)
                    reindexed_count += batch_success
                
                # Progress logging
                logger.info(f"Reindexed batch {i//batch_size + 1}: {reindexed_count} total")
            
            self.metrics.gauge("conversations_reindexed", reindexed_count)
            return reindexed_count
            
        except Exception as e:
            logger.error(f"Failed to reindex conversations: {e}")
            self.metrics.increment("reindexing_errors")
            return 0
    
    def _extract_conversation_text(self, conversation: ConversationRecord) -> str:
        """Extract text content from conversation for indexing"""        text_parts = []
        
        if conversation.conversation_data:
            if "messages" in conversation.conversation_data:
                for message in conversation.conversation_data["messages"]:
                    if "content" in message:
                        text_parts.append(str(message["content"]))
            
            # Extract other text fields
            for key in ["title", "description", "summary", "notes"]:
                if key in conversation.conversation_data:
                    text_parts.append(str(conversation.conversation_data[key]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)
    
    async def _update_unified_index(
        self,
        conversation: ConversationRecord,
        processed_text: Dict[str, Any]
    ):
        """Update unified index cache with conversation metadata"""        try:
            cache_key = f"unified_index:{conversation.conversation_id}"
            
            index_data = {
                "conversation_id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "content_type": conversation.content_type,
                "timestamp": conversation.timestamp.isoformat(),
                "processed_text": processed_text,
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.cache_manager.set(
                cache_key,
                index_data,
                ttl=3600  # 1 hour cache
            )
            
        except Exception as e:
            logger.error(f"Failed to update unified index cache: {e}")


class TopicIndexer(IndexingInterface):
    """    Topic-based indexing using LDA (Latent Dirichlet Allocation)
    
    Extracts topics from conversations and builds topic-based
    indexes for thematic conversation retrieval.
    """    
    def __init__(self, num_topics: int = 20):
        self.num_topics = num_topics
        self.metrics = MetricsCollector("topic_indexer")
        
        # Topic modeling components
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        self.lda_model = LatentDirichletAllocation(
            n_components=num_topics,
            random_state=42,
            max_iter=10
        )
        
        # Topic index storage
        self.topic_index: Dict[int, Set[str]] = defaultdict(set)  # topic_id -> conversation_ids
        self.conversation_topics: Dict[str, List[Tuple[int, float]]] = {}  # conv_id -> [(topic_id, weight)]
        self.topic_terms: Dict[int, List[str]] = {}  # topic_id -> top terms
        
        # Training data
        self.training_documents = []
        self.conversation_id_mapping = []
        self.is_model_trained = False
        
        logger.info(f"TopicIndexer initialized with {num_topics} topics")
    
    async def initialize(self):
        """Initialize topic indexer"""        try:
            # Load pre-trained model if available
            await self._load_pretrained_model()
            logger.info("TopicIndexer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize TopicIndexer: {e}")
            raise
    
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """        Index conversation by topics
        
        Args:
            conversation: ConversationRecord to index
            
        Returns:
            Success status
        """        try:
            # Extract text content
            text_content = self._extract_text_content(conversation)
            
            if not text_content.strip():
                return True  # No content to index
            
            # Add to training data if model not trained
            if not self.is_model_trained:
                self.training_documents.append(text_content)
                self.conversation_id_mapping.append(conversation.conversation_id)
                
                # Train model if we have enough documents
                if len(self.training_documents) >= 100:
                    await self._train_topic_model()
            
            else:
                # Use existing model to extract topics
                topics = await self._extract_topics(text_content)
                
                # Update topic index
                self.conversation_topics[conversation.conversation_id] = topics
                
                for topic_id, weight in topics:
                    if weight > 0.1:  # Minimum weight threshold
                        self.topic_index[topic_id].add(conversation.conversation_id)
            
            self.metrics.increment("conversations_topic_indexed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to topic index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("topic_indexing_errors")
            return False
    
    async def search_index(self, query: Dict[str, Any]) -> List[str]:
        """        Search topic index
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation IDs
        """        try:
            if not self.is_model_trained:
                return []
            
            results = set()
            
            # Text-based topic search
            if "text_query" in query:
                query_topics = await self._extract_topics(query["text_query"])
                
                for topic_id, weight in query_topics:
                    if weight > 0.05:  # Topic relevance threshold
                        if topic_id in self.topic_index:
                            results.update(self.topic_index[topic_id])
            
            # Topic ID search
            if "topic_ids" in query:
                for topic_id in query["topic_ids"]:
                    if topic_id in self.topic_index:
                        results.update(self.topic_index[topic_id])
            
            # User filter
            if "user_id" in query:
                # Would need to filter by user_id (requires additional storage)
                pass
            
            # Convert to list and apply limit
            result_list = list(results)
            limit = query.get("limit", 50)
            
            self.metrics.increment("topic_searches")
            return result_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search topic index: {e}")
            self.metrics.increment("topic_search_errors")
            return []
    
    async def update_index(self, conversation_id: str, conversation: ConversationRecord) -> bool:
        """Update topic index for a conversation"""        # Remove old index entries
        await self.remove_from_index(conversation_id)
        
        # Re-index conversation
        return await self.index_conversation(conversation)
    
    async def remove_from_index(self, conversation_id: str) -> bool:
        """Remove conversation from topic index"""        try:
            # Remove from conversation topics
            if conversation_id in self.conversation_topics:
                topics = self.conversation_topics[conversation_id]
                
                # Remove from topic index
                for topic_id, weight in topics:
                    if topic_id in self.topic_index:
                        self.topic_index[topic_id].discard(conversation_id)
                
                del self.conversation_topics[conversation_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove conversation {conversation_id} from topic index: {e}")
            return False
    
    async def get_topic_terms(self, topic_id: int, num_terms: int = 10) -> List[str]:
        """Get top terms for a topic"""        if topic_id in self.topic_terms:
            return self.topic_terms[topic_id][:num_terms]
        return []
    
    async def get_conversation_topics(
        self,
        conversation_id: str
    ) -> List[Tuple[int, float, List[str]]]:
        """Get topics for a conversation with terms"""        if conversation_id not in self.conversation_topics:
            return []
        
        topics_with_terms = []
        for topic_id, weight in self.conversation_topics[conversation_id]:
            terms = await self.get_topic_terms(topic_id, 5)
            topics_with_terms.append((topic_id, weight, terms))
        
        return topics_with_terms
    
    def _extract_text_content(self, conversation: ConversationRecord) -> str:
        """Extract and preprocess text content"""        text_parts = []
        
        if conversation.conversation_data:
            if "messages" in conversation.conversation_data:
                for message in conversation.conversation_data["messages"]:
                    if "content" in message:
                        text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)
    
    async def _train_topic_model(self):
        """Train LDA topic model on collected documents"""        try:
            if len(self.training_documents) < 10:
                return
            
            # Vectorize documents
            doc_term_matrix = self.vectorizer.fit_transform(self.training_documents)
            
            # Train LDA model
            self.lda_model.fit(doc_term_matrix)
            
            # Extract topic terms
            feature_names = self.vectorizer.get_feature_names_out()
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_terms_idx = topic.argsort()[-10:][::-1]
                top_terms = [feature_names[i] for i in top_terms_idx]
                self.topic_terms[topic_idx] = top_terms
            
            # Index all training documents
            topic_distributions = self.lda_model.transform(doc_term_matrix)
            
            for doc_idx, (conv_id, topic_dist) in enumerate(
                zip(self.conversation_id_mapping, topic_distributions)
            ):
                topics = [
                    (topic_idx, weight)
                    for topic_idx, weight in enumerate(topic_dist)
                    if weight > 0.05
                ]
                
                self.conversation_topics[conv_id] = topics
                
                for topic_idx, weight in topics:
                    self.topic_index[topic_idx].add(conv_id)
            
            self.is_model_trained = True
            self.metrics.gauge("topic_model_documents", len(self.training_documents))
            
            logger.info(f"Topic model trained on {len(self.training_documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to train topic model: {e}")
            self.metrics.increment("topic_model_training_errors")
    
    async def _extract_topics(self, text: str) -> List[Tuple[int, float]]:
        """Extract topics from text using trained model"""        try:
            if not self.is_model_trained:
                return []
            
            # Vectorize text
            text_vector = self.vectorizer.transform([text])
            
            # Get topic distribution
            topic_distribution = self.lda_model.transform(text_vector)[0]
            
            # Return topics with weights above threshold
            topics = [
                (topic_idx, weight)
                for topic_idx, weight in enumerate(topic_distribution)
                if weight > 0.05
            ]
            
            return sorted(topics, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to extract topics from text: {e}")
            return []
    
    async def _load_pretrained_model(self):
        """Load pre-trained topic model if available"""        # In production, would load from persistent storage
        pass


class SemanticIndexer(IndexingInterface):
    """    Semantic indexing using word embeddings and clustering
    
    Groups conversations by semantic similarity for
    content-aware retrieval.
    """    
    def __init__(self, num_clusters: int = 50):
        self.num_clusters = num_clusters
        self.metrics = MetricsCollector("semantic_indexer")
        
        # Clustering components
        self.kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.7
        )
        
        # Semantic index storage
        self.cluster_index: Dict[int, Set[str]] = defaultdict(set)  # cluster_id -> conversation_ids
        self.conversation_clusters: Dict[str, int] = {}  # conv_id -> cluster_id
        self.cluster_centers: Dict[int, np.ndarray] = {}  # cluster_id -> center vector
        
        # Training data
        self.training_documents = []
        self.conversation_id_mapping = []
        self.is_model_trained = False
        
        logger.info(f"SemanticIndexer initialized with {num_clusters} clusters")
    
    async def initialize(self):
        """Initialize semantic indexer"""        try:
            logger.info("SemanticIndexer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize SemanticIndexer: {e}")
            raise
    
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """        Index conversation by semantic similarity
        
        Args:
            conversation: ConversationRecord to index
            
        Returns:
            Success status
        """        try:
            # Extract text content
            text_content = self._extract_text_content(conversation)
            
            if not text_content.strip():
                return True
            
            # Add to training data if model not trained
            if not self.is_model_trained:
                self.training_documents.append(text_content)
                self.conversation_id_mapping.append(conversation.conversation_id)
                
                # Train model if we have enough documents
                if len(self.training_documents) >= 200:
                    await self._train_semantic_model()
            
            else:
                # Use existing model to assign cluster
                cluster_id = await self._assign_cluster(text_content)
                
                if cluster_id is not None:
                    # Update semantic index
                    self.conversation_clusters[conversation.conversation_id] = cluster_id
                    self.cluster_index[cluster_id].add(conversation.conversation_id)
            
            self.metrics.increment("conversations_semantic_indexed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to semantic index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("semantic_indexing_errors")
            return False
    
    async def search_index(self, query: Dict[str, Any]) -> List[str]:
        """        Search semantic index
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation IDs
        """        try:
            if not self.is_model_trained:
                return []
            
            results = set()
            
            # Text-based semantic search
            if "text_query" in query:
                similar_clusters = await self._find_similar_clusters(query["text_query"])
                
                for cluster_id in similar_clusters:
                    if cluster_id in self.cluster_index:
                        results.update(self.cluster_index[cluster_id])
            
            # Cluster ID search
            if "cluster_ids" in query:
                for cluster_id in query["cluster_ids"]:
                    if cluster_id in self.cluster_index:
                        results.update(self.cluster_index[cluster_id])
            
            # Convert to list and apply limit
            result_list = list(results)
            limit = query.get("limit", 50)
            
            self.metrics.increment("semantic_searches")
            return result_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search semantic index: {e}")
            self.metrics.increment("semantic_search_errors")
            return []
    
    async def update_index(self, conversation_id: str, conversation: ConversationRecord) -> bool:
        """Update semantic index for a conversation"""        # Remove old index entries
        await self.remove_from_index(conversation_id)
        
        # Re-index conversation
        return await self.index_conversation(conversation)
    
    async def remove_from_index(self, conversation_id: str) -> bool:
        """Remove conversation from semantic index"""        try:
            if conversation_id in self.conversation_clusters:
                cluster_id = self.conversation_clusters[conversation_id]
                
                # Remove from cluster index
                if cluster_id in self.cluster_index:
                    self.cluster_index[cluster_id].discard(conversation_id)
                
                del self.conversation_clusters[conversation_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove conversation {conversation_id} from semantic index: {e}")
            return False
    
    def _extract_text_content(self, conversation: ConversationRecord) -> str:
        """Extract text content for semantic analysis"""        text_parts = []
        
        if conversation.conversation_data:
            if "messages" in conversation.conversation_data:
                for message in conversation.conversation_data["messages"]:
                    if "content" in message:
                        text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)
    
    async def _train_semantic_model(self):
        """Train semantic clustering model"""        try:
            if len(self.training_documents) < 50:
                return
            
            # Vectorize documents
            doc_vectors = self.vectorizer.fit_transform(self.training_documents)
            
            # Perform clustering
            self.kmeans.fit(doc_vectors)
            
            # Store cluster centers
            for i, center in enumerate(self.kmeans.cluster_centers_):
                self.cluster_centers[i] = center
            
            # Assign conversations to clusters
            cluster_labels = self.kmeans.labels_
            
            for conv_id, cluster_id in zip(self.conversation_id_mapping, cluster_labels):
                self.conversation_clusters[conv_id] = cluster_id
                self.cluster_index[cluster_id].add(conv_id)
            
            self.is_model_trained = True
            self.metrics.gauge("semantic_model_documents", len(self.training_documents))
            
            logger.info(f"Semantic model trained on {len(self.training_documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to train semantic model: {e}")
            self.metrics.increment("semantic_model_training_errors")
    
    async def _assign_cluster(self, text: str) -> Optional[int]:
        """Assign text to semantic cluster"""        try:
            if not self.is_model_trained:
                return None
            
            # Vectorize text
            text_vector = self.vectorizer.transform([text])
            
            # Predict cluster
            cluster_id = self.kmeans.predict(text_vector)[0]
            
            return int(cluster_id)
            
        except Exception as e:
            logger.error(f"Failed to assign cluster: {e}")
            return None
    
    async def _find_similar_clusters(self, query_text: str, top_k: int = 5) -> List[int]:
        """Find clusters similar to query text"""        try:
            if not self.is_model_trained:
                return []
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query_text])
            
            # Calculate similarity to all cluster centers
            similarities = []
            for cluster_id, center in self.cluster_centers.items():
                # Calculate cosine similarity
                similarity = np.dot(query_vector.toarray()[0], center) / (
                    np.linalg.norm(query_vector.toarray()[0]) * np.linalg.norm(center)
                )
                similarities.append((cluster_id, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return [cluster_id for cluster_id, sim in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Failed to find similar clusters: {e}")
            return []


class ContentIndexer(IndexingInterface):
    """    Content-type specific indexing
    
    Indexes conversations based on content creation specializations
    and creator-specific attributes.
    """    
    def __init__(self):
        self.metrics = MetricsCollector("content_indexer")
        
        # Content type indexes
        self.content_type_index: Dict[str, Set[str]] = defaultdict(set)  # content_type -> conversation_ids
        self.creator_index: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )  # user_id -> content_type -> conversation_ids
        
        # Content-specific keyword indexes
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)  # keyword -> conversation_ids
        
        # Content creation stage indexes
        self.stage_index: Dict[str, Set[str]] = defaultdict(set)  # stage -> conversation_ids
        
        logger.info("ContentIndexer initialized")
    
    async def initialize(self):
        """Initialize content indexer"""        try:
            logger.info("ContentIndexer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContentIndexer: {e}")
            raise
    
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """        Index conversation by content attributes
        
        Args:
            conversation: ConversationRecord to index
            
        Returns:
            Success status
        """        try:
            conv_id = conversation.conversation_id
            user_id = conversation.user_id
            content_type = conversation.content_type
            
            # Index by content type
            self.content_type_index[content_type].add(conv_id)
            
            # Index by creator and content type
            self.creator_index[user_id][content_type].add(conv_id)
            
            # Extract and index keywords
            keywords = await self._extract_content_keywords(conversation)
            for keyword in keywords:
                self.keyword_index[keyword].add(conv_id)
            
            # Index by creation stage if available
            stage = await self._extract_creation_stage(conversation)
            if stage:
                self.stage_index[stage].add(conv_id)
            
            self.metrics.increment("conversations_content_indexed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to content index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("content_indexing_errors")
            return False
    
    async def search_index(self, query: Dict[str, Any]) -> List[str]:
        """        Search content index
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation IDs
        """        try:
            results = set()
            
            # Content type search
            if "content_type" in query:
                content_type = query["content_type"]
                if content_type in self.content_type_index:
                    results.update(self.content_type_index[content_type])
            
            # Creator-specific search
            if "user_id" in query:
                user_id = query["user_id"]
                if user_id in self.creator_index:
                    if "content_type" in query:
                        content_type = query["content_type"]
                        if content_type in self.creator_index[user_id]:
                            results.update(self.creator_index[user_id][content_type])
                    else:
                        # All content types for user
                        for content_conversations in self.creator_index[user_id].values():
                            results.update(content_conversations)
            
            # Keyword search
            if "keywords" in query:
                keyword_results = set()
                for keyword in query["keywords"]:
                    if keyword in self.keyword_index:
                        keyword_results.update(self.keyword_index[keyword])
                
                if results:
                    results = results.intersection(keyword_results)
                else:
                    results = keyword_results
            
            # Creation stage search
            if "creation_stage" in query:
                stage = query["creation_stage"]
                if stage in self.stage_index:
                    stage_results = self.stage_index[stage]
                    
                    if results:
                        results = results.intersection(stage_results)
                    else:
                        results = stage_results
            
            # Convert to list and apply limit
            result_list = list(results)
            limit = query.get("limit", 50)
            
            self.metrics.increment("content_searches")
            return result_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search content index: {e}")
            self.metrics.increment("content_search_errors")
            return []
    
    async def update_index(self, conversation_id: str, conversation: ConversationRecord) -> bool:
        """Update content index for a conversation"""        # Remove old index entries
        await self.remove_from_index(conversation_id)
        
        # Re-index conversation
        return await self.index_conversation(conversation)
    
    async def remove_from_index(self, conversation_id: str) -> bool:
        """Remove conversation from content index"""        try:
            # Remove from all indexes
            # This is a simplified approach - in production would track relationships
            
            # Remove from content type index
            for content_conversations in self.content_type_index.values():
                content_conversations.discard(conversation_id)
            
            # Remove from creator index
            for user_content_types in self.creator_index.values():
                for content_conversations in user_content_types.values():
                    content_conversations.discard(conversation_id)
            
            # Remove from keyword index
            for keyword_conversations in self.keyword_index.values():
                keyword_conversations.discard(conversation_id)
            
            # Remove from stage index
            for stage_conversations in self.stage_index.values():
                stage_conversations.discard(conversation_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove conversation {conversation_id} from content index: {e}")
            return False
    
    async def _extract_content_keywords(self, conversation: ConversationRecord) -> List[str]:
        """Extract content-specific keywords"""        keywords = []
        
        # Content type specific keywords
        content_type_keywords = {
            ContentType.MUSIC_CREATION: [
                "music", "song", "album", "track", "beat", "melody", "rhythm",
                "lyrics", "composition", "recording", "mixing", "mastering"
            ],
            ContentType.BLOG_CONTENT: [
                "blog", "article", "writing", "post", "content", "seo",
                "keywords", "publishing", "audience", "engagement"
            ],
            ContentType.PHOTOGRAPHY: [
                "photo", "image", "camera", "shoot", "lighting", "composition",
                "editing", "portfolio", "visual", "aesthetic"
            ],
            ContentType.VIDEO_CONTENT: [
                "video", "film", "editing", "youtube", "tiktok", "instagram",
                "visual", "storytelling", "production", "streaming"
            ]
        }
        
        # Extract text content
        text_content = self._extract_text_content(conversation).lower()
        
        # Find matching keywords
        try:
            content_type_enum = ContentType(conversation.content_type)
            if content_type_enum in content_type_keywords:
                for keyword in content_type_keywords[content_type_enum]:
                    if keyword in text_content:
                        keywords.append(keyword)
        except ValueError:
            pass
        
        # Extract custom keywords from context
        if conversation.context and hasattr(conversation.context, 'seo_keywords'):
            if conversation.context.seo_keywords:
                keywords.extend(conversation.context.seo_keywords)
        
        return list(set(keywords))  # Remove duplicates
    
    async def _extract_creation_stage(self, conversation: ConversationRecord) -> Optional[str]:
        """Extract creation stage from conversation"""        if conversation.context and hasattr(conversation.context, 'creation_stage'):
            return conversation.context.creation_stage
        
        # Try to infer from text content
        text_content = self._extract_text_content(conversation).lower()
        
        stage_keywords = {
            "ideation": ["idea", "brainstorm", "concept", "planning"],
            "production": ["creating", "producing", "recording", "shooting"],
            "post_production": ["editing", "mixing", "mastering", "finalizing"],
            "distribution": ["publishing", "sharing", "release", "distribution"]
        }
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in text_content for keyword in keywords):
                return stage
        
        return None
    
    def _extract_text_content(self, conversation: ConversationRecord) -> str:
        """Extract text content for analysis"""        text_parts = []
        
        if conversation.conversation_data:
            if "messages" in conversation.conversation_data:
                for message in conversation.conversation_data["messages"]:
                    if "content" in message:
                        text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)


class TemporalIndexer(IndexingInterface):
    """    Temporal indexing for time-based conversation retrieval
    
    Indexes conversations by time patterns, enabling
    time-sensitive searches and trend analysis.
    """    
    def __init__(self):
        self.metrics = MetricsCollector("temporal_indexer")
        
        # Temporal indexes
        self.hourly_index: Dict[int, Set[str]] = defaultdict(set)  # hour -> conversation_ids
        self.daily_index: Dict[str, Set[str]] = defaultdict(set)  # YYYY-MM-DD -> conversation_ids
        self.weekly_index: Dict[str, Set[str]] = defaultdict(set)  # YYYY-WW -> conversation_ids
        self.monthly_index: Dict[str, Set[str]] = defaultdict(set)  # YYYY-MM -> conversation_ids
        
        # User activity patterns
        self.user_activity_index: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )  # user_id -> time_period -> conversation_ids
        
        logger.info("TemporalIndexer initialized")
    
    async def initialize(self):
        """Initialize temporal indexer"""        try:
            logger.info("TemporalIndexer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize TemporalIndexer: {e}")
            raise
    
    async def index_conversation(self, conversation: ConversationRecord) -> bool:
        """        Index conversation by temporal attributes
        
        Args:
            conversation: ConversationRecord to index
            
        Returns:
            Success status
        """        try:
            conv_id = conversation.conversation_id
            user_id = conversation.user_id
            timestamp = conversation.timestamp
            
            # Extract time components
            hour = timestamp.hour
            day_key = timestamp.strftime("%Y-%m-%d")
            week_key = timestamp.strftime("%Y-%W")
            month_key = timestamp.strftime("%Y-%m")
            
            # Index by time periods
            self.hourly_index[hour].add(conv_id)
            self.daily_index[day_key].add(conv_id)
            self.weekly_index[week_key].add(conv_id)
            self.monthly_index[month_key].add(conv_id)
            
            # Index user activity patterns
            self.user_activity_index[user_id][day_key].add(conv_id)
            self.user_activity_index[user_id][f"hour_{hour}"].add(conv_id)
            
            self.metrics.increment("conversations_temporal_indexed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to temporal index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("temporal_indexing_errors")
            return False
    
    async def search_index(self, query: Dict[str, Any]) -> List[str]:
        """        Search temporal index
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching conversation IDs
        """        try:
            results = set()
            
            # Date range search
            if "start_date" in query and "end_date" in query:
                start_date = query["start_date"]
                end_date = query["end_date"]
                
                # Generate date range
                current_date = start_date
                while current_date <= end_date:
                    day_key = current_date.strftime("%Y-%m-%d")
                    if day_key in self.daily_index:
                        results.update(self.daily_index[day_key])
                    
                    current_date += timedelta(days=1)
            
            # Specific day search
            elif "date" in query:
                day_key = query["date"].strftime("%Y-%m-%d")
                if day_key in self.daily_index:
                    results.update(self.daily_index[day_key])
            
            # Hour of day search
            if "hour" in query:
                hour = query["hour"]
                if hour in self.hourly_index:
                    hour_results = self.hourly_index[hour]
                    
                    if results:
                        results = results.intersection(hour_results)
                    else:
                        results = hour_results
            
            # Week search
            if "week" in query:
                week_key = query["week"]
                if week_key in self.weekly_index:
                    week_results = self.weekly_index[week_key]
                    
                    if results:
                        results = results.intersection(week_results)
                    else:
                        results = week_results
            
            # Month search
            if "month" in query:
                month_key = query["month"]
                if month_key in self.monthly_index:
                    month_results = self.monthly_index[month_key]
                    
                    if results:
                        results = results.intersection(month_results)
                    else:
                        results = month_results
            
            # User activity search
            if "user_id" in query:
                user_id = query["user_id"]
                if user_id in self.user_activity_index:
                    user_results = set()
                    
                    # Collect all user conversations in time period
                    for period_conversations in self.user_activity_index[user_id].values():
                        user_results.update(period_conversations)
                    
                    if results:
                        results = results.intersection(user_results)
                    else:
                        results = user_results
            
            # Convert to list and apply limit
            result_list = list(results)
            limit = query.get("limit", 50)
            
            self.metrics.increment("temporal_searches")
            return result_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search temporal index: {e}")
            self.metrics.increment("temporal_search_errors")
            return []
    
    async def update_index(self, conversation_id: str, conversation: ConversationRecord) -> bool:
        """Update temporal index for a conversation"""        # Remove old index entries
        await self.remove_from_index(conversation_id)
        
        # Re-index conversation
        return await self.index_conversation(conversation)
    
    async def remove_from_index(self, conversation_id: str) -> bool:
        """Remove conversation from temporal index"""        try:
            # Remove from all temporal indexes
            # This is a simplified approach
            
            for hour_conversations in self.hourly_index.values():
                hour_conversations.discard(conversation_id)
            
            for day_conversations in self.daily_index.values():
                day_conversations.discard(conversation_id)
            
            for week_conversations in self.weekly_index.values():
                week_conversations.discard(conversation_id)
            
            for month_conversations in self.monthly_index.values():
                month_conversations.discard(conversation_id)
            
            # Remove from user activity index
            for user_activity in self.user_activity_index.values():
                for period_conversations in user_activity.values():
                    period_conversations.discard(conversation_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove conversation {conversation_id} from temporal index: {e}")
            return False
    
    async def get_activity_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get user activity patterns"""        try:
            if user_id not in self.user_activity_index:
                return {}
            
            user_activity = self.user_activity_index[user_id]
            
            # Calculate patterns
            patterns = {
                "total_conversations": sum(len(convs) for convs in user_activity.values()),
                "active_days": len([key for key in user_activity.keys() if not key.startswith("hour_")]),
                "hourly_distribution": {},
                "daily_activity": {}
            }
            
            # Hourly distribution
            for key, conversations in user_activity.items():
                if key.startswith("hour_"):
                    hour = key.replace("hour_", "")
                    patterns["hourly_distribution"][hour] = len(conversations)
                else:
                    # Daily activity
                    patterns["daily_activity"][key] = len(conversations)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get activity patterns for user {user_id}: {e}")
            return {}


class TextProcessor:
    """    Text processing utilities for indexing
    
    Provides text preprocessing, cleaning, and feature extraction
    for various indexing strategies.
    """    
    def __init__(self):
        self.metrics = MetricsCollector("text_processor")
        
        # NLP components
        try:
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        except Exception:
            self.stop_words = set()
            self.lemmatizer = None
        
        logger.info("TextProcessor initialized")
    
    async def initialize(self):
        """Initialize text processor"""        try:
            logger.info("TextProcessor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize TextProcessor: {e}")
            raise
    
    async def process_text(self, text: str) -> Dict[str, Any]:
        """        Process text for indexing
        
        Args:
            text: Raw text content
            
        Returns:
            Processed text features
        """        try:
            # Basic cleaning
            cleaned_text = self._clean_text(text)
            
            # Tokenization
            tokens = self._tokenize(cleaned_text)
            
            # Remove stop words
            filtered_tokens = self._remove_stop_words(tokens)
            
            # Lemmatization
            lemmatized_tokens = self._lemmatize_tokens(filtered_tokens)
            
            # Extract features
            features = {
                "original_text": text,
                "cleaned_text": cleaned_text,
                "tokens": tokens,
                "filtered_tokens": filtered_tokens,
                "lemmatized_tokens": lemmatized_tokens,
                "word_count": len(tokens),
                "unique_words": len(set(filtered_tokens)),
                "avg_word_length": sum(len(word) for word in filtered_tokens) / max(len(filtered_tokens), 1)
            }
            
            self.metrics.increment("texts_processed")
            return features
            
        except Exception as e:
            logger.error(f"Failed to process text: {e}")
            self.metrics.increment("text_processing_errors")
            return {"original_text": text}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""        try:
            if nltk:
                return word_tokenize(text)
            else:
                return text.split()
        except Exception:
            return text.split()
    
    def _remove_stop_words(self, tokens: List[str]) -> List[str]:
        """Remove stop words from tokens"""        if self.stop_words:
            return [token for token in tokens if token not in self.stop_words and len(token) > 2]
        else:
            return [token for token in tokens if len(token) > 2]
    
    def _lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens to their root forms"""        if self.lemmatizer:
            try:
                return [self.lemmatizer.lemmatize(token) for token in tokens]
            except Exception:
                return tokens
        else:
            return tokens


# Export all indexing classes
__all__ = [
    # Core indexing
    "IndexingInterface",
    "ConversationIndexer",
    
    # Specialized indexers
    "TopicIndexer",
    "SemanticIndexer",
    "ContentIndexer",
    "TemporalIndexer",
    
    # Utilities
    "TextProcessor"
]
