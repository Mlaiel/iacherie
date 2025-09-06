"""Optimistic Concurrency Manager - Enterprise Implementation

Advanced optimistic concurrency control for event sourcing with conflict detection,
resolution strategies, and distributed coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import time

from . import DomainEvent, EventStoreInterface, AggregateRoot

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of concurrency conflicts"""
    VERSION_MISMATCH = "version_mismatch"  # Expected version doesn't match
    CONCURRENT_MODIFICATION = "concurrent_modification"  # Simultaneous changes
    BUSINESS_RULE_VIOLATION = "business_rule_violation"  # Business constraint violated
    RESOURCE_LOCK = "resource_lock"  # Resource locked by another process
    TEMPORAL_CONFLICT = "temporal_conflict"  # Time-based conflict


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    FAIL_FAST = "fail_fast"  # Fail immediately on conflict
    RETRY = "retry"  # Retry operation with backoff
    MERGE = "merge"  # Attempt to merge changes
    LAST_WRITER_WINS = "last_writer_wins"  # Last write wins
    FIRST_WRITER_WINS = "first_writer_wins"  # First write wins
    CUSTOM = "custom"  # Custom resolution logic


class LockType(Enum):
    """Types of locks"""
    SHARED = "shared"  # Multiple readers
    EXCLUSIVE = "exclusive"  # Single writer
    INTENT_SHARED = "intent_shared"  # Intent to acquire shared lock
    INTENT_EXCLUSIVE = "intent_exclusive"  # Intent to acquire exclusive lock


class LockScope(Enum):
    """Scope of locks"""
    AGGREGATE = "aggregate"  # Lock entire aggregate
    EVENT_TYPE = "event_type"  # Lock specific event type
    FIELD = "field"  # Lock specific field
    CUSTOM = "custom"  # Custom scope


@dataclass
class ConflictInfo:
    """Information about a detected conflict"""
    conflict_id: str
    conflict_type: ConflictType
    aggregate_id: str
    expected_version: int
    actual_version: int
    conflicting_events: List[DomainEvent]
    detection_time: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    resolution_attempts: int = 0
    resolved: bool = False
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "aggregate_id": self.aggregate_id,
            "expected_version": self.expected_version,
            "actual_version": self.actual_version,
            "conflicting_events": [e.event_id for e in self.conflicting_events],
            "detection_time": self.detection_time.isoformat(),
            "context": self.context,
            "resolution_attempts": self.resolution_attempts,
            "resolved": self.resolved,
            "resolution_strategy": self.resolution_strategy.value if self.resolution_strategy else None
        }


@dataclass
class LockInfo:
    """Information about a concurrency lock"""
    lock_id: str
    resource_id: str
    lock_type: LockType
    lock_scope: LockScope
    owner_id: str
    acquired_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        return self.expires_at and datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lock_id": self.lock_id,
            "resource_id": self.resource_id,
            "lock_type": self.lock_type.value,
            "lock_scope": self.lock_scope.value,
            "owner_id": self.owner_id,
            "acquired_at": self.acquired_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "is_expired": self.is_expired
        }


@dataclass
class ConcurrencyMetrics:
    """Concurrency control metrics"""
    total_operations: int = 0
    successful_operations: int = 0
    conflicted_operations: int = 0
    resolved_conflicts: int = 0
    retry_attempts: int = 0
    lock_acquisitions: int = 0
    lock_timeouts: int = 0
    average_lock_hold_time_ms: float = 0.0
    average_conflict_resolution_time_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        return self.successful_operations / max(self.total_operations, 1)
    
    @property
    def conflict_rate(self) -> float:
        return self.conflicted_operations / max(self.total_operations, 1)
    
    @property
    def resolution_rate(self) -> float:
        return self.resolved_conflicts / max(self.conflicted_operations, 1)


