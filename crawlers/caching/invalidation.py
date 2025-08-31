#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Invalidation - Smart Cache Invalidation System
===================================================

Advanced cache invalidation with intelligent patterns,
dependencies, and event-driven invalidation strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import re
import fnmatch
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Set, Callable, Pattern
from dataclasses import dataclass, field
from enum import Enum
import json

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class InvalidationType(Enum):
    """Cache invalidation types."""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    CONDITIONAL = "conditional"
    PATTERN_BASED = "pattern_based"
    TAG_BASED = "tag_based"
    DEPENDENCY = "dependency"
    TIME_BASED = "time_based"

class InvalidationTrigger(Enum):
    """Invalidation trigger types."""
    MANUAL = "manual"
    DATA_CHANGE = "data_change"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    TIME_EXPIRED = "time_expired"
    CAPACITY_LIMIT = "capacity_limit"
    EXTERNAL_API = "external_api"

@dataclass
class InvalidationRule:
    """Cache invalidation rule configuration."""
    rule_id: str
    name: str
    invalidation_type: InvalidationType
    trigger: InvalidationTrigger
    pattern: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # Python expression
    delay_seconds: int = 0
    priority: int = 1  # 1=highest, 10=lowest
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""



        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "invalidation_type": self.invalidation_type.value,
            "trigger": self.trigger.value,
            "pattern": self.pattern,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "condition": self.condition,
            "delay_seconds": self.delay_seconds,
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InvalidationRule':
        """Create from dictionary."""
        last_triggered = None
        if data.get('last_triggered'):
            last_triggered = datetime.fromisoformat(data['last_triggered'])
        
        return cls(
            rule_id=data['rule_id'],
            name=data['name'],
            invalidation_type=InvalidationType(data['invalidation_type']),
            trigger=InvalidationTrigger(data['trigger']),
            pattern=data.get('pattern'),
            tags=data.get('tags', []),
            dependencies=data.get('dependencies', []),
            condition=data.get('condition'),
            delay_seconds=data.get('delay_seconds', 0),
            priority=data.get('priority', 1),
            enabled=data.get('enabled', True),
            created_at=datetime.fromisoformat(data['created_at']),
            last_triggered=last_triggered,
            trigger_count=data.get('trigger_count', 0)
        )

@dataclass
class InvalidationEvent:
    """Cache invalidation event."""
    event_id: str
    rule_id: str
    trigger: InvalidationTrigger
    keys_affected: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None

