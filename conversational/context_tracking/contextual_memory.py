"""
Contextual Memory - IA Influencer Agent

Advanced contextual memory system providing intelligent conversation memory
management with semantic understanding and retrieval capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import hashlib

from ...core.exceptions import MemoryError
from ...core.monitoring import MetricsCollector
from ...utils.nlp import TextProcessor, EmbeddingGenerator
from ...utils.cache import CacheManager
from ...utils.vector_search import VectorSearchEngine


class MemoryType(Enum):
    """Types of memory stored in the system"""
    EPISODIC = "episodic"        # Specific conversation episodes
    SEMANTIC = "semantic"        # General knowledge and concepts
    PROCEDURAL = "procedural"    # How-to knowledge and workflows
    EMOTIONAL = "emotional"      # Emotional context and states
    FACTUAL = "factual"         # Facts about user and content
    BEHAVIORAL = "behavioral"    # Behavioral patterns and preferences
    CONTEXTUAL = "contextual"   # Situational context information


class MemoryPersistence(Enum):
    """Memory persistence levels"""
    TRANSIENT = "transient"      # Session-only memory
    SHORT_TERM = "short_term"    # Days to weeks
    MEDIUM_TERM = "medium_term"  # Weeks to months
    LONG_TERM = "long_term"     # Months to years
    PERMANENT = "permanent"      # Never expires


@dataclass
class MemoryNode:
    """Individual memory node with semantic information"""
    memory_id: str
    content: Any
    memory_type: MemoryType
    persistence: MemoryPersistence
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    importance_score: float = 0.5
    confidence: float = 1.0
    embedding: Optional[np.ndarray] = None
    tags: Set[str] = field(default_factory=set)
    relationships: Dict[str, float] = field(default_factory=dict)  # memory_id -> strength
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_access(self):
        """Update access statistics"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
        
        # Update importance based on access patterns
        recency_factor = 1.0 - (datetime.utcnow() - self.created_at).total_seconds() / (86400 * 30)
        frequency_factor = min(self.access_count / 100.0, 1.0)
        self.importance_score = (recency_factor * 0.3 + frequency_factor * 0.7)
    
    def is_expired(self) -> bool:
        """Check if memory should expire"""
        if self.persistence == MemoryPersistence.PERMANENT:
            return False
        
        age = datetime.utcnow() - self.created_at
        
        if self.persistence == MemoryPersistence.TRANSIENT:
            return age > timedelta(hours=24)
        elif self.persistence == MemoryPersistence.SHORT_TERM:
            return age > timedelta(days=14)
        elif self.persistence == MemoryPersistence.MEDIUM_TERM:
            return age > timedelta(days=90)
        elif self.persistence == MemoryPersistence.LONG_TERM:
            return age > timedelta(days=365)
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "persistence": self.persistence.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "relationships": self.relationships,
            "metadata": self.metadata
        }


@dataclass
class MemoryCluster:
    """Cluster of related memories"""
    cluster_id: str
    memories: List[MemoryNode]
    centroid_embedding: np.ndarray
    topic: str
    coherence_score: float
    last_updated: datetime
    
    def update_centroid(self):
        """Update cluster centroid based on member embeddings"""
        if not self.memories or not any(m.embedding is not None for m in self.memories):
            return
        
        embeddings = [m.embedding for m in self.memories if m.embedding is not None]
        if embeddings:
            self.centroid_embedding = np.mean(embeddings, axis=0)
            self.last_updated = datetime.utcnow()


@dataclass
class MemorySearchResult:
    """Result from memory search operation"""
    memory_node: MemoryNode
    relevance_score: float
    reasoning: str
    context_match: bool = False


