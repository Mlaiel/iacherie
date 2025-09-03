#!/usr/bin/env python3
"""
Cache Invalidation Strategy Implementation
Advanced cache invalidation with event-driven, pattern-based, and dependency tracking
"""
import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import fnmatch
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class InvalidationPriority(Enum):
    """Cache invalidation priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"

class InvalidationStrategy(Enum):
    """Cache invalidation strategies"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    BATCH = "batch"
    CASCADE = "cascade"

@dataclass
class InvalidationRule:
    """Cache invalidation rule definition"""
    name: str
    pattern: str  # Key pattern to match
    strategy: InvalidationStrategy = InvalidationStrategy.IMMEDIATE
    priority: InvalidationPriority = InvalidationPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    ttl_override: Optional[int] = None
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InvalidationRequest:
    """Cache invalidation request"""
    id: str
    target_keys: List[str]
    rule_name: Optional[str] = None
    priority: InvalidationPriority = InvalidationPriority.NORMAL
    strategy: InvalidationStrategy = InvalidationStrategy.IMMEDIATE
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_time: Optional[datetime] = None
    rollback_data: Optional[Dict[str, Any]] = None

@dataclass
class InvalidationResult:
    """Cache invalidation result"""
    request_id: str
    success: bool
    invalidated_keys: List[str]
    failed_keys: List[str]
    execution_time_ms: float
    business_impact_actual: Dict[str, Any]
    creator_notifications_sent: List[str]
    rollback_possible: bool
    dependencies_resolved: bool

