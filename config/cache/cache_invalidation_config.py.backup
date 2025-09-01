"""Cache Invalidation Configuration for IA-Influencer Agent Platform
==================================================================

Advanced cache invalidation strategies and mechanisms for maintaining
data consistency across distributed cache layers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Optional, Set, Any, Callable, Pattern
from dataclasses import dataclass, field
from enum import Enum
import re
import time
import asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator
import json


class InvalidationStrategy(str, Enum):
    """Cache invalidation strategies"""
    TIME_BASED = "time_based"  # TTL-based invalidation
    EVENT_DRIVEN = "event_driven"  # Invalidate on data changes
    PATTERN_BASED = "pattern_based"  # Invalidate by key patterns
    TAG_BASED = "tag_based"  # Invalidate by tags
    VERSION_BASED = "version_based"  # Version-based invalidation
    DEPENDENCY_BASED = "dependency_based"  # Invalidate dependent keys
    MANUAL = "manual"  # Manual invalidation


class InvalidationEvent(str, Enum):
    """Events that can trigger cache invalidation"""
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DELETE = "content_delete"
    FINGERPRINT_UPDATE = "fingerprint_update"
    ALERT_TRIGGERED = "alert_triggered"
    REVENUE_UPDATE = "revenue_update"


class InvalidationScope(str, Enum):
    """Scope of cache invalidation"""
    SINGLE_KEY = "single_key"  # Invalidate specific key
    KEY_PATTERN = "key_pattern"  # Invalidate keys matching pattern
    TAG_GROUP = "tag_group"  # Invalidate all keys with specific tag
    TENANT_SCOPE = "tenant_scope"  # Invalidate all tenant keys
    GLOBAL_SCOPE = "global_scope"  # Invalidate all keys
    DEPENDENCY_CASCADE = "dependency_cascade"  # Cascade invalidation


@dataclass
class InvalidationRule:
    """Cache invalidation rule definition"""
    name: str
    strategy: InvalidationStrategy
    scope: InvalidationScope
    pattern: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    events: List[InvalidationEvent] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    delay_seconds: float = 0.0
    batch_size: int = 100
    max_keys: int = 1000
    enabled: bool = True
    
    def matches_event(self, event: InvalidationEvent) -> bool:
        """Check if rule applies to given event"""
        return event in self.events
    
    def matches_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if rule conditions are met"""
        if not self.conditions:
            return True
        
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            if isinstance(expected_value, dict) and expected_value.get("operator"):
                if not self._evaluate_condition(actual_value, expected_value):
                    return False
            elif actual_value != expected_value:
                return False
        
        return True
    
    def _evaluate_condition(self, actual: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate complex conditions"""
        operator = condition["operator"]
        expected = condition["value"]
        
        if operator == "eq":
            return actual == expected
        elif operator == "ne":
            return actual != expected
        elif operator == "gt":
            return actual > expected
        elif operator == "gte":
            return actual >= expected
        elif operator == "lt":
            return actual < expected
        elif operator == "lte":
            return actual <= expected
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        elif operator == "contains":
            return expected in actual
        elif operator == "regex":
            return bool(re.match(expected, str(actual)))
        
        return False


@dataclass
class InvalidationMetrics:
    """Cache invalidation metrics"""
    total_invalidations: int = 0
    keys_invalidated: int = 0
    pattern_invalidations: int = 0
    tag_invalidations: int = 0
    event_triggered_invalidations: int = 0
    manual_invalidations: int = 0
    failed_invalidations: int = 0
    average_invalidation_time: float = 0.0
    last_invalidation: Optional[datetime] = None


class CacheInvalidationConfig(BaseModel):
    """
    Comprehensive cache invalidation configuration
    """
    
    # General settings
    enabled: bool = True
    default_strategy: InvalidationStrategy = InvalidationStrategy.TIME_BASED
    
    # Invalidation rules
    rules: List[InvalidationRule] = field(default_factory=list)
    
    # Event handling
    event_processing_enabled: bool = True
    event_batch_size: int = 100
    event_processing_interval: float = 1.0
    event_queue_size: int = 10000
    
    # Pattern-based invalidation
    pattern_cache_size: int = 1000
    compiled_patterns: Dict[str, Pattern] = field(default_factory=dict)
    
    # Tag-based invalidation
    tag_index_enabled: bool = True
    max_tags_per_key: int = 10
    tag_separator: str = ","
    
    # Version-based invalidation
    version_tracking_enabled: bool = True
    global_version: int = 1
    version_increment_events: List[InvalidationEvent] = field(default_factory=list)
    
    # Dependency tracking
    dependency_tracking_enabled: bool = True
    max_dependencies_per_key: int = 50
    dependency_depth_limit: int = 5
    
    # Performance settings
    async_invalidation: bool = True
    max_concurrent_invalidations: int = 10
    invalidation_timeout: float = 30.0
    batch_invalidation_enabled: bool = True
    batch_processing_interval: float = 5.0
    
    # Monitoring
    enable_metrics: bool = True
    metrics_retention_hours: int = 24
    log_invalidations: bool = True
    log_level: str = "INFO"
    
    # Failover and recovery
    retry_failed_invalidations: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 1.0
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 10
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('rules')
    def validate_rules(cls, v):
        # Check for duplicate rule names
        names = [rule.name for rule in v]
        if len(names) != len(set(names)):
            raise ValueError("Rule names must be unique")
        return v
    
    @validator('event_queue_size')
    def validate_queue_size(cls, v):
        if v <= 0:
            raise ValueError("Event queue size must be positive")
        return v
    
    def add_rule(self, rule: InvalidationRule):
        """Add invalidation rule"""
        # Check for duplicate names
        if any(r.name == rule.name for r in self.rules):
            raise ValueError(f"Rule with name '{rule.name}' already exists")
        
        self.rules.append(rule)
        
        # Compile pattern if it's a pattern-based rule
        if rule.strategy == InvalidationStrategy.PATTERN_BASED and rule.pattern:
            try:
                self.compiled_patterns[rule.name] = re.compile(rule.pattern)
            except re.error as e:
                raise ValueError(f"Invalid pattern in rule '{rule.name}': {e}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove invalidation rule"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                if rule_name in self.compiled_patterns:
                    del self.compiled_patterns[rule_name]
                return True
        return False
    
    def get_rules_for_event(self, event: InvalidationEvent) -> List[InvalidationRule]:
        """Get rules that apply to specific event"""
        matching_rules = []
        
        for rule in self.rules:
            if rule.enabled and rule.matches_event(event):
                matching_rules.append(rule)
        
        # Sort by priority (higher priority first)
        return sorted(matching_rules, key=lambda r: r.priority, reverse=True)
    
    def get_keys_by_pattern(self, pattern: str, all_keys: List[str]) -> List[str]:
        """Get keys matching pattern"""
        try:
            compiled_pattern = re.compile(pattern)
            return [key for key in all_keys if compiled_pattern.match(key)]
        except re.error:
            return []
    
    def get_keys_by_tags(self, tags: List[str], tag_index: Dict[str, Set[str]]) -> Set[str]:
        """Get keys associated with specific tags"""
        if not self.tag_index_enabled:
            return set()
        
        matching_keys = set()
        for tag in tags:
            if tag in tag_index:
                matching_keys.update(tag_index[tag])
        
        return matching_keys
    
    def increment_global_version(self):
        """Increment global version for version-based invalidation"""
        if self.version_tracking_enabled:
            self.global_version += 1
    
    def should_invalidate_version(self, key_version: int) -> bool:
        """Check if key should be invalidated based on version"""
        return self.version_tracking_enabled and key_version < self.global_version
    
    def create_dependency_chain(self, key: str, dependencies: List[str]) -> Dict[str, List[str]]:
        """Create dependency chain for cascade invalidation"""
        if not self.dependency_tracking_enabled:
            return {}
        
        # Limit dependencies to prevent excessive cascade
        limited_deps = dependencies[:self.max_dependencies_per_key]
        
        return {key: limited_deps}
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for monitoring"""
        return {
            "enabled": self.enabled,
            "default_strategy": self.default_strategy,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules if r.enabled]),
            "event_processing_enabled": self.event_processing_enabled,
            "async_invalidation": self.async_invalidation,
            "tag_index_enabled": self.tag_index_enabled,
            "version_tracking_enabled": self.version_tracking_enabled,
            "dependency_tracking_enabled": self.dependency_tracking_enabled,
            "current_global_version": self.global_version
        }


