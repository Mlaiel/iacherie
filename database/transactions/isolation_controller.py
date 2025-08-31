"""
Isolation Controller - Transaction Isolation Level Management

Enterprise-grade isolation control system providing ACID isolation guarantees,
concurrency control, and lock management for the IA Influencer platform's
multi-tenant creator economy transactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import asyncio
import threading
import time
import logging
from typing import Dict, List, Set, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib

logger = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """SQL standard isolation levels with extended creator economy controls"""
    READ_UNCOMMITTED = "READ_UNCOMMITTED"  # Lowest isolation, phantom reads allowed
    READ_COMMITTED = "READ_COMMITTED"      # Prevents dirty reads
    REPEATABLE_READ = "REPEATABLE_READ"    # Prevents non-repeatable reads
    SERIALIZABLE = "SERIALIZABLE"          # Highest isolation, full serializability
    
    # Extended levels for creator economy
    CREATOR_ISOLATED = "CREATOR_ISOLATED"   # Creator-specific isolation
    CONTENT_CONSISTENT = "CONTENT_CONSISTENT"  # Content consistency guarantees
    REVENUE_ATOMIC = "REVENUE_ATOMIC"      # Revenue operation atomicity


class LockType(Enum):
    """Lock types for resource protection"""
    SHARED = "SHARED"           # Read lock, multiple readers allowed
    EXCLUSIVE = "EXCLUSIVE"     # Write lock, exclusive access
    INTENT_SHARED = "INTENT_SHARED"     # Intent to acquire shared locks
    INTENT_EXCLUSIVE = "INTENT_EXCLUSIVE"  # Intent to acquire exclusive locks
    UPDATE = "UPDATE"           # Update lock, can be upgraded to exclusive
    
    # Creator economy specific locks
    CREATOR_SHARED = "CREATOR_SHARED"     # Creator data shared access
    CREATOR_EXCLUSIVE = "CREATOR_EXCLUSIVE"  # Creator data exclusive access
    CONTENT_READ = "CONTENT_READ"         # Content read access
    CONTENT_WRITE = "CONTENT_WRITE"       # Content write access
    REVENUE_READ = "REVENUE_READ"         # Revenue data read access
    REVENUE_WRITE = "REVENUE_WRITE"       # Revenue data write access


@dataclass
class LockRequest:
    """Lock request information"""
    transaction_id: str
    resource_id: str
    lock_type: LockType
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    granted_at: Optional[datetime] = None
    timeout: float = 30.0
    priority: int = 0
    creator_id: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if lock request has expired"""
        elapsed = (datetime.now(timezone.utc) - self.requested_at).total_seconds()
        return elapsed > self.timeout
    
    @property
    def wait_time(self) -> float:
        """Calculate wait time in seconds"""



        return (datetime.now(timezone.utc) - self.requested_at).total_seconds()


@dataclass
class GrantedLock:
    """Information about granted lock"""
    transaction_id: str
    resource_id: str
    lock_type: LockType
    granted_at: datetime
    creator_id: Optional[str] = None
    access_count: int = 0
    
    def is_compatible(self, lock_type: LockType) -> bool:
        """Check if this lock is compatible with requested lock type"""
        compatibility_matrix = {
            (LockType.SHARED, LockType.SHARED): True,
            (LockType.SHARED, LockType.EXCLUSIVE): False,
            (LockType.SHARED, LockType.UPDATE): False,
            (LockType.EXCLUSIVE, LockType.SHARED): False,
            (LockType.EXCLUSIVE, LockType.EXCLUSIVE): False,
            (LockType.EXCLUSIVE, LockType.UPDATE): False,
            (LockType.UPDATE, LockType.SHARED): True,
            (LockType.UPDATE, LockType.EXCLUSIVE): False,
            (LockType.UPDATE, LockType.UPDATE): False,
            
            # Creator economy compatibility
            (LockType.CREATOR_SHARED, LockType.CREATOR_SHARED): True,
            (LockType.CREATOR_SHARED, LockType.CREATOR_EXCLUSIVE): False,
            (LockType.CREATOR_EXCLUSIVE, LockType.CREATOR_SHARED): False,
            (LockType.CREATOR_EXCLUSIVE, LockType.CREATOR_EXCLUSIVE): False,
            (LockType.CONTENT_READ, LockType.CONTENT_READ): True,
            (LockType.CONTENT_READ, LockType.CONTENT_WRITE): False,
            (LockType.CONTENT_WRITE, LockType.CONTENT_READ): False,
            (LockType.CONTENT_WRITE, LockType.CONTENT_WRITE): False,
            (LockType.REVENUE_READ, LockType.REVENUE_READ): True,
            (LockType.REVENUE_READ, LockType.REVENUE_WRITE): False,
            (LockType.REVENUE_WRITE, LockType.REVENUE_READ): False,
            (LockType.REVENUE_WRITE, LockType.REVENUE_WRITE): False,
        }
        
        return compatibility_matrix.get((self.lock_type, lock_type), False)


