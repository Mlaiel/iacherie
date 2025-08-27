"""
AI Agents Memory System

Advanced memory management system for AI agents to store, retrieve, and process information.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
import time
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryImportance(Enum):
    """Memory importance levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


@dataclass
class MemoryItem:
    """A single memory item."""
    id: str
    content: Any
    memory_type: MemoryType
    importance: MemoryImportance
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None
    confidence: float = 1.0


@dataclass
class MemoryQuery:
    """Query for memory retrieval."""
    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    importance_min: Optional[MemoryImportance] = None
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    max_age: Optional[timedelta] = None
    limit: int = 10


class MemoryManager:
    """Advanced memory management system for AI agents."""
    
    def __init__(self, 
                 max_short_term: int = 100,
                 max_working: int = 50,
                 max_long_term: int = 10000,
                 decay_factor: float = 0.95):
        """Initialize the memory manager."""
        self.max_short_term = max_short_term
        self.max_working = max_working
        self.max_long_term = max_long_term
        self.decay_factor = decay_factor
        
        # Memory storage
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[MemoryType, List[str]] = {
            memory_type: [] for memory_type in MemoryType
        }
        self.tag_index: Dict[str, List[str]] = {}
        
        logger.info("Memory manager initialized")
    
    def store_memory(self, 
                    content: Any,
                    memory_type: MemoryType = MemoryType.SHORT_TERM,
                    importance: MemoryImportance = MemoryImportance.MEDIUM,
                    tags: List[str] = None,
                    context: Dict[str, Any] = None,
                    expiry: Optional[datetime] = None) -> str:
        """Store a new memory item."""
        try:
            # Generate unique ID
            content_str = json.dumps(content, sort_keys=True, default=str)
            memory_id = hashlib.md5(f"{content_str}{time.time()}".encode()).hexdigest()
            
            # Create memory item
            memory_item = MemoryItem(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                tags=tags or [],
                context=context or {},
                expiry=expiry
            )
            
            # Store memory
            self.memories[memory_id] = memory_item
            self.memory_index[memory_type].append(memory_id)
            
            # Update tag index
            for tag in memory_item.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(memory_id)
            
            # Clean up if necessary
            self._cleanup_memory(memory_type)
            
            logger.info(f"Stored memory {memory_id} of type {memory_type.value}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return ""
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory by ID."""
        try:
            if memory_id in self.memories:
                memory_item = self.memories[memory_id]
                
                # Update access statistics
                memory_item.last_accessed = datetime.now()
                memory_item.access_count += 1
                
                logger.info(f"Retrieved memory {memory_id}")
                return memory_item
            
            logger.warning(f"Memory {memory_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory {memory_id}: {e}")
            return None
    
    def search_memories(self, query: MemoryQuery) -> List[MemoryItem]:
        """Search for memories matching the query."""
        try:
            matching_memories = []
            
            # Get candidate memory IDs
            candidate_ids = set()
            
            if query.memory_type:
                candidate_ids.update(self.memory_index[query.memory_type])
            else:
                for memory_ids in self.memory_index.values():
                    candidate_ids.update(memory_ids)
            
            if query.tags:
                tag_candidates = set()
                for tag in query.tags:
                    if tag in self.tag_index:
                        tag_candidates.update(self.tag_index[tag])
                candidate_ids = candidate_ids.intersection(tag_candidates) if candidate_ids else tag_candidates
            
            # Filter candidates
            for memory_id in candidate_ids:
                memory_item = self.memories.get(memory_id)
                if not memory_item:
                    continue
                
                # Check expiry
                if memory_item.expiry and datetime.now() > memory_item.expiry:
                    continue
                
                # Check importance
                if query.importance_min and memory_item.importance.value < query.importance_min.value:
                    continue
                
                # Check age
                if query.max_age:
                    age = datetime.now() - memory_item.created_at
                    if age > query.max_age:
                        continue
                
                # Check content match (simple text matching)
                if query.content:
                    content_str = str(memory_item.content).lower()
                    if query.content.lower() not in content_str:
                        continue
                
                # Check context match
                if query.context:
                    context_match = True
                    for key, value in query.context.items():
                        if key not in memory_item.context or memory_item.context[key] != value:
                            context_match = False
                            break
                    if not context_match:
                        continue
                
                matching_memories.append(memory_item)
            
            # Sort by importance and recency
            matching_memories.sort(
                key=lambda m: (m.importance.value, m.last_accessed),
                reverse=True
            )
            
            # Limit results
            matching_memories = matching_memories[:query.limit]
            
            logger.info(f"Found {len(matching_memories)} matching memories")
            return matching_memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def update_memory(self, 
                     memory_id: str,
                     content: Optional[Any] = None,
                     importance: Optional[MemoryImportance] = None,
                     tags: Optional[List[str]] = None,
                     context: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing memory item."""
        try:
            if memory_id not in self.memories:
                logger.warning(f"Memory {memory_id} not found for update")
                return False
            
            memory_item = self.memories[memory_id]
            
            # Update content
            if content is not None:
                memory_item.content = content
            
            # Update importance
            if importance is not None:
                memory_item.importance = importance
            
            # Update tags
            if tags is not None:
                # Remove from old tag index
                for old_tag in memory_item.tags:
                    if old_tag in self.tag_index:
                        self.tag_index[old_tag].remove(memory_id)
                
                # Add to new tag index
                memory_item.tags = tags
                for new_tag in tags:
                    if new_tag not in self.tag_index:
                        self.tag_index[new_tag] = []
                    self.tag_index[new_tag].append(memory_id)
            
            # Update context
            if context is not None:
                memory_item.context.update(context)
            
            memory_item.last_accessed = datetime.now()
            
            logger.info(f"Updated memory {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item."""
        try:
            if memory_id not in self.memories:
                logger.warning(f"Memory {memory_id} not found for deletion")
                return False
            
            memory_item = self.memories[memory_id]
            
            # Remove from memory index
            self.memory_index[memory_item.memory_type].remove(memory_id)
            
            # Remove from tag index
            for tag in memory_item.tags:
                if tag in self.tag_index:
                    self.tag_index[tag].remove(memory_id)
                    if not self.tag_index[tag]:
                        del self.tag_index[tag]
            
            # Remove memory
            del self.memories[memory_id]
            
            logger.info(f"Deleted memory {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def _cleanup_memory(self, memory_type: MemoryType):
        """Clean up memory based on type limits."""
        try:
            memory_ids = self.memory_index[memory_type]
            
            # Check limits
            max_items = {
                MemoryType.SHORT_TERM: self.max_short_term,
                MemoryType.WORKING: self.max_working,
                MemoryType.LONG_TERM: self.max_long_term,
                MemoryType.EPISODIC: self.max_long_term,
                MemoryType.SEMANTIC: self.max_long_term,
                MemoryType.PROCEDURAL: self.max_long_term
            }.get(memory_type, 1000)
            
            if len(memory_ids) <= max_items:
                return
            
            # Sort by importance and access patterns
            memories_to_sort = []
            for memory_id in memory_ids:
                memory_item = self.memories.get(memory_id)
                if memory_item:
                    # Calculate retention score
                    age_factor = (datetime.now() - memory_item.last_accessed).total_seconds() / 86400  # Days
                    access_factor = memory_item.access_count
                    importance_factor = memory_item.importance.value
                    
                    retention_score = (importance_factor * 2 + access_factor) / (1 + age_factor * 0.1)
                    memories_to_sort.append((retention_score, memory_id))
            
            # Sort by retention score (lowest first for removal)
            memories_to_sort.sort()
            
            # Remove excess memories
            excess_count = len(memory_ids) - max_items
            for i in range(excess_count):
                _, memory_id_to_remove = memories_to_sort[i]
                self.delete_memory(memory_id_to_remove)
            
            logger.info(f"Cleaned up {excess_count} {memory_type.value} memories")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {memory_type.value} memory: {e}")
    
    def consolidate_memories(self):
        """Consolidate short-term memories into long-term storage."""
        try:
            short_term_ids = self.memory_index[MemoryType.SHORT_TERM].copy()
            consolidated_count = 0
            
            for memory_id in short_term_ids:
                memory_item = self.memories.get(memory_id)
                if not memory_item:
                    continue
                
                # Check consolidation criteria
                age = datetime.now() - memory_item.created_at
                
                if (memory_item.access_count > 3 or 
                    memory_item.importance.value >= MemoryImportance.HIGH.value or
                    age > timedelta(hours=24)):
                    
                    # Move to long-term memory
                    self.memory_index[MemoryType.SHORT_TERM].remove(memory_id)
                    memory_item.memory_type = MemoryType.LONG_TERM
                    self.memory_index[MemoryType.LONG_TERM].append(memory_id)
                    
                    # Apply decay to importance if it's old and rarely accessed
                    if age > timedelta(days=7) and memory_item.access_count < 2:
                        new_importance_value = max(1, int(memory_item.importance.value * self.decay_factor))
                        memory_item.importance = MemoryImportance(new_importance_value)
                    
                    consolidated_count += 1
            
            logger.info(f"Consolidated {consolidated_count} memories to long-term storage")
            
        except Exception as e:
            logger.error(f"Failed to consolidate memories: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            stats = {
                'total_memories': len(self.memories),
                'by_type': {},
                'by_importance': {},
                'total_tags': len(self.tag_index),
                'most_accessed': [],
                'recent_memories': []
            }
            
            # Count by type
            for memory_type in MemoryType:
                stats['by_type'][memory_type.value] = len(self.memory_index[memory_type])
            
            # Count by importance
            for importance in MemoryImportance:
                stats['by_importance'][importance.name] = 0
            
            # Most accessed memories
            all_memories = list(self.memories.values())
            all_memories.sort(key=lambda m: m.access_count, reverse=True)
            stats['most_accessed'] = [
                {'id': m.id, 'access_count': m.access_count, 'content_preview': str(m.content)[:50]}
                for m in all_memories[:5]
            ]
            
            # Recent memories
            all_memories.sort(key=lambda m: m.created_at, reverse=True)
            stats['recent_memories'] = [
                {'id': m.id, 'created_at': m.created_at.isoformat(), 'type': m.memory_type.value}
                for m in all_memories[:5]
            ]
            
            # Count by importance
            for memory in self.memories.values():
                stats['by_importance'][memory.importance.name] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    def clear_expired_memories(self):
        """Clear all expired memories."""
        try:
            current_time = datetime.now()
            expired_ids = []
            
            for memory_id, memory_item in self.memories.items():
                if memory_item.expiry and current_time > memory_item.expiry:
                    expired_ids.append(memory_id)
            
            for memory_id in expired_ids:
                self.delete_memory(memory_id)
            
            logger.info(f"Cleared {len(expired_ids)} expired memories")
            
        except Exception as e:
            logger.error(f"Failed to clear expired memories: {e}")


class WorkingMemory:
    """Working memory for active processing."""
    
    def __init__(self, capacity: int = 7):
        """Initialize working memory with limited capacity."""
        self.capacity = capacity
        self.items: List[MemoryItem] = []
        self.memory_manager = MemoryManager()
        
        logger.info(f"Working memory initialized with capacity {capacity}")
    
    def add_item(self, content: Any, importance: MemoryImportance = MemoryImportance.HIGH) -> str:
        """Add item to working memory."""
        # Store in memory manager first
        memory_id = self.memory_manager.store_memory(
            content=content,
            memory_type=MemoryType.WORKING,
            importance=importance
        )
        
        memory_item = self.memory_manager.retrieve_memory(memory_id)
        if memory_item:
            self.items.append(memory_item)
            
            # Remove oldest if over capacity
            if len(self.items) > self.capacity:
                oldest_item = self.items.pop(0)
                # Move to short-term memory
                self.memory_manager.update_memory(
                    oldest_item.id,
                    importance=MemoryImportance.MEDIUM
                )
        
        return memory_id
    
    def get_current_context(self) -> List[Any]:
        """Get current working memory context."""
        return [item.content for item in self.items]
    
    def clear(self):
        """Clear working memory."""
        self.items.clear()
        logger.info("Working memory cleared")


# Module initialization
logger.info("AI agents memory system module loaded successfully")