class ConflictDetector:
    """Detects concurrency conflicts"""
    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
    
    async def detect_version_conflict(self, aggregate_id: str, 
                                    expected_version: int) -> Optional[ConflictInfo]:
        """Detect version-based conflicts"""
        try:
            # Get current events for aggregate
            current_events = await self.event_store.get_events(aggregate_id)
            
            if not current_events:
                current_version = 0
            else:
                current_version = max(event.event_version for event in current_events)
            
            if current_version != expected_version:
                return ConflictInfo(
                    conflict_id=str(uuid4()),
                    conflict_type=ConflictType.VERSION_MISMATCH,
                    aggregate_id=aggregate_id,
                    expected_version=expected_version,
                    actual_version=current_version,
                    conflicting_events=current_events[-5:] if current_events else [],  # Last 5 events
                    detection_time=datetime.now(timezone.utc),
                    context={"current_event_count": len(current_events)}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect version conflict: {e}")
            return None
    
    async def detect_concurrent_modifications(self, aggregate_id: str, 
                                            events_to_save: List[DomainEvent],
                                            time_window_seconds: int = 60) -> Optional[ConflictInfo]:
        """Detect concurrent modifications within time window"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_window_seconds)
            
            # Get recent events for aggregate
            all_events = await self.event_store.get_events(aggregate_id)
            recent_events = [
                event for event in all_events 
                if event.occurred_at > cutoff_time
            ]
            
            if recent_events:
                # Check if any events are being saved concurrently
                for new_event in events_to_save:
                    for recent_event in recent_events:
                        if (recent_event.event_version == new_event.event_version or
                            abs((recent_event.occurred_at - new_event.occurred_at).total_seconds()) < 5):
                            
                            return ConflictInfo(
                                conflict_id=str(uuid4()),
                                conflict_type=ConflictType.CONCURRENT_MODIFICATION,
                                aggregate_id=aggregate_id,
                                expected_version=new_event.event_version,
                                actual_version=recent_event.event_version,
                                conflicting_events=[recent_event] + events_to_save,
                                detection_time=datetime.now(timezone.utc),
                                context={
                                    "time_window_seconds": time_window_seconds,
                                    "recent_events_count": len(recent_events)
                                }
                            )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect concurrent modifications: {e}")
            return None


class ConflictResolver:
    """Resolves concurrency conflicts"""
    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
        self.custom_resolvers: Dict[str, Callable] = {}
    
    def register_custom_resolver(self, event_type: str, 
                                resolver: Callable[[ConflictInfo, List[DomainEvent]], List[DomainEvent]]) -> None:
        """Register custom conflict resolver for event type"""
        self.custom_resolvers[event_type] = resolver
    
    async def resolve_conflict(self, conflict: ConflictInfo, 
                             events_to_save: List[DomainEvent],
                             strategy: ConflictResolutionStrategy) -> Tuple[bool, List[DomainEvent]]:
        """Resolve conflict using specified strategy"""
        try:
            if strategy == ConflictResolutionStrategy.FAIL_FAST:
                return False, []
            
            elif strategy == ConflictResolutionStrategy.RETRY:
                # For retry, return events as-is but with updated versions
                updated_events = await self._update_event_versions(events_to_save, conflict.aggregate_id)
                return True, updated_events
            
            elif strategy == ConflictResolutionStrategy.MERGE:
                merged_events = await self._merge_events(conflict, events_to_save)
                return True, merged_events
            
            elif strategy == ConflictResolutionStrategy.LAST_WRITER_WINS:
                # Keep the new events, update versions
                updated_events = await self._update_event_versions(events_to_save, conflict.aggregate_id)
                return True, updated_events
            
            elif strategy == ConflictResolutionStrategy.FIRST_WRITER_WINS:
                # Discard new events
                return False, []
            
            elif strategy == ConflictResolutionStrategy.CUSTOM:
                return await self._apply_custom_resolution(conflict, events_to_save)
            
            else:
                logger.warning(f"Unknown resolution strategy: {strategy}")
                return False, []
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            return False, []
    
    async def _update_event_versions(self, events: List[DomainEvent], 
                                   aggregate_id: str) -> List[DomainEvent]:
        """Update event versions to resolve version conflicts"""
        # Get current version
        current_events = await self.event_store.get_events(aggregate_id)
        current_version = max((event.event_version for event in current_events), default=0)
        
        updated_events = []
        for i, event in enumerate(events):
            updated_event = DomainEvent(
                event_id=event.event_id,
                aggregate_id=event.aggregate_id,
                aggregate_type=event.aggregate_type,
                event_type=event.event_type,
                event_data=event.event_data,
                event_version=current_version + i + 1,
                occurred_at=event.occurred_at
            )
            updated_events.append(updated_event)
        
        return updated_events
    
    async def _merge_events(self, conflict: ConflictInfo, 
                          events_to_save: List[DomainEvent]) -> List[DomainEvent]:
        """Merge conflicting events"""
        # This is a simplified merge - in practice would be more sophisticated
        # based on event types and business logic
        
        merged_events = []
        
        for new_event in events_to_save:
            # Check if there's a conflicting event of the same type
            conflicting_event = None
            for conflict_event in conflict.conflicting_events:
                if (conflict_event.event_type == new_event.event_type and
                    conflict_event.aggregate_id == new_event.aggregate_id):
                    conflicting_event = conflict_event
                    break
            
            if conflicting_event:
                # Merge event data
                merged_data = self._merge_event_data(conflicting_event.event_data, new_event.event_data)
                
                merged_event = DomainEvent(
                    event_id=str(uuid4()),  # New ID for merged event
                    aggregate_id=new_event.aggregate_id,
                    aggregate_type=new_event.aggregate_type,
                    event_type=new_event.event_type,
                    event_data=merged_data,
                    event_version=conflict.actual_version + 1,
                    occurred_at=datetime.now(timezone.utc)
                )
                merged_events.append(merged_event)
            else:
                # No conflict, keep original event with updated version
                updated_event = DomainEvent(
                    event_id=new_event.event_id,
                    aggregate_id=new_event.aggregate_id,
                    aggregate_type=new_event.aggregate_type,
                    event_type=new_event.event_type,
                    event_data=new_event.event_data,
                    event_version=conflict.actual_version + 1,
                    occurred_at=new_event.occurred_at
                )
                merged_events.append(updated_event)
        
        return merged_events
    
    def _merge_event_data(self, existing_data: Dict[str, Any], 
                         new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge event data dictionaries"""
        # Simple merge strategy - new data takes precedence
        merged = existing_data.copy()
        merged.update(new_data)
        
        # Add merge metadata
        merged['_merge_info'] = {
            'merged_at': datetime.now(timezone.utc).isoformat(),
            'merge_strategy': 'new_wins',
            'original_keys': list(existing_data.keys()),
            'new_keys': list(new_data.keys())
        }
        
        return merged
    
    async def _apply_custom_resolution(self, conflict: ConflictInfo, 
                                     events_to_save: List[DomainEvent]) -> Tuple[bool, List[DomainEvent]]:
        """Apply custom conflict resolution"""
        if not events_to_save:
            return False, []
        
        event_type = events_to_save[0].event_type
        
        if event_type in self.custom_resolvers:
            try:
                resolved_events = self.custom_resolvers[event_type](conflict, events_to_save)
                return True, resolved_events
            except Exception as e:
                logger.error(f"Custom resolver failed for {event_type}: {e}")
                return False, []
        else:
            logger.warning(f"No custom resolver for event type: {event_type}")
            return False, []


class DistributedLockManager:
    """Manages distributed locks for concurrency control"""
    
    def __init__(self):
        self.locks: Dict[str, LockInfo] = {}
        self.lock_waiters: Dict[str, List[asyncio.Event]] = {}
        self.lock_timeout_tasks: Dict[str, asyncio.Task] = {}
    
    async def acquire_lock(self, resource_id: str, owner_id: str, 
                         lock_type: LockType = LockType.EXCLUSIVE,
                         lock_scope: LockScope = LockScope.AGGREGATE,
                         timeout_seconds: int = 30) -> Optional[LockInfo]:
        """Acquire lock on resource"""
        try:
            lock_id = f"{resource_id}:{lock_type.value}:{owner_id}"
            
            # Check if lock can be acquired
            if not await self._can_acquire_lock(resource_id, lock_type, owner_id):
                # Wait for lock if possible
                if timeout_seconds > 0:
                    success = await self._wait_for_lock(resource_id, timeout_seconds)
                    if not success:
                        return None
                else:
                    return None
            
            # Acquire the lock
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)
            
            lock_info = LockInfo(
                lock_id=lock_id,
                resource_id=resource_id,
                lock_type=lock_type,
                lock_scope=lock_scope,
                owner_id=owner_id,
                acquired_at=datetime.now(timezone.utc),
                expires_at=expires_at
            )
            
            self.locks[lock_id] = lock_info
            
            # Set up automatic expiration
            timeout_task = asyncio.create_task(
                self._auto_release_lock(lock_id, timeout_seconds)
            )
            self.lock_timeout_tasks[lock_id] = timeout_task
            
            logger.debug(f"Acquired lock {lock_id} for {owner_id}")
            return lock_info
            
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return None
    
    async def release_lock(self, lock_id: str, owner_id: str) -> bool:
        """Release lock"""
        try:
            if lock_id not in self.locks:
                return False
            
            lock_info = self.locks[lock_id]
            
            # Verify ownership
            if lock_info.owner_id != owner_id:
                logger.warning(f"Lock release attempted by non-owner: {owner_id}")
                return False
            
            # Remove lock
            del self.locks[lock_id]
            
            # Cancel timeout task
            if lock_id in self.lock_timeout_tasks:
                self.lock_timeout_tasks[lock_id].cancel()
                del self.lock_timeout_tasks[lock_id]
            
            # Notify waiters
            await self._notify_waiters(lock_info.resource_id)
            
            logger.debug(f"Released lock {lock_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
            return False
    
    async def extend_lock(self, lock_id: str, owner_id: str, 
                        additional_seconds: int) -> bool:
        """Extend lock duration"""
        try:
            if lock_id not in self.locks:
                return False
            
            lock_info = self.locks[lock_id]
            
            if lock_info.owner_id != owner_id:
                return False
            
            # Extend expiration
            if lock_info.expires_at:
                lock_info.expires_at += timedelta(seconds=additional_seconds)
            
            # Update timeout task
            if lock_id in self.lock_timeout_tasks:
                self.lock_timeout_tasks[lock_id].cancel()
                
                timeout_task = asyncio.create_task(
                    self._auto_release_lock(lock_id, additional_seconds)
                )
                self.lock_timeout_tasks[lock_id] = timeout_task
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend lock: {e}")
            return False
    
    def get_locks_for_resource(self, resource_id: str) -> List[LockInfo]:
        """Get all locks for a resource"""
        return [lock for lock in self.locks.values() if lock.resource_id == resource_id]
    
    def get_locks_for_owner(self, owner_id: str) -> List[LockInfo]:
        """Get all locks owned by owner"""
        return [lock for lock in self.locks.values() if lock.owner_id == owner_id]
    
    async def cleanup_expired_locks(self) -> int:
        """Clean up expired locks"""
        expired_locks = []
        
        for lock_id, lock_info in self.locks.items():
            if lock_info.is_expired:
                expired_locks.append(lock_id)
        
        for lock_id in expired_locks:
            lock_info = self.locks[lock_id]
            await self.release_lock(lock_id, lock_info.owner_id)
        
        return len(expired_locks)
    
    async def _can_acquire_lock(self, resource_id: str, lock_type: LockType, 
                              owner_id: str) -> bool:
        """Check if lock can be acquired"""
        existing_locks = self.get_locks_for_resource(resource_id)
        
        # Remove expired locks
        for lock in existing_locks:
            if lock.is_expired:
                await self.release_lock(lock.lock_id, lock.owner_id)
        
        # Refresh after cleanup
        existing_locks = self.get_locks_for_resource(resource_id)
        
        if not existing_locks:
            return True
        
        # Check compatibility
        for existing_lock in existing_locks:
            if existing_lock.owner_id == owner_id:
                continue  # Same owner can have multiple locks
            
            # Exclusive locks are incompatible with everything
            if (lock_type == LockType.EXCLUSIVE or 
                existing_lock.lock_type == LockType.EXCLUSIVE):
                return False
            
            # Shared locks are compatible with other shared locks
            if (lock_type == LockType.SHARED and 
                existing_lock.lock_type == LockType.SHARED):
                continue
            
            return False
        
        return True
    
    async def _wait_for_lock(self, resource_id: str, timeout_seconds: int) -> bool:
        """Wait for lock to become available"""
        if resource_id not in self.lock_waiters:
            self.lock_waiters[resource_id] = []
        
        wait_event = asyncio.Event()
        self.lock_waiters[resource_id].append(wait_event)
        
        try:
            await asyncio.wait_for(wait_event.wait(), timeout=timeout_seconds)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            if wait_event in self.lock_waiters[resource_id]:
                self.lock_waiters[resource_id].remove(wait_event)
    
    async def _notify_waiters(self, resource_id: str) -> None:
        """Notify waiters that lock is available"""
        if resource_id in self.lock_waiters:
            for waiter in self.lock_waiters[resource_id]:
                waiter.set()
    
    async def _auto_release_lock(self, lock_id: str, timeout_seconds: int) -> None:
        """Automatically release lock after timeout"""
        try:
            await asyncio.sleep(timeout_seconds)
            
            if lock_id in self.locks:
                lock_info = self.locks[lock_id]
                await self.release_lock(lock_id, lock_info.owner_id)
                
        except asyncio.CancelledError:
            pass  # Lock was released manually


class OptimisticConcurrencyManager:
    """Enterprise optimistic concurrency manager"""
    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
        self.conflict_detector = ConflictDetector(event_store)
        self.conflict_resolver = ConflictResolver(event_store)
        self.lock_manager = DistributedLockManager()
        
        self.metrics = ConcurrencyMetrics()
        self.conflict_history: List[ConflictInfo] = []
        self.active_operations: Dict[str, datetime] = {}
        
        # Configuration
        self.default_retry_attempts = 3
        self.default_retry_delay_ms = 100
        self.default_conflict_resolution = ConflictResolutionStrategy.RETRY
        self.enable_distributed_locking = True
    
    async def save_events_with_concurrency_control(self, aggregate_id: str, 
                                                  events: List[DomainEvent],
                                                  expected_version: int,
                                                  resolution_strategy: ConflictResolutionStrategy = None,
                                                  max_retries: int = None,
                                                  owner_id: str = None) -> Tuple[bool, Optional[ConflictInfo]]:
        """Save events with optimistic concurrency control"""
        operation_id = str(uuid4())
        start_time = time.time()
        
        try:
            self.metrics.total_operations += 1
            self.active_operations[operation_id] = datetime.now(timezone.utc)
            
            strategy = resolution_strategy or self.default_conflict_resolution
            retries = max_retries or self.default_retry_attempts
            owner = owner_id or operation_id
            
            # Acquire lock if distributed locking is enabled
            lock_info = None
            if self.enable_distributed_locking:
                lock_info = await self.lock_manager.acquire_lock(
                    resource_id=aggregate_id,
                    owner_id=owner,
                    timeout_seconds=30
                )
                
                if not lock_info:
                    logger.warning(f"Failed to acquire lock for aggregate {aggregate_id}")
                    return False, None
            
            try:
                # Attempt to save with conflict detection and resolution
                for attempt in range(retries + 1):
                    # Detect conflicts
                    conflict = await self.conflict_detector.detect_version_conflict(
                        aggregate_id, expected_version
                    )
                    
                    if not conflict:
                        # Check for concurrent modifications
                        conflict = await self.conflict_detector.detect_concurrent_modifications(
                            aggregate_id, events
                        )
                    
                    if not conflict:
                        # No conflict, try to save
                        try:
                            await self.event_store.save_events(aggregate_id, events, expected_version)
                            self.metrics.successful_operations += 1
                            return True, None
                        except Exception as e:
                            # Exception during save might indicate a conflict
                            logger.warning(f"Save failed, possible conflict: {e}")
                            conflict = ConflictInfo(
                                conflict_id=str(uuid4()),
                                conflict_type=ConflictType.VERSION_MISMATCH,
                                aggregate_id=aggregate_id,
                                expected_version=expected_version,
                                actual_version=-1,  # Unknown
                                conflicting_events=[],
                                detection_time=datetime.now(timezone.utc),
                                context={"save_error": str(e)}
                            )
                    
                    if conflict:
                        # Record conflict
                        self.metrics.conflicted_operations += 1
                        conflict.resolution_attempts = attempt
                        conflict.resolution_strategy = strategy
                        
                        if attempt < retries:
                            # Attempt to resolve conflict
                            self.metrics.retry_attempts += 1
                            resolution_start = time.time()
                            
                            resolved, resolved_events = await self.conflict_resolver.resolve_conflict(
                                conflict, events, strategy
                            )
                            
                            resolution_time = (time.time() - resolution_start) * 1000
                            self.metrics.average_conflict_resolution_time_ms = (
                                (self.metrics.average_conflict_resolution_time_ms + resolution_time) / 2
                            )
                            
                            if resolved and resolved_events:
                                # Update events and expected version for retry
                                events = resolved_events
                                expected_version = conflict.actual_version
                                conflict.resolved = True
                                self.metrics.resolved_conflicts += 1
                                
                                # Add delay before retry
                                await asyncio.sleep(self.default_retry_delay_ms / 1000 * (2 ** attempt))
                                continue
                        
                        # Conflict not resolved or max retries reached
                        self.conflict_history.append(conflict)
                        return False, conflict
                
                # Should not reach here
                return False, None
                
            finally:
                # Release lock
                if lock_info:
                    await self.lock_manager.release_lock(lock_info.lock_id, owner)
                    
                    lock_hold_time = (time.time() - start_time) * 1000
                    self.metrics.average_lock_hold_time_ms = (
                        (self.metrics.average_lock_hold_time_ms + lock_hold_time) / 2
                    )
                
        except Exception as e:
            logger.error(f"Concurrency control failed: {e}")
            return False, None
        finally:
            if operation_id in self.active_operations:
                del self.active_operations[operation_id]
    
    async def check_aggregate_locks(self, aggregate_id: str) -> List[LockInfo]:
        """Check locks on aggregate"""
        return self.lock_manager.get_locks_for_resource(aggregate_id)
    
    async def force_release_locks(self, owner_id: str) -> int:
        """Force release all locks owned by owner"""
        owner_locks = self.lock_manager.get_locks_for_owner(owner_id)
        released_count = 0
        
        for lock in owner_locks:
            if await self.lock_manager.release_lock(lock.lock_id, owner_id):
                released_count += 1
        
        return released_count
    
    def register_custom_conflict_resolver(self, event_type: str, 
                                        resolver: Callable[[ConflictInfo, List[DomainEvent]], List[DomainEvent]]) -> None:
        """Register custom conflict resolver"""
        self.conflict_resolver.register_custom_resolver(event_type, resolver)
    
    def configure_retry_behavior(self, max_retries: int, delay_ms: int) -> None:
        """Configure retry behavior"""
        self.default_retry_attempts = max_retries
        self.default_retry_delay_ms = delay_ms
    
    def set_default_resolution_strategy(self, strategy: ConflictResolutionStrategy) -> None:
        """Set default conflict resolution strategy"""
        self.default_conflict_resolution = strategy
    
    def enable_locking(self, enabled: bool = True) -> None:
        """Enable or disable distributed locking"""
        self.enable_distributed_locking = enabled
    
    async def get_conflict_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get conflict statistics for recent period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_conflicts = [
            c for c in self.conflict_history 
            if c.detection_time >= cutoff_time
        ]
        
        if not recent_conflicts:
            return {"message": "No recent conflicts"}
        
        conflict_types = {}
        resolution_strategies = {}
        
        for conflict in recent_conflicts:
            conflict_types[conflict.conflict_type.value] = conflict_types.get(conflict.conflict_type.value, 0) + 1
            if conflict.resolution_strategy:
                strategy = conflict.resolution_strategy.value
                resolution_strategies[strategy] = resolution_strategies.get(strategy, 0) + 1
        
        return {
            "period_hours": hours,
            "total_conflicts": len(recent_conflicts),
            "resolved_conflicts": len([c for c in recent_conflicts if c.resolved]),
            "conflict_types": conflict_types,
            "resolution_strategies": resolution_strategies,
            "most_common_conflict": max(conflict_types.items(), key=lambda x: x[1])[0] if conflict_types else None,
            "resolution_rate": len([c for c in recent_conflicts if c.resolved]) / len(recent_conflicts)
        }
    
    def get_metrics(self) -> ConcurrencyMetrics:
        """Get current concurrency metrics"""
        return self.metrics
    
    async def cleanup_resources(self) -> Dict[str, int]:
        """Cleanup expired resources and stale operations"""
        # Cleanup expired locks
        expired_locks = await self.lock_manager.cleanup_expired_locks()
        
        # Cleanup stale operations
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        stale_operations = []
        
        for op_id, start_time in self.active_operations.items():
            if start_time < cutoff_time:
                stale_operations.append(op_id)
        
        for op_id in stale_operations:
            del self.active_operations[op_id]
        
        # Cleanup old conflict history
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
        initial_count = len(self.conflict_history)
        self.conflict_history = [
            c for c in self.conflict_history 
            if c.detection_time >= cutoff_time
        ]
        cleaned_conflicts = initial_count - len(self.conflict_history)
        
        return {
            "expired_locks": expired_locks,
            "stale_operations": len(stale_operations),
            "cleaned_conflicts": cleaned_conflicts
        }
    
    async def health_check(self) -> bool:
        """Check manager health"""
        try:
            # Test basic conflict detection
            test_conflict = await self.conflict_detector.detect_version_conflict("test_aggregate", 1)
            
            # Test lock acquisition
            test_lock = await self.lock_manager.acquire_lock("test_resource", "health_check", timeout_seconds=1)
            if test_lock:
                await self.lock_manager.release_lock(test_lock.lock_id, "health_check")
            
            return True
        except Exception as e:
            logger.error(f"Concurrency manager health check failed: {e}")
            return False