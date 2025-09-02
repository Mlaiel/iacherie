"""Conversation Memory Retrieval Systems - Intelligent Conversation Search

Advanced retrieval systems for conversation memory including semantic search,
contextual retrieval, and content-aware search specialized for multi-format
content creators.

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
from dataclasses import dataclass, field
import re

# AI and NLP libraries
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Internal imports
from backend.utils.cache import CacheManager
from backend.utils.metrics import MetricsCollector

from .models import (
    ConversationRecord,
    MemoryEntry,
    ContentContext,
    CollaborationContext,
    ProtectionContext,
    ContentType
)

from .storage import (
    LongTermMemory,
    ShortTermMemory,
    VectorStore
)

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """
Structured search query for conversation retrieval"""
    text_query: Optional[str] = None
    user_id: Optional[str] = None
    content_types: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    sentiment_range: Optional[Tuple[float, float]] = None
    priority_threshold: Optional[float] = None
    collaboration_only: bool = False
    protection_only: bool = False
    semantic_search: bool = True
    limit: int = 20
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for caching"""
        return {
            "text_query": self.text_query,
            "user_id": self.user_id,
            "content_types": self.content_types,
            "date_range": [d.isoformat() for d in self.date_range] if self.date_range else None,
            "sentiment_range": self.sentiment_range,
            "priority_threshold": self.priority_threshold,
            "collaboration_only": self.collaboration_only,
            "protection_only": self.protection_only,
            "semantic_search": self.semantic_search,
            "limit": self.limit,
            "offset": self.offset
        }


@dataclass
class SearchResult:
    """Search result with conversation and relevance information"""
    conversation: ConversationRecord
    relevance_score: float
    similarity_score: Optional[float] = None
    context_matches: List[str] = field(default_factory=list)
    highlight_snippets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for API responses"""
        return {
            "conversation": self.conversation.to_dict(),
            "relevance_score": self.relevance_score,
            "similarity_score": self.similarity_score,
            "context_matches": self.context_matches,
            "highlight_snippets": self.highlight_snippets,
            "metadata": self.metadata
        }


class RetrievalInterface(ABC):
    """Abstract interface for retrieval systems"""
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        try:
            logger.info(f"Executing search")
            
            # Implementation for search
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"search completed successfully")
            return result
            
        except Exception as e:
        try:
                    # Request validation
                    if not conversation_id:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_related_conversations_request(conversation_id)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_related_conversations failed: {e}")
                    return {"status": "error", "message": str(e)}
            raise
    @abstractmethod
    async def get_related_conversations(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[ConversationRecord]:
        """
