"""
Conversation Context Manager - IA Influencer Agent

Enterprise-grade conversation context management orchestrating all conversational
intelligence components for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, deque

from ...core.exceptions import ContextManagerError, ValidationError
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...data.models import User, Conversation, ContentItem
from ...utils.validation import validate_required_fields
from ...utils.cache import CacheManager


class ContextPriority(Enum):
    """Context priority levels for intelligent management"""
    CRITICAL = "critical"        # User identity, security context
    HIGH = "high"               # Content protection, business data
    MEDIUM = "medium"           # Collaboration preferences, platform settings
    LOW = "low"                 # UI preferences, display settings
    BACKGROUND = "background"   # Analytics, logging data


class ContextScope(Enum):
    """Context scope definitions"""
    GLOBAL = "global"           # Cross-session persistent
    SESSION = "session"         # Session-specific
    CONVERSATION = "conversation"  # Conversation-specific
    INTERACTION = "interaction"    # Single interaction
    TEMPORARY = "temporary"     # Short-lived cache


@dataclass
class ContextItem:
    """Individual context item with metadata"""
    key: str
    value: Any
    priority: ContextPriority
    scope: ContextScope
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    source: str = "system"
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if context item has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "key": self.key,
            "value": self.value,
            "priority": self.priority.value,
            "scope": self.scope.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "confidence": self.confidence,
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class ConversationState:
    """Current conversation state tracking"""
    conversation_id: str
    user_id: str
    session_id: str
    current_intent: Optional[str] = None
    conversation_mode: str = "general"
    active_topics: List[str] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)
    context_stack: List[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    engagement_level: float = 0.5
    last_activity: datetime = field(default_factory=datetime.utcnow)
    platform: Optional[str] = None
    content_type_focus: Optional[str] = None
    collaboration_mode: bool = False
    protection_active: bool = True


class ConversationContextManager:
    """
    Enterprise conversation context manager orchestrating intelligent 
    conversation flow and context awareness for content creators.
    
    Manages multi-level context hierarchy, intelligent caching,
    security-aware context handling, and business logic integration.
    """
    
    def __init__(
        self,
        cache_manager: CacheManager,
        security_manager: SecurityManager,
        metrics_collector: MetricsCollector,
        max_context_items: int = 10000,
        cleanup_interval: int = 3600
    ):
        self.cache_manager = cache_manager
        self.security_manager = security_manager
        self.metrics_collector = metrics_collector
        self.max_context_items = max_context_items
        self.cleanup_interval = cleanup_interval
        
        # Context storage hierarchy
        self.global_context: Dict[str, ContextItem] = {}
        self.session_contexts: Dict[str, Dict[str, ContextItem]] = defaultdict(dict)
        self.conversation_contexts: Dict[str, Dict[str, ContextItem]] = defaultdict(dict)
        self.interaction_contexts: Dict[str, Dict[str, ContextItem]] = defaultdict(dict)
        
        # Conversation state tracking
        self.conversation_states: Dict[str, ConversationState] = {}
        
        # Context access patterns for optimization
        self.access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Background cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ConversationContextManager initialized")
    
    async def start(self):
        """Start the context manager and background tasks"""
        try:
            # Start background cleanup
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            
            # Load persistent global context
            await self._load_global_context()
            
            self.logger.info("ConversationContextManager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start ConversationContextManager: {e}")
            raise ContextManagerError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the context manager and cleanup resources"""
        try:
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Save persistent context
            await self._save_global_context()
            
            # Clear memory
            self.global_context.clear()
            self.session_contexts.clear()
            self.conversation_contexts.clear()
            self.interaction_contexts.clear()
            self.conversation_states.clear()
            
            self.logger.info("ConversationContextManager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping ConversationContextManager: {e}")
    
    async def set_context(
        self,
        key: str,
        value: Any,
        scope: ContextScope,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        priority: ContextPriority = ContextPriority.MEDIUM,
        expires_in: Optional[int] = None,
        source: str = "system",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set context item with intelligent scope management
        
        Args:
            key: Context key identifier
            value: Context value
            scope: Context scope (global, session, conversation, interaction)
            conversation_id: Conversation identifier for conversation/interaction scope
            session_id: Session identifier for session+ scopes
            priority: Context priority level
            expires_in: Expiration time in seconds
            source: Context source identifier
            tags: Context tags for categorization
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            validate_required_fields({"key": key, "value": value, "scope": scope})
            
            # Security validation
            if not await self.security_manager.validate_context_access(key, source):
                raise SecurityError(f"Unauthorized context access: {key}")
            
            # Calculate expiration
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Create context item
            context_item = ContextItem(
                key=key,
                value=value,
                priority=priority,
                scope=scope,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=expires_at,
                source=source,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store in appropriate scope
            stored = await self._store_context_item(
                context_item, conversation_id, session_id
            )
            
            if stored:
                # Update access patterns
                self.access_patterns[key].append(datetime.utcnow())
                
                # Collect metrics
                await self.metrics_collector.increment(
                    "context.items.set",
                    tags={"scope": scope.value, "priority": priority.value}
                )
                
                self.logger.debug(f"Context set: {key} in {scope.value} scope")
            
            return stored
            
        except Exception as e:
            self.logger.error(f"Error setting context {key}: {e}")
            await self.metrics_collector.increment("context.errors.set")
            return False
    
    async def get_context(
        self,
        key: str,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        default: Any = None,
        include_metadata: bool = False
    ) -> Any:
        """
        Get context item with intelligent scope resolution
        
        Args:
            key: Context key identifier
            conversation_id: Conversation identifier
            session_id: Session identifier
            default: Default value if not found
            include_metadata: Include context metadata in response
            
        Returns:
            Context value or default
        """
        try:
            # Search in scope hierarchy (most specific to least specific)
            context_item = await self._find_context_item(
                key, conversation_id, session_id
            )
            
            if not context_item:
                await self.metrics_collector.increment("context.items.miss")
                return default
            
            # Check expiration
            if context_item.is_expired():
                await self._remove_expired_context(key, context_item.scope)
                await self.metrics_collector.increment("context.items.expired")
                return default
            
            # Update access patterns
            self.access_patterns[key].append(datetime.utcnow())
            
            # Collect metrics
            await self.metrics_collector.increment(
                "context.items.hit",
                tags={"scope": context_item.scope.value}
            )
            
            if include_metadata:
                return {
                    "value": context_item.value,
                    "metadata": context_item.to_dict()
                }
            
            return context_item.value
            
        except Exception as e:
            self.logger.error(f"Error getting context {key}: {e}")
            await self.metrics_collector.increment("context.errors.get")
            return default
    
    async def remove_context(
        self,
        key: str,
        scope: Optional[ContextScope] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Remove context item from specified scope or all scopes
        
        Args:
            key: Context key identifier
            scope: Specific scope to remove from (optional)
            conversation_id: Conversation identifier
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        try:
            removed = False
            
            if scope:
                # Remove from specific scope
                removed = await self._remove_from_scope(
                    key, scope, conversation_id, session_id
                )
            else:
                # Remove from all scopes
                for scope_type in ContextScope:
                    if await self._remove_from_scope(
                        key, scope_type, conversation_id, session_id
                    ):
                        removed = True
            
            if removed:
                await self.metrics_collector.increment("context.items.removed")
                self.logger.debug(f"Context removed: {key}")
            
            return removed
            
        except Exception as e:
            self.logger.error(f"Error removing context {key}: {e}")
            await self.metrics_collector.increment("context.errors.remove")
            return False
    
    async def start_conversation(
        self,
        conversation_id: str,
        user_id: str,
        session_id: str,
        platform: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ConversationState:
        """
        Start new conversation with initial context setup
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User identifier
            session_id: Session identifier
            platform: Platform identifier (Instagram, TikTok, etc.)
            initial_context: Initial context data
            
        Returns:
            ConversationState: New conversation state
        """
        try:
            # Create conversation state
            state = ConversationState(
                conversation_id=conversation_id,
                user_id=user_id,
                session_id=session_id,
                platform=platform
            )
            
            self.conversation_states[conversation_id] = state
            
            # Set initial context items
            if initial_context:
                for key, value in initial_context.items():
                    await self.set_context(
                        key=key,
                        value=value,
                        scope=ContextScope.CONVERSATION,
                        conversation_id=conversation_id,
                        session_id=session_id,
                        source="conversation_start"
                    )
            
            # Load user profile context
            await self._load_user_context(user_id, session_id)
            
            await self.metrics_collector.increment(
                "conversations.started",
                tags={"platform": platform or "unknown"}
            )
            
            self.logger.info(f"Conversation started: {conversation_id}")
            return state
            
        except Exception as e:
            self.logger.error(f"Error starting conversation {conversation_id}: {e}")
            raise ContextManagerError(f"Failed to start conversation: {e}")
    
    async def end_conversation(
        self,
        conversation_id: str,
        save_summary: bool = True
    ) -> bool:
        """
        End conversation and cleanup context
        
        Args:
            conversation_id: Conversation identifier
            save_summary: Whether to save conversation summary
            
        Returns:
            bool: Success status
        """
        try:
            if conversation_id not in self.conversation_states:
                return False
            
            state = self.conversation_states[conversation_id]
            
            # Save conversation summary if requested
            if save_summary:
                await self._save_conversation_summary(conversation_id, state)
            
            # Clean up conversation context
            if conversation_id in self.conversation_contexts:
                del self.conversation_contexts[conversation_id]
            
            if conversation_id in self.interaction_contexts:
                del self.interaction_contexts[conversation_id]
            
            # Remove conversation state
            del self.conversation_states[conversation_id]
            
            await self.metrics_collector.increment("conversations.ended")
            
            self.logger.info(f"Conversation ended: {conversation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation_state(
        self,
        conversation_id: str
    ) -> Optional[ConversationState]:
        """Get current conversation state"""
        return self.conversation_states.get(conversation_id)
    
    async def update_conversation_state(
        self,
        conversation_id: str,
        **updates
    ) -> bool:
        """
        Update conversation state attributes
        
        Args:
            conversation_id: Conversation identifier
            **updates: State attributes to update
            
        Returns:
            bool: Success status
        """
        try:
            if conversation_id not in self.conversation_states:
                return False
            
            state = self.conversation_states[conversation_id]
            
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            
            state.last_activity = datetime.utcnow()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating conversation state {conversation_id}: {e}")
            return False
    
    async def get_context_summary(
        self,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        include_scopes: Optional[List[ContextScope]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive context summary for debugging and analytics
        
        Args:
            conversation_id: Conversation identifier
            session_id: Session identifier
            include_scopes: Specific scopes to include
            
        Returns:
            Dict containing context summary
        """
        try:
            scopes = include_scopes or list(ContextScope)
            summary = {
                "global_context_count": len(self.global_context),
                "session_contexts_count": len(self.session_contexts),
                "conversation_contexts_count": len(self.conversation_contexts),
                "interaction_contexts_count": len(self.interaction_contexts),
                "active_conversations": len(self.conversation_states),
                "scopes": {}
            }
            
            for scope in scopes:
                scope_data = await self._get_scope_summary(
                    scope, conversation_id, session_id
                )
                summary["scopes"][scope.value] = scope_data
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating context summary: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _store_context_item(
        self,
        item: ContextItem,
        conversation_id: Optional[str],
        session_id: Optional[str]
    ) -> bool:
        """Store context item in appropriate scope storage"""
        try:
            if item.scope == ContextScope.GLOBAL:
                self.global_context[item.key] = item
                
            elif item.scope == ContextScope.SESSION:
                if not session_id:
                    raise ValidationError("Session ID required for session scope")
                self.session_contexts[session_id][item.key] = item
                
            elif item.scope == ContextScope.CONVERSATION:
                if not conversation_id:
                    raise ValidationError("Conversation ID required for conversation scope")
                self.conversation_contexts[conversation_id][item.key] = item
                
            elif item.scope == ContextScope.INTERACTION:
                if not conversation_id:
                    raise ValidationError("Conversation ID required for interaction scope")
                self.interaction_contexts[conversation_id][item.key] = item
                
            elif item.scope == ContextScope.TEMPORARY:
                # Store in cache with TTL
                await self.cache_manager.set(
                    f"context_temp:{item.key}",
                    item.to_dict(),
                    ttl=300  # 5 minutes default for temporary
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing context item {item.key}: {e}")
            return False
    
    async def _find_context_item(
        self,
        key: str,
        conversation_id: Optional[str],
        session_id: Optional[str]
    ) -> Optional[ContextItem]:
        """Find context item in scope hierarchy"""
        
        # Search order: interaction -> conversation -> session -> global -> temporary
        search_order = [
            (ContextScope.INTERACTION, self.interaction_contexts.get(conversation_id or "", {})),
            (ContextScope.CONVERSATION, self.conversation_contexts.get(conversation_id or "", {})),
            (ContextScope.SESSION, self.session_contexts.get(session_id or "", {})),
            (ContextScope.GLOBAL, self.global_context)
        ]
        
        for scope, context_dict in search_order:
            if key in context_dict:
                return context_dict[key]
        
        # Check temporary cache
        temp_data = await self.cache_manager.get(f"context_temp:{key}")
        if temp_data:
            return ContextItem(**temp_data)
        
        return None
    
    async def _remove_from_scope(
        self,
        key: str,
        scope: ContextScope,
        conversation_id: Optional[str],
        session_id: Optional[str]
    ) -> bool:
        """Remove context item from specific scope"""
        try:
            if scope == ContextScope.GLOBAL:
                return self.global_context.pop(key, None) is not None
                
            elif scope == ContextScope.SESSION and session_id:
                return self.session_contexts[session_id].pop(key, None) is not None
                
            elif scope == ContextScope.CONVERSATION and conversation_id:
                return self.conversation_contexts[conversation_id].pop(key, None) is not None
                
            elif scope == ContextScope.INTERACTION and conversation_id:
                return self.interaction_contexts[conversation_id].pop(key, None) is not None
                
            elif scope == ContextScope.TEMPORARY:
                await self.cache_manager.delete(f"context_temp:{key}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing context from {scope.value}: {e}")
            return False
    
    async def _background_cleanup(self):
        """Background task for context cleanup and maintenance"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Remove expired contexts
                await self._cleanup_expired_contexts()
                
                # Optimize memory usage
                await self._optimize_context_storage()
                
                # Collect cleanup metrics
                await self.metrics_collector.increment("context.cleanup.runs")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _cleanup_expired_contexts(self):
        """Remove expired context items from all scopes"""
        current_time = datetime.utcnow()
        cleanup_count = 0
        
        # Clean all scope dictionaries
        for scope_dict in [
            self.global_context,
            *self.session_contexts.values(),
            *self.conversation_contexts.values(),
            *self.interaction_contexts.values()
        ]:
            expired_keys = [
                key for key, item in scope_dict.items()
                if item.is_expired()
            ]
            
            for key in expired_keys:
                del scope_dict[key]
                cleanup_count += 1
        
        if cleanup_count > 0:
            await self.metrics_collector.increment(
                "context.items.cleaned",
                value=cleanup_count
            )
            self.logger.debug(f"Cleaned up {cleanup_count} expired context items")
    
    async def _optimize_context_storage(self):
        """Optimize context storage and remove least recently used items"""
        total_items = (
            len(self.global_context) +
            sum(len(ctx) for ctx in self.session_contexts.values()) +
            sum(len(ctx) for ctx in self.conversation_contexts.values()) +
            sum(len(ctx) for ctx in self.interaction_contexts.values())
        )
        
        if total_items > self.max_context_items:
            # Remove LRU items based on access patterns
            await self._remove_lru_contexts(total_items - self.max_context_items)
    
    async def _remove_lru_contexts(self, count_to_remove: int):
        """Remove least recently used context items"""
        # Implementation would analyze access_patterns and remove LRU items
        # This is a simplified version
        removed = 0
        for pattern_key, accesses in self.access_patterns.items():
            if removed >= count_to_remove:
                break
            
            if not accesses or (datetime.utcnow() - accesses[-1]).days > 7:
                # Remove from all scopes
                await self.remove_context(pattern_key)
                removed += 1
        
        if removed > 0:
            self.logger.debug(f"Removed {removed} LRU context items")
    
    async def _load_global_context(self):
        """Load persistent global context from storage"""
        try:
            # Load from cache or database
            global_data = await self.cache_manager.get("global_context")
            if global_data:
                for key, item_data in global_data.items():
                    self.global_context[key] = ContextItem(**item_data)
                    
        except Exception as e:
            self.logger.error(f"Error loading global context: {e}")
    
    async def _save_global_context(self):
        """Save persistent global context to storage"""
        try:
            global_data = {
                key: item.to_dict()
                for key, item in self.global_context.items()
                if item.priority in [ContextPriority.CRITICAL, ContextPriority.HIGH]
            }
            
            await self.cache_manager.set(
                "global_context",
                global_data,
                ttl=86400 * 30  # 30 days
            )
            
        except Exception as e:
            self.logger.error(f"Error saving global context: {e}")
    
    async def _load_user_context(self, user_id: str, session_id: str):
        """Load user-specific context for new session"""
        try:
            # Load user preferences, settings, historical context
            user_data = await self.cache_manager.get(f"user_context:{user_id}")
            if user_data:
                for key, value in user_data.items():
                    await self.set_context(
                        key=f"user_{key}",
                        value=value,
                        scope=ContextScope.SESSION,
                        session_id=session_id,
                        priority=ContextPriority.HIGH,
                        source="user_profile"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error loading user context for {user_id}: {e}")
    
    async def _save_conversation_summary(
        self,
        conversation_id: str,
        state: ConversationState
    ):
        """Save conversation summary for analytics and learning"""
        try:
            summary = {
                "conversation_id": conversation_id,
                "user_id": state.user_id,
                "session_id": state.session_id,
                "duration": (datetime.utcnow() - state.last_activity).total_seconds(),
                "platform": state.platform,
                "final_intent": state.current_intent,
                "topics_covered": state.active_topics,
                "engagement_level": state.engagement_level,
                "completed_actions": len(state.pending_actions),
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_manager.set(
                f"conversation_summary:{conversation_id}",
                summary,
                ttl=86400 * 7  # Keep for 7 days
            )
            
        except Exception as e:
            self.logger.error(f"Error saving conversation summary: {e}")
    
    async def _get_scope_summary(
        self,
        scope: ContextScope,
        conversation_id: Optional[str],
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get summary for specific context scope"""
        if scope == ContextScope.GLOBAL:
            context_dict = self.global_context
        elif scope == ContextScope.SESSION and session_id:
            context_dict = self.session_contexts.get(session_id, {})
        elif scope == ContextScope.CONVERSATION and conversation_id:
            context_dict = self.conversation_contexts.get(conversation_id, {})
        elif scope == ContextScope.INTERACTION and conversation_id:
            context_dict = self.interaction_contexts.get(conversation_id, {})
        else:
            context_dict = {}
        
        return {
            "count": len(context_dict),
            "keys": list(context_dict.keys()),
            "priorities": {
                priority.value: sum(
                    1 for item in context_dict.values()
                    if item.priority == priority
                )
                for priority in ContextPriority
            }
        }