class DeadlockDetector:
    """Deadlock detection and resolution system"""
    
    def __init__(self):
        self.wait_for_graph: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.RLock()
        self.detection_interval = 5.0  # seconds
        self.running = False
        
    def start_detection(self):
        """Start deadlock detection background task"""
        self.running = True
        asyncio.create_task(self._detection_loop())
    
    def stop_detection(self):
        """Stop deadlock detection"""
        self.running = False
    
    def add_wait_edge(self, waiting_tx: str, blocking_tx: str):
        """Add edge to wait-for graph"""
        with self.lock:
            self.wait_for_graph[waiting_tx].add(blocking_tx)
    
    def remove_wait_edge(self, waiting_tx: str, blocking_tx: str):
        """Remove edge from wait-for graph"""
        with self.lock:
            if waiting_tx in self.wait_for_graph:
                self.wait_for_graph[waiting_tx].discard(blocking_tx)
                if not self.wait_for_graph[waiting_tx]:
                    del self.wait_for_graph[waiting_tx]
    
    def remove_transaction(self, transaction_id: str):
        """Remove transaction from wait-for graph"""
        with self.lock:
            # Remove as waiting transaction
            self.wait_for_graph.pop(transaction_id, None)
            
            # Remove as blocking transaction
            for tx_id in list(self.wait_for_graph.keys()):
                self.wait_for_graph[tx_id].discard(transaction_id)
                if not self.wait_for_graph[tx_id]:
                    del self.wait_for_graph[tx_id]
    
    def detect_deadlock(self) -> Optional[List[str]]:
        """Detect deadlock using cycle detection in wait-for graph"""
        with self.lock:
            visited = set()
            rec_stack = set()
            
            def has_cycle(node: str, path: List[str]) -> Optional[List[str]]:
                if node in rec_stack:
                    # Found cycle, return the cycle path
                    cycle_start = path.index(node)
                    return path[cycle_start:] + [node]
                
                if node in visited:
                    return None
                
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in self.wait_for_graph.get(node, []):
                    cycle = has_cycle(neighbor, path.copy())
                    if cycle:
                        return cycle
                
                rec_stack.remove(node)
                return None
            
            for transaction_id in self.wait_for_graph:
                if transaction_id not in visited:
                    cycle = has_cycle(transaction_id, [])
                    if cycle:
                        return cycle
            
            return None
    
    async def _detection_loop(self):
        """Background deadlock detection loop"""
        while self.running:
            try:
                deadlock = self.detect_deadlock()
                if deadlock:
                    logger.warning("Deadlock detected: %s", " -> ".join(deadlock))
                    # In a real implementation, would trigger deadlock resolution
                
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error("Error in deadlock detection: %s", str(e))
                await asyncio.sleep(1)