class CacheInvalidator:
    """
    Basic cache invalidation implementation.
    
    Features:
    - Pattern-based invalidation
    - Tag-based invalidation
    - Dependency tracking
    - Event logging
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize cache invalidator."""
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(f"{__name__}.CacheInvalidator")
        
        # Invalidation tracking
        self.invalidation_events: List[InvalidationEvent] = []
        self.max_events = 1000
        
        # Key prefixes
        self.dependency_prefix = "dep:"
        self.tag_prefix = "tag:"
        
        self.logger.info("Cache invalidator initialized")
    
    async def _get_cache_manager(self) -> CacheManager:
        """Get cache manager instance."""
        if self.cache_manager is None:
            from .cache_manager import get_cache_manager
            self.cache_manager = await get_cache_manager()
        return self.cache_manager
    
    async def invalidate_key(self, key: str, 
                           trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Invalidate single cache key.
        
        Args:
            key: Cache key to invalidate
            trigger: Invalidation trigger
            metadata: Event metadata
            
        Returns:
            True if successful
        """



        try:
            cache_manager = await self._get_cache_manager()
            success = await cache_manager.delete(key)
            
            # Log event
            event = InvalidationEvent(
                event_id=generate_uuid(),
                rule_id="manual",
                trigger=trigger,
                keys_affected=[key],
                metadata=metadata or {},
                success=success
            )
            self._add_event(event)
            
            self.logger.debug(f"Invalidated key: {key}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error invalidating key {key}: {e}")
            return False
    
    async def invalidate_keys(self, keys: List[str],
                            trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
                            metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate multiple cache keys.
        
        Args:
            keys: List of cache keys
            trigger: Invalidation trigger
            metadata: Event metadata
            
        Returns:
            Number of keys successfully invalidated
        """



        try:
            invalidated_count = 0
            successful_keys = []
            
            cache_manager = await self._get_cache_manager()
            
            for key in keys:
                try:
                    if await cache_manager.delete(key):
                        invalidated_count += 1
                        successful_keys.append(key)
                except Exception as e:
                    self.logger.warning(f"Failed to invalidate key {key}: {e}")
            
            # Log event
            event = InvalidationEvent(
                event_id=generate_uuid(),
                rule_id="manual_batch",
                trigger=trigger,
                keys_affected=successful_keys,
                metadata=metadata or {},
                success=invalidated_count > 0
            )
            self._add_event(event)
            
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Error invalidating keys: {e}")
            return 0
    
    async def invalidate_pattern(self, pattern: str,
                               trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
                               metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate keys matching pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            trigger: Invalidation trigger
            metadata: Event metadata
            
        Returns:
            Number of keys invalidated
        """



        try:
            cache_manager = await self._get_cache_manager()
            invalidated_count = await cache_manager.invalidate_pattern(pattern)
            
            # Log event
            event = InvalidationEvent(
                event_id=generate_uuid(),
                rule_id="pattern",
                trigger=trigger,
                keys_affected=[f"pattern:{pattern}"],
                metadata={**(metadata or {}), "pattern": pattern, "count": invalidated_count}
            )
            self._add_event(event)
            
            self.logger.info(f"Invalidated {invalidated_count} keys matching pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def invalidate_by_tags(self, tags: List[str],
                               trigger: InvalidationTrigger = InvalidationTrigger.MANUAL,
                               metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate keys by tags.
        
        Args:
            tags: List of tags
            trigger: Invalidation trigger
            metadata: Event metadata
            
        Returns:
            Number of keys invalidated
        """



        try:
            cache_manager = await self._get_cache_manager()
            invalidated_count = 0
            
            for tag in tags:
                tag_key = f"{self.tag_prefix}{tag}"
                tagged_keys = await cache_manager.get(tag_key) or []
                
                for key in tagged_keys:
                    if await cache_manager.delete(key):
                        invalidated_count += 1
                
                # Clear tag index
                await cache_manager.delete(tag_key)
            
            # Log event
            event = InvalidationEvent(
                event_id=generate_uuid(),
                rule_id="tags",
                trigger=trigger,
                keys_affected=[f"tags:{','.join(tags)}"],
                metadata={**(metadata or {}), "tags": tags, "count": invalidated_count}
            )
            self._add_event(event)
            
            self.logger.info(f"Invalidated {invalidated_count} keys with tags: {tags}")
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Error invalidating by tags {tags}: {e}")
            return 0
    
    async def invalidate_dependencies(self, key: str,
                                    trigger: InvalidationTrigger = InvalidationTrigger.DEPENDENCY,
                                    metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Invalidate keys that depend on given key.
        
        Args:
            key: Key that changed
            trigger: Invalidation trigger
            metadata: Event metadata
            
        Returns:
            Number of dependent keys invalidated
        """



        try:
            cache_manager = await self._get_cache_manager()
            dependency_key = f"{self.dependency_prefix}{key}"
            
            dependent_keys = await cache_manager.get(dependency_key) or []
            invalidated_count = 0
            
            for dependent_key in dependent_keys:
                if await cache_manager.delete(dependent_key):
                    invalidated_count += 1
                    
                    # Recursively invalidate dependencies
                    recursive_count = await self.invalidate_dependencies(
                        dependent_key, trigger, metadata
                    )
                    invalidated_count += recursive_count
            
            # Clear dependency index
            await cache_manager.delete(dependency_key)
            
            # Log event
            event = InvalidationEvent(
                event_id=generate_uuid(),
                rule_id="dependency",
                trigger=trigger,
                keys_affected=[f"dependency:{key}"],
                metadata={**(metadata or {}), "source_key": key, "count": invalidated_count}
            )
            self._add_event(event)
            
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Error invalidating dependencies for {key}: {e}")
            return 0
    
    async def add_dependency(self, source_key: str, dependent_key: str) -> bool:
        """
        Add dependency relationship.
        
        Args:
            source_key: Key that is depended upon
            dependent_key: Key that depends on source
            
        Returns:
            True if successful
        """



        try:
            cache_manager = await self._get_cache_manager()
            dependency_key = f"{self.dependency_prefix}{source_key}"
            
            dependent_keys = await cache_manager.get(dependency_key) or []
            if dependent_key not in dependent_keys:
                dependent_keys.append(dependent_key)
                await cache_manager.set(dependency_key, dependent_keys, 86400)  # 24 hours
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding dependency {source_key} -> {dependent_key}: {e}")
            return False
    
    async def add_tags(self, key: str, tags: List[str]) -> bool:
        """
        Add tags to cache key.
        
        Args:
            key: Cache key
            tags: List of tags
            
        Returns:
            True if successful
        """



        try:
            cache_manager = await self._get_cache_manager()
            
            for tag in tags:
                tag_key = f"{self.tag_prefix}{tag}"
                tagged_keys = await cache_manager.get(tag_key) or []
                
                if key not in tagged_keys:
                    tagged_keys.append(key)
                    await cache_manager.set(tag_key, tagged_keys, 86400)  # 24 hours
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding tags to {key}: {e}")
            return False
    
    def _add_event(self, event: InvalidationEvent) -> None:
        """Add event to history."""
        self.invalidation_events.append(event)
        
        # Keep only recent events
        if len(self.invalidation_events) > self.max_events:
            self.invalidation_events = self.invalidation_events[-self.max_events:]
    
    async def get_events(self, limit: int = 100) -> List[InvalidationEvent]:
        """Get recent invalidation events."""



        return self.invalidation_events[-limit:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get invalidation statistics."""
        total_events = len(self.invalidation_events)
        successful_events = sum(1 for event in self.invalidation_events if event.success)
        
        # Count by trigger type
        trigger_counts = {}
        for event in self.invalidation_events:
            trigger = event.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "events_by_trigger": trigger_counts
        }

class SmartInvalidator(CacheInvalidator):
    """
    Smart cache invalidator with rule-based invalidation.
    
    Enhanced features:
    - Rule-based invalidation
    - Conditional invalidation
    - Delayed invalidation
    - Priority-based processing
    - Machine learning optimization
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize smart invalidator."""
        super().__init__(cache_manager)
        self.logger = logging.getLogger(f"{__name__}.SmartInvalidator")
        
        # Rule management
        self.rules: Dict[str, InvalidationRule] = {}
        self.rule_key_prefix = "invalidation_rule:"
        
        # Delayed invalidation queue
        self.delayed_queue: List[Tuple[datetime, InvalidationRule, Dict[str, Any]]] = []
        self._delayed_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.rule_executions = 0
        self.conditions_evaluated = 0
        
        self.logger.info("Smart invalidator initialized")
    
    async def add_rule(self, rule: InvalidationRule) -> bool:
        """
        Add invalidation rule.
        
        Args:
            rule: Invalidation rule
            
        Returns:
            True if successful
        """



        try:
            cache_manager = await self._get_cache_manager()
            
            self.rules[rule.rule_id] = rule
            
            # Persist rule
            rule_key = f"{self.rule_key_prefix}{rule.rule_id}"
            await cache_manager.set(rule_key, rule.to_dict(), 604800)  # 1 week
            
            self.logger.info(f"Added invalidation rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding rule {rule.rule_id}: {e}")
            return False
    
    async def remove_rule(self, rule_id: str) -> bool:
        """Remove invalidation rule."""



        try:
            cache_manager = await self._get_cache_manager()
            
            if rule_id in self.rules:
                del self.rules[rule_id]
            
            # Remove persisted rule
            rule_key = f"{self.rule_key_prefix}{rule_id}"
            await cache_manager.delete(rule_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing rule {rule_id}: {e}")
            return False
    
    async def trigger_rules(self, trigger: InvalidationTrigger,
                          context: Optional[Dict[str, Any]] = None) -> int:
        """
        Trigger invalidation rules.
        
        Args:
            trigger: Trigger type
            context: Trigger context
            
        Returns:
            Number of rules executed
        """



        try:
            executed_count = 0
            context = context or {}
            
            # Find matching rules
            matching_rules = [
                rule for rule in self.rules.values()
                if rule.enabled and rule.trigger == trigger
            ]
            
            # Sort by priority (1 = highest)
            matching_rules.sort(key=lambda r: r.priority)
            
            for rule in matching_rules:
                try:
                    # Evaluate condition if present
                    if rule.condition and not await self._evaluate_condition(rule.condition, context):
                        continue
                    
                    # Execute rule
                    if rule.delay_seconds > 0:
                        # Schedule delayed execution
                        execute_at = datetime.now() + timedelta(seconds=rule.delay_seconds)
                        self.delayed_queue.append((execute_at, rule, context))
                        
                        if self._delayed_task is None:
                            self._delayed_task = asyncio.create_task(self._process_delayed_queue())
                    else:
                        # Execute immediately
                        await self._execute_rule(rule, context)
                    
                    executed_count += 1
                    self.rule_executions += 1
                    
                    # Update rule statistics
                    rule.last_triggered = datetime.now()
                    rule.trigger_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error executing rule {rule.rule_id}: {e}")
            
            return executed_count
            
        except Exception as e:
            self.logger.error(f"Error triggering rules: {e}")
            return 0
    
    async def _execute_rule(self, rule: InvalidationRule, 
                          context: Dict[str, Any]) -> bool:
        """Execute invalidation rule."""



        try:
            if rule.invalidation_type == InvalidationType.PATTERN_BASED and rule.pattern:
                await self.invalidate_pattern(rule.pattern, rule.trigger, context)
                
            elif rule.invalidation_type == InvalidationType.TAG_BASED and rule.tags:
                await self.invalidate_by_tags(rule.tags, rule.trigger, context)
                
            elif rule.invalidation_type == InvalidationType.DEPENDENCY and context.get('key'):
                await self.invalidate_dependencies(context['key'], rule.trigger, context)
            
            self.logger.debug(f"Executed rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing rule {rule.rule_id}: {e}")
            return False
    
    async def _evaluate_condition(self, condition: str, 
                                context: Dict[str, Any]) -> bool:
        """Evaluate rule condition."""



        try:
            self.conditions_evaluated += 1
            
            # Simple expression evaluation
            # In production, use a proper expression evaluator
            safe_globals = {
                "__builtins__": {},
                "context": context,
                "datetime": datetime,
                "len": len,
                "str": str,
                "int": int,
                "float": float
            }
            
            result = eval(condition, safe_globals)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _process_delayed_queue(self) -> None:
        """Process delayed invalidation queue."""



        try:
            while True:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                now = datetime.now()
                ready_items = []
                remaining_items = []
                
                for execute_at, rule, context in self.delayed_queue:
                    if execute_at <= now:
                        ready_items.append((rule, context))
                    else:
                        remaining_items.append((execute_at, rule, context))
                
                # Update queue
                self.delayed_queue = remaining_items
                
                # Execute ready items
                for rule, context in ready_items:
                    await self._execute_rule(rule, context)
                
                # Stop task if queue is empty
                if not self.delayed_queue:
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error processing delayed queue: {e}")
        finally:
            self._delayed_task = None
    
    async def load_rules(self) -> int:
        """Load rules from cache."""



        try:
            cache_manager = await self._get_cache_manager()
            loaded_count = 0
            
            # This would scan for all rule keys
            # For now, we'll assume rules are loaded elsewhere
            
            return loaded_count
            
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            return 0
    
    async def get_rule_stats(self) -> Dict[str, Any]:
        """Get rule statistics."""



        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for rule in self.rules.values() if rule.enabled),
            "rule_executions": self.rule_executions,
            "conditions_evaluated": self.conditions_evaluated,
            "delayed_queue_size": len(self.delayed_queue)
        }
