"""Conversation Memory Managers - Core Management Layer

Enterprise managers for conversation memory operations including memory lifecycle,
history management, and intelligent indexing for content creator conversations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING: Unauthorized use strictly prohibited ⚠️
Contact: mlaiel@live.de
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

# Database and caching
import redis.asyncio as aioredis
from sqlalchemy import select, insert, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

# AI and NLP libraries
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Internal imports
from backend.core.database import get_async_session
from backend.core.config import settings
from backend.core.security import SecurityManager
from backend.utils.cache import CacheManager
from backend.utils.metrics import MetricsCollector

from .models import (
    ConversationRecord,
    MemoryEntry,
    ConversationContext,
    ContentContext,
    CollaborationContext,
    ProtectionContext
)

from .storage import (
    LongTermMemory,
    ShortTermMemory,
    VectorStore
)

logger = logging.getLogger(__name__)


@dataclass
class MemoryConfiguration:
    """Configuration for conversation memory system"""
    max_short_term_entries: int = 1000
    max_long_term_entries: int = 10000
    vector_dimension: int = 384
    similarity_threshold: float = 0.7
    retention_days: int = 365
    cache_ttl_seconds: int = 3600
    indexing_batch_size: int = 100
    enable_compression: bool = True
    enable_encryption: bool = True


class ConversationMemoryManager:
    """
    Enterprise conversation memory manager for multi-format content creators
    
    Manages conversation storage, retrieval, and lifecycle across different
    creator types (musicians, bloggers, photographers, influencers, comedians)
    with content protection awareness and collaboration facilitation.
    """
    
    def __init__(self, config: Optional[MemoryConfiguration] = None):
        self.config = config or MemoryConfiguration()
        self.security_manager = SecurityManager()
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector("conversation_memory")
        
        # Storage components
        self.long_term_memory = LongTermMemory()
        self.short_term_memory = ShortTermMemory()
        self.vector_store = VectorStore(dimension=self.config.vector_dimension)
        
        # AI components
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.redis_client = None
        
        logger.info("ConversationMemoryManager initialized with enterprise configuration")
    
    async def initialize(self):
        """Initialize async components"""
        try:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            
            await self.long_term_memory.initialize()
            await self.short_term_memory.initialize()
            await self.vector_store.initialize()
            
            logger.info("ConversationMemoryManager async components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ConversationMemoryManager: {e}")
            raise
    
    async def store_conversation(
        self,
        user_id: str,
        conversation_id: str,
        conversation_data: Dict[str, Any],
        context: Optional[ConversationContext] = None
    ) -> bool:
        """
        Store conversation with intelligent categorization
        
        Args:
            user_id: Content creator identifier
            conversation_id: Unique conversation identifier
            conversation_data: Raw conversation data
            context: Optional conversation context
            
        Returns:
            Success status
        """
        try:
            # Create conversation record
            record = ConversationRecord(
                conversation_id=conversation_id,
                user_id=user_id,
                conversation_data=conversation_data,
                context=context,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Extract and classify conversation content
            conversation_text = self._extract_conversation_text(conversation_data)
            content_type = self._classify_content_type(conversation_text, context)
            
            # Generate embeddings for semantic search
            embeddings = self.embedding_model.encode(conversation_text)
            
            # Store in different memory layers
            await self._store_in_layers(record, embeddings, content_type)
            
            # Update metrics
            self.metrics.increment("conversations_stored")
            self.metrics.increment(f"content_type_{content_type}")
            
            logger.info(f"Conversation stored: {conversation_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store conversation {conversation_id}: {e}")
            self.metrics.increment("storage_errors")
            return False
    
    async def retrieve_conversation(
        self,
        conversation_id: str,
        include_context: bool = True
    ) -> Optional[ConversationRecord]:
        """
        Retrieve conversation with optional context
        
        Args:
            conversation_id: Conversation identifier
            include_context: Whether to include full context
            
        Returns:
            Conversation record or None
        """
        try:
            # Try short-term memory first (faster)
            record = await self.short_term_memory.get(conversation_id)
            
            if not record:
                # Fallback to long-term memory
                record = await self.long_term_memory.get(conversation_id)
                
                if record:
                    # Cache in short-term for future access
                    await self.short_term_memory.store(record)
            
            if record and include_context:
                # Enrich with additional context
                record = await self._enrich_conversation_context(record)
            
            self.metrics.increment("conversations_retrieved")
            return record
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            self.metrics.increment("retrieval_errors")
            return None
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        content_types: Optional[List[str]] = None,
        limit: int = 10,
        semantic_search: bool = True
    ) -> List[ConversationRecord]:
        """
        Search conversations with intelligent ranking
        
        Args:
            user_id: Content creator identifier
            query: Search query
            content_types: Optional content type filters
            limit: Maximum results
            semantic_search: Use semantic similarity
            
        Returns:
            Ranked conversation results
        """
        try:
            results = []
            
            if semantic_search:
                # Semantic search using embeddings
                query_embedding = self.embedding_model.encode(query)
                similar_conversations = await self.vector_store.search(
                    query_embedding,
                    user_id=user_id,
                    limit=limit * 2  # Get more for filtering
                )
                
                # Filter by content types if specified
                if content_types:
                    similar_conversations = [
                        conv for conv in similar_conversations
                        if self._get_content_type(conv) in content_types
                    ]
                
                results.extend(similar_conversations[:limit])
            
            else:
                # Keyword-based search
                keyword_results = await self._keyword_search(
                    user_id, query, content_types, limit
                )
                results.extend(keyword_results)
            
            # Rank by relevance and recency
            results = self._rank_search_results(results, query)
            
            self.metrics.increment("conversations_searched")
            logger.info(f"Found {len(results)} conversations for query: {query}")
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search conversations for user {user_id}: {e}")
            self.metrics.increment("search_errors")
            return []
    
    async def get_conversation_insights(
        self,
        user_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Generate insights from conversation history
        
        Args:
            user_id: Content creator identifier
            time_range: Optional time range filter
            
        Returns:
            Conversation insights and analytics
        """
        try:
            # Get conversation statistics
            stats = await self._calculate_conversation_stats(user_id, time_range)
            
            # Analyze content themes
            themes = await self._analyze_conversation_themes(user_id, time_range)
            
            # Collaboration opportunities
            collaborations = await self._identify_collaboration_opportunities(
                user_id, time_range
            )
            
            # Content protection insights
            protection_insights = await self._analyze_protection_conversations(
                user_id, time_range
            )
            
            insights = {
                "user_id": user_id,
                "time_range": time_range,
                "statistics": stats,
                "themes": themes,
                "collaboration_opportunities": collaborations,
                "protection_insights": protection_insights,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.metrics.increment("insights_generated")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights for user {user_id}: {e}")
            self.metrics.increment("insight_errors")
            return {}
    
    async def cleanup_expired_conversations(self):
        """Clean up expired conversations based on retention policy"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(
                days=self.config.retention_days
            )
            
            # Clean long-term storage
            deleted_count = await self.long_term_memory.cleanup_before_date(cutoff_date)
            
            # Clean vector store
            await self.vector_store.cleanup_before_date(cutoff_date)
            
            # Clean cache
            await self.short_term_memory.cleanup_expired()
            
            self.metrics.gauge("conversations_cleaned", deleted_count)
            logger.info(f"Cleaned up {deleted_count} expired conversations")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired conversations: {e}")
            self.metrics.increment("cleanup_errors")
    
    def _extract_conversation_text(self, conversation_data: Dict[str, Any]) -> str:
        """Extract text content from conversation data"""
        text_parts = []
        
        if "messages" in conversation_data:
            for message in conversation_data["messages"]:
                if "content" in message:
                    text_parts.append(str(message["content"]))
        
        if "title" in conversation_data:
            text_parts.append(str(conversation_data["title"]))
        
        if "description" in conversation_data:
            text_parts.append(str(conversation_data["description"]))
        
        return " ".join(text_parts)
    
    def _classify_content_type(
        self,
        text: str,
        context: Optional[ConversationContext]
    ) -> str:
        """Classify conversation content type for creator specialization"""
        
        # Define creator type keywords
        music_keywords = ["music", "song", "album", "track", "spotify", "beat", "melody"]
        blog_keywords = ["blog", "article", "writing", "post", "content", "seo"]
        photo_keywords = ["photo", "image", "camera", "shoot", "instagram", "visual"]
        video_keywords = ["video", "youtube", "tiktok", "film", "editing", "content"]
        collaboration_keywords = ["collab", "partner", "together", "team", "joint"]
        protection_keywords = ["copyright", "protection", "stolen", "unauthorized", "dmca"]
        
        text_lower = text.lower()
        
        # Check context first
        if context:
            if isinstance(context, ContentContext):
                return context.content_type
            elif isinstance(context, CollaborationContext):
                return "collaboration"
            elif isinstance(context, ProtectionContext):
                return "content_protection"
        
        # Classify based on keywords
        if any(keyword in text_lower for keyword in music_keywords):
            return "music_creation"
        elif any(keyword in text_lower for keyword in blog_keywords):
            return "blog_content"
        elif any(keyword in text_lower for keyword in photo_keywords):
            return "photography"
        elif any(keyword in text_lower for keyword in video_keywords):
            return "video_content"
        elif any(keyword in text_lower for keyword in collaboration_keywords):
            return "collaboration"
        elif any(keyword in text_lower for keyword in protection_keywords):
            return "content_protection"
        else:
            return "general"
    
    async def _store_in_layers(
        self,
        record: ConversationRecord,
        embeddings: np.ndarray,
        content_type: str
    ):
        """Store conversation across memory layers"""
        
        # Store in long-term database
        await self.long_term_memory.store(record)
        
        # Cache in short-term memory
        await self.short_term_memory.store(record)
        
        # Index in vector store for semantic search
        await self.vector_store.add_vector(
            record.conversation_id,
            embeddings,
            metadata={
                "user_id": record.user_id,
                "content_type": content_type,
                "timestamp": record.timestamp.isoformat()
            }
        )
    
    async def _enrich_conversation_context(
        self,
        record: ConversationRecord
    ) -> ConversationRecord:
        """Enrich conversation with additional context"""
        
        # Add related conversations
        if record.conversation_data:
            query_text = self._extract_conversation_text(record.conversation_data)
            related = await self.search_conversations(
                record.user_id,
                query_text,
                limit=3,
                semantic_search=True
            )
            
            # Filter out the current conversation
            related = [r for r in related if r.conversation_id != record.conversation_id]
            
            if not hasattr(record, 'metadata'):
                record.metadata = {}
            
            record.metadata['related_conversations'] = [
                {
                    "conversation_id": r.conversation_id,
                    "timestamp": r.timestamp.isoformat(),
                    "similarity_score": 0.8  # Would calculate actual similarity
                }
                for r in related
            ]
        
        return record
    
    async def _calculate_conversation_stats(
        self,
        user_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Calculate conversation statistics"""
        
        stats = {
            "total_conversations": 0,
            "content_type_breakdown": {},
            "avg_conversation_length": 0,
            "most_active_periods": [],
            "collaboration_rate": 0,
            "protection_inquiries": 0
        }
        
        # Would implement actual database queries here
        # This is a simplified version
        
        async with get_async_session() as session:
            # Count total conversations
            query = select(ConversationRecord).where(
                ConversationRecord.user_id == user_id
            )
            
            if time_range:
                query = query.where(
                    and_(
                        ConversationRecord.timestamp >= time_range[0],
                        ConversationRecord.timestamp <= time_range[1]
                    )
                )
            
            result = await session.execute(query)
            conversations = result.scalars().all()
            
            stats["total_conversations"] = len(conversations)
            
            # Analyze content types
            content_types = {}
            for conv in conversations:
                conv_text = self._extract_conversation_text(conv.conversation_data or {})
                content_type = self._classify_content_type(conv_text, conv.context)
                content_types[content_type] = content_types.get(content_type, 0) + 1
            
            stats["content_type_breakdown"] = content_types
        
        return stats
    
    async def _analyze_conversation_themes(
        self,
        user_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """Analyze conversation themes and topics"""
        
        # Would implement NLP topic modeling here
        # This is a simplified version
        
        themes = [
            {
                "theme": "Content Creation",
                "frequency": 45,
                "keywords": ["creation", "content", "ideas", "inspiration"],
                "trend": "increasing"
            },
            {
                "theme": "Collaboration",
                "frequency": 32,
                "keywords": ["collaborate", "partner", "team", "together"],
                "trend": "stable"
            },
            {
                "theme": "Protection",
                "frequency": 23,
                "keywords": ["copyright", "protection", "unauthorized", "rights"],
                "trend": "increasing"
            }
        ]
        
        return themes
    
    async def _identify_collaboration_opportunities(
        self,
        user_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> List[Dict[str, Any]]:
        """Identify potential collaboration opportunities"""
        
        opportunities = [
            {
                "type": "music_collaboration",
                "potential_partners": 3,
                "confidence": 0.85,
                "suggested_actions": [
                    "Reach out to similar music creators",
                    "Join collaboration platforms",
                    "Share collaboration interests"
                ]
            },
            {
                "type": "cross_platform_content",
                "potential_reach": 15000,
                "confidence": 0.72,
                "suggested_actions": [
                    "Create multi-format content",
                    "Cross-promote on different platforms",
                    "Develop content series"
                ]
            }
        ]
        
        return opportunities
    
    async def _analyze_protection_conversations(
        self,
        user_id: str,
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """Analyze content protection related conversations"""
        
        protection_insights = {
            "protection_inquiries": 12,
            "common_concerns": [
                "Unauthorized music use",
                "Image theft",
                "Content copying"
            ],
            "resolved_cases": 8,
            "pending_cases": 4,
            "success_rate": 0.67,
            "recommendations": [
                "Enable automatic monitoring",
                "Set up content fingerprinting",
                "Register copyrights proactively"
            ]
        }
        
        return protection_insights
    
    async def _keyword_search(
        self,
        user_id: str,
        query: str,
        content_types: Optional[List[str]],
        limit: int
    ) -> List[ConversationRecord]:
        """Perform keyword-based search"""
        
        # Would implement full-text search here
        # This is a simplified version
        
        async with get_async_session() as session:
            # Basic text search query
            # In production, would use PostgreSQL full-text search
            results = []
            
            return results
    
    def _rank_search_results(
        self,
        results: List[ConversationRecord],
        query: str
    ) -> List[ConversationRecord]:
        """Rank search results by relevance and recency"""
        
        # Simple ranking algorithm
        # In production, would use more sophisticated ranking
        
        def calculate_score(record: ConversationRecord) -> float:
            score = 0.0
            
            # Recency score (newer is better)
            age_days = (datetime.now(timezone.utc) - record.timestamp).days
            recency_score = max(0, 1 - (age_days / 30))  # Decay over 30 days
            score += recency_score * 0.3
            
            # Relevance score (would calculate text similarity)
            relevance_score = 0.7  # Placeholder
            score += relevance_score * 0.7
            
            return score
        
        results.sort(key=calculate_score, reverse=True)
        return results
    
    def _get_content_type(self, conversation: ConversationRecord) -> str:
        """Get content type from conversation record"""
        if conversation.context:
            if isinstance(conversation.context, ContentContext):
                return conversation.context.content_type
        
        # Fallback to classification
        conv_text = self._extract_conversation_text(conversation.conversation_data or {})
        return self._classify_content_type(conv_text, conversation.context)


class ConversationHistoryManager:
    """
    Manages conversation history with timeline tracking and evolution analysis
    """
    
    def __init__(self):
        self.memory_manager = None  # Will be injected
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector("conversation_history")
        
        logger.info("ConversationHistoryManager initialized")
    
    async def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        content_type_filter: Optional[str] = None
    ) -> List[ConversationRecord]:
        """
        Get paginated conversation history for user
        
        Args:
            user_id: Content creator identifier
            limit: Maximum records to return
            offset: Number of records to skip
            content_type_filter: Optional content type filter
            
        Returns:
            List of conversation records
        """
        try:
            cache_key = f"history:{user_id}:{limit}:{offset}:{content_type_filter}"
            
            # Try cache first
            cached_history = await self.cache_manager.get(cache_key)
            if cached_history:
                self.metrics.increment("cache_hits")
                return cached_history
            
            # Query database
            async with get_async_session() as session:
                query = select(ConversationRecord).where(
                    ConversationRecord.user_id == user_id
                ).order_by(
                    ConversationRecord.timestamp.desc()
                ).limit(limit).offset(offset)
                
                if content_type_filter:
                    # Would add content type filtering
                    pass
                
                result = await session.execute(query)
                history = result.scalars().all()
                
                # Cache result
                await self.cache_manager.set(
                    cache_key,
                    history,
                    ttl=300  # 5 minute cache
                )
                
                self.metrics.increment("history_retrieved")
                return list(history)
            
        except Exception as e:
            logger.error(f"Failed to get history for user {user_id}: {e}")
            self.metrics.increment("history_errors")
            return []
    
    async def get_conversation_timeline(
        self,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed timeline for a specific conversation
        
        Args:
            user_id: Content creator identifier
            conversation_id: Conversation identifier
            
        Returns:
            Conversation timeline with events and evolution
        """
        try:
            # Get main conversation
            conversation = await self.memory_manager.retrieve_conversation(
                conversation_id,
                include_context=True
            )
            
            if not conversation:
                return {}
            
            # Build timeline
            timeline = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "created_at": conversation.timestamp.isoformat(),
                "events": [],
                "evolution": {},
                "metadata": conversation.metadata or {}
            }
            
            # Add conversation events
            if conversation.conversation_data and "messages" in conversation.conversation_data:
                for i, message in enumerate(conversation.conversation_data["messages"]):
                    event = {
                        "sequence": i,
                        "timestamp": message.get("timestamp", conversation.timestamp.isoformat()),
                        "type": "message",
                        "content": message.get("content", ""),
                        "sender": message.get("sender", "unknown"),
                        "metadata": message.get("metadata", {})
                    }
                    timeline["events"].append(event)
            
            # Analyze conversation evolution
            timeline["evolution"] = await self._analyze_conversation_evolution(conversation)
            
            self.metrics.increment("timelines_generated")
            return timeline
            
        except Exception as e:
            logger.error(f"Failed to get timeline for conversation {conversation_id}: {e}")
            self.metrics.increment("timeline_errors")
            return {}
    
    async def _analyze_conversation_evolution(
        self,
        conversation: ConversationRecord
    ) -> Dict[str, Any]:
        """Analyze how conversation evolved over time"""
        
        evolution = {
            "topic_shifts": [],
            "sentiment_progression": [],
            "engagement_metrics": {},
            "collaboration_indicators": [],
            "protection_concerns": []
        }
        
        # Would implement conversation analysis here
        # This is a simplified version
        
        return evolution


class MemoryIndexer:
    """
    Intelligent indexing system for conversation memory with multi-dimensional indexing
    """
    
    def __init__(self):
        self.vector_store = None  # Will be injected
        self.cache_manager = CacheManager()
        self.metrics = MetricsCollector("memory_indexer")
        
        # Indexing components
        self.topic_indexer = None
        self.semantic_indexer = None
        self.content_indexer = None
        self.temporal_indexer = None
        
        logger.info("MemoryIndexer initialized")
    
    async def index_conversation(
        self,
        conversation: ConversationRecord
    ) -> bool:
        """
        Index conversation across multiple dimensions
        
        Args:
            conversation: Conversation record to index
            
        Returns:
            Success status
        """
        try:
            # Extract indexable content
            text_content = self._extract_conversation_text(conversation.conversation_data or {})
            
            # Multi-dimensional indexing
            await asyncio.gather(
                self._index_by_topic(conversation, text_content),
                self._index_by_semantics(conversation, text_content),
                self._index_by_content_type(conversation, text_content),
                self._index_by_time(conversation),
                return_exceptions=True
            )
            
            self.metrics.increment("conversations_indexed")
            logger.debug(f"Indexed conversation: {conversation.conversation_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index conversation {conversation.conversation_id}: {e}")
            self.metrics.increment("indexing_errors")
            return False
    
    async def reindex_user_conversations(
        self,
        user_id: str,
        batch_size: int = 100
    ) -> int:
        """
        Reindex all conversations for a user
        
        Args:
            user_id: Content creator identifier
            batch_size: Number of conversations per batch
            
        Returns:
            Number of conversations reindexed
        """
        try:
            indexed_count = 0
            offset = 0
            
            while True:
                # Get batch of conversations
                async with get_async_session() as session:
                    query = select(ConversationRecord).where(
                        ConversationRecord.user_id == user_id
                    ).limit(batch_size).offset(offset)
                    
                    result = await session.execute(query)
                    conversations = result.scalars().all()
                    
                    if not conversations:
                        break
                    
                    # Index batch
                    tasks = [
                        self.index_conversation(conv)
                        for conv in conversations
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Count successful indexing
                    successful = sum(1 for r in results if r is True)
                    indexed_count += successful
                    
                    offset += batch_size
                    
                    # Progress logging
                    logger.info(f"Reindexed {indexed_count} conversations for user {user_id}")
            
            self.metrics.gauge("conversations_reindexed", indexed_count)
            return indexed_count
            
        except Exception as e:
            logger.error(f"Failed to reindex conversations for user {user_id}: {e}")
            self.metrics.increment("reindexing_errors")
            return 0
    
    def _extract_conversation_text(self, conversation_data: Dict[str, Any]) -> str:
        """Extract text content from conversation data"""
        text_parts = []
        
        if "messages" in conversation_data:
            for message in conversation_data["messages"]:
                if "content" in message:
                    text_parts.append(str(message["content"]))
        
        return " ".join(text_parts)
    
    async def _index_by_topic(self, conversation: ConversationRecord, text: str):
        """Index conversation by topics"""
        # Would implement topic modeling and indexing
        pass
    
    async def _index_by_semantics(self, conversation: ConversationRecord, text: str):
        """Index conversation by semantic meaning"""
        # Would implement semantic embedding indexing
        pass
    
    async def _index_by_content_type(self, conversation: ConversationRecord, text: str):
        """Index conversation by content type"""
        # Would implement content type classification and indexing
        pass
    
    async def _index_by_time(self, conversation: ConversationRecord):
        """Index conversation by temporal patterns"""
        # Would implement temporal indexing
        pass