class InvalidationExecutor:
    """
    Executes cache invalidation operations
    """
    
    def __init__(self, config: CacheInvalidationConfig):
        self.config = config
        self.metrics = InvalidationMetrics()
        self.event_queue = asyncio.Queue(maxsize=config.event_queue_size)
        self.dependency_graph: Dict[str, List[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.processing_task = None
    
    async def start(self):
        """Start invalidation processing"""
        if self.config.event_processing_enabled:
            self.processing_task = asyncio.create_task(self._process_events())
    
    async def stop(self):
        """Stop invalidation processing"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
    
    async def invalidate_by_event(self, event: InvalidationEvent, context: Dict[str, Any]):
        """Trigger invalidation based on event"""
        if not self.config.enabled:
            return
        
        await self.event_queue.put({
            "event": event,
            "context": context,
            "timestamp": datetime.utcnow()
        })
    
    async def invalidate_key(self, key: str, cache_client: Any) -> bool:
        """Invalidate single cache key"""
        start_time = time.time()
        
        try:
            # Remove from cache
            result = await self._delete_from_cache(cache_client, key)
            
            # Update metrics
            self.metrics.total_invalidations += 1
            self.metrics.keys_invalidated += 1
            self.metrics.last_invalidation = datetime.utcnow()
            
            # Update average time
            elapsed = time.time() - start_time
            self._update_average_time(elapsed)
            
            # Remove from dependency graph
            self._remove_from_dependencies(key)
            
            # Remove from tag index
            self._remove_from_tags(key)
            
            return result
            
        except Exception as e:
            self.metrics.failed_invalidations += 1
            if self.config.log_invalidations:
                # Log error (implementation depends on logging setup)
                pass
            return False
    
    async def invalidate_pattern(self, pattern: str, cache_client: Any, all_keys: List[str]) -> int:
        """Invalidate keys matching pattern"""
        if not self.config.enabled:
            return 0
        
        matching_keys = self.config.get_keys_by_pattern(pattern, all_keys)
        
        if not matching_keys:
            return 0
        
        # Batch invalidation for performance
        invalidated_count = 0
        
        if self.config.batch_invalidation_enabled:
            batch_size = self.config.event_batch_size
            for i in range(0, len(matching_keys), batch_size):
                batch = matching_keys[i:i + batch_size]
                batch_result = await self._invalidate_batch(cache_client, batch)
                invalidated_count += batch_result
        else:
            # Sequential invalidation
            for key in matching_keys:
                if await self.invalidate_key(key, cache_client):
                    invalidated_count += 1
        
        self.metrics.pattern_invalidations += 1
        return invalidated_count
    
    async def invalidate_tags(self, tags: List[str], cache_client: Any) -> int:
        """Invalidate keys associated with tags"""
        if not self.config.tag_index_enabled:
            return 0
        
        keys_to_invalidate = self.config.get_keys_by_tags(tags, self.tag_index)
        
        if not keys_to_invalidate:
            return 0
        
        invalidated_count = 0
        
        for key in keys_to_invalidate:
            if await self.invalidate_key(key, cache_client):
                invalidated_count += 1
        
        self.metrics.tag_invalidations += 1
        return invalidated_count
    
    async def invalidate_dependencies(self, key: str, cache_client: Any) -> int:
        """Invalidate dependent keys in cascade"""
        if not self.config.dependency_tracking_enabled:
            return 0
        
        dependent_keys = self._get_dependent_keys(key, depth=0)
        
        if not dependent_keys:
            return 0
        
        invalidated_count = 0
        
        for dep_key in dependent_keys:
            if await self.invalidate_key(dep_key, cache_client):
                invalidated_count += 1
        
        return invalidated_count
    
    async def _process_events(self):
        """Process invalidation events from queue"""
        while True:
            try:
                # Get events in batch
                events = []
                
                try:
                    # Get first event (blocking)
                    event = await asyncio.wait_for(
                        self.event_queue.get(),
                        timeout=self.config.event_processing_interval
                    )
                    events.append(event)
                    
                    # Get additional events (non-blocking)
                    while len(events) < self.config.event_batch_size:
                        try:
                            event = self.event_queue.get_nowait()
                            events.append(event)
                        except asyncio.QueueEmpty:
                            break
                
                except asyncio.TimeoutError:
                    # No events to process
                    continue
                
                # Process events
                await self._process_event_batch(events)
                
            except Exception as e:
                # Log error and continue
                if self.config.log_invalidations:
                    pass  # Log error
                await asyncio.sleep(1.0)
    
    async def _process_event_batch(self, events: List[Dict[str, Any]]):
        """Process batch of invalidation events"""
        for event_data in events:
            event = event_data["event"]
            context = event_data["context"]
            
            # Get applicable rules
            rules = self.config.get_rules_for_event(event)
            
            for rule in rules:
                if rule.matches_conditions(context):
                    await self._execute_rule(rule, context)
    
    async def _execute_rule(self, rule: InvalidationRule, context: Dict[str, Any]):
        """Execute specific invalidation rule"""
        # Implementation depends on cache client interface
        # This is a placeholder that would be implemented with actual cache operations
        pass
    
    async def _delete_from_cache(self, cache_client: Any, key: str) -> bool:
        """Delete key from cache"""
        try:
            # Implementation depends on cache client interface
            if hasattr(cache_client, 'delete'):
                if asyncio.iscoroutinefunction(cache_client.delete):
                    return await cache_client.delete(key)
                else:
                    return cache_client.delete(key)
            return False
        except Exception:
            return False
    
    async def _invalidate_batch(self, cache_client: Any, keys: List[str]) -> int:
        """Invalidate batch of keys"""
        if hasattr(cache_client, 'delete_many'):
            try:
                if asyncio.iscoroutinefunction(cache_client.delete_many):
                    result = await cache_client.delete_many(keys)
                else:
                    result = cache_client.delete_many(keys)
                return len(keys) if result else 0
            except Exception:
                pass
        
        # Fallback to individual deletions
        count = 0
        for key in keys:
            if await self._delete_from_cache(cache_client, key):
                count += 1
        return count
    
    def _get_dependent_keys(self, key: str, depth: int) -> Set[str]:
        """Get keys that depend on given key"""
        if depth >= self.config.dependency_depth_limit:
            return set()
        
        dependents = set()
        
        # Find direct dependents
        for dep_key, deps in self.dependency_graph.items():
            if key in deps:
                dependents.add(dep_key)
                # Recursively find nested dependents
                nested = self._get_dependent_keys(dep_key, depth + 1)
                dependents.update(nested)
        
        return dependents
    
    def _remove_from_dependencies(self, key: str):
        """Remove key from dependency graph"""
        # Remove as dependent
        if key in self.dependency_graph:
            del self.dependency_graph[key]
        
        # Remove from other keys' dependencies
        for deps in self.dependency_graph.values():
            if key in deps:
                deps.remove(key)
    
    def _remove_from_tags(self, key: str):
        """Remove key from tag index"""
        for tag_keys in self.tag_index.values():
            if key in tag_keys:
                tag_keys.discard(key)
    
    def _update_average_time(self, elapsed_time: float):
        """Update average invalidation time"""
        total_ops = self.metrics.total_invalidations
        if total_ops > 1:
            self.metrics.average_invalidation_time = (
                (self.metrics.average_invalidation_time * (total_ops - 1) + elapsed_time) / total_ops
            )
        else:
            self.metrics.average_invalidation_time = elapsed_time


# Predefined invalidation rules for common scenarios
DEFAULT_RULES = [
    InvalidationRule(
        name="user_data_update",
        strategy=InvalidationStrategy.PATTERN_BASED,
        scope=InvalidationScope.KEY_PATTERN,
        pattern=r"user:\d+:.*",
        events=[InvalidationEvent.DATA_UPDATE, InvalidationEvent.PERMISSION_CHANGE],
        priority=10
    ),
    InvalidationRule(
        name="content_changes",
        strategy=InvalidationStrategy.TAG_BASED,
        scope=InvalidationScope.TAG_GROUP,
        tags=["content", "fingerprint"],
        events=[InvalidationEvent.CONTENT_UPLOAD, InvalidationEvent.CONTENT_DELETE, 
                InvalidationEvent.FINGERPRINT_UPDATE],
        priority=8
    ),
    InvalidationRule(
        name="revenue_updates",
        strategy=InvalidationStrategy.EVENT_DRIVEN,
        scope=InvalidationScope.KEY_PATTERN,
        pattern=r"revenue:.*",
        events=[InvalidationEvent.REVENUE_UPDATE],
        priority=5
    ),
    InvalidationRule(
        name="configuration_changes",
        strategy=InvalidationStrategy.GLOBAL_SCOPE,
        scope=InvalidationScope.GLOBAL_SCOPE,
        events=[InvalidationEvent.CONFIGURATION_CHANGE],
        priority=15,
        delay_seconds=1.0  # Small delay to allow config propagation
    )
]

# Default configurations
DEFAULT_CONFIG = CacheInvalidationConfig(rules=DEFAULT_RULES)

PRODUCTION_CONFIG = CacheInvalidationConfig(
    rules=DEFAULT_RULES,
    async_invalidation=True,
    max_concurrent_invalidations=20,
    batch_invalidation_enabled=True,
    event_batch_size=500,
    tag_index_enabled=True,
    dependency_tracking_enabled=True,
    enable_metrics=True,
    circuit_breaker_enabled=True
)

DEVELOPMENT_CONFIG = CacheInvalidationConfig(
    rules=DEFAULT_RULES,
    log_invalidations=True,
    log_level="DEBUG",
    enable_metrics=True,
    event_batch_size=50,
    max_concurrent_invalidations=5
)