class CacheInvalidationEngine:
    """
    Advanced Cache Invalidation Engine
    
    Features:
    - Event-driven invalidation
    - Pattern-based invalidation
    - Dependency tracking
    - Batch processing
    - Priority queuing
    - Rollback support
    - Impact analysis
    """
    
    def __init__(self, cache_manager, event_bus=None):
        self.cache_manager = cache_manager
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"{__name__}.CacheInvalidationEngine")
        
        # Invalidation rules
        self.rules: Dict[str, InvalidationRule] = {}
        self.pattern_rules: List[InvalidationRule] = []
        
        # Dependency tracking
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}
        
        # Processing queues
        self.invalidation_queue = asyncio.Queue()
        self.batch_queue = asyncio.Queue()
        self.delayed_queue = asyncio.Queue()
        
        # Statistics
        self.stats = {
            "total_invalidations": 0,
            "pattern_invalidations": 0,
            "dependency_invalidations": 0,
            "failed_invalidations": 0,
            "avg_processing_time": 0.0
        }
        
        # Background tasks
        self.processing_task = None
        self.batch_processing_task = None
        self.delayed_processing_task = None
    
    async def initialize(self):
        """Initialize invalidation engine"""
        self.logger.info("🔧 Initializing cache invalidation engine...")
        
        # Load default rules
        await self._load_default_rules()
        
        # Start background processors
        self.processing_task = asyncio.create_task(self._process_invalidations())
        self.batch_processing_task = asyncio.create_task(self._process_batch_invalidations())
        self.delayed_processing_task = asyncio.create_task(self._process_delayed_invalidations())
        
        self.logger.info("✅ Cache invalidation engine initialized")
    
    async def _load_default_rules(self):
        """Load default invalidation rules"""
        
        # User session invalidation
        await self.add_rule(InvalidationRule(
            name="user_session_invalidation",
            pattern="session:user:*",
            strategy=InvalidationStrategy.IMMEDIATE,
            priority=InvalidationPriority.HIGH,
            tags={"session", "user"}
        ))
        
        # Content cache invalidation
        await self.add_rule(InvalidationRule(
            name="content_cache_invalidation", 
            pattern="content:*",
            strategy=InvalidationStrategy.CASCADE,
            priority=InvalidationPriority.NORMAL,
            dependencies=["media:*", "thumbnail:*"],
            tags={"content", "media"}
        ))
        
        # API response cache invalidation
        await self.add_rule(InvalidationRule(
            name="api_response_invalidation",
            pattern="api:response:*",
            strategy=InvalidationStrategy.BATCH,
            priority=InvalidationPriority.LOW,
            tags={"api", "response"}
        ))
        
        # Emergency invalidation for security
        await self.add_rule(InvalidationRule(
            name="security_emergency_invalidation",
            pattern="*",
            strategy=InvalidationStrategy.IMMEDIATE,
            priority=InvalidationPriority.EMERGENCY,
            tags={"security", "emergency"}
        ))
    
    async def add_rule(self, rule: InvalidationRule):
        """Add invalidation rule"""
        self.rules[rule.name] = rule
        
        if '*' in rule.pattern or '?' in rule.pattern:
            self.pattern_rules.append(rule)
        
        # Register dependencies
        for dep in rule.dependencies:
            if dep not in self.dependency_graph:
                self.dependency_graph[dep] = set()
            self.dependency_graph[dep].add(rule.pattern)
            
            if rule.pattern not in self.reverse_dependencies:
                self.reverse_dependencies[rule.pattern] = set()
            self.reverse_dependencies[rule.pattern].add(dep)
        
        self.logger.debug(f"Added invalidation rule: {rule.name}")
    
    async def invalidate_key(self, key: str, priority: InvalidationPriority = InvalidationPriority.NORMAL, 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Invalidate single cache key"""
        return await self.invalidate_keys([key], priority, metadata)
    
    async def invalidate_keys(self, keys: List[str], priority: InvalidationPriority = InvalidationPriority.NORMAL,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """Invalidate multiple cache keys"""
        
        request = InvalidationRequest(
            id=self._generate_request_id(),
            target_keys=keys,
            priority=priority,
            metadata=metadata or {}
        )
        
        return await self.process_invalidation_request(request)
    
    async def invalidate_pattern(self, pattern: str, priority: InvalidationPriority = InvalidationPriority.NORMAL,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Invalidate keys matching pattern"""
        
        # Find keys matching pattern
        matching_keys = await self._find_keys_by_pattern(pattern)
        
        request = InvalidationRequest(
            id=self._generate_request_id(),
            target_keys=matching_keys,
            priority=priority,
            metadata=metadata or {},
            tags={"pattern_invalidation"}
        )
        
        return await self.process_invalidation_request(request)
    
    async def invalidate_by_tags(self, tags: Set[str], priority: InvalidationPriority = InvalidationPriority.NORMAL,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """Invalidate keys by tags"""
        
        # Find keys with matching tags
        matching_keys = await self._find_keys_by_tags(tags)
        
        request = InvalidationRequest(
            id=self._generate_request_id(),
            target_keys=matching_keys,
            priority=priority,
            tags=tags,
            metadata=metadata or {}
        )
        
        return await self.process_invalidation_request(request)
    
    async def process_invalidation_request(self, request: InvalidationRequest) -> str:
        """Process invalidation request"""
        
        # Find applicable rules
        applicable_rules = await self._find_applicable_rules(request.target_keys)
        
        # Apply rule strategies
        if applicable_rules:
            rule = applicable_rules[0]  # Use highest priority rule
            request.strategy = rule.strategy
            request.priority = max(request.priority, rule.priority, key=lambda x: x.value)
            request.rule_name = rule.name
        
        # Calculate dependencies
        dependent_keys = await self._calculate_dependencies(request.target_keys)
        request.target_keys.extend(dependent_keys)
        request.target_keys = list(set(request.target_keys))  # Remove duplicates
        
        # Queue based on strategy
        if request.strategy == InvalidationStrategy.IMMEDIATE:
            await self.invalidation_queue.put(request)
        elif request.strategy == InvalidationStrategy.BATCH:
            await self.batch_queue.put(request)
        elif request.strategy == InvalidationStrategy.DELAYED:
            request.scheduled_time = datetime.now() + timedelta(seconds=30)
            await self.delayed_queue.put(request)
        
        self.logger.info(f"Queued invalidation request {request.id} with {len(request.target_keys)} keys")
        return request.id
    
    async def _process_invalidations(self):
        """Process immediate invalidations"""
        while True:
            try:
                request = await self.invalidation_queue.get()
                await self._execute_invalidation(request)
                self.invalidation_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing invalidation: {e}")
    
    async def _process_batch_invalidations(self):
        """Process batch invalidations"""
        batch = []
        last_process_time = time.time()
        
        while True:
            try:
                # Wait for requests or timeout
                try:
                    request = await asyncio.wait_for(self.batch_queue.get(), timeout=5.0)
                    batch.append(request)
                    self.batch_queue.task_done()
                except asyncio.TimeoutError:
                    pass
                
                # Process batch if conditions met
                current_time = time.time()
                if (batch and 
                    (len(batch) >= 10 or  # Batch size threshold
                     current_time - last_process_time >= 30)):  # Time threshold
                    
                    await self._execute_batch_invalidation(batch)
                    batch = []
                    last_process_time = current_time
                
            except asyncio.CancelledError:
                # Process remaining batch before exiting
                if batch:
                    await self._execute_batch_invalidation(batch)
                break
            except Exception as e:
                self.logger.error(f"Error processing batch invalidations: {e}")
    
    async def _process_delayed_invalidations(self):
        """Process delayed invalidations"""
        while True:
            try:
                request = await self.delayed_queue.get()
                
                # Wait until scheduled time
                if request.scheduled_time and request.scheduled_time > datetime.now():
                    delay = (request.scheduled_time - datetime.now()).total_seconds()
                    await asyncio.sleep(delay)
                
                await self._execute_invalidation(request)
                self.delayed_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing delayed invalidation: {e}")
    
    async def _execute_invalidation(self, request: InvalidationRequest) -> InvalidationResult:
        """Execute single invalidation request"""
        start_time = time.time()
        invalidated_keys = []
        failed_keys = []
        
        try:
            for key in request.target_keys:
                try:
                    success = await self.cache_manager.delete(key)
                    if success:
                        invalidated_keys.append(key)
                    else:
                        failed_keys.append(key)
                except Exception as e:
                    self.logger.error(f"Failed to invalidate key {key}: {e}")
                    failed_keys.append(key)
            
            # Update statistics
            self._update_stats(time.time() - start_time, len(invalidated_keys), len(failed_keys))
            
            # Send notifications if configured
            notifications_sent = await self._send_notifications(request, invalidated_keys)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = InvalidationResult(
                request_id=request.id,
                success=len(failed_keys) == 0,
                invalidated_keys=invalidated_keys,
                failed_keys=failed_keys,
                execution_time_ms=execution_time,
                business_impact_actual=await self._calculate_business_impact(invalidated_keys),
                creator_notifications_sent=notifications_sent,
                rollback_possible=request.rollback_data is not None,
                dependencies_resolved=True
            )
            
            self.logger.info(f"Executed invalidation {request.id}: {len(invalidated_keys)} invalidated, {len(failed_keys)} failed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing invalidation {request.id}: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return InvalidationResult(
                request_id=request.id,
                success=False,
                invalidated_keys=invalidated_keys,
                failed_keys=request.target_keys,
                execution_time_ms=execution_time,
                business_impact_actual={},
                creator_notifications_sent=[],
                rollback_possible=False,
                dependencies_resolved=False
            )
    
    async def _execute_batch_invalidation(self, batch: List[InvalidationRequest]) -> List[InvalidationResult]:
        """Execute batch of invalidation requests"""
        results = []
        
        self.logger.info(f"Executing batch invalidation with {len(batch)} requests")
        
        for request in batch:
            result = await self._execute_invalidation(request)
            results.append(result)
        
        return results
    
    async def _find_applicable_rules(self, keys: List[str]) -> List[InvalidationRule]:
        """Find rules applicable to given keys"""
        applicable_rules = []
        
        for rule in self.pattern_rules:
            for key in keys:
                if fnmatch.fnmatch(key, rule.pattern):
                    applicable_rules.append(rule)
                    break
        
        # Sort by priority
        applicable_rules.sort(key=lambda r: r.priority.value, reverse=True)
        return applicable_rules
    
    async def _calculate_dependencies(self, keys: List[str]) -> List[str]:
        """Calculate dependent keys that should also be invalidated"""
        dependent_keys = set()
        
        for key in keys:
            # Check direct dependencies
            for pattern, deps in self.dependency_graph.items():
                if fnmatch.fnmatch(key, pattern):
                    dependent_keys.update(deps)
        
        return list(dependent_keys)
    
    async def _find_keys_by_pattern(self, pattern: str) -> List[str]:
        """Find cache keys matching pattern"""
        try:
            if hasattr(self.cache_manager, 'scan_keys'):
                return await self.cache_manager.scan_keys(pattern)
            else:
                # Fallback - this would need to be implemented based on cache backend
                return []
        except Exception as e:
            self.logger.error(f"Error finding keys by pattern {pattern}: {e}")
            return []
    
    async def _find_keys_by_tags(self, tags: Set[str]) -> List[str]:
        """Find cache keys by tags"""
        try:
            if hasattr(self.cache_manager, 'find_keys_by_tags'):
                return await self.cache_manager.find_keys_by_tags(tags)
            else:
                # Fallback - this would need to be implemented based on cache backend
                return []
        except Exception as e:
            self.logger.error(f"Error finding keys by tags {tags}: {e}")
            return []
    
    async def _send_notifications(self, request: InvalidationRequest, invalidated_keys: List[str]) -> List[str]:
        """Send notifications for invalidation events"""
        notifications_sent = []
        
        try:
            if self.event_bus:
                event = {
                    "type": "cache_invalidation",
                    "request_id": request.id,
                    "keys": invalidated_keys,
                    "tags": list(request.tags),
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.event_bus.publish("cache.invalidation", event)
                notifications_sent.append("event_bus")
        
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
        
        return notifications_sent
    
    async def _calculate_business_impact(self, invalidated_keys: List[str]) -> Dict[str, Any]:
        """Calculate business impact of invalidation"""
        return {
            "cache_miss_estimate": len(invalidated_keys) * 0.8,  # Estimated cache misses
            "performance_impact": "low" if len(invalidated_keys) < 100 else "medium",
            "affected_users_estimate": len(invalidated_keys) * 2,
            "cost_impact_usd": len(invalidated_keys) * 0.001  # Estimated cost per cache miss
        }
    
    def _update_stats(self, processing_time: float, invalidated_count: int, failed_count: int):
        """Update processing statistics"""
        self.stats["total_invalidations"] += invalidated_count
        self.stats["failed_invalidations"] += failed_count
        
        # Update rolling average
        current_avg = self.stats["avg_processing_time"]
        total = self.stats["total_invalidations"]
        if total > 0:
            self.stats["avg_processing_time"] = ((current_avg * (total - invalidated_count)) + processing_time) / total
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = str(int(time.time() * 1000))
        hash_input = f"{timestamp}_{id(self)}"
        return f"inv_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get invalidation statistics"""
        return {
            **self.stats,
            "active_rules": len(self.rules),
            "dependency_mappings": len(self.dependency_graph),
            "queue_sizes": {
                "immediate": self.invalidation_queue.qsize(),
                "batch": self.batch_queue.qsize(),
                "delayed": self.delayed_queue.qsize()
            }
        }
    
    async def close(self):
        """Close invalidation engine"""
        if self.processing_task:
            self.processing_task.cancel()
        if self.batch_processing_task:
            self.batch_processing_task.cancel()
        if self.delayed_processing_task:
            self.delayed_processing_task.cancel()
        
        # Wait for tasks to complete
        tasks = [t for t in [self.processing_task, self.batch_processing_task, self.delayed_processing_task] if t]
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Error closing invalidation engine: {e}")

# Export main components
__all__ = [
    'CacheInvalidationEngine',
    'InvalidationRule',
    'InvalidationRequest', 
    'InvalidationResult',
    'InvalidationPriority',
    'InvalidationStrategy'
]