class ContextualMemory:
    """
    Advanced contextual memory system providing intelligent conversation 
    memory management with semantic understanding and retrieval.
    
    Features:
    - Multi-type memory storage (episodic, semantic, procedural, etc.)
    - Semantic search and retrieval
    - Memory clustering and organization
    - Importance-based retention
    - Relationship mapping between memories
    - Context-aware memory activation
    """
    
    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        text_processor: TextProcessor,
        embedding_generator: EmbeddingGenerator,
        vector_search_engine: VectorSearchEngine,
        max_memories_per_user: int = 50000,
        embedding_dim: int = 768,
        cluster_threshold: float = 0.7
    ):
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.text_processor = text_processor
        self.embedding_generator = embedding_generator
        self.vector_search_engine = vector_search_engine
        self.max_memories_per_user = max_memories_per_user
        self.embedding_dim = embedding_dim
        self.cluster_threshold = cluster_threshold
        
        # Memory storage
        self.user_memories: Dict[str, Dict[str, MemoryNode]] = defaultdict(dict)
        self.memory_clusters: Dict[str, List[MemoryCluster]] = defaultdict(list)
        
        # Memory graphs for relationship tracking
        self.memory_relationships: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        
        # Active memory cache for quick access
        self.active_memories: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        
        # Background processing
        self.maintenance_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ContextualMemory initialized")
    
    async def start(self):
        """Start the contextual memory system"""
        try:
            # Load existing memories
            await self._load_memories()
            
            # Initialize vector search
            await self.vector_search_engine.initialize()
            
            # Start background maintenance
            self.maintenance_task = asyncio.create_task(self._background_maintenance())
            
            self.logger.info("ContextualMemory started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start ContextualMemory: {e}")
            raise MemoryError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the contextual memory system"""
        try:
            # Cancel background tasks
            if self.maintenance_task:
                self.maintenance_task.cancel()
                try:
                    await self.maintenance_task
                except asyncio.CancelledError:
                    pass
            
            # Save memories
            await self._save_memories()
            
            self.logger.info("ContextualMemory stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping ContextualMemory: {e}")
    
    async def store_memory(
        self,
        user_id: str,
        content: Any,
        memory_type: MemoryType,
        persistence: MemoryPersistence = MemoryPersistence.SHORT_TERM,
        importance: float = 0.5,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        related_memories: Optional[List[str]] = None
    ) -> str:
        """
        Store new memory with semantic processing
        
        Args:
            user_id: User identifier
            content: Memory content
            memory_type: Type of memory
            persistence: How long to retain the memory
            importance: Initial importance score (0-1)
            tags: Memory tags for categorization
            metadata: Additional metadata
            related_memories: IDs of related memories
            
        Returns:
            str: Memory ID
        """
        try:
            # Generate memory ID
            memory_id = hashlib.md5(
                f"{user_id}_{datetime.utcnow().isoformat()}_{str(content)[:100]}".encode()
            ).hexdigest()
            
            # Generate embedding for semantic search
            embedding = None
            if isinstance(content, str):
                embedding = await self.embedding_generator.generate_embedding(content)
            elif isinstance(content, dict) and 'text' in content:
                embedding = await self.embedding_generator.generate_embedding(content['text'])
            
            # Create memory node
            memory_node = MemoryNode(
                memory_id=memory_id,
                content=content,
                memory_type=memory_type,
                persistence=persistence,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                importance_score=importance,
                embedding=embedding,
                tags=tags or set(),
                metadata=metadata or {}
            )
            
            # Store memory
            self.user_memories[user_id][memory_id] = memory_node
            
            # Add to active memories
            self.active_memories[user_id].append(memory_id)
            
            # Store in vector search if embedding available
            if embedding is not None:
                await self.vector_search_engine.add_vector(
                    memory_id,
                    embedding,
                    {"user_id": user_id, "memory_type": memory_type.value}
                )
            
            # Establish relationships
            if related_memories:
                await self._establish_relationships(user_id, memory_id, related_memories)
            
            # Auto-detect related memories
            await self._detect_related_memories(user_id, memory_node)
            
            # Update clusters
            await self._update_memory_clusters(user_id, memory_node)
            
            # Check memory limits
            await self._enforce_memory_limits(user_id)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "memory.stored",
                tags={"type": memory_type.value, "persistence": persistence.value}
            )
            
            self.logger.debug(f"Memory stored: {memory_id} for user {user_id}")
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            await self.metrics_collector.increment("memory.store_errors")
            raise MemoryError(f"Failed to store memory: {e}")
    
    async def retrieve_memory(
        self,
        user_id: str,
        memory_id: str,
        update_access: bool = True
    ) -> Optional[MemoryNode]:
        """
        Retrieve specific memory by ID
        
        Args:
            user_id: User identifier
            memory_id: Memory identifier
            update_access: Whether to update access statistics
            
        Returns:
            MemoryNode or None if not found
        """
        try:
            memory = self.user_memories.get(user_id, {}).get(memory_id)
            
            if memory:
                if update_access:
                    memory.update_access()
                
                await self.metrics_collector.increment("memory.retrieved")
                return memory
            
            await self.metrics_collector.increment("memory.not_found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving memory {memory_id}: {e}")
            return None
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        min_relevance: float = 0.3,
        include_context: bool = True
    ) -> List[MemorySearchResult]:
        """
        Search memories using semantic similarity
        
        Args:
            user_id: User identifier
            query: Search query
            memory_types: Filter by memory types
            limit: Maximum results to return
            min_relevance: Minimum relevance score
            include_context: Include contextual memories
            
        Returns:
            List of memory search results
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search in vector space
            vector_results = await self.vector_search_engine.search(
                query_embedding,
                limit=limit * 2,  # Get more candidates for filtering
                filters={"user_id": user_id}
            )
            
            results = []
            user_memories = self.user_memories.get(user_id, {})
            
            for vector_result in vector_results:
                memory_id = vector_result["id"]
                similarity_score = vector_result["similarity"]
                
                if memory_id not in user_memories:
                    continue
                
                memory = user_memories[memory_id]
                
                # Filter by memory type if specified
                if memory_types and memory.memory_type not in memory_types:
                    continue
                
                # Check minimum relevance
                if similarity_score < min_relevance:
                    continue
                
                # Calculate comprehensive relevance score
                relevance_score = await self._calculate_relevance_score(
                    memory, query, similarity_score, include_context
                )
                
                # Generate reasoning
                reasoning = await self._generate_search_reasoning(
                    memory, query, similarity_score
                )
                
                result = MemorySearchResult(
                    memory_node=memory,
                    relevance_score=relevance_score,
                    reasoning=reasoning,
                    context_match=include_context
                )
                
                results.append(result)
                
                # Update access
                memory.update_access()
            
            # Sort by relevance score
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            # Limit results
            results = results[:limit]
            
            await self.metrics_collector.increment(
                "memory.searched",
                tags={"result_count": str(len(results))}
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            await self.metrics_collector.increment("memory.search_errors")
            return []
    
    async def get_related_memories(
        self,
        user_id: str,
        memory_id: str,
        relationship_threshold: float = 0.5,
        limit: int = 10
    ) -> List[Tuple[MemoryNode, float]]:
        """
        Get memories related to a specific memory
        
        Args:
            user_id: User identifier
            memory_id: Base memory identifier
            relationship_threshold: Minimum relationship strength
            limit: Maximum results to return
            
        Returns:
            List of (memory, relationship_strength) tuples
        """
        try:
            if user_id not in self.memory_relationships:
                return []
            
            relationships = self.memory_relationships[user_id].get(memory_id, {})
            related = []
            
            user_memories = self.user_memories.get(user_id, {})
            
            for related_id, strength in relationships.items():
                if strength >= relationship_threshold and related_id in user_memories:
                    memory = user_memories[related_id]
                    memory.update_access()
                    related.append((memory, strength))
            
            # Sort by relationship strength
            related.sort(key=lambda x: x[1], reverse=True)
            
            return related[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting related memories: {e}")
            return []
    
    async def get_memory_summary(
        self,
        user_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive memory summary for user
        
        Args:
            user_id: User identifier
            memory_types: Filter by memory types
            time_range: Filter by time range (start, end)
            
        Returns:
            Dict containing memory summary
        """
        try:
            user_memories = self.user_memories.get(user_id, {})
            
            # Filter memories
            filtered_memories = []
            for memory in user_memories.values():
                # Filter by type
                if memory_types and memory.memory_type not in memory_types:
                    continue
                
                # Filter by time range
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= memory.created_at <= end_time):
                        continue
                
                filtered_memories.append(memory)
            
            # Calculate statistics
            total_memories = len(filtered_memories)
            if total_memories == 0:
                return {"user_id": user_id, "total_memories": 0}
            
            # Memory type distribution
            type_distribution = defaultdict(int)
            for memory in filtered_memories:
                type_distribution[memory.memory_type.value] += 1
            
            # Persistence distribution
            persistence_distribution = defaultdict(int)
            for memory in filtered_memories:
                persistence_distribution[memory.persistence.value] += 1
            
            # Access statistics
            total_accesses = sum(m.access_count for m in filtered_memories)
            avg_accesses = total_accesses / total_memories if total_memories > 0 else 0
            
            # Importance statistics
            importance_scores = [m.importance_score for m in filtered_memories]
            avg_importance = sum(importance_scores) / len(importance_scores)
            
            # Recent activity
            recent_memories = [
                m for m in filtered_memories
                if (datetime.utcnow() - m.last_accessed).days <= 7
            ]
            
            # Most accessed memories
            most_accessed = sorted(
                filtered_memories,
                key=lambda m: m.access_count,
                reverse=True
            )[:10]
            
            # Memory clusters
            user_clusters = self.memory_clusters.get(user_id, [])
            cluster_info = {
                "total_clusters": len(user_clusters),
                "largest_cluster_size": max([len(c.memories) for c in user_clusters], default=0),
                "avg_cluster_size": sum([len(c.memories) for c in user_clusters]) / len(user_clusters) if user_clusters else 0
            }
            
            return {
                "user_id": user_id,
                "total_memories": total_memories,
                "type_distribution": dict(type_distribution),
                "persistence_distribution": dict(persistence_distribution),
                "access_statistics": {
                    "total_accesses": total_accesses,
                    "average_accesses": avg_accesses,
                    "recent_activity": len(recent_memories)
                },
                "importance_statistics": {
                    "average_importance": avg_importance,
                    "high_importance_count": sum(1 for s in importance_scores if s > 0.7),
                    "low_importance_count": sum(1 for s in importance_scores if s < 0.3)
                },
                "most_accessed_memories": [
                    {
                        "memory_id": m.memory_id,
                        "access_count": m.access_count,
                        "memory_type": m.memory_type.value,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in most_accessed
                ],
                "clustering_info": cluster_info,
                "relationship_count": len(self.memory_relationships.get(user_id, {}))
            }
            
        except Exception as e:
            self.logger.error(f"Error generating memory summary: {e}")
            return {"error": str(e)}
    
    async def delete_memory(
        self,
        user_id: str,
        memory_id: str
    ) -> bool:
        """
        Delete specific memory
        
        Args:
            user_id: User identifier
            memory_id: Memory identifier
            
        Returns:
            bool: Success status
        """
        try:
            # Remove from user memories
            if user_id in self.user_memories and memory_id in self.user_memories[user_id]:
                del self.user_memories[user_id][memory_id]
            
            # Remove from vector search
            await self.vector_search_engine.delete_vector(memory_id)
            
            # Remove relationships
            if user_id in self.memory_relationships:
                # Remove as source
                if memory_id in self.memory_relationships[user_id]:
                    del self.memory_relationships[user_id][memory_id]
                
                # Remove as target
                for source_id in self.memory_relationships[user_id]:
                    if memory_id in self.memory_relationships[user_id][source_id]:
                        del self.memory_relationships[user_id][source_id][memory_id]
            
            # Remove from active memories
            if memory_id in self.active_memories[user_id]:
                active_list = list(self.active_memories[user_id])
                active_list.remove(memory_id)
                self.active_memories[user_id] = deque(active_list, maxlen=100)
            
            # Update clusters
            await self._remove_from_clusters(user_id, memory_id)
            
            await self.metrics_collector.increment("memory.deleted")
            
            self.logger.debug(f"Memory deleted: {memory_id} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    async def cleanup_expired_memories(self, user_id: Optional[str] = None):
        """
        Clean up expired memories
        
        Args:
            user_id: Specific user ID or None for all users
        """
        try:
            users_to_clean = [user_id] if user_id else list(self.user_memories.keys())
            total_cleaned = 0
            
            for uid in users_to_clean:
                if uid not in self.user_memories:
                    continue
                
                expired_memories = []
                for memory_id, memory in self.user_memories[uid].items():
                    if memory.is_expired():
                        expired_memories.append(memory_id)
                
                # Delete expired memories
                for memory_id in expired_memories:
                    await self.delete_memory(uid, memory_id)
                    total_cleaned += 1
            
            if total_cleaned > 0:
                await self.metrics_collector.increment(
                    "memory.expired_cleaned",
                    value=total_cleaned
                )
                self.logger.info(f"Cleaned up {total_cleaned} expired memories")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired memories: {e}")
    
    # Private helper methods
    
    async def _calculate_relevance_score(
        self,
        memory: MemoryNode,
        query: str,
        similarity_score: float,
        include_context: bool
    ) -> float:
        """Calculate comprehensive relevance score"""
        # Base score from semantic similarity
        relevance = similarity_score * 0.4
        
        # Importance factor
        relevance += memory.importance_score * 0.2
        
        # Recency factor
        age_days = (datetime.utcnow() - memory.created_at).days
        recency_factor = max(0, 1 - age_days / 365)  # Decay over a year
        relevance += recency_factor * 0.2
        
        # Access frequency factor
        access_factor = min(memory.access_count / 100, 1.0)
        relevance += access_factor * 0.1
        
        # Context relevance
        if include_context and memory.memory_type in [MemoryType.CONTEXTUAL, MemoryType.EPISODIC]:
            relevance += 0.1
        
        return min(relevance, 1.0)
    
    async def _generate_search_reasoning(
        self,
        memory: MemoryNode,
        query: str,
        similarity_score: float
    ) -> str:
        """Generate reasoning for search result"""
        reasons = []
        
        if similarity_score > 0.8:
            reasons.append("high semantic similarity")
        elif similarity_score > 0.6:
            reasons.append("good semantic similarity")
        else:
            reasons.append("moderate semantic similarity")
        
        if memory.importance_score > 0.7:
            reasons.append("high importance")
        
        if memory.access_count > 10:
            reasons.append("frequently accessed")
        
        age_days = (datetime.utcnow() - memory.created_at).days
        if age_days <= 7:
            reasons.append("recent memory")
        
        if memory.tags:
            # Check if query words match tags
            query_words = set(query.lower().split())
            tag_words = set(tag.lower() for tag in memory.tags)
            if query_words & tag_words:
                reasons.append("matching tags")
        
        return "Relevant due to: " + ", ".join(reasons)
    
    async def _establish_relationships(
        self,
        user_id: str,
        memory_id: str,
        related_memory_ids: List[str]
    ):
        """Establish relationships between memories"""
        for related_id in related_memory_ids:
            if related_id in self.user_memories.get(user_id, {}):
                # Bidirectional relationship with default strength
                self.memory_relationships[user_id][memory_id][related_id] = 0.7
                self.memory_relationships[user_id][related_id][memory_id] = 0.7
    
    async def _detect_related_memories(
        self,
        user_id: str,
        new_memory: MemoryNode
    ):
        """Auto-detect related memories using similarity"""
        if new_memory.embedding is None:
            return
        
        user_memories = self.user_memories.get(user_id, {})
        
        for existing_id, existing_memory in user_memories.items():
            if existing_id == new_memory.memory_id or existing_memory.embedding is None:
                continue
            
            # Calculate similarity
            similarity = np.dot(new_memory.embedding, existing_memory.embedding) / (
                np.linalg.norm(new_memory.embedding) * np.linalg.norm(existing_memory.embedding)
            )
            
            # Establish relationship if similarity is high enough
            if similarity > self.cluster_threshold:
                self.memory_relationships[user_id][new_memory.memory_id][existing_id] = similarity
                self.memory_relationships[user_id][existing_id][new_memory.memory_id] = similarity
    
    async def _update_memory_clusters(
        self,
        user_id: str,
        new_memory: MemoryNode
    ):
        """Update memory clusters with new memory"""
        if new_memory.embedding is None:
            return
        
        user_clusters = self.memory_clusters[user_id]
        best_cluster = None
        best_similarity = 0
        
        # Find best matching cluster
        for cluster in user_clusters:
            if cluster.centroid_embedding is not None:
                similarity = np.dot(new_memory.embedding, cluster.centroid_embedding) / (
                    np.linalg.norm(new_memory.embedding) * np.linalg.norm(cluster.centroid_embedding)
                )
                
                if similarity > best_similarity and similarity > self.cluster_threshold:
                    best_similarity = similarity
                    best_cluster = cluster
        
        if best_cluster:
            # Add to existing cluster
            best_cluster.memories.append(new_memory)
            best_cluster.update_centroid()
        else:
            # Create new cluster
            cluster_id = f"cluster_{user_id}_{len(user_clusters)}"
            new_cluster = MemoryCluster(
                cluster_id=cluster_id,
                memories=[new_memory],
                centroid_embedding=new_memory.embedding.copy(),
                topic="auto_detected",
                coherence_score=1.0,
                last_updated=datetime.utcnow()
            )
            user_clusters.append(new_cluster)
    
    async def _remove_from_clusters(self, user_id: str, memory_id: str):
        """Remove memory from clusters"""
        user_clusters = self.memory_clusters.get(user_id, [])
        
        for cluster in user_clusters:
            cluster.memories = [m for m in cluster.memories if m.memory_id != memory_id]
            
            # Remove empty clusters
            if not cluster.memories:
                user_clusters.remove(cluster)
            else:
                cluster.update_centroid()
    
    async def _enforce_memory_limits(self, user_id: str):
        """Enforce memory limits per user"""
        user_memories = self.user_memories.get(user_id, {})
        
        if len(user_memories) > self.max_memories_per_user:
            # Remove least important memories
            memories_by_importance = sorted(
                user_memories.values(),
                key=lambda m: m.importance_score + (m.access_count / 1000)
            )
            
            memories_to_remove = memories_by_importance[:len(user_memories) - self.max_memories_per_user]
            
            for memory in memories_to_remove:
                await self.delete_memory(user_id, memory.memory_id)
    
    async def _background_maintenance(self):
        """Background task for memory maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up expired memories
                await self.cleanup_expired_memories()
                
                # Update memory importance scores
                await self._update_importance_scores()
                
                # Optimize clusters
                await self._optimize_clusters()
                
                # Save to persistent storage
                await self._save_memories()
                
                await self.metrics_collector.increment("memory.maintenance.runs")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background maintenance error: {e}")
                await asyncio.sleep(300)  # Wait before retrying
    
    async def _update_importance_scores(self):
        """Update importance scores based on access patterns"""
        for user_id, user_memories in self.user_memories.items():
            for memory in user_memories.values():
                # Decay importance over time
                age_factor = max(0, 1 - (datetime.utcnow() - memory.created_at).days / 365)
                access_factor = min(memory.access_count / 100, 1.0)
                
                memory.importance_score = (age_factor * 0.3 + access_factor * 0.7)
    
    async def _optimize_clusters(self):
        """Optimize memory clusters"""
        for user_id, clusters in self.memory_clusters.items():
            # Merge similar clusters
            merged_clusters = []
            
            for i, cluster1 in enumerate(clusters):
                merged = False
                
                for cluster2 in merged_clusters:
                    if cluster1.centroid_embedding is not None and cluster2.centroid_embedding is not None:
                        similarity = np.dot(cluster1.centroid_embedding, cluster2.centroid_embedding) / (
                            np.linalg.norm(cluster1.centroid_embedding) * np.linalg.norm(cluster2.centroid_embedding)
                        )
                        
                        if similarity > 0.9:  # Very similar clusters
                            # Merge clusters
                            cluster2.memories.extend(cluster1.memories)
                            cluster2.update_centroid()
                            merged = True
                            break
                
                if not merged:
                    merged_clusters.append(cluster1)
            
            self.memory_clusters[user_id] = merged_clusters
    
    async def _load_memories(self):
        """Load memories from persistent storage"""
        try:
            # Load from cache or database
            memories_data = await self.cache_manager.get("user_memories")
            if memories_data:
                for user_id, user_data in memories_data.items():
                    for memory_id, memory_data in user_data.items():
                        memory_node = self._memory_from_dict(memory_data)
                        self.user_memories[user_id][memory_id] = memory_node
                        
                        # Restore to vector search
                        if memory_node.embedding is not None:
                            await self.vector_search_engine.add_vector(
                                memory_id,
                                memory_node.embedding,
                                {"user_id": user_id, "memory_type": memory_node.memory_type.value}
                            )
                            
        except Exception as e:
            self.logger.error(f"Error loading memories: {e}")
    
    async def _save_memories(self):
        """Save memories to persistent storage"""
        try:
            memories_data = {}
            for user_id, user_memories in self.user_memories.items():
                memories_data[user_id] = {}
                for memory_id, memory in user_memories.items():
                    # Only save important memories to reduce storage
                    if memory.importance_score > 0.3 or memory.persistence in [
                        MemoryPersistence.LONG_TERM, MemoryPersistence.PERMANENT
                    ]:
                        memory_dict = memory.to_dict()
                        # Don't serialize embedding (stored in vector search)
                        memory_dict.pop('embedding', None)
                        memories_data[user_id][memory_id] = memory_dict
            
            await self.cache_manager.set(
                "user_memories",
                memories_data,
                ttl=86400 * 30  # 30 days
            )
            
        except Exception as e:
            self.logger.error(f"Error saving memories: {e}")
    
    def _memory_from_dict(self, data: Dict[str, Any]) -> MemoryNode:
        """Reconstruct memory node from dictionary"""
        memory = MemoryNode(
            memory_id=data["memory_id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            persistence=MemoryPersistence(data["persistence"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data.get("access_count", 0),
            importance_score=data.get("importance_score", 0.5),
            confidence=data.get("confidence", 1.0),
            tags=set(data.get("tags", [])),
            relationships=data.get("relationships", {}),
            metadata=data.get("metadata", {})
        )
        
        return memory