Get conversations related to a specific conversation"""
        pass


class ConversationRetriever(RetrievalInterface):
    """
    Main conversation retrieval system
    
    Orchestrates different retrieval strategies and combines results
    for optimal conversation search experience.
    """
    
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.short_term_memory = ShortTermMemory()
        self.vector_store = VectorStore()
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector("conversation_retriever")
        
        # Retrieval strategies
        self.semantic_search = SemanticSearch()
        self.contextual_retriever = ContextualRetriever()
        self.content_aware_retriever = ContentAwareRetriever()
        self.collaboration_retriever = CollaborationMemoryRetriever()
        
        logger.info("ConversationRetriever initialized")
    
    async def initialize(self):
        """Initialize retrieval components"""
        try:
            await asyncio.gather(
                self.long_term_memory.initialize(),
                self.short_term_memory.initialize(),
                self.vector_store.initialize(),
                self.semantic_search.initialize(),
                self.contextual_retriever.initialize(),
                self.content_aware_retriever.initialize(),
                self.collaboration_retriever.initialize()
            )
            
            logger.info("ConversationRetriever components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ConversationRetriever: {e}")
            raise
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Comprehensive conversation search with multiple strategies
        
        Args:
            query: Search query parameters
            
        Returns:
            Ranked list of search results
        """
        try:
            # Check cache first
            cache_key = f"search:{hash(str(query.to_dict()))}"
            cached_results = await self.cache_manager.get(cache_key)
            
            if cached_results:
                self.metrics.increment("cache_hits")
                return cached_results
            
            # Parallel search strategies
            search_tasks = []
            
            if query.semantic_search and query.text_query:
                search_tasks.append(
                    self.semantic_search.search(query)
                )
            
            if query.collaboration_only:
                search_tasks.append(
                    self.collaboration_retriever.search(query)
                )
            elif query.content_types:
                search_tasks.append(
                    self.content_aware_retriever.search(query)
                )
            else:
                search_tasks.append(
                    self.contextual_retriever.search(query)
                )
            
            # Execute searches in parallel
            strategy_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and rank results
            combined_results = []
            for results in strategy_results:
                if isinstance(results, list):
                    combined_results.extend(results)
            
            # Remove duplicates and rank
            final_results = self._combine_and_rank_results(combined_results, query)
            
            # Apply pagination
            start_idx = query.offset
            end_idx = start_idx + query.limit
            paginated_results = final_results[start_idx:end_idx]
            
            # Cache results
            await self.cache_manager.set(
                cache_key,
                paginated_results,
                ttl=300  # 5 minute cache
            )
            
            self.metrics.increment("searches_performed")
            self.metrics.gauge("search_results_count", len(paginated_results))
            
            return paginated_results
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            self.metrics.increment("search_errors")
            return []
    
    async def get_related_conversations(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[ConversationRecord]:
        """
        Get conversations related to a specific conversation
        
        Args:
            conversation_id: Source conversation identifier
            limit: Maximum results to return
            
        Returns:
            List of related conversations
        """
        try:
            # Get source conversation
            source_conversation = await self.long_term_memory.get(conversation_id)
            
            if not source_conversation:
                return []
            
            # Extract relevant features for similarity
            source_text = self._extract_conversation_text(source_conversation)
            
            # Use semantic search to find similar conversations
            if source_text:
                query = SearchQuery(
                    text_query=source_text,
                    user_id=source_conversation.user_id,
                    content_types=[source_conversation.content_type],
                    semantic_search=True,
                    limit=limit + 1  # +1 to filter out source conversation
                )
                
                search_results = await self.semantic_search.search(query)
                
                # Filter out the source conversation
                related_conversations = [
                    result.conversation
                    for result in search_results
                    if result.conversation.conversation_id != conversation_id
                ]
                
                return related_conversations[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get related conversations for {conversation_id}: {e}")
            self.metrics.increment("related_search_errors")
            return []
    
    def _combine_and_rank_results(
        self,
        results: List[SearchResult],
        query: SearchQuery
    ) -> List[SearchResult]:
        """Combine results from different strategies and rank them"""
        
        # Remove duplicates by conversation_id
        seen_conversations = set()
        unique_results = []
        
        for result in results:
            conv_id = result.conversation.conversation_id
            if conv_id not in seen_conversations:
                seen_conversations.add(conv_id)
                unique_results.append(result)
        
        # Calculate final ranking scores
        for result in unique_results:
            final_score = self._calculate_final_score(result, query)
            result.relevance_score = final_score
        
        # Sort by relevance score (descending)
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results
    
    def _calculate_final_score(self, result: SearchResult, query: SearchQuery) -> float:
        """
Calculate final ranking score for a search result"""
        
        # Base relevance score
        score = result.relevance_score
        
        # Recency boost
        age_days = (datetime.now(timezone.utc) - result.conversation.timestamp).days
        recency_factor = max(0, 1 - (age_days / 30))  # Decay over 30 days
        score += recency_factor * 0.2
        
        # Priority boost
        if result.conversation.priority_score:
            score += result.conversation.priority_score * 0.1
        
        # Content type preference
        if query.content_types and result.conversation.content_type in query.content_types:
            score += 0.15
        
        # Collaboration/protection specific boosts
        if query.collaboration_only and self._is_collaboration_conversation(result.conversation):
            score += 0.2
        
        if query.protection_only and self._is_protection_conversation(result.conversation):
            score += 0.2
        
        # Semantic similarity boost
        if result.similarity_score:
            score += result.similarity_score * 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_conversation_text(self, conversation: ConversationRecord) -> str:
        """
Extract text content from conversation for analysis"""
        text_parts = []
        
        if conversation.conversation_data:
            if "messages" in conversation.conversation_data:
                for message in conversation.conversation_data["messages"]:
                    if "content" in message:
                        text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)
    
    def _is_collaboration_conversation(self, conversation: ConversationRecord) -> bool:
        """Check if conversation is collaboration-related"""
        collaboration_keywords = [
            "collaboration", "collaborate", "partner", "team", "together",
            "joint", "cooperation", "alliance", "partnership"
        ]
        
        text = self._extract_conversation_text(conversation).lower()
        return any(keyword in text for keyword in collaboration_keywords)
    
    def _is_protection_conversation(self, conversation: ConversationRecord) -> bool:
        """Check if conversation is protection-related"""
        protection_keywords = [
            "copyright", "protection", "stolen", "unauthorized", "dmca",
            "piracy", "infringement", "rights", "legal", "violation"
        ]
        
        text = self._extract_conversation_text(conversation).lower()
        return any(keyword in text for keyword in protection_keywords)


class SemanticSearch:
    """
    Semantic search using vector embeddings
    
    Provides semantic similarity search for conversations using
    pre-trained language models and vector similarity.
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.metrics = MetricsCollector("semantic_search")
        
        logger.info("SemanticSearch initialized")
    
    async def initialize(self):
        """Initialize semantic search components"""
        try:
            await self.vector_store.initialize()
            logger.info("SemanticSearch components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize SemanticSearch: {e}")
            raise
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Perform semantic search using embeddings
        
        Args:
            query: Search query parameters
            
        Returns:
            List of semantically similar conversations
        """
        try:
            if not query.text_query:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query.text_query)
            
            # Search vector store
            vector_results = await self.vector_store.search(
                query_embedding,
                k=query.limit * 2,  # Get more for filtering
                user_id=query.user_id
            )
            
            # Convert to SearchResult objects
            search_results = []
            for vector_result in vector_results:
                # Get full conversation record
                conversation = await self._get_conversation_from_vector_result(
                    vector_result
                )
                
                if conversation and self._matches_query_filters(conversation, query):
                    result = SearchResult(
                        conversation=conversation,
                        relevance_score=vector_result["similarity_score"],
                        similarity_score=vector_result["similarity_score"],
                        context_matches=self._extract_context_matches(
                            conversation, query.text_query
                        ),
                        highlight_snippets=self._generate_highlights(
                            conversation, query.text_query
                        )
                    )
                    
                    search_results.append(result)
            
            self.metrics.increment("semantic_searches")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            self.metrics.increment("semantic_search_errors")
            return []
    
    async def _get_conversation_from_vector_result(
        self,
        vector_result: Dict[str, Any]
    ) -> Optional[ConversationRecord]:
        """Get full conversation record from vector search result"""
        try:
            conversation_id = vector_result["conversation_id"]
            
            # Try to get from storage
            from .storage import LongTermMemory
            long_term_memory = LongTermMemory()
            
            return await long_term_memory.get(conversation_id)
            
        except Exception as e:
            logger.error(f"Failed to get conversation from vector result: {e}")
            return None
    
    def _matches_query_filters(
        self,
        conversation: ConversationRecord,
        query: SearchQuery
    ) -> bool:
        """Check if conversation matches query filters"""
        
        # Content type filter
        if query.content_types:
            if conversation.content_type not in query.content_types:
                return False
        
        # Date range filter
        if query.date_range:
            start_date, end_date = query.date_range
            if not (start_date <= conversation.timestamp <= end_date):
                return False
        
        # Sentiment filter
        if query.sentiment_range and conversation.sentiment_score:
            min_sentiment, max_sentiment = query.sentiment_range
            if not (min_sentiment <= conversation.sentiment_score <= max_sentiment):
                return False
        
        # Priority filter
        if query.priority_threshold and conversation.priority_score:
            if conversation.priority_score < query.priority_threshold:
                return False
        
        return True
    
    def _extract_context_matches(
        self,
        conversation: ConversationRecord,
        query_text: str
    ) -> List[str]:
        """
Extract context matches for highlighting"""
        
        matches = []
        query_words = query_text.lower().split()
        
        # Extract conversation text
        if conversation.conversation_data and "messages" in conversation.conversation_data:
            for message in conversation.conversation_data["messages"]:
                content = message.get("content", "")
                if isinstance(content, str):
                    content_lower = content.lower()
                    
                    # Check for word matches
                    for word in query_words:
                        if word in content_lower:
                            # Extract surrounding context
                            start_idx = max(0, content_lower.find(word) - 50)
                            end_idx = min(len(content), content_lower.find(word) + len(word) + 50)
                            context = content[start_idx:end_idx].strip()
                            
                            if context and context not in matches:
                                matches.append(context)
        
        return matches[:5]  # Limit to 5 matches
    
    def _generate_highlights(
        self,
        conversation: ConversationRecord,
        query_text: str
    ) -> List[str]:
        """Generate highlighted snippets"""
        
        highlights = []
        query_words = set(query_text.lower().split())
        
        # Extract conversation text
        conversation_text = ""
        if conversation.conversation_data and "messages" in conversation.conversation_data:
            for message in conversation.conversation_data["messages"]:
                content = message.get("content", "")
                if isinstance(content, str):
                    conversation_text += content + " "
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', conversation_text)
        
        # Score sentences based on query word matches
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum length
                words = set(sentence.lower().split())
                overlap = len(query_words.intersection(words))
                
                if overlap > 0:
                    score = overlap / len(query_words)
                    scored_sentences.append((sentence, score))
        
        # Sort by score and take top highlights
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        highlights = [sentence for sentence, score in scored_sentences[:3]]
        
        return highlights


