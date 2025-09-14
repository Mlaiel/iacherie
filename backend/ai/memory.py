"""
Context and Conversation Memory Module
====================================

Consolidated memory management functionality from conversational/conversation_memory/ and 
context_tracking/ directories. Provides comprehensive context management and memory systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Memory storage types"""
    SHORT_TERM = "short_term"  # Current session
    LONG_TERM = "long_term"    # Persistent across sessions
    EPISODIC = "episodic"      # Specific events and experiences
    SEMANTIC = "semantic"      # Facts and knowledge
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"        # Active processing memory

class ContextScope(Enum):
    """Context scope levels"""
    SESSION = "session"        # Single conversation session
    USER = "user"             # User-specific context
    PLATFORM = "platform"    # Platform-specific context
    GLOBAL = "global"         # Application-wide context
    BUSINESS = "business"     # Business logic context
    TEMPORAL = "temporal"     # Time-based context

class MemoryPriority(Enum):
    """Memory priority levels"""
    CRITICAL = "critical"     # Must retain
    HIGH = "high"            # Important to retain
    MEDIUM = "medium"        # Useful to retain
    LOW = "low"              # Can be discarded if needed
    TEMPORARY = "temporary"   # Short-lived memory

@dataclass
class MemoryEntry:
    """Individual memory entry"""
    id: str
    content: Any
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: datetime
    context_scope: ContextScope
    metadata: Dict[str, Any] = None
    expiry: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class ConversationContext:
    """Conversation context structure"""
    conversation_id: str
    user_id: str
    session_id: str
    platform: Optional[str] = None
    current_topic: Optional[str] = None
    intent_history: List[str] = None
    entity_cache: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    state_variables: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class UserContext:
    """User-specific context"""
    user_id: str
    profile: Dict[str, Any]
    preferences: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    behavioral_patterns: Dict[str, Any]
    content_interests: List[str]
    collaboration_history: List[str]
    monetization_data: Dict[str, Any]
    protection_settings: Dict[str, Any]
    last_updated: datetime

class MemoryManager(ABC):
    """Abstract base class for memory management"""
    
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry"""
        pass
    
    @abstractmethod
    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory entry by ID"""
        pass
    
    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        """Search memory entries"""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry"""
        pass

class InMemoryStorage(MemoryManager):
    """In-memory storage implementation"""
    
    def __init__(self) -> None:
        self.storage: Dict[str, MemoryEntry] = {}
        self.indices: Dict[str, Dict[str, List[str]]] = {
            "type": {},
            "scope": {},
            "priority": {},
            "user": {}
        }
    
    async def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry in memory"""
        try:
            self.storage[entry.id] = entry
            
            # Update indices
            self._update_index("type", entry.memory_type.value, entry.id)
            self._update_index("scope", entry.context_scope.value, entry.id)
            self._update_index("priority", entry.priority.value, entry.id)
            
            # Extract user_id from metadata if available
            if entry.metadata and "user_id" in entry.metadata:
                self._update_index("user", entry.metadata["user_id"], entry.id)
            
            return True
        except Exception as e:
            logger.error(f"Error storing memory entry: {e}")
            return False
    
    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory entry by ID"""
        entry = self.storage.get(memory_id)
        if entry:
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.now()
        return entry
    
    async def search(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        """Search memory entries"""
        results = []
        
        for entry in self.storage.values():
            if self._matches_query(entry, query):
                results.append(entry)
        
        # Sort by relevance (timestamp and access count)
        results.sort(key=lambda x: (x.timestamp, x.access_count), reverse=True)
        return results
    
    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry"""
        if memory_id in self.storage:
            entry = self.storage[memory_id]
            del self.storage[memory_id]
            
            # Remove from indices
            self._remove_from_index("type", entry.memory_type.value, memory_id)
            self._remove_from_index("scope", entry.context_scope.value, memory_id)
            self._remove_from_index("priority", entry.priority.value, memory_id)
            
            if entry.metadata and "user_id" in entry.metadata:
                self._remove_from_index("user", entry.metadata["user_id"], memory_id)
            
            return True
        return False
    
    def _update_index(self, index_type -> None: str, key -> None: str, memory_id -> None: str) -> None:
        """Update index"""
        if key not in self.indices[index_type]:
            self.indices[index_type][key] = []
        if memory_id not in self.indices[index_type][key]:
            self.indices[index_type][key].append(memory_id)
    
    def _remove_from_index(self, index_type -> None: str, key -> None: str, memory_id -> None: str) -> None:
        """Remove from index"""
        if key in self.indices[index_type] and memory_id in self.indices[index_type][key]:
            self.indices[index_type][key].remove(memory_id)
    
    def _matches_query(self, entry: MemoryEntry, query: Dict[str, Any]) -> bool:
        """Check if entry matches query"""
        for key, value in query.items():
            if key == "memory_type" and entry.memory_type.value != value:
                return False
            elif key == "context_scope" and entry.context_scope.value != value:
                return False
            elif key == "priority" and entry.priority.value != value:
                return False
            elif key == "user_id" and (not entry.metadata or entry.metadata.get("user_id") != value):
                return False
            elif key == "after_timestamp" and entry.timestamp < value:
                return False
            elif key == "before_timestamp" and entry.timestamp > value:
                return False
        return True