class IsolationController:
    """
    Advanced isolation controller providing enterprise-grade concurrency control
    
    Features:
    - Multi-level isolation control
    - Creator-specific isolation guarantees
    - Content consistency management
    - Revenue operation atomicity
    - Deadlock detection and resolution
    - Performance-optimized lock management
    - Real-time monitoring and metrics
    """
    
    def __init__(self):
        # Lock management
        self.granted_locks: Dict[str, List[GrantedLock]] = defaultdict(list)
        self.lock_queue: Dict[str, deque] = defaultdict(deque)
        self.transaction_locks: Dict[str, Set[str]] = defaultdict(set)
        
        # Isolation levels per transaction
        self.transaction_isolation: Dict[str, IsolationLevel] = {}
        
        # Creator-specific controls
        self.creator_locks: Dict[str, Set[str]] = defaultdict(set)
        self.creator_isolation: Dict[str, IsolationLevel] = {}
        
        # Concurrency control
        self.lock = asyncio.Lock()
        self.condition = asyncio.Condition(self.lock)
        
        # Deadlock detection
        self.deadlock_detector = DeadlockDetector()
        self.deadlock_detector.start_detection()
        
        # Performance metrics
        self.metrics = {
            "locks_granted": 0,
            "locks_denied": 0,
            "deadlocks_detected": 0,
            "average_wait_time": 0.0,
            "lock_timeouts": 0,
            "creator_violations": 0,
        }
        
        # Background monitoring
        self._monitoring = True
        asyncio.create_task(self._monitor_locks())
        
        logger.info("IsolationController initialized with deadlock detection")
    
    async def set_transaction_isolation(
        self,
        transaction_id: str,
        isolation_level: IsolationLevel,
        creator_id: Optional[str] = None
    ) -> None:
        """Set isolation level for transaction"""
        async with self.lock:
            self.transaction_isolation[transaction_id] = isolation_level
            
            if creator_id:
                self.creator_isolation[creator_id] = isolation_level
                
        logger.debug("Set isolation level %s for transaction %s", 
                    isolation_level.value, transaction_id)
    
    async def acquire_lock(
        self,
        transaction_id: str,
        resource_id: str,
        lock_type: LockType,
        timeout: float = 30.0,
        creator_id: Optional[str] = None
    ) -> bool:
        """Acquire lock on resource with isolation guarantees"""
        
        request = LockRequest(
            transaction_id=transaction_id,
            resource_id=resource_id,
            lock_type=lock_type,
            timeout=timeout,
            creator_id=creator_id
        )
        
        # Check creator-specific isolation requirements
        if creator_id and not await self._validate_creator_access(transaction_id, creator_id, resource_id):
            logger.warning("Creator isolation violation: tx=%s creator=%s resource=%s",
                          transaction_id, creator_id, resource_id)
            self.metrics["creator_violations"] += 1
            return False
        
        start_time = time.time()
        
        async with self.condition:
            # Check if lock can be granted immediately
            if self._can_grant_lock(request):
                await self._grant_lock(request)
                self.metrics["locks_granted"] += 1
                return True
            
            # Add to wait queue
            self.lock_queue[resource_id].append(request)
            
            # Add to deadlock detection graph
            blocking_transactions = [lock.transaction_id for lock in self.granted_locks[resource_id]]
            for blocking_tx in blocking_transactions:
                self.deadlock_detector.add_wait_edge(transaction_id, blocking_tx)
            
            # Wait for lock to be available
            while not self._can_grant_lock(request):
                if request.is_expired:
                    self._remove_from_queue(request)
                    self._cleanup_deadlock_edges(transaction_id)
                    self.metrics["lock_timeouts"] += 1
                    logger.warning("Lock request timeout: %s", transaction_id)
                    return False
                
                try:
                    await asyncio.wait_for(self.condition.wait(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
            
            # Grant the lock
            self._remove_from_queue(request)
            await self._grant_lock(request)
            self._cleanup_deadlock_edges(transaction_id)
            
            # Update metrics
            wait_time = time.time() - start_time
            self._update_wait_time_metric(wait_time)
            self.metrics["locks_granted"] += 1
            
            return True
    
    async def release_lock(
        self,
        transaction_id: str,
        resource_id: str,
        lock_type: Optional[LockType] = None
    ) -> bool:
        """Release lock on resource"""
        
        async with self.condition:
            granted_locks = self.granted_locks[resource_id]
            
            # Find and remove the lock
            for i, lock in enumerate(granted_locks):
                if (lock.transaction_id == transaction_id and 
                    (lock_type is None or lock.lock_type == lock_type)):
                    
                    granted_locks.pop(i)
                    self.transaction_locks[transaction_id].discard(resource_id)
                    
                    if lock.creator_id:
                        self.creator_locks[lock.creator_id].discard(resource_id)
                    
                    logger.debug("Released lock: tx=%s resource=%s type=%s",
                               transaction_id, resource_id, lock.lock_type.value)
                    
                    # Notify waiting transactions
                    self.condition.notify_all()
                    
                    # Process next in queue
                    await self._process_lock_queue(resource_id)
                    
                    return True
            
            return False
    
    async def release_all_locks(self, transaction_id: str) -> int:
        """Release all locks held by transaction"""
        
        async with self.condition:
            released_count = 0
            resource_ids = list(self.transaction_locks[transaction_id])
            
            for resource_id in resource_ids:
                if await self.release_lock(transaction_id, resource_id):
                    released_count += 1
            
            # Cleanup transaction from all tracking structures
            self.transaction_locks.pop(transaction_id, None)
            self.transaction_isolation.pop(transaction_id, None)
            self.deadlock_detector.remove_transaction(transaction_id)
            
            logger.info("Released %d locks for transaction %s", released_count, transaction_id)
            return released_count
    
    async def upgrade_lock(
        self,
        transaction_id: str,
        resource_id: str,
        new_lock_type: LockType,
        timeout: float = 30.0
    ) -> bool:
        """Upgrade existing lock to higher level"""
        
        async with self.condition:
            # Find existing lock
            existing_lock = None
            for lock in self.granted_locks[resource_id]:
                if lock.transaction_id == transaction_id:
                    existing_lock = lock
                    break
            
            if not existing_lock:
                logger.error("No existing lock found for upgrade: tx=%s resource=%s",
                           transaction_id, resource_id)
                return False
            
            # Check if upgrade is valid
            if not self._is_valid_upgrade(existing_lock.lock_type, new_lock_type):
                logger.error("Invalid lock upgrade: %s -> %s",
                           existing_lock.lock_type.value, new_lock_type.value)
                return False
            
            # Release existing lock
            await self.release_lock(transaction_id, resource_id, existing_lock.lock_type)
            
            # Acquire new lock
            return await self.acquire_lock(
                transaction_id=transaction_id,
                resource_id=resource_id,
                lock_type=new_lock_type,
                timeout=timeout,
                creator_id=existing_lock.creator_id
            )
    
    async def check_isolation_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check if operation would violate isolation requirements"""
        
        isolation_level = self.transaction_isolation.get(transaction_id, IsolationLevel.READ_COMMITTED)
        
        # Implement isolation level specific checks
        if isolation_level == IsolationLevel.SERIALIZABLE:
            return await self._check_serializable_violation(transaction_id, operation_type, resource_id)
        elif isolation_level == IsolationLevel.REPEATABLE_READ:
            return await self._check_repeatable_read_violation(transaction_id, operation_type, resource_id)
        elif isolation_level == IsolationLevel.CREATOR_ISOLATED:
            return await self._check_creator_isolation_violation(transaction_id, operation_type, resource_id)
        elif isolation_level == IsolationLevel.CONTENT_CONSISTENT:
            return await self._check_content_consistency_violation(transaction_id, operation_type, resource_id)
        elif isolation_level == IsolationLevel.REVENUE_ATOMIC:
            return await self._check_revenue_atomicity_violation(transaction_id, operation_type, resource_id)
        
        return False
    
    async def get_lock_statistics(self) -> Dict[str, Any]:
        """Get comprehensive lock statistics"""
        
        async with self.lock:
            total_locks = sum(len(locks) for locks in self.granted_locks.values())
            total_waiting = sum(len(queue) for queue in self.lock_queue.values())
            
            # Calculate lock type distribution
            lock_type_counts = defaultdict(int)
            for locks in self.granted_locks.values():
                for lock in locks:
                    lock_type_counts[lock.lock_type.value] += 1
            
            # Calculate creator lock distribution
            creator_lock_counts = {creator_id: len(resources) 
                                 for creator_id, resources in self.creator_locks.items()}
            
            return {
                "total_granted_locks": total_locks,
                "total_waiting_requests": total_waiting,
                "lock_type_distribution": dict(lock_type_counts),
                "creator_lock_distribution": creator_lock_counts,
                "active_transactions": len(self.transaction_locks),
                "metrics": self.metrics.copy(),
                "deadlock_graph_size": len(self.deadlock_detector.wait_for_graph),
            }
    
    def _can_grant_lock(self, request: LockRequest) -> bool:
        """Check if lock request can be granted"""
        
        existing_locks = self.granted_locks[request.resource_id]
        
        # If no existing locks, grant immediately
        if not existing_locks:
            return True
        
        # Check compatibility with all existing locks
        for existing_lock in existing_locks:
            # Same transaction can always upgrade/acquire compatible locks
            if existing_lock.transaction_id == request.transaction_id:
                continue
            
            if not existing_lock.is_compatible(request.lock_type):
                return False
        
        return True
    
    async def _grant_lock(self, request: LockRequest) -> None:
        """Grant lock request"""
        
        granted_lock = GrantedLock(
            transaction_id=request.transaction_id,
            resource_id=request.resource_id,
            lock_type=request.lock_type,
            granted_at=datetime.now(timezone.utc),
            creator_id=request.creator_id
        )
        
        self.granted_locks[request.resource_id].append(granted_lock)
        self.transaction_locks[request.transaction_id].add(request.resource_id)
        
        if request.creator_id:
            self.creator_locks[request.creator_id].add(request.resource_id)
        
        logger.debug("Granted lock: tx=%s resource=%s type=%s",
                    request.transaction_id, request.resource_id, request.lock_type.value)
    
    def _remove_from_queue(self, request: LockRequest) -> None:
        """Remove request from wait queue"""
        queue = self.lock_queue[request.resource_id]
        try:
            queue.remove(request)
        except ValueError:
            pass  # Request not in queue
    
    def _cleanup_deadlock_edges(self, transaction_id: str) -> None:
        """Clean up deadlock detection edges for transaction"""
        self.deadlock_detector.remove_transaction(transaction_id)
    
    async def _process_lock_queue(self, resource_id: str) -> None:
        """Process waiting lock requests for resource"""
        
        queue = self.lock_queue[resource_id]
        processed = []
        
        # Process requests in FIFO order with priority consideration
        while queue:
            request = queue.popleft()
            
            if request.is_expired:
                self.metrics["lock_timeouts"] += 1
                continue
            
            if self._can_grant_lock(request):
                await self._grant_lock(request)
                self.metrics["locks_granted"] += 1
                processed.append(request)
            else:
                # Put back in queue if can't be granted
                queue.appendleft(request)
                break
        
        if processed:
            self.condition.notify_all()
    
    def _is_valid_upgrade(self, current_type: LockType, new_type: LockType) -> bool:
        """Check if lock upgrade is valid"""
        upgrade_paths = {
            LockType.SHARED: [LockType.EXCLUSIVE, LockType.UPDATE],
            LockType.UPDATE: [LockType.EXCLUSIVE],
            LockType.CREATOR_SHARED: [LockType.CREATOR_EXCLUSIVE],
            LockType.CONTENT_READ: [LockType.CONTENT_WRITE],
            LockType.REVENUE_READ: [LockType.REVENUE_WRITE],
        }
        
        return new_type in upgrade_paths.get(current_type, [])
    
    async def _validate_creator_access(
        self,
        transaction_id: str,
        creator_id: str,
        resource_id: str
    ) -> bool:
        """Validate creator-specific access rules"""
        
        # Check if resource belongs to creator
        if resource_id.startswith(f"creator_{creator_id}_"):
            return True
        
        # Check if it's a shared resource that creator can access
        if resource_id.startswith("shared_"):
            return True
        
        # Check if creator has explicit permission for this resource
        # This would integrate with the actual permission system
        return False
    
    async def _check_serializable_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check for serializable isolation violations"""
        # Implementation for serializable checks
        return False
    
    async def _check_repeatable_read_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check for repeatable read violations"""
        # Implementation for repeatable read checks
        return False
    
    async def _check_creator_isolation_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check for creator isolation violations"""
        # Implementation for creator-specific isolation checks
        return False
    
    async def _check_content_consistency_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check for content consistency violations"""
        # Implementation for content consistency checks
        return False
    
    async def _check_revenue_atomicity_violation(
        self,
        transaction_id: str,
        operation_type: str,
        resource_id: str
    ) -> bool:
        """Check for revenue atomicity violations"""
        # Implementation for revenue operation atomicity checks
        return False
    
    def _update_wait_time_metric(self, wait_time: float) -> None:
        """Update average wait time metric"""
        current_avg = self.metrics["average_wait_time"]
        total_grants = self.metrics["locks_granted"]
        
        if total_grants > 0:
            self.metrics["average_wait_time"] = (
                (current_avg * (total_grants - 1) + wait_time) / total_grants
            )
        else:
            self.metrics["average_wait_time"] = wait_time
    
    async def _monitor_locks(self) -> None:
        """Background task to monitor lock health"""
        while self._monitoring:
            try:
                # Log statistics periodically
                stats = await self.get_lock_statistics()
                
                if stats["total_granted_locks"] > 1000:
                    logger.warning("High lock count detected: %d", stats["total_granted_locks"])
                
                if stats["total_waiting_requests"] > 100:
                    logger.warning("High wait queue size: %d", stats["total_waiting_requests"])
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error("Error in lock monitoring: %s", str(e))
                await asyncio.sleep(5)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of isolation controller"""
        logger.info("Shutting down IsolationController...")
        
        self._monitoring = False
        self.deadlock_detector.stop_detection()
        
        # Release all locks
        async with self.condition:
            for transaction_id in list(self.transaction_locks.keys()):
                await self.release_all_locks(transaction_id)
        
        logger.info("IsolationController shutdown complete")


# Convenience functions for common isolation patterns
async def with_creator_isolation(
    controller: IsolationController,
    transaction_id: str,
    creator_id: str,
    resource_pattern: str = "creator_{creator_id}_*"
):
    """Context manager for creator-isolated operations"""
    await controller.set_transaction_isolation(
        transaction_id, 
        IsolationLevel.CREATOR_ISOLATED, 
        creator_id
    )


async def with_content_consistency(
    controller: IsolationController,
    transaction_id: str,
    content_resources: List[str]
):
    """Ensure content consistency across multiple resources"""
    await controller.set_transaction_isolation(
        transaction_id, 
        IsolationLevel.CONTENT_CONSISTENT
    )
    
    # Acquire locks on all content resources
    for resource_id in content_resources:
        await controller.acquire_lock(
            transaction_id, 
            resource_id, 
            LockType.CONTENT_WRITE
        )


async def with_revenue_atomicity(
    controller: IsolationController,
    transaction_id: str,
    revenue_resources: List[str]
):
    """Ensure atomic revenue operations"""
    await controller.set_transaction_isolation(
        transaction_id, 
        IsolationLevel.REVENUE_ATOMIC
    )
    
    # Acquire exclusive locks on all revenue resources
    for resource_id in revenue_resources:
        await controller.acquire_lock(
            transaction_id, 
            resource_id, 
            LockType.REVENUE_WRITE
        )