class ContextualRetriever:
    """
    Context-aware conversation retrieval
    
    Retrieves conversations based on contextual understanding
    including conversation context, user patterns, and temporal factors.
    """
    
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.metrics = MetricsCollector("contextual_retriever")
        
        logger.info("ContextualRetriever initialized")
    
    async def initialize(self):
        """Initialize contextual retrieval components"""
        try:
            await self.long_term_memory.initialize()
            logger.info("ContextualRetriever initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContextualRetriever: {e}")
            raise
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Perform context-aware search
        
        Args:
            query: Search query parameters
            
        Returns:
            List of contextually relevant conversations
        """
        try:
            # Build database query
            db_query = {
                "user_id": query.user_id,
                "limit": query.limit,
                "offset": query.offset,
                "order_by": "timestamp",
                "order_dir": "desc"
            }
            
            # Add filters
            if query.content_types:
                # For multiple content types, we'll filter after retrieval
                pass
            
            if query.date_range:
                db_query["start_date"] = query.date_range[0]
                db_query["end_date"] = query.date_range[1]
            
            if query.text_query:
                db_query["text_query"] = query.text_query
            
            # Get conversations from database
            conversations = await self.long_term_memory.search(db_query)
            
            # Convert to SearchResult with contextual scoring
            search_results = []
            for conversation in conversations:
                relevance_score = self._calculate_contextual_relevance(
                    conversation, query
                )
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    result = SearchResult(
                        conversation=conversation,
                        relevance_score=relevance_score,
                        context_matches=self._identify_context_matches(
                            conversation, query
                        )
                    )
                    search_results.append(result)
            
            # Sort by relevance
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            self.metrics.increment("contextual_searches")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to perform contextual search: {e}")
            self.metrics.increment("contextual_search_errors")
            return []
    
    def _calculate_contextual_relevance(
        self,
        conversation: ConversationRecord,
        query: SearchQuery
    ) -> float:
        """Calculate contextual relevance score"""
        
        score = 0.5  # Base score
        
        # Content type matching
        if query.content_types:
            if conversation.content_type in query.content_types:
                score += 0.3
            else:
                score -= 0.2
        
        # Collaboration context
        if query.collaboration_only:
            if self._has_collaboration_context(conversation):
                score += 0.4
            else:
                score -= 0.3
        
        # Protection context
        if query.protection_only:
            if self._has_protection_context(conversation):
                score += 0.4
            else:
                score -= 0.3
        
        # Recency factor
        age_days = (datetime.now(timezone.utc) - conversation.timestamp).days
        recency_factor = max(0, 1 - (age_days / 30))
        score += recency_factor * 0.2
        
        # Priority factor
        if conversation.priority_score:
            score += conversation.priority_score * 0.1
        
        return max(0, min(score, 1.0))
    
    def _has_collaboration_context(self, conversation: ConversationRecord) -> bool:
        """