class ConversationMemoryManager:
    """Manages conversation-specific memory"""
    
    def __init__(self, storage -> None: MemoryManager) -> None:
        self.storage = storage
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.memory_cleanup_interval = timedelta(hours=24)
    
    async def start_conversation(self, conversation_id: str, user_id: str, session_id: str, 
                               platform: Optional[str] = None) -> ConversationContext:
        """Start new conversation and initialize context"""
        context = ConversationContext(
            conversation_id=conversation_id,
            user_id=user_id,
            session_id=session_id,
            platform=platform,
            intent_history=[],
            entity_cache={},
            preferences={},
            state_variables={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.active_conversations[conversation_id] = context
        
        # Store conversation start in memory
        memory_entry = MemoryEntry(
            id=f"conv_start_{conversation_id}",
            content={"action": "conversation_started", "context": asdict(context)},
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.MEDIUM,
            timestamp=datetime.now(),
            context_scope=ContextScope.SESSION,
            metadata={"user_id": user_id, "conversation_id": conversation_id}
        )
        
        await self.storage.store(memory_entry)
        return context
    
    async def update_conversation_context(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update conversation context"""
        if conversation_id not in self.active_conversations:
            return False
        
        context = self.active_conversations[conversation_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        context.updated_at = datetime.now()
        
        # Store update in memory
        memory_entry = MemoryEntry(
            id=f"conv_update_{conversation_id}_{datetime.now().timestamp()}",
            content={"action": "context_updated", "updates": updates},
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.LOW,
            timestamp=datetime.now(),
            context_scope=ContextScope.SESSION,
            metadata={"user_id": context.user_id, "conversation_id": conversation_id}
        )
        
        await self.storage.store(memory_entry)
        return True
    
    async def add_message_to_memory(self, conversation_id: str, message: str, 
                                  response: str, metadata: Dict[str, Any] = None) -> bool:
        """Add message exchange to memory"""
        if conversation_id not in self.active_conversations:
            return False
        
        context = self.active_conversations[conversation_id]
        
        memory_entry = MemoryEntry(
            id=f"msg_{conversation_id}_{datetime.now().timestamp()}",
            content={
                "message": message,
                "response": response,
                "metadata": metadata or {}
            },
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.MEDIUM,
            timestamp=datetime.now(),
            context_scope=ContextScope.SESSION,
            metadata={"user_id": context.user_id, "conversation_id": conversation_id}
        )
        
        await self.storage.store(memory_entry)
        return True
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        query = {
            "conversation_id": conversation_id,
            "memory_type": MemoryType.EPISODIC.value
        }
        
        entries = await self.storage.search(query)
        
        # Extract message content
        history = []
        for entry in entries[:limit]:
            if "message" in entry.content:
                history.append({
                    "timestamp": entry.timestamp,
                    "message": entry.content["message"],
                    "response": entry.content["response"],
                    "metadata": entry.content.get("metadata", {})
                })
        
        return sorted(history, key=lambda x: x["timestamp"])
    
    async def end_conversation(self, conversation_id: str) -> bool:
        """End conversation and store summary"""
        if conversation_id not in self.active_conversations:
            return False
        
        context = self.active_conversations[conversation_id]
        
        # Create conversation summary
        summary = {
            "conversation_id": conversation_id,
            "duration": (datetime.now() - context.created_at).total_seconds(),
            "final_topic": context.current_topic,
            "intent_history": context.intent_history,
            "message_count": len(context.intent_history)
        }
        
        # Store conversation end in memory
        memory_entry = MemoryEntry(
            id=f"conv_end_{conversation_id}",
            content={"action": "conversation_ended", "summary": summary},
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.HIGH,
            timestamp=datetime.now(),
            context_scope=ContextScope.USER,
            metadata={"user_id": context.user_id, "conversation_id": conversation_id}
        )
        
        await self.storage.store(memory_entry)
        
        # Remove from active conversations
        del self.active_conversations[conversation_id]
        return True

class ContextTracker:
    """Tracks and manages various context types"""
    
    def __init__(self, storage -> None: MemoryManager) -> None:
        self.storage = storage
        self.user_contexts: Dict[str, UserContext] = {}
        self.platform_contexts: Dict[str, Dict[str, Any]] = {}
        self.business_contexts: Dict[str, Dict[str, Any]] = {}
    
    async def track_user_context(self, user_id: str, interaction_data: Dict[str, Any]) -> UserContext:
        """Track and update user context"""
        if user_id not in self.user_contexts:
            # Initialize new user context
            self.user_contexts[user_id] = UserContext(
                user_id=user_id,
                profile={},
                preferences={},
                interaction_history=[],
                behavioral_patterns={},
                content_interests=[],
                collaboration_history=[],
                monetization_data={},
                protection_settings={},
                last_updated=datetime.now()
            )
        
        context = self.user_contexts[user_id]
        
        # Update interaction history
        context.interaction_history.append({
            "timestamp": datetime.now(),
            "data": interaction_data
        })
        
        # Limit history size
        if len(context.interaction_history) > 1000:
            context.interaction_history = context.interaction_history[-1000:]
        
        context.last_updated = datetime.now()
        
        # Store context update in memory
        memory_entry = MemoryEntry(
            id=f"user_context_{user_id}_{datetime.now().timestamp()}",
            content={"action": "user_context_updated", "interaction": interaction_data},
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.MEDIUM,
            timestamp=datetime.now(),
            context_scope=ContextScope.USER,
            metadata={"user_id": user_id}
        )
        
        await self.storage.store(memory_entry)
        return context
    
    async def track_platform_context(self, platform: str, context_data: Dict[str, Any]) -> bool:
        """Track platform-specific context"""
        if platform not in self.platform_contexts:
            self.platform_contexts[platform] = {}
        
        self.platform_contexts[platform].update(context_data)
        self.platform_contexts[platform]["last_updated"] = datetime.now()
        
        # Store platform context in memory
        memory_entry = MemoryEntry(
            id=f"platform_context_{platform}_{datetime.now().timestamp()}",
            content={"platform": platform, "context": context_data},
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.LOW,
            timestamp=datetime.now(),
            context_scope=ContextScope.PLATFORM,
            metadata={"platform": platform}
        )
        
        await self.storage.store(memory_entry)
        return True
    
    async def track_business_context(self, context_type: str, context_data: Dict[str, Any]) -> bool:
        """Track business logic context"""
        if context_type not in self.business_contexts:
            self.business_contexts[context_type] = {}
        
        self.business_contexts[context_type].update(context_data)
        self.business_contexts[context_type]["last_updated"] = datetime.now()
        
        # Store business context in memory
        memory_entry = MemoryEntry(
            id=f"business_context_{context_type}_{datetime.now().timestamp()}",
            content={"context_type": context_type, "context": context_data},
            memory_type=MemoryType.PROCEDURAL,
            priority=MemoryPriority.HIGH,
            timestamp=datetime.now(),
            context_scope=ContextScope.BUSINESS,
            metadata={"context_type": context_type}
        )
        
        await self.storage.store(memory_entry)
        return True
    
    async def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """Get user context"""
        return self.user_contexts.get(user_id)
    
    async def get_platform_context(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get platform context"""
        return self.platform_contexts.get(platform)
    
    async def get_business_context(self, context_type: str) -> Optional[Dict[str, Any]]:
        """Get business context"""
        return self.business_contexts.get(context_type)

class MemoryCleanupManager:
    """Manages memory cleanup and optimization"""
    
    def __init__(self, storage -> None: MemoryManager) -> None:
        self.storage = storage
        self.cleanup_rules = {
            MemoryType.TEMPORARY: timedelta(hours=1),
            MemoryType.SHORT_TERM: timedelta(days=1),
            MemoryType.WORKING: timedelta(hours=6),
            MemoryType.EPISODIC: timedelta(days=30),
            MemoryType.SEMANTIC: timedelta(days=90),
            MemoryType.LONG_TERM: None  # Never cleanup
        }
    
    async def cleanup_expired_memories(self) -> int:
        """Cleanup expired memories"""
        cleanup_count = 0
        current_time = datetime.now()
        
        for memory_type, expiry_delta in self.cleanup_rules.items():
            if expiry_delta is None:
                continue  # Skip memories that never expire
            
            cutoff_time = current_time - expiry_delta
            
            # Find expired memories
            query = {
                "memory_type": memory_type.value,
                "before_timestamp": cutoff_time
            }
            
            expired_entries = await self.storage.search(query)
            
            # Delete expired memories
            for entry in expired_entries:
                if await self.storage.delete(entry.id):
                    cleanup_count += 1
        
        logger.info(f"Cleaned up {cleanup_count} expired memories")
        return cleanup_count
    
    async def optimize_memory_usage(self) -> Dict[str, int]:
        """Optimize memory usage by cleaning low-priority items"""
        stats = {"removed": 0, "kept": 0}
        
        # Get all low-priority memories
        query = {"priority": MemoryPriority.LOW.value}
        low_priority_entries = await self.storage.search(query)
        
        # Remove oldest low-priority memories if too many
        if len(low_priority_entries) > 1000:
            oldest_entries = sorted(low_priority_entries, key=lambda x: x.timestamp)
            entries_to_remove = oldest_entries[:-500]  # Keep newest 500
            
            for entry in entries_to_remove:
                if await self.storage.delete(entry.id):
                    stats["removed"] += 1
        
        stats["kept"] = len(low_priority_entries) - stats["removed"]
        return stats

# Factory functions
def create_in_memory_storage() -> InMemoryStorage:
    """Create in-memory storage instance"""
    return InMemoryStorage()

def create_conversation_memory_manager(storage: Optional[MemoryManager] = None) -> ConversationMemoryManager:
    """Create conversation memory manager"""
    if storage is None:
        storage = create_in_memory_storage()
    return ConversationMemoryManager(storage)

def create_context_tracker(storage: Optional[MemoryManager] = None) -> ContextTracker:
    """Create context tracker"""
    if storage is None:
        storage = create_in_memory_storage()
    return ContextTracker(storage)

def create_memory_cleanup_manager(storage: Optional[MemoryManager] = None) -> MemoryCleanupManager:
    """Create memory cleanup manager"""
    if storage is None:
        storage = create_in_memory_storage()
    return MemoryCleanupManager(storage)

# Export all classes and functions
__all__ = [
    # Core classes
    "MemoryManager",
    "InMemoryStorage",
    "ConversationMemoryManager",
    "ContextTracker", 
    "MemoryCleanupManager",
    
    # Data structures
    "MemoryEntry",
    "ConversationContext",
    "UserContext",
    "MemoryType",
    "ContextScope",
    "MemoryPriority",
    
    # Factory functions
    "create_in_memory_storage",
    "create_conversation_memory_manager",
    "create_context_tracker",
    "create_memory_cleanup_manager"
]