Check if conversation has collaboration context"""
        if conversation.context and isinstance(conversation.context, CollaborationContext):
            return True
        
        # Check metadata for collaboration indicators
        if conversation.metadata:
            collab_indicators = conversation.metadata.get("collaboration_indicators", [])
            return len(collab_indicators) > 0
        
        return False
    
    def _has_protection_context(self, conversation: ConversationRecord) -> bool:
        """Check if conversation has protection context"""
        if conversation.context and isinstance(conversation.context, ProtectionContext):
            return True
        
        # Check metadata for protection flags
        if conversation.metadata:
            protection_flags = conversation.metadata.get("protection_flags", [])
            return len(protection_flags) > 0
        
        return False
    
    def _identify_context_matches(
        self,
        conversation: ConversationRecord,
        query: SearchQuery
    ) -> List[str]:
        """Identify context-specific matches"""
        
        matches = []
        
        # Context type matches
        if conversation.context:
            if isinstance(conversation.context, ContentContext):
                matches.append(f"Content: {conversation.context.content_type}")
            elif isinstance(conversation.context, CollaborationContext):
                matches.append(f"Collaboration: {conversation.context.collaboration_type}")
            elif isinstance(conversation.context, ProtectionContext):
                matches.append(f"Protection: {conversation.context.protection_type}")
        
        # Metadata matches
        if conversation.metadata:
            if query.collaboration_only and conversation.metadata.get("collaboration_indicators"):
                matches.extend(conversation.metadata["collaboration_indicators"][:2])
            
            if query.protection_only and conversation.metadata.get("protection_flags"):
                matches.extend(conversation.metadata["protection_flags"][:2])
        
        return matches


class ContentAwareRetriever:
    """
    Content-type aware conversation retrieval
    
    Specializes in retrieving conversations based on content creation
    specializations (music, blog, photography, video, etc.).
    """
    
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.metrics = MetricsCollector("content_aware_retriever")
        
        # Content type specific keywords
        self.content_keywords = {
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
            ],
            ContentType.COMEDY_CONTENT: [
                "comedy", "humor", "funny", "joke", "entertainment",
                "performance", "audience", "laughter", "timing"
            ]
        }
        
        logger.info("ContentAwareRetriever initialized")
    
    async def initialize(self):
        """Initialize content-aware retrieval components"""
        try:
            await self.long_term_memory.initialize()
            logger.info("ContentAwareRetriever initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContentAwareRetriever: {e}")
            raise
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Perform content-aware search
        
        Args:
            query: Search query parameters
            
        Returns:
            List of content-relevant conversations
        """
        try:
            search_results = []
            
            # Search for each content type
            for content_type in query.content_types or []:
                content_results = await self._search_by_content_type(
                    content_type, query
                )
                search_results.extend(content_results)
            
            # Remove duplicates and sort
            seen_conversations = set()
            unique_results = []
            
            for result in search_results:
                conv_id = result.conversation.conversation_id
                if conv_id not in seen_conversations:
                    seen_conversations.add(conv_id)
                    unique_results.append(result)
            
            # Sort by relevance
            unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            self.metrics.increment("content_aware_searches")
            return unique_results[:query.limit]
            
        except Exception as e:
            logger.error(f"Failed to perform content-aware search: {e}")
            self.metrics.increment("content_aware_search_errors")
            return []
    
    async def _search_by_content_type(
        self,
        content_type: str,
        query: SearchQuery
    ) -> List[SearchResult]:
        """Search conversations for a specific content type"""
        
        # Build database query
        db_query = {
            "content_type": content_type,
            "user_id": query.user_id,
            "limit": query.limit,
            "order_by": "timestamp",
            "order_dir": "desc"
        }
        
        if query.date_range:
            db_query["start_date"] = query.date_range[0]
            db_query["end_date"] = query.date_range[1]
        
        if query.text_query:
            db_query["text_query"] = query.text_query
        
        # Get conversations
        conversations = await self.long_term_memory.search(db_query)
        
        # Convert to SearchResult with content-specific scoring
        search_results = []
        for conversation in conversations:
            relevance_score = self._calculate_content_relevance(
                conversation, content_type, query
            )
            
            result = SearchResult(
                conversation=conversation,
                relevance_score=relevance_score,
                context_matches=self._extract_content_matches(
                    conversation, content_type, query
                )
            )
            search_results.append(result)
        
        return search_results
    
    def _calculate_content_relevance(
        self,
        conversation: ConversationRecord,
        content_type: str,
        query: SearchQuery
    ) -> float:
        """Calculate content-specific relevance score"""
        
        score = 0.5  # Base score
        
        # Exact content type match
        if conversation.content_type == content_type:
            score += 0.3
        
        # Keyword matching
        conversation_text = self._extract_conversation_text(conversation)
        if conversation_text:
            content_type_enum = None
            try:
                content_type_enum = ContentType(content_type)
            except ValueError:
                pass
            
            if content_type_enum and content_type_enum in self.content_keywords:
                keywords = self.content_keywords[content_type_enum]
                text_lower = conversation_text.lower()
                
                keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
                keyword_score = min(keyword_matches / len(keywords), 0.3)
                score += keyword_score
        
        # Query text matching
        if query.text_query and conversation_text:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__extract_content_matches_input(conversation)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__extract_content_matches_result(result)
            
                    logger.info(f"AI processing _extract_content_matches completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _extract_content_matches failed: {e}")
                    raise
        conversation_text = self._extract_conversation_text(conversation)
        if conversation_text:
            try:
                content_type_enum = ContentType(content_type)
                if content_type_enum in self.content_keywords:
                    keywords = self.content_keywords[content_type_enum]
                    text_lower = conversation_text.lower()
                    
                    found_keywords = [
                        keyword for keyword in keywords
                        if keyword in text_lower
                    ]
                    
                    if found_keywords:
                        keyword_text = ", ".join(found_keywords[:3])
                        matches.append(f"Keywords: {keyword_text}")
            
            except ValueError:
                pass
        
        return matches
    
    def _extract_conversation_text(self, conversation: ConversationRecord) -> str:
        """Extract text content from conversation"""
        text_parts = []
        
        if conversation.conversation_data and "messages" in conversation.conversation_data:
            for message in conversation.conversation_data["messages"]:
                if "content" in message:
                    text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)


class CollaborationMemoryRetriever:
    """
    Specialized retrieval for collaboration-related conversations
    
    Focuses on retrieving conversations related to collaboration
    opportunities, partner matching, and joint content creation.
    """
    
    def __init__(self):
        self.long_term_memory = LongTermMemory()
        self.metrics = MetricsCollector("collaboration_retriever")
        
        logger.info("CollaborationMemoryRetriever initialized")
    
    async def initialize(self):
        """Initialize collaboration retrieval components"""
        try:
            await self.long_term_memory.initialize()
            logger.info("CollaborationMemoryRetriever initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize CollaborationMemoryRetriever: {e}")
            raise
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Search for collaboration-related conversations
        
        Args:
            query: Search query parameters
            
        Returns:
            List of collaboration-relevant conversations
        """
        try:
            # Build query for collaboration conversations
            db_query = {
                "user_id": query.user_id,
                "limit": query.limit * 2,  # Get more for filtering
                "order_by": "timestamp",
                "order_dir": "desc"
            }
            
            if query.date_range:
                db_query["start_date"] = query.date_range[0]
                db_query["end_date"] = query.date_range[1]
            
            # Get all conversations and filter for collaboration
            conversations = await self.long_term_memory.search(db_query)
            
            # Filter and score collaboration conversations
            collaboration_results = []
            for conversation in conversations:
                if self._is_collaboration_conversation(conversation):
                    relevance_score = self._calculate_collaboration_relevance(
                        conversation, query
                    )
                    
                    result = SearchResult(
                        conversation=conversation,
                        relevance_score=relevance_score,
                        context_matches=self._extract_collaboration_matches(
                            conversation, query
                        )
                    )
                    collaboration_results.append(result)
            
            # Sort by relevance and apply limit
            collaboration_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            self.metrics.increment("collaboration_searches")
            return collaboration_results[:query.limit]
            
        except Exception as e:
            logger.error(f"Failed to search collaboration conversations: {e}")
            self.metrics.increment("collaboration_search_errors")
            return []
    
    def _is_collaboration_conversation(self, conversation: ConversationRecord) -> bool:
        """Check if conversation is collaboration-related"""
        
        # Check context
        if conversation.context and isinstance(conversation.context, CollaborationContext):
            return True
        
        # Check metadata
        if conversation.metadata:
            collab_indicators = conversation.metadata.get("collaboration_indicators", [])
            if collab_indicators:
                return True
        
        # Check content for collaboration keywords
        collaboration_keywords = [
            "collaboration", "collaborate", "partner", "team", "together",
            "joint", "cooperation", "alliance", "partnership", "collab",
            "work together", "team up", "join forces", "combine efforts"
        ]
        
        conversation_text = self._extract_conversation_text(conversation).lower()
        return any(keyword in conversation_text for keyword in collaboration_keywords)
    
    def _calculate_collaboration_relevance(
        self,
        conversation: ConversationRecord,
        query: SearchQuery
    ) -> float:
        """Calculate collaboration-specific relevance score"""
        
        score = 0.5  # Base score
        
        # Strong boost for collaboration context
        if conversation.context and isinstance(conversation.context, CollaborationContext):
            score += 0.4
            
            # Specific collaboration type matching
            if query.text_query:
                query_lower = query.text_query.lower()
                collab_type = conversation.context.collaboration_type.lower()
                
                if collab_type in query_lower:
                    score += 0.2
        
        # Metadata collaboration indicators
        if conversation.metadata:
            collab_indicators = conversation.metadata.get("collaboration_indicators", [])
            if collab_indicators:
                score += min(len(collab_indicators) * 0.1, 0.3)
        
        # Text content matching
        if query.text_query:
            conversation_text = self._extract_conversation_text(conversation)
            if conversation_text:
                query_words = set(query.text_query.lower().split())
                text_words = set(conversation_text.lower().split())
                
                overlap = len(query_words.intersection(text_words))
                if overlap > 0:
                    score += min(overlap / len(query_words), 0.2)
        
        # Recency factor for collaboration
        age_days = (datetime.now(timezone.utc) - conversation.timestamp).days
        if age_days <= 7:  # Recent collaborations are more relevant
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_collaboration_matches(
        self,
        conversation: ConversationRecord,
        query: SearchQuery
    ) -> List[str]:
        """Extract collaboration-specific matches"""
        
        matches = []
        
        # Context information
        if conversation.context and isinstance(conversation.context, CollaborationContext):
            matches.append(f"Collaboration Type: {conversation.context.collaboration_type}")
            
            if conversation.context.partner_types:
                partners = ", ".join(conversation.context.partner_types[:3])
                matches.append(f"Partner Types: {partners}")
            
            if conversation.context.collaboration_scope:
                matches.append(f"Scope: {conversation.context.collaboration_scope}")
        
        # Metadata indicators
        if conversation.metadata:
            collab_indicators = conversation.metadata.get("collaboration_indicators", [])
            if collab_indicators:
                indicators = ", ".join(collab_indicators[:3])
                matches.append(f"Indicators: {indicators}")
        
        return matches
    
    def _extract_conversation_text(self, conversation: ConversationRecord) -> str:
        """Extract text content from conversation"""
        text_parts = []
        
        if conversation.conversation_data and "messages" in conversation.conversation_data:
            for message in conversation.conversation_data["messages"]:
                if "content" in message:
                    text_parts.append(str(message["content"]))
        
        if conversation.raw_content:
            text_parts.append(conversation.raw_content)
        
        return " ".join(text_parts)


# Export all retrieval classes
__all__ = [
    # Core retrieval
    "RetrievalInterface",
    "ConversationRetriever",
    
    # Specialized retrievers
    "SemanticSearch",
    "ContextualRetriever", 
    "ContentAwareRetriever",
    "CollaborationMemoryRetriever",
    
    # Data structures
    "SearchQuery",
    "SearchResult"
]
